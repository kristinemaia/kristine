#!/usr/bin/env python3
"""Intro de stream, varianta dinamică (1920 x 1080, ~14 s, fără sunet; muzica o pui în OBS).
  0–1,8 s   3 · 2 · 1 (cifrele „lovesc” ecranul)
  1,8–7,8 s 10 tăieturi rapide (0,6 s) din clipurile de la sală, cu zoom la fiecare și flash alb pe tăietură,
            cuvintele mari GAMING. → GYM. → STRETCH BREAKS. pe margini
  7,8–14 s  flash, apoi „KRISTINE MAIA · LIVE NOW” pe vișiniu, cu zoom lent
Rulezi: python3 brand/twitch/build_intro_v2.py → brand/twitch/stream/stream-intro-dinamic.mp4"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_stream_videos as B
L, ff, ENC, CUR, OUT = B.L, B.ff, B.ENC, B.CUR, B.OUT
CUT = 0.6
# (clip curat, secunda de start) · se schimbă la fiecare 0,6 s
MONTAGE = [('gaming-1', 3.0), ('gaming-1', 6.0),                                          # GAMING. (stream, pauza de stretch)
           ('mus-G4-2', 1.0), ('mus-G3-2', 0.3), ('picioare-goblet-a', 2.2),            # GYM.
           ('DR-7953', 7.0), ('incalzire-coarda', 3.0), ('DR-7953', 13.0),                    # JUMPING.
           ('cook-1', 1.0), ('cook-2', 2.0), ('cook-3', 1.4), ('cook-4', 9.0),                 # COOKING.
           ('mobilitate-worlds-greatest-stretch', 6.0), ('G2-b', 5.0)]                         # STRETCH BREAKS.
# (cuvânt, de la tăietura, până la)
WORDS = [('GAMING.', 0, 2), ('GYM.', 2, 5), ('JUMPING.', 5, 8), ('COOKING.', 8, 12), ('STRETCH', 12, 13), ('BREAKS.', 13, 14)]

def layers():
    num = lambda n: ('<div class="s" style="display:grid;place-items:center"><h1 style="font-size:620px;color:#fff;line-height:1">%s</h1></div>' % n)
    pages = [(L('cd_%s.png' % n), num(n)) for n in '321']
    for i, (w, a, b) in enumerate(WORDS):
        side = 'left:70px' if i % 2 == 0 else 'right:70px'
        pages.append((L('word_%d.png' % i),
            '<div class="s"><h1 style="position:absolute;%s;top:50%%;transform:translateY(-50%%);font-size:%dpx;color:#fff;'
            'text-shadow:0 10px 40px rgba(0,0,0,.45);max-width:620px;line-height:.9">%s</h1></div>' % (side, 170 if len(w) < 8 else 140, w)))
    pages.append((L('title_v2.png'),
        '<div class="s" style="background:#8A3459">'
        '<div class="b" style="width:900px;height:900px;background:#A2456C;right:-280px;top:-400px"></div>'
        '<div class="b" style="width:700px;height:700px;background:#6F2747;left:-260px;bottom:-360px"></div>'
        '<div style="position:absolute;left:0;right:0;top:220px;text-align:center;color:#fff">'
        '<span class="pill" style="background:#FFF9F6;color:#8A3459;font-size:44px;padding:16px 44px;letter-spacing:.08em">● LIVE NOW</span>'
        '<h1 style="font-size:250px;margin-top:40px;color:#fff">Kristine Maia</h1>'
        '<p style="font-size:56px;font-weight:800;margin:30px 0 0;letter-spacing:.02em">GAMING · GYM · COOKING · STRETCH BREAKS</p>'
        '<p style="font-size:40px;font-weight:600;margin:28px 0 0;opacity:.9">Grab water. Sit tall. Let\'s go.</p></div></div>'))
    B.render(pages)

def seg_countdown():
    parts = []
    for n in '321':
        p = L('v2_cd_%s.mp4' % n)
        ff(['-f', 'lavfi', '-i', 'color=c=0x2B2431:s=1920x1080:d=0.6:r=30', '-loop', '1', '-t', '0.6', '-i', L('cd_%s.png' % n),
            '-filter_complex', "[1:v]format=rgba,zoompan=z='1.5-0.5*min(on/7\\,1)':d=1:s=1920x1080:fps=30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[t];[0:v][t]overlay=0:0,format=yuv420p[o]",
            '-map', '[o]', '-t', '0.6'] + B.ENC + [p]); parts.append(p)
    return parts

def seg_cut(i, name, ss):
    p = L('v2_cut_%d.mp4' % i); n = int(CUT * 30)
    fc = ("[0:v]setpts=PTS-STARTPTS,split[a][b];"
          "[a]scale=1920:-2,crop=1920:1080,boxblur=28:2,eq=brightness=-0.22:saturation=1.15[bg];"
          "[b]scale=608:1080,zoompan=z='1.14-0.14*min(on/%d\\,1)':d=1:s=608x1080:fps=30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[fg];"
          "[bg][fg]overlay=656:0,drawbox=x=0:y=0:w=iw:h=ih:color=white@0.55:t=fill:enable='lt(t\\,0.07)',format=yuv420p[o]" % (n - 4))
    ff(['-ss', str(ss), '-t', str(CUT), '-i', os.path.join(CUR, name + '.mp4'), '-filter_complex', fc, '-map', '[o]', '-t', str(CUT)] + ENC + [p])
    return p

def seg_title():
    p = L('v2_title.mp4'); D = 6.2
    ff(['-loop', '1', '-t', str(D), '-i', L('title_v2.png'),
        '-filter_complex', "[0:v]format=rgba,zoompan=z='1+0.05*on/%d':d=1:s=1920x1080:fps=30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',fade=t=in:st=0:d=0.35:color=white,format=yuv420p[o]" % int(D * 30),
        '-map', '[o]', '-t', str(D)] + ENC + [p])
    return p

def main():
    layers()
    parts = seg_countdown()
    cuts = [seg_cut(i, n, ss) for i, (n, ss) in enumerate(MONTAGE)]
    # montajul + cuvintele mari
    lst = L('v2_cuts.txt'); open(lst, 'w').write(''.join("file '%s'\n" % c for c in cuts))
    mont = L('v2_montage_raw.mp4'); ff(['-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', mont])
    inp = ['-i', mont]; fc = []; cur = '[0:v]'
    for i, (w, a, b) in enumerate(WORDS):
        inp += ['-loop', '1', '-t', str(len(MONTAGE) * CUT), '-i', L('word_%d.png' % i)]
        t0, t1 = a * CUT, b * CUT
        # cuvântul intră din lateral, rapid
        dx = -120 if i % 2 == 0 else 120
        fc.append("%s[%d:v]overlay=x='%d*max(0\\,1-(t-%.2f)/0.18)':y=0:enable='between(t\\,%.2f\\,%.2f)'[w%d]" % (cur, i + 1, dx, t0, t0, t1, i)); cur = '[w%d]' % i
    fc.append('%sformat=yuv420p[o]' % cur)
    mont2 = L('v2_montage.mp4'); ff(inp + ['-filter_complex', ';'.join(fc), '-map', '[o]'] + ENC + [mont2])
    parts += [mont2, seg_title()]
    lst = L('v2_all.txt'); open(lst, 'w').write(''.join("file '%s'\n" % c for c in parts))
    out = os.path.join(OUT, 'stream-intro-dinamic.mp4')
    ff(['-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out])
    print(out, '%.1f MB' % (os.path.getsize(out) / 1e6))

if __name__ == '__main__':
    main()
