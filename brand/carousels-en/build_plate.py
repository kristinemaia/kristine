#!/usr/bin/env python3
"""Formatul „A Day On My Plate” (modelul Caroline O'Mahony, 18 nov): ce mănânci într-o zi, minimalist.
Slide 1: tu (selfie la oglindă) + titlul mare, îngust, alb cu contur închis, și un subtitlu piersică.
Slide-urile cu mâncare: un singur rând mic, cu litere mici, pe poză (ex. „eggs on toast with tea”).
Un produs cu cod (Bewit, Revo) poate intra la mijloc, ca la ea („one scoop every morning (…)”); atunci descrierea începe cu „ad”.

Rețeta (specs/<nume>.json):
  {"out": "EN-D1-day-on-my-plate",
   "cover": {"photo": "src/mirror-black-1.jpg", "focus": 0.3, "title": "A Day On My Plate", "sub": "…", "y": 0.2},
   "slides": [{"photo": "src/food-oats-banana.jpg", "text": "oats with banana…", "x": 0.08, "y": 0.42, "focus": 0.5, "align": "left"}, …]}
  x, y: unde începe textul (0–1) · align: left / center / right
Rulezi: python3 brand/carousels-en/build_plate.py brand/carousels-en/specs/<nume>.json -> out/<out>-1.png … + <out>.zip"""
import base64, html, io, json, os, subprocess, sys, tempfile, zipfile
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
E = html.escape

def cover(path, focus):
    im = Image.open(path).convert('RGB'); r = max(1080 / im.width, 1350 / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - 1080) // 2; y = int((im.height - 1350) * focus)
    b = io.BytesIO(); im.crop((x, y, x + 1080, y + 1350)).save(b, 'JPEG', quality=92)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
#s{position:relative;width:1080px;height:1350px;overflow:hidden;font-family:'Barlow Condensed',sans-serif}
#s img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.t{position:absolute;color:#fff;paint-order:stroke fill;-webkit-text-stroke:5px #2a2522;text-shadow:0 2px 10px rgba(0,0,0,.35)}
.wrap{position:absolute;left:0;right:0;text-align:center}
.wrap div{color:#fff;paint-order:stroke fill;-webkit-text-stroke:5px #2a2522;text-shadow:0 2px 10px rgba(0,0,0,.35)}
.title{margin:0 60px;font-size:118px;font-weight:700;letter-spacing:-1.5px;line-height:1}
.sub{margin:22px 110px 0;font-size:50px;font-weight:600;line-height:1.12;color:#F7C99B!important;-webkit-text-stroke:4px #2a2522!important}
.cap{font-size:54px;font-weight:600;line-height:1.1;max-width:900px}
"""

def slide_html(bg, inner): return '<div id="s"><img src="%s">%s</div>' % (bg, inner)

JS = r"""
const { chromium } = require('playwright');
(async () => { const items = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8')); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
 for (const [file, html] of items) { await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150); await (await p.$('#s')).screenshot({ path: file }); }
 await b.close(); })();
"""

def path(p): return p if os.path.isabs(p) else os.path.join(HERE, p)

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1])); os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith(spec['out'] + '-'): os.unlink(os.path.join(OUT, f))
    head = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&display=swap" rel="stylesheet">'
            '<style>%s</style></head><body>' % CSS)
    c = spec['cover']; jobs = []
    inner = ('<div class="wrap" style="top:%dpx"><div class="title">%s</div>'
             '<div class="sub">%s</div></div>') % (int(1350 * c.get('y', 0.2)), E(c['title']), E(c.get('sub', '')))
    jobs.append(slide_html(cover(path(c['photo']), c.get('focus', 0.3)), inner))
    for s in spec['slides']:
        al = s.get('align', 'left'); x = int(1080 * s.get('x', 0.08)); y = int(1350 * s.get('y', 0.42))
        pos = 'left:%dpx' % x if al == 'left' else ('right:%dpx' % x if al == 'right' else 'left:90px;right:90px')
        inner = '<div class="t cap" style="%s;top:%dpx;text-align:%s">%s</div>' % (pos, y, al, '<br>'.join(E(l) for l in s['text'].split('\n')))
        jobs.append(slide_html(cover(path(s['photo']), s.get('focus', 0.45)), inner))
    files = [os.path.join(OUT, '%s-%d.png' % (spec['out'], n)) for n in range(1, len(jobs) + 1)]
    tmp = tempfile.mkdtemp(); jf = os.path.join(tmp, 'j.json'); json.dump([[f, head + h + '</body></html>'] for f, h in zip(files, jobs)], open(jf, 'w'))
    jsf = os.path.join(tmp, 'r.js'); open(jsf, 'w').write(JS)
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf, jf], check=True, env=env)
    z = os.path.join(HERE, spec['out'] + '.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files: zf.write(f, os.path.basename(f))
    print('gata:', len(files), 'slide-uri ->', z)
