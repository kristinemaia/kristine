#!/usr/bin/env python3
"""Reel-uri de promovare pentru Custom Program: înregistrarea site-ului într-un cadru de telefon + text mare sus.

Rulezi:   python3 studio/custom-program/build_promo.py
Intrare:  studio/custom-program/clips/demo/{quiz,start,weights}.webm
          (le face record_demo.js:  NODE_PATH=$(npm root -g) node studio/custom-program/record_demo.js website <folder>)
Ieșire:   studio/custom-program/out/promo/P1..P4-*.mp4 (1080x1920, fără muzică: pui sunetul în Instagram)
"""
import os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FONTS = os.path.join(ROOT, 'brand', 'reels-overlays', 'fonts')
DEMO = os.path.join(HERE, 'clips', 'demo')
OUT = os.path.join(HERE, 'out', 'promo')
W, H = 1080, 1920
BG, INK, PLUM, PINK = (237, 226, 234), (43, 36, 49), (162, 61, 102), (229, 155, 185)
PH, PW = 1330, 614            # ecranul telefonului (780x1688 micșorat)
PX, PY = (W - PW) // 2, 400   # sub text, deasupra zonei cu descrierea din Instagram
R = 56                        # colțuri rotunjite
START_B = 1.66                # weights.webm: partea bună începe aici

def font(w, s): return ImageFont.truetype(os.path.join(FONTS, f'Poppins-{w}.ttf'), s)

def background(path):
    im = Image.new('RGB', (W, H), BG)
    sh = Image.new('L', (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle((PX - 14, PY + 10, PX + PW + 14, PY + PH + 34), R + 14, fill=120)
    im.paste((120, 90, 110), (0, 0), sh.filter(ImageFilter.GaussianBlur(30)))
    ImageDraw.Draw(im).rounded_rectangle((PX - 14, PY - 14, PX + PW + 14, PY + PH + 14), R + 14, fill=INK)
    im.save(path)

def mask(path):
    m = Image.new('L', (PW, PH), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, PW - 1, PH - 1), R, fill=255)
    m.save(path)

def wrap(d, text, f, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

def caption(path, big, small=None):
    # textul de sus: rândul mare (ink) + un rând mic (plum) deasupra
    im = Image.new('RGBA', (W, PY - 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fb, fs = font('Bold', 68), font('SemiBold', 36)
    lines = wrap(d, big, fb, W - 100)
    hb = len(lines) * 82; y = (im.height - hb - (56 if small else 0)) // 2 + 10
    if small:
        tw = d.textlength(small, font=fs)
        d.rounded_rectangle(((W - tw) / 2 - 22, y - 6, (W + tw) / 2 + 22, y + 50), 28, fill=PLUM)
        d.text((W / 2, y + 22), small, font=fs, fill='white', anchor='mm'); y += 72
    for l in lines:
        d.text((W / 2, y + 38), l, font=fb, fill=INK, anchor='mm'); y += 82
    im.save(path)

# fiecare reel: bucăți (fișier, de la, până la, viteză) + texte (de la, până la, rând mic, rând mare)
REELS = {
    'P1-am-facut-o-aplicatie': {
        'parts': [('quiz', 2.0, 14.6, 1.3), ('start', 0.5, 11.76, 1.25), ('weights', START_B, 9.2, 1.0)],
        'texts': [(0, 2.6, 'I built this', 'A training app for people who sit all day'),
                  (2.6, 5.8, 'Step 1', 'Take the 2-minute quiz'),
                  (5.8, 13.9, 'Step 2', 'Get your plan for the week'),
                  (13.9, 18.7, 'Step 3', 'Press Start, follow the timer'),
                  (18.7, 99, 'Step 4', 'It remembers what you lifted')],
    },
    'P2-quiz-2-minute': {
        'parts': [('quiz', 1.0, 14.6, 1.0)],
        'texts': [(0, 5, 'Stop guessing', 'Answer a few questions'), (5, 99, '2 minutes', 'Get a plan made for your body')],
    },
    'P3-pov-cronometru': {
        'parts': [('start', 0.5, 11.76, 1.0)],
        'texts': [(0, 99, 'POV', 'Your workout tells you exactly what’s next')],
    },
    'P4-greutati': {
        'parts': [('weights', START_B, 9.2, 1.0)],
        'texts': [(0, 3.5, 'Progressive overload', 'Write down every set'), (3.5, 99, 'Rest timer', 'Next time it shows what you lifted')],
    },
}

def build(name, spec, tmp):
    bgp, mp = os.path.join(tmp, 'bg.png'), os.path.join(tmp, 'mask.png')
    if not os.path.exists(bgp): background(bgp); mask(mp)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', bgp, '-loop', '1', '-i', mp]
    fc, labels = [], []
    for k, (f, a, b, sp) in enumerate(spec['parts']):
        cmd += ['-ss', str(a), '-to', str(b), '-i', os.path.join(DEMO, f + '.webm')]
        fc.append(f'[{k + 2}:v]setpts=(PTS-STARTPTS)/{sp},fps=30,scale={PW}:{PH}:flags=lanczos,format=yuv420p[p{k}]')
        labels.append(f'[p{k}]')
    n = len(spec['parts'])
    hold = '1.5'
    fc.append(''.join(labels) + f'concat=n={n}:v=1:a=0,tpad=stop_mode=clone:stop_duration={hold},format=rgba[sc]')
    fc.append('[1:v]format=gray[m];[sc][m]alphamerge[ph]')
    fc.append(f'[0:v][ph]overlay={PX}:{PY}:shortest=1[v0]')
    base = n + 2; last = 'v0'
    for j, (t0, t1, small, big) in enumerate(spec['texts']):
        p = os.path.join(tmp, f'{name}-t{j}.png'); caption(p, big, small)
        cmd += ['-loop', '1', '-i', p]
        fc.append(f"[{last}][{base + j}:v]overlay=0:0:shortest=1:enable='between(t,{t0},{t1})'[v{j + 1}]")
        last = f'v{j + 1}'
    out = os.path.join(OUT, name + '.mp4')
    total = sum((b - a) / sp for _, a, b, sp in spec['parts']) + float(hold)
    cmd += ['-filter_complex', ';'.join(fc), '-map', f'[{last}]', '-t', f'{total:.2f}', '-c:v', 'libx264', '-preset', 'medium',
            '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True)
    return out

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, spec in REELS.items():
            o = build(name, spec, tmp)
            d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', o],
                               capture_output=True, text=True).stdout.strip()
            print(f'{os.path.basename(o)}  {float(d):.1f} s')
