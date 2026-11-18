#!/usr/bin/env python3
"""Formatul „Here's how to fix it” (modelul Caroline O'Mahony, 18 nov): carusel educativ cu textul din Instagram, cu fundal
(cutiuțe rotunjite pe fiecare rând, ca opțiunea „text cu fundal” din aplicație). Slide 1: tu + o cutie albă cu întrebarea.
Apoi câte un motiv pe slide: titlul scurt, 2–4 paragrafe în cutii negre, pe poza ta (mâncare, birou, sală).

Rețeta (specs/<nume>.json):
  {"out": "EN-F1-snacking-on-stream",
   "cover": {"photo": "src/…", "focus": 0.3, "text": "For the gamers who … here's how to fix it ➡️", "y": 0.2},
   "slides": [{"photo": "src/…", "focus": 0.5, "y": 0.08, "paras": ["Your meals are lacking protein.", "…"]}, …]}
Rulezi: python3 brand/carousels-en/build_labels.py brand/carousels-en/specs/<nume>.json -> out/<out>-1.png … + <out>.zip"""
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
#s{position:relative;width:1080px;height:1350px;overflow:hidden;font-family:Inter,sans-serif}
#s>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.col{position:absolute;left:70px;right:70px;text-align:center}
.p{margin-bottom:14px;font-size:35px;font-weight:600;line-height:1.36;letter-spacing:-.2px}
.p span{padding:5px 16px;border-radius:12px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.dark span{background:#000;color:#fff}
.light span{background:#fff;color:#000}
.cov{font-size:39px;font-weight:700}
"""

def slide(bg, y, paras, cls, extra=''):
    ps = ''.join('<div class="p %s %s"><span>%s</span></div>' % (cls, extra, E(p)) for p in paras)
    return '<div id="s"><img src="%s"><div class="col" style="top:%dpx">%s</div></div>' % (bg, int(1350 * y), ps)

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
    head = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700&display=swap" rel="stylesheet">'
            '<style>%s</style></head><body>' % CSS)
    c = spec['cover']
    jobs = [slide(cover(path(c['photo']), c.get('focus', 0.3)), c.get('y', 0.2), [c['text']], 'light', 'cov')]
    for s in spec['slides']:
        jobs.append(slide(cover(path(s['photo']), s.get('focus', 0.45)), s.get('y', 0.08), s['paras'], 'dark'))
    files = [os.path.join(OUT, '%s-%d.png' % (spec['out'], n)) for n in range(1, len(jobs) + 1)]
    tmp = tempfile.mkdtemp(); jf = os.path.join(tmp, 'j.json'); json.dump([[f, head + h + '</body></html>'] for f, h in zip(files, jobs)], open(jf, 'w'))
    jsf = os.path.join(tmp, 'r.js'); open(jsf, 'w').write(JS)
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf, jf], check=True, env=env)
    z = os.path.join(HERE, spec['out'] + '.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files: zf.write(f, os.path.basename(f))
    print('gata:', len(files), 'slide-uri ->', z)
