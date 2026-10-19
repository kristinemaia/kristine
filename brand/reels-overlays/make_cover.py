#!/usr/bin/env python3
"""Coperta finită pentru un reel: cadrul tău (screenshot din reel) + titlul în cutia culorii zonei.

Rulezi:   python3 brand/reels-overlays/make_cover.py <cod reel> <imagine> [ieșire.jpg]
Exemplu:  python3 brand/reels-overlays/make_cover.py R1 cadru-r1.png
Rezultat: out/coperti/<COD>_coperta.jpg  (1080 x 1920; profilul Instagram arată partea din mijloc, 3:4)
Cadrul e tăiat la 9:16 din centru. Titlul vine din build_overlays.py (lista R); îl poți schimba acolo.
"""
import base64, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_overlays as bo

def main():
    code, img = sys.argv[1], sys.argv[2]
    row = next((r for r in bo.R if r[0] == code), None)
    if not row:
        sys.exit('cod necunoscut: ' + code + ' (alege din: ' + ', '.join(r[0] for r in bo.R) + ')')
    _, zone, _, cover, *_ = row
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(bo.OUT, 'coperti', code + '_coperta.jpg')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ext = os.path.splitext(img)[1].lower().lstrip('.'); mime = 'image/png' if ext == 'png' else 'image/jpeg'
    data = base64.b64encode(open(img, 'rb').read()).decode()
    body = (f'<div style="position:absolute;inset:0;background:url(data:{mime};base64,{data}) center/cover no-repeat"></div>'
            + bo.box(760, cover, bo.ZONE[zone] if zone != 'wine' else bo.WINE, '#FFFFFF' if zone == 'wine' else bo.INK, 84, maxw=900, pad='40px 54px'))
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
    os.unlink(jf.name); os.unlink(sf.name)
    print('gata:', out)

if __name__ == '__main__':
    main()
