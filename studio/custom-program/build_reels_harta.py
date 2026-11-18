#!/usr/bin/env python3
"""Reel-uri de antrenament în stilul „hartă” (exemplul trimis de Kristine pe 18 nov): 4 exerciții la rând, câte ~3 s,
sus câte o siluetă pe exercițiu cu mușchiul lucrat în roșu și o săgeată sub cel de acum, jos seriile mari, roz.
Doar pentru reel-uri (antrenamentele clienților sunt pe site, în my-program.html).
Rulezi: python3 studio/custom-program/build_reels_harta.py -> studio/custom-program/out/reels-harta/RH*.mp4 + copertele .jpg"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import muscle_map as mm
from workouts import NAMES
W, H, SEG = 1080, 1920, 3.0
FONTS = os.path.join(ROOT, 'brand/reels-overlays/fonts')
OUT = os.path.join(HERE, 'out', 'reels-harta')
PINK, RED = (255, 77, 109, 255), (229, 45, 58, 255)

REELS = [
    {'id': 'RH1-glute-workout', 'hook': 'Glute workout for people who sit all day',
     'ex': [('picioare-hip-thrust', '4 × 10'), ('picioare-rdl', '3 × 10'), ('picioare-fandare-inapoi', '3 × 8 / side'), ('picioare-glute-bridge', '3 × 15')]},
    {'id': 'RH2-desk-hunch', 'hook': 'Fix your desk hunch at the gym',
     'ex': [('spate-face-pull', '3 × 15'), ('spate-fluturari-inverse', '3 × 12'), ('spate-ramat-gantera', '3 × 10 / side'), ('spate-lat-pulldown', '3 × 10')]},
    {'id': 'RH3-core-desk', 'hook': 'Core workout for a back that lasts all day',
     'ex': [('core-dead-bug', '3 × 8 / side'), ('core-bird-dog', '3 × 8 / side'), ('core-plank-lateral', '3 × 20 s / side'), ('core-hollow-hold', '3 × 20 s')]},
]

def font(n, s): return ImageFont.truetype(os.path.join(FONTS, n), s)

def clip(cid):
    for p in (os.path.join(HERE, 'out', cid + '.mp4'), os.path.join(HERE, 'clips/preview', cid + '.mp4'), os.path.join(HERE, 'clips/istoric', cid + '.mp4')):
        if os.path.exists(p): return p
    raise SystemExit('lipsește clipul: ' + cid)

def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)

def overlay(ids, idx, name, sets, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    for i in range(420): g.line([(0, i), (W, i)], fill=(0, 0, 0, int(110 * (1 - i / 420) ** 1.5)))          # sus, ca să se vadă siluetele
    for y in range(H - 700, H):                                                                            # jos: acoperă etichetele vechi din clipuri
        a = 252 if y >= H - 560 else int(252 * ((y - (H - 700)) / 140) ** 1.6)
        g.line([(0, y), (W, y)], fill=(14, 12, 13, a))
    n = len(ids); cw = 180; x0 = (W - cw * n) // 2; top = 150
    for k, cid in enumerate(ids):
        c = mm.render_card(cid, cw - 16)
        if k != idx: c.putalpha(c.split()[3].point(lambda a: int(a * 0.5)))
        im.alpha_composite(c, (x0 + k * cw + 8, top))
    ax = x0 + idx * cw + cw // 2; ay = top + (cw - 16) * 2 + 10
    g = ImageDraw.Draw(im); g.polygon([(ax, ay), (ax - 28, ay + 40), (ax + 28, ay + 40)], fill=RED); g.rectangle((ax - 11, ay + 38, ax + 11, ay + 96), fill=RED)
    d = ImageDraw.Draw(im); fn, fd = font('Poppins-SemiBold.ttf', 56), font('Poppins-Bold.ttf', 128)
    y = H - 560
    d.text(((W - d.textlength(name, font=fn)) / 2, y), name, font=fn, fill=(255, 255, 255, 255))
    d.text(((W - d.textlength(sets, font=fd)) / 2, y + 74), sets, font=fd, fill=PINK, stroke_width=7, stroke_fill=(255, 255, 255, 255))
    im.save(path)

def cover(reel, frame, path):
    im = Image.open(frame).convert('RGB').resize((W, H)); im = im.filter(ImageFilter.GaussianBlur(2)).convert('RGBA')
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(sh)
    for y in range(H): g.line([(0, y), (W, y)], fill=(0, 0, 0, int(150 * max(0, (y - 500) / 1400))))
    for y in range(H - 700, H): g.line([(0, y), (W, y)], fill=(14, 12, 13, 252 if y >= H - 560 else int(252 * ((y - (H - 700)) / 140) ** 1.6)))
    im.alpha_composite(sh); d = ImageDraw.Draw(im); f = font('Poppins-Bold.ttf', 104)
    words, lines, cur = reel['hook'].split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) > W - 140 and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur); y = H - 520
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=(255, 255, 255, 255), stroke_width=6, stroke_fill=(30, 20, 25, 255)); y += 120
    im.convert('RGB').save(path, quality=92)

def build(reel):
    tmp = tempfile.mkdtemp(); ids = [c for c, _ in reel['ex']]; segs = []
    for i, (cid, sets) in enumerate(reel['ex']):
        png = os.path.join(tmp, 'o%d.png' % i); overlay(ids, i, NAMES[cid], sets, png)
        p = clip(cid); d = dur(p); ss = max(0.0, min(d - SEG - 0.1, d * 0.3))
        s = os.path.join(tmp, 's%d.mp4' % i); segs.append(s)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.2f' % ss, '-t', '%.2f' % SEG, '-i', p, '-loop', '1', '-i', png, '-filter_complex',
                        '[0:v]fps=30,scale=%d:%d:flags=lanczos,unsharp=5:5:0.6,setsar=1[v];[v][1:v]overlay=0:0:shortest=1,format=yuv420p[o]' % (W, H),
                        '-map', '[o]', '-t', '%.2f' % SEG, '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', s], check=True)
    lst = os.path.join(tmp, 'l.txt'); open(lst, 'w').write(''.join("file '%s'\n" % x for x in segs))
    out = os.path.join(OUT, reel['id'] + '.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out], check=True)
    fr = os.path.join(tmp, 'f.jpg'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.2', '-i', clip(ids[0]), '-frames:v', '1', fr], check=True)
    cover(reel, fr, os.path.join(OUT, reel['id'] + '-coperta.jpg'))
    return out

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for r in REELS: print('gata:', os.path.basename(build(r)))
