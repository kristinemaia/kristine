#!/usr/bin/env python3
"""Mușchiul care se aprinde (stilul „muscle highlight”): o formă de mușchi, desenată pe corp, care urmărește mișcarea.
Rulezi: python3 studio/montaj/muschi.py <clip.mp4> <ss> <d> <ieșire.mp4> <mușchi.json>
mușchi.json: {"t": 9.5, "color": [255,40,60], "shapes": [[[x,y], ...], ...], "track": [x, y, w, h], "on": [[0.2, 1.5]]}
  t      = secunda (din clip) la care sunt desenate formele
  shapes = poligoane în 1080x1920, fiecare un mușchi (le fac pe rând cu grila de coordonate)
  track  = zona din corp după care se mișcă formele (fluxul optic, cv2)"""
import json, subprocess, sys
import numpy as np, cv2
src, ss, d, out, cfg = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], json.load(open(sys.argv[5]))
W, H = 1080, 1920
def chaikin(p, it=3):
    """colțuri rotunjite: poligonul devine o formă organică, de mușchi"""
    p = np.array(p, np.float32)
    for _ in range(it):
        q = np.roll(p, -1, 0); p = np.stack([0.75 * p + 0.25 * q, 0.25 * p + 0.75 * q], 1).reshape(-1, 2)
    return p
def mask_of(shapes):
    """fiecare mușchi: formă netedă, margine clară, mai luminos la mijloc, cu fibre pe direcția lui și un contur fin"""
    fill = np.zeros((H, W), np.float32); rim = np.zeros((H, W), np.float32)
    fibers = cfg.get('fibers') or [cfg.get('fiber', 60)] * len(shapes)
    yy, xx = np.mgrid[0:H, 0:W]
    for p, ang in zip(shapes, fibers):
        poly = chaikin(p).astype(np.int32)
        m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [poly], 255)
        dist = cv2.distanceTransform(m, cv2.DIST_L2, 5); dn = dist / max(1.0, dist.max())
        a_ = np.deg2rad(ang)
        fib = 0.86 + 0.14 * np.sin((xx * np.cos(a_) + yy * np.sin(a_)) / 3.2)        # fibre fine
        shade = (0.55 + 0.45 * np.sqrt(dn)) * fib                                     # volum: mijlocul mai aprins
        fill = np.maximum(fill, (m > 0) * shade)
        r = np.zeros((H, W), np.uint8); cv2.polylines(r, [poly], True, 255, 3, cv2.LINE_AA)
        rim = np.maximum(rim, r.astype(np.float32) / 255)
    fill = cv2.GaussianBlur(fill, (0, 0), 2.2)
    return fill, cv2.GaussianBlur(rim, (0, 0), 1.2)
base, rimb = None, None  # se calculează după ce citim cadrele (avem nevoie de cadrul de referință)
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
base, rimb = mask_of(cfg['shapes'])
def body_clip(img, shapes):
    """GrabCut: separă corpul de fundal în jurul formelor; păstrăm din forme doar partea de pe corp"""
    gc = np.full((H, W), cv2.GC_BGD, np.uint8)
    allp = np.concatenate([np.array(p) for p in shapes]); x0, y0 = allp.min(0) - 80; x1, y1 = allp.max(0) + 80
    x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(W - 1, x1), min(H - 1, y1)
    gc[y0:y1, x0:x1] = cv2.GC_PR_BGD
    for p in shapes:
        m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [chaikin(p).astype(np.int32)], 1)
        gc[m > 0] = cv2.GC_PR_FGD
        core = cv2.erode(m, np.ones((25, 25), np.uint8)); gc[core > 0] = cv2.GC_FGD
    bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(img, gc, None, bg, fg, 4, cv2.GC_INIT_WITH_MASK)
    body = np.where((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD), 1.0, 0.0).astype(np.float32)
    body = cv2.morphologyEx(body, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    return cv2.GaussianBlur(body, (0, 0), 2.0)
if cfg.get('clip_body', True):
    bc = body_clip(frames[k0], cfg['shapes']); base = base * bc; rimb = rimb * bc
# urmărim zona aleasă: puncte pe corp urmărite cadru cu cadru (Lucas-Kanade) → mutare, rotire și mărime
def step(a, b):
    ga = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY); gb = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    roi = np.zeros_like(ga); roi[ty:ty + th, tx:tx + tw] = 255
    pts = cv2.goodFeaturesToTrack(ga, 150, 0.01, 6, mask=roi)
    if pts is None or len(pts) < 6: return np.float32([[1, 0, 0], [0, 1, 0]])
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(ga, gb, pts, None, winSize=(31, 31), maxLevel=3)
    ok = st.ravel() == 1
    if ok.sum() < 6: return np.float32([[1, 0, 0], [0, 1, 0]])
    M, _ = cv2.estimateAffinePartial2D(pts[ok], nxt[ok], method=cv2.RANSAC, ransacReprojThreshold=3)
    return M.astype(np.float32) if M is not None else np.float32([[1, 0, 0], [0, 1, 0]])
def cat(A, B):  # aplică întâi A, apoi B
    A3 = np.vstack([A, [0, 0, 1]]); B3 = np.vstack([B, [0, 0, 1]]); return (B3 @ A3)[:2].astype(np.float32)
def inv(A): return cv2.invertAffineTransform(A)
T = [np.float32([[1, 0, 0], [0, 1, 0]]) for _ in range(n)]
for k in range(k0 + 1, n): T[k] = cat(T[k - 1], step(frames[k - 1], frames[k]))
for k in range(k0 - 1, -1, -1): T[k] = cat(T[k + 1], inv(step(frames[k], frames[k + 1])))
for k, f in enumerate(frames):
    t = k / 30.0
    # lumina apare doar în ferestrele „on” (secunde de la începutul bucății), de ex. cât brațele sunt întinse și nu acoperă spatele
    a = 0.0
    for t0, t1 in cfg.get('on', [[0.25, d - 0.3]]):
        if t0 <= t <= t1:
            u = (t - t0) / max(0.01, t1 - t0)
            a = max(a, min(1.0, (t - t0) / 0.25, (t1 - t) / 0.25) * (0.75 + 0.25 * np.sin(np.pi * u)))   # un singur puls, lin
    if a <= 0.001: enc.stdin.write(f.tobytes()); continue
    m = cv2.warpAffine(base, T[k], (W, H)) * a * cfg.get('opacity', 0.7)
    rm = cv2.warpAffine(rimb, T[k], (W, H)) * a
    fl = f.astype(np.float32)
    # culoarea păstrează luminile și umbrele de sub ea (cutele hainei, forma corpului): ca o lumină din interiorul mușchiului
    lum = (0.114 * fl[..., 0] + 0.587 * fl[..., 1] + 0.299 * fl[..., 2])[..., None] / 255.0
    colored = col * (0.25 + 1.05 * lum)
    mm = m[..., None]
    out_f = fl * (1 - mm) + colored * mm
    glow = cv2.GaussianBlur(m, (0, 0), 16)[..., None]
    out_f = out_f + col * (glow * 0.35 + rm[..., None] * cfg.get('rim', 0.18))
    tinted = np.clip(out_f, 0, 255)
    enc.stdin.write(tinted.astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.wait(); print('gata', out, n, 'cadre')
