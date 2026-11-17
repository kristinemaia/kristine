#!/usr/bin/env python3
"""Formatul „Tried and tested” (modelul Caroline O'Mahony, 17 nov): carusel cu poze făcute de Kristine, câte un lucru pe slide,
text galben cu contur negru, centrat, ca pus direct din aplicație (pare spontan, nu reclamă). Emoji-urile ies colorate.

Rețeta (o postare = un fișier JSON în brand/carousels-en/specs/):
  {"out": "EN-P1-tried-and-tested",
   "slides": [{"photo": "src/poza.jpg", "text": "Rândul 1\\nRândul 2", "y": 0.30, "focus": 0.4}, ...]}
  photo: calea față de brand/carousels-en/ (sau absolută) · text: rândurile, \\n între paragrafe · y: unde începe textul (0 = sus, 1 = jos; implicit 0.33)
  focus: unde e subiectul pe verticală, la decupare (0 = sus, 0.5 = mijloc, 1 = jos; implicit 0.4)
Rulezi: python3 brand/carousels-en/build_produse.py brand/carousels-en/specs/<fișier>.json -> out/<out>-1.png … + <out>.zip"""
import json, os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
FONT = os.path.join(ROOT, 'brand/reels-overlays/fonts/Poppins-SemiBold.ttf')
EMOJI_FONT = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
W, H, SIZE, MAXW = 1080, 1350, 42, 880
YELLOW, BLACK = (255, 228, 92, 255), (0, 0, 0, 255)

def is_emoji(ch): o = ord(ch); return o >= 0x2190 and not (0x2000 <= o <= 0x206F) or o in (0x200D, 0xFE0F)
def tokens(line):
    """cuvinte și emoji, cu spațiile păstrate"""
    out, cur, emo = [], '', False
    for ch in line:
        e = is_emoji(ch)
        if ch == ' ':
            if cur: out.append((cur, emo)); cur = ''
            out.append((' ', False)); continue
        if cur and e != emo: out.append((cur, emo)); cur = ''
        cur += ch; emo = e
    if cur: out.append((cur, emo))
    return out

def emoji_img(seq, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (400, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 20), seq, font=f, embedded_color=True)
    im = im.crop(im.getbbox()); return im.resize((int(im.width * size / im.height), size), Image.LANCZOS)

def width(tok, f):
    t, e = tok
    return emoji_img(t, SIZE).width + 4 if e else f.getlength(t)

def wrap(par, f):
    lines, cur, w = [], [], 0
    for tok in tokens(par):
        tw = width(tok, f)
        if cur and w + tw > MAXW and tok[0] != ' ':
            while cur and cur[-1][0] == ' ': w -= f.getlength(' '); cur.pop()
            lines.append(cur); cur, w = [], 0
        if not cur and tok[0] == ' ': continue
        cur.append(tok); w += tw
    if cur: lines.append(cur)
    return lines

def cover(path, focus):
    im = Image.open(path).convert('RGB'); r = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - W) // 2; y = int((im.height - H) * focus)
    return im.crop((x, y, x + W, y + H))

def slide(s, base):
    p = s['photo'] if os.path.isabs(s['photo']) else os.path.join(base, s['photo'])
    im = cover(p, s.get('focus', 0.4)).convert('RGBA'); d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, SIZE)
    lh = int(SIZE * 1.32); y = int(H * s.get('y', 0.33))
    for k, par in enumerate(s['text'].split('\n')):
        if not par.strip(): y += lh // 2; continue
        for line in wrap(par, f):
            lw = sum(width(t, f) for t in line); x = (W - lw) / 2
            for t, e in line:
                if e:
                    em = emoji_img(t, SIZE); im.alpha_composite(em, (int(x), int(y + 4))); x += em.width + 4
                else:
                    d.text((x, y), t, font=f, fill=YELLOW, stroke_width=3, stroke_fill=BLACK); x += f.getlength(t)
            y += lh
        y += lh // 3
    return im.convert('RGB')

def build(spec_path):
    spec = json.load(open(spec_path, encoding='utf-8')); out_dir = os.path.join(HERE, 'out'); os.makedirs(out_dir, exist_ok=True)
    files = []
    for n, s in enumerate(spec['slides'], 1):
        f = os.path.join(out_dir, '%s-%d.png' % (spec['out'], n)); slide(s, HERE).save(f); files.append(f)
    z = os.path.join(HERE, spec['out'] + '.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files: zf.write(f, os.path.basename(f))
    print('gata:', len(files), 'slide-uri ->', z)

if __name__ == '__main__':
    for a in sys.argv[1:]: build(a)
