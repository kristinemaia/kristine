#!/usr/bin/env python3
"""Carusel EN S1 „Save this: full-body gym workout” (formatul „Save this workout”, modelul Senada Greca), stilul estetic (16 nov):
prima poză singură, fără text; apoi slide-uri cu text, Poppins, ca la reel-urile estetice.
Varianta 2 (16 nov, cerută de Kristine): doar prima poză; restul slide-urilor sunt text, fiecare pe altă poză de la oglindă, estompată și întunecată (src/s1-bg-2…7.jpg).
Pozele: src/s1-cover.jpg (selfie-ul la oglindă cu „flex”, ales pe 16 nov, fără alți oameni în cadru).
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

def bg(n):
    return '<img class="bg" src="%s"><div class="shade" style="background:rgba(10,9,8,.6)"></div>' % img('s1-bg-%d.jpg' % n)

def part(n, label, title, why, items):
    return frame(n, bg(n) + '<div class="label">%s</div><div class="num">%d / %d</div>'
        '<div style="position:absolute;left:90px;right:90px;top:330px"><div style="font-size:96px;font-weight:500;line-height:1.05;letter-spacing:-1.5px">%s</div>'
        '<div style="font-size:36px;font-weight:400;line-height:1.4;margin-top:34px;color:#E6DCCD">%s</div></div>'
        '%s<div class="foot">%s</div>' % (E(label), n, T, E(title), E(why), rows(items, 1180 - 104 * len(items)), FOOT))

def slides():
    s = []
    # 1: poza singură, fără text
    s.append(frame(1, '<img class="bg" src="%s">' % img('s1-cover.jpg')))
    # 2: titlul
    s.append(frame(2, bg(2) + '<div class="num">2 / %d</div>'
        '<div class="center" style="top:430px"><div style="font-size:28px;font-weight:500;letter-spacing:8px;color:#D9CDBB">SIT ALL DAY?</div>'
        '<div style="font-size:84px;font-weight:500;line-height:1.08;margin-top:34px;letter-spacing:-1px">Save this full-body gym workout</div>'
        '<div style="font-size:28px;font-weight:400;letter-spacing:6px;margin-top:46px;color:#D9CDBB">45 MIN · 4 PARTS · BEGINNER FRIENDLY</div></div>' % T))
    s.append(part(3, '01 · Warm-up · 5 min', 'Wake up your hips and back',
                  'After hours in a chair, your body needs a few minutes before the first set.',
                  [('March or jumping jacks', '1 min'), ("World's greatest stretch", '5 / side'), ('Cat-cow', '8 slow')]))
    s.append(part(4, '02 · Legs', 'Turn your glutes back on',
                  'Sitting all day makes them lazy. These two moves wake them up.',
                  [('Goblet squat', '3 × 10'), ('Dumbbell lunge', '3 × 8 / side')]))
    s.append(part(5, '03 · Back & posture', 'Undo the desk hunch',
                  'Pull more than you push: your upper back holds your shoulders where they belong.',
                  [('Lat pulldown', '3 × 10'), ('Seated cable row', '3 × 12'), ('Face pull', '2 × 15')]))
    s.append(part(6, '04 · Core', 'A back that lasts all day',
                  'A strong core keeps you upright through the next long session.',
                  [('Side plank', '3 × 20 s / side'), ('Dead bug', '3 × 8 / side')]))
    # 7: îndemnul
    s.append(frame(7, bg(7) + '<div class="num">7 / %d</div>'
        '<div class="center" style="top:440px"><div style="font-size:84px;font-weight:500;line-height:1.08;letter-spacing:-1px">Want one built for you?</div>'
        '<div style="font-size:36px;font-weight:400;margin-top:40px;color:#E6DCCD;line-height:1.45">Your goal, your time, home or gym.<br>A 2-minute quiz builds your plan.</div>'
        '<div style="font-size:30px;font-weight:500;letter-spacing:6px;margin-top:70px;color:#D9CDBB">LEVEL UP · NOW OPEN</div>'
        '<div style="font-size:26px;font-weight:400;letter-spacing:5px;margin-top:22px;color:#B8AE9F">$10/MONTH FOR THE FIRST 50 · LINK IN BIO</div>'
        '<div style="font-size:30px;font-weight:400;margin-top:90px;color:#E6DCCD">Save it for your next gym day 🔖</div></div>' % T))
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
