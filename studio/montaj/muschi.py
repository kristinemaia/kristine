#!/usr/bin/env python3
"""Mușchiul care se aprinde (stilul „muscle highlight”): o formă de mușchi, desenată pe corp, care urmărește mișcarea.
Rulezi: python3 studio/montaj/muschi.py <clip.mp4> <ss> <d> <ieșire.mp4> <mușchi.json>
mușchi.json: {"t": 9.5, "color": [255,40,60], "shapes": [[[x,y], ...], ...], "track": [x, y, w, h], "pulse": true}
  t      = secunda (din clip) la care sunt desenate formele
  shapes = poligoane în 1080x1920, fiecare un mușchi (le fac pe rând cu grila de coordonate)
  track  = zona din corp după care se mișcă formele (fluxul optic, cv2)"""
import json, subprocess, sys
import numpy as np, cv2
src, ss, d, out, cfg = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], json.load(open(sys.argv[5]))
W, H = 1080, 1920
def mask_of(shapes):
    m = np.zeros((H, W), np.float32)
    for p in shapes: cv2.fillPoly(m, [np.array(p, np.int32)], 1.0)
    m = cv2.GaussianBlur(m, (0, 0), 7)                                     # margini moi
    # textura de fibră: dungi fine pe direcția mușchiului, ca să nu pară o pată plată
    yy, xx = np.mgrid[0:H, 0:W]; ang = np.deg2rad(cfg.get('fiber', 60))
    stripes = 0.82 + 0.18 * np.sin((xx * np.cos(ang) + yy * np.sin(ang)) / 5.0)
    return m * stripes
base = mask_of(cfg['shapes'])
col = np.array(cfg.get('color', [255, 40, 60])[::-1], np.float32)            # BGR
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(ss), '-t', str(d), '-i', src, '-vf', 'scale=%d:%d' % (W, H), '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H), '-r', '30', '-i', '-',
                        '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
frames = []
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    frames.append(np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy())
n = len(frames); k0 = min(n - 1, max(0, int(round((cfg['t'] - ss) * 30))))
tx, ty, tw, th = cfg['track']
# urmărim zona aleasă cu flux optic, înainte și înapoi față de cadrul de referință
def shift(a, b):
    ga = cv2.cvtColor(a[ty:ty + th, tx:tx + tw], cv2.COLOR_BGR2GRAY); gb = cv2.cvtColor(b[ty:ty + th, tx:tx + tw], cv2.COLOR_BGR2GRAY)
    f = cv2.calcOpticalFlowFarneback(ga, gb, None, 0.5, 3, 25, 3, 5, 1.2, 0)
    return np.median(f[..., 0]), np.median(f[..., 1])
off = [np.zeros(2) for _ in range(n)]
for k in range(k0 + 1, n): off[k] = off[k - 1] + np.array(shift(frames[k - 1], frames[k]))
for k in range(k0 - 1, -1, -1): off[k] = off[k + 1] - np.array(shift(frames[k], frames[k + 1]))
for k, f in enumerate(frames):
    t = k / 30.0
    a = min(1.0, max(0.0, (t - 0.25) / 0.35)) * min(1.0, max(0.0, (d - t) / 0.3))      # apare și dispare lin
    if cfg.get('pulse', True): a *= 0.8 + 0.2 * np.sin(t * 2 * np.pi * 1.2)
    M = np.float32([[1, 0, off[k][0]], [0, 1, off[k][1]]])
    m = cv2.warpAffine(base, M, (W, H))[..., None] * a * cfg.get('opacity', 0.62)
    # culoarea intră ca lumină: amestec „soft light” peste piele/haine, plus o strălucire ușoară
    fl = f.astype(np.float32)
    glow = cv2.GaussianBlur(m, (0, 0), 18)[..., None] if m.ndim == 2 else cv2.GaussianBlur(m[..., 0], (0, 0), 18)[..., None]
    tinted = fl * (1 - m) + (fl * 0.35 + col * 0.65) * m
    tinted = np.clip(tinted + col * glow * 0.25, 0, 255)
    enc.stdin.write(tinted.astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.wait(); print('gata', out, n, 'cadre')
