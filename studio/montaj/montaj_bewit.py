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
SEG = [('8204', 15.2, 3.0, 1.0, ''),      # hook: cana gata
       ('8192', 0.2, 2.6, 1.0, ''),       # laptele în oală
       ('8193', 0.5, 8.0, 2.0, ''),       # condimentele (fără punga cu etichetă)
       ('8195', 2.0, 10.0, 2.0, ''),      # cacaua amestecată
       ('8204', 3.5, 8.8, 1.8, ''),      # turnat în cană
       ('8213', 4.0, 6.0, 1.0, CROP_TU)]  # tu cu cana
inputs, chains, labels, total = [], [], [], 0.0
for i, (n, ss, d, sp, extra) in enumerate(SEG):
    inputs += ['-ss', str(ss), '-t', str(d), '-i', clip(n)]
    f = '[%d:v]fps=30,%ssetpts=(PTS-STARTPTS)/%s,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v%d]' % (i, (extra + ',') if extra else '', sp, i)
    chains.append(f); labels.append('[v%d]' % i); total += d / sp
n = len(SEG)
inputs += ['-i', os.path.join(OV, 'Bewit_1-hook.png'), '-i', os.path.join(OV, 'Bewit_2-final.png')]
fc = ';'.join(chains) + ';' + ''.join(labels) + 'concat=n=%d:v=1:a=0[c];' % n
fc += '[c][%d:v]overlay=0:0:enable=\'between(t,0.2,2.8)\'[o1];[o1][%d:v]overlay=0:0:enable=\'gte(t,%.2f)\',fade=t=out:st=%.2f:d=0.3[o]' % (n, n + 1, total - 3.4, total - 0.3)
cmd = ['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-movflags', '+faststart', out]
subprocess.run(cmd, check=True); print('gata %.1f s -> %s' % (total, out))
