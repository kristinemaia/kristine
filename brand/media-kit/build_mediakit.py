#!/usr/bin/env python3
"""Media kit de o pagină (A4, PDF + previzualizare PNG).

Rulezi:  python3 brand/media-kit/build_mediakit.py
Rezultat: Kristine-Maia-Media-Kit.pdf și Kristine-Maia-Media-Kit.png în acest folder.

Cifrele se schimbă în dicționarul STATS. Un câmp lăsat gol (None) nu apare în pagină.
Pune aici doar cifre reale, din Twitch Analytics și Instagram Insights.
"""
import base64, json, os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))

STATS = {
    'twitch_followers': '72K',
    'instagram_followers': '12.6K',
    'streams_per_week': '4',
    'avg_viewers': '1.5–2.3K',    # spectatori unici pe stream (rezumatele Twitch, 6–7 nov 2026); None = nu apare
}
AUDIENCE = None                    # ex. 'Top countries: ... · Main age group: ...' din Analytics; None = nu apare
EMAIL = 'kristinemaia527@gmail.com'

def stat_tiles():
    t = [(STATS['twitch_followers'], 'Twitch followers', 'Twitch Partner'),
         (STATS['instagram_followers'], 'Instagram followers', '@kristinemaia11'),
         (STATS['streams_per_week'] + '×', 'live streams a week', 'with a stretch break every hour')]
    if STATS['avg_viewers']:
        t.append((STATS['avg_viewers'], 'unique viewers per stream', 'Twitch, November 2026'))
    return ''.join(f'<div class="stat"><b>{a}</b><span>{b}</span><i>{c}</i></div>' for a, b, c in t)

CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--blue:#DDE9F7;--blue-ink:#2A5580;--mint:#D8F0E4;--mint-ink:#1C6550;--lilac:#E9E1F7;--lilac-ink:#4C3A78}
*{box-sizing:border-box}html,body{margin:0}
@page{size:A4;margin:0}
.page{width:210mm;height:297mm;position:relative;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif;padding:12mm 14mm 8mm}
.blob{position:absolute;border-radius:50%;z-index:0}
.in{position:relative;z-index:1;height:100%;display:flex;flex-direction:column;gap:6mm}
h1,h2,.stat b{font-family:'Bricolage Grotesque',sans-serif}
.head{display:grid;grid-template-columns:1fr 46mm;gap:8mm;align-items:center}
h1{font-size:46pt;font-weight:800;letter-spacing:-.035em;line-height:.92;margin:0}
.tag{font-size:13pt;font-weight:600;margin:2.5mm 0 0;line-height:1.25}
.chips{margin-top:3mm}.chips span{display:inline-block;border-radius:99px;font-weight:700;font-size:9.5pt;padding:2mm 4mm;margin-right:2mm}
.photo{width:46mm;height:46mm;border-radius:50%;background:url(PHOTO) center/cover;border:1.6mm solid var(--lilac);justify-self:end}
.stats{display:grid;grid-template-columns:repeat(STATN,1fr);gap:3.5mm}
.stat{background:#fff;border:.3mm solid #EADFE6;border-radius:4mm;padding:4mm 4.5mm;display:flex;flex-direction:column}
.stat b{font-size:25pt;font-weight:800;letter-spacing:-.03em;line-height:1}
.stat span{font-size:10pt;font-weight:700;margin-top:1.5mm}.stat i{font-style:normal;font-size:8.5pt;color:var(--muted);margin-top:.8mm}
.two{display:grid;grid-template-columns:1.35fr 1fr;gap:7mm}
h2{font-size:11pt;font-weight:800;text-transform:uppercase;letter-spacing:.09em;color:var(--berry);margin:0 0 2mm}
p{margin:0;font-size:10.4pt;line-height:1.45}
ul{margin:0;padding:0;list-style:none}li{font-size:10.4pt;line-height:1.35;padding:.6mm 0 .6mm 5mm;position:relative}
li:before{content:'';position:absolute;left:0;top:2mm;width:2.2mm;height:2.2mm;border-radius:50%;background:var(--pink)}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:3.5mm}
.card{border-radius:4mm;padding:4mm 4.5mm}.card b{display:block;font-size:11pt;margin-bottom:1mm}.card p{font-size:9.8pt;line-height:1.35}
.row{display:grid;grid-template-columns:1fr 1fr;gap:7mm}
.pill{display:inline-block;border-radius:99px;background:#fff;border:.3mm solid #EADFE6;font-weight:700;font-size:9.5pt;padding:1.3mm 3.4mm;margin:0 1.6mm 1.3mm 0}
.contact{margin-top:auto;background:var(--ink);color:#fff;border-radius:5mm;padding:4mm 6mm;display:grid;grid-template-columns:1fr auto;gap:4mm;align-items:center}
.contact h2{color:var(--pink);margin-bottom:1.5mm}.contact p{color:#fff;font-size:10pt;line-height:1.55}.contact a{color:#fff;text-decoration:none}
.rates{background:var(--pink);color:var(--ink);font-weight:800;font-size:10pt;border-radius:99px;padding:2.6mm 5mm;text-align:center}
.foot{font-size:7.6pt;color:var(--muted);text-align:center}
"""

def html(photo):
    css = CSS.replace('PHOTO', 'data:image/jpeg;base64,' + photo).replace('STATN', str(4 if STATS['avg_viewers'] else 3))
    aud = f'<p style="margin-top:2mm"><b>Audience:</b> {AUDIENCE}</p>' if AUDIENCE else ''
    return f"""<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>{css}</style></head><body>
<div class="page"><div class="blob" style="width:90mm;height:90mm;background:#E9E1F7;right:-34mm;top:-40mm"></div><div class="blob" style="width:70mm;height:70mm;background:#F8DCE6;left:-30mm;bottom:-30mm"></div>
<div class="in">
<div class="head"><div><h1>Kristine<br>Maia</h1><p class="tag">Mobility, recovery &amp; good food for people who sit all day</p>
<div class="chips"><span style="background:var(--blue);color:var(--blue-ink)">Desk stretches</span><span style="background:var(--mint);color:var(--mint-ink)">Recipes</span><span style="background:var(--lilac);color:var(--lilac-ink)">Recovery</span></div></div><div class="photo"></div></div>
<div class="stats">{stat_tiles()}</div>
<div class="two"><div><h2>About</h2><p>I'm a Twitch Partner who streams four times a week and shows gamers and desk workers simple ways to move and recover. My streams mix gaming, a stretch break every hour, workouts and cooking, and my chat joins in.</p><p style="margin-top:2mm">I have a degree in Physical Education and Sport, and I'm a certified recovery massage therapist and mobility &amp; recovery coach.</p>{aud}</div>
<div><h2>Best fit for</h2><ul><li>Ergonomic desk and gaming gear</li><li>Mobility and recovery tools</li><li>Fitness accessories</li><li>Everyday nutrition and healthy food</li></ul></div></div>
<div><h2>What we can do together</h2><div class="cards">
<div class="card" style="background:var(--blue)"><b>Sponsored live segment</b><p>A short, natural moment in my stream: I use your product on camera and the chat sees it live.</p></div>
<div class="card" style="background:var(--pink)"><b>Reels &amp; TikTok</b><p>Short vertical videos filmed in the gym (mobility tests, form checks, follow-alongs), posted 5 times a week, with clear captions and #ad.</p></div>
<div class="card" style="background:var(--mint)"><b>Stories with your code</b><p>Story posts with a discount code and link for my community, and a pinned panel on my Twitch channel.</p></div>
<div class="card" style="background:var(--lilac)"><b>Chat command &amp; panel</b><p>A command in my Twitch chat (for example !yourbrand) that gives viewers your link and code.</p></div></div></div>
<div class="row"><div><h2>Brands I use &amp; share codes for</h2><span class="pill">Dope Rope</span><span class="pill">Bewit</span><span class="pill">Revo Natural</span></div>
<div><h2>My own products</h2><span class="pill">Free PDF: 5-minute desk stretch</span><span class="pill">Recipe e-book</span><span class="pill">1:1 online coaching</span></div></div>
<div class="contact"><div><h2>Let's talk</h2><p>{EMAIL} · kristinemaia.com<br>twitch.tv/kristinemaia · instagram.com/kristinemaia11 · TikTok @kristinemaia11</p></div><div class="rates">Rates on request</div></div>
<div class="foot">General mobility and recipe content, not medical advice. Sponsored posts are marked #ad; affiliate codes are always disclosed.</div>
</div></div></body></html>"""

def main():
    photo = base64.b64encode(open(os.path.join(HERE, 'foto-profil.jpg'), 'rb').read()).decode()
    page_html = html(photo)
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f: f.write(page_html); hp = f.name
    js = r"""
const { chromium } = require('playwright'); const [,, html, pdf, png] = process.argv;
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 2 });
  await p.goto('file://' + html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const over = await p.evaluate(() => { const c = document.querySelector('.contact').getBoundingClientRect(); const pg = document.querySelector('.page').getBoundingClientRect(); const f = document.querySelector('.foot').getBoundingClientRect(); return {contactBottom: Math.round(c.bottom), footBottom: Math.round(f.bottom), pageBottom: Math.round(pg.bottom)}; });
  console.log(JSON.stringify(over));
  await p.pdf({ path: pdf, format: 'A4', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await p.screenshot({ path: png, clip: { x: 0, y: 0, width: 794, height: 1123 } }); await b.close(); })();
"""
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf: sf.write(js); jp = sf.name
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', jp, hp, os.path.join(HERE, 'Kristine-Maia-Media-Kit.pdf'), os.path.join(HERE, 'Kristine-Maia-Media-Kit.png')], check=True, env=env)
    os.unlink(hp); os.unlink(jp); print('gata')

if __name__ == '__main__':
    main()
