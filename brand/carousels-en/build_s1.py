#!/usr/bin/env python3
"""Carusel EN S1 „Save this: full-body gym workout” (formatul „Save this workout”, modelul Senada Greca), stilul estetic (16 nov):
prima poză singură, fără text; apoi slide-uri închise la culoare, cu Poppins, ca la reel-urile estetice; la final, a doua poză cu îndemnul.
Pozele: src/s1-cover.jpg și s1-end.jpg (selfie-urile la oglindă din 16 nov, fără alți oameni în cadru), s1-blur.jpg (coperta estompată)
și cadrele din filmările programului (wk-*.jpg, gym-lunge.jpg), afișate la rezoluția lor.
Rulezi: python3 brand/carousels-en/build_s1.py -> out/EN-S1-save-this-workout-*.png"""
import base64, html, json, os, subprocess, tempfile, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, 'src'), os.path.join(HERE, 'out')
E = html.escape

def img(name):
    return 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(SRC, name), 'rb').read()).decode()

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#000}
.s{position:relative;overflow:hidden;width:1080px;height:1350px;background:#141311;color:#F3EEE6;font-family:Poppins,sans-serif}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.label{position:absolute;left:90px;top:96px;font-size:26px;font-weight:500;letter-spacing:7px;text-transform:uppercase;color:#B8AE9F}
.num{position:absolute;right:90px;top:96px;font-size:26px;font-weight:400;letter-spacing:4px;color:#7E766B}
.ph{position:absolute;overflow:hidden;border-radius:18px}
.ph img{width:100%;height:100%;object-fit:cover;display:block}
.rows{position:absolute;left:90px;right:90px}
.row{display:flex;justify-content:space-between;align-items:baseline;padding:24px 0;border-top:1px solid rgba(243,238,230,.16);font-size:38px;font-weight:400}
.row:last-child{border-bottom:1px solid rgba(243,238,230,.16)}
.row b{font-weight:500;color:#E9D9C2;letter-spacing:1px}
.foot{position:absolute;left:90px;right:90px;bottom:48px;font-size:21px;color:#7E766B;letter-spacing:.5px}
.center{position:absolute;left:90px;right:90px;text-align:center}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,9,8,.25) 0%,rgba(10,9,8,.15) 40%,rgba(10,9,8,.82) 72%,rgba(10,9,8,.92) 100%)}
"""
FOOT = 'General exercise, not medical advice. Rest 60–90 s between sets.'
T = 7

def frame(n, inner, cls=''):
    return '<div class="s %s" id="s">%s</div>' % (cls, inner)

def rows(items, top):
    return '<div class="rows" style="top:%dpx">%s</div>' % (top, ''.join('<div class="row"><span>%s</span><b>%s</b></div>' % (E(a), E(b)) for a, b in items))

def part(n, label, items, photos):
    if len(photos) == 1:
        name, pos = photos[0]
        pics = '<div class="ph" style="left:290px;top:180px;width:500px;height:660px"><img src="%s" style="object-position:%s"></div>' % (img(name), pos)
    else:
        pics = ''.join('<div class="ph" style="left:%dpx;top:180px;width:440px;height:660px"><img src="%s" style="object-position:%s"></div>' % (x, img(nm), pos)
                       for x, (nm, pos) in zip((90, 550), photos))
    top = 890
    return frame(n, '<div class="label">%s</div><div class="num">%d / %d</div>%s%s<div class="foot">%s</div>' % (E(label), n, T, pics, rows(items, top), FOOT))

def slides():
    s = []
    # 1: poza singură
    s.append(frame(1, '<img class="bg" src="%s">' % img('s1-cover.jpg')))
    # 2: titlul, pe poza estompată
    s.append(frame(2, '<img class="bg" src="%s"><div class="shade" style="background:rgba(10,9,8,.62)"></div>'
        '<div class="num">2 / %d</div>'
        '<div class="center" style="top:430px"><div style="font-size:28px;font-weight:500;letter-spacing:8px;color:#D9CDBB">SIT ALL DAY?</div>'
        '<div style="font-size:84px;font-weight:500;line-height:1.08;margin-top:34px;letter-spacing:-1px">Save this full-body gym workout</div>'
        '<div style="font-size:28px;font-weight:400;letter-spacing:6px;margin-top:46px;color:#D9CDBB">45 MIN · 4 PARTS · BEGINNER FRIENDLY</div></div>' % (img('s1-blur.jpg'), T)))
    s.append(part(3, '01 · Warm-up · 5 min', [('March or jumping jacks', '1 min'), ("World's greatest stretch", '5 / side'), ('Cat-cow', '8 slow')],
                  [('wk-mobilitate-worlds-greatest-stretch.jpg', 'center 80%')]))
    s.append(part(4, '02 · Legs', [('Goblet squat', '3 × 10'), ('Dumbbell lunge', '3 × 8 / side')],
                  [('wk-picioare-goblet-a.jpg', 'center 40%'), ('gym-lunge.jpg', 'center 40%')]))
    s.append(part(5, '03 · Back & posture', [('Lat pulldown', '3 × 10'), ('Seated cable row', '3 × 12'), ('Face pull', '2 × 15')],
                  [('wk-spate-lat-pulldown.jpg', 'center 45%')]))
    s.append(part(6, '04 · Core', [('Side plank', '3 × 20 s / side'), ('Dead bug', '3 × 8 / side')],
                  [('wk-core-plank-lateral.jpg', 'center 85%')]))
    # 7: a doua poză, cu îndemnul jos
    s.append(frame(7, '<img class="bg" src="%s"><div class="shade"></div><div class="num">7 / %d</div>'
        '<div class="center" style="top:1000px"><div style="font-size:62px;font-weight:500;line-height:1.1;letter-spacing:-.5px">Want one built for you?</div>'
        '<div style="font-size:30px;font-weight:400;margin-top:26px;color:#E6DCCD;line-height:1.4">Your goal, your time, home or gym.<br>Custom Program · opening soon</div>'
        '<div style="font-size:24px;font-weight:500;letter-spacing:6px;margin-top:34px;color:#D9CDBB">JOIN THE WAITLIST · LINK IN BIO</div></div>' % (img('s1-end.jpg'), T)))
    return s

JS = r"""
const { chromium } = require('playwright');
(async () => { const items = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8')); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
 for (const [file, html] of items) { await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150); await (await p.$('#s')).screenshot({ path: file }); }
 await b.close(); })();
"""

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith('EN-S1-save-this-workout-'): os.unlink(os.path.join(OUT, f))
    head = '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500&display=swap" rel="stylesheet"><style>%s</style></head><body>' % CSS
    jobs = [(os.path.join(OUT, 'EN-S1-save-this-workout-%d.png' % n), head + inner + '</body></html>') for n, inner in enumerate(slides(), 1)]
    jf = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(jobs, jf); jf.close()
    jsf = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False); jsf.write(JS); jsf.close()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf.name, jf.name], check=True, env=env); os.unlink(jsf.name); os.unlink(jf.name)
    z = os.path.join(HERE, 'EN-S1-save-this-workout.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f, _ in jobs: zf.write(f, os.path.basename(f))
    print('gata:', len(jobs), 'imagini')
