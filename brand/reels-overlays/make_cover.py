#!/usr/bin/env python3
"""Coperta finită pentru un reel: cadrul tău (screenshot din reel) + titlul în cutia culorii zonei.

Rulezi:   python3 brand/reels-overlays/make_cover.py <cod reel> <imagine> [ieșire.jpg]
Exemplu:  python3 brand/reels-overlays/make_cover.py R1 cadru-r1.png
Rezultat: coperti/<COD>_coperta.jpg  (1080 x 1920; profilul Instagram arată partea din mijloc, 3:4)
Opțional: --sub "text" = un rând mai mic sub titlu (face cutia mai înaltă).
Opțional: --top N  = unde începe cutia cu titlul (implicit 760); o mută sus când fața ta e în mijloc.
Barele negre de sus și de jos din screenshot-uri se taie automat.
Cadrul e tăiat la 9:16 din centru. Titlul vine din build_overlays.py (lista R); îl poți schimba acolo.
"""
import base64, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_overlays as bo

def prepare(path):
    # taie barele negre din screenshot și aduce cadrul la 9:16 (din centru)
    from PIL import Image
    im = Image.open(path).convert('RGB'); w, h = im.size
    px = im.load()
    def dark(y): return max(max(px[x, y]) for x in range(0, w, 8)) < 16
    top = 0
    while top < h // 3 and dark(top): top += 1
    bot = h
    while bot > h * 2 // 3 and dark(bot - 1): bot -= 1
    im = im.crop((0, top, w, bot)); w, h = im.size
    want = 9 / 16
    if w / h > want:                      # prea lat: tai din lateral
        nw = int(h * want); x0 = (w - nw) // 2; im = im.crop((x0, 0, x0 + nw, h))
    else:                                 # prea înalt: tai de sus și de jos
        nh = int(w / want); y0 = (h - nh) // 2; im = im.crop((0, y0, w, y0 + nh))
    out = tempfile.NamedTemporaryFile(suffix='.png', delete=False); im.save(out.name); return out.name

def main():
    sub = None
    if '--sub' in sys.argv:
        i = sys.argv.index('--sub'); sub = sys.argv[i + 1]; del sys.argv[i:i + 2]
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    topv = 760
    if '--top' in sys.argv:
        topv = int(sys.argv[sys.argv.index('--top') + 1]); args = [a for a in args if a != str(topv)]
    code, img = args[0], args[1]
    sys.argv = [sys.argv[0]] + args
    row = next((r for r in bo.R if r[0] == code), None)
    if not row:
        sys.exit('cod necunoscut: ' + code + ' (alege din: ' + ', '.join(r[0] for r in bo.R) + ')')
    _, zone, _, cover, *_ = row
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(bo.HERE, 'coperti', code + '_coperta.jpg')
    img = prepare(img)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ext = os.path.splitext(img)[1].lower().lstrip('.'); mime = 'image/png' if ext == 'png' else 'image/jpeg'
    data = base64.b64encode(open(img, 'rb').read()).decode()
    bgc = bo.ZONE[zone] if zone != 'wine' else bo.WINE; fg = '#FFFFFF' if zone == 'wine' else bo.INK
    if sub:
        cov = (f'<div class="box" data-fit="1" style="top:{topv}px;max-width:900px;background:{bgc};color:{fg};font-size:84px;padding:40px 54px">'
               f'{bo.esc(cover)}<div style="font-size:.62em;font-weight:600;margin-top:14px">{bo.esc(sub)}</div></div>')
    else:
        cov = bo.box(topv, cover, bgc, fg, 84, maxw=900, pad='40px 54px')
    body = (f'<div style="position:absolute;inset:0;background:url(data:{mime};base64,{data}) center/cover no-repeat"></div>' + cov)
    htm = bo.page(body).replace('background:transparent', 'background:#fff')
    js = r"""
const { chromium } = require('playwright'); const it = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.setContent(it.html, { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => { document.querySelectorAll('[data-fit]').forEach(el => { let s = parseFloat(el.style.fontSize);
    const lines = () => Math.round((el.clientHeight - 80) / (s * 1.22)); while (s > 46 && lines() > 3) { s -= 2; el.style.fontSize = s + 'px'; } }); });
  await p.waitForTimeout(80); await p.screenshot({ path: it.file, type: 'jpeg', quality: 92 }); await b.close(); })();
"""
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
        json.dump({'html': htm, 'file': out}, jf); jf.flush(); sf.write(js); sf.flush()
        env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
        subprocess.run(['node', sf.name, jf.name], check=True, env=env)
    os.unlink(jf.name); os.unlink(sf.name); os.unlink(img)
    print('gata:', out)

if __name__ == '__main__':
    main()
