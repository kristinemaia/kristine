#!/usr/bin/env python3
"""Face videourile antrenamentelor pentru Payhip (unul pe postare) și textele postărilor, din workouts.py.
Video: 720×1280, fără sunet. Card de titlu → fiecare exercițiu (clipul, repetat cât să țină ~8 s), cu numele și seriile sus → card de final.
Rulezi: python3 studio/custom-program/build_workouts.py [cuvânt din titlu ...] [--text = doar textele, fără videouri]
   -> studio/custom-program/out/workouts/<nn>-<slug>.mp4  și  WORKOUTS-PAYHIP.md (în rădăcina repo-ului)"""
import os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'brand/carousels-en'))
from workouts import ALL, NAMES, HOME_NAMES
import build_produse as bp
W, H, MIN_SEG, MAX_SEG = 720, 1280, 8.0, 14.0
FONTS = os.path.join(ROOT, 'brand/reels-overlays/fonts')
OUT = os.path.join(HERE, 'out/workouts')

def clip_path(cid):
    for p in (os.path.join(HERE, 'out', cid + '.mp4'), os.path.join(HERE, 'clips/preview', cid + '.mp4')):
        if os.path.exists(p): return p
    raise SystemExit('lipsește clipul: ' + cid)

def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
def slug(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
def font(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)

def fit(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines

def label_png(section, name, sets, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    for i in range(380): g.line([(0, i), (W, i)], fill=(0, 0, 0, int(165 * (1 - i / 380) ** 1.4)))
    d = ImageDraw.Draw(im)
    fs, fn, fp = font('Poppins-Medium.ttf', 22), font('Poppins-SemiBold.ttf', 44), font('Poppins-SemiBold.ttf', 30)
    s = section.upper(); x = (W - (sum(d.textlength(c, font=fs) for c in s) + 4 * (len(s) - 1))) / 2
    for c in s: d.text((x, 62), c, font=fs, fill=(235, 225, 210, 255)); x += d.textlength(c, font=fs) + 4
    y = 100
    for ln in fit(d, name, fn, W - 80):
        d.text(((W - d.textlength(ln, font=fn)) / 2, y), ln, font=fn, fill=(255, 255, 255, 255)); y += 56
    tw = d.textlength(sets, font=fp); px, py = (W - tw) / 2, y + 14
    d.rounded_rectangle((px - 22, py - 6, px + tw + 22, py + 44), radius=26, fill=(255, 228, 92, 240))
    d.text((px, py), sets, font=fp, fill=(20, 18, 16, 255))
    im.save(path)

def card_png(lines, path, bg):
    im = bg.convert('RGBA'); d = ImageDraw.Draw(im); y = 470
    for txt, f, col, gap in lines:
        if any(ord(c) > 0x2190 for c in txt):
            em = bp.emoji_img(txt, 90); im.alpha_composite(em, ((W - em.width) // 2, y)); y += em.height + gap; continue
        for ln in fit(d, txt, f, W - 90):
            d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=col); y += int(f.size * 1.3)
        y += gap
    im.convert('RGB').save(path)

def frame_bg(p, t, tmp):
    j = os.path.join(tmp, 'bg.jpg')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', p, '-frames:v', '1', '-vf', 'scale=%d:%d' % (W, H), j], check=True)
    im = Image.open(j).filter(ImageFilter.GaussianBlur(24)); return Image.blend(im, Image.new('RGB', im.size, (12, 11, 10)), 0.6)

def seg_from_clip(p, png, out):
    d = dur(p); target = min(MAX_SEG, max(MIN_SEG, d)); loops = int(target // d) + 1
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', str(loops), '-i', p, '-loop', '1', '-i', png, '-filter_complex',
                    '[0:v]fps=30,scale=%d:%d:flags=lanczos,setsar=1[v];[v][1:v]overlay=0:0,format=yuv420p[o]' % (W, H),
                    '-map', '[o]', '-t', '%.2f' % target, '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', out], check=True)

def seg_from_image(jpg, secs, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', jpg, '-t', str(secs), '-vf', 'fps=30,format=yuv420p', '-an',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', out], check=True)

def name_of(cid, home): return HOME_NAMES.get(cid, NAMES[cid]) if home else NAMES[cid]

def build_video(n, wk):
    tmp = tempfile.mkdtemp(); segs = []
    first = clip_path((wk['main'] or wk['warm'])[0][0]); bg = frame_bg(first, 1.0, tmp)
    t = os.path.join(tmp, 'title.jpg')
    card_png([('CUSTOM PROGRAM', font('Poppins-Medium.ttf', 24), (220, 210, 195, 255), 18), (wk['title'], font('Poppins-SemiBold.ttf', 58), (255, 255, 255, 255), 26),
              (' · '.join(wk['tags']), font('Poppins-Medium.ttf', 26), (255, 228, 92, 255), 30), ('Rest 60–90 s between sets', font('Poppins-Medium.ttf', 26), (230, 225, 215, 255), 0)], t, bg)
    s = os.path.join(tmp, 's00.mp4'); seg_from_image(t, 3, s); segs.append(s)
    parts = [('Warm-up', wk['warm']), ('Workout', wk['main']), ('Cool-down', wk['cool'])]
    k = 0
    for sec, items in parts:
        for i, (cid, sets) in enumerate(items, 1):
            k += 1; png = os.path.join(tmp, 'l%02d.png' % k)
            label_png('%s · %d / %d' % (sec, i, len(items)) if sec == 'Workout' else sec, name_of(cid, wk['home']), sets, png)
            s = os.path.join(tmp, 's%02d.mp4' % k); seg_from_clip(clip_path(cid), png, s); segs.append(s)
    e = os.path.join(tmp, 'end.jpg')
    card_png([('💪', None, None, 20), (('Reset done' if 'Resets' in wk['tags'] else 'Workout done'), font('Poppins-SemiBold.ttf', 58), (255, 255, 255, 255), 22),
              (('Write your weights and reps in your training log' if not any(t in wk['tags'] for t in ('Resets', 'Unstiff', 'Cardio')) else 'Nice work. Your body says thank you'), font('Poppins-Medium.ttf', 28), (230, 225, 215, 255), 0)], e, bg)
    s = os.path.join(tmp, 's99.mp4'); seg_from_image(e, 3, s); segs.append(s)
    lst = os.path.join(tmp, 'list.txt'); open(lst, 'w').write(''.join("file '%s'\n" % x for x in segs))
    os.makedirs(OUT, exist_ok=True); out = os.path.join(OUT, '%02d-%s.mp4' % (n, slug(wk['title'])))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out], check=True)
    return out

def post_text(wk):
    L = []
    def block(head, items):
        if not items: return
        L.append(head)
        for i, (cid, sets) in enumerate(items, 1):
            L.append(('%d. ' % i if head == 'Workout' else '• ') + '%s · %s' % (name_of(cid, wk['home']), sets))
        L.append('')
    block('Warm-up', wk['warm']); block('Workout', wk['main']); block('Cool-down', wk['cool'])
    if wk['note']: L += [wk['note'], '']
    if 'Resets' in wk['tags']:
        L.append('Do it on any day, as often as you like. Slow and gentle: a stretch is a pull, never pain.')
    elif 'Cardio' in wk['tags']:
        L.append('Easy to moderate: you should be able to talk in short sentences.')
    elif 'Unstiff' in wk['tags']:
        L.append('Move slowly and breathe. A stretch is a gentle pull, never sharp pain.')
    else:
        L += ['Rest 60–90 s between sets. Write every set in your training log.',
              'Beginner (weeks 1–2): 2 sets, light weight, stop with 4–5 reps in the tank.',
              'Intermediate: as written, stop with about 2 reps in the tank. Hit the top of the range on every set? Add 1–2 kg next time.',
              'Advanced: add 1 set and stop 1–2 reps before failure.',
              '20 minutes only? Do 2 sets of each move and skip the last one.']
    L += ['', 'General exercise, not medical advice. Stop if anything feels sharp.']
    return '\n'.join(L)

DAY_GUIDE = """Your quiz result lists your days, for example "Day 1: Lower body and core (gym)". Here's which post to open:

• Full body A / Full body B → Full body A or B (gym or home)
• Full body → alternate Full body A and Full body B
• Lower body · Legs · Legs and glutes → Lower body
• Lower body and core · Glutes and core · Glutes and hamstrings · Lower body + core → Lower body and core
• Upper body and back → Upper body and back
• Upper body and core → Upper body and back, then 2 rounds of the Plank
• Shoulders and posture · Upper body and posture → Shoulders and posture
• Core and full body · Full body + core finisher → Core and full body
• Cardio → Cardio: jump rope intervals, Cardio: incline walk, or Cardio: no-jump (home)
• Unstiff → alternate Unstiff A and Unstiff B
• Desk Reset: Upper back and core strength → Shoulders and posture
• Desk Reset: Upper back, glutes and core → Core and full body
• Desk Reset: Unstiff → Unstiff A or B
• 10 minutes a day → Express 10 (gym or home)
• Your resets → the 5-minute reset for each spot

Gym day → the (gym) post. Home day → the (home) post.
Your training log: kristinemaia.com/log.html (add it to your home screen)."""

def main(filters):
    md = ['# Antrenamentele pentru Payhip: titlu, etichete, video și textul fiecărei postări', '',
          '_17 noiembrie 2026. Generat de `studio/custom-program/build_workouts.py` din `workouts.py`. Pentru fiecare postare: **Create New Post** → tip video → videoul din Video Library → titlul → textul → etichetele → All members → Publish._', '',
          '**Ordinea:** urcă-le de la ultima la prima, ca „Which workout is my day?” și Start here să rămână sus. Videourile: `studio/custom-program/out/workouts/` (ți le trimit în chat).', '']
    md += ['## 00 · Which workout is my day? (postare text, eticheta `Start here`)', '', '```', DAY_GUIDE, '```', '']
    for n, wk in enumerate(ALL, 1):
        if filters and not any(f.lower() in wk['title'].lower() for f in filters): continue
        out = os.path.join(OUT, '%02d-%s.mp4' % (n, slug(wk['title']))) if TEXT_ONLY else build_video(n, wk); print('gata:', os.path.basename(out))
        md += ['## %02d · %s' % (n, wk['title']), '', '**Etichete:** ' + ' · '.join('`%s`' % t for t in wk['tags']), '',
               '**Video:** `%s`' % os.path.basename(out), '', '```', post_text(wk), '```', '']
    if not filters: open(os.path.join(ROOT, 'WORKOUTS-PAYHIP.md'), 'w').write('\n'.join(md))

TEXT_ONLY = '--text' in sys.argv
if __name__ == '__main__':
    main([a for a in sys.argv[1:] if a != '--text'])
