#!/usr/bin/env python3
"""Imaginile pentru Payhip: coperta produsului gratuit (16:9 și pătrat) și bannerul magazinului.
Rulezi: python3 brand/payhip/build_payhip.py  (folosește previzualizările PDF-ului din library/dist/pdf)"""
import base64, os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
PREV = os.path.join(REPO, 'library', 'dist', 'pdf')
def b64(f):
    return 'data:image/png;base64,' + base64.b64encode(open(os.path.join(PREV, f), 'rb').read()).decode()
P1, P2 = b64('prev-desk-stretch-2.png'), b64('prev-desk-stretch-1.png')
CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--pink2:#F1C3D6;--berry:#8A3459;--blue:#DDE9F7;--mint:#D8F0E4;--lilac:#E9E1F7;--lilac-ink:#4C3A78}
*{box-sizing:border-box}body{margin:0;background:transparent}
.c{position:relative;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif}
.sh{position:absolute;border-radius:50%}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.035em;margin:0;line-height:.95}
.tag{display:inline-block;background:var(--berry);color:#fff;font-weight:700;border-radius:999px}
.pg{position:absolute;border-radius:10px;box-shadow:0 18px 40px rgba(43,36,49,.18);background:#fff}
.pg img{width:100%;display:block;border-radius:10px}
.sub{color:var(--muted);font-weight:600}
.chips span{display:inline-block;border-radius:999px;font-weight:700;margin-right:8px}
"""
def card(w, h, body):
    return '<div class="c" id="c" style="width:%dpx;height:%dpx">%s</div>' % (w, h, body)
WIDE = card(1280, 720, """
<div class="sh" style="width:700px;height:700px;left:-260px;top:300px;background:var(--pink)"></div>
<div class="sh" style="width:520px;height:520px;right:-140px;top:-260px;background:var(--lilac)"></div>
<div class="sh" style="width:300px;height:300px;right:360px;bottom:-200px;background:var(--mint)"></div>
<div style="position:absolute;left:80px;top:0;bottom:0;width:600px;display:flex;flex-direction:column;justify-content:center">
 <span class="tag" style="font-size:22px;padding:10px 20px;align-self:flex-start">FREE PDF</span>
 <h1 style="font-size:84px;margin-top:22px">The 5-minute<br>desk stretch</h1>
 <p class="sub" style="font-size:28px;margin:22px 0 0;line-height:1.25">4 gentle moves for neck, shoulders,<br>wrists and hips. From your chair.</p>
 <p style="font-size:22px;margin:26px 0 0;font-weight:700">Kristine Maia · mobility & recovery for people who sit all day</p>
</div>
<div class="pg" style="width:300px;left:760px;top:120px;transform:rotate(-6deg)"><img src="%s"></div>
<div class="pg" style="width:300px;left:900px;top:170px;transform:rotate(5deg)"><img src="%s"></div>
""" % (P2, P1))
SQUARE = card(1080, 1080, """
<div class="sh" style="width:760px;height:760px;left:-300px;top:560px;background:var(--pink)"></div>
<div class="sh" style="width:560px;height:560px;right:-200px;top:-240px;background:var(--lilac)"></div>
<div style="position:absolute;left:80px;top:90px;width:920px">
 <span class="tag" style="font-size:26px;padding:12px 24px">FREE PDF</span>
 <h1 style="font-size:104px;margin-top:26px">The 5-minute desk stretch</h1>
 <p class="sub" style="font-size:32px;margin:22px 0 0">4 gentle moves. From your chair.</p>
</div>
<div class="pg" style="width:330px;left:170px;top:520px;transform:rotate(-6deg)"><img src="%s"></div>
<div class="pg" style="width:330px;left:560px;top:560px;transform:rotate(5deg)"><img src="%s"></div>
<p style="position:absolute;left:80px;bottom:34px;margin:0;font-size:26px;font-weight:700">Kristine Maia</p>
""" % (P2, P1))
BANNER = card(1500, 500, """
<div class="sh" style="width:620px;height:620px;left:-220px;top:180px;background:var(--pink)"></div>
<div class="sh" style="width:480px;height:480px;right:-120px;top:-240px;background:var(--lilac)"></div>
<div class="sh" style="width:260px;height:260px;right:420px;bottom:-170px;background:var(--mint)"></div>
<div style="position:absolute;left:300px;top:0;bottom:0;width:900px;display:flex;flex-direction:column;justify-content:center;text-align:center;align-items:center">
 <h1 style="font-size:96px">Kristine Maia</h1>
 <p style="font-size:32px;font-weight:600;margin:18px 0 0">Mobility, recovery &amp; good food for people who sit all day</p>
 <div class="chips" style="margin-top:22px"><span style="background:var(--blue);color:#2A5580;font-size:20px;padding:10px 18px">Desk stretches</span><span style="background:var(--mint);color:#1C6550;font-size:20px;padding:10px 18px">Recipes</span><span style="background:var(--lilac);color:var(--lilac-ink);font-size:20px;padding:10px 18px">Recovery</span></div>
</div>
""")
JS = r"""
const { chromium } = require('playwright');
(async () => { const [html, out, w, h] = process.argv.slice(2); const b = await chromium.launch();
 const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
 await p.goto('file://' + html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
 await (await p.$('#c')).screenshot({ path: out, omitBackground: true }); await b.close(); })();
"""
def render(name, body, w, h):
    doc = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700&display=swap" rel="stylesheet"><style>%s</style></head><body>%s</body></html>') % (CSS, body)
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(doc); html = f.name
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
        f.write(JS); js = f.name
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', js, html, os.path.join(HERE, name), str(w), str(h)], check=True, env=env)
    os.unlink(html); os.unlink(js)
    print('gata:', name)
LOGO = card(1000, 1000, """
<div class="sh" style="width:620px;height:620px;left:-170px;top:520px;background:var(--pink)"></div>
<div class="sh" style="width:520px;height:520px;right:-180px;top:-180px;background:var(--lilac)"></div>
<div class="sh" style="width:240px;height:240px;right:120px;bottom:-60px;background:var(--mint)"></div>
<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">
 <h1 style="font-size:190px;line-height:.86">Kristine<br>Maia</h1>
 <p style="font-size:40px;font-weight:700;color:var(--berry);margin:34px 0 0;letter-spacing:.06em">MOVE · RECOVER · EAT WELL</p>
</div>
""")
WORD = '<div class="c" id="c" style="width:1200px;height:300px;background:transparent;display:flex;align-items:center;justify-content:center"><h1 style="font-size:150px">Kristine Maia<span style="color:var(--berry)">.</span></h1></div>'
render('payhip-logo-1000x1000.png', LOGO, 1000, 1000)
render('payhip-logo-orizontal-1200x300.png', WORD, 1200, 300)
render('payhip-produs-1280x720.png', WIDE, 1280, 720)
render('payhip-produs-1080x1080.png', SQUARE, 1080, 1080)
render('payhip-banner-1500x500.png', BANNER, 1500, 500)
