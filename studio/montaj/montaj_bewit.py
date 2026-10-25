#!/usr/bin/env python3
"""Montaj Bewit „My evening cacao ritual” (ffmpeg): ~26 s, 1080 x 1920, 30 fps.
Rulezi: python3 studio/montaj/montaj_bewit.py <folder cu clipurile .mov> <ieșire.mp4>
Clipurile: IMG_8192 (laptele), 8193 (condimentele), 8195 (amestecat), 8204 (turnat în cană), 8213 (tu cu cana)."""
import glob, os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
def clip(n): return glob.glob(os.path.join(src, '*IMG_%s.mov' % n))[0]
OV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'brand', 'reels-overlays', 'out', 'Bewit')
# (clip, start, durată în sursă, viteză, filtru suplimentar)
CROP_TU = 'crop=560:996:185:430,scale=1080:1920:flags=lanczos'
SEG = [('8204', 15.2, 2.8, 1.0, ''),      # hook: cana gata
       ('8192', 0.2, 2.4, 1.0, ''),       # laptele în oală
       ('8193', 0.5, 7.2, 2.0, ''),       # condimentele (fără punga cu etichetă)
       ('8195', 2.0, 9.0, 2.0, ''),       # cacaua amestecată
       ('8204', 3.5, 8.2, 1.8, ''),       # turnat în cană (fără ultimele picături)
       ('8213', 4.0, 6.0, 1.0, CROP_TU)]  # tu cu cana
TD = 0.3                                   # durata fiecărei tranziții (dizolvare)
inputs, chains, durs = [], [], []
for i, (n, ss, d, sp, extra) in enumerate(SEG):
    inputs += ['-ss', str(ss), '-t', str(d), '-i', clip(n)]
    f = '[%d:v]fps=30,%ssetpts=(PTS-STARTPTS)/%s,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v%d]' % (i, (extra + ',') if extra else '', sp, i)
    chains.append(f); durs.append(d / sp)
n = len(SEG)
# dizolvări între cadre (xfade); decalajul = suma duratelor anterioare minus tranzițiile deja făcute
x, acc, cur = [], 0.0, '[v0]'
for k in range(1, n):
    acc += durs[k - 1]; off = acc - k * TD
    x.append('%s[v%d]xfade=transition=fade:duration=%.2f:offset=%.2f[x%d]' % (cur, k, TD, off, k)); cur = '[x%d]' % k
total = sum(durs) - (n - 1) * TD
inputs += ['-i', os.path.join(OV, 'Bewit_1-hook.png'), '-i', os.path.join(OV, 'Bewit_2-final.png')]
fc = ';'.join(chains + x) + ';'
fc += "%s[%d:v]overlay=0:0:enable='between(t,0.2,2.5)'[o1];[o1][%d:v]overlay=0:0:enable='gte(t,%.2f)',fade=t=out:st=%.2f:d=0.3[o]" % (cur, n, n + 1, total - 3.2, total - 0.3)
cmd = ['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-movflags', '+faststart', out]
subprocess.run(cmd, check=True); print('gata %.1f s -> %s' % (total, out))
