#!/usr/bin/env python3
"""Cronometru pentru reel-uri (R2, B4): PNG static + GIF animat 60 -> 0, fundal transparent.

Rulezi:   python3 brand/reels-overlays/make_timer.py
Rezultat: brand/reels-overlays/timer/
  timer-60s-static.png            insigna „60 s”, fullframe 1080 x 1920 (sus-centru, zona sigură)
  timer-60s-numaratoare.gif       numărătoare inversă 60 -> 0, 1 cadru pe secundă, 360 x 360, fundal transparent
  timer-60s-numaratoare-fullframe.gif   același, dar 1080 x 1920, deja așezat sus-centru
GIF-ul: dacă aplicația ta nu importă GIF cu transparență, folosești stickerul de cronometru din aplicație.
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'timer'); os.makedirs(OUT, exist_ok=True)
BOLD = os.path.join(HERE, 'fonts', 'Poppins-Bold.ttf')
INK, CREAM, WINE, TRACK = (43, 36, 49), (255, 249, 246), (138, 52, 89), (248, 220, 230)
S = 4          # supraeșantionare
SIZE = 360

def frame(n, total=60):
    W = SIZE * S
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pad = 12 * S
    d.ellipse([pad, pad, W - pad, W - pad], fill=CREAM + (255,))
    ring = 26 * S
    box = [pad + ring // 2, pad + ring // 2, W - pad - ring // 2, W - pad - ring // 2]
    d.arc(box, 0, 360, fill=TRACK + (255,), width=ring)
    if n > 0:
        end = -90 + 360 * (n / total)
        d.arc(box, -90, end, fill=WINE + (255,), width=ring)
        # capete rotunjite
        r = ring // 2; cx = cy = W // 2; rad = (box[2] - box[0]) // 2
        for ang in (-90, end):
            x = cx + rad * math.cos(math.radians(ang)); y = cy + rad * math.sin(math.radians(ang))
            d.ellipse([x - r, y - r, x + r, y + r], fill=WINE + (255,))
    f1 = ImageFont.truetype(BOLD, 128 * S); f2 = ImageFont.truetype(BOLD, 36 * S)
    txt = str(n)
    bb = d.textbbox((0, 0), txt, font=f1); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((W - tw) / 2 - bb[0], W / 2 - th / 2 - bb[1] - 22 * S), txt, font=f1, fill=INK + (255,))
    lab = 'seconds'; bb2 = d.textbbox((0, 0), lab, font=f2)
    d.text(((W - (bb2[2] - bb2[0])) / 2 - bb2[0], W / 2 + 62 * S), lab, font=f2, fill=WINE + (255,))
    return im.resize((SIZE, SIZE), Image.LANCZOS)

def to_gif_frame(rgba):
    # GIF are transparență pe 1 bit: pixelii semi-transparenți devin crem (aproape de culoarea ceasului) sau dispar
    bg = Image.new('RGB', rgba.size, CREAM)
    rgb = Image.alpha_composite(Image.new('RGBA', rgba.size, CREAM + (255,)), rgba).convert('RGB')
    p = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    mask = rgba.split()[3].point(lambda a: 255 if a < 100 else 0)
    p.paste(255, mask=mask)
    p.info['transparency'] = 255
    return p

def static_png():
    im = frame(60)
    full = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    small = im.resize((240, 240), Image.LANCZOS)
    full.alpha_composite(small, ((1080 - 240) // 2, 300))
    full.save(os.path.join(OUT, 'timer-60s-static.png'))
    im.save(os.path.join(OUT, 'timer-60s-static-mic.png'))

def gifs():
    frames = [frame(n) for n in range(60, -1, -1)]
    g = [to_gif_frame(f) for f in frames]
    g[0].save(os.path.join(OUT, 'timer-60s-numaratoare.gif'), save_all=True, append_images=g[1:], duration=1000, loop=1,
              transparency=255, disposal=2, optimize=False)
    full = []
    for f in frames:
        c = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); c.alpha_composite(f.resize((240, 240), Image.LANCZOS), (420, 300)); full.append(to_gif_frame(c))
    full[0].save(os.path.join(OUT, 'timer-60s-numaratoare-fullframe.gif'), save_all=True, append_images=full[1:], duration=1000, loop=1,
                 transparency=255, disposal=2, optimize=False)

if __name__ == '__main__':
    static_png(); gifs()
    for f in sorted(os.listdir(OUT)): print(f, round(os.path.getsize(os.path.join(OUT, f)) / 1024), 'KB')
