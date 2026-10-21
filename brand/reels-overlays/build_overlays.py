#!/usr/bin/env python3
"""Overlay-uri pentru reel-uri (PNG transparent, 1080 x 1920): hook, final, copertă, etichete, insigna #ad, coduri.

Rulezi:   python3 brand/reels-overlays/build_overlays.py
Rezultat: brand/reels-overlays/out/<REEL>/...png  +  out/_comune/...  +  Reels-overlays.zip

Stilul: vezi studio/STIL-VIZUAL-REELURI.md (Poppins, textul închis pe cutie crem; cutia colorată pe zone;
finalul alb pe vișiniu). Fișierele „fullframe” se pun peste tot ecranul (fit to screen), deci stau deja în zona sigură.
Etichetele (labels) sunt decupate strâns; le pui unde ai nevoie, lângă mișcare.
"""
import base64, html, json, os, re, shutil, subprocess, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, 'fonts')
OUT = os.path.join(HERE, 'out')

INK, CREAM, WINE = '#2B2431', '#FFF9F6', '#8A3459'
ZONE = {'neck': '#F8DCE6', 'shoulders': '#DDE9F7', 'wrists': '#D8F0E4', 'hips': '#E9E1F7', 'cream': CREAM, 'wine': WINE}
PDF = 'Free 5-minute desk stretch → link in bio'
GENTLE = "Gentle pull only. Stop if it's sharp."

# cod, zonă, hook, copertă (3–4 cuvinte), final rând 1 (sau None), final rând 2, etichete [(text, zonă)], insigna #ad
R = [
 ('R1', 'neck', 'Neck stiff after gaming? 3 moves, 35 seconds.', 'Neck stiff after gaming?', GENTLE, PDF,
  [('8 slow reps', 'neck'), ('20 s each side', 'neck'), ('5 each side, slowly', 'neck')], False),
 ('R2', 'shoulders', '60-second stretch break. Do it with me.', '60-second stretch break', 'Save it for your next queue time.', PDF,
  [('Side neck stretch', 'neck'), ('Shoulder rolls', 'shoulders'), ('Palm-up wrist stretch', 'wrists'), ('Seated twist', 'hips')], False),
 ('R3', 'wrists', 'Wrists tired from mouse and keyboard? 3 moves.', 'Wrists tired from mouse?', GENTLE, PDF,
  [('15 s each hand', 'wrists'), ('3 rounds', 'wrists')], False),
 ('R4', 'neck', 'My 5-minute morning desk reset, in 60 seconds.', 'Morning desk reset', None, 'The full 5 minutes is free → link in bio',
  [('Neck', 'neck'), ('Shoulders', 'shoulders'), ('Wrists', 'wrists'), ('Hips & back', 'hips')], False),
 ('B1', 'hips', 'Hips tight after a long stream? Try this.', 'Hips tight after a stream?', 'If your knees complain, make the range smaller.', PDF,
  [('20 s each side', 'hips'), ('20 s', 'hips')], False),
 ('B2', 'hips', 'Lower back stiff after a desk day? 3 gentle moves.', 'Lower back stiff?', 'Slow is the point.', PDF,
  [('6 slow rounds', 'hips'), ('30 s', 'hips'), ('20 s each side', 'hips')], False),
 ('B3', 'shoulders', 'Shoulders rounded from the desk? 3 moves.', 'The gamer hunch', GENTLE, PDF,
  [('8 slow reps', 'shoulders'), ('20 s each side', 'shoulders')], False),
 ('B4', 'shoulders', 'Before you queue: 4 moves, 1 minute.', 'Warm-up before gaming', 'Now go win.', PDF,
  [('Wrist circles', 'wrists'), ('Shoulder rolls', 'shoulders'), ('Neck tilts', 'neck'), ('Reach & twist', 'hips')], False),
 ('K1', 'cream', 'Stream-day breakfast in 15 minutes.', 'Protein pancakes', None, 'Recipe in the caption',
  [('15 minutes', 'cream')], False),
 ('Ton', 'cream', 'No-cook tuna and bean salad in 5 minutes.', 'Tuna & bean salad', None, 'Recipe in the caption',
  [('5 minutes', 'cream')], False),
 ('K4', 'cream', 'After a long stream: salmon & broccoli.', 'Salmon & broccoli', None, 'Recipe in the caption', [], False),
 ('K5', 'cream', 'Dinner after the stream: white fish, rice, veggies.', 'White fish & rice', None, 'Recipe in the caption', [], False),
 ('Sala', 'hips', 'Sit all day? 3 machines undo the chair.', 'Undo the chair', 'Not medical advice.', PDF, [], False),
 ('DopeRope', 'wine', '20-second rope warm-up. Just a rope.', 'Just a rope', 'Affiliate: I earn a small commission', 'Code KRISTINEMAIA → link in bio',
  [('20 seconds', 'cream')], False),
 ('Bewit', 'wine', 'My evening cacao ritual', 'Evening cacao ritual', 'Affiliate: I earn a small commission', 'Code KRISTINE15 → link in bio', [], False),
 ('Revu', 'wine', '60-second shoulder reset', 'Shoulder reset', 'Affiliate: I earn a small commission', 'Code KRISTINE20 → link in bio', [], False),
 # rezerva (după 18 nov)
 ('Rez-K6', 'cream', 'No scale needed: your hand is the measure.', 'Your hand is the measure', 'General food ideas, not medical advice.', PDF, [], False),
 ('Rez-O1', 'shoulders', 'Your desk in 10 seconds: 3 checks.', 'Desk check: 10 seconds', 'A comfortable setup, not a perfect one.', PDF, [], False),
 ('Rez-K2', 'cream', 'Dessert for breakfast: 5 minutes the night before.', 'Tiramisu oats', None, 'Recipe in the caption', [], False),
 ('Rez-K7', 'cream', '3 swaps that keep you full.', '3 swaps', 'General food ideas, not medical advice.', PDF, [], False),
 ('Rez-O3', 'wrists', 'Mouse hand tired? Check this first.', 'Mouse hand tired?', GENTLE, PDF, [], False),
 ('Rez-K3', 'cream', 'A hot meal in 10 minutes, between two matches.', 'Hot meal in 10 minutes', None, 'Recipe in the caption', [], False),
 ('Rez-K8', 'cream', 'My stream-day desk snacks (3 things).', 'Stream-day snacks', 'General food ideas, not medical advice.', PDF, [], False),
 ('Rez-O7', 'neck', 'Why your neck feels stiff after 4 hours of gaming.', 'Why your neck feels stiff', GENTLE, PDF, [], False),
 ('Rez-K9', 'cream', '12 things I always keep in my kitchen.', '12 kitchen staples', 'General food ideas, not medical advice.', PDF, [], False),
]
TIMES = ['5 minutes', '10 minutes', '15 minutes', '20 minutes', '25 minutes', '30 minutes']

ARROW = ('<svg viewBox="0 0 24 24" style="width:.9em;height:.9em;vertical-align:-.12em;margin:0 .15em" fill="none" '
         'stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16M14 6l6 6-6 6"/></svg>')

def esc(t):
    h = html.escape(t)
    # cuvintele cu cratimă nu se rup la capăt de rând (înainte de a pune săgeata SVG, ca să nu-i atingem atributele)
    h = re.sub(r'(?<![\w>])([\w&;]+(?:-[\w&;]+)+)', r'<span style="white-space:nowrap">\1</span>', h)
    return h.replace('→', ARROW)

CSS = """
@font-face{font-family:P;font-weight:700;src:url(data:font/ttf;base64,BOLD64)}
@font-face{font-family:P;font-weight:600;src:url(data:font/ttf;base64,SEMI64)}
*{box-sizing:border-box;margin:0}
html,body{background:transparent}
body{font-family:P,sans-serif;font-weight:700;width:1080px;height:1920px;position:relative;overflow:hidden}
.box{position:absolute;left:50%;transform:translateX(-50%);width:max-content;border-radius:30px;text-align:center;line-height:1.22;
  box-shadow:0 6px 18px rgba(43,36,49,.12)}
.t{display:inline-block}
.box{text-wrap:balance}
.stack{position:absolute;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:24px}
.stack .box{position:static;transform:none}
"""

def box(top, text, bg, color, size, maxw=900, op=1.0, pad='30px 44px', extra=''):
    # bg cu opacitate: o aplicăm pe fundal, nu pe text
    return (f'<div class="box" data-fit="1" style="top:{top}px;max-width:{maxw}px;background:{rgba(bg, op)};color:{color};'
            f'font-size:{size}px;padding:{pad};{extra}">{esc(text)}</div>')

def rgba(hexc, op):
    h = hexc.lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f'rgba({r},{g},{b},{op})'

def b64(name):
    return base64.b64encode(open(os.path.join(FONTS, name), 'rb').read()).decode()

_CSS = None
def page(body):
    global _CSS
    if _CSS is None:
        _CSS = CSS.replace('BOLD64', b64('Poppins-Bold.ttf')).replace('SEMI64', b64('Poppins-SemiBold.ttf'))
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{_CSS}</style></head><body>{body}</body></html>'

def hook_html(text, bg=CREAM, color=INK, size=66):
    return page(box(320, text, bg, color, size, op=0.92))

def final_html(l1, l2):
    if l1:
        inner = (box(0, l1, CREAM, INK, 46, op=0.92, pad='24px 40px') + box(0, l2, WINE, '#FFFFFF', 46, pad='24px 40px'))
        return page(f'<div class="stack" style="top:940px">{inner}</div>')
    return page(f'<div class="stack" style="top:1120px">{box(0, l2, WINE, "#FFFFFF", 48, pad="26px 42px")}</div>')

def cover_html(text, zone):
    bg = ZONE[zone]; color = '#FFFFFF' if zone == 'wine' else INK
    return page(box(760, text, bg, color, 84, maxw=900, pad='40px 54px'))

def label_html(text, zone):
    bg = ZONE[zone]; color = '#FFFFFF' if zone == 'wine' else INK
    border = f'border:4px solid {WINE};' if zone == 'cream' else ''
    return page(f'<div id="lab" style="position:absolute;left:30px;top:30px;display:inline-block;white-space:nowrap;border-radius:999px;'
                f'padding:18px 40px;font-size:48px;background:{bg};color:{color};{border}box-shadow:0 6px 18px rgba(43,36,49,.12)">{esc(text)}</div>')

def ad_html():
    return page(f'<div id="lab" style="position:absolute;left:60px;top:280px;display:inline-block;border-radius:16px;padding:10px 26px;'
                f'font-size:40px;background:{WINE};color:#fff">#ad</div>')

def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

JS = r"""
const { chromium } = require('playwright');
const items = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const it of items) {
    await p.setContent(it.html, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    // ajustare: scade fontul până încape pe max. 2 rânduri (3 la textele lungi), minim 46 px
    await p.evaluate(() => {
      document.querySelectorAll('[data-fit]').forEach(el => {
        let size = parseFloat(el.style.fontSize);
        const lh = 1.22;
        const maxLines = size >= 80 ? 3 : 2;
        const lines = () => Math.round((el.clientHeight - 60) / (size * lh));
        while (size > 46 && lines() > maxLines) { size -= 2; el.style.fontSize = size + 'px'; }
      });
    });
    await p.waitForTimeout(80);
    const info = await p.evaluate(() => {
      const els = [...document.querySelectorAll('.box, #lab')];
      return els.map(e => { const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height, fs: getComputedStyle(e).fontSize}; });
    });
    if (it.clip) {
      const r = info[0];
      await p.screenshot({ path: it.file, omitBackground: true, clip: { x: Math.max(0, r.x - 30), y: Math.max(0, r.y - 30), width: r.w + 60, height: r.h + 60 } });
    } else {
      await p.screenshot({ path: it.file, omitBackground: true });
    }
    it.info = info;
  }
  require('fs').writeFileSync(process.argv[2] + '.out', JSON.stringify(items.map(i => ({ file: i.file, info: i.info }))));
  await b.close();
})();
"""

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    items = []
    def add(folder, name, htm, clip=False):
        d = os.path.join(OUT, folder); os.makedirs(d, exist_ok=True)
        items.append({'file': os.path.join(d, name), 'html': htm, 'clip': clip})
    for code, zone, hook, cover, l1, l2, labels, ad in R:
        bg = WINE if zone == 'wine' else CREAM
        color = '#FFFFFF' if zone == 'wine' else INK
        add(code, f'{code}_1-hook.png', hook_html(hook, bg=bg, color=color))
        add(code, f'{code}_2-final.png', final_html(l1, l2))
        add(code, f'{code}_3-coperta.png', cover_html(cover, zone))
        for i, (txt, z) in enumerate(labels, 1):
            add(code, f'{code}_eticheta-{i}-{slug(txt)}.png', label_html(txt, z), clip=True)
        if ad:
            add(code, f'{code}_insigna-ad.png', ad_html())
    for t in TIMES:
        add('_comune', f'eticheta-timp-{slug(t)}.png', label_html(t, 'cream'), clip=True)
    add('_comune', 'insigna-ad.png', ad_html())
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as jf, tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as sf:
        json.dump(items, jf); jf.flush(); sf.write(JS); sf.flush()
        env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
        subprocess.run(['node', sf.name, jf.name], check=True, env=env)
    res = json.load(open(jf.name + '.out'))
    os.unlink(jf.name); os.unlink(jf.name + '.out'); os.unlink(sf.name)
    # verificare zonă sigură: pe fișierele full-frame, cutiile trebuie să stea între y=250 și y=1520, x între 60 și 950
    bad = []
    for r in res:
        if '_eticheta' in r['file'] or 'eticheta-timp' in r['file']:
            continue
        for e in r['info']:
            if e['y'] < 250 and 'insigna' not in r['file'] or e['y'] + e['h'] > 1520 or e['x'] < 60 or e['x'] + e['w'] > 1020:
                bad.append((os.path.relpath(r['file'], OUT), round(e['y']), round(e['y'] + e['h']), round(e['x']), round(e['x'] + e['w'])))
    if bad:
        print('ATENȚIE, în afara zonei sigure:'); [print(' ', b) for b in bad]
    # copie plată, pentru Bibliotecă
    flat = os.path.join(HERE, 'out-flat')
    if os.path.exists(flat): shutil.rmtree(flat)
    os.makedirs(flat)
    for root, _, files in os.walk(OUT):
        for fn in files: shutil.copyfile(os.path.join(root, fn), os.path.join(flat, fn))
    # ZIP
    zp = os.path.join(HERE, 'Reels-overlays.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            for f in sorted(files):
                full = os.path.join(root, f); z.write(full, os.path.join('Reels-overlays', os.path.relpath(full, OUT)))
        for extra, arc in (('timer', 'Reels-overlays/_timer'), ('coperti', 'Reels-overlays/_coperti-gata-facute')):
            d = os.path.join(HERE, extra)
            if os.path.isdir(d):
                for fn in sorted(os.listdir(d)): z.write(os.path.join(d, fn), arc + '/' + fn)
        z.write(os.path.join(HERE, 'CITESTE.txt'), 'Reels-overlays/CITESTE.txt') if os.path.exists(os.path.join(HERE, 'CITESTE.txt')) else None
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print('gata:', n, 'fișiere PNG,', round(os.path.getsize(zp) / 1024), 'KB →', zp)

if __name__ == '__main__':
    main()
