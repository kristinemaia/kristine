#!/usr/bin/env python3
"""Coperta pentru Custom Program pe Payhip (19 nov), în același stil ca a PDF-ului gratuit:
fundal crem, cercuri pastel, titlul mare, două telefoane cu programul (cronometrul și pauza).
Rulezi: python3 brand/payhip/build_cover_program.py -> custom-program-coperta-1280x720.png, -1080x1080.png, -1920x1080.png"""
import base64, json, os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
def b64(f): return 'data:image/png;base64,' + base64.b64encode(open(os.path.join(HERE, f), 'rb').read()).decode()
T, R = b64('screen-timer.png'), b64('screen-rest.png')
CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--mint:#D8F0E4;--lilac:#E9E1F7}
*{box-sizing:border-box}body{margin:0;background:transparent}
.c{position:relative;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif}
.sh{position:absolute;border-radius:50%}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.035em;margin:0;line-height:.95}
.tag{display:inline-block;background:var(--berry);color:#fff;font-weight:700;border-radius:999px}
.sub{color:var(--muted);font-weight:600}
.ph{position:absolute;border-radius:38px;background:#1d1a20;padding:10px;box-shadow:0 24px 50px rgba(43,36,49,.28)}
.ph img{display:block;width:100%;border-radius:30px}
.chips span{display:inline-block;background:#fff;border:2px solid #EBDDE4;border-radius:999px;font-weight:700;color:var(--ink)}
"""
def card(w, h, body): return '<div class="c" id="c" style="width:%dpx;height:%dpx">%s</div>' % (w, h, body)
def phones(x, y, w, gap, rot=5):
    return ('<div class="ph" style="width:%dpx;left:%dpx;top:%dpx;transform:rotate(-%ddeg)"><img src="%s"></div>'
            '<div class="ph" style="width:%dpx;left:%dpx;top:%dpx;transform:rotate(%ddeg)"><img src="%s"></div>') % (w, x, y, rot, T, w, x + gap, y + 50, rot, R)
CHIPS = '<div class="chips" style="margin-top:%dpx">%s</div>'
def chips(fs, pad, mt): return CHIPS % (mt, ''.join('<span style="font-size:%dpx;padding:%s;margin:0 8px 8px 0">%s</span>' % (fs, pad, t) for t in ['Gym or home', 'Video + timer', 'Logs your weights']))
WIDE = card(1280, 720, """
<div class="sh" style="width:700px;height:700px;left:-260px;top:320px;background:var(--pink)"></div>
<div class="sh" style="width:520px;height:520px;right:-120px;top:-250px;background:var(--lilac)"></div>
<div class="sh" style="width:300px;height:300px;right:380px;bottom:-200px;background:var(--mint)"></div>
<div style="position:absolute;left:80px;top:0;bottom:0;width:640px;display:flex;flex-direction:column;justify-content:center">
 <span class="tag" style="font-size:22px;padding:10px 20px;align-self:flex-start">MEMBERSHIP</span>
 <h1 style="font-size:96px;margin-top:22px">Custom<br>Program</h1>
 <p class="sub" style="font-size:28px;margin:22px 0 0;line-height:1.25">Your gym or home plan, built from a<br>2-minute quiz. For people who sit all day.</p>
 %s
 <p style="font-size:22px;margin:18px 0 0;font-weight:700">Kristine Maia</p>
</div>%s""" % (chips(20, '8px 16px', 22), phones(800, 70, 215, 190)))
SQUARE = card(1080, 1080, """
<div class="sh" style="width:760px;height:760px;left:-320px;top:620px;background:var(--pink)"></div>
<div class="sh" style="width:560px;height:560px;right:-220px;top:-260px;background:var(--lilac)"></div>
<div class="sh" style="width:340px;height:340px;right:-60px;bottom:-160px;background:var(--mint)"></div>
<div style="position:absolute;left:80px;top:70px;right:80px">
 <span class="tag" style="font-size:24px;padding:11px 22px">MEMBERSHIP</span>
 <h1 style="font-size:112px;margin-top:20px">Custom Program</h1>
 <p class="sub" style="font-size:30px;margin:18px 0 0;line-height:1.25">Your gym or home plan, built from a 2-minute quiz.</p>
 %s
</div>%s""" % (chips(22, '9px 18px', 18), phones(250, 470, 270, 300, 5)))
HERO = card(1920, 1080, """
<div class="sh" style="width:1000px;height:1000px;left:-360px;top:460px;background:var(--pink)"></div>
<div class="sh" style="width:760px;height:760px;right:-180px;top:-380px;background:var(--lilac)"></div>
<div class="sh" style="width:440px;height:440px;right:560px;bottom:-300px;background:var(--mint)"></div>
<div style="position:absolute;left:140px;top:0;bottom:0;width:900px;display:flex;flex-direction:column;justify-content:center">
 <span class="tag" style="font-size:30px;padding:14px 28px;align-self:flex-start">MEMBERSHIP</span>
 <h1 style="font-size:150px;margin-top:30px">Custom Program</h1>
 <p class="sub" style="font-size:40px;margin:30px 0 0;line-height:1.25">Your gym or home plan,<br>built from a 2-minute quiz.<br>For people who sit all day.</p>
 %s
 <p style="font-size:32px;margin:26px 0 0;font-weight:700">Kristine Maia</p>
</div>%s""" % (chips(30, '12px 24px', 34), phones(1200, 120, 320, 280, 6)))
JS = r"""
const { chromium } = require('playwright');
(async () => { const items = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8')); const b = await chromium.launch(); const p = await b.newPage();
 for (const [file, html, w, h] of items) { await p.setViewportSize({width: w, height: h}); await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200); await (await p.$('#c')).screenshot({ path: file }); }
 await b.close(); })();
"""
if __name__ == '__main__':
    head = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700&display=swap" rel="stylesheet"><style>%s</style></head><body>' % CSS)
    jobs = [[os.path.join(HERE, 'custom-program-coperta-%s.png' % n), head + h + '</body></html>', w, hh] for n, h, w, hh in
            [('1280x720', WIDE, 1280, 720), ('1080x1080', SQUARE, 1080, 1080), ('1920x1080', HERO, 1920, 1080)]]
    tmp = tempfile.mkdtemp(); jf = os.path.join(tmp, 'j.json'); json.dump(jobs, open(jf, 'w')); jsf = os.path.join(tmp, 'r.js'); open(jsf, 'w').write(JS)
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf, jf], check=True, env=env); print('gata')
