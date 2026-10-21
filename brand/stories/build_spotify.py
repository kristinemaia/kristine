#!/usr/bin/env python3
"""Imagini pentru anunțul unui episod nou pe Spotify: story (1080 x 1920) și postare (1080 x 1350).

Rulezi:  python3 brand/stories/build_spotify.py            (fără titlu)
         python3 brand/stories/build_spotify.py "Titlul episodului"   (cu titlul pe imagine)
Rezultat: out/Spotify-story-1080x1920.png și out/Spotify-postare-1080x1350.png
Linkul se pune din Instagram (sticker Link în story, linkul din bio la postare), nu în imagine.
"""
import base64, json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
title = sys.argv[1] if len(sys.argv) > 1 else ''
photo = base64.b64encode(open(os.path.join(HERE, '_foto.jpg'), 'rb').read()).decode()
CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--mint:#D8F0E4;--lilac:#E9E1F7;--green:#1DB954}
*{box-sizing:border-box}html,body{margin:0}
.s{position:relative;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif;text-align:center}
.b{position:absolute;border-radius:50%}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.035em;line-height:.95;margin:0}
.pill{display:inline-block;border-radius:999px;font-weight:800;white-space:nowrap}
"""
def content(w, top, big, small):
    t = (f'<p style="font-family:Bricolage Grotesque,sans-serif;font-weight:800;font-size:{small}px;line-height:1.1;margin:{int(small*.6)}px 80px 0;letter-spacing:-.02em">{title}</p>' if title else '')
    return (f'<div style="position:absolute;left:0;right:0;top:{top}px">'
            f'<div style="width:{int(big*1.5)}px;height:{int(big*1.5)}px;border-radius:50%;margin:0 auto;background:url(data:image/jpeg;base64,{photo}) center/cover;border:12px solid #fff;box-shadow:0 18px 50px rgba(43,36,49,.22)"></div>'
            f'<h1 style="font-size:{big}px;margin-top:{int(big*.45)}px">New episode<br>out now</h1>'
            f'<span class="pill" style="background:var(--green);color:#fff;font-size:{int(big*.34)}px;padding:{int(big*.14)}px {int(big*.3)}px;margin-top:{int(big*.4)}px">Listen on Spotify</span>'
            f'{t}<p style="font-size:{int(big*.3)}px;font-weight:600;color:var(--muted);margin:{int(big*.35)}px 0 0">Kristine Maia · Mobility &amp; Recovery</p></div>')
STORY = ('<div class="s" style="width:1080px;height:1920px">'
         '<div class="b" style="width:760px;height:760px;background:var(--lilac);right:-300px;top:-220px"></div>'
         '<div class="b" style="width:640px;height:640px;background:var(--pink);left:-260px;bottom:-200px"></div>'
         + content(1080, 300, 128, 54) +
         '<div style="position:absolute;left:0;right:0;top:1330px;font-size:130px;color:var(--berry);line-height:1">↓</div></div>')
POST = ('<div class="s" style="width:1080px;height:1350px">'
        '<div class="b" style="width:700px;height:700px;background:var(--lilac);right:-260px;top:-200px"></div>'
        '<div class="b" style="width:560px;height:560px;background:var(--mint);left:-220px;bottom:-180px"></div>'
        + content(1080, 120, 110, 50) +
        '<div style="position:absolute;left:0;right:0;bottom:70px;font-size:40px;font-weight:800;color:var(--berry)">Link in bio</div></div>')
def page(b): return '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700;800&display=swap" rel="stylesheet"><style>' + CSS + '</style></head><body>' + b + '</body></html>'
jobs = [{'html': page(STORY), 'file': os.path.join(OUT, 'Spotify-story-1080x1920.png'), 'w': 1080, 'h': 1920},
        {'html': page(POST), 'file': os.path.join(OUT, 'Spotify-postare-1080x1350.png'), 'w': 1080, 'h': 1350}]
js = r"""
const { chromium } = require('playwright'); const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => { const b = await chromium.launch(); for (const j of jobs) { const p = await b.newPage({ viewport: { width: j.w, height: j.h } });
  await p.setContent(j.html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
  await p.screenshot({ path: j.file, type: 'png' }); await p.close(); } await b.close(); })();
"""
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
    json.dump(jobs, jf); jf.flush(); sf.write(js); sf.flush()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', sf.name, jf.name], check=True, env=env)
os.unlink(jf.name); os.unlink(sf.name); print('gata')
