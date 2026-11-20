#!/usr/bin/env python3
"""Lansarea Custom Program (20 nov): 6 story-uri 1080×1920 și reel-ul L1 „It's open”.
Rulezi: python3 brand/lansare/build_lansare.py -> brand/lansare/out/"""
import base64, json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
P = os.path.join(ROOT, 'brand', 'payhip')
def b64(path, mime='image/jpeg'): return 'data:%s;base64,' % mime + base64.b64encode(open(path, 'rb').read()).decode()
FOTO = b64(os.path.join(P, 'coperta-foto-sala.jpg'))
FOTO2 = b64(os.path.join(ROOT, 'brand/carousels-en/src/mirror-white-top.jpg'))
TIMER, REST = b64(os.path.join(P, 'screen-timer.png'), 'image/png'), b64(os.path.join(P, 'screen-rest.png'), 'image/png')

CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--mint:#D8F0E4;--lilac:#E9E1F7}
*{box-sizing:border-box}body{margin:0}
.s{position:relative;width:1080px;height:1920px;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif}
.sh{position:absolute;border-radius:50%}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.035em;margin:0;line-height:.95}
.tag{display:inline-block;background:var(--berry);color:#fff;font-weight:700;border-radius:999px;font-size:34px;padding:14px 30px}
.sub{color:var(--muted);font-weight:600}
.ph{position:absolute;border-radius:46px;background:#1d1a20;padding:12px;box-shadow:0 30px 60px rgba(43,36,49,.28)}
.ph img{display:block;width:100%;border-radius:36px}
.photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 35%,rgba(0,0,0,.72) 75%)}
.white{color:#fff}
.sticker{position:absolute;left:50%;transform:translateX(-50%);border:5px dashed rgba(138,52,89,.55);border-radius:30px;width:560px;height:150px;
  display:flex;align-items:center;justify-content:center;color:rgba(138,52,89,.8);font-weight:700;font-size:30px;text-align:center}
.steps{list-style:none;padding:0;margin:0}
.steps li{display:flex;gap:30px;align-items:flex-start;margin:0 0 54px}
.steps b.n{flex:none;width:96px;height:96px;border-radius:50%;background:var(--berry);color:#fff;font-size:52px;display:flex;align-items:center;justify-content:center;font-family:'Bricolage Grotesque'}
.steps span{font-size:50px;font-weight:700;line-height:1.15}.steps small{display:block;font-size:34px;color:var(--muted);font-weight:600;margin-top:8px}
"""
def s(body): return '<div class="s" id="s">%s</div>' % body
STICK = '<!-- %d: %s -->'   # locul pentru sticker (îl pui în Instagram), lăsat gol în imagine
STORIES = [
 ('01-its-open', s('''<img class="photo" src="%s" style="object-position:42%% 30%%"><div class="shade"></div>
  <div style="position:absolute;left:80px;right:80px;bottom:330px"><span class="tag">NOW OPEN</span>
  <h1 class="white" style="font-size:150px;margin-top:30px">Level Up<br>is live 🎉</h1>
  <p class="white" style="font-size:44px;font-weight:600;margin:30px 0 0;line-height:1.25">My training program, built around you.</p></div>''' % FOTO)),
 ('02-what-you-get', s('''<div class="sh" style="width:900px;height:900px;left:-380px;top:1150px;background:var(--pink)"></div>
  <div class="sh" style="width:700px;height:700px;right:-260px;top:-260px;background:var(--lilac)"></div>
  <div style="position:absolute;left:80px;right:80px;top:150px"><span class="tag">WHAT YOU GET</span>
  <h1 style="font-size:104px;margin-top:28px">Every workout,<br>step by step</h1>
  <p class="sub" style="font-size:42px;margin:26px 0 0;line-height:1.3">A video for every exercise, a timer for your rest and holds, and your weights saved for next time.</p></div>
  <div class="ph" style="width:390px;left:120px;top:880px;transform:rotate(-5deg)"><img src="%s"></div>
  <div class="ph" style="width:390px;left:560px;top:940px;transform:rotate(5deg)"><img src="%s"></div>''' % (TIMER, REST))),
 ('03-how-it-works', s('''<div class="sh" style="width:820px;height:820px;right:-320px;top:-300px;background:var(--mint)"></div>
  <div style="position:absolute;left:90px;right:90px;top:200px"><span class="tag">HOW IT WORKS</span>
  <h1 style="font-size:110px;margin:30px 0 80px">3 steps</h1>
  <ul class="steps"><li><b class="n">1</b><span>Take the 2-minute quiz<small>your goal, gym or home, your time</small></span></li>
  <li><b class="n">2</b><span>Join for $10/month<small>founding price, first 50 members</small></span></li>
  <li><b class="n">3</b><span>Press Start<small>your plan opens on your phone</small></span></li></ul></div>''' + STICK % (1560, 'link sticker here →<br>kristinemaia.com/training'))),
 ('04-founding-price', s('''<div class="sh" style="width:1000px;height:1000px;left:-300px;top:-300px;background:var(--pink)"></div>
  <div class="sh" style="width:600px;height:600px;right:-200px;bottom:-160px;background:var(--lilac)"></div>
  <div style="position:absolute;left:80px;right:80px;top:330px;text-align:center"><span class="tag">FOUNDING PRICE</span>
  <h1 style="font-size:300px;margin-top:40px">$10</h1><p style="font-size:56px;font-weight:800;margin:0">per month</p>
  <p class="sub" style="font-size:44px;margin:40px 0 0;line-height:1.3">for the first 50 members,<br>kept for as long as you stay.<br>Cancel anytime.</p></div>''' + STICK % (1370, 'link sticker here →<br>payhip.com/b/gWIHB'))),
 ('05-who-its-for', s('''<img class="photo" src="%s" style="object-position:50%% 30%%"><div class="shade"></div>
  <div style="position:absolute;left:80px;right:80px;bottom:300px"><span class="tag">IS IT FOR ME?</span>
  <p class="white" style="font-size:54px;font-weight:700;line-height:1.35;margin:34px 0 0">✔ You sit 6+ hours a day<br>✔ Gym or home, 10 to 40 min<br>✔ Beginner or intermediate<br>✔ You want a plan, not random workouts</p></div>''' % FOTO2)),
 ('06-questions', s('''<div class="sh" style="width:900px;height:900px;left:-340px;bottom:-300px;background:var(--mint)"></div>
  <div style="position:absolute;left:80px;right:80px;top:380px;text-align:center"><span class="tag">QUESTIONS?</span>
  <h1 style="font-size:120px;margin-top:34px">Ask me<br>anything 💬</h1>
  <p class="sub" style="font-size:44px;margin:36px 0 0;line-height:1.3">Gym or home? Beginner? Bad back?<br>Send me a DM with the word<br><b style="color:var(--berry)">PROGRAM</b></p></div>''' + STICK % (1380, 'question sticker here'))),
]
JS = r"""
const { chromium } = require('playwright');
(async () => { const items = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8')); const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1080,height:1920}});
 for (const [file, html] of items) { await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200); await (await p.$('#s')).screenshot({ path: file }); }
 await b.close(); })();
"""
def render(items):
    head = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700;800&display=swap" rel="stylesheet"><style>%s</style></head><body>' % CSS)
    tmp = tempfile.mkdtemp(); jf = os.path.join(tmp, 'j.json'); json.dump([[f, head + h + '</body></html>'] for f, h in items], open(jf, 'w'))
    jsf = os.path.join(tmp, 'r.js'); open(jsf, 'w').write(JS)
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jsf, jf], check=True, env=env)

def reel():
    """L1: 3 s intro (story 1) → demo-ul P1 din site → 3 s final (prețul)."""
    tmp = tempfile.mkdtemp(); parts = []
    for name, png in (('a', os.path.join(OUT, 'story-01-its-open.png')), ('c', os.path.join(OUT, 'story-04-founding-price.png'))):
        mp = os.path.join(tmp, name + '.mp4'); parts.append((name, mp))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', png, '-t', '3', '-vf', "scale=1080:1920,zoompan=z='min(zoom+0.0008,1.05)':d=90:s=1080x1920:fps=30,format=yuv420p",
                        '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', mp], check=True)
    p1 = os.path.join(ROOT, 'studio/custom-program/out/promo/P1-am-facut-o-aplicatie.mp4')
    mid = os.path.join(tmp, 'b.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p1, '-vf', 'scale=1080:1920,fps=30,format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', mid], check=True)
    lst = os.path.join(tmp, 'l.txt'); open(lst, 'w').write("file '%s'\nfile '%s'\nfile '%s'\n" % (parts[0][1], mid, parts[1][1]))
    out = os.path.join(OUT, 'L1-its-open.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out], check=True)
    return out

if __name__ == '__main__':
    render([(os.path.join(OUT, 'story-%s.png' % n), h) for n, h in STORIES])
    print('gata:', reel())
