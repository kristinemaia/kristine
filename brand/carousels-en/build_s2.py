#!/usr/bin/env python3
"""Carusel EN S2 „5 rules I live by as a gamer girl who lifts” (același stil ca S1, 18 nov):
prima poză singură, fără text; apoi text pe pozele de la sală, estompate și întunecate; slide-ul 6 e video (mersul pe bandă înclinată).
Fiecare regulă e o parte din Custom Program, iar ultimul slide trimite la quiz („opening soon”, fără vânzare).
Pozele (fiecare doar în S2, fără repetări în alte postări): src/gym-black-*.jpg, src/mirror-black-*.jpg, src/food-lunch-potatoes-meatballs.jpg, src/desk-headset-side.jpg
Video:  studio/custom-program/clips/carusel/treadmill-incline.mov (nu e în git; dacă lipsește, slide-ul 6 iese ca poză)
Rulezi: python3 brand/carousels-en/build_s2.py -> out/EN-S2-5-rules-*.png (+ EN-S2-5-rules-6.mp4) și EN-S2-5-rules.zip"""
import base64, html, io, json, os, subprocess, tempfile, zipfile
from PIL import Image, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SRC, OUT = os.path.join(HERE, 'src'), os.path.join(HERE, 'out')
VIDEO = os.path.join(ROOT, 'studio', 'custom-program', 'clips', 'carusel', 'treadmill-incline.mov')
NAME = 'EN-S2-5-rules'
E = html.escape
T = 8

def crop(name, focus=0.4):
    im = Image.open(os.path.join(SRC, name)).convert('RGB'); r = max(1080 / im.width, 1350 / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - 1080) // 2; y = int((im.height - 1350) * focus)
    return im.crop((x, y, x + 1080, y + 1350))

def data(im, q=88):
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

def blurred(name, focus=0.4):
    return data(ImageEnhance.Color(crop(name, focus).filter(ImageFilter.GaussianBlur(14))).enhance(0.85))

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent}
.s{position:relative;overflow:hidden;width:1080px;height:1350px;background:#141311;color:#F3EEE6;font-family:Poppins,sans-serif}
.s.clear{background:transparent}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.shade{position:absolute;inset:0;background:rgba(10,9,8,.6)}
.label{position:absolute;left:90px;top:96px;font-size:26px;font-weight:500;letter-spacing:7px;text-transform:uppercase;color:#D9CDBB}
.num{position:absolute;right:90px;top:96px;font-size:26px;font-weight:400;letter-spacing:4px;color:#B8AE9F}
.center{position:absolute;left:90px;right:90px;text-align:center}
.foot{position:absolute;left:90px;right:90px;bottom:48px;font-size:21px;color:#9C9387;letter-spacing:.5px}
.big{font-size:150px;font-weight:500;line-height:1;color:#E9D9C2;letter-spacing:-3px}
"""
FOOT = 'General exercise and education, not medical advice.'

def frame(inner, cls=''): return '<div class="s %s" id="s">%s</div>' % (cls, inner)
def bg(name, focus=0.4): return '<img class="bg" src="%s"><div class="shade"></div>' % blurred(name, focus)

def rule(n, k, title, body, extra=''):
    return ('<div class="label">Rule %d of 5</div><div class="num">%d / %d</div>'
            '<div style="position:absolute;left:90px;right:90px;top:300px"><div class="big">0%d</div>'
            '<div style="font-size:84px;font-weight:500;line-height:1.07;letter-spacing:-1.2px;margin-top:40px">%s</div>'
            '<div style="font-size:36px;font-weight:400;line-height:1.45;margin-top:34px;color:#E6DCCD">%s</div>%s</div>'
            '<div class="foot">%s</div>' % (k, n, T, k, E(title), E(body), extra, FOOT))

def slides():
    s = []
    s.append(('img', frame('<img class="bg" src="%s">' % data(crop('gym-black-smile.jpg', 0.25), 92))))
    s.append(('img', frame(bg('mirror-black-2.jpg') + '<div class="num">2 / %d</div>'
        '<div class="center" style="top:420px"><div style="font-size:28px;font-weight:500;letter-spacing:8px;color:#D9CDBB">I SIT 9 HOURS A DAY</div>'
        '<div style="font-size:88px;font-weight:500;line-height:1.07;margin-top:34px;letter-spacing:-1.2px">5 rules that keep me strong anyway</div>'
        '<div style="font-size:28px;font-weight:400;letter-spacing:6px;margin-top:46px;color:#D9CDBB">GAMER · STREAMER · GYM GIRL</div></div>' % T)))
    s.append(('img', frame(bg('gym-black-side.jpg') + rule(3, 1, '3 workouts a week, not 6',
        'Three sessions I actually do beat six I skip. Consistency first, intensity later.'))))
    s.append(('img', frame(bg('gym-black-look.jpg', 0.3) + rule(4, 2, '5-minute warm-up, every time',
        'Jump rope or marching, then hips and upper back. My body has been in a chair all day; it needs a minute.'))))
    s.append(('img', frame(bg('mirror-black-1.jpg') + rule(5, 3, 'I write down every set',
        'Kilos and reps, every time. Next week I try one more rep or a little more weight. That’s how you get stronger.'))))
    s.append(('video', frame(rule(6, 4, 'I walk after I lift',
        '10 minutes on an incline. Easy on the joints, good for the heart, and it clears my head before stream.'), 'clear')))
    s.append(('img', frame(bg('food-lunch-potatoes-meatballs.jpg', 0.5) + rule(7, 5, 'Protein at every meal',
        'I cook once for 4 days: potatoes, veggies and meatballs. No midnight snack raids on stream.'))))
    s.append(('img', frame(bg('desk-headset-side.jpg') + '<div class="num">8 / %d</div>'
        '<div class="center" style="top:430px"><div style="font-size:84px;font-weight:500;line-height:1.08;letter-spacing:-1px">Want these rules turned into your plan?</div>'
        '<div style="font-size:36px;font-weight:400;margin-top:40px;color:#E6DCCD;line-height:1.45">Gym or home, 2 to 4 days, 10 to 40 minutes.<br>A 2-minute quiz builds it.</div>'
        '<div style="font-size:30px;font-weight:500;letter-spacing:6px;margin-top:70px;color:#D9CDBB">CUSTOM PROGRAM · OPENING SOON</div>'
        '<div style="font-size:26px;font-weight:400;letter-spacing:5px;margin-top:22px;color:#B8AE9F">JOIN THE WAITLIST · LINK IN BIO</div>'
        '<div style="font-size:30px;font-weight:400;margin-top:90px;color:#E6DCCD">Save this for your next desk day 🔖</div></div>' % T)))
    return s

JS = r"""
const { chromium } = require('playwright');
(async () => { const items = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8')); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
 for (const [file, html, clear] of items) { await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150); await (await p.$('#s')).screenshot({ path: file, omitBackground: clear }); }
 await b.close(); })();
"""

def video_slide(overlay, out):
    # banda: crop 4:5 din clipul vertical, puțin încetinit, întunecat ca celelalte, textul deasupra
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', VIDEO, '-loop', '1', '-i', overlay, '-filter_complex',
        '[0:v]scale=1080:-2,crop=1080:1350:0:(ih-1350)*0.45,setpts=PTS/0.85,fps=30,eq=saturation=0.85,'
        'drawbox=c=black@0.55:t=fill[v];[v][1:v]overlay=0:0:shortest=1,format=yuv420p[o]',
        '-map', '[o]', '-an', '-t', '7.8', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-movflags', '+faststart', out], check=True)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith(NAME + '-'): os.unlink(os.path.join(OUT, f))
    head = '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500&display=swap" rel="stylesheet"><style>%s</style></head><body>' % CSS
    tmp = tempfile.mkdtemp(); jobs, final = [], []
    for n, (kind, inner) in enumerate(slides(), 1):
        png = os.path.join(OUT, '%s-%d.png' % (NAME, n))
        if kind == 'video':
            ov = os.path.join(tmp, 'ov.png'); jobs.append((ov, head + inner + '</body></html>', True))
            final.append(('video', png, ov, n))
        else:
            jobs.append((png, head + inner + '</body></html>', False)); final.append(('img', png, None, n))
    jf = os.path.join(tmp, 'j.json'); json.dump(jobs, open(jf, 'w'))
    jsf = os.path.join(tmp, 'r.js'); open(jsf, 'w').write(JS)
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf, jf], check=True, env=env)
    files = []
    for kind, png, ov, n in final:
        if kind == 'video':
            if os.path.exists(VIDEO):
                mp4 = os.path.join(OUT, '%s-%d.mp4' % (NAME, n)); video_slide(ov, mp4); files.append(mp4)
                # și o poză din video, ca rezervă / copertă în aplicație
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '2', '-i', mp4, '-frames:v', '1', png], check=True); files.append(png)
            else:
                im = Image.new('RGB', (1080, 1350), (20, 19, 17)); im.paste(Image.open(ov), (0, 0), Image.open(ov)); im.save(png); files.append(png)
        else:
            files.append(png)
    z = os.path.join(HERE, NAME + '.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files: zf.write(f, os.path.basename(f))
    print('gata:', len(files), 'fișiere')
