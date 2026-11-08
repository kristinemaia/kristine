#!/usr/bin/env python3
"""Clipurile din stream, pe vertical (1080x1920) pentru TikTok / Reels / Shorts:
sus facecam-ul (decupat strâns pe față), jos jocul, la mijloc hook-ul pe o bandă vișinie (fără emoji: fontul nu le are; emoji le pui în descriere). Sunetul din stream, egalizat.
Rulezi: python3 studio/twitch-clips/build_vertical.py <folder cu clipurile descărcate> <folder ieșire>"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
FONT = os.path.join(ROOT, 'brand/reels-overlays/fonts/Poppins-Bold.ttf')
# id clip: (nume, hook, facecam x,y,w,h, joc x,y,w,h, start, durată)   coordonate în sursa 1280x720
CLIPS = {
 '3719226022': ('wow-camel', 'First time in WoW: I die…\nso I do a camel impression', (20, 270, 360, 320), (450, 0, 810, 720), 0, 60),
 '743161647':  ('cant-say-wow', 'Me trying to say\n"World of Warcraft"', (40, 300, 360, 320), (470, 0, 810, 720), 0, 22.5),
 '2295954336': ('fortnite-win', 'My reaction when\nI finally win in Fortnite', (20, 320, 360, 320), (400, 0, 810, 720), 0, 40),
}
def band(text, path):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 54); lines = text.split('\n'); lh = 70; h = lh * len(lines) + 44; y0 = 960 - h // 2
    d.rectangle([0, y0, 1080, y0 + h], fill=(138, 52, 89, 245))
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f); d.text(((1080 - tw) / 2, y0 + 22 + i * lh), l, font=f, fill=(255, 255, 255))
    f2 = ImageFont.truetype(FONT, 34); s = 'twitch.tv/kristinemaia'; tw = d.textlength(s, font=f2)
    d.rounded_rectangle([(1080 - tw) / 2 - 24, 1830, (1080 + tw) / 2 + 24, 1890], 30, fill=(43, 36, 49, 220))
    d.text(((1080 - tw) / 2, 1836), s, font=f2, fill=(255, 255, 255))
    im.save(path)
def build(src, out):
    os.makedirs(out, exist_ok=True)
    for cid, (name, hook, fc, gm, ss, d) in CLIPS.items():
        inp = os.path.join(src, cid + '.mp4')
        if not os.path.exists(inp): continue
        png = os.path.join(out, '_' + name + '.png'); band(hook, png)
        fc_ = 'crop=%d:%d:%d:%d,scale=1080:960:flags=lanczos' % (fc[2], fc[3], fc[0], fc[1])
        gm_ = 'crop=%d:%d:%d:%d,scale=1080:960:flags=lanczos' % (gm[2], gm[3], gm[0], gm[1])
        fcx = ("[0:v]split[a][b];[a]%s,eq=contrast=1.04:saturation=1.05[top];[b]%s[bot];[top][bot]vstack[v];"
               "[v][1:v]overlay=0:0,fade=t=in:st=0:d=0.2,fade=t=out:st=%.2f:d=0.4,format=yuv420p[o];"
               "[0:a]highpass=f=80,loudnorm=I=-15:TP=-1.5:LRA=9,afade=t=out:st=%.2f:d=0.4[ao]") % (fc_, gm_, d - 0.4, d - 0.4)
        o = os.path.join(out, name + '.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(d), '-i', inp, '-loop', '1', '-t', str(d), '-i', png,
                        '-filter_complex', fcx, '-map', '[o]', '-map', '[ao]', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-r', '30',
                        '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', o], check=True)
        print('gata', name)
if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
