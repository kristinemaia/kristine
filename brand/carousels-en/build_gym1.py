#!/usr/bin/env python3
"""Carusel EN „2 moves for your next gym day” (G-C1), același șablon ca build_en.py, 4 slide-uri.
Pozele: src/gym-lunge.jpg, src/gym-cobra.jpg (de la ședința foto de la sală, cu acordul fotografului).
Rulezi: python3 brand/carousels-en/build_gym1.py -> out/EN-G1-gym-day-*.png"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__file__': os.path.join(HERE, 'build_en.py')}
exec(open(ns['__file__'], encoding='utf-8').read().split('\ndef main():')[0], ns)  # CSS, img(), blobs(), bullets(), JS
img, blobs, bullets, E, CSS, JS = ns['img'], ns['blobs'], ns['bullets'], ns['E'], ns['CSS'], ns['JS']
DISC = 'General exercise, not medical advice. Stop if anything feels sharp.'
T = 4
def frame(n, inner, k, a='var(--pink)', b='var(--lilac)'):
    return '<div class="s" id="s">%s<div class="tag">KRISTINE MAIA</div><div class="num">%d/%d</div>%s</div>' % (blobs(k, a, b), n, T, inner)
lunge, cobra = img('gym-lunge.jpg'), img('gym-cobra.jpg')
def slides():
    s = []
    s.append(frame(1, '<div style="position:absolute;left:80px;right:80px;top:170px"><h1 style="font-size:104px">Sit all day? 2 moves for your next gym day</h1></div>'
        '<div class="card" style="left:150px;top:610px;width:780px;height:660px"><img src="%s" style="object-position:center 30%%"></div>' % lunge, 1))
    s.append(frame(2, '<div style="position:absolute;left:80px;right:80px;top:170px"><h2>1 · Dumbbell lunge</h2>%s</div>'
        '<div class="card" style="left:240px;top:580px;width:600px;height:660px"><img src="%s" style="object-position:center 25%%"></div><div class="foot">%s</div>'
        % (bullets(['Long step back, chest tall', 'Back knee hovers, never slams', '3 sets of 8 per leg']), lunge, DISC), 2, 'var(--blue)', 'var(--mint)'))
    s.append(frame(3, '<div style="position:absolute;left:80px;right:80px;top:170px"><h2>2 · Cobra, to undo the chair</h2>%s</div>'
        '<div class="card" style="left:80px;top:740px;width:920px;height:500px"><img src="%s" style="object-position:30%% center"></div><div class="foot">%s</div>'
        % (bullets(['Hips stay on the mat', 'Shoulders down, away from ears', '5 slow breaths, only as high as feels easy']), cobra, DISC), 3, 'var(--lilac)', 'var(--pink)'))
    s.append(frame(4, '<div style="position:absolute;left:80px;right:80px;top:230px"><h1 style="font-size:100px">Save this for your next gym day</h1>'
        '<p style="font-size:44px;font-weight:600;margin:40px 0 60px;line-height:1.3">And send it to the friend who sits all day.</p>'
        '<div class="btn">Free 5-minute desk stretch · link in bio</div></div>'
        '<div class="card" style="left:340px;top:820px;width:400px;height:400px;border-radius:50%%"><img src="%s" style="object-position:center 30%%"></div>' % img('gym-window.jpg'), 4, 'var(--mint)', 'var(--blue)'))
    return s
if __name__ == '__main__':
    import json, subprocess, tempfile
    OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
    head = '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700&display=swap" rel="stylesheet"><style>%s</style></head><body>' % CSS
    jobs = [(os.path.join(OUT, 'EN-G1-gym-day-%d.png' % n), head + inner + '</body></html>') for n, inner in enumerate(slides(), 1)]
    jf = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(jobs, jf); jf.close()
    jsf = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False); jsf.write(JS); jsf.close()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf.name, jf.name], check=True, env=env); os.unlink(jsf.name); os.unlink(jf.name)
    print('gata:', len(jobs), 'imagini')
