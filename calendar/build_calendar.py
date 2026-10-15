#!/usr/bin/env python3
"""Calendarele săptămânale de printat (A4 orizontal), 17 oct – 15 nov 2026, plus o pagină goală.
Rulezi: python3 calendar/build_calendar.py  ->  calendar/Calendar-saptamanal.pdf"""
import html, os, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CAT = {  # cod: (eticheta, fundal, text)
    'S': ('Stream', '#E9E1F7', '#4C3A78'),
    'C': ('Conținut', '#DDE9F7', '#2A5580'),
    'P': ('Postare', '#F8DCE6', '#8A3459'),
    'A': ('Bani și admin', '#FBEBC8', '#7A5410'),
    'G': ('Sală', '#D8F0E4', '#1C6550'),
    'V': ('Viață', '#EEEAE6', '#4A4450'),
}

WEEKS = [
 dict(title='Vineri 16 – duminică 18 octombrie', where='București → țară (sâmbătă)', goal='Mutarea gata; reel-urile filmate la țară', days=[
   ('Vin 16', [('V', 'Ultimele lucruri mutate'), ('A', 'Avocat: tranșa 1 (1.500 lei)'), ('A', 'Twitch: goal-uri, cadoul de la Kelly, About, 5 clipuri'), ('C', 'Dacă apuci: R1–R4 la un perete simplu'), ('S', 'Game night, doar dacă ai energie')]),
   ('Sâm 17', [('G', 'Sală, dimineața'), ('V', 'Drum la țară'), ('C', 'Filmat: R1–R4, KM1–KM4 (lista de filmat)'), ('C', 'Dacă ai timp: K1 clătite + poze ton'), ('S', 'Opțional: stream scurt de la țară')]),
   ('Dum 18', [('V', 'Liber'), ('V', 'Seara înapoi în București')]),
 ]),
 dict(title='Săptămâna 1 · 19–25 octombrie', where='București; weekend la țară', goal='PDF-ul gratuit live, primele reel-uri, emailurile către branduri; TikTok zilnic', days=[
   ('Lun 19', [('S', 'Stream 10–11 (Move Monday)'), ('C', 'Montaj R1–R4 + descrieri'), ('A', 'Adresele de colaborări la cele 6 branduri'), ('A', 'TikTok @kristinemaia + primul clip'), ('A', 'Instagram: arhivare + review'), ('G', 'Sală')]),
   ('Mar 20', [('A', 'PDF-ul pe Payhip (ghidul pas cu pas) + test'), ('C', 'Montaj KM1, KM2'), ('P', 'R1 · 17:00, după test'), ('S', 'Stream de marți'), ('G', 'Sală')]),
   ('Mie 21', [('S', 'Cook with me + cacao Bewit (#ad)'), ('A', 'Media kit (90 min)'), ('C', 'Montaj K1, dacă e filmat'), ('P', 'R2 · 17:00; programat R3 + KM1'), ('G', 'Sală')]),
   ('Joi 22', [('V', 'Liber'), ('P', 'R3 și KM1 ies singure')]),
   ('Vin 23', [('S', 'Game night: pauză cu coarda, Revu la final'), ('A', '6 emailuri către branduri'), ('A', 'Avocat: tranșa 2 (ultima)'), ('P', 'Carusel C1'), ('G', 'Sală')]),
   ('Sâm 24', [('G', 'Sală'), ('V', 'Drum la țară cu cutiile'), ('C', 'Filmat: B1–B4, KM3–KM4, K4, reel Bewit, reel Revu, poza de copertă'), ('V', 'Vinted')]),
   ('Dum 25', [('V', 'Liber'), ('V', 'Seara înapoi în București')]),
 ]),
 dict(title='Săptămâna 2 · 26 octombrie – 1 noiembrie', where='București; din 29 oct, Turcia', goal='Tot ce pleacă e programat; e-book-ul gata, ideal', days=[
   ('Lun 26', [('S', 'Stream 10–11'), ('C', 'Ales dublele + descrieri'), ('C', 'E-book partea 1'), ('A', 'Discord abonați · program Twitch'), ('G', 'Sală')]),
   ('Mar 27', [('S', 'Stream de marți'), ('C', 'Montaj B1–B4, K4'), ('C', 'E-book partea 2 + export'), ('P', 'Programat IG + TikTok până pe 6 nov'), ('G', 'Sală')]),
   ('Mie 28', [('S', 'Ultimul stream din România'), ('A', 'Răspuns automat pe KM'), ('V', 'Bagaj · clipurile pe laptop și stick'), ('G', 'Sală')]),
   ('Joi 29', [('V', 'Zbor după-amiază'), ('V', 'Seara: testul colțului'), ('P', 'B1 · KM2 (programate)')]),
   ('Vin 30', [('S', 'Game night (opțional)'), ('A', 'Revenire la branduri (un mesaj)'), ('P', 'R4 (programat)'), ('G', 'Sală (opțional)')]),
   ('Sâm 31', [('G', 'Sală'), ('A', 'Cifre + cele 3 întrebări'), ('A', 'Lista lunară'), ('C', 'Montaj')]),
   ('Dum 1', [('V', 'Liber'), ('V', 'Păr')]),
 ]),
 dict(title='Săptămâna 3 · 2–8 noiembrie', where='Turcia (program pe ora României)', goal='Ritmul din Turcia: 4 streamuri, montaj, TikTok zilnic', days=[
   ('Lun 2', [('S', 'Move Monday 10:00 RO (11:00 TR)'), ('C', 'Montaj B2, reel coarda, reel Bewit'), ('P', 'Programate; TikTok 7–12 nov'), ('G', 'Sală')]),
   ('Mar 3', [('S', 'Stream de marți'), ('C', 'Montaj B3 + carusel C2'), ('P', 'B2 (programat)'), ('G', 'Sală')]),
   ('Mie 4', [('S', 'Cook with me + cacao Bewit'), ('C', 'KM3 (opțional)'), ('P', 'Reel Bewit (programat)'), ('G', 'Sală')]),
   ('Joi 5', [('V', 'Liber'), ('P', 'K5 și KM3 ies singure')]),
   ('Vin 6', [('S', 'Game night + Revu'), ('A', 'TikTok 13–16 nov'), ('P', 'Reel cu coarda (programat)'), ('G', 'Sală')]),
   ('Sâm 7', [('G', 'Sală'), ('C', 'Montaj: ce a rămas'), ('A', 'Cifre')]),
   ('Dum 8', [('V', 'Liber'), ('P', 'Carusel C2 iese singur')]),
 ]),
 dict(title='Săptămâna 4 · 9–15 noiembrie', where='Turcia; 15 nov întoarcere', goal='Ultimele reel-uri programate; bilanț', days=[
   ('Lun 9', [('S', 'Move Monday 10:00 RO'), ('C', 'Montaj K4, B4, reel Revu'), ('P', 'Programate'), ('G', 'Sală')]),
   ('Mar 10', [('S', 'Stream de marți'), ('A', 'Brief copertă e-book'), ('P', 'B3 (programat)'), ('G', 'Sală')]),
   ('Mie 11', [('S', 'Cook with me'), ('C', 'KM4 (opțional)'), ('P', 'Reel Revu (programat)'), ('G', 'Sală')]),
   ('Joi 12', [('V', 'Liber'), ('P', 'K4 și KM4 ies singure')]),
   ('Vin 13', [('S', 'Game night: notezi viewerii'), ('P', 'B4 (programat)'), ('G', 'Sală')]),
   ('Sâm 14', [('G', 'Sală'), ('V', 'Bagaj'), ('A', 'Bilanț scurt')]),
   ('Dum 15', [('V', 'Întoarcere'), ('V', 'Colțul de acasă pregătit')]),
 ]),
 dict(title='Săptămâna · ______________________', where='', goal='', days=[(d, []) for d in ('Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri', 'Sâmbătă', 'Duminică')], blank=True),
]

CSS = """
@page{size:A4 landscape;margin:9mm}
*{box-sizing:border-box}
body{margin:0;font-family:Figtree,system-ui,sans-serif;color:#2B2431;background:#fff}
.pg{page-break-after:always;height:190mm;display:flex;flex-direction:column}
.pg:last-child{page-break-after:auto}
.hd{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:3mm}
h1{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:21pt;margin:0;letter-spacing:-.02em}
.meta{font-size:9.5pt;color:#5C5466;text-align:right}
.meta b{color:#2B2431}
.grid{flex:1;display:grid;gap:2mm}
.day{border:1px solid #DDD5CF;border-radius:3mm;padding:2mm;display:flex;flex-direction:column;min-width:0}
.dn{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:700;font-size:12pt;margin-bottom:1.5mm}
.it{font-size:8.6pt;line-height:1.25;border-radius:1.6mm;padding:1.2mm 1.6mm;margin-bottom:1.2mm}
.it .bx{display:inline-block;width:3mm;height:3mm;border:1px solid currentColor;border-radius:.6mm;margin-right:1.2mm;vertical-align:-.4mm}
.lines{flex:1;margin-top:1mm;background:repeating-linear-gradient(to bottom,transparent 0,transparent 5.2mm,#E6DFD9 5.2mm,#E6DFD9 5.5mm)}
.leg{display:flex;gap:4mm;font-size:8.5pt;margin-top:2.5mm;align-items:center;flex-wrap:wrap}
.leg span{display:inline-flex;align-items:center;gap:1.2mm}
.leg i{display:inline-block;width:3.5mm;height:3.5mm;border-radius:1mm}
.foot{margin-left:auto;color:#5C5466}
"""

def page(w):
    n = len(w['days'])
    cols = 'repeat(%d,1fr)' % n
    out = ['<section class="pg"><div class="hd"><h1>%s</h1><div class="meta">' % html.escape(w['title'])]
    if w.get('where'):
        out.append('<b>Unde:</b> %s<br><b>Ținta săptămânii:</b> %s' % (html.escape(w['where']), html.escape(w['goal'])))
    else:
        out.append('<b>Unde:</b> ____________________ &nbsp; <b>Ținta:</b> ______________________________')
    out.append('</div></div><div class="grid" style="grid-template-columns:%s">' % cols)
    for name, items in w['days']:
        out.append('<div class="day"><div class="dn">%s</div>' % html.escape(name))
        for c, t in items:
            _, bg, fg = CAT[c]
            out.append('<div class="it" style="background:%s;color:%s"><span class="bx"></span>%s</div>' % (bg, fg, html.escape(t)))
        out.append('<div class="lines"></div></div>')
    out.append('</div><div class="leg">')
    for c, (lab, bg, fg) in CAT.items():
        out.append('<span><i style="background:%s;border:1px solid %s"></i>%s</span>' % (bg, fg, lab))
    out.append('<span class="foot">Liber joia și duminica · streamuri luni, marți, miercuri, vineri · sală 5 zile · filmat sâmbăta, la țară · TikTok zilnic · bifezi pătrățelul</span></div></section>')
    return ''.join(out)

def build():
    doc = ('<!doctype html><html lang="ro"><head><meta charset="utf-8">'
           '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700&family=Figtree:wght@500;600&display=swap" rel="stylesheet">'
           '<style>%s</style></head><body>%s</body></html>') % (CSS, ''.join(page(w) for w in WEEKS))
    src = os.path.join(HERE, 'calendar.html')
    open(src, 'w', encoding='utf-8').write(doc)
    js = r"""
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.argv[2], { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: process.argv[3], format: 'A4', landscape: true, printBackground: true, preferCSSPageSize: true });
  await p.setViewportSize({ width: 1123, height: 794 });
  const pgs = await p.$$('.pg'); await b.close(); })();
"""
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
        f.write(js)
    env = dict(os.environ)
    env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', f.name, src, os.path.join(HERE, 'Calendar-saptamanal.pdf'), os.path.join(HERE, 'calendar-saptamana-1.png')], check=True, env=env)
    os.unlink(f.name)
    print('gata:', os.path.join(HERE, 'Calendar-saptamanal.pdf'))

if __name__ == '__main__':
    build()
