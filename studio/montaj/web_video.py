#!/usr/bin/env python3
"""Versiunile ușoare pentru site: clipurile din Custom Program și reel-urile din ghidurile de formă.
Rulezi: python3 studio/montaj/web_video.py   →  website/assets/video/<nume>.mp4 + <nume>.jpg (coperta)
540 x 960 (reel-urile din ghiduri 720 x 1280), fără sunet, mici (~1 MB), pornesc repede (faststart)."""
import os, subprocess
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(ROOT, 'studio/custom-program/web')        # toate clipurile, ușoare (pentru Payhip și previzualizări)
SITE = os.path.join(ROOT, 'website/assets/video')           # pe site ajung doar previzualizarea și ghidurile
PROG = os.path.join(ROOT, 'studio/custom-program/out'); REEL = os.path.join(ROOT, 'studio/montaj/out-g')
# (sursa, nume pe site, lățime, secunda pentru copertă)
LIST = [(os.path.join(PROG, n + '.mp4'), n, 540, 1.5) for n in [
    'incalzire-coarda', 'incalzire-cercuri-brate', 'incalzire-cercuri-sold', 'incalzire-leg-swings', 'incalzire-leg-swings-lateral',
    'incalzire-gambe', 'incalzire-respiratie',
    'mobilitate-cat-cow-v2', 'mobilitate-open-book-v3a', 'mobilitate-worlds-greatest-stretch', 'mobilitate-90-90-v2',
    'mobilitate-flexori-sold', 'mobilitate-childs-pose', 'mobilitate-deep-squat-hold',
    'picioare-genuflexiune', 'picioare-goblet-a', 'picioare-goblet-b', 'picioare-fandare-inapoi', 'picioare-fandare-inainte',
    'picioare-split-a', 'picioare-varfuri', 'picioare-wall-sit',
    'spate-face-pull', 'spate-lat-pulldown', 'core-plank', 'core-plank-leg-lift', 'core-bird-dog', 'core-plank-lateral', 'mobilitate-cobra',
    'gat-lateral', 'gat-chin-tucks-sezut', 'gat-semicercuri', 'incheieturi-palma-jos', 'incheieturi-palma-sus', 'incheieturi-cercuri',
    'picioare-glute-bridge', 'picioare-hip-thrust', 'picioare-rdl', 'core-dead-bug', 'core-high-plank', 'core-tabletop-crunch', 'core-russian-twist',
    'spate-swimmers', 'spate-ramat-gantera', 'spate-fluturari-inverse', 'impins-flotare-inclinata', 'impins-umeri-gantere',
    'umeri-ridicari-laterale', 'brate-biceps-curl', 'mobilitate-triceps', 'cardio-spinning', 'cardio-bicicleta-spatar', 'cardio-banda']] + [
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
# site-ul: doar clipurile din PREVIEW (website/build_site.py) și ghidurile de formă; restul se șterge din folderul site-ului
import re, shutil
pv = set(re.findall(r'\("([a-z0-9-]+)", "[^"]+", "[^"]+"\)', open(os.path.join(ROOT, 'website/build_site.py'), encoding='utf-8').read()))
keep = pv | {n for _, n, _, _ in LIST if n.startswith('ghid-')}
os.makedirs(SITE, exist_ok=True)
for f in os.listdir(SITE):
    if f.rsplit('.', 1)[0] not in keep: os.remove(os.path.join(SITE, f))
for n in keep:
    for ext in ('mp4', 'jpg'):
        src = os.path.join(OUT, n + '.' + ext)
        if os.path.exists(src): shutil.copy2(src, os.path.join(SITE, n + '.' + ext))
print('pe site:', len(keep), 'clipuri')
