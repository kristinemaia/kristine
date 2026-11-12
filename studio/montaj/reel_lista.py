#!/usr/bin/env python3
"""Reel „N moves for…”: un hook (opțional cu un clip de gaming și freeze-frame), apoi exercițiile numerotate,
cu emoji care „sar” în cadru, o etichetă mică sub titlu, bara de progres sus și efecte sonore.
Rulezi: python3 studio/montaj/reel_lista.py studio/montaj/<spec>.json
Spec:
  out, hook (rânduri), hook_d, outro, outro_d, punch / sfx / progress (true/false)
  intro (opțional): {"clip", "ss", "d", "crop": "w:h:x:y", "freeze": 1.0, "text": [rânduri], "emoji": "😩"}
  items: [{"clip", "ss", "d", "speed", "title", "chip": "upper back · 8 reps", "emoji": "🔓"}]
Clipurile exercițiilor trebuie să fie curățate (1080x1920, fără etichetă), de ex. din studio/montaj/_curat."""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
FONTS = os.path.join(ROOT, 'brand/reels-overlays/fonts')
EMOJI_FONT = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
CREAM, WINE = (255, 249, 246), (138, 52, 89)
ENC = ['-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-r', '30', '-pix_fmt', 'yuv420p']

def text_png(lines, path, size, y, bold=True):
    """text centrat, crem, cu umbră moale (se citește pe orice fundal); y = marginea de sus a blocului"""
    f = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Bold.ttf' if bold else 'Poppins-SemiBold.ttf'), size)
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); sh = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(im), ImageDraw.Draw(sh); lh = int(size * 1.18)
    for i, t in enumerate(lines):
        w = d.textlength(t, font=f); x = (1080 - w) / 2; yy = y + i * lh
        ds.text((x, yy + 4), t, font=f, fill=(0, 0, 0, 170)); d.text((x, yy), t, font=f, fill=CREAM + (255,))
    sh = sh.filter(ImageFilter.GaussianBlur(10)); Image.alpha_composite(sh, im).save(path)

def title_png(title, chip, path):
    """titlul numerotat + sub el o pastilă crem cu text vișiniu (zona lucrată, repetări)"""
    text_png([title], path, 70, 250)
    if not chip: return
    im = Image.open(path); d = ImageDraw.Draw(im); f = ImageFont.truetype(os.path.join(FONTS, 'Poppins-SemiBold.ttf'), 36)
    w = d.textlength(chip.upper(), font=f) + 56; x = (1080 - w) / 2; y = 352
    d.rounded_rectangle([x, y, x + w, y + 62], 31, fill=CREAM + (235,), outline=WINE, width=3)
    d.text((x + 28, y + 11), chip.upper(), font=f, fill=WINE); im.save(path)

def emoji_png(ch, path, size=230):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, 20), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox()).resize((size, size), Image.LANCZOS)
    out = Image.new('RGBA', (size + 40, size + 40), (0, 0, 0, 0)); a = im.split()[3].point(lambda v: int(v * 0.5))
    shadow = Image.new('RGBA', out.size, (0, 0, 0, 0)); shadow.paste((0, 0, 0, 255), (20, 28), a)
    out = Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)), out); out.alpha_composite(im, (20, 20)); out.save(path)

# emoji-ul „sare”: crește la 120% în 0,12 s, revine la 100% până la 0,24 s
POP = "if(lt(T\\,0.12)\\,1.2*T/0.12\\,if(lt(T\\,0.24)\\,1.2-0.2*(T-0.12)/0.12\\,1))"

def overlay_emoji(fc, cur, idx, t0, x, y, tag):
    s = POP.replace('T', 'max(0.01\\,t-%.2f)' % t0)
    fc += (";[%d:v]format=rgba,scale=w='trunc(270*%s/2)*2+2':h='trunc(270*%s/2)*2+2':eval=frame[e%s];"
           "%s[e%s]overlay=x='%d-overlay_w/2':y='%d-overlay_h/2':enable='gte(t\\,%.2f)'[o%s]") % (idx, s, s, tag, cur, tag, x, y, t0, tag)
    return fc, '[o%s]' % tag

def punch(S):
    if not S.get('punch'): return ''
    return (",scale=w='trunc(1080*(1+0.08*max(0\\,1-t/0.25))/2)*2':h='trunc(1920*(1+0.08*max(0\\,1-t/0.25))/2)*2':eval=frame,crop=1080:1920"
            ",drawbox=x=0:y=0:w=iw:h=ih:color=white@0.35:t=fill:enable='lt(t\\,0.06)'")

def n_in(inputs): return inputs.count('-i')

def seg_intro(S, tmp):
    """clipul de hook: joacă, apoi îngheață (freeze-frame) cu zoom lent, flash, emoji și textul POV deasupra"""
    I = S['intro']; fr = I.get('freeze', 1.0); d = I['d']; dur = d + fr
    h = os.path.join(tmp, 'ih.png'); text_png(I['text'], h, 64, 230); e = os.path.join(tmp, 'ie.png'); emoji_png(I.get('emoji', '😩'), e)
    crop = ('crop=%s,' % I['crop']) if I.get('crop') else ''
    z = '(1+0.10*max(0\\,t-%.2f)/%.2f)' % (d, fr)
    fc = ("[0:v]setpts=PTS-STARTPTS,fps=30,%sscale=1080:1920:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=%.2f,"
          "scale=w='trunc(1080*%s/2)*2':h='trunc(1920*%s/2)*2':eval=frame,crop=1080:1920,"
          "drawbox=x=0:y=0:w=iw:h=ih:color=white@0.5:t=fill:enable='between(t\\,%.2f\\,%.2f)'[v];"
          "[1:v]format=rgba[h];[v][h]overlay=0:0[a]") % (crop, fr, z, z, d, d + 0.06)
    fc, cur = overlay_emoji(fc, '[a]', 2, d, 820, 1180, 'i')
    fc += ';%sformat=yuv420p[out]' % cur
    p = os.path.join(tmp, 'p_intro.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(I['ss']), '-t', '%.3f' % d, '-i', os.path.join(ROOT, I['clip']),
                    '-loop', '1', '-t', '%.3f' % dur, '-i', h, '-loop', '1', '-t', '%.3f' % dur, '-i', e,
                    '-filter_complex', fc, '-map', '[out]', '-t', '%.3f' % dur, '-an'] + ENC + [p], check=True)
    return p, dur

def main(spec_path):
    S = json.load(open(spec_path)); tmp = tempfile.mkdtemp(); parts, durs = [], []
    intro = S.get('intro')
    if intro:
        p, d0 = seg_intro(S, tmp); parts.append(p); durs.append(d0)
    hd = 0.0 if intro else S.get('hook_d', 2.6)   # cu intro, hook-ul e pe clipul de gaming; fără, e peste primul exercițiu
    for i, it in enumerate(S['items']):
        png = os.path.join(tmp, 't%d.png' % i); title_png('%d. %s' % (i + 1, it['title']), it.get('chip'), png)
        sp = it.get('speed', 1.0); dur = it['d'] / sp; t0 = hd if i == 0 else 0.0
        fc = '[0:v]setpts=(PTS-STARTPTS)/%.3f,fps=30,scale=1080:1920,setsar=1%s[v];' % (sp, punch(S))
        fc += ("[1:v]format=rgba,fade=t=in:st=%.2f:d=0.12:alpha=1[t];[v][t]overlay=x=0:y='-60*max(0\\,1-(t-%.2f)/0.16)':enable='gte(t\\,%.2f)'[a]"
               % (t0, t0, t0))
        cur = '[a]'; inputs = ['-ss', str(it['ss']), '-t', '%.3f' % it['d'], '-i', os.path.join(ROOT, it['clip']), '-loop', '1', '-t', '%.3f' % dur, '-i', png]
        if i == 0 and not intro and S.get('hook'):
            h = os.path.join(tmp, 'hook.png'); text_png(S['hook'], h, 62, 230); inputs += ['-loop', '1', '-t', '%.3f' % dur, '-i', h]
            fc += ";[%d:v]format=rgba,fade=t=out:st=%.2f:d=0.2:alpha=1[h];%s[h]overlay=0:0:enable='lt(t\\,%.2f)'[b]" % (n_in(inputs) - 1, hd - 0.2, cur, hd)
            cur = '[b]'
        if it.get('emoji'):
            e = os.path.join(tmp, 'e%d.png' % i); emoji_png(it['emoji'], e); inputs += ['-loop', '1', '-t', '%.3f' % dur, '-i', e]
            fc, cur = overlay_emoji(fc, cur, n_in(inputs) - 1, t0 + 0.25, 860, 1320, 'x%d' % i)
        if i == len(S['items']) - 1 and S.get('outro'):
            o = os.path.join(tmp, 'outro.png'); text_png([S['outro']], o, 56, 1500, bold=False); inputs += ['-loop', '1', '-t', '%.3f' % dur, '-i', o]
            st = dur - S.get('outro_d', 2.0)
            fc += ";[%d:v]format=rgba,fade=t=in:st=%.2f:d=0.25:alpha=1[ou];%s[ou]overlay=0:0:enable='gte(t\\,%.2f)'[c]" % (n_in(inputs) - 1, st, cur, st); cur = '[c]'
        fc += ';%sformat=yuv420p[out]' % cur
        p = os.path.join(tmp, 'p%d.mp4' % i)
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[out]', '-t', '%.3f' % dur, '-an'] + ENC + [p], check=True)
        parts.append(p); durs.append(dur)
    lst = os.path.join(tmp, 'l.txt'); open(lst, 'w').write(''.join("file '%s'\n" % p for p in parts))
    out = os.path.join(ROOT, S['out']); os.makedirs(os.path.dirname(out), exist_ok=True)
    joined = os.path.join(tmp, 'v.mp4'); total = sum(durs)
    if S.get('progress'):   # bara de progres sus: crește pe toată durata (oamenii văd că e scurt și rămân până la capăt)
        vf = ['-vf', "drawbox=x=40:y=196:w=1000:h=10:color=white@0.35:t=fill,drawbox=x=40:y=196:w='max(2\\,1000*t/%.3f)':h=10:color=0x8A3459:t=fill" % total] + ENC
    else:
        vf = ['-c', 'copy']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst] + vf + [joined], check=True)
    if not S.get('sfx'):
        os.replace(joined, out); print(out); return
    import sfx
    starts, acc = [], 0.0
    for d in durs: starts.append(acc); acc += d
    first = 1 if intro else 0
    ev = [(0.0, 'whoosh', 0.7), (intro['d'], 'boom', 1.0), (intro['d'] + 0.25, 'pop', 0.7)] if intro else [(0.0, 'boom', 0.8), (0.02, 'pop', 0.9)]
    for k in range(first, len(durs)):
        s0 = starts[k]
        if s0 > 0: ev.append((s0 - 0.22, 'whoosh', 0.9))
        tt = s0 + (hd if k == first else 0.0); ev.append((tt + 0.03, 'pop', 0.9))
        if S['items'][k - first].get('emoji'): ev.append((tt + 0.28, 'pop', 0.6))
    if S.get('outro'): ev.append((total - S.get('outro_d', 2.0), 'ding', 0.8))
    wav = os.path.join(tmp, 'sfx.wav'); sfx.timeline(ev, total, wav)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', joined, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True)
    print(out)

if __name__ == '__main__':
    main(sys.argv[1])
