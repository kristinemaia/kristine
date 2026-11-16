#!/usr/bin/env python3
"""Reel de mâncare în stil „estetic” (ca exemplele de meal prep): tăieturi scurte (~1 s) pe prim-planuri cu mâncarea,
un singur titlu mic, elegant, care stă pe tot reel-ul, sunetul real al gătitului (ASMR) și un card de final cu contul.
Fără emoji, fără cronometre, fără flash. Muzica o pui din aplicație.
Rulezi: python3 studio/montaj/reel_estetic.py studio/montaj/<spec>.json
Spec: {"out", "title", "handle": "@kristinemaia11", "end_small": "Save this recipe",
       "segs": [{"clip", "audio", "ss", "d", "speed", "crop": "w:h:x:y" (în pixeli 1080x1920), "zoom": 0.05}]}"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
FONTS = os.path.join(ROOT, 'brand/reels-overlays/fonts')
ENC = ['-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-r', '30', '-pix_fmt', 'yuv420p']
SR = 48000

def spaced(d, xy, txt, f, fill, track):
    x, y = xy
    for ch in txt:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track

def spaced_w(d, txt, f, track): return sum(d.textlength(c, font=f) for c in txt) + track * (len(txt) - 1)

def title_png(title, handle, path):
    """titlul mic, cu litere rare, alb, cu umbră fină; contul dedesubt, mai mic"""
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); sh = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(im), ImageDraw.Draw(sh)
    f = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Medium.ttf'), 46); t = title.upper(); w = spaced_w(d, t, f, 3)
    for dd, fill, off in ((ds, (0, 0, 0, 150), 3), (d, (255, 255, 255, 255), 0)): spaced(dd, ((1080 - w) / 2, 700 + off), t, f, fill, 3)
    if handle:
        f2 = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Medium.ttf'), 26); w2 = spaced_w(d, handle, f2, 1)
        for dd, fill, off in ((ds, (0, 0, 0, 120), 2), (d, (255, 255, 255, 200), 0)): spaced(dd, ((1080 - w2) / 2, 770 + off), handle, f2, fill, 1)
    Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), im).save(path)

def q_png(text, path, y=845):
    """întrebarea mică de sub titlu (interactivitate, dar discretă): crem, cu umbră fină"""
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); sh = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(im), ImageDraw.Draw(sh); f = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Medium.ttf'), 36)
    w = spaced_w(d, text, f, 1)
    for dd, fill, off in ((ds, (0, 0, 0, 160), 3), (d, (255, 249, 246, 255), 0)): spaced(dd, ((1080 - w) / 2, y + off), text, f, fill, 1)
    Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), im).save(path)

def end_png(frame, handle, small, path, big=None):
    """ultimul cadru, întunecat, cu o pictogramă de cameră desenată, contul și un rând mic"""
    im = Image.open(frame).convert('RGBA').resize((1080, 1920)).filter(ImageFilter.GaussianBlur(6))
    im = Image.alpha_composite(im, Image.new('RGBA', im.size, (12, 8, 10, 165))); d = ImageDraw.Draw(im)
    if handle:   # pictograma de cameră + contul (doar dacă specul are „handle”)
        cx, cy, s = 540, 880, 120
        d.rounded_rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2], 34, outline=(255, 255, 255, 255), width=9)
        d.ellipse([cx - 27, cy - 27, cx + 27, cy + 27], outline=(255, 255, 255, 255), width=9); d.ellipse([cx + 28, cy - 42, cx + 42, cy - 28], fill=(255, 255, 255, 255))
        f = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Medium.ttf'), 40); w = spaced_w(d, handle, f, 2); spaced(d, ((1080 - w) / 2, 980), handle, f, (255, 255, 255, 255), 2)
    if big:   # întrebarea mare de final, pe 1–2 rânduri
        fb = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Medium.ttf'), 58)
        for k, line in enumerate(big):
            t = line.upper(); w = spaced_w(d, t, fb, 4); spaced(d, ((1080 - w) / 2, 760 + k * 80), t, fb, (255, 255, 255, 255), 4)
    if small:
        f2 = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Medium.ttf'), 30 if (handle or big) else 44); t = small.upper(); w2 = spaced_w(d, t, f2, 3 if handle else 5)
        y2 = 1050 if handle else (760 + len(big) * 80 + 40 if big else 930)
        spaced(d, ((1080 - w2) / 2, y2), t, f2, (255, 255, 255, 200 if (handle or big) else 240), 3 if (handle or big) else 5)
    im.save(path)

def main(spec):
    S = json.load(open(spec)); tmp = tempfile.mkdtemp(); parts, auds, total = [], [], 0.0
    tp = os.path.join(tmp, 'title.png'); title_png(S['title'], S.get('handle'), tp)
    for i, g in enumerate(S['segs']):
        sp = g.get('speed', 1.0); dur = g['d'] / sp; z = g.get('zoom', 0.04)
        crop = ('crop=%s,' % g['crop']) if g.get('crop') else ''
        # o apropiere lentă pe fiecare cadru (cum se mișcă telefonul în mână), fără flash
        vf = ("[0:v]setpts=(PTS-STARTPTS)/%.3f,fps=30,%sscale=1080:1920:flags=lanczos,setsar=1,"
              "scale=w='trunc(1080*(1+%.3f*t/%.3f)/2)*2':h='trunc(1920*(1+%.3f*t/%.3f)/2)*2':eval=frame,crop=1080:1920[v];"
              "[1:v]format=rgba[t];[v][t]overlay=0:0[w]") % (sp, crop, z, dur, z, dur)
        extra = []
        if g.get('q'):   # întrebarea segmentului: apare lin după 0,15 s
            qp = os.path.join(tmp, 'q%d.png' % i); q_png(g['q'], qp); extra = ['-loop', '1', '-t', '%.3f' % dur, '-i', qp]
            vf += ";[2:v]format=rgba,fade=t=in:st=0.15:d=0.25:alpha=1[q];[w][q]overlay=0:0,format=yuv420p[out]"
        else:
            vf += ";[w]format=yuv420p[out]"
        p = os.path.join(tmp, 'p%d.mp4' % i)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(g['ss']), '-t', '%.3f' % g['d'], '-i', os.path.join(ROOT, g['clip']),
                        '-loop', '1', '-t', '%.3f' % dur, '-i', tp] + extra + ['-filter_complex', vf, '-map', '[out]', '-t', '%.3f' % dur, '-an'] + ENC + [p], check=True)
        a = os.path.join(tmp, 'a%d.wav' % i)
        if g.get('audio'):
            tempo = '' if abs(sp - 1) < 1e-3 else ',atempo=%.3f' % sp
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(g['ss']), '-t', '%.3f' % g['d'], '-i', os.path.join(ROOT, g['audio']), '-vn',
                            '-af', 'aresample=%d,pan=mono|c0=0.5*c0+0.5*c1%s,afade=t=in:d=0.04,afade=t=out:st=%.3f:d=0.06,apad' % (SR, tempo, max(0, dur - 0.06)),
                            '-t', '%.3f' % dur, a], check=True)
        else:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=%d:cl=mono' % SR, '-t', '%.3f' % dur, a], check=True)
        parts.append(p); auds.append(a); total += dur
    # cardul de final
    last = S['segs'][-1]; fr = os.path.join(tmp, 'last.png')
    crop = (',crop=%s' % last['crop']) if last.get('crop') else ''
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % (last['ss'] + last['d'] - 0.1), '-i', os.path.join(ROOT, last['clip']), '-frames:v', '1',
                    '-vf', 'scale=1080:1920%s,scale=1080:1920' % crop, fr], check=True)
    ep = os.path.join(tmp, 'end.png'); end_png(fr, S.get('handle', ''), S.get('end_small'), ep, S.get('end_big')); ed = S.get('end_d', 2.0)
    p = os.path.join(tmp, 'p_end.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', '%.3f' % ed, '-i', ep, '-vf', 'fade=t=in:st=0:d=0.25,format=yuv420p', '-t', '%.3f' % ed] + ENC + [p], check=True)
    a = os.path.join(tmp, 'a_end.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=%d:cl=mono' % SR, '-t', '%.3f' % ed, a], check=True)
    parts.append(p); auds.append(a); total += ed
    for name, items in (('v', parts), ('a', auds)):
        open(os.path.join(tmp, name + '.txt'), 'w').write(''.join("file '%s'\n" % x for x in items))
    v = os.path.join(tmp, 'v.mp4'); au = os.path.join(tmp, 'a.wav'); X = S.get('xfade', 0)
    if X:   # trecere lină (dizolvare) între cadre, și la imagine, și la sunet
        durs = []
        for pth in parts:
            durs.append(float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', pth], capture_output=True, text=True).stdout))
        vin, fc, cur, off = [], [], '[0:v]', 0.0
        for k, pth in enumerate(parts): vin += ['-i', pth]
        for k in range(1, len(parts)):
            off += durs[k - 1] - X
            fc.append('%s[%d:v]xfade=transition=fade:duration=%.2f:offset=%.3f[x%d]' % (cur, k, X, off, k)); cur = '[x%d]' % k
        fc.append('%sformat=yuv420p[out]' % cur)
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + vin + ['-filter_complex', ';'.join(fc), '-map', '[out]'] + ENC + [v], check=True)
        ain, fa, cur = [], [], '[0:a]'
        for k, pth in enumerate(auds): ain += ['-i', pth]
        for k in range(1, len(auds)):
            fa.append('%s[%d:a]acrossfade=d=%.2f:c1=tri:c2=tri[y%d]' % (cur, k, X, k)); cur = '[y%d]' % k
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ain + ['-filter_complex', ';'.join(fa), '-map', cur, au], check=True)
        total -= X * (len(parts) - 1)
    else:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'v.txt'), '-c', 'copy', v], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'a.txt'), au], check=True)
    out = os.path.join(ROOT, S['out']); os.makedirs(os.path.dirname(out), exist_ok=True)
    # sunetul gătitului, adus la un nivel bun (ASMR), fără să se audă fâșâitul de fond
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-i', au, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-af', 'highpass=f=80,afftdn=nf=-30,loudnorm=I=-18:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR),
                    '-shortest', '-movflags', '+faststart', out], check=True)
    print(out, '%.1f s' % total)

if __name__ == '__main__':
    main(sys.argv[1])
