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
 dict(title='Weekendul 17–18 octombrie', where='București → țară', goal='Mutarea gata; PDF-ul pregătit; reel-urile filmate', days=[
   ('Sâm 17', [('V', 'Ultimele lucruri din mutare'), ('C', 'Dacă apuci dimineața: R1–R4 și KM1–KM4 (lista de filmat)'), ('V', 'Drum la țară')]),
   ('Dum 18', [('A', 'Payhip, PDF pe link permanent, grup MailerLite + email de bun venit'), ('A', 'Documente pentru avocat'), ('A', 'Instagram: arhivare + cerere de review'), ('A', 'Contract Twitch: exclusivitate'), ('C', 'Filmat R1–R4, KM1–KM4, dacă n-ai făcut sâmbătă'), ('V', 'Seara înapoi în București')]),
 ]),
 dict(title='Săptămâna 1 · 19–25 octombrie', where='București; weekend la țară', goal='PDF-ul live și primele reel-uri', days=[
   ('Lun 19', [('S', 'Move Monday 10:00 (3 h)'), ('C', 'Montaj R1–R4 + 6 descrieri'), ('A', 'Email la avocat (seara)'), ('A', 'IBAN către cei 2 clienți')]),
   ('Mar 20', [('A', 'PDF live: formular, Linktree, test cu alt email (până la 12)'), ('C', 'Montaj KM1, KM2'), ('P', 'R1 · 17:00 (Trial Reel)'), ('G', 'Sală, dimineața')]),
   ('Mie 21', [('S', 'Cook with me + cacao Bewit'), ('C', 'K1 clătite filmat de sus + poze ton'), ('C', 'Montaj K1'), ('P', 'R2 · 17:00'), ('G', 'Sală (sau vineri)')]),
   ('Joi 22', [('V', 'Cele 2 terapii'), ('P', 'R3 · 17:00 · KM1 · 19:00'), ('A', 'Discord abonați, testat')]),
   ('Vin 23', [('S', 'Game night: pauză cu coarda, Revu la final'), ('P', 'Carusel C1'), ('C', '3 clipuri din stream')]),
   ('Sâm 24', [('V', 'Liber · drum la țară cu cutiile'), ('G', 'Sală (opțional)')]),
   ('Dum 25', [('V', 'Ceasul −1 h (ora de iarnă)'), ('A', 'Cifre + cele 3 întrebări'), ('A', 'eSIM, 2FA, program Twitch'), ('A', 'Lista lunară octombrie'), ('V', 'Vinted · seara înapoi')]),
 ]),
 dict(title='Săptămâna 2 · 26 octombrie – 1 noiembrie', where='București; din 29 oct, Turcia', goal='Tot ce pleacă e programat; zbor liniștit', days=[
   ('Lun 26', [('S', 'Move Monday 10:00'), ('C', 'Filmat B1–B4 (+ KM3–KM4 dacă lipsesc)'), ('A', 'Go / no-go: contabilă + avocat'), ('A', 'Copii în 2 locuri')]),
   ('Mar 27', [('C', 'Montaj B1'), ('P', 'Programat: K1, B1, KM2, R4, K5 + TikTok până pe 6 nov'), ('A', 'Notar, dacă e fixat'), ('V', 'Bagaj, asigurare, check-in'), ('G', 'Sală dimineața (fără notar)')]),
   ('Mie 28', [('S', 'Cook with me (ultimul din RO) + K4 somon'), ('A', 'Avocat: tranșa 2 (1.500 lei)'), ('A', 'Răspuns automat KM și Google'), ('V', 'Echipamentul de stream împachetat'), ('P', 'K1 (programat)')]),
   ('Joi 29', [('V', 'Zbor după-amiază'), ('V', 'Seara: testul colțului'), ('P', 'B1 · KM2 (programate)')]),
   ('Vin 30', [('S', 'Game night (opțional)'), ('P', 'R4 (programat)'), ('A', 'Verifici postările programate')]),
   ('Sâm 31', [('V', 'Liber'), ('G', 'Sală')]),
   ('Dum 1', [('A', 'Cifre + cele 3 întrebări'), ('A', 'Test înscriere PDF · domeniul site-ului'), ('V', 'Păr'), ('G', 'Sală'), ('S', 'Chill Sunday doar dacă ai sărit vineri')]),
 ]),
 dict(title='Săptămâna 3 · 2–8 noiembrie', where='Turcia (program pe ora României)', goal='Ritmul din Turcia; e-book partea 1', days=[
   ('Lun 2', [('S', 'Move Monday 10:00 RO (11:00 TR)'), ('C', 'Montaj B2 + reelul cu coarda'), ('P', 'Programat B2, reel din stream; TikTok 7–12 nov')]),
   ('Mar 3', [('C', 'E-book Canva, partea 1 (pag. 5, 8, 15, 3, 33)'), ('C', 'Montaj B3'), ('P', 'B2 (programat)'), ('G', 'Sală')]),
   ('Mie 4', [('S', 'Cook with me + cacao Bewit'), ('C', 'KM3 montat (opțional)')]),
   ('Joi 5', [('A', 'Media kit (dacă go/no-go nu e „nu”)'), ('C', 'Carusel C2'), ('P', 'K5 · KM3 (programate)'), ('G', 'Sală')]),
   ('Vin 6', [('S', 'Game night'), ('A', 'TikTok programat 13–16 nov'), ('P', 'Reel din stream (programat)')]),
   ('Sâm 7', [('V', 'Liber'), ('G', 'Sală')]),
   ('Dum 8', [('S', 'Sesiune abonați, doar cu „da” scris'), ('A', 'Cifre + cele 3 întrebări'), ('P', 'Carusel C2 (programat)'), ('G', 'Sală')]),
 ]),
 dict(title='Săptămâna 4 · 9–15 noiembrie', where='Turcia; 15 nov întoarcere', goal='E-book exportat; branduri; bilanț', days=[
   ('Lun 9', [('S', 'Move Monday 10:00 RO'), ('C', 'Montaj K4 + B4'), ('P', 'Programat K4, B4')]),
   ('Mar 10', [('C', 'E-book partea 2 + export'), ('P', 'B3 (programat)'), ('G', 'Sală')]),
   ('Mie 11', [('S', 'Cook with me'), ('C', 'KM4 montat (opțional)')]),
   ('Joi 12', [('A', 'Emailuri către branduri (doar cu „da”)'), ('A', 'Brief pentru copertă'), ('P', 'K4 · KM4 (programate)'), ('G', 'Sală')]),
   ('Vin 13', [('S', 'Game night: notezi viewerii'), ('P', 'B4 (programat)')]),
   ('Sâm 14', [('V', 'Liber · bagajul'), ('G', 'Sală')]),
   ('Dum 15', [('V', 'Întoarcere'), ('A', 'Bilanț scurt'), ('V', 'Colțul de acasă pregătit')]),
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
    out.append('<span class="foot">Sâmbăta e liberă · 3 streamuri pe săptămână · 4 vizite la sală · Bifezi pătrățelul când e gata</span></div></section>')
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
