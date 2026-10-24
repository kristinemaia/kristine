#!/usr/bin/env python3
"""Carusele pentru Kristine Maia (engleză, șablonul A: cald, roz-lila), 1080 x 1350, 5 slide-uri fiecare.
C1: Why your neck hurts after 4 hours of gaming (23 oct) · C2: 3 things I do after every stream (8 nov).
Rulezi: python3 brand/carousels-en/build_en.py -> out/EN-C1-*.png, out/EN-C2-*.png + EN-carusele.zip
Poza cu cana de cacao: pune src/cacao.jpg (pătrat) și rulezi din nou; până atunci slide-ul 4 din C2 are o ilustrație."""
import base64, html, json, os, subprocess, tempfile, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'src'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
def img(name):
    p = os.path.join(SRC, name)
    if not os.path.exists(p): return None
    mime = 'image/png' if name.endswith('.png') else 'image/jpeg'
    return 'data:%s;base64,%s' % (mime, base64.b64encode(open(p, 'rb').read()).decode())
DISC = 'General mobility, not medical advice. Gentle pull only. Stop if it\'s sharp.'
CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--pink:#F8DCE6;--blue:#DDE9F7;--mint:#D8F0E4;--lilac:#E9E1F7;--wine:#8A3459;--muted:#6B6073}
*{box-sizing:border-box}body{margin:0}
.s{position:relative;overflow:hidden;width:1080px;height:1350px;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif}
.blob{position:absolute;border-radius:50%}
.tag{position:absolute;left:80px;top:68px;font-weight:700;font-size:28px;color:var(--wine);letter-spacing:.05em}
.num{position:absolute;right:80px;top:68px;font-weight:700;font-size:28px;color:var(--muted)}
h1,h2{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.03em;margin:0;color:var(--ink)}
h1{line-height:1.02}h2{font-size:78px;line-height:1.05;margin-bottom:44px}
ul{margin:0;padding:0;list-style:none}li{font-size:46px;line-height:1.3;margin-bottom:34px;padding-left:58px;position:relative;font-weight:600}
li:before{content:'';position:absolute;left:0;top:17px;width:24px;height:24px;border-radius:50%;background:var(--wine)}
.foot{position:absolute;left:80px;right:80px;bottom:56px;font-size:26px;color:var(--muted);line-height:1.4}
.card{position:absolute;border-radius:44px;overflow:hidden;box-shadow:0 14px 40px rgba(43,36,49,.14)}
.card img{width:100%;height:100%;object-fit:cover;display:block}
.pill{display:inline-block;background:#fff;border-radius:999px;padding:10px 26px;font-size:30px;font-weight:700;color:var(--wine);margin-left:14px;vertical-align:middle}
.btn{display:inline-block;background:var(--wine);color:#fff;font-weight:700;font-size:44px;border-radius:999px;padding:28px 56px}
"""
def blobs(k, a, b):
    s = [('width:720px;height:720px;right:-240px;bottom:-230px;background:%s' % a), ('width:420px;height:420px;left:-150px;top:520px;background:%s;opacity:.7' % b)] if k % 2 else [('width:640px;height:640px;left:-230px;top:-210px;background:%s' % a), ('width:380px;height:380px;right:-130px;bottom:-110px;background:%s;opacity:.7' % b)]
    return ''.join('<div class="blob" style="%s"></div>' % x for x in s)
def frame(n, inner, k, a='var(--pink)', b='var(--lilac)'):
    return '<div class="s" id="s">%s<div class="tag">KRISTINE MAIA</div><div class="num">%d/5</div>%s</div>' % (blobs(k, a, b), n, inner)
E = html.escape
def bullets(items): return '<ul>' + ''.join('<li>%s</li>' % E(t) for t in items) + '</ul>'
def mid(n, head, items, k, a='var(--pink)', b='var(--lilac)', photo=None, pos='center 40%'):
    card = '<div class="card" style="left:190px;top:740px;width:700px;height:520px"><img src="%s" style="object-position:%s"></div>' % (photo, pos) if photo else ''
    return frame(n, '<div style="position:absolute;left:80px;right:80px;top:200px"><h2>%s</h2>%s</div>%s<div class="foot">%s</div>' % (E(head), bullets(items), card, DISC), k, a, b)
def cta(n, k, extra=''):
    p = img('poster-prev.png')
    return frame(n, '<div style="position:absolute;left:80px;right:80px;top:190px"><h1 style="font-size:96px">Free 5-minute desk stretch</h1><p style="font-size:42px;font-weight:600;margin:36px 0 44px;line-height:1.3">Neck, shoulders, wrists and hips. One chair, no equipment.</p><div class="btn">Link in bio</div></div>'
                 '<div class="card" style="left:290px;top:690px;width:500px;height:640px;border-radius:30px"><img src="%s" style="object-position:top"></div>' % p, k, 'var(--mint)', 'var(--blue)')
def c1():
    s = []
    s.append(frame(1, '<div style="position:absolute;left:80px;right:80px;top:300px"><h1 style="font-size:116px">Why your neck hurts after 4 hours of gaming</h1><p style="font-size:42px;color:var(--muted);margin-top:50px;font-weight:600">And 3 small things that help →</p></div>', 1))
    s.append(mid(2, 'What\'s happening', ['Your head drifts forward as you focus on the screen.', 'Your shoulders round toward it.', 'Your neck muscles work the whole session to hold your head up.'], 2, photo=img('portrait2.jpg'), pos='center 12%'))
    s.append(mid(3, 'Why gaming makes it worse', ['You\'re focused, so you forget to move.', 'The screen sits a little too low.', 'One position for hours, with no break.'], 3, 'var(--blue)', 'var(--mint)', photo=img('hips.jpg'), pos='center 12%'))
    n, sh = img('neck.jpg'), img('shoulders.jpg')
    s.append(frame(4, '<div style="position:absolute;left:80px;right:80px;top:170px"><h2 style="margin-bottom:0">3 small fixes</h2></div>'
        '<div class="card" style="left:80px;top:330px;width:440px;height:440px"><img src="%s"></div><div class="card" style="left:560px;top:330px;width:440px;height:440px"><img src="%s"></div>'
        '<div style="position:absolute;left:80px;top:800px;width:440px;font-size:40px;font-weight:700;line-height:1.2">1 · Chin tucks<span style="display:block;font-size:32px;font-weight:600;color:var(--muted);margin-top:8px">Glide your chin straight back. 8 slow reps.</span></div>'
        '<div style="position:absolute;left:560px;top:800px;width:440px;font-size:40px;font-weight:700;line-height:1.2">2 · Shoulder blade squeeze<span style="display:block;font-size:32px;font-weight:600;color:var(--muted);margin-top:8px">Back and down, hold 3 seconds. 8 reps.</span></div>'
        '<div style="position:absolute;left:80px;right:80px;top:1060px;font-size:42px;font-weight:700;line-height:1.25;background:#fff;border-radius:36px;padding:34px 44px">3 · Set a 60-minute alarm to stand up and stretch.</div><div class="foot">%s</div>' % (n, sh, DISC), 4, 'var(--lilac)', 'var(--pink)'))
    s.append(cta(5, 5))
    return s
def c2():
    s = []
    s.append(frame(1, '<div class="card" style="left:90px;top:640px;width:620px;height:620px;border-radius:50%%;box-shadow:0 18px 50px rgba(43,36,49,.18)"><img src="%s"></div><div style="position:absolute;left:80px;right:80px;top:190px"><h1 style="font-size:112px">3 things I do after every stream</h1><p style="font-size:40px;color:var(--muted);margin-top:34px;font-weight:600">Swipe →</p></div>' % img('portrait.jpg'), 1))
    sh, wr, cc = img('shoulders.jpg'), img('wrists.jpg'), img('cacao.jpg')
    def photo_slide(n, head, text, photo, k, a, b):
        return frame(n, '<div style="position:absolute;left:80px;right:80px;top:190px"><h2>%s</h2><p style="font-size:44px;line-height:1.3;font-weight:600;margin:0">%s</p></div><div class="card" style="left:190px;top:650px;width:700px;height:590px"><img src="%s"></div><div class="foot" style="bottom:30px">%s</div>' % (head, E(text), photo, DISC), k, a, b)
    s.append(photo_slide(2, '1 · Shoulder blade squeeze', 'Pull your shoulder blades back and down. Hold 3 seconds, 8 reps.', sh, 2, 'var(--blue)', 'var(--lilac)'))
    s.append(photo_slide(3, '2 · Wrist stretch', 'Arm straight, palm facing forward. Gently pull the fingers back toward you. 15 seconds each hand.', wr, 3, 'var(--mint)', 'var(--blue)'))
    if cc:
        s.append(photo_slide(4, '3 · A warm drink, screens off', 'Five quiet minutes. My evening cacao ritual (affiliate, code KRISTINE15).', cc, 4, 'var(--pink)', 'var(--lilac)'))
    else:
        cup = '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;background:var(--pink)"><g fill="none" stroke="#8A3459" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="M34 52 H82 V74 Q82 92 58 92 Q34 92 34 74 Z" fill="#fff"/><path d="M82 58 H92 Q100 58 100 66 Q100 76 90 76 H82"/><path d="M48 40 Q44 32 50 26 M62 40 Q58 32 64 26"/></g></svg>'
        s.append(frame(4, '<div style="position:absolute;left:80px;right:80px;top:190px"><h2>3 · A warm drink, screens off</h2><p style="font-size:44px;line-height:1.3;font-weight:600;margin:0">Five quiet minutes. My evening cacao ritual (affiliate, code KRISTINE15).</p></div><div class="card" style="left:190px;top:650px;width:700px;height:590px">%s</div><div class="foot" style="bottom:30px">%s</div>' % (cup, DISC), 4, 'var(--pink)', 'var(--lilac)'))
    s.append(cta(5, 5))
    return s
JS = r"""
const { chromium } = require('playwright');
(async () => { const items = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8')); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
 for (const [file, html] of items) { await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150); await (await p.$('#s')).screenshot({ path: file }); }
 await b.close(); })();
"""
def main():
    head = '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700&display=swap" rel="stylesheet"><style>%s</style></head><body>' % CSS
    jobs, files = [], []
    for code, slug, fn in (('C1', 'neck-after-gaming', c1), ('C2', 'after-every-stream', c2)):
        for n, inner in enumerate(fn(), 1):
            f = os.path.join(OUT, 'EN-%s-%s-%d.png' % (code, slug, n)); jobs.append((f, head + inner + '</body></html>')); files.append(f)
    jf = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(jobs, jf); jf.close()
    jsf = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False); jsf.write(JS); jsf.close()
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf.name, jf.name], check=True, env=env); os.unlink(jsf.name); os.unlink(jf.name)
    z = os.path.join(HERE, 'EN-carusele.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files: zf.write(f, os.path.basename(f))
    print('gata:', len(files), 'imagini')
main()
