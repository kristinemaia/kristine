#!/usr/bin/env python3
"""Hărțile de mușchi pentru videourile antrenamentelor (stilul cerut de Kristine pe 18 nov):
o siluetă simplă (din față sau din spate) cu zona lucrată în roșu. Desenul e al nostru, făcut din forme simple.
MUSCLES: exercițiu -> (vedere, [zone]). Zonele: vezi REGIONS_FRONT / REGIONS_BACK.
render_card(cid, size) -> PIL.Image RGBA (fundal transparent)."""
import os
from PIL import Image, ImageDraw, ImageFilter

SKIN, SKIN_D, RED = (244, 214, 200, 255), (214, 178, 164, 255), (229, 45, 58, 255)

# vedere: 'front' sau 'back'; zonele marcate
MUSCLES = {
    'incalzire-coarda': ('front', ['quads', 'calves_f', 'heart']), 'incalzire-cercuri-brate': ('front', ['delts_f']),
    'incalzire-leg-swings': ('front', ['hipflex', 'quads']), 'incalzire-mars-pe-loc': ('front', ['hipflex', 'quads', 'heart']),
    'incalzire-step-jack': ('front', ['quads', 'delts_f', 'heart']), 'incalzire-jumping-jacks': ('front', ['quads', 'delts_f', 'heart']),
    'incalzire-inchworm': ('back', ['hams', 'lowback', 'delts_b']), 'mobilitate-cat-cow-v2': ('back', ['lowback', 'upback']),
    'mobilitate-worlds-greatest-stretch': ('front', ['hipflex', 'obliques']), 'mobilitate-flexori-sold': ('front', ['hipflex']),
    'mobilitate-childs-pose': ('back', ['lats', 'lowback']), 'mobilitate-cobra': ('front', ['abs']),
    'mobilitate-extensie-toracica': ('back', ['upback']), 'mobilitate-rasucire-sezut': ('front', ['obliques']),
    'picioare-goblet-a': ('front', ['quads', 'glutes_f']), 'picioare-fandare-inapoi': ('back', ['glutes', 'hams']),
    'picioare-split-a': ('front', ['quads', 'glutes_f']), 'picioare-varfuri': ('back', ['calves']),
    'picioare-hip-thrust': ('back', ['glutes']), 'picioare-rdl': ('back', ['hams', 'glutes']),
    'spate-lat-pulldown': ('back', ['lats']), 'spate-face-pull': ('back', ['delts_b', 'upback']),
    'spate-ramat-gantera': ('back', ['lats', 'upback']), 'spate-fluturari-inverse': ('back', ['delts_b', 'upback']),
    'impins-flotare-inclinata': ('front', ['chest', 'triceps_f']), 'impins-flotare': ('front', ['chest', 'triceps_f']),
    'impins-umeri-gantere': ('front', ['delts_f']), 'umeri-ridicari-laterale': ('front', ['delts_f']),
    'core-plank': ('front', ['abs']), 'core-bird-dog': ('back', ['lowback', 'glutes']), 'core-plank-lateral': ('front', ['obliques']),
    'core-dead-bug': ('front', ['abs']), 'core-hollow-hold': ('front', ['abs']), 'gat-chin-tucks-sezut': ('back', ['neck']),
    'incheieturi-palma-sus': ('front', ['forearms']), 'cardio-banda': ('back', ['glutes', 'calves', 'heart']),
    'cardio-skaters': ('back', ['glutemed', 'glutes', 'heart']), 'picioare-genuflexiune': ('front', ['quads', 'glutes_f']),
    'picioare-glute-bridge': ('back', ['glutes']), 'picioare-goblet-b': ('front', ['adductors', 'quads']),
    'picioare-fandare-inainte': ('front', ['quads', 'glutes_f']), 'picioare-wall-sit': ('front', ['quads']),
    'spate-swimmers': ('back', ['upback', 'lowback']), 'brate-biceps-curl': ('front', ['biceps']),
    'umeri-ridicari-frontale': ('front', ['delts_f']), 'core-plank-leg-lift': ('back', ['glutes', 'lowback']),
    'core-high-plank': ('front', ['abs', 'delts_f']), 'core-tabletop-crunch': ('front', ['abs']), 'core-russian-twist': ('front', ['obliques']),
    'gat-lateral': ('back', ['neck']), 'gat-semicercuri': ('back', ['neck']), 'incheieturi-palma-jos': ('front', ['forearms']),
    'incheieturi-cercuri': ('front', ['forearms']), 'incalzire-cercuri-sold': ('back', ['glutemed', 'glutes']),
    'incalzire-leg-swings-lateral': ('front', ['adductors', 'glutes_f']), 'incalzire-gambe': ('back', ['hams', 'calves']),
    'incalzire-respiratie': ('front', ['abs', 'chest']), 'mobilitate-open-book-v3a': ('front', ['chest', 'obliques']),
    'mobilitate-90-90-v2': ('back', ['glutemed', 'glutes']), 'mobilitate-deep-squat-hold': ('front', ['adductors', 'quads']),
    'mobilitate-triceps': ('back', ['triceps']), 'cardio-spinning': ('front', ['quads', 'heart']), 'cardio-bicicleta-spatar': ('front', ['quads', 'heart']),
}

# coordonate pe o pânză de 200 x 420 (silueta), (stânga, sus, dreapta, jos) pentru elipse; fiecare zonă e simetrică stânga/dreapta
def _sym(box):
    l, t, r, b = box; return [box, (200 - r, t, 200 - l, b)]

REGIONS = {
    'front': {
        'delts_f': _sym((44, 92, 70, 120)), 'chest': _sym((66, 96, 99, 130)), 'biceps': _sym((34, 122, 52, 168)),
        'triceps_f': _sym((30, 118, 46, 160)), 'forearms': _sym((22, 170, 42, 220)), 'abs': [(78, 132, 122, 206)],
        'obliques': _sym((62, 140, 80, 200)), 'hipflex': _sym((70, 206, 96, 236)), 'glutes_f': _sym((62, 200, 82, 228)),
        'quads': _sym((60, 228, 96, 314)), 'adductors': _sym((88, 230, 100, 300)), 'calves_f': _sym((64, 330, 90, 392)),
    },
    'back': {
        'neck': [(88, 66, 112, 92)], 'upback': [(66, 90, 134, 128)], 'delts_b': _sym((42, 92, 68, 122)),
        'triceps': _sym((32, 120, 50, 168)), 'lats': _sym((62, 122, 94, 180)), 'lowback': [(80, 170, 120, 206)],
        'glutemed': _sym((60, 194, 82, 220)), 'glutes': _sym((66, 202, 100, 248)), 'hams': _sym((62, 250, 96, 318)),
        'calves': _sym((64, 330, 92, 394)),
    },
}

def _silhouette(d):
    d.ellipse((78, 8, 122, 60), fill=SKIN)                      # capul
    d.polygon([(91, 52), (109, 52), (112, 84), (88, 84)], fill=SKIN)   # gâtul
    # trunchiul: umeri, talie, șolduri (siluetă feminină, simplă)
    d.polygon([(60, 82), (140, 82), (152, 96), (146, 130), (134, 172), (148, 206), (154, 236), (46, 236), (52, 206), (66, 172), (54, 130), (48, 96)], fill=SKIN)
    d.ellipse((44, 80, 76, 112), fill=SKIN); d.ellipse((124, 80, 156, 112), fill=SKIN)   # umerii rotunjiți
    d.ellipse((46, 196, 154, 258), fill=SKIN)                  # bazinul, rotunjit
    for s in (1, -1):
        x = lambda v: v if s == 1 else 200 - v
        # brațul: se subțiază spre încheietură
        d.polygon([(x(46), 98), (x(62), 104), (x(52), 160), (x(44), 216), (x(32), 218), (x(36), 160)], fill=SKIN)
        d.ellipse((x(38) - 9, 210, x(38) + 9, 232), fill=SKIN)
        # piciorul: coapsă plină, genunchi, gambă, gleznă
        d.polygon([(x(50), 230), (x(99), 236), (x(94), 300), (x(90), 322), (x(92), 352), (x(86), 396), (x(72), 396), (x(66), 352), (x(62), 322), (x(54), 290)], fill=SKIN)
        d.ellipse((min(x(68), x(92)), 390, max(x(68), x(92)), 410), fill=SKIN)

def render_card(cid, size=150):
    view, zones = MUSCLES.get(cid, ('front', []))
    base = Image.new('RGBA', (200, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(base); _silhouette(d)
    if view == 'back':                                           # o linie pe mijlocul spatelui, ca să se vadă că e din spate
        d.line([(100, 84), (100, 200)], fill=SKIN_D, width=2)
    mask = Image.new('L', (200, 420), 0); m = ImageDraw.Draw(mask)
    for z in zones:
        for box in REGIONS[view].get(z, []): m.ellipse(box, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    alpha = base.split()[3]; mask = Image.composite(mask, Image.new('L', mask.size, 0), alpha)
    red = Image.new('RGBA', base.size, RED); base = Image.composite(red, base, mask)
    if 'heart' in zones:                                         # inima mică, pentru cardio
        h = ImageDraw.Draw(base); h.ellipse((150, 10, 170, 30), fill=RED); h.ellipse((166, 10, 186, 30), fill=RED); h.polygon([(151, 24), (185, 24), (168, 46)], fill=RED)
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0)); sh.putalpha(base.split()[3].point(lambda a: int(a * 0.55)))
    out = Image.new('RGBA', (220, 440), (0, 0, 0, 0))
    out.alpha_composite(Image.merge('RGBA', (*Image.new('RGB', base.size, (0, 0, 0)).split(), sh.split()[3])).filter(ImageFilter.GaussianBlur(6)), (12, 14))
    out.alpha_composite(base, (10, 10))
    return out.resize((size, int(size * 2)), Image.LANCZOS)

if __name__ == '__main__':
    ids = list(MUSCLES)
    sheet = Image.new('RGBA', (110 * 12, 230 * ((len(ids) + 11) // 12)), (60, 60, 60, 255))
    for i, cid in enumerate(ids): sheet.alpha_composite(render_card(cid, 100), ((i % 12) * 110 + 5, (i // 12) * 230 + 10))
    sheet.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'muscle-sheet.png'))
