#!/usr/bin/env python3
"""Reel „N moves for…”: hook POV sus, apoi exercițiile numerotate (un cadru pe exercițiu, tăieturi simple), text final.
Rulezi: python3 studio/montaj/reel_lista.py studio/montaj/<spec>.json
Spec: {"out": "...mp4", "hook": ["rândul 1", "rândul 2"], "hook_d": 2.6, "outro": "text final", "outro_d": 2.0,
       "items": [{"clip": "cale/catre/clip.mp4", "ss": 1.0, "d": 3.5, "speed": 1.0, "title": "Thoracic extension"}]}
Clipurile trebuie să fie deja curățate (1080x1920, fără etichetă), de ex. din studio/montaj/_curat."""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
FONTS = os.path.join(ROOT, 'brand/reels-overlays/fonts')
CREAM, WINE = (255, 249, 246), (138, 52, 89)

def text_png(lines, path, size, y, bold=True):
    """text centrat, crem, cu umbră moale (se citește pe orice fundal); y = marginea de sus a blocului"""
    f = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Bold.ttf' if bold else 'Poppins-SemiBold.ttf'), size)
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); sh = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(im), ImageDraw.Draw(sh); lh = int(size * 1.18)
    for i, t in enumerate(lines):
        w = d.textlength(t, font=f); x = (1080 - w) / 2; yy = y + i * lh
        ds.text((x, yy + 4), t, font=f, fill=(0, 0, 0, 170)); d.text((x, yy), t, font=f, fill=CREAM + (255,))
    sh = sh.filter(ImageFilter.GaussianBlur(10)); Image.alpha_composite(sh, im).save(path)

def main(spec_path):
    S = json.load(open(spec_path)); tmp = tempfile.mkdtemp(); parts = []
    for i, it in enumerate(S['items']):
        png = os.path.join(tmp, 't%d.png' % i); text_png(['%d. %s' % (i + 1, it['title'])], png, 70, 250)
        sp = it.get('speed', 1.0); dur = it['d'] / sp
        ov = [png]; fc = '[0:v]setpts=(PTS-STARTPTS)/%.3f,fps=30,scale=1080:1920,setsar=1[v];' % sp
        # titlul numerotat (la primul exercițiu apare după hook)
        t0 = S.get('hook_d', 2.6) if i == 0 else 0.0
        fc += "[1:v]format=rgba,fade=t=in:st=%.2f:d=0.2:alpha=1[t];[v][t]overlay=0:0:enable='gte(t,%.2f)'[a]" % (t0, t0)
        cur = '[a]'; inputs = ['-ss', str(it['ss']), '-t', '%.3f' % it['d'], '-i', it['clip'], '-loop', '1', '-t', '%.3f' % dur, '-i', png]
        if i == 0:
            h = os.path.join(tmp, 'hook.png'); text_png(S['hook'], h, 62, 230); inputs += ['-loop', '1', '-t', '%.3f' % dur, '-i', h]
            fc += ";[2:v]format=rgba,fade=t=out:st=%.2f:d=0.2:alpha=1[h];%s[h]overlay=0:0:enable='lt(t,%.2f)'[b]" % (S.get('hook_d', 2.6) - 0.2, cur, S.get('hook_d', 2.6)); cur = '[b]'
        if i == len(S['items']) - 1 and S.get('outro'):
            o = os.path.join(tmp, 'outro.png'); text_png([S['outro']], o, 56, 1500, bold=False)
            idx = 3 if i == 0 else 2; inputs += ['-loop', '1', '-t', '%.3f' % dur, '-i', o]; st = dur - S.get('outro_d', 2.0)
            fc += ";[%d:v]format=rgba,fade=t=in:st=%.2f:d=0.25:alpha=1[o];%s[o]overlay=0:0:enable='gte(t,%.2f)'[c]" % (idx, st, cur, st); cur = '[c]'
        fc += ';%sformat=yuv420p[out]' % cur
        p = os.path.join(tmp, 'p%d.mp4' % i)
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[out]', '-t', '%.3f' % dur, '-an',
                        '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-r', '30', p], check=True)
        parts.append(p)
    lst = os.path.join(tmp, 'l.txt'); open(lst, 'w').write(''.join("file '%s'\n" % p for p in parts))
    out = os.path.join(ROOT, S['out']); os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out], check=True)
    print(out)

if __name__ == '__main__':
    main(sys.argv[1])
