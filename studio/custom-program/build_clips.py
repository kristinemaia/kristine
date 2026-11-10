#!/usr/bin/env python3
"""Clipurile exercițiilor pentru Custom Program: curățate (culoarea Kristine Maia), tăiate și cu numele exercițiului.
Rulezi: python3 studio/custom-program/build_clips.py [nume ...]
Intrare: studio/custom-program/clips/<nume>.mov   Ieșire: studio/custom-program/out/<nume>.mp4 (1080x1920, fără sunet)"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'montaj')); import curat
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC, OUT = os.path.join(ROOT, 'studio/custom-program/clips'), os.path.join(ROOT, 'studio/custom-program/out')
CUR = os.path.join(ROOT, 'studio/montaj/_curat'); FONTS = os.path.join(ROOT, 'brand/reels-overlays/fonts')
INK, CREAM, WINE = (43, 36, 49), (255, 249, 246), (138, 52, 89)
# nume: (titlu EN, eticheta mică, început s, sfârșit s sau None = până la final - 0,4 s)
#   la final poate avea și un 'crop=...' (în pixeli 1080x1920, raport 9:16), ca să scoți ceva de la margine
#   sau (titlu, eticheta, [(început, sfârșit), ...]) = păstrează doar bucățile astea, legate cu o dizolvare scurtă (ex.: tai întoarcerea între picioare)
CLIPS = {
    'incalzire-coarda':                   ('Jump rope', 'Warm-up', 0.4, None),
    'incalzire-cercuri-brate':            ('Arm circles', 'Warm-up · forward & back', 0.3, None),
    'incalzire-cercuri-sold':             ('Hip circles', 'Warm-up · both ways', 0.3, None),
    'mobilitate-cat-cow-v2':              ('Cat-cow', 'Mobility', 0.3, None),   # refilmat 3 nov, din lateral (v1 din față rămâne doar în G2)
    'mobilitate-open-book-v2a':           ('Open book', 'Mobility · first side', 0.3, None),   # refilmat 3 nov, cu fața la cameră
    'mobilitate-open-book-v2b':           ('Open book', 'Mobility · other side', 0.3, None),
    'mobilitate-worlds-greatest-stretch': ("World's greatest stretch", 'Mobility · each side', 0.4, None),
    'mobilitate-90-90-v2':                ('90/90 hip switch', 'Mobility', 7.0, None),
    'mobilitate-flexori-sold':            ('Kneeling hip flexor stretch', 'Mobility · each side', 0.4, None),
    'mobilitate-childs-pose':             ("Child's pose reach", 'Mobility', 0.4, None),
    'mobilitate-deep-squat-hold':         ('Deep squat hold', 'Mobility', 0.4, None),
    'incalzire-leg-swings':               ('Leg swings', 'Warm-up · front & back · each leg', [(0.2, 4.0), (6.2, 9.5)]),
    'incalzire-leg-swings-lateral':       ('Lateral leg swings', 'Warm-up · side to side · each leg', [(0.2, 7.3), (9.3, 13.6)]),
    'incalzire-gambe':                    ('Calf & hamstring stretch', 'Warm-up · toes up · each leg', [(0.2, 3.9), (5.9, 7.7)]),
    'incalzire-gambe-2':                  ('Calf & hamstring stretch', 'Warm-up · other leg', [(0.6, 3.9), (5.6, 7.7)]),
    'incalzire-respiratie':               ('Reset breathing', 'Warm-up · arms up as you breathe in', 0.3, None),
    'picioare-genuflexiune':              ('Bodyweight squat', 'Legs 1', 0.3, None),
    'picioare-goblet-a':                  ('Goblet squat', 'Legs 1 · dumbbell at your chest', 0.3, None),
    'picioare-goblet-b':                  ('Dumbbell sumo squat', 'Legs · variation', 0.3, None),
    'picioare-fandare-inainte':           ('Forward lunge', 'Legs 1 · alternate legs', 0.3, None),
    'picioare-fandare-inapoi':            ('Reverse lunge', 'Legs 1 · alternate legs', 0.3, None),
    'picioare-split-a':                   ('Split squat', 'Legs 1 · first leg', 0.3, None),
    'picioare-split-b':                   ('Split squat', 'Legs 1 · other leg', 3.0, None),
    'picioare-varfuri':                   ('Calf raises', 'Legs 1 · hand on the wall', 0.3, None, 'crop=1000:1778:20:0'),
    'picioare-wall-sit':                  ('Wall sit', 'Legs 1 · hold', 0.2, None, 'crop=1000:1778:20:0'),
    # joi 5 nov: spate + core
    'spate-face-pull':                    ('Face pull', 'Back · rope to your face, elbows high', 0.3, None),
    'spate-lat-pulldown':                 ('Lat pulldown', 'Back · bar to your upper chest', 0.3, None),
    'spate-lat-pulldown-b':               ('Lat pulldown', 'Back · slight lean back', 0.3, None),
    'core-plank':                         ('Plank', 'Core · hold, body in one line', 0.3, None),
    'core-plank-leg-lift':                ('Plank with leg lift', 'Core · alternate legs', 0.3, None),
    'mobilitate-cobra':                   ('Cobra stretch', 'Mobility · chest up, hips down', 0.3, None),
    'core-bird-dog':                      ('Bird dog', 'Core · opposite arm and leg', 0.3, None),
    'core-plank-lateral':                 ('Side plank', 'Core · hold, then switch sides', 0.2, None),
    # vineri 6 nov: gât, încheieturi, glute bridge
    'gat-lateral':                        ('Neck side stretch', 'Neck · ear toward shoulder, both sides', 0.3, None),
    'gat-chin-tucks':                     ('Chin tucks', 'Neck · slide your chin straight back', 0.3, None),
    'gat-chin-tucks-sezut':               ('Chin tucks', 'Neck · seated, slide your chin straight back', 0.2, None),   # din profil, mai clar
    'gat-semicercuri':                    ('Neck half circles', 'Neck · slow, no full circles', 0.3, None),
    'incheieturi-palma-jos':              ('Wrist stretch, palm down', 'Wrists · 15 s each hand', 0.3, None),
    'incheieturi-palma-sus':              ('Wrist stretch, palm up', 'Wrists · 15 s each hand', 0.3, None),
    'incheieturi-cercuri':                ('Wrist circles', 'Wrists · both ways', 0.3, None),
    'picioare-glute-bridge':              ('Glute bridge', 'Legs · squeeze at the top', 0.3, None),
    'core-dead-bug':                      ('Dead bug', 'Core · low back stays down', 0.3, None),
    'core-high-plank':                    ('High plank', 'Core · hands under shoulders', 0.3, None),
    'core-tabletop-crunch':               ('Tabletop crunch', 'Core · legs up, slow', 0.3, None),
    'core-russian-twist':                 ('Russian twist', 'Core · lean back, rotate', 0.3, None),
    'spate-swimmers':                     ('Prone swimmers', 'Back · arms sweep low and slow', 0.3, None),
    'spate-ramat-gantera':                ('One-arm dumbbell row', 'Back · elbow to your hip, each side', 0.3, None),
    'impins-flotare-inclinata':           ('Incline push-up', 'Push · hands on a bench', 0.3, None),
    'mobilitate-open-book-v3a':           ('Open book', 'Mobility · first side', 0.3, None),   # refilmat 6 nov
    'mobilitate-open-book-v3b':           ('Open book', 'Mobility · other side', 0.3, None),
    'picioare-hip-thrust':                ('Hip thrust', 'Legs · upper back on a bench, squeeze at the top', 0.3, None),
    'picioare-rdl':                       ('Romanian deadlift', 'Legs · hips back, dumbbells close to your legs', 0.3, None),
    'spate-fluturari-inverse':            ('Reverse fly', 'Back · hinge forward, arms wide', 0.3, None),
    'impins-umeri-gantere':               ('Seated shoulder press', 'Push · dumbbells up, ribs down', 0.3, None),
    'brate-biceps-curl':                  ('Biceps curl', 'Arms · elbows by your sides', 0.3, None),
    'umeri-ridicari-laterale':            ('Lateral raise', 'Shoulders · elbows soft, to shoulder height', 0.3, None),
    'mobilitate-triceps':                 ('Triceps stretch', 'Mobility · 20 s each arm', 0.3, None),
    'cardio-spinning':                    ('Spin bike', 'Cardio · seat at hip height', 0.3, None),
    'cardio-bicicleta-spatar':            ('Recumbent bike', 'Cardio · easy on knees and back', 0.3, None),
    'cardio-banda':                       ('Incline walk', 'Cardio · don\'t hold the rails', 0.3, None),
    # marți 10 nov: alternativele la coardă, ce lipsea și câteva în plus
    'incalzire-mars-pe-loc':              ('March in place', 'Warm-up · knees high, no jumping', 0.3, None),
    'incalzire-step-jack':                ('Step jacks', 'Warm-up · jumping jacks without the jump', 0.3, None),
    'incalzire-jumping-jacks':            ('Jumping jacks', 'Warm-up · light and quick', 0.3, None),
    'incalzire-inchworm':                 ('Inchworm', 'Warm-up · walk out to a plank and back', 0.3, None),
    'mobilitate-extensie-toracica':       ('Thoracic extension on a bench', 'Mobility · elbows on the bench, chest down', 0.3, None),
    'mobilitate-rasucire-sezut':          ('Seated spinal twist', 'Mobility · each side, sit tall', 0.3, None),
    'impins-flotare':                     ('Push-up', 'Push · body in one line', 0.3, None),
    'core-hollow-hold':                   ('Hollow hold', 'Core · low back pressed down', 0.2, None),
    'cardio-skaters':                     ('Skaters', 'Cardio · side to side, reach to the floor', 0.3, None),
}
def eticheta(titlu, mic, path):
    """pastila cu numele: crem cu margine vișinie, jos în stânga, pe podea (sus îți acoperea fața la exercițiile din picioare)"""
    fb, fm = ImageFont.truetype(os.path.join(FONTS, 'Poppins-SemiBold.ttf'), 54), ImageFont.truetype(os.path.join(FONTS, 'Poppins-Medium.ttf'), 32)
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = max(d.textlength(titlu, font=fb), d.textlength(mic.upper(), font=fm)) + 84; h = 160; x, y = 60, 1660
    d.rounded_rectangle([x + 6, y + 8, x + w + 6, y + h + 8], 34, fill=(0, 0, 0, 60))            # umbră discretă
    d.rounded_rectangle([x, y, x + w, y + h], 34, fill=CREAM + (240,), outline=WINE, width=5)
    d.text((x + 42, y + 22), mic.upper(), font=fm, fill=WINE)
    d.text((x + 42, y + 62), titlu, font=fb, fill=INK)
    im.save(path)
def construieste(nume):
    titlu, mic, *rest = CLIPS[nume]; crop = rest.pop() if isinstance(rest[-1], str) else None; os.makedirs(CUR, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    c = os.path.join(CUR, nume + '.mp4')
    if not os.path.exists(c): curat.ruleaza(os.path.join(SRC, nume + '.mov'), c)
    segs = rest[0] if isinstance(rest[0], list) else [(rest[0], rest[1] if rest[1] is not None else curat.dur(c) - 0.4)]
    td = 0.25; n = len(segs); d = sum(b - a for a, b in segs) - (n - 1) * td
    png = os.path.join(CUR, nume + '-eticheta.png'); eticheta(titlu, mic, png)
    fc = '[0:v]%ssplit=%d%s;' % ((crop + ',scale=1080:1920:flags=lanczos,setsar=1,') if crop else '', n, ''.join('[s%d]' % i for i in range(n)))
    fc += ';'.join('[s%d]trim=%.2f:%.2f,setpts=PTS-STARTPTS[t%d]' % (i, a, b, i) for i, (a, b) in enumerate(segs))
    cur, acc = '[t0]', 0.0
    for j in range(1, n):
        acc += segs[j - 1][1] - segs[j - 1][0]
        fc += ';%s[t%d]xfade=transition=fade:duration=%.2f:offset=%.2f[x%d]' % (cur, j, td, acc - j * td, j); cur = '[x%d]' % j
    fc += (";%sfade=t=in:st=0:d=0.25,fade=t=out:st=%.2f:d=0.3[v];"
           "[1:v]format=rgba,fade=t=in:st=0.3:d=0.35:alpha=1[e];[v][e]overlay=0:0:shortest=1,format=yuv420p[o]") % (cur, d - 0.3)
    out = os.path.join(OUT, nume + '.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', c, '-loop', '1', '-t', '%.2f' % d, '-i', png,
                    '-filter_complex', fc, '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-movflags', '+faststart', out], check=True)
    print('gata %-36s %.1f s' % (nume, d))
if __name__ == '__main__':
    for n in (sys.argv[1:] or CLIPS): construieste(n)
