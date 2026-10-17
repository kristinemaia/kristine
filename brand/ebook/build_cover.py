#!/usr/bin/env python3
"""Coperta e-book-ului (1600 x 2560, raport 1:1,6, Kindle/Payhip). Rulezi: python3 brand/ebook/build_cover.py
Poza: cover-photo-src.jpg (cadrul larg din bucătărie). Titlul și subtitlul sunt în TITLE / SUB mai jos."""
import base64, io, os, subprocess, json
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
TITLE = 'Stream Day Kitchen'
SUB = 'Simple, filling meals for long days at a desk'
AUTHOR = 'Kristine Maia'
W, H = 1600, 2560
im = Image.open(os.path.join(HERE, 'cover-photo-src.jpg')).convert('RGB')
w, h = im.size  # 1450 x 2576
ch = int(w * H / W)  # înălțimea decupajului la 1:1,6
im = im.crop((0, 0, w, min(ch, h))).resize((W, H), Image.LANCZOS)
buf = io.BytesIO(); im.save(buf, 'JPEG', quality=92)
b64 = base64.b64encode(buf.getvalue()).decode()
HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700&display=swap" rel="stylesheet">
<style>*{{box-sizing:border-box}}body{{margin:0}}
#c{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#222;font-family:Figtree,sans-serif}}
#c img{{position:absolute;inset:0;width:100%;height:100%}}
.top{{position:absolute;left:0;right:0;top:0;height:880px;background:linear-gradient(180deg,rgba(18,12,16,.78) 0%,rgba(18,12,16,.55) 55%,rgba(18,12,16,0) 100%)}}
.bot{{position:absolute;left:0;right:0;bottom:0;height:420px;background:linear-gradient(0deg,rgba(18,12,16,.78) 0%,rgba(18,12,16,0) 100%)}}
h1{{position:absolute;left:110px;right:110px;top:150px;margin:0;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:250px;line-height:.95;letter-spacing:-.035em;color:#fff;text-shadow:0 6px 30px rgba(0,0,0,.35)}}
.sub{{position:absolute;left:114px;right:200px;top:660px;font-size:58px;line-height:1.2;font-weight:600;color:#fff}}
.sub:before{{content:'';display:block;width:140px;height:10px;background:#F8DCE6;border-radius:5px;margin-bottom:34px}}
.by{{position:absolute;left:114px;bottom:120px;font-weight:700;font-size:74px;letter-spacing:.08em;text-transform:uppercase;color:#fff}}
</style></head><body><div id="c"><img src="data:image/jpeg;base64,{b64}"><div class="top"></div><div class="bot"></div>
<h1>{TITLE}</h1><div class="sub">{SUB}</div><div class="by">{AUTHOR}</div></div></body></html>"""
JS = r"""
const { chromium } = require('playwright');
(async () => { const [hf, out] = JSON.parse(process.argv[2]); const html = require('fs').readFileSync(hf, 'utf8'); const b = await chromium.launch();
 const p = await b.newPage({ viewport: { width: 1600, height: 2560 }, deviceScaleFactor: 1 });
 await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
 await (await p.$('#c')).screenshot({ path: out }); await b.close(); })();
"""
out = os.path.join(HERE, 'ebook-coperta-1600x2560.png')
js = os.path.join(HERE, '_r.js'); open(js, 'w').write(JS)
env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
hf = os.path.join(HERE, '_c.html'); open(hf, 'w').write(HTML)
subprocess.run(['node', js, json.dumps([hf, out])], check=True, env=env); os.unlink(js); os.unlink(hf)
t = Image.open(out).convert('RGB'); t.resize((200, 320), Image.LANCZOS).save(os.path.join(HERE, 'ebook-coperta-miniatura-200x320.png'))
t.convert('RGB').save(os.path.join(HERE, 'ebook-coperta-1600x2560.jpg'), quality=90)
print('gata', out)
