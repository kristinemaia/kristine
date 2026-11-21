#!/usr/bin/env python3
"""Verificare conținut: ține evidența paginilor cu numele tău, până se șterg.

Ce face (fără să descarce sau să arate poze):
  1. Ia linkurile tale din linkuri.txt și caută singur numele tale pe Google, Google Imagini, Bing și Yandex
     (prin SerpApi) și pe Brave, dacă ai pus o cheie în chei.txt.
  2. Ce găsește nou adaugă singur. Din linkurile găsite învață adresele de profil ale site-urilor
     și verifică acolo și celelalte nume ale tale.
  3. Verifică fiecare pagină: ONLINE, ȘTERS sau NU POT VERIFICA (site blocat în țară, protecție Cloudflare).
  4. Află unde e găzduit fiecare site (Cloudflare sau altă firmă) și adresa lor de abuz.
  5. Deschide raportul în browser: la fiecare site vezi ce mai ai de trimis (Google, Bing, site, hosting),
     bifezi „Am trimis”, iar programul îți spune când e timpul pentru revenire.

Rulezi: dublu-click pe verificare.bat (Windows) sau: python verificare.py
  python verificare.py --raport        doar raportul, fără verificare (ca să bifezi ce ai trimis)
  python verificare.py --cauta         caută acum pe Google/Bing, chiar dacă n-a trecut o săptămână
  python verificare.py --fara-cautare  verifică doar linkurile știute
  python verificare.py --fara-server   scrie raport.html și se oprește
Linkurile, cheile și rezultatele rămân doar în folderul ăsta, pe laptopul tău.
"""
import json, os, re, secrets, shutil, socket, ssl, sys, threading, time, webbrowser
import urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'stare.json')
LINKS = os.path.join(HERE, 'linkuri.txt')
REPORT = os.path.join(HERE, 'raport.html')
KEYS = os.path.join(HERE, 'chei.txt')

# ───────────── Setări (le poți schimba) ─────────────
# Numele tale. Variantele cu liniuță/underscore (kristine-maia, kristine_maia) se fac automat.
NUME = ['kristinemaia', 'kristinemaia11', 'crismaia', 'missfoxyfire']
# Ce caută pe Google/Bing (fiecare exact așa, între ghilimele).
CAUTARI = NUME + ['kristine maia']
# Paginile tale oficiale: nu apar în raport (un domeniu întreg sau începutul unei adrese).
PROPRII = ['kristinemaia.com', 'payhip.com', 'instagram.com/kristinemaia11', 'tiktok.com/@kristinemaia11',
           'twitch.tv/kristinemaia', 'linktr.ee/kristinemaia']
# Paginile de profil de pe site-urile unde a apărut conținutul (din scanarea din 21 nov). {u} = numele lipit, {d} = cu liniuță.
# Pe lângă ele, programul învață singur adresele de profil ale site-urilor noi (le ține în stare.json).
SABLOANE = [
    'https://fapello.com/{u}/', 'https://es.fapello.com/{u}/', 'https://fapello.ru/models/{u}',
    'https://www.erome.vip/models/{u}', 'https://de.thefap.net/@{u}', 'https://nudostar.com/model/{d}/',
    'https://leaked.fans/models/{d}/', 'https://pornrewind.com/creators/{u}', 'https://fapeza.com/{d}/',
    'https://wildskirts.com/{d}/', 'https://fapachi.com/{d}/', 'https://www.masterfap.net/profile/{u}/',
    'https://erothots.co/photos/{u}', 'https://cn.nudogram.com/models/{u}/', 'https://anacams.com/user/{u}/',
    'https://myteenwebcam.com/cam/{u}', 'https://ytboob.com/tag/{u}/', 'https://adultphotosets.best/tags/%40{u}/',
    'https://thefappeningblog.com/gallery/{u}/', 'https://leakgallery.com/{u}', 'https://www.reddit.com/r/{u}/',
]
# Pe platformele mari nu ghicește profiluri: același nume poate fi al altcuiva.
PLATFORME_MARI = ['instagram.com', 'tiktok.com', 'youtube.com', 'x.com', 'twitter.com', 'facebook.com', 'twitch.tv',
                  'reddit.com', 'threads.net', 'pinterest.com', 'linkedin.com', 'linktr.ee', 'onlyfans.com', 'fansly.com',
                  'patreon.com', 'tumblr.com', 'vk.com', 't.me', 'telegram.me', 'github.com', 'payhip.com', 'snapchat.com']
# Căutarea pe Google/Bing (SerpApi: 250 de căutări gratuite pe lună).
MOTOARE = ['google', 'bing', 'google_imagini', 'yandex', 'google_pagina2']   # în ordinea importanței
ZILE_INTRE_CAUTARI = 7       # caută o dată pe săptămână (verificarea linkurilor știute merge oricând)
MAX_CAUTARI_PE_RULARE = 25
LIMITA_SERPAPI = 250         # pe lună, planul gratuit
# Revenirile (din planul tău): site-ul are 7 zile, apoi revenire + hosting; hostingul are 14 zile.
ZILE_REVENIRE_SITE = 7
ZILE_REVENIRE = 14
ZILE_NOU = 7                 # cât timp apare 🆕 la ce a găsit singur
FIRE = 10                    # câte pagini verifică deodată
# ────────────────────────────────────────────────────

ONLINE, STERS, NUPOT = 'ONLINE', 'ȘTERS', 'NU POT VERIFICA'
SURSE_TALE = ('linkurile tale', 'adăugat de tine')
LUNI = ['ian', 'feb', 'mar', 'apr', 'mai', 'iun', 'iul', 'aug', 'sep', 'oct', 'nov', 'dec']
CANALE = [('google', 'Google'), ('bing', 'Bing'), ('site', 'Site-ul'), ('gazda', 'Hosting')]
MOTOR_CANAL = {'google': ('Google', 'Google Imagini'), 'bing': ('Bing',)}
FORMULARE = {
    'google': [('conținut intim', 'https://support.google.com/accounts/answer/17045517'),
               ('copyright', 'https://reportcontent.google.com/forms/dmca_search')],
    'bing': [('formularul Bing', 'https://aka.ms/reportci')],
    'cloudflare': [('formularul Cloudflare', 'https://abuse.cloudflare.com/')],
    'vechi': 'https://search.google.com/search-console/remove-outdated-content',
}

# Ce arată că o pagină e goală / ștearsă, chiar dacă serverul răspunde 200.
GOL_TITLU = ['not found', '404 error', 'error 404', '404 -', '- 404', '| 404', '404 |', 'does not exist',
             "doesn't exist", 'has been removed', 'was removed', 'been deleted', 'banned', 'suspended',
             'no results', 'nothing found', 'unavailable', 'pagina nu exist', 'sayfa bulunamad']
GOL_CORP = ['this community has been banned', 'this account has been suspended', 'model not found', 'no posts found',
            'page not found', 'content has been removed', 'removed due to dmca', 'has been removed due to a dmca',
            'this content is no longer available', 'nothing found']
BLOCAT = ['attention required', 'just a moment', 'cf-chl', 'erişim engellendi', 'bu internet sitesi', 'access denied']
SUFIXE2 = {'co.uk', 'org.uk', 'ac.uk', 'com.br', 'com.tr', 'net.tr', 'org.tr', 'com.au', 'co.jp', 'co.nz', 'co.za',
           'com.mx', 'com.ar', 'us.com', 'uk.com', 'eu.com', 'co.in', 'com.ua', 'com.ru', 'com.cn', 'co.kr', 'com.sg',
           'com.hk', 'com.tw', 'com.pl', 'com.ro', 'co.il', 'com.es', 'com.de', 'co.id', 'com.ph', 'com.vn', 'com.my'}

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'
UA_API = 'verificare-continut/2.0'
CTX = ssl.create_default_context()
SERPAPI_URL = 'https://serpapi.com'
BRAVE_URL = 'https://api.search.brave.com/res/v1/web/search'
DOH_URL = 'https://dns.google/resolve'
RDAP_URL = 'https://rdap.org/ip/'


# ───────────── Mici ajutoare ─────────────
def acum():
    return datetime.now().strftime('%Y-%m-%d %H:%M')


def zi(s):
    return date.fromisoformat(s[:10]) if s else None


def scurt(s):
    d = zi(s)
    if not d:
        return '—'
    return f'{d.day} {LUNI[d.month - 1]}' + ('' if d.year == date.today().year else f' {d.year}')


def zile_de_la(s):
    return (date.today() - zi(s)).days


def nr(n, unu, multe):
    """1 link, 2 linkuri, 20 de linkuri."""
    if n == 1:
        return f'1 {unu}'
    return f'{n} ' + ('de ' if n >= 20 and (n % 100 == 0 or n % 100 >= 20) else '') + multe


def variante(n):
    n = n.lower()
    d = re.sub(r'([a-z])(maia)', r'\1-\2', n) if 'maia' in n else n
    return {'u': n, 'd': d, 's': d.replace('-', '_')}


NUME_TEXT = sorted({v for n in NUME for v in variante(n).values()} | {c.lower() for c in CAUTARI}
                   | {'kristine maia', 'kristine%20maia', 'kristine+maia'})


def are_nume(text):
    text = text.lower()
    return any(v in text for v in NUME_TEXT)


def gazda(url):
    return (urllib.parse.urlsplit(url).hostname or '').lower().rstrip('.')


def domeniu(url):
    h = gazda(url)
    if re.fullmatch(r'[\d.]+|\[?[0-9a-f:]+\]?', h):
        return h
    p = h.split('.')
    if len(p) >= 3 and '.'.join(p[-2:]) in SUFIXE2:
        return '.'.join(p[-3:])
    return '.'.join(p[-2:])


def fara_www(url):
    p = urllib.parse.urlsplit(url)
    h = gazda(url)
    return (h[4:] if h.startswith('www.') else h) + p.path


def cheie(url):
    """Aceeași pagină scrisă puțin diferit (http/https, www, / la final, utm_...) are aceeași cheie."""
    p = urllib.parse.urlsplit(url.strip())
    h = gazda(url)
    h = h[4:] if h.startswith('www.') else h
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=True)
         if not k.lower().startswith('utm_') and k.lower() not in ('fbclid', 'gclid', 'ref', 'ref_src')]
    return h + (p.path.rstrip('/') or '') + ('?' + urllib.parse.urlencode(sorted(q)) if q else '')


def e_al_domeniului(h, d):
    return h == d or h.endswith('.' + d)


def e_propriu(url):
    h, a = gazda(url), fara_www(url).lower()
    for p in PROPRII:
        p = p.lower()
        if ('/' in p and a.startswith(p)) or ('/' not in p and e_al_domeniului(h, p)):
            return True
    return False


def e_motor(url):
    h = gazda(url)
    return bool(re.fullmatch(r'((www|images|translate|webcache|m)\.)?(google|bing|yandex|duckduckgo|serpapi)\.[a-z.]+', h)
                or h in ('search.brave.com', 'webcache.googleusercontent.com') or h.endswith('.translate.goog'))


def platforma_mare(h):
    return any(e_al_domeniului(h, p) for p in PLATFORME_MARI)


def gaseste_linkuri(text):
    out = []
    for m in re.finditer(r'https?://[^\s<>"\']+', text):
        u = m.group(0).rstrip('.,;:!?)]}»”’')
        if gazda(u):
            out.append(u)
    return out


def cere(url, antete=None, timp=20, maxim=600_000, ua=UA):
    req = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept-Language': 'en-US,en;q=0.8', **(antete or {})})
    with urllib.request.urlopen(req, timeout=timp, context=CTX) as r:
        return r.geturl(), r.read(maxim).decode('utf-8', 'ignore')


def cere_json(url, antete=None, timp=25):
    return json.loads(cere(url, {'Accept': 'application/json', **(antete or {})}, timp, 5_000_000, UA_API)[1])


# ───────────── Starea (stare.json, doar pe laptopul tău) ─────────────
def incarca():
    data, citit = {}, None
    for cale in (STATE, STATE + '.bak'):
        if not os.path.exists(cale):
            continue
        try:
            with open(cale, encoding='utf-8') as f:
                data, citit = json.load(f), cale
            break
        except (ValueError, OSError):
            print(f'Atenție: {os.path.basename(cale)} e stricat. Încerc copia de rezervă.')
    if citit == STATE:   # copia de rezervă = cum era înainte de rularea asta
        shutil.copyfile(STATE, STATE + '.bak')
    if data and 'linkuri' not in data:   # formatul vechi: {link: {...}}
        tale = {cheie(u) for u in linkurile_tale()}
        for u, e in data.items():
            e.setdefault('sursa', 'linkurile tale' if cheie(u) in tale else 'profil')
        data = {'linkuri': data}
    data['versiune'] = 2
    for k in ('linkuri', 'site', 'cautare'):
        data.setdefault(k, {})
    data.setdefault('sabloane', [])
    for e in data['linkuri'].values():
        e.setdefault('istoric', [])
        e.setdefault('stare', NUPOT)
        e.setdefault('motiv', 'încă neverificat')
        e.setdefault('ultima', None)
        e.setdefault('sursa', 'profil')
    return data


def salveaza(stare):
    tmp = STATE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(stare, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def linkurile_tale():
    if not os.path.exists(LINKS):
        return []
    out = []
    with open(LINKS, encoding='utf-8-sig') as f:
        for line in f:
            if line.strip() and not line.strip().startswith('#'):
                out += gaseste_linkuri(line)
    return out


def index(stare):
    return {cheie(u): u for u in stare['linkuri']}


def adauga(stare, idx, url, sursa, cand):
    """Adaugă un link nou (dacă nu există deja). Întoarce (intrarea, e_nou)."""
    k = cheie(url)
    if k in idx:
        return stare['linkuri'][idx[k]], False
    e = {'gasit': None if sursa == 'profil' else cand, 'adaugat': cand, 'sursa': sursa,
         'istoric': [], 'stare': NUPOT, 'motiv': 'încă neverificat', 'ultima': None}
    stare['linkuri'][url] = e
    idx[k] = url
    return e, True


def efectiv(e):
    """Starea de care ținem cont: verificarea ta manuală, altfel ultima verificare automată."""
    if e.get('manual'):
        return e['manual']['stare']
    if e['stare'] == NUPOT:
        sigure = [i['stare'] for i in e['istoric'] if i['stare'] in (ONLINE, STERS)]
        if sigure and sigure[-1] == STERS:
            return STERS   # ultima dată știam că e șters
    return e['stare']


def recalculeaza(e, cand):
    ef = efectiv(e)
    if ef == STERS and (e.get('gasit') or e.get('manual')):
        e.setdefault('sters', cand)
    elif ef == ONLINE:
        e.pop('sters', None)


def actualizeaza(e, st, motiv, cand):
    prev = e['istoric'][-1]['stare'] if e['istoric'] else None
    if st != prev:
        e['istoric'].append({'data': cand, 'stare': st, 'motiv': motiv})
        if st in (ONLINE, STERS):
            e.pop('manual', None)   # s-a schimbat ceva de la verificarea ta
    e['ultima'], e['stare'], e['motiv'] = cand, st, motiv
    if st == ONLINE and not e.get('gasit'):
        e['gasit'] = cand
    recalculeaza(e, cand)


def ignorat(stare, url, e):
    return bool(e.get('ignorat') or stare['site'].get(domeniu(url), {}).get('ignorat') or e_propriu(url))


# ───────────── Profilurile (adresele învățate) ─────────────
def sablon_din(url):
    """https://site.com/model/kristinemaia/123 → https://site.com/model/{u}/"""
    p = urllib.parse.urlsplit(url)
    h = gazda(url)
    if not h or platforma_mare(h) or e_propriu(url) or e_motor(url):
        return None
    segs = p.path.split('/')
    for i, seg in enumerate(segs):
        s = seg.lower()
        for pref in ('', '@', '%40'):
            for n in NUME:
                for k, v in variante(n).items():
                    if s == pref + v:
                        esc = [x.replace('{', '{{').replace('}', '}}') for x in segs[:i]]
                        cale = '/'.join(esc + [pref + '{' + k + '}'])
                        if i < len(segs) - 1:
                            cale += '/'
                        return f'{p.scheme}://{p.netloc.lower()}{cale}'
    return None


def invata_sabloane(stare):
    noi = set()
    for url, e in stare['linkuri'].items():
        if ignorat(stare, url, e) or not (e.get('gasit') or e['sursa'] != 'profil'):
            continue
        s = sablon_din(url)
        if s:
            noi.add(s)
    vechi = set(stare['sabloane'])
    stare['sabloane'] = sorted(noi)
    return len(noi - vechi - set(SABLOANE))


def genereaza_profiluri(stare, idx, cand):
    for s in SABLOANE + stare['sabloane']:
        for n in NUME:
            try:
                adauga(stare, idx, s.format(**variante(n)), 'profil', cand)
            except (KeyError, IndexError, ValueError):
                pass


# ───────────── Verificarea unei pagini ─────────────
def verifica(url):
    try:
        final, body = cere(url, {'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8'})
        body = body.lower()
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return STERS, f'eroare {e.code}: pagina nu mai există'
        if e.code == 451:
            return NUPOT, '451: blocat legal în țara ta'
        try:
            corp = e.read(30000).decode('utf-8', 'ignore').lower()
        except Exception:
            corp = ''
        if any(b in corp for b in BLOCAT):
            return NUPOT, 'protecție Cloudflare sau blocare (deschide-l tu în browser)'
        return NUPOT, f'eroare {e.code} (protecție sau blocare)'
    except (socket.timeout, TimeoutError):
        return NUPOT, 'nu răspunde (poate e blocat în țară)'
    except urllib.error.URLError as e:
        r = e.reason
        if isinstance(r, socket.gaierror):
            return NUPOT, 'adresa nu se găsește (site închis sau blocat în țară)'
        if isinstance(r, (socket.timeout, TimeoutError)):
            return NUPOT, 'nu răspunde (poate e blocat în țară)'
        if isinstance(r, ssl.SSLError):
            return NUPOT, 'problemă de certificat la site'
        return NUPOT, 'nu se poate conecta (poate e blocat în țară)'
    except Exception as e:
        return NUPOT, type(e).__name__ + ': ' + str(e)[:80]
    m = re.search(r'<title[^>]*>(.*?)</title>', body[:60000], re.S)
    titlu = re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''
    if any(b in titlu or b in body[:20000] for b in BLOCAT):
        return NUPOT, 'pagină de blocare (Cloudflare sau blocare în țară)'
    if any(g in titlu for g in GOL_TITLU) or titlu in ('404', '410'):
        return STERS, 'pagina spune că nu există'
    p0, p1 = urllib.parse.urlsplit(url), urllib.parse.urlsplit(final)
    if p1.path in ('', '/') and p0.path not in ('', '/') and not p1.query:
        return STERS, 'te trimite la prima pagină a site-ului'
    if not are_nume(body):
        return STERS, 'numele nu mai apare pe pagină' + (' (redirecționat)' if final.rstrip('/') != url.rstrip('/') else '')
    if any(g in body for g in GOL_CORP) and sum(body.count(v) for v in NUME_TEXT) < 3:
        return STERS, 'pagina spune că nu există'
    return ONLINE, 'pagina există și conține numele'


def verifica_toate(stare, urls, cand, arata=True):
    if not urls:
        return
    gata = 0
    with ThreadPoolExecutor(FIRE) as ex:
        viitor = {ex.submit(verifica, u): u for u in urls}
        for f in as_completed(viitor):
            st, motiv = f.result()
            actualizeaza(stare['linkuri'][viitor[f]], st, motiv, cand)
            gata += 1
            if arata and (gata % 10 == 0 or gata == len(urls)):
                print(f'\r  verificate: {gata}/{len(urls)}', end='', flush=True)
    if arata:
        print()


# ───────────── Căutarea pe Google / Bing ─────────────
def citeste_chei():
    if not os.path.exists(KEYS):
        with open(KEYS, 'w', encoding='utf-8') as f:
            f.write('# Lipește cheia după semnul =, fără spații. Fișierul rămâne doar pe laptopul tău.\n'
                    '# SerpApi (Google, Bing, Yandex; 250 de căutări gratuite pe lună): serpapi.com → Dashboard → Your Private API Key\n'
                    'SERPAPI=\n'
                    '# Brave (opțional, alt motor de căutare): api-dashboard.search.brave.com → API Keys\n'
                    'BRAVE=\n')
    chei = {}
    with open(KEYS, encoding='utf-8-sig') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                if v.strip():
                    chei[k.strip().upper()] = v.strip()
    return chei


def _rezultate(lista, motor, camp='link'):
    return [(r.get(camp) or '', r.get('title') or '', r.get('snippet') or r.get('description') or '', motor)
            for r in lista or [] if isinstance(r, dict)]


def cereri_serpapi():
    q = [f'"{t}"' for t in CAUTARI]
    plan = {
        'google': [('Google', {'engine': 'google', 'q': x, 'safe': 'off', 'filter': '0', 'hl': 'en', 'gl': 'us'}) for x in q],
        'bing': [('Bing', {'engine': 'bing', 'q': x, 'safeSearch': 'off', 'count': '50', 'cc': 'US'}) for x in q],
        'google_imagini': [('Google Imagini', {'engine': 'google_images', 'q': x, 'safe': 'off', 'hl': 'en', 'gl': 'us'}) for x in q],
        'yandex': [('Yandex', {'engine': 'yandex', 'text': x}) for x in q],
        'google_pagina2': [('Google', {'engine': 'google', 'q': x, 'safe': 'off', 'filter': '0', 'hl': 'en', 'gl': 'us', 'start': '10'}) for x in q],
    }
    return [c for m in MOTOARE for c in plan.get(m, [])]


def cauta_serpapi(k, stare, mesaje):
    luna = datetime.now().strftime('%Y-%m')
    folosite = stare['cautare'].setdefault('luna', {})
    ramase = LIMITA_SERPAPI - folosite.get(luna, 0)
    try:
        cont = cere_json(f'{SERPAPI_URL}/account.json?' + urllib.parse.urlencode({'api_key': k}))
        if cont.get('error'):
            mesaje.append('SerpApi: ' + str(cont['error'])[:120])
            return [], 0
        ramase = int(cont.get('plan_searches_left', cont.get('total_searches_left', ramase)) or 0)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            mesaje.append('SerpApi: cheia nu e bună. Copiaz-o din nou în chei.txt.')
            return [], 0
    except Exception:
        pass   # nu știm câte au rămas: ne bazăm pe numărătoarea noastră
    cereri = cereri_serpapi()[:max(0, min(MAX_CAUTARI_PE_RULARE, ramase - 2))]
    if not cereri:
        mesaje.append('SerpApi: s-au terminat căutările gratuite pe luna asta. Reîncep luna viitoare.')
        return [], 0
    out, facute, motoare = [], 0, []
    for motor, params in cereri:
        try:
            d = cere_json(f'{SERPAPI_URL}/search.json?' + urllib.parse.urlencode({**params, 'api_key': k}))
        except urllib.error.HTTPError as e:
            mesaje.append('SerpApi: ' + ('cheia nu e bună.' if e.code == 401 else
                                         's-au terminat căutările pe luna asta.' if e.code == 429 else f'eroare {e.code}.'))
            break
        except Exception as e:
            mesaje.append(f'SerpApi nu răspunde ({type(e).__name__}).')
            break
        facute += 1
        if d.get('error') and 'any results' not in str(d['error']):
            mesaje.append('SerpApi: ' + str(d['error'])[:120])
            continue
        out += _rezultate(d.get('organic_results'), motor) + _rezultate(d.get('images_results'), motor)
        if motor not in motoare:
            motoare.append(motor)
    folosite[luna] = folosite.get(luna, 0) + facute
    if facute:
        mesaje.append(f'SerpApi: {nr(facute, "căutare", "căutări")} ({", ".join(motoare)}); '
                      f'mai ai ~{nr(max(0, ramase - facute), "căutare", "căutări")} luna asta.')
    return out, facute


def cauta_brave(k, mesaje):
    out, facute = [], 0
    for t in CAUTARI:
        for pagina in (0, 1):
            url = BRAVE_URL + '?' + urllib.parse.urlencode({'q': f'"{t}"', 'count': 20, 'offset': pagina, 'safesearch': 'off'})
            try:
                d = cere_json(url, {'X-Subscription-Token': k})
            except urllib.error.HTTPError as e:
                mesaje.append('Brave: ' + ('cheia nu e bună.' if e.code in (401, 403) else
                                           's-a atins limita.' if e.code == 429 else f'eroare {e.code}.'))
                return out, facute
            except Exception as e:
                mesaje.append(f'Brave nu răspunde ({type(e).__name__}).')
                return out, facute
            facute += 1
            out += _rezultate((d.get('web') or {}).get('results'), 'Brave', 'url')
            time.sleep(1.1)   # planul gratuit: o căutare pe secundă
    mesaje.append(f'Brave: {nr(facute, "căutare", "căutări")}.')
    return out, facute


def relevant(url, titlu, text):
    if not url.lower().startswith(('http://', 'https://')) or not gazda(url):
        return False
    if e_propriu(url) or e_motor(url):
        return False
    return are_nume(urllib.parse.unquote(url) + ' ' + titlu + ' ' + text)


def cauta(stare, idx, cand, fortat=False):
    """Întoarce un text scurt despre căutare (pentru raport și ecran)."""
    info = stare['cautare']
    chei = citeste_chei()
    if not (chei.get('SERPAPI') or chei.get('BRAVE')):
        info['text'] = 'Căutarea pe Google/Bing e oprită: pune cheia SerpApi în chei.txt (vezi CITESTE.md).'
        return info['text']
    if not fortat and info.get('ultima') and zile_de_la(info['ultima']) < ZILE_INTRE_CAUTARI:
        rest = ZILE_INTRE_CAUTARI - zile_de_la(info['ultima'])
        return f'Ultima căutare pe Google/Bing: {scurt(info["ultima"])}. Următoarea peste {nr(rest, "zi", "zile")} (sau rulează cu --cauta).'
    mesaje, rez, facute = [], [], 0
    for nume, fn in (('SERPAPI', lambda k: cauta_serpapi(k, stare, mesaje)), ('BRAVE', lambda k: cauta_brave(k, mesaje))):
        if chei.get(nume):
            r, f = fn(chei[nume])
            rez, facute = rez + r, facute + f
    noi, site_noi = 0, set()
    stiute = {domeniu(u) for u in stare['linkuri']}
    for url, titlu, text, motor in rez:
        if not relevant(url, titlu, text):
            continue
        e, nou = adauga(stare, idx, url, motor, cand)
        e.setdefault('in_cautare', {})[motor] = cand[:10]
        if nou:
            noi += 1
            if domeniu(url) not in stiute:
                site_noi.add(domeniu(url))
    if not facute:   # n-a mers deloc: încearcă din nou data viitoare
        info['text'] = 'Căutarea pe Google/Bing n-a mers: ' + ' '.join(mesaje)
        return info['text']
    info['ultima'] = cand
    info['text'] = (f'Căutare pe Google/Bing: {scurt(cand)}, {nr(noi, "link nou", "linkuri noi")}'
                    + (f' pe {nr(len(site_noi), "site nou", "site-uri noi")}.' if site_noi else '.') + ' ' + ' '.join(mesaje))
    info['site_noi'] = sorted(site_noi)
    return info['text']


# ───────────── Unde e găzduit site-ul ─────────────
def _vcard(ent, camp):
    for item in (ent.get('vcardArray') or [None, []])[1]:
        if isinstance(item, list) and len(item) > 3 and item[0] == camp:
            v = item[3]
            return v[0] if isinstance(v, list) else v
    return None


def _entitati(obj):
    for e in obj.get('entities') or []:
        yield e
        yield from _entitati(e)


def afla_gazda(host):
    try:
        d = cere_json(DOH_URL + '?' + urllib.parse.urlencode({'name': host, 'type': 'A'}), timp=10)
        ips = [a['data'] for a in d.get('Answer') or [] if a.get('type') == 1]
        if not ips:
            return None
        r = cere_json(RDAP_URL + ips[0], timp=15)
    except Exception:
        return None
    nume = email = None
    for e in _entitati(r):
        roluri = e.get('roles') or []
        if 'abuse' in roluri and not email:
            email = _vcard(e, 'email')
        if ('registrant' in roluri or 'administrative' in roluri) and not nume:
            nume = _vcard(e, 'fn')
    nume = nume or r.get('name') or '?'
    text = (nume + ' ' + str(r.get('name', ''))).lower()
    return {'nume': 'Cloudflare' if 'cloudflare' in text else nume, 'email': email, 'tara': r.get('country'),
            'ip': ips[0], 'cloudflare': 'cloudflare' in text, 'data': date.today().isoformat()}


def actualizeaza_gazde(stare):
    de_aflat = {}
    for url, e in stare['linkuri'].items():
        if ignorat(stare, url, e) or categorie(e) != 'activ':
            continue
        dom = domeniu(url)
        g = stare['site'].get(dom, {}).get('gazda')
        if dom not in de_aflat and (not g or zile_de_la(g['data']) > 30):
            de_aflat[dom] = gazda(url)
    if not de_aflat:
        return
    with ThreadPoolExecutor(6) as ex:
        for dom, g in zip(de_aflat, ex.map(afla_gazda, de_aflat.values())):
            if g:
                stare['site'].setdefault(dom, {})['gazda'] = g


# ───────────── Ce ai de trimis ─────────────
def categorie(e):
    if e['sursa'] == 'profil' and not e.get('gasit') and not e.get('manual'):
        return 'neverificat' if e['stare'] == NUPOT else None   # profil ghicit care n-a existat
    return 'sters' if efectiv(e) == STERS else 'activ'


def stare_canal(canal, linkuri):
    """Pentru un site: ce mai e de făcut pe canalul ăsta (Google, Bing, site, hosting)."""
    stari = []
    for e in linkuri:
        t = e.get('trimis') or {}
        d = t.get(canal)
        if canal == 'gazda' and not d:
            ds = t.get('site')
            stari.append(('de_trimis', None) if ds and zile_de_la(ds) >= ZILE_REVENIRE_SITE else ('mai_tarziu', ds))
        elif not d:
            stari.append(('de_trimis', None))
        elif canal in MOTOR_CANAL:
            vazut = max([v for m, v in (e.get('in_cautare') or {}).items() if m in MOTOR_CANAL[canal]], default=None)
            stari.append(('de_revenit', d) if vazut and (zi(vazut) - zi(d)).days >= ZILE_REVENIRE else ('trimis', d))
        else:
            lim = ZILE_REVENIRE_SITE if canal == 'site' else ZILE_REVENIRE
            stari.append(('de_revenit', d) if zile_de_la(d) >= lim else ('trimis', d))
    for s in ('de_trimis', 'de_revenit', 'mai_tarziu', 'trimis'):
        if any(x[0] == s for x in stari):
            date_ = sorted(x[1] for x in stari if x[0] == s and x[1])
            return s, sum(1 for x in stari if x[0] == s), date_
    return 'trimis', 0, []


def canal_vedere(cid, nume, linkuri, g):
    st, k, date_ = stare_canal(cid, linkuri)
    n = len(linkuri)
    are_data = any((e.get('trimis') or {}).get(cid) for e in linkuri)
    if st == 'de_trimis':
        text, buton = 'de trimis' + (f' ({k} din {nr(n, "link", "linkuri")})' if k < n else ''), 'Am trimis'
        if cid == 'gazda':
            text = 'site-ul n-a șters în 7 zile → trimite la hosting'
    elif st == 'de_revenit':
        d = scurt(date_[0])
        text = {'site': f'trimis pe {d}, n-a șters → trimite revenirea',
                'gazda': f'trimis pe {d}, tot online → scrie din nou (vezi pașii din plan)'}.get(
            cid, f'trimis pe {d}, dar după 2 săptămâni încă apare în {nume} → verifică răspunsul și retrimite')
        buton = 'Am trimis din nou'
    elif st == 'mai_tarziu':
        text = (f'din {scurt((zi(date_[0]) + timedelta(days=ZILE_REVENIRE_SITE)).isoformat())}, dacă site-ul nu șterge'
                if date_ else 'după site, dacă nu șterge în 7 zile')
        buton = 'Am trimis deja'
    else:
        text = 'trimis pe ' + scurt(date_[0]) + (f' – {scurt(date_[-1])}' if date_ and date_[-1] != date_[0] else '')
        buton = None
    linkuri_ajutor, ajutor = FORMULARE.get(cid, []), None
    if cid == 'site':
        ajutor = 'textul A, B sau C din plan, la contactul sau DMCA-ul site-ului'
    if cid == 'gazda':
        if g and g.get('cloudflare'):
            linkuri_ajutor = FORMULARE['cloudflare']
        elif g and g.get('email'):
            ajutor = 'adresa de abuz: ' + g['email']
        elif g:
            ajutor = f'găzduit la {g["nume"]}' + (f' ({g["tara"]})' if g.get('tara') else '') + ', adresa de abuz nu e publică'
        else:
            ajutor = 'nu știu încă unde e găzduit'
    return {'id': cid, 'nume': nume, 'stare': st, 'text': text, 'buton': buton, 'are_data': are_data,
            'ajutor': ajutor, 'email': (g or {}).get('email') if cid == 'gazda' and not (g or {}).get('cloudflare') else None,
            'linkuri': linkuri_ajutor}


def in_cautare_text(e, dupa=None):
    v = [(m, d) for m, d in (e.get('in_cautare') or {}).items() if not dupa or d >= dupa[:10]]
    return ' · '.join(f'{m} {scurt(d)}' for m, d in sorted(v)) or None


def text_cautare(info):
    t = info.get('text') or ''
    if info.get('ultima') and t.startswith('Căutare pe'):
        t += f" Următoarea: {scurt((zi(info['ultima']) + timedelta(days=ZILE_INTRE_CAUTARI)).isoformat())}."
    return t


def e_nou(e):
    return e['sursa'] not in SURSE_TALE and bool(e.get('gasit')) and zile_de_la(e['gasit']) < ZILE_NOU


def vedere(stare, interactiv=False, token=''):
    """Tot ce arată raportul, gata calculat."""
    grupuri, sterse, neverificate, ignorate = {}, [], [], []
    dom_ignorate = set()
    for url, e in stare['linkuri'].items():
        dom = domeniu(url)
        if e_propriu(url):
            continue
        cat = categorie(e)
        if stare['site'].get(dom, {}).get('ignorat'):
            if cat:
                dom_ignorate.add(dom)
            continue
        if e.get('ignorat'):
            if cat:
                ignorate.append({'url': url, 'domeniu': dom})
            continue
        if cat == 'activ':
            grupuri.setdefault(dom, []).append((url, e))
        elif cat == 'sters':
            sterse.append({'url': url, 'domeniu': dom, 'gasit': scurt(e.get('gasit')), 'sters': scurt(e.get('sters')),
                           'sters_iso': (e.get('sters') or '')[:10], 'manual': bool(e.get('manual')),
                           'in_cautare': in_cautare_text(e, e.get('sters'))})
        elif cat == 'neverificat':
            neverificate.append({'url': url, 'domeniu': dom, 'motiv': e['motiv']})
    out = []
    for dom, lst in grupuri.items():
        lst.sort(key=lambda x: (efectiv(x[1]) != ONLINE, x[0]))
        es = [e for _, e in lst]
        g = stare['site'].get(dom, {}).get('gazda')
        canale = [canal_vedere(cid, nume, es, g) for cid, nume in CANALE]
        stari = {k['stare'] for k in canale}
        cat = 'de_trimis' if 'de_trimis' in stari else 'de_revenit' if 'de_revenit' in stari else 'astept'
        gasit = min((e['gasit'] for e in es if e.get('gasit')), default=None)
        out.append({
            'domeniu': dom, 'categorie': cat, 'gazda': g, 'canale': canale,
            'nou': all(e['sursa'] not in SURSE_TALE for e in es) and bool(gasit) and zile_de_la(gasit) < ZILE_NOU,
            'linkuri': [{'url': u, 'ef': efectiv(e), 'motiv': e['motiv'], 'sursa': e['sursa'], 'gasit': scurt(e.get('gasit')),
                         'nou': e_nou(e), 'manual': bool(e.get('manual')), 'cautare': in_cautare_text(e),
                         'ultima_online': scurt(next((i['data'] for i in reversed(e['istoric']) if i['stare'] == ONLINE), None))}
                        for u, e in lst]})
    ordine = {'de_trimis': 0, 'de_revenit': 1, 'astept': 2}
    out.sort(key=lambda g: (ordine[g['categorie']], not g['nou'], -len(g['linkuri']), g['domeniu']))
    sterse.sort(key=lambda s: (s['sters_iso'], s['url']), reverse=True)
    activ = [l for g in out for l in g['linkuri']]
    rez = {
        'de_trimis': sum(g['categorie'] == 'de_trimis' for g in out),
        'de_trimis_linkuri': sum(len(g['linkuri']) for g in out if g['categorie'] == 'de_trimis'),
        'de_revenit': sum(g['categorie'] == 'de_revenit' for g in out),
        'astept': sum(g['categorie'] == 'astept' for g in out),
        'online': sum(l['ef'] == ONLINE for l in activ), 'neverificate_active': sum(l['ef'] != ONLINE for l in activ),
        'noi': sum(l['nou'] for l in activ), 'sterse': len(sterse), 'neverificate': len(neverificate),
        'nesters_google': sum(1 for lst in grupuri.values() for _, e in lst if not (e.get('trimis') or {}).get('google')),
        'nesters_bing': sum(1 for lst in grupuri.values() for _, e in lst if not (e.get('trimis') or {}).get('bing')),
    }
    return {'generat': scurt(acum()) + ' ' + acum()[11:], 'azi': date.today().isoformat(),
            'azi_ro': date.today().strftime('%d.%m.%Y'), 'interactiv': interactiv, 'token': token,
            'cautare_text': text_cautare(stare['cautare']), 'rezumat': rez, 'grupuri': out, 'sterse': sterse,
            'neverificate': sorted(neverificate, key=lambda x: x['url']),
            'ignorate': sorted(ignorate, key=lambda x: x['url']) + [{'domeniu': d, 'tot_site': True} for d in sorted(dom_ignorate)],
            'formulare': FORMULARE, 'zile_site': ZILE_REVENIRE_SITE}


# ───────────── Ce apeși în raport ─────────────
def aplica(stare, a):
    tip, cand = a.get('tip'), acum()
    if tip == 'trimis':
        canal, d = a.get('canal'), a.get('data')
        if canal not in dict(CANALE):
            raise ValueError('canal necunoscut')
        if d is not None and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(d)):
            raise ValueError('data nu e bună')
        if d:
            date.fromisoformat(d)
        for url, e in stare['linkuri'].items():
            if (a.get('toate') or domeniu(url) == a.get('domeniu')) and not ignorat(stare, url, e) and categorie(e) == 'activ':
                if d:
                    e.setdefault('trimis', {})[canal] = d
                else:
                    (e.get('trimis') or {}).pop(canal, None)
    elif tip == 'manual':
        e = stare['linkuri'][a['url']]
        if a.get('stare') in (ONLINE, STERS):
            e['manual'] = {'stare': a['stare'], 'data': cand}
            if a['stare'] == ONLINE and not e.get('gasit'):
                e['gasit'] = cand
        else:
            e.pop('manual', None)
        recalculeaza(e, cand)
    elif tip == 'ignora':
        if a.get('url'):
            e = stare['linkuri'][a['url']]
            if a.get('valoare', True):
                e['ignorat'] = cand
            else:
                e.pop('ignorat', None)
        elif a.get('domeniu'):
            s = stare['site'].setdefault(a['domeniu'], {})
            if a.get('valoare', True):
                s['ignorat'] = cand
            else:
                s.pop('ignorat', None)
    elif tip == 'adauga':
        idx, noi = index(stare), []
        for u in gaseste_linkuri(str(a.get('text', ''))[:200_000]):
            e, nou = adauga(stare, idx, u, 'adăugat de tine', cand)
            if not nou and e['sursa'] == 'profil':
                e['sursa'], e['gasit'] = 'adăugat de tine', e.get('gasit') or cand
            e.pop('ignorat', None)
            noi.append(idx[cheie(u)])
        verifica_toate(stare, noi, cand, arata=False)
        invata_sabloane(stare)
    else:
        raise ValueError('acțiune necunoscută')


# ───────────── Raportul ─────────────
def pagina(v):
    date_ = json.dumps(v, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return PAGINA.replace('__DATE__', date_)


def scrie_raport(stare):
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(pagina(vedere(stare)))


def porneste_server(stare):
    token, lacat = secrets.token_urlsafe(16), threading.Lock()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _raspunde(self, cod, corp, tip='text/plain; charset=utf-8'):
            b = corp.encode('utf-8')
            self.send_response(cod)
            self.send_header('Content-Type', tip)
            self.send_header('Content-Length', str(len(b)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.end_headers()
            self.wfile.write(b)

        def _local(self):
            return self.headers.get('Host', '').rsplit(':', 1)[0] in ('127.0.0.1', 'localhost')

        def do_GET(self):
            if not self._local():
                return self._raspunde(403, 'Interzis')
            if self.path.split('?')[0] != '/':
                return self._raspunde(404, 'Nu există')
            with lacat:
                corp = pagina(vedere(stare, True, token))
            self._raspunde(200, corp, 'text/html; charset=utf-8')

        def do_POST(self):
            if not self._local() or self.path != '/actiune':
                return self._raspunde(403, 'Interzis')
            try:
                n = int(self.headers.get('Content-Length') or 0)
                if n > 2_000_000:
                    raise ValueError('prea mult text')
                a = json.loads(self.rfile.read(n).decode('utf-8'))
                if not secrets.compare_digest(str(a.get('token', '')), token):
                    return self._raspunde(403, 'Pagina e veche: reîncarc-o (F5).')
                with lacat:
                    aplica(stare, a)
                    salveaza(stare)
                    scrie_raport(stare)
                    corp = json.dumps(vedere(stare, True, token), ensure_ascii=False)
                self._raspunde(200, corp, 'application/json; charset=utf-8')
            except Exception as e:
                self._raspunde(400, f'{type(e).__name__}: {e}')

    srv = None
    for port in list(range(8765, 8776)) + [0]:
        try:
            srv = ThreadingHTTPServer(('127.0.0.1', port), H)
            break
        except OSError:
            continue
    url = f'http://127.0.0.1:{srv.server_address[1]}/'
    print(f'\nRaportul: {url}')
    print('Lasă fereastra asta deschisă cât bifezi în raport. Când termini, o închizi.')
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('Oprit.')


def rezumat_ecran(v):
    r = v['rezumat']
    print('\nGata.')
    s = lambda n: nr(n, 'site', 'site-uri')
    print(f"  📮 De trimis:      {s(r['de_trimis'])} ({nr(r['de_trimis_linkuri'], 'link', 'linkuri')})")
    print(f"  ⏰ De revenit:     {s(r['de_revenit'])}")
    print(f"  ⏳ Aștept răspuns: {s(r['astept'])}")
    print(f"  🆕 Linkuri noi:    {r['noi']} (găsite singur, în ultimele {ZILE_NOU} zile)")
    print(f"  🟢 Șterse:         {nr(r['sterse'], 'link', 'linkuri')}")
    if v['cautare_text']:
        print('  ' + v['cautare_text'])


def main():
    try:
        sys.stdout.reconfigure(errors='replace')   # ecranele vechi de Windows nu știu toate semnele
    except Exception:
        pass
    arg = set(sys.argv[1:])
    stare = incarca()
    if '--raport' not in arg:
        cand = acum()
        idx = index(stare)
        tale = linkurile_tale()
        for u in tale:
            e, _ = adauga(stare, idx, u, 'linkurile tale', cand)
            if e['sursa'] not in SURSE_TALE:
                e['sursa'], e['gasit'] = 'linkurile tale', e.get('gasit') or cand
        if '--fara-cautare' not in arg:
            print('Caut numele tale pe Google, Bing și celelalte...')
            print('  ' + cauta(stare, idx, cand, fortat='--cauta' in arg))
        n = invata_sabloane(stare)
        if n:
            print(f'  Am învățat {nr(n, "adresă de profil nouă", "adrese de profil noi")} (le verific pentru toate numele tale).')
        genereaza_profiluri(stare, idx, cand)
        de_verificat = [u for u, e in stare['linkuri'].items() if not ignorat(stare, u, e)]
        print(f'Verific {len(de_verificat)} adrese... (durează 1–3 minute)')
        verifica_toate(stare, de_verificat, cand)
        print('Caut unde e găzduit fiecare site...')
        actualizeaza_gazde(stare)
        salveaza(stare)
    scrie_raport(stare)
    rezumat_ecran(vedere(stare))
    if '--fara-server' in arg:
        print('Deschide raport.html în browser.')
    else:
        porneste_server(stare)


PAGINA = r'''<!doctype html>
<html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer"><title>Evidența ștergerilor</title>
<style>
:root{--bg:#faf7f5;--card:#fff;--ink:#1f1f1f;--mut:#666;--line:#ebe4df;--rosu:#b71c1c;--rosu-bg:#fdecea;--port:#9a5200;
--port-bg:#fff2dc;--verde:#2e6b31;--verde-bg:#e7f4e8;--gri-bg:#f2efec;--acc:#8e3b63;--acc-bg:#fbe7f0}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1080px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 8px}h3{font-size:17px;margin:0}
.sub,.mut{color:var(--mut)}.sub{margin:0 0 14px;font-size:14px}
.banner{background:var(--port-bg);border:1px solid #efd3a6;padding:10px 14px;border-radius:8px;margin:12px 0}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px}
.tile b{display:block;font-size:28px;line-height:1.15}.tile small{color:var(--mut)}
.tile.r b{color:var(--rosu)}.tile.o b{color:var(--port)}.tile.v b{color:var(--verde)}.tile.n b{color:var(--acc)}
.box{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px}
.box ol{margin:6px 0 4px;padding-left:22px}.box li{margin:3px 0}
.card{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--rosu);border-radius:10px;padding:14px 16px;margin:12px 0}
.card.de_revenit{border-left-color:#e08a00}.card.astept{border-left-color:#a7a09b}
.ch{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin-bottom:10px}
.tag{font-size:12px;background:var(--gri-bg);border-radius:20px;padding:2px 9px}
.tag.nou{background:var(--acc-bg);color:var(--acc);font-weight:600}
.canale{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:8px}
.canal{border-radius:8px;padding:9px 11px;background:var(--gri-bg);display:flex;flex-direction:column;gap:3px}
.canal.de_trimis{background:var(--rosu-bg)}.canal.de_revenit{background:var(--port-bg)}.canal.trimis{background:var(--verde-bg)}
.cn{font-weight:700}.ct{font-size:14px}.canal.de_trimis .ct{color:var(--rosu);font-weight:600}
.canal.de_revenit .ct{color:var(--port);font-weight:600}.canal.trimis .ct{color:var(--verde)}
.ca{font-size:13px;color:var(--mut);word-break:break-word}
.cb{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;margin-top:3px;font-size:13px}
button{font:inherit;font-size:14px;border:0;border-radius:6px;padding:6px 12px;background:var(--acc);color:#fff;cursor:pointer}
button:hover{filter:brightness(1.08)}button:disabled{opacity:.5;cursor:wait}
button.sec{background:#fff;color:var(--ink);border:1px solid #d5cdc7}
button.mic{padding:2px 8px;font-size:13px;background:#fff;color:var(--ink);border:1px solid #d5cdc7}
a{color:#7a2d55}.u{word-break:break-all}
details{margin-top:8px}summary{cursor:pointer;color:var(--mut)}
.ll{list-style:none;padding:0;margin:8px 0 0}.ll li{padding:8px 0;border-top:1px solid var(--line)}
.meta{font-size:13px;color:var(--mut)}.acts{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:1px}
.dot.r{background:var(--rosu)}.dot.o{background:#e09b2d}.dot.v{background:var(--verde)}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;background:#fff;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}th{background:var(--gri-bg)}
textarea{width:100%;min-height:90px;font:inherit;font-size:14px;padding:8px;border:1px solid #d5cdc7;border-radius:6px;margin:6px 0}
.ok{color:var(--verde);font-weight:600}.help li{margin:5px 0}
</style></head><body><main id="app"></main>
<script type="application/json" id="date">__DATE__</script>
<script>
'use strict';
let D = JSON.parse(document.getElementById('date').textContent);
const LIVE = !!D.interactiv && location.protocol.startsWith('http');
const deschise = new Set();
const nr = (n, unu, multe) => n === 1 ? '1 ' + unu : n + ' ' + (n >= 20 && (n % 100 === 0 || n % 100 >= 20) ? 'de ' : '') + multe;

function h(tag, at, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(at || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (k === 'href') { if (/^https?:\/\//i.test(v)) el.href = v; }
    else el.setAttribute(k, v === true ? '' : v);
  }
  el.append(...curata(kids));
  return el;
}
function curata(kids) {
  return kids.flat(4).filter(c => c != null && c !== false && c !== '').map(c => c instanceof Node ? c : String(c));
}
function det(key, sum, ...kids) {
  const d = h('details', {}, h('summary', {}, sum), ...kids);
  if (deschise.has(key)) d.open = true;
  d.addEventListener('toggle', () => d.open ? deschise.add(key) : deschise.delete(key));
  return d;
}
const ext = (url, text) => h('a', {href: url, target: '_blank', rel: 'noreferrer noopener'}, text);

async function act(a, btn) {
  if (!LIVE) return;
  if (btn) btn.disabled = true;
  try {
    const r = await fetch('/actiune', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                       body: JSON.stringify({...a, token: D.token})});
    if (!r.ok) throw new Error(await r.text());
    D = await r.json();
    randeaza();
  } catch (e) {
    alert('Nu s-a salvat. Fereastra neagră a programului e închisă? Pornește din nou raport.bat.\n\n' + e.message);
    if (btn) btn.disabled = false;
  }
}
function copiaza(text, btn) {
  const ok = () => { const t = btn.textContent; btn.textContent = 'Copiat ✓'; setTimeout(() => { btn.textContent = t; }, 1600); };
  const vechi = () => {
    const ta = h('textarea'); ta.value = text; document.body.append(ta); ta.select();
    try { document.execCommand('copy') ? ok() : prompt('Copiază de aici (Ctrl+C):', text); }
    catch (e) { prompt('Copiază de aici (Ctrl+C):', text); }
    ta.remove();
  };
  if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(ok, vechi); else vechi();
}
function cereData(implicit) {
  const r = prompt('Data trimiterii (zz.ll.aaaa). Lasă gol ca să ștergi bifa.', implicit);
  if (r === null) return undefined;
  if (!r.trim()) return null;
  const m = r.trim().match(/^(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{4})$/);
  if (!m) { alert('Scrie data așa: ' + D.azi_ro); return undefined; }
  return m[3] + '-' + m[2].padStart(2, '0') + '-' + m[1].padStart(2, '0');
}

function canal(g, k) {
  return h('div', {class: 'canal ' + k.stare},
    h('div', {class: 'cn'}, k.nume),
    h('div', {class: 'ct'}, k.text),
    k.ajutor && h('div', {class: 'ca'}, k.ajutor),
    h('div', {class: 'cb'},
      LIVE && k.buton && h('button', {onclick: e => act({tip: 'trimis', domeniu: g.domeniu, canal: k.id, data: D.azi}, e.target)}, k.buton),
      LIVE && k.are_data && h('button', {class: 'mic', title: 'Schimbă data sau șterge bifa', onclick: e => {
        const d = cereData(D.azi_ro); if (d !== undefined) act({tip: 'trimis', domeniu: g.domeniu, canal: k.id, data: d}, e.target);
      }}, '✎ data'),
      k.email && h('button', {class: 'mic', onclick: e => copiaza(k.email, e.target)}, 'Copiază adresa'),
      k.linkuri.map(([t, u]) => ext(u, t + ' ↗'))));
}

function linkLi(l) {
  const on = l.ef === 'ONLINE';
  const meta = [on ? (l.manual ? 'online (verificat de tine)' : 'online')
                   : 'neverificat acum: ' + l.motiv + (l.ultima_online !== '—' ? ' · ultima dată online: ' + l.ultima_online : ''),
                'găsit ' + l.gasit + ' (' + l.sursa + ')', l.cautare && 'apare în ' + l.cautare].filter(Boolean).join(' · ');
  return h('li', {},
    h('span', {class: 'dot ' + (on ? 'r' : 'o')}), l.nou && h('span', {class: 'tag nou'}, '🆕 nou'), ' ',
    ext(l.url, l.url), h('div', {class: 'meta'}, meta),
    LIVE && h('div', {class: 'acts'},
      h('button', {class: 'mic', onclick: e => act({tip: 'manual', url: l.url, stare: 'ȘTERS'}, e.target)}, 'E șters (am verificat)'),
      !on && h('button', {class: 'mic', onclick: e => act({tip: 'manual', url: l.url, stare: 'ONLINE'}, e.target)}, 'Mai e online (am verificat)'),
      l.manual && h('button', {class: 'mic', onclick: e => act({tip: 'manual', url: l.url, stare: null}, e.target)}, 'Anulează verificarea mea'),
      h('button', {class: 'mic', onclick: e => act({tip: 'ignora', url: l.url, valoare: true}, e.target)}, 'Ascunde (nu e furat)')));
}

function card(g) {
  const on = g.linkuri.filter(l => l.ef === 'ONLINE').length, nv = g.linkuri.length - on;
  const urls = g.linkuri.map(l => l.url).join('\n');
  return h('div', {class: 'card ' + g.categorie, id: 's-' + g.domeniu},
    h('div', {class: 'ch'},
      h('h3', {}, g.domeniu), g.nou && h('span', {class: 'tag nou'}, '🆕 site nou'),
      g.gazda && h('span', {class: 'tag'}, 'găzduit: ' + g.gazda.nume),
      h('span', {class: 'mut'}, [on && on + ' online', nv && nr(nv, 'neverificat (blocat)', 'neverificate (blocat)')].filter(Boolean).join(' · ')),
      h('button', {class: 'sec', onclick: e => copiaza(urls, e.target)}, 'Copiază linkurile (' + g.linkuri.length + ')')),
    h('div', {class: 'canale'}, g.canale.map(k => canal(g, k))),
    det('l-' + g.domeniu, 'Linkurile (' + g.linkuri.length + ')',
      h('ul', {class: 'll'}, g.linkuri.map(linkLi)),
      LIVE && h('button', {class: 'mic', onclick: e => {
        if (confirm('Ascund tot site-ul ' + g.domeniu + ' din raport?')) act({tip: 'ignora', domeniu: g.domeniu, valoare: true}, e.target);
      }}, 'Nu e conținut furat: ascunde tot site-ul')));
}

function tile(cls, n, eticheta, mic) { return h('div', {class: 'tile ' + cls}, h('b', {}, n), eticheta, mic && h('br'), mic && h('small', {}, mic)); }

function todo(lista) {
  const R = D.rezumat;
  const box = h('div', {class: 'box'});
  if (!lista.length) box.append(h('p', {class: 'ok'}, 'Nimic de trimis acum. Ce e trimis așteaptă răspuns.'));
  else box.append(h('b', {}, 'Ce ai de trimis:'), h('ol', {}, lista.map(g => {
    const k = g.canale.filter(c => c.stare === 'de_trimis' || c.stare === 'de_revenit')
                      .map(c => c.nume + (c.stare === 'de_revenit' ? ' (revenire)' : ''));
    return h('li', {}, h('a', {href: '#s-' + g.domeniu}, g.domeniu), ': ' + k.join(', ') + ' · ' + nr(g.linkuri.length, 'link', 'linkuri'));
  })));
  if (LIVE && (R.nesters_google || R.nesters_bing)) {
    const tot = (canal, nume, n) => n > 0 && h('button', {class: 'sec', onclick: e => {
      const d = cereData(D.azi_ro);
      if (d && confirm('Bifez ' + nume + ' ca trimis pe ' + d.split('-').reverse().join('.') + ' pentru ' + (n === 1 ? 'linkul netrimis' : 'toate cele ' + nr(n, 'link', 'linkuri') + ' netrimise') + '?'))
        act({tip: 'trimis', toate: true, canal, data: d}, e.target);
    }}, 'Am trimis tot la ' + nume);
    box.append(h('p', {class: 'mut'}, 'Ai trimis deja o listă mare la Google sau Bing? Bifezi tot deodată: ',
      tot('google', 'Google', R.nesters_google), ' ', tot('bing', 'Bing', R.nesters_bing)));
  }
  return box;
}

function neverificate() {
  return h('div', {},
    h('p', {class: 'mut'}, 'Adrese de profil ghicite de program pe site-uri care nu s-au deschis (blocate în țară sau protejate). Deschide-le cu VPN: dacă există pagina cu numele tău, apasă „Există”.'),
    det('nev', 'Arată adresele (' + D.neverificate.length + ')', h('ul', {class: 'll'}, D.neverificate.map(l => h('li', {},
      h('span', {class: 'dot o'}), ext(l.url, l.url), h('div', {class: 'meta'}, l.motiv),
      LIVE && h('div', {class: 'acts'},
        h('button', {class: 'mic', onclick: e => act({tip: 'manual', url: l.url, stare: 'ONLINE'}, e.target)}, 'Există (am verificat)'),
        h('button', {class: 'mic', onclick: e => act({tip: 'ignora', url: l.url, valoare: true}, e.target)}, 'Nu există')))))));
}

function sterse() {
  if (!D.sterse.length) return h('p', {class: 'mut'}, 'Încă niciunul.');
  const inG = D.sterse.filter(s => s.in_cautare).length;
  return h('div', {},
    inG > 0 && h('p', {}, nr(inG, 'pagină ștearsă încă apare', 'pagini șterse încă apar') + ' în căutări. Cere scoaterea lor din Google: ', ext(D.formulare.vechi, 'Remove outdated content ↗')),
    det('sterse', 'Arată lista', h('div', {class: 'tw'}, h('table', {},
      h('tr', {}, h('th', {}, 'Site'), h('th', {}, 'Adresa'), h('th', {}, 'Găsit'), h('th', {}, 'Dispărut'), h('th', {}, 'Încă în căutări'), LIVE && h('th', {}, '')),
      D.sterse.map(s => h('tr', {},
        h('td', {}, h('span', {class: 'dot v'}), s.domeniu), h('td', {class: 'u'}, ext(s.url, s.url)),
        h('td', {}, s.gasit), h('td', {}, s.sters + (s.manual ? ' (verificat de tine)' : '')), h('td', {}, s.in_cautare || '—'),
        LIVE && h('td', {}, s.manual && h('button', {class: 'mic', onclick: e => act({tip: 'manual', url: s.url, stare: null}, e.target)}, 'Anulează'))))))));
}

function ignorate() {
  return det('ign', 'Arată (' + D.ignorate.length + ')', h('ul', {class: 'll'}, D.ignorate.map(x => h('li', {},
    x.tot_site ? h('b', {}, x.domeniu + ' (tot site-ul)') : ext(x.url, x.url),
    LIVE && h('div', {class: 'acts'}, h('button', {class: 'mic', onclick: e =>
      act(x.tot_site ? {tip: 'ignora', domeniu: x.domeniu, valoare: false} : {tip: 'ignora', url: x.url, valoare: false}, e.target)}, 'Readu în raport'))))));
}

function adauga() {
  const ta = h('textarea', {placeholder: 'Lipește aici linkuri noi (de la Internet Removals, din Google...), câte unul pe rând.'});
  return [h('h2', {}, '➕ Adaugă linkuri'), h('div', {class: 'box'}, ta,
    h('button', {onclick: e => { if (ta.value.trim()) act({tip: 'adauga', text: ta.value}, e.target); }}, 'Adaugă și verifică'),
    h('span', {class: 'mut'}, ' Rămân doar pe laptopul tău.'))];
}

function undeTrimiti() {
  const F = D.formulare;
  return [h('h2', {}, 'Unde trimiți'), h('div', {class: 'box'}, h('ul', {class: 'help'},
    h('li', {}, h('b', {}, 'Google: '), ext(F.google[0][1], 'formularul pentru conținut intim ↗'), ', ', ext(F.google[1][1], 'copyright ↗'),
      '. Din Google Imagini: ⋮ → Remove result.'),
    h('li', {}, h('b', {}, 'Bing: '), ext(F.bing[0][1], 'aka.ms/reportci ↗'), ', cu aceeași listă.'),
    h('li', {}, h('b', {}, 'Site-ul: '), 'textele A (Take It Down), B (GDPR), C (DMCA) din planul tău, la adresa de contact sau DMCA a site-ului.'),
    h('li', {}, h('b', {}, 'Hosting: '), 'după ' + D.zile_site + ' zile fără ștergere. Dacă site-ul e pe Cloudflare: ', ext(F.cloudflare[0][1], 'formularul Cloudflare ↗'),
      '. Altfel, la adresa de abuz arătată pe card.'),
    h('li', {}, h('b', {}, 'Șterse, dar încă în Google: '), ext(F.vechi, 'Remove outdated content ↗'), '.')))];
}

function randeaza() {
  const R = D.rezumat;
  const lucru = D.grupuri.filter(g => g.categorie !== 'astept'), astept = D.grupuri.filter(g => g.categorie === 'astept');
  document.getElementById('app').replaceChildren(...curata([
    h('h1', {}, 'Evidența ștergerilor'),
    h('p', {class: 'sub'}, 'Verificat: ' + D.generat, D.cautare_text && h('br'), D.cautare_text),
    !LIVE && h('div', {class: 'banner'}, 'Raportul ăsta e doar de citit. Ca să bifezi ce ai trimis, dă dublu-click pe raport.bat.'),
    h('div', {class: 'tiles'},
      tile('r', R.de_trimis, R.de_trimis === 1 ? 'site de trimis' : 'site-uri de trimis', nr(R.de_trimis_linkuri, 'link', 'linkuri')),
      tile('o', R.de_revenit, 'de revenit', 'n-au șters la timp'),
      tile('', R.astept, 'aștept răspuns', 'trimis, încă online'),
      tile('n', R.noi, R.noi === 1 ? 'link nou' : 'linkuri noi', 'găsite singur, 7 zile'),
      tile('v', R.sterse, R.sterse === 1 ? 'link șters' : 'linkuri șterse', 'de la început')),
    todo(lucru),
    h('h2', {}, '📮 De trimis (' + lucru.length + ')'),
    lucru.length ? lucru.map(card) : h('p', {class: 'ok'}, 'Nimic de trimis acum.'),
    h('h2', {}, '⏳ Trimis, aștept să se șteargă (' + astept.length + ')'),
    astept.length ? det('astept', 'Arată site-urile', astept.map(card)) : h('p', {class: 'mut'}, 'Niciunul.'),
    D.neverificate.length > 0 && [h('h2', {}, '🟠 Profiluri neverificate (' + D.neverificate.length + ')'), neverificate()],
    h('h2', {}, '🟢 Șterse (' + D.sterse.length + ')'), sterse(),
    D.ignorate.length > 0 && [h('h2', {}, 'Ascunse (' + D.ignorate.length + ')'), ignorate()],
    LIVE && adauga(),
    undeTrimiti()]));
}
randeaza();
</script></body></html>
'''

if __name__ == '__main__':
    main()
