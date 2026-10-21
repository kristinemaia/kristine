#!/usr/bin/env python3
"""Ecranul „offline” pentru Twitch (1920 x 1080 PNG, sub 10 MB).

Rulezi:  python3 brand/twitch/build_offline.py
Rezultat: brand/twitch/offline/twitch-offline-1920x1080.png
În Twitch: Creator Dashboard → Settings → Channel → Brand → „Video player banner”.
"""
import base64, json, os, subprocess, tempfile
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'offline')
photo = base64.b64encode(open(os.path.join(HERE, '_foto.jpg'), 'rb').read()).decode()
CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--blue:#DDE9F7;--mint:#D8F0E4;--lilac:#E9E1F7}
*{box-sizing:border-box}html,body{margin:0}
.s{width:1920px;height:1080px;position:relative;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif}
.b{position:absolute;border-radius:50%}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.035em;margin:0;line-height:.95}
.pill{display:inline-block;border-radius:999px;font-weight:700;white-space:nowrap}
"""
BODY = ('<div class="s">'
 '<div class="b" style="width:900px;height:900px;background:var(--lilac);right:-260px;top:-380px"></div>'
 '<div class="b" style="width:760px;height:760px;background:var(--pink);left:-300px;bottom:-380px"></div>'
 '<div class="b" style="width:420px;height:420px;background:var(--mint);right:120px;bottom:-190px"></div>'
 '<div style="position:absolute;left:150px;top:190px;width:430px;height:430px;border-radius:50%;background:url(data:image/jpeg;base64,' + photo + ') center/cover;border:14px solid #fff;box-shadow:0 20px 60px rgba(43,36,49,.22)"></div>'
 '<div style="position:absolute;left:700px;top:170px;right:120px">'
 '<span class="pill" style="background:var(--berry);color:#fff;font-size:34px;padding:12px 30px;letter-spacing:.05em">OFFLINE RIGHT NOW</span>'
 '<h1 style="font-size:190px;margin-top:34px">Kristine Maia</h1>'
 '<p style="font-size:54px;font-weight:600;margin:30px 0 0;line-height:1.2">Mobility, recovery &amp; good food for people who sit all day</p>'
 '<p style="font-size:38px;font-weight:600;margin:26px 0 0;color:var(--muted)">Move Monday · Cook with me · Game night, with a stretch break every hour</p></div>'
 '<div style="position:absolute;left:150px;right:150px;bottom:90px;display:flex;gap:26px;align-items:center;flex-wrap:nowrap">'
 '<span class="pill" style="background:var(--ink);color:#fff;font-size:37px;padding:22px 40px">Free 5-minute desk stretch: payhip.com/b/myR5B</span>'
 '<span class="pill" style="background:#fff;border:3px solid #EADFE6;font-size:35px;padding:19px 36px">Instagram · TikTok @kristinemaia11</span></div>'
 '</div>')
html = '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700;800&display=swap" rel="stylesheet"><style>' + CSS + '</style></head><body>' + BODY + '</body></html>'
js = r"""
const { chromium } = require('playwright'); const j = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.setContent(j.html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(250);
  await p.screenshot({ path: j.file, type: 'png' }); await b.close(); })();
"""
out = os.path.join(HERE, 'twitch-offline-1920x1080.png')
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
    json.dump({'html': html, 'file': out}, jf); jf.flush(); sf.write(js); sf.flush()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', sf.name, jf.name], check=True, env=env)
os.unlink(jf.name); os.unlink(sf.name); print(out, os.path.getsize(out) // 1024, 'KB')
