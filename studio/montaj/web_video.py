#!/usr/bin/env python3
"""Versiunile ușoare pentru site: clipurile din Custom Program și reel-urile din ghidurile de formă.
Rulezi: python3 studio/montaj/web_video.py   →  website/assets/video/<nume>.mp4 + <nume>.jpg (coperta)
540 x 960 (reel-urile din ghiduri 720 x 1280), fără sunet, mici (~1 MB), pornesc repede (faststart)."""
import os, subprocess
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(ROOT, 'website/assets/video')
PROG = os.path.join(ROOT, 'studio/custom-program/out'); REEL = os.path.join(ROOT, 'studio/montaj/out-g')
# (sursa, nume pe site, lățime, secunda pentru copertă)
LIST = [(os.path.join(PROG, n + '.mp4'), n, 540, 1.5) for n in [
    'incalzire-coarda', 'incalzire-cercuri-brate', 'incalzire-cercuri-sold', 'incalzire-leg-swings', 'incalzire-leg-swings-lateral',
    'incalzire-gambe', 'incalzire-respiratie',
    'mobilitate-cat-cow-v2', 'mobilitate-open-book-v2a', 'mobilitate-worlds-greatest-stretch', 'mobilitate-90-90-v2',
    'mobilitate-flexori-sold', 'mobilitate-childs-pose', 'mobilitate-deep-squat-hold',
    'picioare-genuflexiune', 'picioare-goblet-a', 'picioare-goblet-b', 'picioare-fandare-inapoi', 'picioare-fandare-inainte',
    'picioare-split-a', 'picioare-varfuri', 'picioare-wall-sit',
    'spate-face-pull', 'spate-lat-pulldown', 'core-plank', 'core-plank-leg-lift', 'core-bird-dog', 'mobilitate-cobra']] + [
    (os.path.join(REEL, 'G4-Squat.mp4'), 'ghid-squat', 720, 4.0),
    (os.path.join(REEL, 'G3-Form.mp4'), 'ghid-cable-row', 720, 4.0),
    (os.path.join(REEL, 'G6-Hang.mp4'), 'ghid-hang', 720, 4.0)]
os.makedirs(OUT, exist_ok=True)
for src, name, w, t in LIST:
    h = w * 16 // 9; mp4 = os.path.join(OUT, name + '.mp4'); jpg = os.path.join(OUT, name + '.jpg')
    if not os.path.exists(mp4) or os.path.getmtime(mp4) < os.path.getmtime(src):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', 'scale=%d:%d:flags=lanczos,format=yuv420p' % (w, h), '-an',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '29', '-profile:v', 'main', '-movflags', '+faststart', mp4], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', src, '-frames:v', '1', '-vf', 'scale=%d:%d' % (w, h), '-q:v', '6', jpg], check=True)
    print('%-36s %5.0f KB' % (name, os.path.getsize(mp4) / 1024))
