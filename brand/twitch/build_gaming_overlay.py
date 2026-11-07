#!/usr/bin/env python3
"""Overlay pentru scena „gaming” din OBS (1920 x 1080, fundal transparent) + masca pentru cameră.

Rulezi:  python3 brand/twitch/build_gaming_overlay.py
Rezultat în brand/twitch/overlay/:
  gaming-overlay-1920x1080.png   ramă pentru cameră (stânga), „GAMING · Kristine Maia” sus, „Stretch break every 30 min” jos
  gaming-cam-mask-520x580.png    colțuri rotunjite pentru cameră (OBS → Filters → Image Mask/Blend → Alpha Mask)

Camera stă în stânga, unde jocul (WoW) nu are interfață: nu acoperă rama jucătorului (stânga sus),
harta (dreapta sus), questurile (dreapta) și bara de abilități (jos, la mijloc).
În OBS, ordinea surselor de sus în jos: overlay → cameră → captura jocului.
Camera: Edit Transform → Position 50, 390 · Bounding Box 520 x 580 · „Scale to outer bounds” · bifat „Crop to bounding box”.
"""
import json, os, subprocess, tempfile
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overlay')
os.makedirs(HERE, exist_ok=True)

# rama camerei: exterior 540 x 600 la (40, 380), bordură 10 → interior (camera) 520 x 580 la (50, 390)
FX, FY, FW, FH, BORDER, R = 40, 380, 540, 600, 10, 36
CW, CH, CR = FW - 2 * BORDER, FH - 2 * BORDER, R - BORDER

CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--blue:#DDE9F7;--mint:#D8F0E4;--lilac:#E9E1F7}
*{box-sizing:border-box}html,body{margin:0;background:transparent}
.s{width:1920px;height:1080px;position:relative;overflow:hidden;color:var(--ink);font-family:Figtree,sans-serif}
.b{position:absolute;border-radius:50%}
.pill{position:absolute;display:flex;align-items:center;gap:14px;border-radius:999px;white-space:nowrap;box-shadow:0 8px 24px rgba(0,0,0,.28)}
.name{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.02em}
"""
HEAD = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800'
        '&family=Figtree:wght@600;700;800&display=swap" rel="stylesheet"><style>' + CSS + '</style></head><body>')

OVERLAY = (
    '<div class="s">'
    # bule de culoare din brand, care ies din spatele ramei; masca le taie ca să nu acopere camera
    '<svg width="1920" height="1080" style="position:absolute;left:0;top:0"><defs><mask id="m">'
    '<rect width="1920" height="1080" fill="#fff"/><rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="#000"/></mask></defs>' % (FX, FY, FW, FH, R) +
    '<g mask="url(#m)"><circle cx="%d" cy="%d" r="85" fill="#E9E1F7"/><circle cx="%d" cy="%d" r="60" fill="#D8F0E4"/></g></svg>' % (FX + FW - 25, FY + 25, FX + 30, FY + FH - 20) +
    # rama: doar bordura și umbra, interiorul rămâne transparent pentru cameră
    '<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;border-radius:%dpx;border:%dpx solid var(--bg);'
    'box-shadow:0 0 0 4px var(--pink),0 18px 50px rgba(0,0,0,.35)"></div>' % (FX, FY, FW, FH, R, BORDER) +
    # sus, peste marginea ramei
    '<div class="pill" style="left:%dpx;top:%dpx;background:var(--ink);padding:10px 30px 10px 10px">' % (FX + 26, FY - 32) +
    '<span style="background:var(--pink);color:var(--berry);font-weight:800;font-size:20px;letter-spacing:.08em;border-radius:999px;padding:8px 16px">GAMING</span>'
    '<span class="name" style="color:#fff;font-size:34px;line-height:1">Kristine Maia</span></div>'
    # jos, peste marginea ramei, centrat
    '<div style="position:absolute;left:%dpx;width:%dpx;top:%dpx;display:flex;justify-content:center">' % (FX, FW, FY + FH - 26) +
    '<div class="pill" style="position:static;background:var(--bg);border:3px solid var(--pink);padding:9px 24px 9px 14px;font-weight:700;font-size:22px">'
    '<span style="width:16px;height:16px;border-radius:50%;background:var(--berry);flex:none"></span>'
    'Stretch break every 30 min <span style="color:var(--muted);font-weight:600">· type</span>'
    '<span style="background:var(--ink);color:#fff;border-radius:10px;padding:2px 10px;font-weight:800;margin-left:-6px">!stretch</span></div></div>'
    '</div>')

MASK = ('<div style="width:%dpx;height:%dpx;border-radius:%dpx;background:#fff"></div>' % (CW, CH, CR))

jobs = [{'html': HEAD + OVERLAY + '</body></html>', 'file': os.path.join(HERE, 'gaming-overlay-1920x1080.png'), 'w': 1920, 'h': 1080},
        {'html': HEAD + MASK + '</body></html>', 'file': os.path.join(HERE, 'gaming-cam-mask-%dx%d.png' % (CW, CH)), 'w': CW, 'h': CH}]
js = r"""
const { chromium } = require('playwright'); const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => { const b = await chromium.launch(); for (const j of jobs) { const p = await b.newPage({ viewport: { width: j.w, height: j.h } });
  await p.setContent(j.html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
  await p.screenshot({ path: j.file, type: 'png', omitBackground: true, clip: { x: 0, y: 0, width: j.w, height: j.h } }); await p.close(); }
  await b.close(); })();
"""
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
    json.dump(jobs, jf); jf.flush(); sf.write(js); sf.flush()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', sf.name, jf.name], check=True, env=env)
os.unlink(jf.name); os.unlink(sf.name)
for j in jobs: print(os.path.basename(j['file']), os.path.getsize(j['file']) // 1024, 'KB')
print('Camera în OBS: Position %d, %d · Bounding Box %d x %d' % (FX + BORDER, FY + BORDER, CW, CH))
