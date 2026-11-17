#!/usr/bin/env python3
"""Videourile vorbite pentru Custom Program (Welcome, How to use, Safety, How to film your form).
Bucățile brute (telefonul nu trimite mai mult de ~15 s într-un mesaj) stau în studio/custom-program/clips/vorbite/<n>-<nume>-a.mov, -b.mov, -c.mov.
Le lipește în ordine, aplică grading-ul din curat.py, taie marginile (tocul ușii din stânga), curăță sunetul și pune un titlu mic, cu spațiere, în primele secunde.
Rulezi: python3 studio/custom-program/build_vorbite.py [1 2 3 4]  -> studio/custom-program/out/vorbit-<n>-<nume>.mp4"""
import glob, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'studio/montaj'))
from curat import GRADE
CLIPS, OUT = os.path.join(HERE, 'clips/vorbite'), os.path.join(HERE, 'out')
FONT = os.path.join(ROOT, 'brand/reels-overlays/fonts/Poppins-Medium.ttf')
VIDEOS = {1: ('welcome', 'Welcome'), 2: ('how-to-use', 'How to use your program'), 3: ('safety', 'Safety first'), 4: ('film-your-form', 'How to film your form')}
AUDIO = 'highpass=f=80,afftdn=nf=-28,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=9'

def title_png(text, path):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(im), ImageDraw.Draw(sh); f = ImageFont.truetype(FONT, 44); t = text.upper(); track = 6
    w = sum(d.textlength(c, font=f) for c in t) + track * (len(t) - 1); x = (1080 - w) / 2; y = 250
    for c in t:
        ds.text((x, y), c, font=f, fill=(0, 0, 0, 150)); d.text((x, y), c, font=f, fill=(255, 255, 255, 255)); x += d.textlength(c, font=f) + track
    Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), im).save(path)

def build(n):
    slug, title = VIDEOS[n]
    parts = sorted(glob.glob(os.path.join(CLIPS, '%d-%s-*.mov' % (n, slug))))
    if not parts: print('lipsesc clipurile pentru', n); return
    tmp = tempfile.mkdtemp(); png = os.path.join(tmp, 't.png'); title_png(title, png)
    ins = sum([['-i', p] for p in parts], []) + ['-loop', '1', '-i', png]
    k = len(parts)
    fc = ''.join('[%d:v]fps=30,scale=1080:1920,setsar=1[v%d];[%d:a]aresample=48000[a%d];' % (i, i, i, i) for i in range(k))
    fc += ''.join('[v%d][a%d]' % (i, i) for i in range(k)) + 'concat=n=%d:v=1:a=1[vc][ac];' % k
    # zoom 4% (scapă de tocul ușii și de podea), apoi culoarea
    fc += '[vc]crop=iw*0.96:ih*0.96:iw*0.02:ih*0.02,scale=1080:1920:flags=lanczos,%s,format=yuv420p[vg];' % GRADE
    fc += '[%d:v]format=rgba,fade=t=in:st=0.3:d=0.5:alpha=1,fade=t=out:st=3.0:d=0.6:alpha=1[tt];' % k
    fc += "[vg][tt]overlay=0:0:shortest=1:enable='lt(t,3.7)',fade=t=in:st=0:d=0.25[v];"
    fc += '[ac]%s[a]' % AUDIO
    out = os.path.join(OUT, 'vorbit-%d-%s.mp4' % (n, slug)); os.makedirs(OUT, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', out], check=True)
    print('gata:', out)

if __name__ == '__main__':
    for n in ([int(a) for a in sys.argv[1:]] or VIDEOS): build(n)
