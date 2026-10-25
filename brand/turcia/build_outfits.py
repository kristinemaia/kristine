#!/usr/bin/env python3
"""Lista ținutelor pentru Turcia, o imagine pentru telefon (1080 x 2000).
Rulezi: python3 brand/turcia/build_outfits.py -> Turcia-tinute.png"""
import json, os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
CSS = """
:root{--bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--pink:#F8DCE6;--berry:#8A3459;--blue:#DDE9F7;--mint:#D8F0E4;--lilac:#E9E1F7}
*{box-sizing:border-box}html,body{margin:0}
.s{width:1080px;height:2000px;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif;padding:70px 64px;position:relative;overflow:hidden}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.03em;font-size:78px;line-height:1;margin:0}
.sub{font-size:30px;color:var(--muted);font-weight:600;margin:14px 0 34px}
.box{border-radius:34px;padding:30px 36px;margin-bottom:24px}
.box h2{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:40px;margin:0 0 14px;letter-spacing:-.02em}
.box ul{margin:0;padding:0;list-style:none}.box li{font-size:31px;line-height:1.28;font-weight:600;padding-left:44px;position:relative;margin-bottom:7px}
.box li:before{content:'';position:absolute;left:0;top:11px;width:20px;height:20px;border-radius:6px;border:3px solid var(--berry)}
.note{font-size:27px;color:var(--muted);font-weight:600;line-height:1.35;margin-top:6px}
.rule{background:var(--berry);color:#fff;border-radius:26px;padding:22px 32px;font-size:28px;font-weight:700;line-height:1.35}
"""
def box(bg, title, items, note=''):
    return '<div class="box" style="background:var(--%s)"><h2>%s</h2><ul>%s</ul>%s</div>' % (bg, title, ''.join('<li>%s</li>' % i for i in items), ('<div class="note">%s</div>' % note) if note else '')
body = ('<div class="s"><h1>Turcia: ținutele</h1><p class="sub">29 oct – 15 nov · doar bagaj de mână + rucsac</p>'
 + box('pink', 'Pe tine în avion', ['blugii albaștri · body sau bluză', 'hanoracul gri · fularul', 'geaca de piele', 'cizmele negre lungi (spray impermeabilizant)'])
 + box('blue', 'Oraș', ['blugi negri sau gri închis · colanți negri', 'bluza bleumarin · bluza neagră', 'cardiganul gri · topul alb tricotat', 'tricoul alb · geaca scurtă bej', 'geacă subțire de ploaie sau umbrelă'])
 + box('mint', 'Casual (stream și acasă)', ['trening gri (set)', 'pantaloni de trening negri', 'încă un hanorac'])
 + box('lilac', 'Sport și reel-uri', ['setul verde (jachetă + colanți)', 'jacheta crem (nu la cardio intens)', '1 colanți negri · 3 topuri · 3 tricouri', '6 șosete sport · prosop mic', 'adidașii gri New Balance 9060'], 'Opțional, dacă mai e loc: adidașii roz McQueen.')
 + '<div class="rule">La sală (negru cu galben): verde, albastru deschis, gri deschis, crem. Fără galben, fără negru sus; negru doar colanții. Fără logo.</div>'
 + '<p class="note" style="margin-top:22px">Rămân acasă: geaca maro, cizmele cowboy, setul alb, maioul alb, pantalonii roz, gri-lila cu decolteu în V, pantalonii negri largi, setul roz cu logo. Lenjerie 9, șosete, pijamale, căciulă, mănuși.</p></div>')
HTML = '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700&display=swap" rel="stylesheet"><style>' + CSS + '</style></head><body>' + body + '</body></html>'
JS = r"""
const { chromium } = require('playwright'); const [html, out] = JSON.parse(process.argv[2]);
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 2000 } });
 await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
 await p.screenshot({ path: out }); await b.close(); })();
"""
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as t: t.write(JS)
env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
out = os.path.join(HERE, 'Turcia-tinute.png')
subprocess.run(['node', t.name, json.dumps([HTML, out])], check=True, env=env); os.unlink(t.name); print('gata:', out)
