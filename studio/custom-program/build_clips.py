#!/usr/bin/env python3
"""Clipurile exercițiilor pentru Custom Program: curățate (culoarea Kristine Maia), tăiate și cu numele exercițiului.
Rulezi: python3 studio/custom-program/build_clips.py [nume ...]
Intrare: studio/custom-program/clips/<nume>.mov   Ieșire: studio/custom-program/out/<nume>.mp4 (1080x1920, fără sunet)"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'montaj')); import curat
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC, OUT = os.path.join(ROOT, 'studio/custom-program/clips'), os.path.join(ROOT, 'studio/custom-program/out')
CUR = os.path.join(ROOT, 'studio/montaj/_curat'); FONTS = os.path.join(ROOT, 'brand/reels-overlays/fonts')
INK, CREAM, WINE = (43, 36, 49), (255, 249, 246), (138, 52, 89)
# nume: (titlu EN, eticheta mică, început s, sfârșit s sau None = până la final - 0,4 s)
CLIPS = {
    'incalzire-coarda':                   ('Jump rope', 'Warm-up', 0.4, None),
    'incalzire-cercuri-brate':            ('Arm circles', 'Warm-up · forward & back', 0.3, None),
    'incalzire-cercuri-sold':             ('Hip circles', 'Warm-up · both ways', 0.3, None),
    'mobilitate-cat-cow':                 ('Cat-cow', 'Mobility', 0.5, None),
    'mobilitate-open-book':               ('Open book', 'Mobility · each side', 0.4, None),
    'mobilitate-worlds-greatest-stretch': ("World's greatest stretch", 'Mobility · each side', 0.4, None),
    'mobilitate-90-90-v2':                ('90/90 hip switch', 'Mobility', 7.0, None),
    'mobilitate-flexori-sold':            ('Kneeling hip flexor stretch', 'Mobility · each side', 0.4, None),
    'mobilitate-childs-pose':             ("Child's pose reach", 'Mobility', 0.4, None),
    'mobilitate-deep-squat-hold':         ('Deep squat hold', 'Mobility', 0.4, None),
}
def eticheta(titlu, mic, path):
    """pastila cu numele: crem cu margine vișinie, sus în stânga, sub zona de status a telefonului"""
    fb, fm = ImageFont.truetype(os.path.join(FONTS, 'Poppins-SemiBold.ttf'), 54), ImageFont.truetype(os.path.join(FONTS, 'Poppins-Medium.ttf'), 32)
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = max(d.textlength(titlu, font=fb), d.textlength(mic.upper(), font=fm)) + 84; h = 160; x, y = 60, 150
    d.rounded_rectangle([x + 6, y + 8, x + w + 6, y + h + 8], 34, fill=(0, 0, 0, 60))            # umbră discretă
    d.rounded_rectangle([x, y, x + w, y + h], 34, fill=CREAM + (240,), outline=WINE, width=5)
    d.text((x + 42, y + 22), mic.upper(), font=fm, fill=WINE)
    d.text((x + 42, y + 62), titlu, font=fb, fill=INK)
    im.save(path)
def construieste(nume):
    titlu, mic, a, b = CLIPS[nume]; os.makedirs(CUR, exist_ok=True)
    c = os.path.join(CUR, nume + '.mp4')
    if not os.path.exists(c): curat.ruleaza(os.path.join(SRC, nume + '.mov'), c)
    b = b if b is not None else curat.dur(c) - 0.4; d = b - a
    png = os.path.join(CUR, nume + '-eticheta.png'); eticheta(titlu, mic, png)
    fc = ("[0:v]setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.25,fade=t=out:st=%.2f:d=0.3[v];"
          "[1:v]format=rgba,fade=t=in:st=0.3:d=0.35:alpha=1[e];[v][e]overlay=0:0:shortest=1,format=yuv420p[o]") % (d - 0.3)
    out = os.path.join(OUT, nume + '.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', '%.2f' % d, '-i', c, '-loop', '1', '-t', '%.2f' % d, '-i', png,
                    '-filter_complex', fc, '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-movflags', '+faststart', out], check=True)
    print('gata %-36s %.1f s' % (nume, d))
if __name__ == '__main__':
    for n in (sys.argv[1:] or CLIPS): construieste(n)
