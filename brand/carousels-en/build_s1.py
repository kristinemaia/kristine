#!/usr/bin/env python3
"""Carusel EN „Save this: full-body gym workout for people who sit all day” (S1, formatul „Save this workout”, modelul Senada Greca), același șablon ca build_en.py, 6 slide-uri.
Pozele: src/mirror-jacket.jpg (selfie la oglindă, 16 nov, fără alți oameni în cadru) și cadrele din filmările programului (wk-*.jpg, gym-lunge.jpg).
Rulezi: python3 brand/carousels-en/build_s1.py -> out/EN-S1-save-this-workout-*.png"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__file__': os.path.join(HERE, 'build_en.py')}
exec(open(ns['__file__'], encoding='utf-8').read().split('\ndef main():')[0], ns)  # CSS, img(), blobs(), bullets(), JS
img, blobs, bullets, E, CSS, JS = ns['img'], ns['blobs'], ns['bullets'], ns['E'], ns['CSS'], ns['JS']
DISC = 'General exercise, not medical advice. Rest 60–90 s between sets.'
T = 6
def frame(n, inner, k, a='var(--pink)', b='var(--lilac)'):
    return '<div class="s" id="s">%s<div class="tag">KRISTINE MAIA</div><div class="num">%d/%d</div>%s</div>' % (blobs(k, a, b), n, T, inner)
def sets(rows):
    return ''.join('<div style="display:flex;justify-content:space-between;align-items:center;background:#fff;border-radius:28px;padding:22px 34px;margin:0 0 18px;font-size:40px;font-weight:700">'
                   '<span>%s</span><span style="color:var(--wine)">%s</span></div>' % (E(a), E(b)) for a, b in rows)
def part(n, title, rows, photos, k, a, b):
    photos = [p if isinstance(p, tuple) else (p, 'center 30%') for p in photos]
    if len(photos) == 1:
        pics = '<div class="card" style="left:190px;top:760px;width:700px;height:500px"><img src="%s" style="object-position:%s"></div>' % (img(photos[0][0]), photos[0][1])
    else:
        pics = ''.join('<div class="card" style="left:%dpx;top:760px;width:440px;height:500px;border-radius:36px"><img src="%s" style="object-position:%s"></div>' % (x, img(p), pos)
                       for x, (p, pos) in zip((80, 560), photos))
    return frame(n, '<div style="position:absolute;left:80px;right:80px;top:150px"><h2 style="margin-bottom:34px">%s</h2>%s</div>%s<div class="foot">%s</div>'
                 % (E(title), sets(rows), pics, DISC), k, a, b)
def slides():
    s = []
    s.append(frame(1, '<div style="position:absolute;left:80px;right:80px;top:150px"><h1 style="font-size:92px">Sit all day? Save this full-body gym workout</h1>'
        '<p style="font-size:42px;font-weight:600;margin:26px 0 0">45 min · 4 parts · beginner friendly</p></div>'
        '<div class="card" style="left:220px;top:560px;width:640px;height:700px"><img src="%s" style="object-position:center 35%%"></div>' % img('mirror-jacket.jpg'), 1))
    s.append(part(2, '1 · Warm-up, 5 min', [('March or jumping jacks', '1 min'), ("World's greatest stretch", '5 / side'), ('Cat-cow', '8 slow')],
                  [('wk-mobilitate-worlds-greatest-stretch.jpg', 'center 85%')], 2, 'var(--blue)', 'var(--mint)'))
    s.append(part(3, '2 · Legs', [('Goblet squat', '3 × 10'), ('Dumbbell lunge', '3 × 8 / side')],
                  ['wk-picioare-goblet-a.jpg', 'gym-lunge.jpg'], 3, 'var(--lilac)', 'var(--pink)'))
    s.append(part(4, '3 · Back & posture', [('Lat pulldown', '3 × 10'), ('Seated cable row', '3 × 12'), ('Face pull', '2 × 15')],
                  ['wk-spate-lat-pulldown.jpg'], 4, 'var(--mint)', 'var(--blue)'))
    s.append(part(5, '4 · Core', [('Side plank', '3 × 20 s / side'), ('Dead bug', '3 × 8 / side')],
                  [('wk-core-plank-lateral.jpg', 'center 90%')], 5, 'var(--pink)', 'var(--lilac)'))
    s.append(frame(6, '<div style="position:absolute;left:80px;right:80px;top:260px"><h1 style="font-size:96px">Want one built for you?</h1>'
        '<p style="font-size:44px;font-weight:600;margin:36px 0 0;line-height:1.3">Your goal, your time, home or gym. A 2-minute quiz builds your plan.</p>'
        '<p style="font-size:46px;font-weight:700;margin:36px 0 70px;color:var(--wine)">Custom Program · opening soon</p>'
        '<div class="btn">Join the waitlist · link in bio</div>'
        '<p style="font-size:38px;font-weight:600;margin:60px 0 0;color:var(--muted)">Save this for your next gym day 🔖</p></div>', 6, 'var(--blue)', 'var(--mint)'))
    return s
if __name__ == '__main__':
    import json, subprocess, tempfile
    OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
    head = '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700&display=swap" rel="stylesheet"><style>%s</style></head><body>' % CSS
    jobs = [(os.path.join(OUT, 'EN-S1-save-this-workout-%d.png' % n), head + inner + '</body></html>') for n, inner in enumerate(slides(), 1)]
    jf = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(jobs, jf); jf.close()
    jsf = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False); jsf.write(JS); jsf.close()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf.name, jf.name], check=True, env=env); os.unlink(jsf.name); os.unlink(jf.name)
    print('gata:', len(jobs), 'imagini')
