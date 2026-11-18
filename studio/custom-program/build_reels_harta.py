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
sys.path.insert(0, os.path.join(ROOT, 'studio/montaj'))
from curat import GRADE   # aceeași culoare ca la reel-urile tale
from workouts import NAMES
W, H, SEG = 1080, 1920, 3.0
FONTS = os.path.join(ROOT, 'brand/reels-overlays/fonts')
OUT = os.path.join(HERE, 'out', 'reels-harta')
PINK, RED = (255, 77, 109, 255), (229, 45, 58, 255)

REELS = [
    {'id': 'RH1-warm-up', 'hook': 'Warm up like this if you sit all day',
     'ex': [('incalzire-mars-pe-loc', '1 min'), ('incalzire-step-jack', '30 s'), ('incalzire-inchworm', '5 slow reps'), ('mobilitate-extensie-toracica', '8 reps')]},
    {'id': 'RH2-home-workout', 'hook': 'No equipment? Do this at home',
     'ex': [('incalzire-jumping-jacks', '40 s'), ('cardio-skaters', '40 s'), ('impins-flotare', '3 × 8'), ('core-hollow-hold', '3 × 20 s')]},
]

def font(n, s): return ImageFont.truetype(os.path.join(FONTS, n), s)

def clip(cid):
    # doar originalele filmate de Kristine (clips/<id>.mov, 1080 × 1920, fără text pe ele); clipurile vechi, de 540 × 960, nu intră în reel-uri
    p = os.path.join(HERE, 'clips', cid + '.mov')
    if not os.path.exists(p): raise SystemExit('lipsește originalul la rezoluție mare: ' + cid)
    wh = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip().rstrip(',').split(',')
    if max(int(wh[0]), int(wh[1])) < 1920: raise SystemExit('clip prea mic pentru reel: ' + cid)
    return p

def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)

def overlay(ids, idx, name, sets, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    for i in range(420): g.line([(0, i), (W, i)], fill=(0, 0, 0, int(110 * (1 - i / 420) ** 1.5)))          # sus, ca să se vadă siluetele
    for y in range(H - 760, H):                                                                            # jos: umbră, ca să se citească seriile
        g.line([(0, y), (W, y)], fill=(0, 0, 0, int(170 * ((y - (H - 760)) / 760) ** 1.2)))
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
                        ('[0:v]fps=30,scale=%d:%d:flags=lanczos,' % (W, H)) + GRADE + ',setsar=1[v];[v][1:v]overlay=0:0:shortest=1,format=yuv420p[o]',
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
