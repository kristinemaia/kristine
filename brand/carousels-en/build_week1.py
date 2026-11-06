#!/usr/bin/env python3
"""Carusel EN „This week I filmed my whole program” (W1, anunțul lansării Custom Program), același șablon ca build_en.py, 5 slide-uri.
Pozele (câte una pe slide): src/gym-window-wide.jpg, gym-lunge.jpg, gym-cobra.jpg, gym-rope-smile.jpg (de la ședința foto de la sală, cu acordul fotografului).
Rulezi: python3 brand/carousels-en/build_week1.py -> out/EN-W1-filmed-program-*.png"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__file__': os.path.join(HERE, 'build_en.py')}
exec(open(ns['__file__'], encoding='utf-8').read().split('\ndef main():')[0], ns)  # CSS, img(), blobs(), bullets(), JS
img, blobs, bullets, E, CSS, JS = ns['img'], ns['blobs'], ns['bullets'], ns['E'], ns['CSS'], ns['JS']
T = 5
def frame(n, inner, k, a='var(--pink)', b='var(--lilac)'):
    return '<div class="s" id="s">%s<div class="tag">KRISTINE MAIA</div><div class="num">%d/%d</div>%s</div>' % (blobs(k, a, b), n, T, inner)
def tile(name, label, x, y):
    return ('<div class="card" style="left:%dpx;top:%dpx;width:440px;height:470px;border-radius:36px"><img src="%s" style="object-position:center 30%%"></div>'
            '<div style="position:absolute;left:%dpx;top:%dpx;background:#fff;border-radius:999px;padding:10px 26px;font-size:30px;font-weight:700">%s</div>'
            % (x, y, img(name), x + 20, y + 400, label))
def slides():
    s = []
    s.append(frame(1, '<div style="position:absolute;left:80px;right:80px;top:160px"><h1 style="font-size:96px">This week I filmed my whole program</h1>'
        '<p style="font-size:42px;font-weight:600;margin:28px 0 0">40+ exercises, all in the gym</p></div>'
        '<div class="card" style="left:200px;top:590px;width:680px;height:690px"><img src="%s" style="object-position:center 22%%"></div>' % img('wk-side.jpg'), 1))
    s.append(frame(2, '<div style="position:absolute;left:80px;right:80px;top:170px"><h2>Filmed by me, for people who sit all day</h2>%s</div>'
        '<div class="card" style="left:240px;top:640px;width:600px;height:640px"><img src="%s" style="object-position:center 20%%"></div>'
        % (bullets(['Every move with a home version', 'Short, follow-along videos']), img('wk-front-walk.jpg')), 2, 'var(--blue)', 'var(--mint)'))
    s.append(frame(3, '<div style="position:absolute;left:80px;right:80px;top:150px"><h2>Legs, back, core, mobility</h2></div>'
        + tile('wk-picioare-goblet-a.jpg', 'Legs', 80, 300) + tile('wk-spate-lat-pulldown.jpg', 'Back', 560, 300)
        + tile('wk-core-plank-lateral.jpg', 'Core', 80, 810) + tile('wk-mobilitate-worlds-greatest-stretch.jpg', 'Mobility', 560, 810), 3, 'var(--lilac)', 'var(--pink)'))
    s.append(frame(4, '<div style="position:absolute;left:80px;right:80px;top:170px"><h2>Your plan is built from your answers</h2>%s</div>'
        '<div class="card" style="left:240px;top:700px;width:600px;height:580px"><img src="%s" style="object-position:center 18%%"></div>'
        % (bullets(['Your goal, your time, home or gym', 'A 2-minute quiz builds it']), img('wk-front-hip.jpg')), 4, 'var(--mint)', 'var(--blue)'))
    s.append(frame(5, '<div style="position:absolute;left:80px;right:80px;top:300px"><h1 style="font-size:100px">Your custom program</h1>'
        '<p style="font-size:48px;font-weight:700;margin:36px 0 0;color:var(--wine)">Launching 16 November</p>'
        '<p style="font-size:40px;font-weight:600;margin:30px 0 70px;line-height:1.3">Take the 2-minute quiz and get your plan.</p>'
        '<div class="btn">kristinemaia.com · link in bio</div></div>', 5, 'var(--pink)', 'var(--lilac)'))
    return s
if __name__ == '__main__':
    import json, subprocess, tempfile
    OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
    head = '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700&display=swap" rel="stylesheet"><style>%s</style></head><body>' % CSS
    jobs = [(os.path.join(OUT, 'EN-W1-filmed-program-%d.png' % n), head + inner + '</body></html>') for n, inner in enumerate(slides(), 1)]
    jf = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(jobs, jf); jf.close()
    jsf = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False); jsf.write(JS); jsf.close()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf.name, jf.name], check=True, env=env); os.unlink(jsf.name); os.unlink(jf.name)
    print('gata:', len(jobs), 'imagini')
