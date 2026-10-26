#!/usr/bin/env python3
"""Story de luni (1080 x 1920): Dope Rope, codul KRISTINEMAIA.

Rulezi:  python3 brand/stories/build_story_luni.py
Rezultat: out/Story-luni-DopeRope.png
Zona sigură: nimic important în primii 250 px și în ultimii 340 px (interfața Instagram acoperă acolo).
Stickerul cu link și sondajul se pun din aplicație, în zonele goale marcate în instrucțiuni.
"""
import base64, json, os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)

CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--blue:#DDE9F7;--mint:#D8F0E4;--lilac:#E9E1F7}
*{box-sizing:border-box}html,body{margin:0}
.s{width:1080px;height:1920px;position:relative;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif}
.b{position:absolute;border-radius:50%}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.035em;line-height:.98;margin:0}
.t{position:absolute;left:90px;right:90px}
.sub{font-size:46px;font-weight:600;line-height:1.28;color:var(--muted)}
.tag{display:inline-block;background:var(--berry);color:#fff;font-weight:800;font-size:38px;border-radius:999px;padding:16px 36px;letter-spacing:.04em}
.foot{position:absolute;left:90px;right:90px;text-align:center;font-size:30px;font-weight:600;color:var(--muted)}
"""
def page(body): return ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700;800&display=swap" rel="stylesheet"><style>' + CSS + '</style></head><body>' + body + '</body></html>')
pic = base64.b64encode(open(os.path.join(HERE, 'coarda-poza.jpg'), 'rb').read()).decode()
S1 = ('<div class="s"><div class="b" style="width:780px;height:780px;background:var(--mint);right:-300px;top:-220px"></div><div class="b" style="width:640px;height:640px;background:var(--pink);left:-260px;bottom:-120px"></div>'
      '<div class="t" style="top:330px"><span class="tag">MOVE MONDAY</span><h1 style="font-size:110px;margin-top:40px">2 minutes of rope before your first match</h1>'
      '<p class="sub" style="margin:54px 0 0">Wakes the legs up after a long sit.</p></div>'
      '<div style="position:absolute;left:90px;right:90px;top:1230px;background:var(--berry);color:#fff;border-radius:36px;padding:44px 40px;text-align:center"><div style="font-size:34px;font-weight:700;opacity:.9">Dope Rope</div><div style="font-family:Bricolage Grotesque,sans-serif;font-weight:800;font-size:78px;letter-spacing:.02em;margin-top:6px">Code KRISTINEMAIA</div><div style="font-size:36px;font-weight:700;margin-top:10px">link in bio</div></div>'
      '<div class="foot" style="top:1530px;font-size:28px">General mobility, not medical advice.</div></div>')
S2 = ('<div class="s"><div class="b" style="width:780px;height:780px;background:var(--mint);right:-300px;top:-220px"></div><div class="b" style="width:640px;height:640px;background:var(--pink);left:-260px;bottom:-120px"></div>'
      '<div class="t" style="top:270px"><span class="tag">MOVE MONDAY</span><h1 style="font-size:104px;margin-top:36px">2 minutes of rope before your first match</h1></div>'
      '<div style="position:absolute;left:150px;right:150px;top:770px;height:570px;border-radius:40px;overflow:hidden;box-shadow:0 30px 70px rgba(43,36,49,.25)"><img src="data:image/jpeg;base64,' + pic + '" style="display:block;width:100%;height:100%;object-fit:cover;object-position:50% 12%"></div>'
      '<div style="position:absolute;left:90px;right:90px;top:1370px;background:var(--berry);color:#fff;border-radius:32px;padding:26px 30px;text-align:center"><div style="font-family:Bricolage Grotesque,sans-serif;font-weight:800;font-size:66px;letter-spacing:.02em">Code KRISTINEMAIA</div><div style="font-size:32px;font-weight:700;margin-top:4px">Dope Rope · link in bio</div></div></div>')
jobs = [{'html': page(S), 'file': os.path.join(OUT, n)} for S, n in ((S1, 'Story-luni-DopeRope.png'), (S2, 'Story-luni-DopeRope-poza.png'))]

js = r"""
const { chromium } = require('playwright'); const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const j of jobs) { await p.setContent(j.html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200); await p.screenshot({ path: j.file, type: 'png' }); }
  await b.close(); })();
"""

with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
    json.dump(jobs, jf); jf.flush(); sf.write(js); sf.flush()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', sf.name, jf.name], check=True, env=env)
os.unlink(jf.name); os.unlink(sf.name); print('gata:', ', '.join(os.path.basename(j['file']) for j in jobs))
