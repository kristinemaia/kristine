#!/usr/bin/env python3
"""„Starting soon” cu numărătoare inversă (1920 x 1080, fără sunet), pentru primele minute de stream:
în stânga, clipurile (sală, coardă, gătit, stretching) se schimbă la 4 s; în dreapta, ceasul mare de la 15:00 (sau 12:00) la 00:00,
apoi „Let's go!”. În OBS: Media Source, fără Loop, cu „Restart playback when source becomes active”.
Rulezi: python3 brand/twitch/build_starting_soon.py [minute ...]   (implicit 15 și 12)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_stream_videos as B
L, ff, CUR, OUT = B.L, B.ff, B.CUR, B.OUT
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reels-overlays', 'fonts', 'Poppins-Bold.ttf')
LOOP = [('DR-7953', 3.0), ('mus-G4-2', 0.5), ('cook-4', 8.0), ('incalzire-coarda', 2.0), ('mobilitate-worlds-greatest-stretch', 4.0),
        ('cook-3', 0.5), ('picioare-goblet-a', 1.0), ('G2-b', 4.5), ('cook-1', 1.0), ('mus-G3-2', 0.2)]
STEP, XF = 4.0, 0.5
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'stillimage', '-crf', '26', '-pix_fmt', 'yuv420p', '-r', '25', '-g', '120', '-movflags', '+faststart', '-an']

def layers():
    B.render([(L('soon_text.png'),
        '<div class="s"><div style="position:absolute;left:820px;right:110px;top:110px">'
        '<span class="pill" style="background:var(--berry);color:#fff;font-size:36px;padding:14px 36px;letter-spacing:.07em">STARTING SOON</span>'
        '<h1 style="font-size:150px;margin-top:34px">Kristine Maia</h1>'
        '<p style="font-size:44px;font-weight:700;margin:26px 0 0;line-height:1.25">Gaming, gym, cooking &amp; a stretch break every 30 minutes</p>'
        '<p style="font-size:34px;font-weight:600;margin:22px 0 0;color:var(--muted)">Grab water. We go live at zero.</p>'
        '</div>'
        '<div style="position:absolute;left:820px;bottom:96px;display:flex;gap:18px">'
        '<span class="pill" style="background:var(--ink);color:#fff;font-size:30px;padding:14px 30px">' + B.SOCIAL + '</span>'
        '<span class="pill" style="background:#fff;border:3px solid #EADFE6;font-size:30px;padding:12px 28px">kristinemaia.com</span></div>'
        '</div>'),
        (L('soon_go.png'),
        '<div class="s"><div style="position:absolute;left:820px;top:610px"><h1 style="font-size:200px;color:var(--berry)">Let\'s go!</h1></div></div>')])

def panel_loop():
    """clipurile din stânga, 540x960 cu colțuri rotunjite, ~40 s, se repetă fără tăietură vizibilă"""
    W, H = 540, 960; mask = B.panel_mask(W, H, 44); n = len(LOOP)
    inp, fc = [], []
    for i, (name, ss) in enumerate(LOOP):
        inp += B.clip_in(name, ss, STEP + XF)
        fc.append('[%d:v]scale=%d:%d,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[c%d]' % (i, W, H, i))
    cur = '[c0]'
    for j in range(1, n):
        fc.append('%s[c%d]xfade=transition=fade:duration=%.2f:offset=%.2f[x%d]' % (cur, j, XF, j * STEP, j))   # fiecare clip: 4 s + 0,5 s de trecere
        cur = '[x%d]' % j
    inp += ['-loop', '1', '-i', mask]
    fc.append('[%d:v]format=gray[m];%sformat=rgba[cv];[cv][m]alphamerge[o]' % (n, cur))
    out = L('soon_panel.mov')
    ff(inp + ['-filter_complex', ';'.join(fc), '-map', '[o]', '-t', '%.2f' % (n * STEP), '-c:v', 'qtrle', out])
    return out

def build(minutes, panel):
    T = minutes * 60; D = T + 6
    clock = "%%{eif\\:floor(max(0\\,%d-t)/60)\\:d\\:2}\\:%%{eif\\:mod(floor(max(0\\,%d-t))\\,60)\\:d\\:2}" % (T, T)
    fc = ['[0:v]format=rgba[bg]', '[bg][1:v]overlay=150:60[a]', '[a][2:v]overlay=0:0[b]',
          "[b]drawtext=fontfile=%s:text='%s':fontsize=230:fontcolor=0x2B2431:x=820:y=600:enable='lt(t\\,%d)'[c]" % (FONT, clock, T),
          "[c][3:v]overlay=0:0:enable='gte(t\\,%d)',format=yuv420p[out]" % T]
    out = os.path.join(OUT, 'stream-starting-soon-%dmin.mp4' % minutes)
    ff(['-loop', '1', '-t', str(D), '-i', L('bg.png'), '-stream_loop', '-1', '-t', str(D), '-i', panel,
        '-loop', '1', '-t', str(D), '-i', L('soon_text.png'), '-loop', '1', '-t', str(D), '-i', L('soon_go.png'),
        '-filter_complex', ';'.join(fc), '-map', '[out]', '-t', str(D)] + ENC + [out])
    print(out, '%.0f MB' % (os.path.getsize(out) / 1e6))

if __name__ == '__main__':
    mins = [int(a) for a in sys.argv[1:]] or [15, 12]
    layers(); p = panel_loop()
    for m in mins: build(m, p)
