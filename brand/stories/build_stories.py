#!/usr/bin/env python3
"""3 story-uri (1080 x 1920) pentru PDF-ul gratuit „The 5-minute desk stretch”.

Rulezi:  python3 brand/stories/build_stories.py
Rezultat: out/PDF-story-1-hook.png, PDF-story-2-pdf.png, PDF-story-3-link.png
Zona sigură: nimic important în primii 250 px și în ultimii 340 px (interfața Instagram acoperă acolo).
Stickerul cu link și sondajul se pun din aplicație, în zonele goale marcate în instrucțiuni.
"""
import base64, os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
pdf = base64.b64encode(open(os.path.join(HERE, 'pdf-pagina-1.png'), 'rb').read()).decode()
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
S1 = ('<div class="s"><div class="b" style="width:760px;height:760px;background:var(--lilac);right:-300px;top:-200px"></div><div class="b" style="width:620px;height:620px;background:var(--pink);left:-260px;bottom:-180px"></div>'
      '<div class="t" style="top:430px"><h1 style="font-size:132px">Neck stiff after hours at your desk?</h1>'
      '<p class="sub" style="margin:54px 0 0">Here\'s a 5-minute reset you can do from your chair.</p></div>'
      '<div class="foot" style="top:1500px;font-size:36px;color:var(--berry);font-weight:800">Tap to see it →</div></div>')
S2 = ('<div class="s"><div class="b" style="width:700px;height:700px;background:var(--mint);left:-250px;top:-160px"></div><div class="b" style="width:560px;height:560px;background:var(--lilac);right:-220px;bottom:-120px"></div>'
      '<div class="t" style="top:250px;text-align:center"><h1 style="font-size:98px">The 5-minute desk stretch</h1><p class="sub" style="margin:26px 0 0;font-size:42px">4 spots. 1 chair. No equipment.</p></div>'
      '<div style="position:absolute;left:50%;top:640px;width:590px;transform:translateX(-50%) rotate(-2.5deg);background:#fff;border-radius:22px;box-shadow:0 30px 70px rgba(43,36,49,.22);overflow:hidden;border:6px solid #fff">'
      '<img src="data:image/png;base64,' + pdf + '" style="display:block;width:100%"></div>'
      '<div class="foot" style="top:1525px;font-size:34px">Free PDF · 3 pages · printable</div></div>')
S3 = ('<div class="s"><div class="b" style="width:820px;height:820px;background:var(--pink);right:-330px;top:-260px"></div><div class="b" style="width:560px;height:560px;background:var(--blue);left:-240px;bottom:-140px"></div>'
      '<div class="t" style="top:360px"><span class="tag">FREE PDF</span><h1 style="font-size:150px;margin-top:44px">Get it free</h1>'
      '<p class="sub" style="margin:44px 0 0">Tap the link below, enter your email, and it\'s yours.</p></div>'
      '<div style="position:absolute;left:0;right:0;top:1010px;text-align:center;font-size:170px;line-height:1;color:var(--berry)">↓</div>'
      '<div class="foot" style="top:1520px;font-size:28px">General mobility, not medical advice.</div></div>')
js = r"""
const { chromium } = require('playwright'); const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const j of jobs) { await p.setContent(j.html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200); await p.screenshot({ path: j.file, type: 'png' }); }
  await b.close(); })();
"""
import json
jobs = [{'html': page(S), 'file': os.path.join(OUT, n)} for S, n in ((S1, 'PDF-story-1-hook.png'), (S2, 'PDF-story-2-pdf.png'), (S3, 'PDF-story-3-link.png'))]
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
    json.dump(jobs, jf); jf.flush(); sf.write(js); sf.flush()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', sf.name, jf.name], check=True, env=env)
os.unlink(jf.name); os.unlink(sf.name); print('gata:', ', '.join(os.path.basename(j['file']) for j in jobs))
