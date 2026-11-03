#!/usr/bin/env python3
"""Presetul de montaj Kristine Maia (ffmpeg): același aspect curat la toate reel-urile.
Rulezi: python3 studio/montaj/preset.py spec.json <folder cu clipurile> <ieșire.mp4>

Ce face presetul (valorile sunt în PRESET, le schimbi într-un singur loc):
  · 1080 x 1920, 30 fps, fără sunet (muzica o pui tu)
  · dizolvări de 0,3 s între toate cadrele; fade-out de 0,3 s la final
  · aspect curat: contrast +5%, saturație +6%, claritate ușoară (unsharp), lumină +3%; cu "curat":true folosește culoarea din curat.py
  · accent pe esențial: hook în primele 3 s, eticheta doar cât durează mișcarea, codul/final în ultimele 3 s
  · tăieturi scurte: fiecare cadru se oprește înainte de ultimele ~0,3 s din clip

spec.json: {"curat":true (clipuri din curat.py), "hook_dy":0 (mută hook-ul în jos/sus), la segment "blur":[x,y,w,h], "label_d":s, "segments":[{"clip":"IMG_8204","ss":15.2,"d":2.8,"speed":1.0,"crop":null,"label":null}, ...],
            "hook":"Bewit_1-hook.png", "final":"Bewit_2-final.png", "overlay_dir":"brand/reels-overlays/out/Bewit",
            "labels":{"eticheta.png":[x,y]}}"""
import glob, json, os, subprocess, sys
PRESET = dict(td=0.3, fps=30, eq='eq=contrast=1.05:saturation=1.06:brightness=0.02', sharp='unsharp=5:5:0.6:5:5:0.0', hook=(0.2, 2.8), final_len=3.0)
spec = json.load(open(sys.argv[1], encoding='utf-8')); src, out = sys.argv[2], sys.argv[3]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OV = os.path.join(root, spec['overlay_dir'])
def clip(k): return sorted(glob.glob(os.path.join(src, '*' + k + '*.mov')) + glob.glob(os.path.join(src, '*' + k + '*.mp4')))[0]
if spec.get('curat'):  # clipuri trecute deja prin curat.py (culoarea Kristine Maia): fără a doua corecție
    PRESET['eq'], PRESET['sharp'] = 'null', 'null'
inputs, chains, durs, starts = [], [], [], [0.0]
for i, s in enumerate(spec['segments']):
    inputs += ['-ss', str(s['ss']), '-t', str(s['d']), '-i', clip(s['clip'])]
    crop = (s.get('crop') + ',scale=1080:-2:flags=lanczos,pad=1080:1920:0:(1920-ih)/2:color=0xFFF9F6') if s.get('crop') and s.get('frame') else ((s['crop'] + ',scale=1080:1920:flags=lanczos') if s.get('crop') else 'scale=1080:1920:flags=lanczos')
    blur = ''
    if s.get('blur'):  # [x, y, w, h] sau o listă de cutii, în 1080x1920: estompează ceva fix din fundal (logo, reclamă)
        boxes = s['blur'] if isinstance(s['blur'][0], list) else [s['blur']]
        for j, (bx, by, bw, bh) in enumerate(boxes):
            t = '%d_%d' % (i, j)
            r = max(1, min(18, min(bw, bh) // 2 - 1)); rc = max(1, min(r, min(bw, bh) // 4 - 1))   # raza încape în cutiile mici
            blur += ',split[a%s][b%s];[b%s]crop=%d:%d:%d:%d,boxblur=luma_radius=%d:luma_power=2:chroma_radius=%d:chroma_power=2[c%s];[a%s][c%s]overlay=%d:%d' % (t, t, t, bw, bh, bx, by, r, rc, t, t, t, bx, by)
    chains.append('[%d:v]fps=%d,%s,setpts=(PTS-STARTPTS)/%s%s,%s,%s,setsar=1,format=yuv420p[v%d]' % (i, PRESET['fps'], crop, s.get('speed', 1.0), blur, PRESET['eq'], PRESET['sharp'], i))
    durs.append(s['d'] / s.get('speed', 1.0))
n = len(durs); x, acc, cur = [], 0.0, '[v0]'
for j in range(1, n):
    acc += durs[j - 1]; off = acc - j * PRESET['td']; starts.append(off)
    x.append('%s[v%d]xfade=transition=fade:duration=%.2f:offset=%.2f[x%d]' % (cur, j, PRESET['td'], off, j)); cur = '[x%d]' % j
total = sum(durs) - (n - 1) * PRESET['td']
k = n; ov = []
inputs += ['-i', os.path.join(OV, spec['hook'])]; hook_i = k; k += 1
fin_i = k; inputs += ['-i', os.path.join(OV, spec['final'])]; k += 1
fc = ';'.join(chains + x) + ';'
fc += "%s[%d:v]overlay=0:%d:enable='between(t,%.1f,%.1f)'[o0]" % (cur, hook_i, spec.get('hook_dy', 0), *PRESET['hook'])
last = '[o0]'
for idx, s in enumerate(spec['segments']):
    if s.get('label'):
        inputs += ['-i', os.path.join(OV, s['label'])]; li = k; k += 1
        t0 = starts[idx] + (0.1 if idx else PRESET['hook'][1]); t1 = (starts[idx + 1] + 0.1) if idx + 1 < n and spec['segments'][idx + 1].get('label') != s['label'] else (total - PRESET['final_len'] if idx + 1 == n else starts[idx + 1] + 0.1)
        if s.get('label_d'): t1 = starts[idx] + s['label_d']   # eticheta dispare mai devreme (ex.: când te ridici și fața urcă sub ea)
        px, py = s.get('label_pos', [333, 1440])
        fc += ";%s[%d:v]overlay=%d:%d:enable='between(t,%.2f,%.2f)'[l%d]" % (last, li, px, py, t0, t1, idx); last = '[l%d]' % idx
fc += ";%s[%d:v]overlay=0:%d:enable='gte(t,%.2f)',fade=t=out:st=%.2f:d=0.3[o]" % (last, fin_i, spec.get('final_dy', 0), total - PRESET['final_len'], total - 0.3)
amap = ['-an']
if spec.get('audio'):  # păstrează vocea: acrossfade între cadre, curățare ușoară, volum uniform
    ach = ['[%d:a]aresample=48000,asetpts=PTS-STARTPTS,volume=%sdB[a%d]' % (i, spec['segments'][i].get('gain', 0), i) for i in range(n)]
    cur_a = '[a0]'
    for j in range(1, n):
        ach.append('%s[a%d]acrossfade=d=%.2f[ax%d]' % (cur_a, j, PRESET['td'], j)); cur_a = '[ax%d]' % j
    ach.append('%shighpass=f=80,afftdn=nr=10:nf=-40,dynaudnorm=f=200:g=11:p=0.9,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,afade=t=out:st=%.2f:d=0.3[aout]' % (cur_a, total - 0.3))
    fc += ';' + ';'.join(ach); amap = ['-map', '[aout]', '-c:a', 'aac', '-b:a', '160k']
cmd = ['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[o]'] + amap + [ '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-movflags', '+faststart', out]
subprocess.run(cmd, check=True); print('gata %.1f s -> %s' % (total, out))
