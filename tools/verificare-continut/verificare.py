#!/usr/bin/env python3
"""Verificare conținut: caută dacă paginile cu numele tău mai sunt online și ține evidența până se șterg.

Ce face (fără să descarce sau să arate poze):
  1. Construiește adresele paginilor de „profil” de pe site-urile cunoscute, pentru fiecare nume din NUME.
  2. Adaugă linkurile tale din linkuri.txt (câte unul pe rând; liniile cu # sunt ignorate).
  3. Verifică fiecare adresă: ONLINE (pagina există și conține numele), ȘTERS (404/410 sau numele nu mai apare),
     NU POT VERIFICA (site blocat în țară, protecție Cloudflare, eroare) → verifici manual sau cu VPN.
  4. Ține istoricul în stare.json: când a fost găsit, când a fost verificat ultima dată, când a dispărut.
  5. Face raport.html (îl deschizi în browser) cu tot tabelul, sortat: întâi ce e încă online.

Rulezi: python verificare.py      (sau dublu-click pe verificare.bat, pe Windows)
Totul rămâne pe laptopul tău; nimic nu se trimite nicăieri.
"""
import html, json, os, re, ssl, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'stare.json')
LINKS = os.path.join(HERE, 'linkuri.txt')
REPORT = os.path.join(HERE, 'raport.html')

# Numele tale (le poți schimba). Variantele cu liniuță/underscore se fac automat.
NUME = ['kristinemaia', 'kristinemaia11', 'crismaia', 'missfoxyfire']

# Paginile de profil de pe site-urile unde a apărut conținutul (din scanarea din 21 nov). {u} = numele lipit, {d} = cu liniuță.
SABLOANE = [
    'https://fapello.com/{u}/', 'https://es.fapello.com/{u}/', 'https://fapello.ru/models/{u}',
    'https://www.erome.vip/models/{u}', 'https://de.thefap.net/@{u}', 'https://nudostar.com/model/{d}/',
    'https://leaked.fans/models/{d}/', 'https://pornrewind.com/creators/{u}', 'https://fapeza.com/{d}/',
    'https://wildskirts.com/{d}/', 'https://fapachi.com/{d}/', 'https://www.masterfap.net/profile/{u}/',
    'https://erothots.co/photos/{u}', 'https://cn.nudogram.com/models/{u}/', 'https://anacams.com/user/{u}/',
    'https://myteenwebcam.com/cam/{u}', 'https://ytboob.com/tag/{u}/', 'https://adultphotosets.best/tags/%40{u}/',
    'https://thefappeningblog.com/gallery/{u}/', 'https://leakgallery.com/{u}', 'https://www.reddit.com/r/{u}/',
]
# Fraze care arată că pagina e goală / ștearsă, chiar dacă serverul răspunde 200.
GOL = ['not found', 'no results', 'nothing found', 'page not found', 'removed', 'does not exist', '404',
       'no posts', 'banned', 'this community has been banned', 'model not found']
BLOCAT = ['attention required', 'just a moment', 'cf-chl', 'erişim engellendi', 'bu internet sitesi', 'access denied']

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'
CTX = ssl.create_default_context()


def variante(n):
    d = re.sub(r'([a-z])(maia)', r'\1-\2', n) if 'maia' in n and '-' not in n else n
    return n, d


def adrese():
    out = []
    for n in NUME:
        u, d = variante(n)
        out += [s.format(u=u, d=d) for s in SABLOANE]
    if os.path.exists(LINKS):
        for line in open(LINKS, encoding='utf-8'):
            line = line.strip()
            if line and not line.startswith('#'):
                out.append(line)
    seen, res = set(), []
    for a in out:
        if a not in seen:
            seen.add(a); res.append(a)
    return res


def verifica(url):
    nume = [n.lower() for n in NUME] + ['kristine maia', 'kristine-maia', 'kristine_maia', 'kristine%20maia']
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en'})
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            body = r.read(400_000).decode('utf-8', 'ignore').lower()
            final = r.geturl()
        if any(b in body[:20000] for b in BLOCAT):
            return 'NU POT VERIFICA', 'blocat (Cloudflare sau blocare în țară)'
        if not any(n in body for n in nume):
            return 'ȘTERS', 'numele nu mai apare pe pagină' + (' (redirecționat)' if final.rstrip('/') != url.rstrip('/') else '')
        if any(g in body[:6000] for g in GOL) and body.count(nume[0]) < 3:
            return 'ȘTERS', 'pagina spune că nu există'
        return 'ONLINE', 'pagina există și conține numele'
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return 'ȘTERS', f'eroare {e.code} (pagina nu mai există)'
        if e.code == 451:
            return 'NU POT VERIFICA', '451: blocat legal în țara ta'
        return 'NU POT VERIFICA', f'eroare {e.code} (protecție sau blocare)'
    except Exception as e:  # timeout, DNS blocat, conexiune refuzată
        return 'NU POT VERIFICA', type(e).__name__ + ': ' + str(e)[:80]


def main():
    azi = datetime.now().strftime('%Y-%m-%d %H:%M')
    stare = json.load(open(STATE, encoding='utf-8')) if os.path.exists(STATE) else {}
    lista = adrese()
    ale_tale = adrese_utilizator()
    print(f'Verific {len(lista)} adrese... (durează 1–3 minute)')
    with ThreadPoolExecutor(8) as ex:
        rez = list(ex.map(verifica, lista))
    for url, (st, motiv) in zip(lista, rez):
        e = stare.get(url, {'gasit': None, 'istoric': []})
        if (st == 'ONLINE' or url in ale_tale) and not e['gasit']:
            e['gasit'] = azi
        prev = e['istoric'][-1]['stare'] if e['istoric'] else None
        if st != prev:
            e['istoric'].append({'data': azi, 'stare': st, 'motiv': motiv})
        e['ultima'] = azi; e['stare'] = st; e['motiv'] = motiv
        if st == 'ȘTERS' and e['gasit'] and not e.get('sters'):
            e['sters'] = azi
        if st == 'ONLINE':
            e.pop('sters', None)
        stare[url] = e
    json.dump(stare, open(STATE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    raport(stare, azi)
    n = {k: sum(1 for v in stare.values() if v['stare'] == k and (v.get('gasit') or k != 'ȘTERS')) for k in ('ONLINE', 'ȘTERS', 'NU POT VERIFICA')}
    print(f"Gata. ONLINE: {n['ONLINE']} · ȘTERSE: {n['ȘTERS']} · de verificat manual: {n['NU POT VERIFICA']}")
    print('Deschide raport.html în browser.')


def raport(stare, azi):
    ordine = {'ONLINE': 0, 'NU POT VERIFICA': 1, 'ȘTERS': 2}
    # profilurile generate care n-au existat niciodată nu apar în raport
    rows = [(u, v) for u, v in stare.items() if v.get('gasit') or v['stare'] != 'ȘTERS' or u in adrese_utilizator()]
    rows.sort(key=lambda x: (ordine[x[1]['stare']], x[0]))
    culoare = {'ONLINE': '#c62828', 'ȘTERS': '#2e7d32', 'NU POT VERIFICA': '#b26a00'}
    def dom(u): return re.sub(r'^https?://(www\.)?', '', u).split('/')[0]
    tr = ''.join(
        f"<tr><td><b style='color:{culoare[v['stare']]}'>{v['stare']}</b><br><small>{html.escape(v['motiv'])}</small></td>"
        f"<td>{html.escape(dom(u))}</td><td class=u><a href='{html.escape(u)}' rel=noreferrer target=_blank>{html.escape(u)}</a></td>"
        f"<td>{v.get('gasit') or '—'}</td><td>{v.get('sters') or '—'}</td><td>{v['ultima']}</td></tr>" for u, v in rows)
    cnt = {k: sum(1 for _, v in rows if v['stare'] == k) for k in culoare}
    open(REPORT, 'w', encoding='utf-8').write(f"""<!doctype html><meta charset=utf-8><title>Evidența ștergerilor</title>
<style>body{{font-family:system-ui,sans-serif;margin:24px;background:#faf7f5;color:#222}}table{{border-collapse:collapse;width:100%;font-size:14px;background:#fff}}
td,th{{border-bottom:1px solid #eee;padding:8px;text-align:left;vertical-align:top}}th{{background:#f3e8ee}}.u{{word-break:break-all;max-width:520px}}
.k{{display:inline-block;margin:0 16px 12px 0;font-size:18px}}</style>
<h1>Evidența ștergerilor</h1><p>Verificat: {azi}. Rulează din nou programul ca să actualizezi.</p>
<div><span class=k style='color:#c62828'>🔴 Încă online: <b>{cnt['ONLINE']}</b></span><span class=k style='color:#b26a00'>🟠 De verificat manual: <b>{cnt['NU POT VERIFICA']}</b></span><span class=k style='color:#2e7d32'>🟢 Șterse: <b>{cnt['ȘTERS']}</b></span></div>
<p><small>„De verificat manual” = site blocat în țară sau protejat. Deschide-l cu VPN; dacă e șters, scrie la începutul liniei din linkuri.txt „# sters”.</small></p>
<table><tr><th>Stare</th><th>Site</th><th>Adresa</th><th>Găsit</th><th>Dispărut</th><th>Ultima verificare</th></tr>{tr}</table>""")


def adrese_utilizator():
    if not os.path.exists(LINKS):
        return set()
    return {l.strip() for l in open(LINKS, encoding='utf-8') if l.strip() and not l.startswith('#')}


if __name__ == '__main__':
    main()
