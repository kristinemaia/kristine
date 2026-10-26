#!/usr/bin/env python3
"""Montaj B3 „Shoulders rounded from the desk? 3 moves.” (ffmpeg), ~24 s, 1080 x 1920.
Cadrele sunt tăiate de la talie în sus și puse pe fundal crem (fără cadre centrate pe fese).
Rulezi: python3 studio/montaj/montaj_b3.py <folder cu clipurile> <ieșire.mp4>
Clipuri: 699ac151-IMG_8163 (wall angels), 08d62be8-IMG_8163 (chest opener), c6940856-IMG_8166 (thread the needle)."""
import glob, os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
def clip(k): return glob.glob(os.path.join(src, k + '*.mov'))[0]
OV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'brand', 'reels-overlays', 'out', 'B3')
BG = '0xFFF9F6'
def panel(crop):  # crop de la talie în sus, apoi pe fundal crem
    return 'crop=%s,scale=1080:-2:flags=lanczos,pad=1080:1920:0:(1920-ih)/2:color=%s' % (crop, BG)
WIDE = len(sys.argv) > 3 and sys.argv[3] == '--wide'   # varianta mai largă: wall angels cu tot corpul (din față), restul tăiat sub talie
C1 = 'null' if WIDE else panel('1080:840:0:260')
C2 = panel('1080:1000:0:250') if WIDE else panel('1080:840:0:300')
C3 = panel('660:560:0:1120') if WIDE else panel('660:500:0:1150')
SEG = [('699ac151', 0.3, 10.0, 1.15, C1, 1),   # 1 · wall angels
       ('08d62be8', 1.0, 4.5, 1.0, C2, 2),     # 2 · chest opener, o parte
       ('08d62be8', 13.0, 4.5, 1.0, C2, 2),    # 2 · chest opener, cealaltă parte
       ('c6940856', 1.0, 8.0, 1.0, C3, 2)]     # 3 · thread the needle
TD = 0.3
inputs, chains, durs, lab = [], [], [], []
for i, (k, ss, d, sp, f, l) in enumerate(SEG):
    inputs += ['-ss', str(ss), '-t', str(d), '-i', clip(k)]
    chains.append('[%d:v]fps=30,%s,setpts=(PTS-STARTPTS)/%s,setsar=1,format=yuv420p[v%d]' % (i, f, sp, i)); durs.append(d / sp); lab.append(l)
n = len(SEG)
x, acc, cur = [], 0.0, '[v0]'
starts = [0.0]
for j in range(1, n):
    acc += durs[j - 1]; off = acc - j * TD
    x.append('%s[v%d]xfade=transition=fade:duration=%.2f:offset=%.2f[x%d]' % (cur, j, TD, off, j)); cur = '[x%d]' % j; starts.append(off)
total = sum(durs) - (n - 1) * TD
t_l2 = starts[1]  # eticheta 2 începe odată cu al doilea segment
inputs += ['-i', os.path.join(OV, 'B3_1-hook.png'), '-i', os.path.join(OV, 'B3_eticheta-1-8-slow-reps.png'), '-i', os.path.join(OV, 'B3_eticheta-2-20-s-each-side.png'), '-i', os.path.join(OV, 'B3_2-final.png')]
h, l1, l2, fin = n, n + 1, n + 2, n + 3
fc = ';'.join(chains + x) + ';'
fc += "%s[%d:v]overlay=0:0:enable='between(t,0.2,2.8)'[o1];" % (cur, h)
fc += "[o1][%d:v]overlay=333:1440:enable='between(t,2.8,%.2f)'[o2];" % (l1, t_l2 + 0.1)
fc += "[o2][%d:v]overlay=299:1440:enable='gte(t,%.2f)'[o3];" % (l2, t_l2 + 0.1)
fc += "[o3][%d:v]overlay=0:0:enable='gte(t,%.2f)',fade=t=out:st=%.2f:d=0.3[o]" % (fin, total - 3.0, total - 0.3)
cmd = ['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-movflags', '+faststart', out]
subprocess.run(cmd, check=True); print('gata %.1f s -> %s' % (total, out))
