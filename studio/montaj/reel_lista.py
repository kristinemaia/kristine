#!/usr/bin/env python3
"""Reel „N moves for…”, varianta interactivă:
  intro cu clipul de gaming + freeze-frame (POV) · exercițiile numerotate cu etichetă, emoji, cronometru „try it with me”,
  un mesaj pe parcurs („breathe out…”), un „teaser” înaintea ultimului („#3 is the one everyone skips”),
  un card de final cu întrebarea pentru comentarii și „Part 2”, bara de progres, sunetul original + efecte sonore.
Rulezi: python3 studio/montaj/reel_lista.py studio/montaj/<spec>.json
Spec:
  out, punch / sfx / progress (true/false), orig_gain (dB pentru sunetul original, implicit 14)
  intro: {"clip", "ss", "d", "crop": "w:h:x:y", "freeze": 1.3, "text": [rânduri], "emoji": "😩"}
  items: [{"clip", "audio" (clipul brut, cu sunet), "ss", "d", "speed", "title", "chip", "emoji", "timer": 5, "note": "breathe out"}]
  tease: textul care apare la începutul ultimului exercițiu
  end: {"lines": [rânduri mari], "small": "rândul mic", "emoji": "👇", "d": 2.8}
Clipurile exercițiilor trebuie să fie curățate (1080x1920, fără etichetă), de ex. din studio/montaj/_curat."""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
FONTS = os.path.join(ROOT, 'brand/reels-overlays/fonts')
EMOJI_FONT = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
CREAM, WINE = (255, 249, 246), (138, 52, 89)
ENC = ['-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-r', '30', '-pix_fmt', 'yuv420p']
SR = 48000

def font(bold, size): return ImageFont.truetype(os.path.join(FONTS, 'Poppins-Bold.ttf' if bold else 'Poppins-SemiBold.ttf'), size)

def text_png(lines, path, size, y, bold=True, base=None):
    """text centrat, crem, cu umbră moale; y = marginea de sus a blocului"""
    f = font(bold, size); im = base or Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); sh = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    top = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d, ds = ImageDraw.Draw(top), ImageDraw.Draw(sh); lh = int(size * 1.18)
    for i, t in enumerate(lines):
        w = d.textlength(t, font=f); x = (1080 - w) / 2; yy = y + i * lh
        ds.text((x, yy + 4), t, font=f, fill=(0, 0, 0, 170)); d.text((x, yy), t, font=f, fill=CREAM + (255,))
    out = Image.alpha_composite(Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10))), top)
    if path: out.save(path)
    return out

def pill(im, txt, y, size=36, fill=CREAM + (235,), ink=WINE):
    d = ImageDraw.Draw(im); f = font(False, size); w = d.textlength(txt, font=f) + 56; x = (1080 - w) / 2
    d.rounded_rectangle([x, y, x + w, y + size + 26], (size + 26) // 2, fill=fill, outline=WINE, width=3)
    d.text((x + 28, y + 11), txt, font=f, fill=ink); return im

def title_png(title, chip, path):
    im = text_png([title], None, 70, 250)
    if chip: pill(im, chip.upper(), 352)
    im.save(path)

def emoji_img(ch, size=230):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, 20), ch, font=f, embedded_color=True)
    return im.crop(im.getbbox()).resize((size, size), Image.LANCZOS)

def emoji_png(ch, path, size=230):
    im = emoji_img(ch, size); out = Image.new('RGBA', (size + 40, size + 40), (0, 0, 0, 0)); a = im.split()[3].point(lambda v: int(v * 0.5))
    shadow = Image.new('RGBA', out.size, (0, 0, 0, 0)); shadow.paste((0, 0, 0, 255), (20, 28), a)
    out = Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)), out); out.alpha_composite(im, (20, 20)); out.save(path)

def timer_png(n, path):
    """cercul vișiniu din stânga-jos, cu secundele rămase și „TRY IT WITH ME” deasupra"""
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx, cy, r = 190, 1330, 92
    d.ellipse([cx - r + 4, cy - r + 8, cx + r + 4, cy + r + 8], fill=(0, 0, 0, 90))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WINE + (240,), outline=CREAM, width=6)
    f = font(True, 88); t = str(n); w = d.textlength(t, font=f); d.text((cx - w / 2, cy - 62), t, font=f, fill=CREAM)
    f2 = font(True, 30); lab = 'TRY IT WITH ME'; w2 = d.textlength(lab, font=f2)
    d.rounded_rectangle([cx - w2 / 2 - 18, cy - r - 62, cx + w2 / 2 + 18, cy - r - 14], 22, fill=CREAM + (240,))
    d.text((cx - w2 / 2, cy - r - 58), lab, font=f2, fill=WINE); im.save(path)

POP = "if(lt(T\\,0.12)\\,1.2*T/0.12\\,if(lt(T\\,0.24)\\,1.2-0.2*(T-0.12)/0.12\\,1))"

def overlay_emoji(fc, cur, idx, t0, x, y, tag):
    s = POP.replace('T', 'max(0.01\\,t-%.2f)' % t0)
    fc += (";[%d:v]format=rgba,scale=w='trunc(270*%s/2)*2+2':h='trunc(270*%s/2)*2+2':eval=frame[e%s];"
           "%s[e%s]overlay=x='%d-overlay_w/2':y='%d-overlay_h/2':enable='gte(t\\,%.2f)'[o%s]") % (idx, s, s, tag, cur, tag, x, y, t0, tag)
    return fc, '[o%s]' % tag

def overlay_at(fc, cur, idx, a, b, tag, slide=True):
    y = "'-40*max(0\\,1-(t-%.2f)/0.15)'" % a if slide else '0'
    fc += ";[%d:v]format=rgba[s%s];%s[s%s]overlay=x=0:y=%s:enable='between(t\\,%.2f\\,%.2f)'[q%s]" % (idx, tag, cur, tag, y, a, b, tag)
    return fc, '[q%s]' % tag

def punch(S):
    if not S.get('punch'): return ''
    return (",scale=w='trunc(1080*(1+0.08*max(0\\,1-t/0.25))/2)*2':h='trunc(1920*(1+0.08*max(0\\,1-t/0.25))/2)*2':eval=frame,crop=1080:1920"
            ",drawbox=x=0:y=0:w=iw:h=ih:color=white@0.35:t=fill:enable='lt(t\\,0.06)'")

def n_in(inputs): return inputs.count('-i')

def run_seg(inputs, fc, dur, p):
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[out]', '-t', '%.3f' % dur, '-an'] + ENC + [p], check=True)

def silence(dur, p):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=%d:cl=mono' % SR, '-t', '%.3f' % dur, p], check=True)

def seg_intro(S, tmp):
    I = S['intro']; fr = I.get('freeze', 1.0); d = I['d']; dur = d + fr
    h = os.path.join(tmp, 'ih.png'); text_png(I['text'], h, 64, 230); e = os.path.join(tmp, 'ie.png'); emoji_png(I.get('emoji', '😩'), e)
    crop = ('crop=%s,' % I['crop']) if I.get('crop') else ''; z = '(1+0.10*max(0\\,t-%.2f)/%.2f)' % (d, fr)
    fc = ("[0:v]setpts=PTS-STARTPTS,fps=30,%sscale=1080:1920:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=%.2f,"
          "scale=w='trunc(1080*%s/2)*2':h='trunc(1920*%s/2)*2':eval=frame,crop=1080:1920,"
          "drawbox=x=0:y=0:w=iw:h=ih:color=white@0.5:t=fill:enable='between(t\\,%.2f\\,%.2f)'[v];"
          "[1:v]format=rgba[h];[v][h]overlay=0:0[a]") % (crop, fr, z, z, d, d + 0.06)
    fc, cur = overlay_emoji(fc, '[a]', 2, d, 820, 1180, 'i'); fc += ';%sformat=yuv420p[out]' % cur
    p = os.path.join(tmp, 'p_intro.mp4')
    run_seg(['-ss', str(I['ss']), '-t', '%.3f' % d, '-i', os.path.join(ROOT, I['clip']), '-loop', '1', '-t', '%.3f' % dur, '-i', h,
             '-loop', '1', '-t', '%.3f' % dur, '-i', e], fc, dur, p)
    a = os.path.join(tmp, 'a_intro.wav'); silence(dur, a); return p, dur, a, []

def seg_stretch(S, tmp):
    """momentul „Ok… let's stretch”: clipul cu tine întinzându-te, încetinit, cu textul mare și emoji"""
    X = S['stretch']; sp = X.get('speed', 0.6); base = X['d'] / sp; dur = max(base, X.get('min_d', 0))
    h = os.path.join(tmp, 'sh.png'); text_png(X['text'], h, 104, 260); e = os.path.join(tmp, 'se.png'); emoji_png(X.get('emoji', '🙆‍♀️'), e)
    crop = ('crop=%s,' % X['crop']) if X.get('crop') else ''
    fc = ("[0:v]setpts=(PTS-STARTPTS)/%.3f,fps=30,%sscale=1080:1920:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=%.2f%s[v];"
          "[1:v]format=rgba,fade=t=in:st=0:d=0.1:alpha=1[h];[v][h]overlay=x=0:y='-60*max(0\\,1-t/0.16)'[a]") % (sp, crop, max(0.0, dur - base) + 0.1, punch(S))
    fc, cur = overlay_emoji(fc, '[a]', 2, 0.2, 820, 1180, 's'); fc += ';%sformat=yuv420p[out]' % cur
    p = os.path.join(tmp, 'p_stretch.mp4')
    run_seg(['-ss', str(X['ss']), '-t', '%.3f' % X['d'], '-i', os.path.join(ROOT, X['clip']), '-loop', '1', '-t', '%.3f' % dur, '-i', h,
             '-loop', '1', '-t', '%.3f' % dur, '-i', e], fc, dur, p)
    a = os.path.join(tmp, 'a_stretch.wav'); silence(dur, a); return p, dur, a, [(0.03, 'pop', 0.9), (0.22, 'pop', 0.6)]

def clip_len(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout)

def make_voice(S, tmp):
    """vocea de femeie (Kokoro, offline, licență Apache): un wav pe segment; potrivește duratele ca să încapă vorbele"""
    V = S['voice']; from kokoro_onnx import Kokoro; import soundfile as sf
    d = os.path.join(ROOT, V.get('dir', 'studio/montaj/_tts')); k = Kokoro(os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin'))
    def say(text, key):
        a, sr = k.create(text, voice=V.get('name', 'af_heart'), speed=V.get('speed', 1.05), lang='en-us')
        p = os.path.join(tmp, 'vo_%s.wav' % key); sf.write(p, a, sr); return p, len(a) / sr
    vo = {}
    if S.get('intro', {}).get('vo'):
        vo['intro'] = say(S['intro']['vo'], 'intro'); I = S['intro']; I['freeze'] = max(I.get('freeze', 1.0), vo['intro'][1] + 0.35 - I['d'])
    if S.get('stretch', {}).get('vo'):
        vo['stretch'] = say(S['stretch']['vo'], 'stretch'); S['stretch']['min_d'] = vo['stretch'][1] + 0.3
    for i, it in enumerate(S['items']):
        if not it.get('vo'): continue
        vo['item%d' % i] = say(it['vo'], 'item%d' % i); need = vo['item%d' % i][1] + 0.5; sp = it.get('speed', 1.0)
        if it['d'] / sp < need:
            room = clip_len(os.path.join(ROOT, it['clip'])) - it['ss'] - 0.2
            it['d'] = min(room, need * sp)
            if it['d'] / sp < need: it['speed'] = max(0.6, it['d'] / need)
    if S.get('end', {}).get('vo'):
        vo['end'] = say(S['end']['vo'], 'end'); S['end']['d'] = max(S['end'].get('d', 2.8), vo['end'][1] + 0.5)
    return vo

def seg_item(S, tmp, i, it, last):
    png = os.path.join(tmp, 't%d.png' % i); title_png(('%d. %s' % (i + 1, it['title'])) if it.get('number', True) else it['title'], it.get('chip'), png)
    sp = it.get('speed', 1.0); dur = it['d'] / sp; ev = []
    fc = '[0:v]setpts=(PTS-STARTPTS)/%.3f,fps=30,scale=1080:1920,setsar=1%s[v];' % (sp, punch(S))
    fc += "[1:v]format=rgba,fade=t=in:st=0:d=0.12:alpha=1[t];[v][t]overlay=x=0:y='-60*max(0\\,1-t/0.16)'[a]"
    cur = '[a]'; inputs = ['-ss', str(it['ss']), '-t', '%.3f' % it['d'], '-i', os.path.join(ROOT, it['clip']), '-loop', '1', '-t', '%.3f' % dur, '-i', png]
    ev.append((0.03, 'pop', 0.9))
    if it.get('emoji'):
        e = os.path.join(tmp, 'e%d.png' % i); emoji_png(it['emoji'], e); inputs += ['-loop', '1', '-t', '%.3f' % dur, '-i', e]
        fc, cur = overlay_emoji(fc, cur, n_in(inputs) - 1, 0.25, 880, 1330, 'x%d' % i); ev.append((0.28, 'pop', 0.6))
    # cronometrul „try it with me”: numără invers secundele, cu un „tick” la fiecare
    n = int(it.get('timer', 0)); t_start = 0.6
    if n:
        n = min(n, int(dur - t_start))
        for k in range(n):
            tp = os.path.join(tmp, 'tm%d_%d.png' % (i, k)); timer_png(n - k, tp); inputs += ['-loop', '1', '-t', '%.3f' % dur, '-i', tp]
            a = t_start + k; b = a + 1.0 if k < n - 1 else dur
            fc, cur = overlay_at(fc, cur, n_in(inputs) - 1, a, b, 'tm%d_%d' % (i, k), slide=False); ev.append((a, 'tick', 0.5))
    if it.get('note'):
        npng = os.path.join(tmp, 'n%d.png' % i); im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); pill(im, it['note'], 1480, 40, fill=(255, 255, 255, 230)); im.save(npng)
        inputs += ['-loop', '1', '-t', '%.3f' % dur, '-i', npng]; a = min(1.4, dur * 0.35)
        fc, cur = overlay_at(fc, cur, n_in(inputs) - 1, a, dur, 'n%d' % i)
    if last and S.get('tease'):
        tz = os.path.join(tmp, 'tease.png'); im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); pill(im, S['tease'], 470, 40, fill=(255, 220, 90, 245), ink=(43, 36, 49)); im.save(tz)
        inputs += ['-loop', '1', '-t', '%.3f' % dur, '-i', tz]; fc, cur = overlay_at(fc, cur, n_in(inputs) - 1, 0.15, min(2.4, dur), 'tz'); ev.append((0.15, 'pop', 0.7))
    fc += ';%sformat=yuv420p[out]' % cur
    p = os.path.join(tmp, 'p%d.mp4' % i); run_seg(inputs, fc, dur, p)
    # sunetul original al clipului (respirația, pașii, sala), cu aceeași tăietură și viteză
    a = os.path.join(tmp, 'a%d.wav' % i)
    if it.get('audio'):
        tempo = '' if abs(sp - 1) < 1e-3 else ',atempo=%.3f' % sp
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(it['ss']), '-t', '%.3f' % it['d'], '-i', os.path.join(ROOT, it['audio']), '-vn',
                        '-af', 'aresample=%d,pan=mono|c0=0.5*c0+0.5*c1%s,volume=%ddB,afade=t=in:d=0.05,afade=t=out:st=%.3f:d=0.08,apad' % (SR, tempo, S.get('orig_gain', 14), dur - 0.08),
                        '-t', '%.3f' % dur, a], check=True)
    else:
        silence(dur, a)
    return p, dur, a, ev

def seg_end(S, tmp, last_item):
    """cardul de final: ultimul cadru înghețat, întunecat, cu întrebarea mare și „Part 2”"""
    E = S['end']; dur = E.get('d', 2.8); fr = os.path.join(tmp, 'last.png')
    t_last = last_item['ss'] + last_item['d'] - 0.1   # cadrul curat din clipul sursă, fără cronometru și emoji
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % t_last, '-i', os.path.join(ROOT, last_item['clip']), '-frames:v', '1', '-vf', 'scale=1080:1920', fr], check=True)
    im = Image.open(fr).convert('RGBA').filter(ImageFilter.GaussianBlur(14)); im = Image.alpha_composite(im, Image.new('RGBA', im.size, (20, 14, 22, 150)))
    card = os.path.join(tmp, 'end.png'); im = text_png(E['lines'], None, 84, 640, base=im)
    if E.get('small'): pill(im, E['small'], 1060, 40)
    if E.get('emoji'): em = emoji_img(E['emoji'], 200); im.alpha_composite(em, ((1080 - 200) // 2, 1200))
    im.save(card); p = os.path.join(tmp, 'p_end.mp4')
    fc = "[0:v]scale=1080:1920,setsar=1,format=rgba,fade=t=in:st=0:d=0.15[c];[c]scale=w='trunc(1080*(1+0.04*t/%.2f)/2)*2':h='trunc(1920*(1+0.04*t/%.2f)/2)*2':eval=frame,crop=1080:1920,format=yuv420p[out]" % (dur, dur)
    run_seg(['-loop', '1', '-t', '%.3f' % dur, '-i', card], fc, dur, p)
    a = os.path.join(tmp, 'a_end.wav'); silence(dur, a); return p, dur, a, [(0.0, 'whoosh', 0.8), (0.12, 'ding', 0.8)]

def main(spec_path):
    S = json.load(open(spec_path)); tmp = tempfile.mkdtemp(); segs = []; keys = []
    vo = make_voice(S, tmp) if S.get('voice') else {}
    if S.get('intro'): segs.append(seg_intro(S, tmp)); keys.append('intro')
    if S.get('stretch'): segs.append(seg_stretch(S, tmp)); keys.append('stretch')
    for i, it in enumerate(S['items']): segs.append(seg_item(S, tmp, i, it, i == len(S['items']) - 1)); keys.append('item%d' % i)
    if S.get('end'): segs.append(seg_end(S, tmp, S['items'][-1])); keys.append('end')
    lst = os.path.join(tmp, 'l.txt'); open(lst, 'w').write(''.join("file '%s'\n" % s[0] for s in segs))
    total = sum(s[1] for s in segs); joined = os.path.join(tmp, 'v.mp4')
    vf = ['-vf', "drawbox=x=40:y=196:w=1000:h=10:color=white@0.35:t=fill,drawbox=x=40:y=196:w='max(2\\,1000*t/%.3f)':h=10:color=0x8A3459:t=fill" % total] + ENC \
        if S.get('progress') else ['-c', 'copy']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst] + vf + [joined], check=True)
    # sunetul original, lipit segment cu segment
    alst = os.path.join(tmp, 'a.txt'); open(alst, 'w').write(''.join("file '%s'\n" % s[2] for s in segs))
    orig = os.path.join(tmp, 'orig.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', alst, '-ar', str(SR), '-ac', '1', orig], check=True)
    out = os.path.join(ROOT, S['out']); os.makedirs(os.path.dirname(out), exist_ok=True)
    og = 0.45 if vo else 1.0   # când vorbește vocea, sunetul original stă mai jos
    inputs, mix = ['-i', joined, '-i', orig], '[1:a]volume=%.2f[o]' % og
    if S.get('sfx'):
        import sfx
        ev, acc = [], 0.0
        for k, s in enumerate(segs):
            if k > 0: ev.append((acc - 0.22, 'whoosh', 0.85))
            ev += [(acc + t, kind, v) for t, kind, v in s[3]]; acc += s[1]
        if S.get('intro'): ev += [(0.0, 'whoosh', 0.6), (S['intro']['d'], 'boom', 1.0), (S['intro']['d'] + 0.25, 'pop', 0.7)]
        wav = os.path.join(tmp, 'sfx.wav'); sfx.timeline(ev, total, wav); inputs += ['-i', wav]
        mix = '[1:a]volume=%.2f[o];[2:a]volume=%.2f[f];[o][f]amix=inputs=2:normalize=0[m0]' % (og, 0.7 if vo else 0.9)
        amap = '[m0]'
    else:
        amap = '[o]'
    if vo:   # vocea, pusă la începutul fiecărui segment
        starts, acc = {}, 0.0
        for kk, sg in zip(keys, segs): starts[kk] = acc; acc += sg[1]
        for kk, (pth, ln) in vo.items():
            inputs += ['-i', pth]; idx = n_in(inputs) - 1; ms = int((starts[kk] + (0.15 if kk != 'intro' else 0.1)) * 1000)
            mix += ';[%d:a]aresample=%d,aformat=channel_layouts=mono,volume=1.6,adelay=%d|%d[v%s]' % (idx, SR, ms, ms, kk)
        mix += ';%s%samix=inputs=%d:normalize=0:duration=first[mv]' % (amap, ''.join('[v%s]' % kk for kk in vo), len(vo) + 1); amap = '[mv]'
    mix += ';%salimiter=limit=0.95[fin]' % amap; amap = '[fin]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', mix, '-map', '0:v', '-map', amap, '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True)
    print(out, '%.1f s' % total)

if __name__ == '__main__':
    main(sys.argv[1])
