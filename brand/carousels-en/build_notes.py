#!/usr/bin/env python3
"""Formatul „Poza + Notes” (modelul Caroline O'Mahony, 18 nov): slide 1 = poza ta la sală, fără text;
slide 2 = antrenamentul zilei, ca o notiță din aplicația Notes de pe iPhone (alb, accente galbene, listă numerotată).
Pare spontan: „am scris antrenamentul în Notes și ți-l arăt”. Oamenii îl salvează și îl fac.

Rețeta (specs/<nume>.json):
  {"out": "EN-N1-glute-day", "photo": "src/gym-black-side.jpg", "focus": 0.3,
   "time": "17:29", "date": "18 November 2026 at 17:29", "title": "Glutes 🍑",
   "items": ["Hip thrust 4x 8-10 (pause at the top)", ...]}
Rulezi: python3 brand/carousels-en/build_notes.py brand/carousels-en/specs/<nume>.json -> out/<out>-1.png, -2.png + <out>.zip
Varianta și mai autentică: scrii lista chiar în Notes pe telefon și faci screenshot; textul e în fișierul JSON."""
import base64, html, io, json, os, subprocess, sys, tempfile, zipfile
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
E = html.escape

def cover(path, focus):
    im = Image.open(path).convert('RGB'); r = max(1080 / im.width, 1350 / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - 1080) // 2; y = int((im.height - 1350) * focus)
    return im.crop((x, y, x + 1080, y + 1350))

ICONS = {  # iconițele din bara Notes, desenate simplu, galbene
    'back': '<svg width="26" height="44" viewBox="0 0 13 22"><path d="M11 2 2 11l9 9" fill="none" stroke="#E0A800" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    'undo': '<svg width="52" height="52" viewBox="0 0 26 26"><circle cx="13" cy="13" r="11.5" fill="none" stroke="#E0A800" stroke-width="1.8"/><path d="M8.5 11.5h6.5a3.5 3.5 0 0 1 0 7h-3M11 9l-2.5 2.5L11 14" fill="none" stroke="#E0A800" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    'redo': '<svg width="52" height="52" viewBox="0 0 26 26"><circle cx="13" cy="13" r="11.5" fill="none" stroke="#C9C9CC" stroke-width="1.8"/><path d="M17.5 11.5H11a3.5 3.5 0 0 0 0 7h3M15 9l2.5 2.5L15 14" fill="none" stroke="#C9C9CC" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    'share': '<svg width="44" height="54" viewBox="0 0 22 27"><path d="M11 2v15M6.5 6.5 11 2l4.5 4.5M7 11H3v14h16V11h-4" fill="none" stroke="#E0A800" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    'more': '<svg width="52" height="52" viewBox="0 0 26 26"><circle cx="13" cy="13" r="11.5" fill="none" stroke="#E0A800" stroke-width="1.8"/><circle cx="8" cy="13" r="1.5" fill="#E0A800"/><circle cx="13" cy="13" r="1.5" fill="#E0A800"/><circle cx="18" cy="13" r="1.5" fill="#E0A800"/></svg>',
}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
#s{width:1080px;height:1350px;background:#fff;font-family:Inter,-apple-system,sans-serif;color:#1c1c1e;position:relative;overflow:hidden}
.sb{display:flex;justify-content:space-between;align-items:center;padding:40px 70px 0 84px;height:120px;font-size:40px;font-weight:600;letter-spacing:-.5px}
.sb .r{display:flex;gap:16px;align-items:center}
.bar{display:flex;align-items:center;justify-content:space-between;padding:22px 52px 0 40px;height:110px}
.bar .l{display:flex;align-items:center;gap:14px;color:#E0A800;font-size:38px;font-weight:400}
.bar .ic{display:flex;gap:44px;align-items:center}
.date{text-align:center;color:#8E8E93;font-size:32px;margin-top:18px}
h1{font-size:72px;font-weight:700;letter-spacing:-1px;margin:40px 0 0 72px;color:#3a3a3c}
ol{margin:26px 70px 0 120px;font-size:41px;line-height:1.36;color:#3a3a3c;padding-left:40px}
li{padding-left:8px;margin-bottom:4px}
li::marker{color:#3a3a3c}
.foot{position:absolute;left:0;right:0;bottom:42px;text-align:center;font-size:24px;color:#B0B0B5}
"""

def notes_html(spec):
    sig = '<svg width="46" height="30" viewBox="0 0 23 15"><rect x="0" y="10" width="4" height="5" rx="1" fill="#1c1c1e"/><rect x="6" y="7" width="4" height="8" rx="1" fill="#1c1c1e"/><rect x="12" y="4" width="4" height="11" rx="1" fill="#1c1c1e"/><rect x="18" y="0" width="4" height="15" rx="1" fill="#C9C9CC"/></svg>'
    wifi = '<svg width="42" height="32" viewBox="0 0 21 16"><path d="M10.5 15 13 12a3.6 3.6 0 0 0-5 0zM5.6 9.6a7 7 0 0 1 9.8 0l1.8-1.8a9.6 9.6 0 0 0-13.4 0zM1.8 5.8a12.4 12.4 0 0 1 17.4 0L21 4A15 15 0 0 0 0 4z" fill="#1c1c1e"/></svg>'
    bat = '<svg width="62" height="30" viewBox="0 0 31 15"><rect x=".7" y=".7" width="26" height="13.6" rx="4" fill="none" stroke="#9a9a9e" stroke-width="1.2"/><rect x="2.6" y="2.6" width="15" height="9.8" rx="2.2" fill="#1c1c1e"/><path d="M28.6 5v5c.9-.3 1.5-1.3 1.5-2.5s-.6-2.2-1.5-2.5z" fill="#9a9a9e"/></svg>'
    items = ''.join('<li>%s</li>' % E(i) for i in spec['items'])
    return ('<div id="s"><div class="sb"><span>%s</span><span class="r">%s%s%s</span></div>'
            '<div class="bar"><span class="l">%s<span>All iCloud</span></span><span class="ic">%s%s%s%s</span></div>'
            '<div class="date">%s</div><h1>%s</h1><ol>%s</ol>%s</div>') % (
        E(spec.get('time', '17:29')), sig, wifi, bat, ICONS['back'], ICONS['undo'], ICONS['redo'], ICONS['share'], ICONS['more'],
        E(spec['date']), E(spec['title']), items,
        '<div class="foot">%s</div>' % E(spec['foot']) if spec.get('foot') else '')

JS = r"""
const { chromium } = require('playwright');
(async () => { const [file, html] = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8')); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
 await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200); await (await p.$('#s')).screenshot({ path: file }); await b.close(); })();
"""

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1])); os.makedirs(OUT, exist_ok=True)
    photo = spec['photo'] if os.path.isabs(spec['photo']) else os.path.join(HERE, spec['photo'])
    f1, f2 = [os.path.join(OUT, '%s-%d.png' % (spec['out'], n)) for n in (1, 2)]
    cover(photo, spec.get('focus', 0.35)).save(f1)
    head = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
            '<style>%s</style></head><body>' % CSS)
    tmp = tempfile.mkdtemp(); jf = os.path.join(tmp, 'j.json'); json.dump([f2, head + notes_html(spec) + '</body></html>'], open(jf, 'w'))
    jsf = os.path.join(tmp, 'r.js'); open(jsf, 'w').write(JS)
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf, jf], check=True, env=env)
    z = os.path.join(HERE, spec['out'] + '.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in (f1, f2): zf.write(f, os.path.basename(f))
    print('gata ->', z)
