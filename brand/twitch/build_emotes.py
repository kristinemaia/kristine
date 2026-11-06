#!/usr/bin/env python3
"""Emoticoanele Twitch ale Kristinei (prefixul tău de canal se pune în față, ex. kristi + Flex).
Rulezi: python3 brand/twitch/build_emotes.py  → brand/twitch/emotes/
  static:  <nume>_112.png, _56.png, _28.png  (PNG transparent, cum le cere Twitch)
  animate: <nume>_anim_112.gif (buclă, sub 1 MB, max 60 de cadre; Twitch face singur mărimile mici)
Desen vectorial: siluetă rotundă în vișiniu, contur gros închis (se citește și la 28 px, pe chat închis sau deschis)."""
import math, os
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emotes'); os.makedirs(OUT, exist_ok=True)
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reels-overlays', 'fonts', 'Poppins-Bold.ttf')
S = 4; N = 112 * S                                   # desenăm la 448 px și micșorăm (margini netede)
INK, WINE, PINK, CREAM, MINT, BLUE, GOLD = (43, 36, 49), (138, 52, 89), (241, 195, 214), (255, 249, 246), (120, 205, 165), (110, 160, 220), (245, 190, 60)
OUTL = 22                                            # grosimea conturului (la 448 px)

def canvas(): return Image.new('RGBA', (N, N), (0, 0, 0, 0))
def seg(d, a, b, w, col):
    d.line([a, b], fill=col, width=w); r = w // 2
    for p in (a, b): d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)
def limbs(d, pairs, w, col=WINE):
    for a, b in pairs: seg(d, a, b, w + OUTL, INK)
    for a, b in pairs: seg(d, a, b, w, col)
def head(d, c, r, col=WINE):
    d.ellipse([c[0] - r - OUTL // 2, c[1] - r - OUTL // 2, c[0] + r + OUTL // 2, c[1] + r + OUTL // 2], fill=INK)
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col)
    # coada de cal (semnul tău), prinsă sus cu un elastic auriu
    tx, ty = c[0] + r * 0.55, c[1] - r * 0.95
    d.ellipse([tx - 24 - OUTL // 2, ty - 50 - OUTL // 2, tx + 24 + OUTL // 2, ty + 10 + OUTL // 2], fill=INK)
    d.ellipse([tx - 24, ty - 50, tx + 24, ty + 10], fill=col)
    d.ellipse([tx - 13, ty - 4, tx + 13, ty + 22], fill=GOLD)
def P(x, y): return (int(x * N), int(y * N))
def figure(d, hip, sh, hd, la, ra, ll, rl, w=44, col=WINE):
    """hip, sh = șold și umăr; la/ra/ll/rl = [cot, mână] / [genunchi, picior]"""
    limbs(d, [(sh, la[0]), (la[0], la[1]), (sh, ra[0]), (ra[0], ra[1]), (hip, ll[0]), (ll[0], ll[1]), (hip, rl[0]), (rl[0], rl[1]), (hip, sh)], w, col)
    head(d, hd, 46, col)
def text(d, s, y, size, col=CREAM, stroke=INK, sw=16):
    f = ImageFont.truetype(FONT, size); tw = d.textlength(s, font=f)
    d.text(((N - tw) / 2, y), s, font=f, fill=col, stroke_width=sw, stroke_fill=stroke)
def save(name, frames, dur=70):
    small = [f.resize((112, 112), Image.LANCZOS) for f in frames]
    first = small[0]
    for sz in (112, 56, 28): first.resize((sz, sz), Image.LANCZOS).save(os.path.join(OUT, '%s_%d.png' % (name, sz)))
    if len(frames) > 1:
        # GIF cu transparență: paletă + o culoare rezervată pentru fundal
        pal = []
        for im in small:
            a = im.split()[3].point(lambda v: 255 if v > 110 else 0)
            p = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
            p.paste(255, mask=Image.eval(a, lambda v: 255 - v)); pal.append(p)
        pal[0].save(os.path.join(OUT, '%s_anim_112.gif' % name), save_all=True, append_images=pal[1:], loop=0, duration=dur,
                    transparency=255, disposal=2, optimize=False)

def ease(t): return 0.5 - 0.5 * math.cos(2 * math.pi * t)
F = 16
# 1. Flex: brațul încordat, bicepsul „pompează”
def flex(t):
    im = canvas(); d = ImageDraw.Draw(im); k = ease(t)
    sh, el, fi = P(.38, .62), P(.62, .66), P(.66, .36 - .04 * k)
    limbs(d, [(P(.2, .95), sh), (sh, el), (el, fi)], 70)
    r = int(N * (.075 + .025 * k)); bc = P(.5, .58 - .02 * k)       # bicepsul
    d.ellipse([bc[0] - r - 13, bc[1] - r - 13, bc[0] + r + 13, bc[1] + r + 13], fill=INK)
    d.ellipse([bc[0] - r, bc[1] - r, bc[0] + r, bc[1] + r], fill=WINE)
    d.ellipse([fi[0] - 44, fi[1] - 44, fi[0] + 44, fi[1] + 44], fill=INK); d.ellipse([fi[0] - 31, fi[1] - 31, fi[0] + 31, fi[1] + 31], fill=WINE)
    if k > .5:  # sclipiri
        for x, y in [(.8, .22), (.86, .4)]:
            c = P(x, y); s = int(26 * (k - .5) * 2) + 6
            d.polygon([(c[0], c[1] - s * 2), (c[0] + s // 2, c[1]), (c[0], c[1] + s * 2), (c[0] - s // 2, c[1])], fill=GOLD)
            d.polygon([(c[0] - s * 2, c[1]), (c[0], c[1] + s // 2), (c[0] + s * 2, c[1]), (c[0], c[1] - s // 2)], fill=GOLD)
    return im
# 2. Stretch: brațele sus, înclinare dintr-o parte în alta
def stretch(t):
    im = canvas(); d = ImageDraw.Draw(im); a = math.sin(2 * math.pi * t) * .3
    hip = P(.5, .64); L = .2 * N
    sh = (int(hip[0] + L * math.sin(a)), int(hip[1] - L * math.cos(a)))
    hd = (int(sh[0] + .12 * N * math.sin(a)), int(sh[1] - .12 * N * math.cos(a)))
    def arm(side):
        ang = a + side * 1.05
        el = (int(sh[0] + .16 * N * math.sin(ang)), int(sh[1] - .13 * N * math.cos(ang)))
        ha = (int(el[0] + .15 * N * math.sin(ang - side * .55)), int(el[1] - .15 * N * math.cos(ang - side * .55)))
        return [el, ha]
    figure(d, hip, sh, hd, arm(-1), arm(1), [P(.43, .8), P(.39, .95)], [P(.57, .8), P(.61, .95)])
    return im
# 3. Squat: în jos și în sus
def squat(t):
    im = canvas(); d = ImageDraw.Draw(im); k = ease(t); dy = .16 * k
    hip = P(.48 - .08 * k, .58 + dy); sh = P(.5 + .04 * k, .36 + dy * .9); hd = P(.53 + .05 * k, .23 + dy * .9)
    knee = P(.62, .74 + dy * .2)
    figure(d, hip, sh, hd, [P(.66, .4 + dy), P(.82, .4 + dy)], [P(.66, .42 + dy), P(.82, .42 + dy)],
           [knee, P(.58, .93)], [(knee[0] + 14, knee[1] + 6), P(.62, .93)])
    return im
# 4. Water: sticla de apă care se înclină spre „gură”, cu picături
def water(t):
    im = canvas().rotate(0); d = ImageDraw.Draw(im); k = ease(t)
    b = Image.new('RGBA', (N, N), (0, 0, 0, 0)); db = ImageDraw.Draw(b)
    db.rounded_rectangle([N * .34, N * .26, N * .66, N * .9], 60, fill=INK); db.rounded_rectangle([N * .34 + 14, N * .26 + 14, N * .66 - 14, N * .9 - 14], 48, fill=BLUE)
    db.rectangle([N * .34 + 14, N * .26 + 14, N * .66 - 14, N * .5], fill=CREAM)
    db.rounded_rectangle([N * .41, N * .12, N * .59, N * .3], 22, fill=INK); db.rounded_rectangle([N * .41 + 12, N * .12 + 12, N * .59 - 12, N * .3 - 12], 14, fill=WINE)
    db.rectangle([N * .34 + 14, N * .6, N * .66 - 14, N * .7], fill=WINE)
    b = b.rotate(-25 * k, resample=Image.BICUBIC, center=(N * .5, N * .6)); im.alpha_composite(b)
    if k > .35:
        for i, (x, y) in enumerate([(.2, .3), (.14, .48), (.24, .6)]):
            c = P(x, y + .05 * k); r = 20
            d.ellipse([c[0] - r - 9, c[1] - r - 9, c[0] + r + 9, c[1] + r + 9], fill=INK); d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=BLUE)
    return im
# 5. GG: literele „pulsează”
def gg(t):
    im = canvas(); d = ImageDraw.Draw(im); k = ease(t)
    d.ellipse([N * .06, N * .06, N * .94, N * .94], fill=INK); d.ellipse([N * .06 + 16, N * .06 + 16, N * .94 - 16, N * .94 - 16], fill=WINE)
    text(d, 'GG', N * .2 - 14 * k, int(230 + 30 * k), CREAM, INK, 14)
    return im
# 6. Sit: scaunul cu „stand up!” care clipește
def sit(t):
    im = canvas(); d = ImageDraw.Draw(im)
    w = 46
    limbs(d, [(P(.3, .2), P(.3, .62)), (P(.3, .62), P(.7, .62)), (P(.3, .62), P(.3, .9)), (P(.7, .62), P(.7, .9))], w, PINK)
    if t < .5:
        d.ellipse([N * .48, N * .02, N * .98, N * .52], fill=INK); d.ellipse([N * .48 + 14, N * .02 + 14, N * .98 - 14, N * .52 - 14], fill=(220, 60, 70))
        f = ImageFont.truetype(FONT, 190); tw = d.textlength('!', font=f); d.text((N * .73 - tw / 2, N * .0), '!', font=f, fill=CREAM)
    return im
# 7. Rope: coarda trece pe sub picioare
def rope(t):
    im = canvas(); d = ImageDraw.Draw(im); k = abs(math.sin(math.pi * t)); up = .06 * k
    a = 2 * math.pi * t; ry = .5 + .44 * math.cos(a)
    hip, sh, hd = P(.5, .6 - up), P(.5, .38 - up), P(.5, .24 - up)
    hl, hr = P(.24, .6 - up), P(.76, .6 - up)
    col = (220, 90, 130)
    behind = math.sin(a) > 0
    def ropeline():
        pts = [(hl[0] + (hr[0] - hl[0]) * s, int(hl[1] + (N * ry - hl[1]) * math.sin(math.pi * s) + 0)) for s in [i / 20 for i in range(21)]]
        d.line(pts, fill=INK, width=24); d.line(pts, fill=col, width=12)
    if behind: ropeline()
    figure(d, hip, sh, hd, [P(.32, .5 - up), hl], [P(.68, .5 - up), hr], [P(.45, .78 - up), P(.45, .93 - up)], [P(.55, .78 - up), P(.55, .93 - up)])
    if not behind: ropeline()
    return im
# 8. Love: inimă cu ganteră
def love(t):
    im = canvas(); d = ImageDraw.Draw(im); k = ease(t); s = 1 + .08 * k
    c = (N / 2, N * .52)
    def heart(sc, col):
        pts = []
        for i in range(120):
            u = 2 * math.pi * i / 120
            x = 16 * math.sin(u) ** 3; y = -(13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u) - math.cos(4 * u))
            pts.append((c[0] + x * sc, c[1] + y * sc))
        d.polygon(pts, fill=col)
    heart(13.2 * s, INK); heart(12.2 * s, WINE)
    limbs(d, [(P(.3, .5), P(.7, .5))], 22, CREAM)
    for x in (.27, .73):
        d.rounded_rectangle([N * x - 26, N * .38, N * x + 26, N * .62], 14, fill=INK); d.rounded_rectangle([N * x - 16, N * .38 + 10, N * x + 16, N * .62 - 10], 10, fill=CREAM)
    return im

EMOTES = [('Flex', flex), ('Stretch', stretch), ('Squat', squat), ('Water', water), ('GG', gg), ('StandUp', sit), ('Rope', rope), ('Love', love)]
if __name__ == '__main__':
    for name, fn in EMOTES:
        frames = [fn(i / F) for i in range(F)]
        save(name, frames, 60 if name in ('Rope', 'StandUp') else 70)
        print(name, os.path.getsize(os.path.join(OUT, '%s_anim_112.gif' % name)) // 1024, 'KB')
