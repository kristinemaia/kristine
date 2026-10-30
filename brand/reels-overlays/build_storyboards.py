#!/usr/bin/env python3
"""Storyboard și video de referință (animatic) pentru reel-urile de sală G1–G3.

Rulezi:   python3 brand/reels-overlays/build_storyboards.py   (după build_overlays.py)
Rezultat: storyboard/<COD>/<COD>-storyboard.png (toate cadrele pe o pagină)
          storyboard/<COD>/<COD>-referinta.mp4 (ritmul reel-ului, cu textul exact de pe ecran)

Omulețul arată poziția și unghiul, nu cum arăți tu. Caseta punctată de jos e nota de filmare:
nu apare în reel. Textele (hook, etichete, final) sunt PNG-urile reale din out/<COD>/.
"""
import base64, json, os, shutil, subprocess, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'storyboard')
OV = os.path.join(HERE, 'out')
INK, CREAM, WINE, PINK, YEL = '#2B2431', '#FFF9F6', '#8A3459', '#E59BB9', '#E8C547'

# ---------- omulețul: puncte într-o cutie 400 x 520 (podeaua la y=500) ----------
P = {
 'stand':   dict(head=(200, 60), neck=(200, 100), hip=(200, 265), k1=(188, 385), f1=(182, 500), k2=(212, 385), f2=(218, 500),
                 e1=(168, 175), h1=(160, 255), e2=(232, 175), h2=(240, 255)),
 'wave':    dict(head=(200, 60), neck=(200, 100), hip=(200, 265), k1=(188, 385), f1=(182, 500), k2=(212, 385), f2=(218, 500),
                 e1=(168, 175), h1=(160, 255), e2=(268, 120), h2=(290, 40)),
 'angel':   dict(head=(200, 60), neck=(200, 100), hip=(200, 265), k1=(188, 385), f1=(182, 500), k2=(212, 385), f2=(218, 500),
                 e1=(120, 110), h1=(112, 30), e2=(280, 110), h2=(288, 30)),
 'squat':   dict(head=(232, 248), neck=(214, 285), hip=(150, 425), k1=(255, 405), f1=(185, 500), k2=(262, 412), f2=(195, 500),
                 e1=(268, 335), h1=(320, 330), e2=(272, 340), h2=(324, 338)),
 'sitx':    dict(head=(200, 250), neck=(200, 290), hip=(200, 445), k1=(120, 470), f1=(235, 495), k2=(280, 470), f2=(165, 495),
                 e1=(150, 370), h1=(128, 455), e2=(250, 370), h2=(272, 455)),
 'stuck':   dict(head=(318, 236), neck=(285, 232), hip=(190, 270), k1=(198, 385), f1=(196, 500), k2=(206, 385), f2=(206, 500),
                 e1=(300, 290), h1=(282, 345), e2=(306, 292), h2=(290, 350)),
 'fold':    dict(head=(262, 372), neck=(250, 335), hip=(180, 262), k1=(196, 385), f1=(196, 500), k2=(204, 385), f2=(206, 500),
                 e1=(262, 400), h1=(256, 470), e2=(268, 402), h2=(264, 474)),
 'knee':    dict(head=(200, 70), neck=(196, 110), hip=(190, 290), k1=(300, 385), f1=(300, 500), k2=(150, 490), f2=(60, 498),
                 e1=(165, 200), h1=(200, 285), e2=(225, 200), h2=(214, 288)),
 'side':    dict(head=(70, 448), neck=(110, 462), hip=(250, 470), k1=(320, 430), f1=(300, 495), k2=(318, 440), f2=(298, 498),
                 e1=(110, 380), h1=(118, 300), e2=(190, 470), h2=(250, 478)),
 'cat':     dict(head=(330, 405), neck=(292, 372), hip=(140, 372), k1=(140, 500), f1=(60, 500), k2=(150, 500), f2=(70, 500),
                 e1=(300, 440), h1=(300, 500), e2=(310, 440), h2=(310, 500), arch=(215, 315)),
 'row':     dict(head=(192, 180), neck=(182, 218), hip=(170, 385), k1=(262, 330), f1=(325, 395), k2=(268, 336), f2=(330, 400),
                 e1=(118, 310), h1=(218, 318), e2=(124, 314), h2=(222, 322)),
 'rowlean': dict(head=(105, 205), neck=(128, 238), hip=(170, 385), k1=(262, 330), f1=(325, 395), k2=(268, 336), f2=(330, 400),
                 e1=(80, 330), h1=(196, 330), e2=(86, 334), h2=(200, 334)),
 'desk':    dict(head=(272, 172), neck=(232, 196), hip=(168, 335), k1=(262, 335), f1=(262, 470), k2=(268, 340), f2=(270, 475),
                 e1=(256, 262), h1=(332, 240), e2=(262, 266), h2=(338, 244)),
}

def fig(pose, glow=()):
    j = P[pose]; s = []
    L = lambda a, b, w=16, c=CREAM: s.append(f'<line x1="{j[a][0]}" y1="{j[a][1]}" x2="{j[b][0]}" y2="{j[b][1]}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>')
    if 'arch' in j:
        s.append(f'<path d="M{j["neck"][0]} {j["neck"][1]} Q{j["arch"][0]} {j["arch"][1]} {j["hip"][0]} {j["hip"][1]}" stroke="{CREAM}" stroke-width="18" fill="none" stroke-linecap="round"/>')
    else:
        L('neck', 'hip', 18)
    for a, b in (('hip', 'k1'), ('k1', 'f1'), ('hip', 'k2'), ('k2', 'f2'), ('neck', 'e1'), ('e1', 'h1'), ('neck', 'e2'), ('e2', 'h2')):
        L(a, b)
    s.append(f'<circle cx="{j["head"][0]}" cy="{j["head"][1]}" r="30" fill="{CREAM}"/>')
    for g in glow:
        x, y = j[g]; s.append(f'<circle cx="{x}" cy="{y}" r="34" fill="none" stroke="{PINK}" stroke-width="8"/>')
    return ''.join(s)

FLOOR = '<line x1="0" y1="505" x2="400" y2="505" stroke="#4a4550" stroke-width="6"/>'
WALL = '<rect x="70" y="0" width="260" height="505" rx="8" fill="#3a3540"/>'
MAT = '<rect x="20" y="500" width="360" height="14" rx="7" fill="#5f8f7b"/>'
BENCH = '<rect x="110" y="385" width="120" height="24" rx="8" fill="#55505c"/><line x1="170" y1="409" x2="170" y2="505" stroke="#55505c" stroke-width="12"/>'
CABLE = f'<rect x="372" y="120" width="26" height="385" fill="#55505c"/><line x1="222" y1="320" x2="372" y2="300" stroke="{YEL}" stroke-width="5"/>'
CHAIR = '<rect x="120" y="335" width="110" height="18" rx="6" fill="#55505c"/><line x1="175" y1="353" x2="175" y2="470" stroke="#55505c" stroke-width="10"/><line x1="128" y1="335" x2="112" y2="210" stroke="#55505c" stroke-width="10"/>'
DESK = '<rect x="300" y="240" width="100" height="14" fill="#55505c"/><line x1="380" y1="254" x2="380" y2="470" stroke="#55505c" stroke-width="10"/>'
def arrow(x1, y1, x2, y2, c=PINK):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="8" stroke-linecap="round" marker-end="url(#ah)"/>')
UP_ARROW = arrow(330, 470, 330, 120)
SHRUG = arrow(140, 230, 140, 150, '#E06C6C')
ELBOWS = arrow(150, 300, 70, 260, '#E06C6C') + arrow(150, 310, 70, 360, '#E06C6C')
def badge(ok):
    c = '#3BB37A' if ok else '#E06C6C'
    mark = '<path d="M-22 2 L-6 18 L24 -16" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' if ok else \
           '<path d="M-18 -18 L18 18 M18 -18 L-18 18" stroke="#fff" stroke-width="10" stroke-linecap="round"/>'
    return f'<g transform="translate(350 40)"><circle r="40" fill="{c}"/>{mark}</g>'
ROT = f'<path d="M150 250 A60 40 0 1 1 260 250" stroke="{PINK}" stroke-width="8" fill="none" marker-end="url(#ah)"/>'

# ---------- cele trei reel-uri ----------
# cadru: (început, sfârșit, poza, recuzită, overlay PNG sau None, unde pui eticheta, nota de filmare)
REELS = {
 'G1-Test': dict(title='Testul de stat jos', frames=[
  (0, 2, 'wave', FLOOR, '1-hook', None, 'Hook: te uiți în cameră și ridici 3 degete. Telefonul vertical, pe diagonală (45°), la înălțimea șoldului; tot corpul în cadru.'),
  (2, 7, 'angel', WALL + FLOOR, 'eticheta-1-test-1-wall-angel', 'label', 'Wall angel: spatele, capul și brațele lipite de perete; urci brațele încet. Dacă se dezlipesc, arăți asta la cameră, cu umor.'),
  (7, 12, 'squat', FLOOR, 'eticheta-2-test-2-deep-squat-10-s', 'label', 'Genuflexiune adâncă, călcâiele jos, 10 secunde. Te întorci puțin din profil, ca să se vadă călcâiele.'),
  (12, 14.5, 'sitx', MAT + FLOOR, 'eticheta-3-test-3-floor-to-standing-no-hands', 'label', 'Șezi turcește pe saltea…'),
  (14.5, 17, 'stand', MAT + FLOOR + UP_ARROW, 'eticheta-3-test-3-floor-to-standing-no-hands', 'label', '…și te ridici fără să pui mâinile jos. O singură încercare, fără grabă.'),
  (17, 20.5, 'wave', FLOOR, '2-final', None, 'Final: „How many?” cu degetele. Ultimul cadru seamănă cu primul, ca reel-ul să se reia fără să se simtă (loop).'),
 ]),
 'G2-POV': dict(title='POV: 9 ore pe scaun', frames=[
  (0, 2.5, 'stuck', FLOOR, '1-hook', None, 'Joc de actor: încerci să atingi vârfurile, te oprești la genunchi și te uiți la cameră, „blocată”.'),
  (2.5, 4.5, 'stand', FLOOR + ROT, 'eticheta-1-my-hips', 'label', 'Un cerc de șold lent, cu o față amuzantă. Sunet: un „scârțâit” din biblioteca de sunete Instagram.'),
  (4.5, 5.5, 'stand', FLOOR, 'eticheta-2-10-second-fixes', 'label', 'Tăietură rapidă: arăți spre saltea.'),
  (5.5, 9, 'knee', MAT + FLOOR, 'eticheta-3-hip-flexors', 'label', 'Fandare pe genunchi: strângi fesierul piciorului din spate și împingi ușor șoldul înainte.'),
  (9, 12.5, 'side', MAT + FLOOR, 'eticheta-4-upper-back', 'label', 'Open book: culcată pe o parte, deschizi brațul de sus și îl urmărești cu privirea.'),
  (12.5, 15.5, 'cat', MAT + FLOOR, 'eticheta-5-cat-cow', 'label', 'Cat-cow lent: spatele rotund, apoi arcuit.'),
  (15.5, 18, 'fold', FLOOR, 'eticheta-6-better', 'label', 'Din nou flexia: acum ajungi mai jos și zâmbești. Fără exagerări: arăți doar diferența reală.'),
  (18, 21, 'stand', FLOOR, '2-final', None, 'Final: textul „Save this for your next leg day”.'),
 ]),
 'G3-Form': dict(title='Form check la ramat', frames=[
  (0, 2.5, 'row', BENCH + CABLE + FLOOR, '1-hook', None, 'Hook: ești așezată la aparatul de ramat și te uiți în cameră. Telefonul din profil, la înălțimea pieptului.'),
  (2.5, 5, 'row', BENCH + CABLE + FLOOR + SHRUG + badge(False), 'eticheta-1-wrong-shoulders-up', 'label', 'Greșeala 1: tragi cu umerii ridicați spre urechi. Greutate mică: arăți greșeala, nu o faci la maxim.'),
  (5, 7.5, 'row', BENCH + CABLE + FLOOR + badge(True), 'eticheta-2-right-shoulders-down', 'label', 'Corect: umerii jos și înapoi, apoi tragi.'),
  (7.5, 10, 'rowlean', BENCH + CABLE + FLOOR + badge(False), 'eticheta-3-wrong-leaning-back', 'label', 'Greșeala 2 (cea din hook): te lași mult pe spate ca să tragi greutatea.'),
  (10, 12.5, 'row', BENCH + CABLE + FLOOR + badge(True), 'eticheta-4-right-sit-tall', 'label', 'Corect: trunchiul drept, mișcarea vine din brațe și omoplați.'),
  (12.5, 15, 'row', BENCH + CABLE + FLOOR + ELBOWS + badge(False), 'eticheta-5-wrong-elbows-out', 'label', 'Greșeala 3: coatele depărtate. Aici întoarce telefonul pe diagonală (45°), ca să se vadă coatele.'),
  (15, 17.5, 'row', BENCH + CABLE + FLOOR + badge(True), 'eticheta-6-right-elbows-close', 'label', 'Corect: coatele aproape de corp.'),
  (17.5, 21, 'row', BENCH + CABLE + FLOOR, '2-final', None, 'Final: te uiți în cameră. „Send me your row. I\'ll rate it.” Răspunzi la fiecare video primit (în comentarii sau DM).'),
 ]),
}

def b64(path):
    return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def ovpath(code, key):
    d = os.path.join(OV, code)
    for fn in os.listdir(d):
        if fn.startswith(f'{code}_{key}'):
            return os.path.join(d, fn)
    raise SystemExit('lipsește overlay-ul ' + code + ' ' + key)

def frame_html(code, title, f, i, n):
    t0, t1, pose, props, ov, kind, note = f
    glow = {'G3-Form': ('neck',)}.get(code, ()) if 'shoulders up' in (ov or '') else ()
    svg = (f'<svg viewBox="0 0 400 520" width="740" height="962" style="position:absolute;left:170px;top:370px">'
           f'<defs><marker id="ah" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" orient="auto">'
           f'<path d="M0 0 L10 5 L0 10z" fill="{PINK}"/></marker></defs>{props}{fig(pose, glow)}</svg>')
    over = ''
    if ov:
        src = b64(ovpath(code, ov))
        if kind == 'label':
            over = f'<img src="{src}" style="position:absolute;left:300px;top:1380px;transform:translateX(-50%);left:540px">'
        else:
            over = f'<img src="{src}" style="position:absolute;left:0;top:0;width:1080px;height:1920px">'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}body{{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:Figtree,Arial,sans-serif;
background:linear-gradient(180deg,#26232b 0%,#1b191f 62%,#141217 100%)}}
.stripe{{position:absolute;left:0;right:0;top:1300px;height:16px;background:repeating-linear-gradient(90deg,{YEL} 0 60px,#141217 60px 120px);opacity:.55}}
.chip{{position:absolute;left:40px;top:170px;background:#3a3540;color:#fff;font:700 34px Arial;padding:10px 22px;border-radius:999px}}
.code{{position:absolute;right:40px;top:170px;color:#9a93a3;font:600 30px Arial}}
.note{{position:absolute;left:40px;right:40px;top:1560px;border:4px dashed #8a8296;border-radius:24px;padding:22px 26px;color:#f2eef6;font:500 34px/1.3 Arial}}
.note b{{display:block;color:#c9b8ff;font-size:26px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}}
</style></head><body><div class="stripe"></div>{svg}
<div class="chip">{t0:g}–{t1:g} s · cadrul {i}/{n}</div><div class="code">{code} · {title}</div>
{over}<div class="note"><b>Notă de filmare (nu apare în reel)</b>{note}</div></body></html>'''

JS = r"""
const { chromium } = require('playwright');
const items = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const it of items) { await p.setContent(it.html, { waitUntil: 'load' }); await p.waitForTimeout(60); await p.screenshot({ path: it.file }); }
  await b.close(); })();
"""

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    items = []
    for code, r in REELS.items():
        d = os.path.join(OUT, code); os.makedirs(d)
        n = len(r['frames'])
        for i, f in enumerate(r['frames'], 1):
            items.append({'file': os.path.join(d, f'{code}-cadru-{i:02d}.png'), 'html': frame_html(code, r['title'], f, i, n)})
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
        json.dump(items, jf); jf.flush(); sf.write(JS); sf.flush()
        env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
        subprocess.run(['node', sf.name, jf.name], check=True, env=env)
    os.unlink(jf.name); os.unlink(sf.name)
    for code, r in REELS.items():
        d = os.path.join(OUT, code)
        frames = [os.path.join(d, f'{code}-cadru-{i:02d}.png') for i in range(1, len(r['frames']) + 1)]
        # foaia cu toate cadrele
        tw, th, cols = 270, 480, 4
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * tw + (cols + 1) * 16, rows * th + (rows + 1) * 16), '#FFF9F6')
        for k, fp in enumerate(frames):
            im = Image.open(fp).convert('RGB').resize((tw, th), Image.LANCZOS)
            sheet.paste(im, (16 + (k % cols) * (tw + 16), 16 + (k // cols) * (th + 16)))
        sheet.save(os.path.join(d, f'{code}-storyboard.png'))
        # video de referință: fiecare cadru cât durează în reel
        lst = os.path.join(d, '_list.txt')
        with open(lst, 'w') as fh:
            for fp, f in zip(frames, r['frames']):
                fh.write(f"file '{fp}'\nduration {f[1] - f[0]}\n")
            fh.write(f"file '{frames[-1]}'\n")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', 'fps=30,scale=720:1280,format=yuv420p',
                        '-c:v', 'libx264', '-crf', '24', '-movflags', '+faststart', os.path.join(d, f'{code}-referinta.mp4')], check=True)
        os.remove(lst)
    print('gata:', OUT)

if __name__ == '__main__':
    main()
