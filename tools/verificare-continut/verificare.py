#!/usr/bin/env python3
"""Verificare conținut: ține evidența paginilor cu numele tău, până se șterg.

Ce face (fără să descarce sau să arate poze):
  1. Ia linkurile tale din linkuri.txt și caută singur numele tale pe Google, Google Imagini, Bing și Yandex
     (prin SerpApi; cu „leak”, „nude”, „onlyfans”, Reddit/X/Telegram și „site:” pe fiecare site găsit).
  2. Ce găsește nou adaugă singur și recunoaște conținutul adult. Din linkurile găsite învață adresele de profil
     ale site-urilor și verifică acolo și celelalte nume ale tale.
  3. Verifică fiecare pagină: ONLINE, ȘTERS sau NU POT VERIFICA (site blocat în țară, protecție Cloudflare).
  4. La fiecare site află hostingul (sau Cloudflare), firma domeniului, pagina de DMCA și adresa de email.
  5. Deschide raportul în browser: la fiecare site vezi ce mai ai de trimis (Google, Bing, site, hosting),
     cu emailul gata scris, bifezi „Am trimis”, iar programul îți spune când e timpul pentru revenire.

Rulezi: dublu-click pe verificare.bat (Windows) sau: python verificare.py
  python verificare.py --raport        doar raportul, fără verificare (ca să bifezi ce ai trimis)
  python verificare.py --cauta         caută acum pe Google/Bing, chiar dacă n-a trecut o săptămână
  python verificare.py --fara-cautare  verifică doar linkurile știute
  python verificare.py --fara-server   scrie raport.html și se oprește
Linkurile, cheile și rezultatele rămân doar în folderul ăsta, pe laptopul tău.
"""
import html, imaplib, json, os, re, secrets, shutil, socket, ssl, sys, threading, time, webbrowser
import urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from email import message_from_bytes, policy as email_policy, utils as email_utils
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'stare.json')
LINKS = os.path.join(HERE, 'linkuri.txt')
REPORT = os.path.join(HERE, 'raport.html')
KEYS = os.path.join(HERE, 'chei.txt')
SITE_ADULT = os.path.join(HERE, 'site-uri-adult.txt')
BAZA_ADULT = os.path.join(HERE, 'baza-site-adult.txt')   # se descarcă singur (listă publică, ~77.000 de site-uri adult)
BAZA_URL = 'https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn-only/hosts'

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
# Căutarea pe Google/Bing/Yandex (prin SerpApi). Fiecare formulă se caută pentru fiecare nume din CAUTARI ({n}),
# în ordinea de mai jos. Pe lângă ele: „site:SITE (numele tale)” pe Google, pentru fiecare site cu conținut adult găsit,
# ca să apară toate paginile tale de pe el. Planul gratuit nu ajunge pentru toate deodată: programul le ia pe rând,
# întâi pe cele necăutate de cel mai mult timp (planul gratuit: ~25 la fiecare 3 zile; cu un plan mai mare, mai multe).
FORMULE = [
    ('google', '"{n}"'),
    ('bing', '"{n}"'),
    ('google', '"{n}" leak OR leaked OR leaks'),
    ('google', '"{n}" nude OR naked OR nudes OR nsfw'),
    ('google', '"{n}" onlyfans OR fansly OR porn OR xxx'),
    ('google_imagini', '"{n}"'),
    ('bing', '"{n}" leaked OR nude OR onlyfans OR porn'),
    ('yandex', '"{n}"'),
    ('google', '"{n}" site:reddit.com OR site:x.com OR site:t.me OR site:erome.com'),
    ('google_imagini', '"{n}" nude OR leaked'),
    ('yandex', '{n} leaked nude'),
    ('google_pagina2', '"{n}"'),
    ('bing_pagina2', '"{n}"'),
]
# Cuvintele-cheie de la bara de căutare (le schimbi din pagină; astea sunt cele de la început).
CUVINTE_IMPLICITE = ['xxx', 'naked', 'nude', 'leaked', 'onlyfans', 'porn', 'nsfw', 'sextape']
TIMP_CAUTARE = {'': '', 'z': 'qdr:d', 's': 'qdr:w', 'l': 'qdr:m', 'a': 'qdr:y'}
ZILE_INTRE_CAUTARI = 3       # cel mult o dată la 3 zile (verificarea linkurilor știute merge oricând)
MIN_CAUTARI_PE_RULARE = 10
LIMITA_SERPAPI = 250         # pe lună, planul gratuit (dacă SerpApi nu răspunde la întrebarea „câte mai am”)
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
    'bing': [('formularul Microsoft / Bing', 'https://www.microsoft.com/en-us/concern/revengeporn'),
             ('Report a Concern (dacă primul nu merge)', 'https://www.microsoft.com/en-us/concern')],
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
RDAP_DOMENIU_URL = 'https://rdap.org/domain/'
SCHEMA_SITE = 'https://'      # pentru teste

# Cuvinte care arată conținut adult (în adresă, titlu sau pagină).
ADULT_RE = re.compile(r'(?<![a-z])(leak(?:s|ed)?|nudes?|naked|nsfw|onlyfans|only fans|fansly|porn\w*|xxx|sex|fap\w*|'
                      r'erome|thots?|boobs?|tits|nipples?|lewd|explicit|uncensored|topless|camgirls?|webcam|hentai|'
                      r'pussy|milf|escort|18\+)(?![a-z])')
UE = {'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV',
      'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'}

# Emailurile gata de copiat (textele A, B, C din planul tău + hosting + revenire). {linkuri}, {nume}, {email}, {azi},
# {site}, {data}, {rol}, {ip} se completează singure.
TEXTE = {
    'A': ('TAKE IT DOWN Act removal request: non-consensual intimate images of me',
          'Hello,\n\nI am the person shown in the intimate images/videos at the locations listed below. They are published '
          'without my consent, and I request their removal, and the removal of any identical copies, within 48 hours, as '
          'required by the TAKE IT DOWN Act.\n\nWhere they are:\n{linkuri}\n\nI have a good faith belief that this intimate '
          'visual depiction is not consensual: I do not consent to its publication.\n\nPlease confirm the removal at this '
          'email address.\n\n{nume}\n{email}\nSignature: {nume} · Date: {azi}'),
    'B': ('GDPR Article 17 erasure request: images of me',
          'Hello,\n\nI am an EU citizen and the person shown in the images/videos at the locations below. They are my '
          'personal data, including data concerning my sex life (GDPR Article 9).\n\nWhere they are:\n{linkuri}\n\nI withdraw '
          'any consent that may have been given for their processing (Article 7(3)) and object to their processing '
          '(Article 21). Under Article 17, I request that you erase them without undue delay, including copies and '
          'thumbnails, and confirm this in writing within one month (Article 12(3)).\n\nIf you do not act, I will file a '
          'complaint with the data protection authority.\n\n{nume}\n{email}\nDate: {azi}'),
    'C': ('DMCA Takedown Notice',
          'To whom it may concern,\n\nI am the copyright owner of the images/videos found at the URLs below. They were '
          'published without my authorization and I request their removal under the Digital Millennium Copyright Act '
          '(17 U.S.C. § 512).\n\nInfringing URLs:\n{linkuri}\n\nOriginal work: photos/videos created and owned by me.\n\n'
          'I have a good faith belief that the use of this material is not authorized by the copyright owner, its agent, '
          'or the law. The information in this notice is accurate, and under penalty of perjury, I am the owner of the '
          'copyright that is allegedly infringed.\n\n{nume} · {email}\nSignature: {nume} · Date: {azi}'),
    'google': ('Google: cererea de copyright (formularul „Căutare Google”)',
               'Descrierea lucrării (Identify and describe the copyrighted work):\nPhotos and videos of myself that I created and own. They were stolen from my private accounts and republished without my permission on the pages listed below. They are also intimate images published without my consent.\n\n'
               'Unde e o copie autorizată (Where can we see an authorized example):\nhttps://www.instagram.com/kristinemaia11/\nhttps://www.twitch.tv/kristinemaia\n\n'
               'Adresele de scos din căutare (Location of infringing material), câte una pe rând:\n{linkuri}\n\n'
               'Semnătura: {nume} · Data: {azi}'),
    'bing': ('Bing: formularul Microsoft „Report a Concern” (conținut intim publicat fără acord)',
             'I am the person shown in the intimate images and videos at the links below. They were stolen from my private accounts and published without my consent. I am an adult and I did not authorize their publication. Please remove these pages from Bing search results, including copies and thumbnails.\n\n'
             'Links:\n{linkuri}\n\n{nume}\n{email}\nDate: {azi}'),
    'r_multumesc': ('Re: {subiect}',
                    'Hello,\n\nThank you very much for removing the content. Could you please also make sure that all copies, '
                    'thumbnails and cached versions are removed, and that the content cannot be uploaded again?\n\n'
                    'For reference, these were the links:\n{linkuri}\n\nThank you,\n{nume}'),
    'r_linkuri': ('Re: {subiect}',
                  'Hello,\n\nThank you for your reply. Here is the list of direct URLs, one per line, in plain text:\n\n{linkuri}\n\n'
                  'I am the person shown in this content. It was published without my consent and I am the copyright owner. '
                  'Please remove all of them and confirm.\n\nThank you,\n{nume}'),
    'r_rusa': ('Re: {subiect}',
               'Здравствуйте!\n\nЭто не жалоба компании на нарушение авторских прав. Я частное лицо, и на этих '
               'изображениях изображена я сама. Они опубликованы без моего согласия.\n\nСогласно статье 152.1 '
               'Гражданского кодекса РФ (охрана изображения гражданина) и Федеральному закону № 152-ФЗ «О персональных '
               'данных», публикация изображения человека без его согласия незаконна.\n\nПрошу передать жалобу клиенту '
               '(владельцу сайта {site}) и удалить материалы:\n{linkuri}\n\nПожалуйста, не передавайте владельцу сайта '
               'моё имя и контакты.\n\nС уважением,\n{nume}'),
    'r_revin': ('Re: {subiect}',
                'Hello,\n\nThank you for your reply. The content is still online at the links below. Please remove it, including '
                'all copies, and confirm by email.\n\n{linkuri}\n\nI am the person shown, it was published without my consent, '
                'and I am the copyright owner.\n\nThank you,\n{nume}'),
    'revenire': ('Second notice: my removal request of {data} (non-consensual intimate images)',
                 'Hello,\n\nOn {data} I asked you to remove the intimate images of me listed below. They were published '
                 'without my consent and they are still online.\n\nWhere they are:\n{linkuri}\n\nPlease remove them, and any '
                 'copies, without further delay and confirm by email. If they are not removed, I will report this to your '
                 'hosting provider, to the search engines and to the authorities.\n\n{nume}\n{email}\nDate: {azi}'),
    'gazda': ('Abuse report: non-consensual intimate images on {site}',
              'Hello,\n\nI am writing to you as the {rol} of the website {site}{ip}. This website publishes intimate '
              'images of me without my consent. {intro}They are still online.\n\nWhere they are:\n{linkuri}\n\n'
              'I am the person shown in these images, and I do not consent to their publication. Publishing intimate images '
              'without consent is illegal in the EU and in the US (TAKE IT DOWN Act). Please have this content removed '
              'under your acceptable use policy, or suspend the service, and confirm by email.\n\n{nume}\n{email}\n'
              'Date: {azi}'),
}


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


def scor_adult(text):
    """Câte cuvinte diferite de conținut adult apar în text."""
    return len({m.group(1) for m in ADULT_RE.finditer(text.lower())})


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


JURNAL = os.path.join(HERE, 'bife-jurnal.txt')
TIPURI_JURNAL = ('trimis', 'manual', 'ignora', 'adult', 'nota_site', 'email_rezolvat')


def scrie_jurnal(a):
    if a.get('tip') in TIPURI_JURNAL:
        with open(JURNAL, 'a', encoding='utf-8') as f:
            f.write(json.dumps({k: v for k, v in a.items() if k != 'token'}, ensure_ascii=False) + '\n')


def reaplica_jurnal(stare):
    """Bifele tale sunt scrise și în bife-jurnal.txt; la pornire le pun din nou, ca să nu se piardă niciodată."""
    if not os.path.exists(JURNAL):
        return 0
    n = 0
    for line in open(JURNAL, encoding='utf-8'):
        try:
            a = json.loads(line)
            if a.get('tip') == 'manual' and a.get('url') not in stare['linkuri']:
                continue
            aplica(stare, a)
            n += 1
        except Exception:
            pass
    return n


def reincarca(stare):
    """Citește din nou stare.json (fără copie de rezervă): fișierul e mereu sursa adevărului."""
    try:
        with open(STATE, encoding='utf-8') as f:
            nou = json.load(f)
        if isinstance(nou, dict) and 'linkuri' in nou:
            stare.clear()
            stare.update(nou)
    except (OSError, ValueError):
        pass


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


def actualizeaza(e, st, motiv, cand, adult=None):
    if adult:
        e['adult'] = True
    elif adult is False:
        e.setdefault('adult', False)
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
def verifica(url, cu_nume=True):
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
    if cu_nume and not are_nume(body):
        return STERS, 'numele nu mai apare pe pagină' + (' (redirecționat)' if final.rstrip('/') != url.rstrip('/') else '')
    if any(g in body for g in GOL_CORP) and (not cu_nume or sum(body.count(v) for v in NUME_TEXT) < 3):
        return STERS, 'pagina spune că nu există'
    adult = (scor_adult(urllib.parse.unquote(url) + ' ' + titlu) >= 1 or scor_adult(body[:300_000]) >= 3
             or in_baza(gazda(final)))
    return ONLINE, 'pagina există' + (' și conține numele' if cu_nume else ' (găsită după poză)'), adult


def verifica_toate(stare, urls, cand, arata=True):
    if not urls:
        return
    gata = 0
    with ThreadPoolExecutor(FIRE) as ex:
        viitor = {ex.submit(verifica, u, not stare['linkuri'][u].get('dupa_poza')): u for u in urls}
        for f in as_completed(viitor):
            st, motiv, *rest = f.result()
            actualizeaza(stare['linkuri'][viitor[f]], st, motiv, cand, rest[0] if rest else None)
            gata += 1
            if arata and (gata % 10 == 0 or gata == len(urls)):
                print(f'\r  verificate: {gata}/{len(urls)}', end='', flush=True)
    if arata:
        print()


# ───────────── Căutarea pe Google / Bing ─────────────
SABLON_CHEI = [
    ('SERPAPI', '# Lipește cheia după semnul =, fără spații. Fișierul rămâne doar pe laptopul tău.\n'
                '# SerpApi (Google, Bing, Yandex; 250 de căutări gratuite pe lună): serpapi.com → Dashboard → Your Private API Key\n'),
    ('BRAVE', '# Brave (opțional, alt motor de căutare): api-dashboard.search.brave.com → API Keys\n'),
    ('EMAIL', '# Emailul separat din care trimiți cererile (programul doar citește, nu trimite și nu șterge nimic)\n'),
    ('EMAIL_PAROLA', '# Parola de aplicație (la Gmail: myaccount.google.com/apppasswords, 16 litere), NU parola ta obișnuită\n'),
]


def citeste_chei():
    vechi = open(KEYS, encoding='utf-8-sig').read() if os.path.exists(KEYS) else ''
    lipsa = [(k, c) for k, c in SABLON_CHEI if not re.search(rf'^\s*{k}\s*=', vechi, re.M)]
    if lipsa:   # adaugă rândurile noi, fără să atingă ce ai scris deja
        with open(KEYS, 'a', encoding='utf-8') as f:
            f.write(('\n' if vechi and not vechi.endswith('\n') else '') + ''.join(c + k + '=\n' for k, c in lipsa))
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


PARAMETRI = {   # motor: (cum apare în raport, parametrii SerpApi, numele parametrului pentru text)
    'google': ('Google', {'engine': 'google', 'safe': 'off', 'filter': '0', 'hl': 'en', 'gl': 'us'}, 'q'),
    'google_pagina2': ('Google', {'engine': 'google', 'safe': 'off', 'filter': '0', 'hl': 'en', 'gl': 'us', 'start': '10'}, 'q'),
    'google_imagini': ('Google Imagini', {'engine': 'google_images', 'safe': 'off', 'hl': 'en', 'gl': 'us'}, 'q'),
    'bing': ('Bing', {'engine': 'bing', 'safeSearch': 'off', 'count': '50', 'cc': 'US'}, 'q'),
    'bing_pagina2': ('Bing', {'engine': 'bing', 'safeSearch': 'off', 'count': '50', 'cc': 'US', 'first': '51'}, 'q'),
    'yandex': ('Yandex', {'engine': 'yandex'}, 'text'),
    'google_lens': ('Google Lens', {'engine': 'google_lens', 'type': 'exact_matches', 'hl': 'en', 'country': 'us'}, 'url'),
}
FORMULE_INAINTE_DE_SITE = 5   # căutările „site:” vin după primele 5 formule


def domenii_adult(stare):
    out = set()
    for url, e in stare['linkuri'].items():
        d = domeniu(url)
        if not ignorat(stare, url, e) and e_adult(stare, url, e) and categorie(e) in ('activ', 'sters') and not platforma_mare(d):
            out.add(d)
    return sorted(out)


def cereri_serpapi(stare):
    """Toate căutările, în ordinea în care le facem: întâi cele necăutate de cel mai mult timp."""
    baza = [(m, f.replace('{n}', t)) for m, f in FORMULE for t in CAUTARI]
    cuv = cuvinte(stare)
    if cuv:
        baza += [('google', f'"{t}" ' + ' OR '.join(cuv)) for t in CAUTARI]
    nume = ' OR '.join(f'"{t}"' for t in CAUTARI)
    k = FORMULE_INAINTE_DE_SITE * len(CAUTARI)
    stiute = domenii_adult(stare)
    lista = [d for d in site_adult() if not any(e_al_domeniului(d, x) for x in stiute)]
    grupe = [('google', f'({nume}) (' + ' OR '.join(f'site:{d}' for d in lista[i:i + 8]) + ')') for i in range(0, len(lista), 8)]
    lens = [('google_lens', u) for u in poze_de_cautat(stare)]
    toate = baza[:k] + [('google', f'site:{d} ({nume})') for d in stiute] + lens + grupe + baza[k:]
    facute = stare['cautare'].get('facute', {})
    ordine = {c: i for i, c in enumerate(toate)}
    return sorted(toate, key=lambda c: (facute.get(c[0] + '|' + c[1], ''), ordine[c]))


def cuvinte(stare):
    c = stare.get('cuvinte')
    return list(CUVINTE_IMPLICITE if c is None else c)


def intrebare_implicita(stare):
    nume = ' OR '.join(f'"{t}"' for t in CAUTARI)
    cuv = cuvinte(stare)
    return f'({nume})' + (' (' + ' OR '.join(cuv) + ')' if cuv else '')


def cauta_acum(stare, q, motor, timp):
    """Căutarea pornită de tine din bara de căutare: o singură căutare SerpApi, rezultatele le verifici tu."""
    q = (q or '').strip()[:400] or intrebare_implicita(stare)
    if motor not in ('google', 'bing', 'google_imagini'):
        raise ValueError('motor necunoscut')
    k = citeste_chei().get('SERPAPI')
    if not k:
        raise ValueError('Ca să caute din program, pune cheia SerpApi în chei.txt (vezi CITESTE.md). '
                         'Până atunci, folosește butoanele „Deschide în Google” și „Deschide în Bing”.')
    eticheta, params, camp = PARAMETRI[motor]
    params = dict(params)
    if TIMP_CAUTARE.get(timp) and motor != 'bing':
        params['tbs'] = TIMP_CAUTARE[timp]
    try:
        d = cere_json(f'{SERPAPI_URL}/search.json?' + urllib.parse.urlencode({**params, camp: q, 'api_key': k}))
    except urllib.error.HTTPError as e:
        raise ValueError('SerpApi: ' + ('cheia nu e bună.' if e.code == 401 else
                                        's-au terminat căutările pe luna asta.' if e.code == 429 else f'eroare {e.code}.'))
    except Exception as e:
        raise ValueError(f'SerpApi nu răspunde ({type(e).__name__}). Încearcă din nou peste un minut.')
    if d.get('error') and 'any results' not in str(d['error']):
        raise ValueError('SerpApi: ' + str(d['error'])[:160])
    luna = datetime.now().strftime('%Y-%m')
    fl = stare['cautare'].setdefault('luna', {})
    fl[luna] = fl.get(luna, 0) + 1
    idx, respinse, rez, vazute = index(stare), set(stare.get('cautare_respinse') or []), [], set()
    for url, titlu, text, _ in (_rezultate(d.get('organic_results'), eticheta) + _rezultate(d.get('images_results'), eticheta)):
        if not url.lower().startswith(('http://', 'https://')) or e_propriu(url) or e_motor(url):
            continue
        kk = cheie(url)
        if kk in vazute or kk in respinse:
            continue
        vazute.add(kk)
        stiut = idx.get(kk)
        e = stare['linkuri'].get(stiut) if stiut else None
        rez.append({'url': url, 'titlu': titlu[:200], 'text': text[:300],
                    'stiut': bool(e and not e.get('ignorat')), 'site_stiut': domeniu(url) in {domeniu(u) for u in stare['linkuri']},
                    'nume': are_nume(urllib.parse.unquote(url) + ' ' + titlu + ' ' + text),
                    'adult': bool(scor_adult(urllib.parse.unquote(url) + ' ' + titlu + ' ' + text) or in_baza(gazda(url)))})
    rez.sort(key=lambda r: (r['stiut'], not r['adult'], not r['nume']))
    stare['cautare_acum'] = {'q': q, 'motor': motor, 'timp': timp, 'data': acum(), 'rezultate': rez[:60]}


def poze_de_cautat(stare):
    """Pozele căutate cu Google Lens: cele adăugate de tine în raport și linkurile spre poze din evidență."""
    out = list(stare.get('poze') or [])
    for u, e in stare['linkuri'].items():
        if (re.search(r'\.(jpe?g|png|webp)(\?|$)', u, re.I) and not ignorat(stare, u, e)
                and categorie(e) in ('activ', 'sters') and u not in out):
            out.append(u)
    return out[:60]


def buget(ramase, pe_luna, total):
    """Câte căutări facem acum: căutările pe lună împărțite egal (o căutare la ZILE_INTRE_CAUTARI zile)."""
    pe_rulare = max(MIN_CAUTARI_PE_RULARE, pe_luna // max(1, 30 // ZILE_INTRE_CAUTARI))
    return max(0, min(total, pe_rulare, ramase - 3))


def cauta_serpapi(k, stare, mesaje):
    luna = datetime.now().strftime('%Y-%m')
    folosite = stare['cautare'].setdefault('luna', {})
    facute_cand = stare['cautare'].setdefault('facute', {})
    ramase, pe_luna = LIMITA_SERPAPI - folosite.get(luna, 0), LIMITA_SERPAPI
    try:
        cont = cere_json(f'{SERPAPI_URL}/account.json?' + urllib.parse.urlencode({'api_key': k}))
        if cont.get('error'):
            mesaje.append('SerpApi: ' + str(cont['error'])[:120])
            return [], 0
        ramase = int(cont.get('plan_searches_left', cont.get('total_searches_left', ramase)) or 0)
        pe_luna = int(cont.get('searches_per_month') or pe_luna)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            mesaje.append('SerpApi: cheia nu e bună. Copiaz-o din nou în chei.txt.')
            return [], 0
    except Exception:
        pass   # nu știm câte au rămas: ne bazăm pe numărătoarea noastră
    toate = cereri_serpapi(stare)
    cereri = toate[:buget(ramase, pe_luna, len(toate))]
    if not cereri:
        mesaje.append('SerpApi: s-au terminat căutările pe luna asta. Reîncep luna viitoare.')
        return [], 0
    out, facute, motoare = [], 0, []
    for motor, q in cereri:
        eticheta, params, camp = PARAMETRI[motor]
        try:
            d = cere_json(f'{SERPAPI_URL}/search.json?' + urllib.parse.urlencode({**params, camp: q, 'api_key': k}))
        except urllib.error.HTTPError as e:
            mesaje.append('SerpApi: ' + ('cheia nu e bună.' if e.code == 401 else
                                         's-au terminat căutările pe luna asta.' if e.code == 429 else f'eroare {e.code}.'))
            break
        except Exception as e:
            mesaje.append(f'SerpApi nu răspunde ({type(e).__name__}).')
            break
        facute += 1
        facute_cand[motor + '|' + q] = date.today().isoformat()
        if d.get('error') and 'any results' not in str(d['error']):
            mesaje.append('SerpApi: ' + str(d['error'])[:120])
            continue
        out += (_rezultate(d.get('organic_results'), eticheta) + _rezultate(d.get('images_results'), eticheta)
                + _rezultate(d.get('exact_matches'), eticheta) + _rezultate(d.get('visual_matches'), eticheta))
        if eticheta not in motoare:
            motoare.append(eticheta)
    folosite[luna] = folosite.get(luna, 0) + facute
    if facute:
        necautate = sum(1 for m, q in toate if m + '|' + q not in facute_cand)
        mesaje.append(f'SerpApi: {nr(facute, "căutare", "căutări")} ({", ".join(motoare)}); '
                      f'mai ai ~{nr(max(0, ramase - facute), "căutare", "căutări")} pe luna asta.'
                      + (f' Încă {nr(necautate, "căutare", "căutări")} la rând, le fac data viitoare.' if necautate else
                         ' Toate căutările au fost făcute cel puțin o dată.'))
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


def relevant_poza(url):
    """Pagină găsită după poză: nu trebuie să conțină numele."""
    return (url.lower().startswith(('http://', 'https://')) and bool(gazda(url)) and not e_propriu(url)
            and not e_motor(url) and not re.search(r'\.(jpe?g|png|gif|webp)(\?|$)', url, re.I))


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
        if not (relevant_poza(url) if motor == 'Google Lens' else relevant(url, titlu, text)):
            continue
        e, nou = adauga(stare, idx, url, motor, cand)
        e.setdefault('in_cautare', {})[motor] = cand[:10]
        if scor_adult(urllib.parse.unquote(url) + ' ' + titlu + ' ' + text) or in_baza(gazda(url)):
            e['adult'] = True
        if motor == 'Google Lens' and nou:
            e['dupa_poza'] = True
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


def afla_registrar(dom):
    """Firma la care e înregistrat domeniul (următorul pas, dacă nici hostingul nu șterge)."""
    try:
        r = cere_json(RDAP_DOMENIU_URL + dom, timp=15)
    except Exception:
        return None
    for e in _entitati(r):
        if 'registrar' in (e.get('roles') or []):
            email = next((_vcard(x, 'email') for x in _entitati(e) if 'abuse' in (x.get('roles') or [])), None)
            return {'nume': _vcard(e, 'fn') or '?', 'email': email, 'data': date.today().isoformat()}
    return None


CONTACT_RE = re.compile(r'dmca|abuse|takedown|take-down|removal|remove|copyright|contact|2257|complain|report|legal|terms', re.I)
PRIORITATE = ['dmca', 'takedown', 'take-down', 'removal', 'remove', 'abuse', 'copyright', 'complain', 'report', 'contact',
              'legal', 'support', '2257', 'terms']
CAI_CONTACT = ['/dmca', '/contact', '/dmca/', '/contact-us', '/contact/', '/content-removal', '/abuse']
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,24}')


def _prio(text):
    t = text.lower()
    return next((i for i, w in enumerate(PRIORITATE) if w in t), len(PRIORITATE))


def _emailuri(body):
    """Adresele de email de pe o pagină, și cele ascunse de Cloudflare sau scrise „dmca [at] site [dot] com”."""
    text = html.unescape(body)
    text = re.sub(r'\s*[\[(]\s*(?:at|@)\s*[\])]\s*', '@', text, flags=re.I)
    text = re.sub(r'\s*[\[(]\s*(?:dot|\.)\s*[\])]\s*', '.', text, flags=re.I)
    gasite = set(EMAIL_RE.findall(text))
    gasite |= {urllib.parse.unquote(m) for m in re.findall(r'mailto:([^"\'?>\s]+)', text, re.I)}
    for hx in re.findall(r'data-cfemail="([0-9a-fA-F]+)"', body) + re.findall(r'email-protection#([0-9a-fA-F]+)', body):
        try:
            b = bytes.fromhex(hx)
            gasite.add(''.join(chr(c ^ b[0]) for c in b[1:]))
        except (ValueError, IndexError):
            pass
    return {e.lower().strip('.') for e in gasite if EMAIL_RE.fullmatch(e.strip('.'))
            and not re.search(r'\.(png|jpe?g|gif|webp|svg|css|js|ico)$|example\.|sentry|wixpress|@2x|domain\.com|youremail', e, re.I)}


def afla_contact(dom, host):
    """Caută pe site pagina de DMCA / contact și adresele de email."""
    final = body = None
    for baza in dict.fromkeys([f'{SCHEMA_SITE}{dom}/', f'{SCHEMA_SITE}{host}/']):
        try:
            final, body = cere(baza, timp=15)
            break
        except Exception:
            continue
    if body is None:
        return {'eroare': 'site-ul nu s-a deschis (blocat în țară sau închis)', 'data': date.today().isoformat()}
    emailuri, pagini = _emailuri(body), []
    for m in re.finditer(r'<a\b[^>]*?href\s*=\s*["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', body, re.S | re.I):
        href, text = html.unescape(m.group(1)).strip(), re.sub(r'<[^>]+>', ' ', m.group(2))
        if href.lower().startswith(('mailto:', 'javascript:')):
            continue
        if CONTACT_RE.search(href) or CONTACT_RE.search(text):
            u = urllib.parse.urljoin(final, href)
            if u.startswith(('http://', 'https://')) and domeniu(u) == domeniu(final) and u not in pagini:
                pagini.append(u)
    if not pagini:   # nu are linkuri: încercăm adresele obișnuite
        for cale in CAI_CONTACT:
            try:
                f2, b2 = cere(urllib.parse.urljoin(final, cale), timp=10)
            except Exception:
                continue
            t = re.search(r'<title[^>]*>(.*?)</title>', b2[:60000], re.S | re.I)
            if (domeniu(f2) == domeniu(final) and urllib.parse.urlsplit(f2).path not in ('', '/')
                    and not any(g in (t.group(1).lower() if t else '') for g in GOL_TITLU)):
                pagini.append(f2)
                emailuri |= _emailuri(b2)
    pagini.sort(key=_prio)
    for u in pagini[:3]:
        try:
            emailuri |= _emailuri(cere(u, timp=12)[1])
        except Exception:
            pass
    return {'emailuri': sorted(emailuri, key=lambda e: (_prio(e), e))[:5], 'pagini': pagini[:3],
            'data': date.today().isoformat()}


def actualizeaza_site(stare):
    """Pentru fiecare site de unde trebuie șters ceva: hostingul, registrarul și adresa de contact (o dată pe lună)."""
    de_aflat = {}
    for url, e in stare['linkuri'].items():
        if not ignorat(stare, url, e) and categorie(e) == 'activ' and e_adult(stare, url, e) is not False:
            de_aflat.setdefault(domeniu(url), gazda(url))

    def vechi(x, zile=30):
        return not x or zile_de_la(x['data']) > zile

    def lucreaza(dom, host):
        s, r = stare['site'].get(dom, {}), {}
        if vechi(s.get('gazda')):
            r['gazda'] = afla_gazda(host)
        if vechi(s.get('registrar')):
            r['registrar'] = afla_registrar(dom)
        c = s.get('contact')
        if vechi(c) or (c.get('eroare') and zile_de_la(c['data']) >= 1):
            r['contact'] = afla_contact(dom, host)
        return dom, r

    with ThreadPoolExecutor(6) as ex:
        for dom, r in ex.map(lambda x: lucreaza(*x), de_aflat.items()):
            s = stare['site'].setdefault(dom, {})
            s.update({k: v for k, v in r.items() if v})


# ───────────── Emailul tău (doar citire) ─────────────
IMAP_SERVERE = {'gmail.com': 'imap.gmail.com', 'googlemail.com': 'imap.gmail.com', 'yahoo.com': 'imap.mail.yahoo.com',
                'icloud.com': 'imap.mail.me.com', 'me.com': 'imap.mail.me.com', 'gmx.com': 'imap.gmx.com',
                'gmx.net': 'imap.gmx.net', 'outlook.com': 'outlook.office365.com', 'hotmail.com': 'outlook.office365.com'}
ZILE_EMAIL = 365
MAX_EMAILURI = 3000
CUVINTE_EMAIL = ['dmca', 'takedown', 'removal', 'remove', 'removed', 'abuse', 'cloudflare', 'gdpr', 'copyright',
                 'infringement', 'consent', 'erasure', 'complaint', 'notice', 'ticket', 'stopncii', 'lumen']
STERS_RE = re.compile(r'(has|have|had) been (removed|deleted|taken down|disabled)|\b(we|i) (have )?(removed|deleted|took down)'
                      r'|content (was|is) removed|takedown (is )?(complete|processed)|action (was|has been) taken', re.I)
DOMENII_CANAL = {'google': ('google.com',), 'bing': ('microsoft.com', 'bing.com'), 'gazda': ('cloudflare.com',)}


def _text_email(msg):
    text = []
    for part in msg.walk():
        if part.get_content_maintype() != 'text':
            continue
        try:
            t = part.get_content()
        except Exception:
            try:
                t = (part.get_payload(decode=True) or b'').decode('utf-8', 'ignore')
            except Exception:
                t = ''
        if part.get_content_subtype() == 'html':
            t = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?is)<(script|style).*?</\1>', ' ', t)))
        text.append(t)
    return re.sub(r'\s+', ' ', ' '.join(text))[:30000]


def _mesaj(raw, eu):
    try:
        msg = message_from_bytes(raw, policy=email_policy.default)
        de_la = email_utils.parseaddr(str(msg['from'] or ''))[1].lower()
        catre = [a.lower() for _, a in email_utils.getaddresses([str(msg['to'] or ''), str(msg['cc'] or '')]) if a]
        d = email_utils.parsedate_to_datetime(str(msg['date'])).date().isoformat()
        return {'data': d, 'de_la': de_la, 'catre': catre, 'subiect': re.sub(r'\s+', ' ', str(msg['subject'] or ''))[:160],
                'text': _text_email(msg), 'trimis': de_la in eu, 'mid': str(msg['message-id'] or '').strip().strip('<>')}
    except Exception:
        return None


def _quote(nume):
    return nume if nume.startswith('"') else '"' + nume.replace('\\', '\\\\').replace('"', '\\"') + '"'


def conturi_email(chei):
    """Conturile din chei.txt: EMAIL / EMAIL_PAROLA, EMAIL_2 / EMAIL_PAROLA_2 ..."""
    out = []
    for k, v in chei.items():
        m = re.fullmatch(r'EMAIL(_\d+)?', k)
        if m and '@' in v:
            suf, adresa = m.group(1) or '', v.strip().lower()
            out.append({'adresa': adresa, 'parola': chei.get('EMAIL_PAROLA' + suf, '').replace(' ', ''), 'sufix': suf,
                        'server': chei.get('IMAP' + suf) or IMAP_SERVERE.get(adresa.split('@')[-1]) or 'imap.' + adresa.split('@')[-1]})
    return out


def conecteaza(cont):
    """Întoarce (conexiunea, None) sau (None, motivul în română)."""
    try:
        M = imaplib.IMAP4_SSL(cont['server'], 993, ssl_context=CTX, timeout=40)
    except Exception as e:
        return None, f'nu mă pot conecta la {cont["server"]} ({type(e).__name__})'
    try:
        M.login(cont['adresa'], cont['parola'])
        return M, None
    except Exception:
        try:
            M.logout()
        except Exception:
            pass
        return None, ('adresa sau parola de aplicație nu e bună. La Gmail trebuie parola de aplicație de 16 litere '
                      '(myaccount.google.com/apppasswords), nu parola obișnuită')


def scrie_cheie(k, v):
    """Schimbă (sau șterge, cu v=None) un rând din chei.txt, fără să atingă restul."""
    linii = open(KEYS, encoding='utf-8-sig').read().splitlines() if os.path.exists(KEYS) else []
    gasit, out = False, []
    for line in linii:
        if re.match(rf'^\s*{re.escape(k)}\s*=', line):
            if v is not None and not gasit:
                out.append(f'{k}={v}')
            gasit = True
        else:
            out.append(line)
    if not gasit and v is not None:
        out.append(f'{k}={v}')
    with open(KEYS, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def citeste_emailuri(cont, eu, stare, mesaje_ecran):
    """Citește (fără să marcheze ca citit) emailurile din ultimele luni legate de cereri."""
    server = cont['server']
    M, eroare = conecteaza(cont)
    if not M:
        mesaje_ecran.append(f'{cont["adresa"]}: {eroare}.')
        return None
    try:
        foldere = {}
        for line in M.list()[1] or []:
            line = line.decode('utf-8', 'ignore') if isinstance(line, bytes) else str(line)
            m = re.match(r'\((.*?)\) (?:"[^"]*"|NIL) (.*)$', line)
            if m:
                for flag, cheie_f in (('\\All', 'toate'), ('\\Sent', 'trimise')):
                    if flag in m.group(1):
                        foldere[cheie_f] = m.group(2).strip()
        domenii = sorted({domeniu(u) for u, e in stare['linkuri'].items()
                          if categorie(e) in ('activ', 'sters') and not ignorat(stare, u, e) and e_adult(stare, u, e)})
        gmail = 'X-GM-EXT-1' in M.capabilities or server == 'imap.gmail.com'
        cautari = []
        if gmail and 'toate' in foldere:
            adrese = sorted({x for d in domenii for x in ((stare['site'].get(d, {}).get('contact') or {}).get('emailuri') or [])}
                            | {(stare['site'].get(d, {}).get('gazda') or {}).get('email') for d in domenii} - {None})
            termeni = domenii + adrese + CUVINTE_EMAIL
            cautari.append((foldere['toate'], ['X-GM-RAW', '"in:sent newer_than:%dd"' % ZILE_EMAIL]))   # tot ce ai trimis
            for i in range(0, len(termeni), 25):
                cautari.append((foldere['toate'], ['X-GM-RAW', '"newer_than:%dd (%s)"' % (ZILE_EMAIL, ' OR '.join(termeni[i:i + 25]))]))
        else:
            de_la = (date.today() - timedelta(days=ZILE_EMAIL)).strftime('%d-%b-%Y')
            for f in ['INBOX'] + ([foldere['trimise']] if 'trimise' in foldere else []):
                cautari.append((f, ['SINCE', de_la]))
        out, vazute = [], set()
        for folder, criterii in cautari:
            if M.select(_quote(folder), readonly=True)[0] != 'OK':
                continue
            tip, data = M.search(None, *criterii)
            ids = (data[0] or b'').split()[-MAX_EMAILURI:] if tip == 'OK' else []
            for i in range(0, len(ids), 50):
                tip, raspuns = M.fetch(b','.join(ids[i:i + 50]), '(BODY.PEEK[]<0.60000>)')
                for item in raspuns or []:
                    if isinstance(item, tuple) and len(item) > 1:
                        m = _mesaj(item[1], eu)
                        k = m and (m['data'], m['de_la'], m['subiect'], tuple(m['catre']))
                        if m and k not in vazute:
                            vazute.add(k)
                            out.append(m)
        return out
    except Exception as e:
        mesaje_ecran.append(f'{cont["adresa"]}: eroare la citire ({type(e).__name__}).')
        return None
    finally:
        try:
            M.logout()
        except Exception:
            pass


def _al(adresa, dom):
    return bool(adresa) and e_al_domeniului(adresa.split('@')[-1], dom)


def _curat(t):
    return t.replace('hxxp', 'http').replace('[.]', '.').replace('(.)', '.').replace('[:]', ':')


def _subiect_baza(sub):
    t = re.sub(r'\[[^\]]*\]', ' ', sub.lower())
    t = re.sub(r'^(\s*(re|fwd?|aw|tr|sv)\s*:\s*)+', '', t.strip())
    t = re.sub(r'^(\s*(re|fwd?)\s*:\s*)+', '', t.strip())
    return re.sub(r'\s+', ' ', t).strip()


def potriveste_emailuri(stare, mesaje):
    """Leagă fiecare email de un site: cereri trimise, confirmări (Google, Bing, Cloudflare) și răspunsuri."""
    for m in mesaje:
        m['text'] = _curat(m['text']); m['subiect_c'] = _curat(m['subiect'])
    pe_site = {}
    for u, e in stare['linkuri'].items():
        if categorie(e) in ('activ', 'sters') and not ignorat(stare, u, e):
            pe_site.setdefault(domeniu(u), []).append((u, e))
    noi = 0
    for dom, lst in pe_site.items():
        s = stare['site'].setdefault(dom, {})
        site_em = set((s.get('contact') or {}).get('emailuri') or [])
        gz = s.get('gazda') or {}
        gz_em = {gz['email']} if gz.get('email') else set()
        reg_em = {(s.get('registrar') or {}).get('email')} - {None}
        url_k = [(u, fara_www(u).lower().rstrip('/')) for u, _ in lst]
        evenim = s.setdefault('emailuri', [])
        vechi = {(x['data'], x['cine'], x['subiect']) for x in evenim}
        fir = {}   # subiectele cererilor trimise pentru site-ul ăsta → canalul
        for m in mesaje:
            if m['trimis']:
                t0 = (m['subiect_c'] + ' ' + m['text']).lower()
                if dom in t0 or any(k and k in t0 for _, k in url_k) or any(a in site_em or _al(a, dom) for a in m['catre']):
                    b = _subiect_baza(m['subiect'])
                    if len(b) > 12:
                        fir[b] = 'site' if any(a in site_em or _al(a, dom) for a in m['catre']) else (
                            'gazda' if any(a in gz_em for a in m['catre']) else 'altul')
        for m in mesaje:
            txt = (m['subiect_c'] + ' ' + m['text']).lower()
            urls = [u for u, k in url_k if k and re.search(re.escape(k) + r'/?(?![\w/%.-])', txt)]
            mentionat = bool(urls) or dom in txt
            canal = tip = None
            if m['trimis']:
                for a in m['catre']:
                    if a in site_em or _al(a, dom):
                        canal, cine = 'site', a
                    elif mentionat and (a in gz_em or (gz.get('email') and _al(a, gz['email'].split('@')[-1]))):
                        canal, cine = 'gazda', a   # aceeași firmă poate găzdui mai multe site-uri: trebuie să-l pomenească
                    elif mentionat and a in reg_em:
                        canal, cine = 'registrar', a
                    if canal:
                        break
                if not canal and mentionat and m['catre']:
                    canal, cine = 'altul', m['catre'][0]
                tip = 'trimis' if canal else None
            else:
                cine = m['de_la']
                for c, doms in DOMENII_CANAL.items():
                    if any(_al(cine, d) for d in doms) and mentionat:
                        canal, tip = c, 'confirmare'
                if not canal:
                    if cine in site_em or _al(cine, dom):
                        canal, tip = 'site', 'raspuns'
                    elif mentionat and (cine in gz_em or (gz.get('email') and _al(cine, gz['email'].split('@')[-1]))):
                        canal, tip = 'gazda', 'raspuns'
                    elif mentionat and cine in reg_em:
                        canal, tip = 'registrar', 'raspuns'
                    elif mentionat and not any(_al(cine, d) for doms in DOMENII_CANAL.values() for d in doms):
                        canal, tip = 'altul', 'raspuns'
                    elif _subiect_baza(m['subiect']) in fir:   # răspuns pe firul unei cereri trimise de tine
                        canal, tip = fir[_subiect_baza(m['subiect'])], 'raspuns'
            if not tip:
                continue
            k = (m['data'], cine, m['subiect'])
            if k in vechi:
                continue
            vechi.add(k)
            noi += tip in ('raspuns', 'confirmare')
            evenim.append({'data': m['data'], 'tip': tip, 'canal': canal, 'cine': cine, 'subiect': m['subiect'],
                           'sters': tip != 'trimis' and bool(STERS_RE.search(m['text'] + ' ' + m['subiect'])),
                           'text': '' if tip == 'trimis' else m['text'][:1500], 'mid': m.get('mid', '')})
            # bifează singur „Am trimis”: linkurile scrise în email sau, dacă nu are linkuri, tot site-ul
            if canal in dict(CANALE) and tip in ('trimis', 'confirmare'):
                for u, e in lst:
                    if categorie(e) == 'activ' and not (e.get('trimis') or {}).get(canal) and (u in urls or not urls):
                        e.setdefault('trimis', {})[canal] = m['data']
        evenim.sort(key=lambda x: x['data'])
        del evenim[:-40]
    return noi


def citeste_tot(stare):
    """Partea lentă (rețeaua): citește conturile. Nu schimbă nimic în stare."""
    conturi = [c for c in conturi_email(citeste_chei()) if c['parola']]
    eu = {c['adresa'] for c in conturi} | ({(stare.get('semnatura') or {}).get('email', '').lower()} - {''})
    toate, mesaje_ecran, stari = [], [], {}
    for c in conturi:
        n = len(mesaje_ecran)
        mesaje = citeste_emailuri(c, eu, stare, mesaje_ecran)
        stari[c['adresa']] = {'ok': mesaje is not None, 'data': acum(),
                              'mesaj': (f'{nr(len(mesaje), "email citit", "emailuri citite")}' if mesaje is not None
                                        else ' '.join(mesaje_ecran[n:]))}
        toate += mesaje or []
    return conturi, toate, mesaje_ecran, stari


def aplica_emailuri(stare, conturi, toate, mesaje_ecran, stari):
    stare.setdefault('email_conturi', {}).update(stari)
    noi = potriveste_emailuri(stare, toate)
    stare['email_text'] = (f'Email verificat: {scurt(acum())} {acum()[11:16]}, {nr(len(conturi), "cont", "conturi")}, '
                           f'{nr(len(toate), "email citit", "emailuri citite")}'
                           + (f', {nr(noi, "răspuns nou", "răspunsuri noi")}.' if noi else '.')
                           + ' Se verifică singur la 5 minute cât e deschisă fereastra neagră.'
                           + (' ' + ' '.join(mesaje_ecran) if mesaje_ecran else ''))
    return stare['email_text']


def verifica_emailul(stare):
    if not [c for c in conturi_email(citeste_chei()) if c['parola']]:
        stare['email_text'] = 'Emailul nu e conectat: conectează-l din raport, la „📧 Emailuri conectate”.'
        return stare['email_text']
    return aplica_emailuri(stare, *citeste_tot(stare))


# ───────────── Ce ai de trimis ─────────────
_site_adult = None
_baza = None


def actualizeaza_baza():
    """Descarcă o dată pe lună lista publică de site-uri adult (porno, videochat, leak)."""
    global _baza
    if os.path.exists(BAZA_ADULT) and time.time() - os.path.getmtime(BAZA_ADULT) < 30 * 86400:
        return None
    try:
        _, text = cere(BAZA_URL, timp=90, maxim=30_000_000, ua=UA_API)
        if text.count('0.0.0.0 ') < 1000:
            raise ValueError('lista e prea scurtă')
        with open(BAZA_ADULT + '.tmp', 'w', encoding='utf-8') as f:
            f.write(text)
        os.replace(BAZA_ADULT + '.tmp', BAZA_ADULT)
        _baza = None
        return f'Baza de site-uri adult actualizată: {nr(len(baza_adult()), "site", "site-uri")}.'
    except Exception as e:
        return ('Baza de site-uri adult nu s-a putut actualiza acum; folosesc lista veche.' if os.path.exists(BAZA_ADULT)
                else f'Baza de site-uri adult nu s-a putut descărca ({type(e).__name__}); încerc data viitoare.')


def baza_adult():
    global _baza
    if _baza is None:
        _baza = set()
        if os.path.exists(BAZA_ADULT):
            with open(BAZA_ADULT, encoding='utf-8', errors='ignore') as f:
                for line in f:
                    p = line.split()
                    if len(p) >= 2 and p[0] in ('0.0.0.0', '127.0.0.1') and '.' in p[1]:
                        d = p[1].lower()
                        _baza.add(d[4:] if d.startswith('www.') else d)
    return _baza


def in_baza(h):
    """Site-ul (sau domeniul lui principal) e în baza de site-uri adult?"""
    b, h = baza_adult(), h.lower()
    p = (h[4:] if h.startswith('www.') else h).split('.')
    return bool(b) and any('.'.join(p[i:]) in b for i in range(len(p) - 1))


def site_adult():
    """Lista din site-uri-adult.txt (domenii)."""
    global _site_adult
    if _site_adult is None:
        _site_adult = []
        if os.path.exists(SITE_ADULT):
            with open(SITE_ADULT, encoding='utf-8-sig') as f:
                for line in f:
                    d = line.split('#')[0].strip().lower()
                    d = re.sub(r'^https?://', '', d).split('/')[0]
                    if d.startswith('www.'):
                        d = d[4:]
                    if d and '.' in d and d not in _site_adult:
                        _site_adult.append(d)
    return _site_adult


def e_adult(stare, url, e):
    """True = conținut adult, False = nu pare, None = nu știm încă (pagina nu s-a deschis)."""
    if 'adult_manual' in e:
        return e['adult_manual']
    s = stare['site'].get(domeniu(url), {})
    if 'adult' in s:
        return s['adult']
    h = gazda(url)
    if any(e_al_domeniului(h, d) for d in site_adult()) or in_baza(h):
        return True
    if e['sursa'] in SURSE_TALE:
        return True
    return e.get('adult')


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
        ajutor = None
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
            'data_trimis': date_[0] if date_ and st in ('trimis', 'de_revenit') else None,
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
            grupuri.setdefault(dom, []).append((url, e, e_adult(stare, url, e)))
        elif cat == 'sters':
            sterse.append({'url': url, 'domeniu': dom, 'gasit': scurt(e.get('gasit')), 'sters': scurt(e.get('sters')),
                           'sters_iso': (e.get('sters') or '')[:10], 'manual': bool(e.get('manual')),
                           'in_cautare': in_cautare_text(e, e.get('sters'))})
        elif cat == 'neverificat':
            neverificate.append({'url': url, 'domeniu': dom, 'motiv': e['motiv']})
    out, alte = [], []
    for dom, lst in grupuri.items():
        lst.sort(key=lambda x: (efectiv(x[1]) != ONLINE, x[0]))
        es = [e for _, e, _ in lst]
        si = stare['site'].get(dom, {})
        g = si.get('gazda')
        canale = [canal_vedere(cid, nume, es, g) for cid, nume in CANALE]
        stari = {k['stare'] for k in canale}
        cat = 'de_trimis' if 'de_trimis' in stari else 'de_revenit' if 'de_revenit' in stari else 'astept'
        gasit = min((e['gasit'] for e in es if e.get('gasit')), default=None)
        adult = [a for _, _, a in lst]
        tinta = out if (True in adult or None in adult) else alte   # „alte” = toate paginile par fără conținut adult
        tinta.append({
            'domeniu': dom, 'categorie': cat, 'gazda': g, 'canale': canale,
            'registrar': si.get('registrar'), 'contact': si.get('contact'),
            'ue': bool(g and g.get('tara') in UE),
            'site_trimis': min(((e.get('trimis') or {}).get('site') for e in es if (e.get('trimis') or {}).get('site')), default=None),
            'manual_adult': si.get('adult'), 'stiu': si.get('stiu'), 'rezolvat': si.get('rezolvat'),
            'emailuri': [{**x, 'zi': scurt(x['data']), 'nou': zile_de_la(x['data']) < ZILE_NOU}
                         for x in reversed((si.get('emailuri') or [])[-6:])],
            'nou': all(e['sursa'] not in SURSE_TALE for e in es) and bool(gasit) and zile_de_la(gasit) < ZILE_NOU,
            'linkuri': [{'url': u, 'ef': efectiv(e), 'motiv': e['motiv'], 'sursa': e['sursa'], 'gasit': scurt(e.get('gasit')),
                         'nou': e_nou(e), 'manual': bool(e.get('manual')), 'cautare': in_cautare_text(e),
                         'ultima_online': scurt(next((i['data'] for i in reversed(e['istoric']) if i['stare'] == ONLINE), None))}
                        for u, e, _ in lst]})
    ordine = {'de_trimis': 0, 'de_revenit': 1, 'astept': 2}
    out.sort(key=lambda g: (ordine[g['categorie']], not g['nou'], -len(g['linkuri']), g['domeniu']))
    sterse.sort(key=lambda s: (s['sters_iso'], s['url']), reverse=True)
    activ = [l for g in out for l in g['linkuri']]
    activ_url = {l['url'] for l in activ}
    rez = {
        'de_trimis': sum(g['categorie'] == 'de_trimis' for g in out),
        'de_trimis_linkuri': sum(len(g['linkuri']) for g in out if g['categorie'] == 'de_trimis'),
        'de_revenit': sum(g['categorie'] == 'de_revenit' for g in out),
        'astept': sum(g['categorie'] == 'astept' for g in out),
        'online': sum(l['ef'] == ONLINE for l in activ), 'neverificate_active': sum(l['ef'] != ONLINE for l in activ),
        'noi': sum(l['nou'] for l in activ), 'sterse': len(sterse), 'neverificate': len(neverificate),
        'nesters_google': sum(1 for lst in grupuri.values() for u, e, _ in lst if u in activ_url and not (e.get('trimis') or {}).get('google')),
        'nesters_bing': sum(1 for lst in grupuri.values() for u, e, _ in lst if u in activ_url and not (e.get('trimis') or {}).get('bing')),
        'alte': len(alte),
        'raspunsuri_noi': [{'domeniu': g['domeniu'], **x} for g in out for x in g['emailuri']
                           if x['nou'] and x['tip'] != 'trimis'],
        'inbox': sorted([{'domeniu': dom, 'zi': scurt(x['data']), 'data': x['data'], 'cine': x['cine'], 'subiect': x['subiect'],
                          'canal': x['canal'], 'tip': x['tip'], 'sters': x.get('sters'), 'text': x.get('text', ''), 'mid': x.get('mid', ''),
                          'cheie': x['data'] + '|' + x['cine'] + '|' + x['subiect'],
                          'linkuri': [u for u, e in stare['linkuri'].items() if domeniu(u) == dom and categorie(e) == 'activ'][:60]}
                         for dom, si in stare['site'].items() for x in (si.get('emailuri') or [])
                         if x['tip'] != 'trimis' and zile_de_la(x['data']) <= 45
                         and (x['data'] + '|' + x['cine'] + '|' + x['subiect']) not in set(stare.get('email_rezolvate') or [])],
                        key=lambda x: x['data'], reverse=True),
    }
    return {'generat': scurt(acum()) + ' ' + acum()[11:], 'azi': date.today().isoformat(),
            'azi_ro': date.today().strftime('%d.%m.%Y'), 'interactiv': interactiv, 'token': token,
            'folder': HERE, 'cautare_text': text_cautare(stare['cautare']), 'email_text': stare.get('email_text') or '', 'rezumat': rez, 'grupuri': out, 'sterse': sterse,
            'neverificate': sorted(neverificate, key=lambda x: x['url']),
            'ignorate': sorted(ignorate, key=lambda x: x['url']) + [{'domeniu': d, 'tot_site': True} for d in sorted(dom_ignorate)],
            'alte': sorted(alte, key=lambda g: g['domeniu']), 'semnatura': stare.get('semnatura') or {},
            'conturi': [{'adresa': c['adresa'], **(stare.get('email_conturi') or {}).get(c['adresa'], {'ok': None, 'mesaj': 'neverificat încă'})}
                        for c in conturi_email(citeste_chei())],
            'poze': stare.get('poze') or [], 'poze_toate': len(poze_de_cautat(stare)),
            'baza': len(baza_adult()),
            'cuvinte': cuvinte(stare), 'intrebare': intrebare_implicita(stare), 'cautari_nume': CAUTARI,
            'cautare_acum': {**(stare.get('cautare_acum') or {}), 'zi': scurt((stare.get('cautare_acum') or {}).get('data'))}
                            if stare.get('cautare_acum') else None,
            'texte': TEXTE, 'formulare': FORMULARE, 'zile_site': ZILE_REVENIRE_SITE}


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
        principale = {g['domeniu'] for g in vedere(stare)['grupuri']} if a.get('toate') else set()
        for url, e in stare['linkuri'].items():
            dom = domeniu(url)
            if (dom in principale or dom == a.get('domeniu')) and not ignorat(stare, url, e):
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
    elif tip == 'adult':   # „E conținut furat” / „nu e” pentru tot site-ul
        s = stare['site'].setdefault(a['domeniu'], {})
        if a.get('valoare') is None:
            s.pop('adult', None)
        else:
            s['adult'] = bool(a['valoare'])
    elif tip == 'nota_site':
        si = stare['site'].setdefault(a['domeniu'], {})
        for k in ('stiu', 'rezolvat'):
            if k in a:
                if a[k] is None:
                    si.pop(k, None)
                else:
                    si[k] = bool(a[k])
    elif tip == 'semnatura':
        stare['semnatura'] = {'nume': str(a.get('nume', ''))[:200].strip(), 'email': str(a.get('email', ''))[:200].strip()}
    elif tip == 'email_adauga':
        adresa = str(a.get('adresa', '')).strip().lower()
        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[a-z]{2,}', adresa):
            raise ValueError('adresa de email nu e scrisă bine')
        chei = citeste_chei()
        existent = next((c for c in conturi_email(chei) if c['adresa'] == adresa), None)
        suf = existent['sufix'] if existent else next(
            x for x in [''] + [f'_{i}' for i in range(2, 20)] if not chei.get('EMAIL' + x))
        cont = {'adresa': adresa, 'parola': str(a.get('parola', '')).replace(' ', ''), 'sufix': suf,
                'server': str(a.get('server') or '').strip() or IMAP_SERVERE.get(adresa.split('@')[-1]) or 'imap.' + adresa.split('@')[-1]}
        M, eroare = conecteaza(cont)
        if not M:
            raise ValueError('Nu m-am putut conecta: ' + eroare + '.')
        M.logout()
        scrie_cheie('EMAIL' + suf, adresa)
        scrie_cheie('EMAIL_PAROLA' + suf, cont['parola'])
        if a.get('server'):
            scrie_cheie('IMAP' + suf, cont['server'])
        stare.setdefault('email_conturi', {})[adresa] = {'ok': True, 'mesaj': 'conectat', 'data': cand}
        verifica_emailul(stare)
    elif tip == 'email_sterge':
        for c in conturi_email(citeste_chei()):
            if c['adresa'] == a.get('adresa'):
                for k in ('EMAIL', 'EMAIL_PAROLA', 'IMAP'):
                    scrie_cheie(k + c['sufix'], '' if (k == 'EMAIL' and not c['sufix']) else None)
                (stare.get('email_conturi') or {}).pop(c['adresa'], None)
    elif tip == 'email_verifica':
        verifica_emailul(stare)
    elif tip == 'email_rezolvat':
        r = stare.setdefault('email_rezolvate', [])
        if a.get('cheie') and a['cheie'] not in r:
            r.append(str(a['cheie'])[:400])
    elif tip == 'cuvinte':
        lista = [w.strip().lstrip('#')[:40] for w in re.split(r'[,\n]', str(a.get('text', '')))]
        stare['cuvinte'] = [w for i, w in enumerate(lista) if w and w not in lista[:i]][:15]
    elif tip == 'cauta_acum':
        cauta_acum(stare, str(a.get('q', '')), a.get('motor', 'google'), str(a.get('timp', '')))
    elif tip == 'cautare_respinge':
        r = stare.setdefault('cautare_respinse', [])
        k = cheie(str(a.get('url', '')))
        if k not in r:
            r.append(k)
        ca = stare.get('cautare_acum') or {}
        ca['rezultate'] = [x for x in ca.get('rezultate', []) if cheie(x['url']) != k]
    elif tip == 'cautare_inchide':
        stare.pop('cautare_acum', None)
    elif tip == 'poze':
        poze = stare.setdefault('poze', [])
        for u in gaseste_linkuri(str(a.get('text', ''))[:100_000]):
            if u not in poze:
                poze.append(u)
    elif tip == 'poza_sterge':
        stare['poze'] = [u for u in stare.get('poze') or [] if u != a.get('url')]
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
        adaugate = {cheie(u) for u in noi}
        for x in (stare.get('cautare_acum') or {}).get('rezultate', []):
            if cheie(x['url']) in adaugate:
                x['stiut'] = True
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
    n = reaplica_jurnal(stare)
    if n:
        salveaza(stare)
        scrie_raport(stare)
        print(f'Am pus din nou {nr(n, "bifă salvată", "bife salvate")} din bife-jurnal.txt.')
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
            if self.path.split('?')[0] == '/date':
                with lacat:
                    reincarca(stare)
                    corp = json.dumps(vedere(stare, True, token), ensure_ascii=False)
                return self._raspunde(200, corp, 'application/json; charset=utf-8')
            if self.path.split('?')[0] != '/':
                return self._raspunde(404, 'Nu există')
            with lacat:
                reincarca(stare)
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
                    reincarca(stare)
                    aplica(stare, a)
                    scrie_jurnal(a)
                    salveaza(stare)
                    scrie_raport(stare)
                    corp = json.dumps(vedere(stare, True, token), ensure_ascii=False)
                self._raspunde(200, corp, 'application/json; charset=utf-8')
            except Exception as e:
                self._raspunde(400, f'{type(e).__name__}: {e}')

    try:
        with socket.create_connection(('127.0.0.1', 8765), timeout=1):
            pass
        print('\nProgramul e deja deschis în altă fereastră neagră. Îți deschid raportul de acolo: http://127.0.0.1:8765/')
        print('(Dacă ai schimbat verificare.py, închide întâi fereastra veche și pornește din nou.)')
        webbrowser.open('http://127.0.0.1:8765/')
        return
    except OSError:
        pass
    srv = None
    for port in list(range(8765, 8776)) + [0]:
        try:
            srv = ThreadingHTTPServer(('127.0.0.1', port), H)
            break
        except OSError:
            continue
    def email_automat():
        while True:
            time.sleep(300)
            try:
                if not [c for c in conturi_email(citeste_chei()) if c['parola']]:
                    continue
                with lacat:
                    cop = json.loads(json.dumps(stare))
                rez = citeste_tot(cop)          # rețeaua, fără să blocheze pagina
                with lacat:
                    reincarca(stare)
                    aplica_emailuri(stare, *rez)
                    salveaza(stare)
                    scrie_raport(stare)
            except Exception as e:
                print('Verificarea automată a emailului:', type(e).__name__)
    threading.Thread(target=email_automat, daemon=True).start()
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
        m = actualizeaza_baza()
        if m:
            print(m)
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
        print('Caut la fiecare site hostingul, adresa de email și pagina de DMCA...')
        actualizeaza_site(stare)
        print('Citesc emailul (doar citire)...')
        print('  ' + verifica_emailul(stare))
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
.rez{margin:10px 0;padding-bottom:8px;border-bottom:1px solid #eee}.rez.stiut{opacity:.6}
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
dialog.dlg{max-width:760px;width:calc(100% - 32px);border:0;border-radius:12px;padding:18px 20px;box-shadow:0 12px 40px rgba(0,0,0,.25)}
dialog::backdrop{background:rgba(0,0,0,.35)}.rand{margin:8px 0;word-break:break-word}
dialog textarea{min-height:280px;font-family:ui-monospace,Consolas,monospace;font-size:13px}
.setg{display:grid;grid-template-columns:1fr 1fr auto;gap:10px;align-items:end;margin-top:8px}
.setg label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--mut)}
.setg input{font:inherit;color:var(--ink);padding:7px 9px;border:1px solid #d5cdc7;border-radius:6px;min-width:0}
@media (max-width:640px){.setg{grid-template-columns:1fr}}
.ok{color:var(--verde);font-weight:600}
.em{margin-top:10px;font-size:13px;background:var(--gri-bg);border-radius:8px;padding:8px 11px}.em ul{margin:4px 0 0;padding-left:18px}
.em li.nou{font-weight:600}.help li{margin:5px 0}
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
  let r;
  try {
    r = await fetch('/actiune', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                 body: JSON.stringify({...a, token: D.token})});
  } catch (e) {
    alert('Nu s-a salvat: fereastra neagră a programului e închisă. Pornește din nou raport.bat.');
    if (btn) btn.disabled = false;
    return;
  }
  if (!r.ok) {
    alert((await r.text()).replace(/^ValueError: /, ''));
    if (btn) btn.disabled = false;
    return;
  }
  D = await r.json();
  randeaza();
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

const LUNI_EN = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const en = iso => { const [y, m, d] = iso.slice(0, 10).split('-').map(Number); return d + ' ' + LUNI_EN[m - 1] + ' ' + y; };

function completeaza(tip, g, extra) {
  const [sub, corp] = D.texte[tip];
  const v = {linkuri: g.linkuri.map(l => l.url).join('\n'), nume: D.semnatura.nume || '[Numele legal complet]',
             email: D.semnatura.email || '[Emailul separat]', azi: en(D.azi), site: g.domeniu, ...(extra || {})};
  const f = t => t.replace(/\{(\w+)\}/g, (m, k) => (k in v ? v[k] : m));
  return [f(sub), f(corp)];
}
function arataEmail(titlu, catre, tip, g, extra, nota) {
  const [sub, corp] = completeaza(tip, g, extra);
  const ta = h('textarea', {readonly: true});
  ta.value = corp;
  const dlg = h('dialog', {class: 'dlg'},
    h('h3', {}, titlu),
    nota && h('div', {class: 'mut'}, nota),
    (!D.semnatura.nume || !D.semnatura.email) && h('p', {class: 'banner'}, 'Completează sus „Datele tale pentru emailuri”, ca să apară în text numele și emailul tău.'),
    catre && catre.length > 0 && h('div', {class: 'rand'}, h('b', {}, 'Către: '), catre.join(', '), ' ',
      h('button', {class: 'mic', onclick: e => copiaza(catre.join(', '), e.target)}, 'Copiază adresa')),
    !(tip === 'google' || tip === 'bing') && h('div', {class: 'rand'}, h('b', {}, 'Subiect: '), sub, ' ', h('button', {class: 'mic', onclick: e => copiaza(sub, e.target)}, 'Copiază subiectul')),
    ta,
    h('div', {class: 'rand'}, h('button', {onclick: e => copiaza(corp, e.target)}, 'Copiază textul'), ' ',
      h('button', {class: 'sec', onclick: () => dlg.close()}, 'Închide')),
    h('p', {class: 'mut'}, 'Trimiți din emailul separat. După ce trimiți, apeși „Am trimis” pe card.'));
  dlg.addEventListener('close', () => dlg.remove());
  document.body.append(dlg);
  dlg.showModal();
}
const numePagina = u => { try { return 'pagina ' + (decodeURIComponent(new URL(u).pathname).replace(/^\/+|\/+$/g, '') || 'principală'); } catch (e) { return u; } };

function siteInfo(g, k) {
  const c = g.contact, out = [];
  if (!c) out.push(h('div', {class: 'ca'}, 'Caut adresa site-ului la următoarea verificare.'));
  else if (c.eroare) out.push(h('div', {class: 'ca'}, 'Site-ul nu s-a deschis (blocat în țară sau închis), așa că n-am găsit adresa. Deschide-l cu VPN și caută jos „DMCA” sau „Contact”.'));
  else {
    if (c.emailuri.length) out.push(h('div', {class: 'ca'}, 'Adresa site-ului: ', h('b', {}, c.emailuri.join(', '))));
    if (c.pagini.length) out.push(h('div', {class: 'ca'}, c.pagini.map((u, i) => [i ? ' · ' : '', ext(u, numePagina(u) + ' ↗')])));
    if (!c.emailuri.length && !c.pagini.length) out.push(h('div', {class: 'ca'}, 'N-am găsit email sau pagină de DMCA. Caută jos pe site „DMCA”, „Contact” sau „2257”.'));
  }
  const catre = c && c.emailuri ? c.emailuri : [];
  if (c && !c.eroare && !catre.length && c.pagini.length) out.push(h('div', {class: 'ca'}, h('b', {}, 'Site-ul n-are email. '),
    'Deschide pagina de DMCA / report de mai sus și lipește acolo „📋 Mesajul de trimis” (în formularul lor sau la emailul scris pe pagină).'));
  const btn = (tip, eticheta, extra) => h('button', {class: 'mic', onclick: () => arataEmail(eticheta + ' pentru ' + g.domeniu, catre, tip, g, extra)}, eticheta);
  out.push(h('div', {class: 'cb'}, k.stare === 'de_revenit'
    ? btn('revenire', 'Email de revenire', {data: en(k.data_trimis)})
    : [btn(g.ue ? 'B' : 'A', '📋 Mesajul de trimis'), ' sau alt text: ', btn('A', 'Take It Down (A)'), btn('B', 'GDPR (B)' + (g.ue ? ' ★ site din UE' : '')), btn('C', 'DMCA (C)')]));
  return out;
}
function gazdaInfo(g) {
  const out = [], gz = g.gazda;
  const extra = rol => ({rol, ip: gz && gz.ip ? ' (IP ' + gz.ip + ')' : '',
                         intro: g.site_trimis ? 'I asked the website to remove them on ' + en(g.site_trimis) + '. ' : ''});
  if (gz) out.push(h('div', {class: 'cb'}, h('button', {class: 'mic', onclick: () => arataEmail('Email pentru hosting (' + gz.nume + ')',
    gz.cloudflare ? [] : (gz.email ? [gz.email] : []), 'gazda', g, extra(gz.cloudflare ? 'service provider (Cloudflare)' : 'hosting provider'),
    gz.cloudflare ? 'Cloudflare nu primește email: deschide formularul lor, alege tipul de abuz, lipește linkurile și textul ăsta la descriere.' : null)}, '📋 Mesajul de trimis')));
  const r = g.registrar;
  if (r) out.push(h('div', {class: 'ca'}, 'Dacă nici hostingul nu șterge: firma domeniului, ' + r.nume + (r.email ? ' · ' + r.email : '') + ' ',
    h('button', {class: 'mic', onclick: () => arataEmail('Email pentru firma domeniului (' + r.nume + ')', r.email ? [r.email] : [], 'gazda', g, extra('domain registrar'))}, 'Email')));
  return out;
}

const CAUTARI_BING = 'Kristine Maia, kristinemaia, missfoxyfire, crismaia';
function ghidBing() {
  return h('div', {},
    h('b', {}, 'Pașii în formularul Microsoft „Report a Concern”:'),
    h('ol', {},
      h('li', {}, 'Service or product: ', h('b', {}, 'Bing Search'), '.'),
      h('li', {}, 'Link to the content: lipești ', h('b', {}, 'un link'), ' (butonul „📋 Primul link” de pe card) → Continue.'),
      h('li', {}, 'Tipul: ', h('b', {}, 'Non-consensual intimate imagery'), ' (sau „Sharing intimate images without consent”).'),
      h('li', {}, 'Did you report it to the site: ', h('b', {}, 'Yes'), ' dacă ai bifat „Site-ul” la acest card; altfel „No – I have not tried”.'),
      h('li', {}, 'Reference number: gol la primul raport; la următoarele pui numărul primit pe email. Dacă Microsoft răspunde „not enough information”, retrimiți cu numărul lor (SIR…) aici.'),
      h('li', {}, 'Search terms: ', h('b', {}, CAUTARI_BING), ' (butonul „📋 Search terms”).'),
      h('li', {}, 'Country of residence: ', h('b', {}, 'Romania'), ' (UE → se aplică GDPR).'),
      h('li', {}, 'Screenshot: cauți „Kristine Maia” pe bing.com și faci o captură cu rezultatul site-ului, cu numele tău vizibil. Pune-o mereu: fără ea, Microsoft răspunde des „not enough information”.'),
      h('li', {}, 'Linkul: adresa exactă a paginii, copiată din bara browserului (nu doar numele site-ului). Pentru o poză din Bing Imagini: click pe poză → click dreapta → „Copy link”.'),
      h('li', {}, 'Descrierea: lipești textul de mai jos → bifezi confirmările → Submit.')),
    h('p', {}, 'Formularul ia un singur link. Dacă site-ul are mai multe, folosește formularul „revengeporn” de mai jos, care le ia pe toate odată, sau faci câte un raport pe link, cu același număr de referință.'));
}
function canal(g, k) {
  return h('div', {class: 'canal ' + k.stare},
    h('div', {class: 'cn'}, k.nume),
    h('div', {class: 'ct'}, k.text),
    k.ajutor && h('div', {class: 'ca'}, k.ajutor),
    k.id === 'site' && siteInfo(g, k),
    k.id === 'gazda' && gazdaInfo(g),
    (k.id === 'google' || k.id === 'bing') && h('div', {class: 'cb'}, h('button', {onclick: () => arataEmail(
      k.id === 'google' ? 'Mesajul pentru Google · ' + g.domeniu : 'Mesajul pentru Bing · ' + g.domeniu, [], k.id, g, null,
      k.id === 'google' ? 'Deschizi formularul „copyright” de mai jos și copiezi fiecare bucată în câmpul ei. Linkurile de mai jos sunt deja ale acestui site.'
                        : ghidBing())}, '📋 Mesajul de trimis')),
    k.id === 'bing' && h('div', {class: 'cb'}, h('button', {class: 'mic', onclick: e => copiaza(CAUTARI_BING, e.target)}, '📋 Search terms'),
      h('button', {class: 'mic', onclick: e => copiaza(g.linkuri.length ? g.linkuri[0].url : '', e.target)}, '📋 Primul link')),
    h('div', {class: 'cb'},
      LIVE && k.buton && h('button', {onclick: e => act({tip: 'trimis', domeniu: g.domeniu, canal: k.id, data: D.azi}, e.target)}, k.buton),
      LIVE && k.are_data && h('button', {class: 'mic', title: 'Schimbă data sau șterge bifa', onclick: e => {
        const d = cereData(D.azi_ro); if (d !== undefined) act({tip: 'trimis', domeniu: g.domeniu, canal: k.id, data: d}, e.target);
      }}, '✎ data'),
      k.email && h('button', {class: 'mic', onclick: e => copiaza(k.email, e.target)}, 'Copiază adresa'),
      k.linkuri.map(([t, u]) => ext(u, t + ' ↗'))));
}

const NUME_CANAL = {site: 'site', gazda: 'hosting', registrar: 'firma domeniului', google: 'Google', bing: 'Bing', altul: ''};
function emLi(x) {
  const ce = x.tip === 'trimis' ? 'ai trimis la ' + x.cine : x.tip === 'confirmare' ? 'confirmare de la ' + NUME_CANAL[x.canal] : '💬 răspuns de la ' + x.cine;
  return h('li', {class: x.nou && x.tip !== 'trimis' ? 'nou' : ''}, x.zi + ' · ' + ce + (x.canal !== 'altul' && x.tip !== 'confirmare' ? ' (' + NUME_CANAL[x.canal] + ')' : '') + ': „' + x.subiect + '”',
    x.sters && h('b', {class: 'ok'}, ' ✓ spun că au șters'));
}

function texteSect() {
  const g0 = {domeniu: '[site]', linkuri: [{url: '[lipește linkurile aici, câte unul pe rând]'}]};
  const b = (tip, et, extra, nota) => h('button', {class: 'sec', onclick: () => arataEmail(et, [], tip, g0, extra, nota)}, et);
  return [h('h2', {}, '📄 Textele'), h('div', {class: 'box'},
    h('p', {class: 'mut'}, 'Toate textele, gata de copiat. Pe carduri le găsești deja completate cu linkurile site-ului; aici sunt pentru orice alt site.'),
    h('div', {class: 'cb'},
      b('A', 'A · Take It Down (orice site, mai ales din SUA)'), b('B', 'B · GDPR (site din Europa)'), b('C', 'C · DMCA (pozele făcute de tine)'),
      b('revenire', 'Revenire (după 7 zile)', {data: '[data primei cereri]'}),
      b('gazda', 'Hosting / Cloudflare', {rol: 'hosting provider', ip: '', intro: ''}),
      b('gazda', 'Firma domeniului (registrar)', {rol: 'domain registrar', ip: '', intro: ''})))];
}

function conturiSect() {
  const ad = h('input', {type: 'email', placeholder: 'adresa@gmail.com', autocomplete: 'off'});
  const pa = h('input', {type: 'password', placeholder: 'parola de aplicație (16 litere)', autocomplete: 'new-password'});
  const sv = h('input', {type: 'text', placeholder: 'server IMAP (doar dacă nu e Gmail/Yahoo/iCloud)', autocomplete: 'off'});
  return [h('h2', {}, '📧 Emailuri conectate (' + D.conturi.length + ')'), h('div', {class: 'box'},
    D.conturi.length ? h('ul', {class: 'll'}, D.conturi.map(c => h('li', {},
      h('span', {class: 'dot ' + (c.ok ? 'v' : c.ok === false ? 'r' : 'o')}), h('b', {}, c.adresa), ' · ' + c.mesaj, ' ',
      h('button', {class: 'mic', onclick: e => { if (confirm('Deconectez ' + c.adresa + '? Parola se șterge din chei.txt.')) act({tip: 'email_sterge', adresa: c.adresa}, e.target); }}, 'Deconectează'))))
      : h('p', {class: 'mut'}, 'Niciun email conectat. Conectează emailul din care trimiți cererile: programul vede singur ce ai trimis și cine ți-a răspuns.'),
    h('div', {class: 'setg'}, h('label', {}, 'Adresa de email', ad), h('label', {}, 'Parola de aplicație', pa),
      h('button', {onclick: e => {
        if (!ad.value.trim() || !pa.value.trim()) { alert('Scrie adresa și parola de aplicație.'); return; }
        e.target.textContent = 'Mă conectez...';
        act({tip: 'email_adauga', adresa: ad.value, parola: pa.value, server: sv.value}, e.target).then(() => { e.target.textContent = 'Conectează'; });
      }}, 'Conectează')),
    det('imap', 'Alt furnizor de email (nu Gmail)', h('div', {class: 'setg'}, h('label', {}, 'Server IMAP', sv))),
    h('p', {class: 'mut'}, 'Gmail: parola de aplicație se face pe myaccount.google.com/apppasswords (cere verificarea în doi pași). Nu e parola ta obișnuită. ',
      'Programul doar citește: nu trimite, nu șterge, nu marchează nimic ca citit. Parola rămâne doar în chei.txt, pe laptop.'),
    D.conturi.length > 0 && h('button', {class: 'sec', onclick: e => act({tip: 'email_verifica'}, e.target)}, 'Verifică emailul acum'))];
}

function pozeSect() {
  const ta = h('textarea', {placeholder: 'Lipește aici linkurile pozelor (click dreapta pe poză → „Copy image address”), câte unul pe rând.'});
  return [h('h2', {}, '📷 Caută după poză'), h('div', {class: 'box'},
    h('p', {class: 'mut'}, 'Google Lens caută pe tot internetul alte pagini cu aceeași poză, chiar dacă nu scrie numele tău. ',
      'Caut automat și pozele din linkurile tale (cele care se termină în .jpg, .png). Acum sunt ' + nr(D.poze_toate, 'poză', 'poze') + ' de căutat, pe rând, odată cu celelalte căutări.'),
    ta, h('button', {onclick: e => { if (ta.value.trim()) act({tip: 'poze', text: ta.value}, e.target); }}, 'Adaugă pozele'),
    D.poze.length > 0 && det('poze', 'Pozele adăugate de tine (' + D.poze.length + ')', h('ul', {class: 'll'}, D.poze.map(u => h('li', {},
      h('span', {class: 'u'}, u), ' ', h('button', {class: 'mic', onclick: e => act({tip: 'poza_sterge', url: u}, e.target)}, 'Scoate')))))),
    h('p', {class: 'mut'}, 'Pozele de pe telefon sau laptop nu le poate căuta direct: trebuie să fie deja pe internet. Folosește pozele furate (linkul lor de pe site) sau o poză de pe Instagram-ul tău.')];
}

function semnatura() {
  const n = h('input', {type: 'text', placeholder: 'Numele legal complet', autocomplete: 'name'});
  const m = h('input', {type: 'email', placeholder: 'Emailul separat', autocomplete: 'email'});
  n.value = D.semnatura.nume || ''; m.value = D.semnatura.email || '';
  return det('semn', 'Datele tale pentru emailuri' + (D.semnatura.nume ? ' ✓' : ' (completează o dată)'),
    h('div', {class: 'box setg'},
      h('label', {}, 'Numele legal complet', n), h('label', {}, 'Emailul separat', m),
      h('button', {onclick: e => act({tip: 'semnatura', nume: n.value, email: m.value}, e.target)}, 'Salvează')),
    h('p', {class: 'mut'}, 'Apar în emailurile gata scrise. Rămân doar pe laptopul tău.'));
}

function alteSect() {
  return [h('h2', {}, '❔ Alte pagini cu numele tău (' + D.alte.length + ')'),
    h('p', {class: 'mut'}, 'Site-uri unde paginile nu par să aibă conținut adult (reposturi, articole, profiluri). Dacă e ceva furat, apasă „E conținut furat” și site-ul trece la De trimis.'),
    det('alte', 'Arată site-urile', D.alte.map(g => h('div', {class: 'card astept'},
      h('div', {class: 'ch'}, h('h3', {}, g.domeniu), h('span', {class: 'mut'}, nr(g.linkuri.length, 'pagină', 'pagini')),
        LIVE && h('button', {onclick: e => act({tip: 'adult', domeniu: g.domeniu, valoare: true}, e.target)}, 'E conținut furat: mută la De trimis'),
        LIVE && h('button', {class: 'sec', onclick: e => act({tip: 'ignora', domeniu: g.domeniu, valoare: true}, e.target)}, 'Ascunde')),
      h('div', {class: 'acts'},
        h('b', {}, g.stiu === true ? '✓ Le știu' : g.stiu === false ? '✗ Nu le știu' : 'Le știi?'), ' ',
        LIVE && h('button', {class: 'mic', onclick: e => act({tip: 'nota_site', domeniu: g.domeniu, stiu: g.stiu === true ? null : true}, e.target)}, g.stiu === true ? 'Anulează' : 'Le știu'),
        LIVE && h('button', {class: 'mic', onclick: e => act({tip: 'nota_site', domeniu: g.domeniu, stiu: g.stiu === false ? null : false}, e.target)}, g.stiu === false ? 'Anulează' : 'Nu le știu'),
        ' · ', h('b', {}, g.rezolvat ? '✓ Rezolvat' : 'Nerezolvat'), ' ',
        LIVE && h('button', {class: 'mic', onclick: e => act({tip: 'nota_site', domeniu: g.domeniu, rezolvat: g.rezolvat ? null : true}, e.target)}, g.rezolvat ? 'Marchează nerezolvat' : 'Rezolvat ✓')),
      h('ul', {class: 'll'}, g.linkuri.map(l => h('li', {}, ext(l.url, l.url), h('div', {class: 'meta'}, 'găsit ' + l.gasit + ' (' + l.sursa + ')')))))))];
}

function linkLi(l) {
  const on = l.ef === 'ONLINE';
  const meta = [on ? (l.manual ? 'online (verificat de tine)' : 'online')
                   : 'neverificat acum: ' + l.motiv + (l.ultima_online !== '—' ? ' · ultima dată online: ' + l.ultima_online : ''),
                'găsit ' + l.gasit + ' (' + (l.sursa === 'Google Lens' ? 'după poză, Google Lens' : l.sursa) + ')', l.cautare && 'apare în ' + l.cautare].filter(Boolean).join(' · ');
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
    g.emailuri.length > 0 && h('div', {class: 'em'}, h('b', {}, '📧 Din email: '), h('ul', {}, g.emailuri.map(emLi))),
    det('l-' + g.domeniu, 'Linkurile (' + g.linkuri.length + ')',
      h('ul', {class: 'll'}, g.linkuri.map(linkLi)),
      LIVE && h('div', {class: 'acts'},
        h('button', {class: 'mic', onclick: e => act({tip: 'adult', domeniu: g.domeniu, valoare: false}, e.target)}, 'Nu e conținut adult: mută la „Alte pagini”'),
        h('button', {class: 'mic', onclick: e => {
          if (confirm('Ascund tot site-ul ' + g.domeniu + ' din raport?')) act({tip: 'ignora', domeniu: g.domeniu, valoare: true}, e.target);
        }}, 'Nu e conținut furat: ascunde tot site-ul'))));
}

function tile(cls, n, eticheta, mic) { return h('div', {class: 'tile ' + cls}, h('b', {}, n), eticheta, mic && h('br'), mic && h('small', {}, mic)); }

function todo(lista) {
  const R = D.rezumat;
  const box = h('div', {class: 'box'});
  if (R.raspunsuri_noi.length) box.append(h('b', {}, '💬 Răspunsuri noi pe email:'), h('ul', {}, R.raspunsuri_noi.map(x =>
    h('li', {}, h('a', {href: '#s-' + x.domeniu}, x.domeniu), ': ' + x.zi + ', de la ' + x.cine + ': „' + x.subiect + '”', x.sters && h('b', {class: 'ok'}, ' ✓ spun că au șters')))));
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
    h('p', {class: 'mut'}, 'Adrese de profil pe care programul le-a ghicit (numele tău + site-uri cunoscute), dar nu le-a putut deschide: site-ul e blocat în Turcia sau protejat. Nu știm încă dacă există. Ce faci: le deschizi cu VPN (sau din România). Dacă vezi pagina cu numele tău → „Există”, și site-ul trece la De trimis. Dacă scrie „not found” sau e gol → „Nu există”, și dispare din listă.'),
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

const CA = {q: null, motor: 'google', timp: 's', cuv: null};
function urlMotor(m, q, timp) {
  const t = {z: 'qdr:d', s: 'qdr:w', l: 'qdr:m', a: 'qdr:y'}[timp];
  if (m === 'bing') return 'https://www.bing.com/search?q=' + encodeURIComponent(q) + (timp === 'z' ? '&filters=ex1%3a%22ez1%22' : timp === 's' ? '&filters=ex1%3a%22ez2%22' : timp === 'l' ? '&filters=ex1%3a%22ez3%22' : '');
  return 'https://www.google.com/search?q=' + encodeURIComponent(q) + (m === 'google_imagini' ? '&tbm=isch' : '') + (t ? '&tbs=' + t : '') + '&safe=off';
}
function cautareSect() {
  if (CA.q === null) CA.q = D.intrebare;
  if (CA.cuv === null) CA.cuv = D.cuvinte.join(', ');
  const inp = h('input', {type: 'text', value: CA.q, style: 'flex:1;min-width:220px', oninput: e => { CA.q = e.target.value; }});
  const sel = (v, opts, onc) => { const s = h('select', {onchange: e => onc(e.target.value)}, opts.map(([k, t]) => h('option', {value: k}, t))); s.value = v; return s; };
  const cuv = h('input', {type: 'text', value: CA.cuv, style: 'flex:1;min-width:220px', placeholder: 'xxx, naked, nude, leaked...', oninput: e => { CA.cuv = e.target.value; }});
  const R = D.cautare_acum;
  const rezultat = x => h('li', {class: 'rez' + (x.stiut ? ' stiut' : '')},
    h('div', {}, h('b', {}, x.titlu || x.url), ' ',
      x.stiut ? h('span', {class: 'tag'}, '✓ deja în evidență') : h('span', {class: 'tag nou'}, '🆕 nou'),
      x.adult && h('span', {class: 'tag'}, '🔞'), !x.nume && h('span', {class: 'tag'}, 'fără numele tău')),
    h('div', {class: 'u'}, ext(x.url, x.url + ' ↗')),
    x.text && h('div', {class: 'mut'}, x.text),
    !x.stiut && LIVE && h('div', {class: 'cb'},
      h('button', {class: 'mic', onclick: e => act({tip: 'adauga', text: x.url}, e.target)}, '✓ E cu mine, adaug la evidență'),
      h('button', {class: 'mic sec', onclick: e => act({tip: 'cautare_respinge', url: x.url}, e.target)}, '✗ Nu e cu mine')));
  return [h('h2', {id: 'cautare'}, '🔎 Caută conținut nou'), h('div', {class: 'box'},
    h('p', {class: 'mut'}, 'Caută numele tale (' + D.cautari_nume.join(', ') + ') împreună cu cuvintele-cheie. Deschide fiecare rezultat nou și uită-te dacă ești tu. Dacă da, apeși „E cu mine” și site-ul apare în „De trimis”, cu mesajele gata.'),
    h('div', {class: 'setg', style: 'display:flex;gap:6px;flex-wrap:wrap;align-items:center'},
      h('b', {}, 'Cuvinte-cheie:'), cuv,
      LIVE && h('button', {class: 'mic', onclick: e => { act({tip: 'cuvinte', text: CA.cuv}, e.target).then(() => { CA.q = D.intrebare; randeaza(); }); }}, 'Salvează cuvintele')),
    h('p', {class: 'mut'}, '5–10 cuvinte, despărțite prin virgulă. Le folosește și căutarea automată, o dată la 3 zile.'),
    h('div', {class: 'setg', style: 'display:flex;gap:6px;flex-wrap:wrap;align-items:center'},
      inp,
      sel(CA.motor, [['google', 'Google'], ['bing', 'Bing'], ['google_imagini', 'Google Imagini']], v => { CA.motor = v; }),
      sel(CA.timp, [['z', 'ultima zi'], ['s', 'ultima săptămână'], ['l', 'ultima lună'], ['a', 'ultimul an'], ['', 'oricând']], v => { CA.timp = v; }),
      LIVE && h('button', {onclick: e => { e.target.textContent = 'Caut...'; act({tip: 'cauta_acum', q: CA.q, motor: CA.motor, timp: CA.timp}, e.target); }}, '🔎 Caută în program')),
    h('div', {class: 'cb'},
      h('button', {class: 'mic sec', onclick: () => window.open(urlMotor(CA.motor === 'bing' ? 'google' : CA.motor, CA.q, CA.timp), '_blank', 'noopener')}, 'Deschide în Google ↗'),
      h('button', {class: 'mic sec', onclick: () => window.open(urlMotor('bing', CA.q, CA.timp), '_blank', 'noopener')}, 'Deschide în Bing ↗'),
      h('button', {class: 'mic sec', onclick: () => { CA.q = D.intrebare; randeaza(); }}, 'Înapoi la căutarea cu cuvintele-cheie')),
    h('p', {class: 'mut'}, '„Caută în program” folosește o căutare SerpApi (din cele 250 gratuite pe lună) și îți arată ce e nou față de evidență. „Deschide în Google/Bing” merge și fără cheie: verifici tu rezultatele și lipești linkurile la „➕ Adaugă linkuri”.'),
    R && [h('h3', {}, 'Rezultatele pentru „' + R.q + '” · ' + R.zi + ' · ' + nr(R.rezultate.filter(x => !x.stiut).length, 'rezultat nou', 'rezultate noi')),
      R.rezultate.length ? h('ul', {class: 'll'}, R.rezultate.map(rezultat)) : h('p', {class: 'ok'}, 'Niciun rezultat nou. 💚'),
      LIVE && h('button', {class: 'mic sec', onclick: e => act({tip: 'cautare_inchide'}, e.target)}, 'Închide rezultatele')])];
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


function emailuriDin(t) {
  return [...new Set((t.match(/[\w.+-]+@[\w-]+(\.[\w-]+)+/g) || []).map(e => e.toLowerCase()))]
    .filter(e => !/cloudflare|kristine|gmail\.com$|noreply|no-reply/.test(e));
}
function raspunsPotrivit(x) {
  const t = (x.text + ' ' + x.subiect).toLowerCase();
  if (/cloudflare/.test(x.cine) && /response to your/.test(t)) {
    const em = emailuriDin(x.text);
    return ['gazda', em.length ? 'Cloudflare îți spune cine găzduiește site-ul: ' + em.join(', ') + '. Trimite-i hostingului mesajul de mai jos.'
                               : 'Cloudflare a răspuns: deschide „Citește mesajul”, acolo scrie hostingul. Trimite-i emailul de la coloana Hosting.', em];
  }
  if (/53-фз|state language|russian language|apostil|рег\.ру|reg\.ru/.test(t))
    return ['r_rusa', 'Cer plângerea în rusă și acte legalizate (procedura lor pentru firme). Le răspunzi o singură dată cu textul de mai jos, în rusă; dacă refuză iar, site-ul rămâne pe drumul Google + Bing.'];
  if (x.sters) return ['r_multumesc', 'Spun că au șters. Verifici linkurile, apoi le mulțumești și ceri să șteargă și copiile.'];
  if (/(provide|send|list|give|include).{0,60}(url|link)|direct (url|link)|plain text|one url per line|specific (url|link)/.test(t))
    return ['r_linkuri', 'Cer linkurile exacte: le trimiți lista, câte unul pe rând, în text simplu.'];
  if (/(ticket|request).{0,40}(created|opened|received)|we (have )?received|will (review|investigate|look into)|thank you for (your )?(report|contacting)/.test(t))
    return [null, 'E doar confirmarea că au primit cererea. Nu trebuie să răspunzi: aștepți câteva zile și apeși „Rezolvat”.'];
  if (/(cannot|can't|unable|will not|won't|not able).{0,40}(remove|delete|act)|not (our|the) (host|responsib)|contact the (site|website|owner|host)/.test(t))
    return ['r_revin', 'Refuză sau te trimit în altă parte. Le răspunzi cu textul de mai jos, iar în aplicație treci la pasul următor (hosting / Cloudflare).'];
  return ['r_revin', 'Dacă linkurile mai sunt online, le răspunzi cu textul de mai jos.'];
}
function inboxSect() {
  const L = D.rezumat.inbox || [];
  if (!L.length) return null;
  return [h('h2', {}, '📬 Mesaje primite (' + L.length + ')'),
    h('p', {class: 'mut'}, 'Răspunsurile la cererile tale, din ultimele 45 de zile. Pentru fiecare ai textul de răspuns gata. Când ai terminat cu unul, apeși „Rezolvat”.'),
    L.map(x => {
      const [tip, sfat, emH] = raspunsPotrivit(x);
      const g = {domeniu: x.domeniu, linkuri: x.linkuri.map(u => ({url: u}))};
      const gm = x.mid ? 'https://mail.google.com/mail/u/0/#search/' + encodeURIComponent('rfc822msgid:' + x.mid)
                       : 'https://mail.google.com/mail/u/0/#search/' + encodeURIComponent('from:' + x.cine);
      return h('div', {class: 'card ' + (x.sters ? 'astept' : 'de_trimis')},
        h('div', {class: 'ch'}, h('h3', {}, x.domeniu), h('span', {class: 'tag'}, x.zi), h('span', {class: 'mut'}, 'de la ' + x.cine),
          x.sters && h('b', {class: 'ok'}, '✓ spun că au șters')),
        h('div', {}, h('b', {}, '„' + x.subiect + '”')),
        x.text && det('m-' + x.cheie, 'Citește mesajul', h('p', {class: 'mut', style: 'white-space:pre-wrap'}, x.text)),
        h('p', {}, '👉 ' + sfat),
        h('div', {class: 'cb'},
          tip === 'gazda' ? h('button', {onclick: () => arataEmail('Email pentru hosting · ' + x.domeniu, emH || [], 'gazda', g,
              {rol: 'hosting provider', ip: '', intro: 'I reported it to Cloudflare, who named you as the hosting provider. '})}, '📋 Emailul pentru hosting')
          : tip && h('button', {onclick: () => arataEmail('Răspuns pentru ' + x.cine, [x.cine], tip, g, {subiect: x.subiect.replace(/^((re|fwd?|aw)\s*:\s*)+/i, '')})}, '📋 Răspunsul gata'),
          ext(gm, 'Deschide în Gmail ↗'),
          LIVE && h('button', {class: 'sec', onclick: e => act({tip: 'email_rezolvat', cheie: x.cheie}, e.target)}, 'Rezolvat ✓'),
          h('a', {href: '#s-' + x.domeniu}, 'la cardul site-ului')));
    })];
}
if (LIVE) setInterval(async () => {
  if (document.querySelector('dialog[open]') || /^(INPUT|TEXTAREA|SELECT)$/.test((document.activeElement || {}).tagName || '')) return;
  try {
    const r = await fetch('/date'); if (!r.ok) return;
    const nou = await r.json();
    if (nou.email_text !== D.email_text || (nou.rezumat.inbox || []).length !== (D.rezumat.inbox || []).length) { D = nou; randeaza(); }
  } catch (e) {}
}, 60000);
function randeaza() {
  const R = D.rezumat;
  const lucru = D.grupuri.filter(g => g.categorie !== 'astept'), astept = D.grupuri.filter(g => g.categorie === 'astept');
  document.getElementById('app').replaceChildren(...curata([
    h('h1', {}, 'Evidența ștergerilor'),
    h('p', {class: 'sub'}, '📁 Folderul programului: ' + D.folder + ' · Verificat: ' + D.generat + (D.baza ? ' · baza de site-uri adult: ' + D.baza.toLocaleString('ro-RO') + ' de site-uri' : ''), D.cautare_text && h('br'), D.cautare_text, D.email_text && h('br'), D.email_text),
    !LIVE && h('div', {class: 'banner'}, 'Ai deschis fișierul raport.html, care e doar de citit. Ca să bifezi, pornește raport.bat (sau scrie python verificare.py --raport) și folosește pagina care se deschide: ',
      h('a', {href: 'http://127.0.0.1:8765/'}, 'http://127.0.0.1:8765'), '.'),
    h('div', {class: 'tiles'},
      tile('r', R.de_trimis, R.de_trimis === 1 ? 'site de trimis' : 'site-uri de trimis', nr(R.de_trimis_linkuri, 'link', 'linkuri')),
      tile('o', R.de_revenit, 'de revenit', 'n-au șters la timp'),
      tile('', R.astept, 'aștept răspuns', 'trimis, încă online'),
      tile('n', R.noi, R.noi === 1 ? 'link nou' : 'linkuri noi', 'găsite singur, 7 zile'),
      tile('v', R.sterse, R.sterse === 1 ? 'link șters' : 'linkuri șterse', 'de la început')),
    inboxSect(),
    todo(lucru),
    cautareSect(),
    LIVE && semnatura(),
    h('h2', {}, '📮 De trimis (' + lucru.length + ')'),
    lucru.length ? lucru.map(card) : h('p', {class: 'ok'}, 'Nimic de trimis acum.'),
    h('h2', {}, '⏳ Trimis, aștept să se șteargă (' + astept.length + ')'),
    astept.length ? det('astept', 'Arată site-urile', astept.map(card)) : h('p', {class: 'mut'}, 'Niciunul.'),
    D.alte.length > 0 && alteSect(),
    D.neverificate.length > 0 && [h('h2', {}, '🟠 Profiluri neverificate (' + D.neverificate.length + ')'), neverificate()],
    h('h2', {}, '🟢 Șterse (' + D.sterse.length + ')'), sterse(),
    D.ignorate.length > 0 && [h('h2', {}, 'Ascunse (' + D.ignorate.length + ')'), ignorate()],
    LIVE && adauga(),
    LIVE && pozeSect(),
    LIVE && conturiSect(),
    texteSect(),
    undeTrimiti()]));
}
randeaza();
</script></body></html>
'''

if __name__ == '__main__':
    main()
