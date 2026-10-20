#!/usr/bin/env python3
"""Panouri Twitch (320 px lățime) + pop-up pentru OBS (1920 x 1080, fundal transparent).

Rulezi:  python3 brand/twitch/build_panels.py
Rezultat în brand/twitch/panels/:
  panel-1-despre-320.png, panel-2-pdf-gratuit-320.png, panel-3-comanda-320.png, obs-popup-stretch-1920x1080.png
Linkul se pune în Twitch, în câmpul „Image links to” al panoului, nu în imagine.
"""
import base64, json, os, subprocess, tempfile
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'panels')
b64 = lambda f: base64.b64encode(open(os.path.join(HERE, f), 'rb').read()).decode()
photo, pdf = b64('_foto.jpg'), b64('_pdf.png')
CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--blue:#DDE9F7;--mint:#D8F0E4;--lilac:#E9E1F7}
*{box-sizing:border-box}html,body{margin:0;background:transparent}
.p{width:320px;position:relative;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif;text-align:center}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.03em;line-height:1;margin:0}
.b{position:absolute;border-radius:50%}
.tag{display:inline-block;background:var(--berry);color:#fff;font-weight:800;font-size:13px;border-radius:99px;padding:6px 14px;letter-spacing:.05em}
.btn{display:inline-block;background:var(--berry);color:#fff;font-weight:800;font-size:19px;border-radius:99px;padding:12px 26px}
"""
def page(body): return '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700;800&display=swap" rel="stylesheet"><style>' + CSS + '</style></head><body>' + body + '</body></html>'
P1 = ('<div class="p" id="c" style="height:330px"><div class="b" style="width:230px;height:230px;background:var(--lilac);right:-90px;top:-100px"></div><div class="b" style="width:170px;height:170px;background:var(--pink);left:-70px;bottom:-60px"></div>'
      '<div style="position:relative;padding-top:24px"><div style="width:140px;height:140px;border-radius:50%;margin:0 auto;background:url(data:image/jpeg;base64,' + photo + ') center/cover;border:5px solid #fff;box-shadow:0 4px 14px rgba(43,36,49,.15)"></div>'
      '<h1 style="font-size:36px;margin-top:16px">Kristine Maia</h1><p style="margin:8px 22px 0;font-size:15px;font-weight:600;line-height:1.3;color:var(--muted)">Mobility, recovery &amp; good food for people who sit all day</p></div></div>')
P2 = ('<div class="p" id="c" style="height:460px"><div class="b" style="width:220px;height:220px;background:var(--mint);left:-90px;top:-80px"></div><div class="b" style="width:190px;height:190px;background:var(--lilac);right:-70px;bottom:-60px"></div>'
      '<div style="position:relative;padding-top:20px"><span class="tag">FREE PDF</span><h1 style="font-size:30px;margin:12px 20px 0">The 5-minute desk stretch</h1>'
      '<div style="width:178px;margin:16px auto 0;transform:rotate(-2.5deg);background:#fff;border-radius:8px;box-shadow:0 12px 26px rgba(43,36,49,.22);overflow:hidden;border:3px solid #fff"><img src="data:image/png;base64,' + pdf + '" style="display:block;width:100%"></div>'
      '<div style="margin-top:20px"><span class="btn">Get it free →</span></div></div></div>')
P3 = ('<div class="p" id="c" style="height:210px;background:var(--lilac)"><div class="b" style="width:160px;height:160px;background:var(--pink);right:-50px;top:-60px"></div>'
      '<div style="position:relative;padding-top:24px"><p style="margin:0;font-size:18px;font-weight:700">Want the routine?</p><div style="display:inline-block;margin-top:12px;background:var(--ink);color:#fff;font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:46px;letter-spacing:-.02em;border-radius:18px;padding:8px 26px">!stretch</div>'
      '<p style="margin:14px 0 0;font-size:15px;font-weight:600;color:var(--muted)">Type it in chat. I\'ll send the link.</p></div></div>')
POP = ('<div id="c" style="width:1920px;height:1080px;position:relative;font-family:Figtree,sans-serif"><div style="position:absolute;left:60px;bottom:60px;display:flex;align-items:center;gap:26px;background:#FFF9F6;border-radius:34px;padding:22px 40px 22px 22px;box-shadow:0 14px 40px rgba(43,36,49,.28);border:4px solid #F8DCE6">'
       '<div style="width:112px;height:158px;border-radius:10px;overflow:hidden;box-shadow:0 6px 16px rgba(43,36,49,.25);flex:none;transform:rotate(-3deg)"><img src="data:image/png;base64,' + pdf + '" style="display:block;width:100%"></div>'
       '<div><span style="display:inline-block;background:#8A3459;color:#fff;font-weight:800;font-size:24px;border-radius:99px;padding:6px 18px;letter-spacing:.05em">FREE PDF</span>'
       '<div style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:54px;letter-spacing:-.03em;color:#2B2431;line-height:1;margin-top:10px">The 5-minute desk stretch</div>'
       '<div style="font-size:34px;font-weight:700;color:#5C5466;margin-top:10px">Type <span style="background:#2B2431;color:#fff;border-radius:12px;padding:2px 14px;font-weight:800">!stretch</span> in chat</div></div></div></div>')
jobs = [(P1, 'panel-1-despre-320.png', 320, 330, False), (P2, 'panel-2-pdf-gratuit-320.png', 320, 460, False), (P3, 'panel-3-comanda-320.png', 320, 210, False), (POP, 'obs-popup-stretch-1920x1080.png', 1920, 1080, True)]
js = r"""
const { chromium } = require('playwright'); const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => { const b = await chromium.launch(); for (const j of jobs) { const p = await b.newPage({ viewport: { width: j.w, height: j.h } });
  await p.setContent(j.html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
  await p.screenshot({ path: j.file, type: 'png', omitBackground: j.t, clip: { x: 0, y: 0, width: j.w, height: j.h } }); await p.close(); }
  await b.close(); })();
"""
data = [{'html': page(h), 'file': os.path.join(HERE, n), 'w': w, 'h': hh, 't': t} for h, n, w, hh, t in jobs]
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
    json.dump(data, jf); jf.flush(); sf.write(js); sf.flush()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', sf.name, jf.name], check=True, env=env)
os.unlink(jf.name); os.unlink(sf.name)
for d in data: print(os.path.basename(d['file']), os.path.getsize(d['file']) // 1024, 'KB')
