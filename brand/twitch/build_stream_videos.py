#!/usr/bin/env python3
"""Videourile pentru stream (1920 x 1080, 30 fps, fără sunet, pentru OBS → Media Source):
  intro   (15 s): clipurile de la sală urcă pe rând, apoi „Kristine Maia · stream starting”
  pauză   (2 min): „Stretch break: stretch with me”, 6 mișcări × 20 s, cu numărătoare și bară de progres
  outro   (20 s, se poate pune pe repeat): „Thanks for hanging out” + unde mă găsești

Rulezi: python3 brand/twitch/build_stream_videos.py      → brand/twitch/stream/*.mp4
Clipurile vin din studio/montaj/_curat (culoarea Kristine Maia, fără etichete). Textele: Bricolage + Figtree, ca pe site.
În OBS: Sources → + → Media Source → fișierul; bifezi „Loop” la pauză și outro (și la intro, dacă îl folosești ca „Starting soon”)."""
import json, os, subprocess, tempfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
CUR = os.path.join(ROOT, 'studio/montaj/_curat')
OUT = os.path.join(ROOT, 'brand/twitch/stream'); TMP = os.path.join(OUT, '_layers')
os.makedirs(TMP, exist_ok=True)
FONT = os.path.join(ROOT, 'brand/reels-overlays/fonts/Poppins-Bold.ttf')
CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--blue:#DDE9F7;--mint:#D8F0E4;--lilac:#E9E1F7}
*{box-sizing:border-box}html,body{margin:0;background:transparent}
.s{width:1920px;height:1080px;position:relative;overflow:hidden;color:var(--ink);font-family:Figtree,sans-serif}
.b{position:absolute;border-radius:50%}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.035em;margin:0;line-height:.95}
.pill{display:inline-block;border-radius:999px;font-weight:700;white-space:nowrap}
"""
HEAD = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800'
        '&family=Figtree:wght@500;600;700;800&display=swap" rel="stylesheet"><style>' + CSS + '</style></head><body>')
BG = ('<div class="s" style="background:var(--bg)">'
      '<div class="b" style="width:900px;height:900px;background:var(--lilac);right:-260px;top:-380px"></div>'
      '<div class="b" style="width:760px;height:760px;background:var(--pink);left:-300px;bottom:-380px"></div>'
      '<div class="b" style="width:420px;height:420px;background:var(--mint);right:120px;bottom:-190px"></div></div>')
SOCIAL = 'Instagram · TikTok @kristinemaia11'

def render(pages):
    """pages: [(fișier, html_body)] → PNG-uri transparente 1920x1080 (fonturile de pe Google, ca la ecranul offline)"""
    js = r"""
const { chromium } = require('playwright'); const fs = require('fs');
(async () => { const items = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const it of items) { await p.setContent(it.html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(150); await p.screenshot({ path: it.file, omitBackground: true }); }
  await b.close(); })();"""
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
        json.dump([{'file': f, 'html': HEAD + h + '</body></html>'} for f, h in pages], jf); sf.write(js)
    subprocess.run(['node', sf.name, jf.name], check=True, cwd='/tmp')
    os.unlink(jf.name); os.unlink(sf.name)

def L(name): return os.path.join(TMP, name)
def ff(args): subprocess.run(['ffmpeg', '-v', 'error', '-y'] + args, check=True)
ENC = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', '-an']

def panel_mask(w, h, r):
    """masca cu colțuri rotunjite pentru clipuri (alb = se vede)"""
    from PIL import Image, ImageDraw
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    p = L('mask_%dx%d.png' % (w, h)); m.save(p); return p

def clip_in(name, ss, d):
    return ['-stream_loop', '-1', '-ss', str(ss), '-t', str(d), '-i', os.path.join(CUR, name + '.mp4')]

# ---------------------------------------------------------------- straturile de text
def layers():
    pages = [(L('bg.png'), BG)]
    # intro: titlul (centrat), apare după clipuri
    pages.append((L('intro_title.png'),
        '<div class="s"><div style="position:absolute;left:0;right:0;top:250px;text-align:center">'
        '<span class="pill" style="background:var(--berry);color:#fff;font-size:38px;padding:14px 36px;letter-spacing:.06em">STREAM STARTING</span>'
        '<h1 style="font-size:210px;margin-top:40px">Kristine Maia</h1>'
        '<p style="font-size:56px;font-weight:700;margin:34px 0 0">Gaming, gym &amp; a stretch break every 30 minutes</p>'
        '<p style="margin:44px 0 0"><span class="pill" style="background:var(--ink);color:#fff;font-size:36px;padding:18px 38px">Grab water. Sit tall. We start in a minute.</span></p>'
        '</div></div>'))
    # pauza: cardul din dreapta, câte unul pentru fiecare mișcare
    for i, (name, ss, title, cue) in enumerate(MOVES, 1):
        nxt = MOVES[i][2] if i < len(MOVES) else 'Back to the game'
        pages.append((L('break_%d.png' % i),
            '<div class="s"><div style="position:absolute;left:820px;right:110px;top:120px">'
            '<span class="pill" style="background:var(--berry);color:#fff;font-size:32px;padding:12px 30px;letter-spacing:.06em">STRETCH BREAK · %d/%d</span>' % (i, len(MOVES)) +
            '<p style="font-size:40px;font-weight:700;margin:34px 0 0;color:var(--muted)">Stretch with me. Back in 2 minutes.</p>'
            '<h1 style="font-size:128px;margin-top:26px">%s</h1>' % title +
            '<p style="font-size:44px;font-weight:600;margin:30px 0 0;line-height:1.25;max-width:900px">%s</p>' % cue +
            '</div>'
            '<div style="position:absolute;left:820px;bottom:118px;font-size:34px;font-weight:700;color:var(--muted)">Next: <span style="color:var(--ink)">%s</span></div>' % nxt +
            '<div style="position:absolute;right:110px;bottom:118px;font-size:30px;font-weight:700;color:var(--muted)">kristinemaia.com</div>'
            '</div>'))
    # outro
    pages.append((L('outro_text.png'),
        '<div class="s"><div style="position:absolute;left:880px;right:100px;top:150px">'
        '<span class="pill" style="background:var(--berry);color:#fff;font-size:34px;padding:12px 32px;letter-spacing:.06em">THANKS FOR HANGING OUT</span>'
        '<h1 style="font-size:150px;margin-top:36px">See you next stream</h1>'
        '<p style="font-size:46px;font-weight:700;margin:34px 0 0">Mon · Wed · Fri. Stand up and stretch before you go.</p>'
        '<div style="display:flex;flex-direction:column;gap:22px;margin-top:56px;align-items:flex-start">'
        '<span class="pill" style="background:var(--ink);color:#fff;font-size:36px;padding:18px 36px">' + SOCIAL + '</span>'
        '<span class="pill" style="background:#fff;border:3px solid #EADFE6;font-size:36px;padding:16px 34px">Free 5-minute desk stretch: kristinemaia.com</span>'
        '<span class="pill" style="background:#fff;border:3px solid #EADFE6;font-size:36px;padding:16px 34px">Your custom program: take the quiz on the site</span>'
        '</div></div></div>'))
    render(pages)

# mișcările din pauză: (clip curat, început, titlu, indicație) · 20 s fiecare
MOVES = [
    ('incalzire-respiratie', 0.3, 'Reset breathing', 'Arms up as you breathe in, down as you breathe out. Slow.'),
    ('incalzire-cercuri-brate', 0.3, 'Arm circles', 'Big, slow circles. Forward first, then back.'),
    ('incalzire-cercuri-sold', 0.3, 'Hip circles', 'Hands on hips, slow circles both ways.'),
    ('incalzire-gambe', 0.2, 'Calf & hamstring stretch', 'Heel down, toes up, hinge forward. Switch legs at 10.'),
    ('incalzire-leg-swings', 0.2, 'Leg swings', 'Hold the wall, swing front to back. Switch legs at 10.'),
    ('mobilitate-deep-squat-hold', 0.4, 'Deep squat hold', 'Heels down, chest up. Hold the chair if you need to.'),
]
SEG = 20.0

# ---------------------------------------------------------------- intro
def intro():
    W, H, Y = 480, 854, 113; mask = panel_mask(W, H, 44)
    clips = [('incalzire-coarda', 2.0), ('picioare-goblet-a', 1.0), ('mobilitate-worlds-greatest-stretch', 1.0)]
    xs = [150, 720, 1290]; D = 15.0
    inp = ['-loop', '1', '-t', str(D), '-i', L('bg.png'), '-loop', '1', '-t', str(D), '-i', mask, '-loop', '1', '-t', str(D), '-i', L('intro_title.png')]
    for n, ss in clips: inp += clip_in(n, ss, D)
    fc = ['[0:v]format=rgba[bg]', '[1:v]format=gray,split=3[m0][m1][m2]', '[2:v]format=rgba,fade=t=in:st=6.6:d=0.7:alpha=1[title]']
    cur = '[bg]'
    for i in range(3):
        d0 = 0.15 + 0.3 * i
        fc.append('[%d:v]scale=%d:%d,setsar=1,format=rgba[c%d];[c%d][m%d]alphamerge,fade=t=out:st=6.2:d=0.6:alpha=1[p%d]' % (3 + i, W, H, i, i, i, i))
        fc.append("%s[p%d]overlay=x=%d:y='%d+1080*pow(max(0,1-(t-%.2f)/0.7),3)'[o%d]" % (cur, i, xs[i], Y, d0, i)); cur = '[o%d]' % i
    fc.append("%s[title]overlay=x=0:y='40*pow(max(0,1-(t-6.6)/0.8),2)',format=yuv420p[out]" % cur)
    ff(inp + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-t', str(D)] + ENC + [os.path.join(OUT, 'stream-intro.mp4')])

# ---------------------------------------------------------------- pauza
def pauza():
    W, H = 540, 960; mask = panel_mask(W, H, 44); parts = []
    for i, (name, ss, title, cue) in enumerate(MOVES, 1):
        seg = L('break_seg_%d.mp4' % i)
        inp = ['-loop', '1', '-t', str(SEG), '-i', L('bg.png'), '-loop', '1', '-t', str(SEG), '-i', mask,
               '-loop', '1', '-t', str(SEG), '-i', L('break_%d.png' % i)] + clip_in(name, ss, SEG)
        fc = ['[0:v]format=rgba[bg]', '[1:v]format=gray[m]',
              '[3:v]scale=%d:%d,setsar=1,format=rgba[c];[c][m]alphamerge[p]' % (W, H),
              '[bg][p]overlay=150:60[a]', '[a][2:v]overlay=0:0[b]',
              # bara de progres: se umple în 20 s
              'color=c=0xEDE2EA:s=980x22:d=%g[tr];color=c=0x8A3459:s=980x22:d=%g[br];[tr][br]overlay=x=\'-980+980*t/%g\':y=0[pb]' % (SEG, SEG, SEG),
              '[b][pb]overlay=820:830[c2]',
              # numărătoarea mare, în dreapta jos
              "[c2]drawtext=fontfile=%s:text='%%{eif\\:max(1\\,%d-floor(t))\\:d}':fontsize=170:fontcolor=0x8A3459:x=1810-tw:y=600,format=yuv420p[out]" % (FONT, int(SEG))]
        ff(inp + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-t', str(SEG)] + ENC + [seg]); parts.append(seg)
    lst = L('break_list.txt'); open(lst, 'w').write(''.join("file '%s'\n" % p for p in parts))
    ff(['-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', os.path.join(OUT, 'stream-pauza-stretch.mp4')])

# ---------------------------------------------------------------- outro
def outro():
    W, H = 340, 604; mask = panel_mask(W, H, 36); D = 20.0
    clips = [('incalzire-coarda', 4.0), ('mobilitate-worlds-greatest-stretch', 6.0)]
    inp = ['-loop', '1', '-t', str(D), '-i', L('bg.png'), '-loop', '1', '-t', str(D), '-i', mask, '-loop', '1', '-t', str(D), '-i', L('outro_text.png')]
    for n, ss in clips: inp += clip_in(n, ss, D)
    fc = ['[0:v]format=rgba[bg]', '[1:v]format=gray,split=2[m0][m1]',
          '[3:v]scale=%d:%d,setsar=1,format=rgba[c0];[c0][m0]alphamerge[p0]' % (W, H),
          '[4:v]scale=%d:%d,setsar=1,format=rgba[c1];[c1][m1]alphamerge[p1]' % (W, H),
          '[bg][p0]overlay=120:238[a]', '[a][p1]overlay=490:178[b]',
          "[2:v]format=rgba,fade=t=in:st=0.2:d=0.6:alpha=1[t]", "[b][t]overlay=0:0,format=yuv420p[out]"]
    ff(inp + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-t', str(D)] + ENC + [os.path.join(OUT, 'stream-outro.mp4')])

if __name__ == '__main__':
    layers(); intro(); pauza(); outro()
    for f in sorted(os.listdir(OUT)):
        if f.endswith('.mp4'): print('%-28s %6.1f MB' % (f, os.path.getsize(os.path.join(OUT, f)) / 1e6))
