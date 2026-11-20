#!/usr/bin/env python3
"""Programul pentru membri, pe site: kristinemaia.com/my-program.html (noindex, linkul îl primesc doar membrii, din postarea Start here de pe Payhip).
Omul își alege planul o dată (ca în chestionar), apoi vede zilele lui și face antrenamentul pas cu pas:
videoul exercițiului, cum se face, seturile, cronometru pentru pauze și pentru exercițiile pe timp, kg și repetări la fiecare set,
„Last time” și sugestia când să crească greutatea. Totul rămâne în telefonul lui (localStorage).
Sursa: studio/custom-program/workouts.py (aceleași 27 de antrenamente ca pe Payhip).
Rulezi: python3 website/build_program.py  -> website/my-program.html + website/assets/program/<id>.mp4/.jpg"""
import re, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CP = os.path.join(ROOT, 'studio/custom-program'); sys.path.insert(0, CP)
from workouts import ALL, NAMES, HOME_NAMES, CUES
ASSETS = os.path.join(HERE, 'assets/program'); os.makedirs(ASSETS, exist_ok=True)
WEIGHTED = {'picioare-goblet-a', 'picioare-goblet-b', 'picioare-rdl', 'picioare-hip-thrust', 'spate-lat-pulldown', 'spate-face-pull', 'spate-ramat-gantera',
            'spate-fluturari-inverse', 'impins-umeri-gantere', 'umeri-ridicari-laterale', 'umeri-ridicari-frontale', 'brate-biceps-curl', 'picioare-split-a', 'picioare-fandare-inapoi'}

def src(cid):
    """Sursa clipului: întâi originalul tău (clips/<id>.mov, 1080 × 1920, fără text), apoi variantele vechi (540 × 960)."""
    for p in (os.path.join(CP, 'clips', cid + '.mov'), os.path.join(CP, 'out', cid + '.mp4'), os.path.join(CP, 'clips/preview', cid + '.mp4'), os.path.join(CP, 'clips/istoric', cid + '.mp4')):
        if os.path.exists(p): return p
    raise SystemExit('lipsește clipul ' + cid)

def asset(cid):
    mp4, jpg = os.path.join(ASSETS, cid + '.mp4'), os.path.join(ASSETS, cid + '.jpg')
    p = src(cid); hi = p.endswith('.mov')
    if not os.path.exists(mp4):
        if hi:   # original: rezoluție mare, aceeași culoare ca reel-urile
            sys.path.insert(0, os.path.join(ROOT, 'studio/montaj')); from curat import GRADE
            vf = 'scale=1080:1920:flags=lanczos,' + GRADE + ',fps=30,format=yuv420p'; crf = '23'
        else:
            vf = 'scale=540:960:flags=lanczos,fps=30,format=yuv420p'; crf = '24'
        cut = ['-t', '10'] if hi else []   # în program clipul se repetă, deci 10 s ajung (site-ul rămâne rapid)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p] + cut + ['-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-movflags', '+faststart', mp4], check=True)
    if not os.path.exists(jpg):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1', '-i', mp4, '-frames:v', '1', '-q:v', '4', jpg], check=True)

def parse(dose):
    """„3 × 8–12” → 3 seturi de repetări; „3 × 20 s / side” → 3 seturi pe timp; „2 min” → o dată, pe timp"""
    d = {'sets': 1, 'secs': 0, 'side': '/ side' in dose or 'each side' in dose}
    m = re.match(r'\s*(\d+)\s*×\s*(.*)', dose)
    rest = dose
    if m: d['sets'] = int(m.group(1)); rest = m.group(2)
    t = re.match(r'\s*(\d+)\s*(s|min)\b', rest)
    if t: d['secs'] = int(t.group(1)) * (60 if t.group(2) == 'min' else 1)
    r = re.match(r'\s*(\d+)(?:–(\d+))?', rest)
    if r and not t: d['top'] = int(r.group(2) or r.group(1))
    return d

used = set(); data = {}
for wk in ALL:
    kind = 'reset' if 'Resets' in wk['tags'] else 'cardio' if 'Cardio' in wk['tags'] else 'mob' if 'Unstiff' in wk['tags'] else 'str'
    parts = []
    for sec, items in (('Warm-up', wk['warm']), ('Workout', wk['main']), ('Cool-down', wk['cool'])):
        if not items: continue
        ex = []
        for cid, dose in items:
            used.add(cid); p = parse(dose)
            nm = HOME_NAMES.get(cid, NAMES[cid]) if wk['home'] else NAMES[cid]
            ex.append({'id': cid, 'n': nm, 'd': dose, 'c': CUES[cid], 'sets': p['sets'], 'secs': p['secs'], 'side': p['side'], 'top': p.get('top', 0),
                       'w': cid in WEIGHTED and sec == 'Workout' and kind == 'str'})
        parts.append({'s': sec, 'x': ex})
    data[wk['title']] = {'kind': kind, 'note': wk['note'], 'p': parts}
for cid in sorted(used): asset(cid)

page = open(os.path.join(HERE, 'program_template.html'), encoding='utf-8').read()
sys.path.insert(0, HERE)
from program_i18n import LANGS, ROWS
from program_i18n_cues import CUES
i18n = {code: {} for code, _ in LANGS[1:]}
for row in ROWS + CUES:
    for (code, _), txt in zip(LANGS[1:], row[1:]): i18n[code][row[0]] = txt
# verificare: fiecare nume, instrucțiune, titlu, parte și notă are traducere
need = set(data) | {w['note'] for w in data.values() if w['note']} | {p['s'] for w in data.values() for p in w['p']} | {x['n'] for w in data.values() for p in w['p'] for x in p['x']} | {x['c'] for w in data.values() for p in w['p'] for x in p['x']}
need = {re.sub(r' \((gym|home)\)$', '', t) for t in need}
missing = sorted(t for t in need if t not in i18n['ro'])
if missing: print('FĂRĂ TRADUCERE:', missing)
open(os.path.join(HERE, 'my-program.html'), 'w', encoding='utf-8').write(page.replace('__DATA__', json.dumps(data, ensure_ascii=False)).replace('__I18N__', json.dumps(i18n, ensure_ascii=False)).replace('__LANGS__', json.dumps(LANGS, ensure_ascii=False)))
tot = sum(os.path.getsize(os.path.join(ASSETS, f)) for f in os.listdir(ASSETS))
print('gata: website/my-program.html ·', len(data), 'antrenamente ·', len(used), 'exerciții · %.1f MB clipuri' % (tot / 1e6))
