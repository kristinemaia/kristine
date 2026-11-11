#!/usr/bin/env python3
"""
„Farfuria lui Cem”: fișă de bucătărie (A4 orizontal) cu ce pui la fiecare masă, pe componente:
proteină, carbohidrați, legume, grăsime, fruct. Toate gramele sunt pentru mâncarea GĂTITĂ.

Gramajele vin din ghidul lui Cem (Kristine-ghid-bucatarie1.pdf, noiembrie 2026). Variantele din aceeași
căsuță au cam aceleași calorii, ca totalul zilei să rămână același oricum le combini. Caloriile și
proteinele sunt estimările noastre (ghidul lui nu dă un total).

Rulezi:   python3 library/build_farfuria_cem.py
Rezultat: FARFURIA-LUI-CEM.pdf
"""
import os
import subprocess
import sys
import tempfile

from build_bucataria_cem import CSS

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "FARFURIA-LUI-CEM.pdf")

EXTRA = """
@page { size: A4 landscape; margin: 9mm 10mm 10mm; }
body { font-size:8.3pt; line-height:1.24; }
h1 { font-size:21pt; }
.top { display:flex; justify-content:space-between; align-items:flex-end; gap:14px; margin-bottom:5px; }
.top .sub { margin:3px 0 0; font-size:9.2pt; max-width:150mm; }
.tot { display:flex; gap:6px; }
.tot div { background:var(--soft); border-radius:8px; padding:5px 9px; text-align:right; }
.tot b { display:block; font-family:"Inter Display","Inter",sans-serif; font-size:13pt; font-weight:800; letter-spacing:-.01em; }
.tot span { font-size:7.4pt; color:var(--muted); letter-spacing:.05em; text-transform:uppercase; font-weight:700; }
table.f th { font-size:7.2pt; padding:3px 5px; }
table.f td { padding:4px 5px 4px; }
table.f td.m { background:var(--soft); }
table.f td.m b { display:block; font-family:"Inter Display","Inter",sans-serif; font-size:11.5pt; font-weight:800; letter-spacing:-.01em; }
table.f td.m span { display:block; color:var(--muted); font-size:7.8pt; margin-top:2px; }
table.f td.m em { display:block; font-style:normal; font-size:7.6pt; font-weight:700; color:var(--k-ink); margin-top:4px; }
ul.o { list-style:none; padding:0; margin:0; }
ul.o li { margin:0 0 1.5px; padding-left:10px; position:relative; }
ul.o li::before { content:""; position:absolute; left:0; top:.55em; width:4px; height:4px; border-radius:50%; background:var(--muted); }
ul.o li small { color:var(--muted); font-size:7.6pt; }
.no { color:var(--muted); font-weight:700; }
.p2 { break-before:page; }
.p2 h2 { font-size:17pt; margin-bottom:8px; }
.low { display:grid; grid-template-columns:1.2fr 1fr; gap:12px; font-size:10pt; line-height:1.4; }
.low .box { padding:10px 12px; margin:0 0 12px; }
.low table.c td, .low table.c th { padding:5px 7px; }
.low table.c th { font-size:8pt; }
table.c { margin:0; }
table.c td, table.c th { padding:2px 5px; }
table.c td:nth-child(2), table.c td:nth-child(3) { text-align:right; font-variant-numeric:tabular-nums; }
table.c th:nth-child(2), table.c th:nth-child(3) { text-align:right; }
.foot { color:var(--muted); font-size:7.4pt; margin-top:5px; }
"""


def o(*items):
    return '<ul class="o">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


ROWS = [
    ("Mic dejun", "≈500 kcal · ≈33 g proteină", "",
     o("<b>2 ouă + 4 albușuri</b> (≈130 ml albuș lichid), omletă",
       "<b>3 ouă + 2 albușuri</b>: fierte (5 ouă, la 2 scoți gălbenușul) sau la tigaie",
       "<b>1 ou fiert + 4 albușuri</b>, doar la terci"),
     o("<b>2 felii pâine integrală</b> (≈60 g)",
       "<b>1 lipie integrală</b> (≈60 g)",
       "<b>60 g fulgi de ovăz</b> (cântăriți cruzi) + 300 ml apă: terci"),
     o("<b>150–200 g</b> la tigaie: ardei, ceapă, spanac, ciuperci, praz, dovlecel",
       "+ <b>100 g</b> crude: castravete, rucola",
       "<small>la terci: fără legume</small>"),
     o("<b>1 linguriță ulei + 5 măsline</b>",
       "<b>½ linguriță ulei + ½ avocado</b> (≈70 g)",
       "<b>20 g nucă</b>, la terci",
       "<small>la ouăle fierte: nimic</small>"),
     o("<b>½ banană</b> la terci", "<b>1 portocală mare</b> la ouăle fierte", "<small>la omletă: fără</small>")),

    ("Prânz", "≈550 kcal · ≈50 g proteină", "",
     o("<b>150–160 g piept de pui</b>",
       "<b>160 g pulpe de pui</b>",
       "<b>1 conservă ton</b> (≈120 g scurs), + 1 ou fiert când e cu quinoa",
       "<b>120 g pui + ≈300 ml supă de linte</b>"),
     o("<b>1 lipie integrală</b> (≈60 g): wrap",
       "<b>240 g hrișcă</b>",
       "<b>180 g quinoa</b>",
       "<b>150 g bulgur</b>",
       "<b>250 g cartofi fierți</b> sau cartof dulce",
       "<b>150 g năut</b>, doar lângă ton",
       "<small>la supă: 1 felie pâine (≈30 g)</small>"),
     o("<b>150 g</b> crude: castravete, salată, ceapă roșie, pătrunjel, ceapă verde, rodie",
       "+ <b>50 g ardei copți</b>"),
     o("<b>1 linguriță ulei</b> în sos, cu lămâie",
       "<b>1 lingură pesto</b>",
       "la wrap: <b>1 linguriță muștar</b>, fără ulei"),
     o("<b>1 măr</b>, la wrap", "<small>în rest: fără</small>")),

    ("Înainte de sală", "≈100 kcal", "Zi de odihnă: doar cafea",
     '<span class="no">–</span>', '<span class="no">–</span>', '<span class="no">–</span>', '<span class="no">–</span>',
     "<b>1 banană</b> · <b>2 curmale</b> · <b>2 mandarine</b> · <b>1 măr</b> <small>+ cafea simplă</small>"),

    ("După sală", "≈850 kcal · ≈50 g proteină", "Masa mare a zilei",
     o("<b>180 g chiftele</b>",
       "<b>160 g pulpe de pui</b>",
       "<b>160 g sote de vită</b>",
       "<b>180 g piept de pui</b> (pe pizza: 130 g)",
       "<b>150 g chiftea de burger</b>"),
     o("<b>250 g bulgur</b>",
       "<b>300 g cartof dulce</b> la cuptor",
       "<b>350 g cartofi fierți</b>",
       "<b>350 g hrișcă</b>",
       "<b>270 g quinoa</b>",
       "la burger: <b>1 chiflă</b> (≈85 g) + <b>200 g cartofi la cuptor</b>",
       "pizza: <b>1 bilă de aluat</b>, întreaga masă"),
     o("<b>100–200 g</b>: 100 g ardei copți, 200 g legume la cuptor sau 150 g ardei, ceapă, ciuperci în sote",
       "la burger: ≈100 g salată, ceapă roșie, cornișoni"),
     o("doar ce e în gătit", "<b>1 linguriță ulei</b> la sote", "<small>nimic în plus pe cutie</small>"),
     o("<b>1 portocală mare</b> · <b>1 măr</b>", "<b>1 pară</b> · <b>2 mandarine</b>")),

    ("Cină", "≈400 kcal · ≈45 g proteină", "Fără carbohidrați",
     o("<b>150 g somon</b>",
       "<b>180 g biban sau doradă</b>",
       "<b>160 g frigărui sau piept de pui</b>",
       "<b>160 g sote de vită</b>"),
     '<span class="no">Deloc</span>',
     o("<b>150–250 g</b>: 150–200 g broccoli, 200 g legume la cuptor sau 250 g sote de legume",
       "+ <b>bol mare de salată verde</b>: salată, rucola, castravete, pătrunjel"),
     o("la somon: <b>½ linguriță ulei</b>",
       "la biban, doradă: <b>1 linguriță ulei</b> sau <b>10 g nucă</b>",
       "la pui, vită: doar lămâie"),
     '<span class="no">–</span>'),
]

TR = "".join(
    f'<tr><td class="m"><b>{m}</b><span>{k}</span>' + (f"<em>{note}</em>" if note else "") + "</td>"
    + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
    for m, k, note, *cells in ROWS
)

CRUD = [
    ("Piept de pui, frigărui", "160 g", "≈225 g"),
    ("Piept de pui", "150 g", "≈210 g"),
    ("Piept de pui", "130 g", "≈185 g"),
    ("Piept de pui", "120 g", "≈170 g"),
    ("Pulpe de pui fără os", "160 g", "≈215 g"),
    ("Chiftele (carne tocată)", "180 g", "≈240 g"),
    ("Chiftea de burger", "150 g", "200 g"),
    ("Vită pentru sote", "160 g", "≈245 g"),
    ("Biban, doradă (file)", "180 g", "≈220 g"),
    ("Somon", "150 g", "≈180 g"),
]
CR = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in CRUD[:5])
CR2 = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in CRUD[5:])

HTML = f"""<!doctype html><html lang="ro"><head><meta charset="utf-8"><title>Farfuria lui Cem</title><style>{CSS}{EXTRA}</style></head><body>
<div class="top">
 <div><h1>Farfuria lui Cem</h1>
 <p class="sub">La fiecare masă alegi <b>câte o variantă din fiecare coloană</b>. Variantele din aceeași căsuță au cam aceleași calorii, așa că oricum le combini, ziua iese la fel. <b>Toate gramele sunt gătite</b>: cântărești după gătit, fără os, piele sau zeamă.</p></div>
 <div class="tot"><div><span>Zi de sală</span><b>≈2.400 kcal</b><span>≈180 g proteină</span></div><div><span>Zi de odihnă</span><b>≈2.050 kcal</b><span>≈170 g proteină</span></div></div>
</div>
<table class="f">
 <thead><tr><th style="width:12%">Masa</th><th style="width:20%">Proteină (gătită) · alegi una</th><th style="width:21%">Carbohidrați (gătiți) · alegi unul</th><th style="width:19%">Legume</th><th style="width:15%">Grăsime</th><th style="width:13%">Fruct</th></tr></thead>
 <tbody>{TR}</tbody>
</table>
<div class="p2"><h2>Cât pui crud și ziua de odihnă</h2>
<div class="low">
 <div class="box"><b class="t">Cât pui crud ca să iasă porția gătită</b>
  <table class="c"><thead><tr><th>Proteina</th><th>Porția gătită</th><th>Cât pui crud</th></tr></thead><tbody>{CR}{CR2}</tbody></table>
  <p style="margin:6px 0 0;color:var(--muted);font-size:8.6pt">Cantitățile crude sunt aproximative: carnea pierde apă diferit de la o bucată la alta. Cel mai sigur e să cântărești după gătit.</p></div>
 <div>
 <div class="box mint"><b class="t">Zi de odihnă (sâmbătă, duminică)</b>
  <ul><li>Înainte de sală: <b>doar cafea</b>, fără fruct.</li>
  <li>După-amiază: <b>carbohidrații la jumătate</b>: 125 g bulgur, 150 g cartof dulce, 175 g cartofi fierți, 100 g cartofi la cuptor. <b>Fără fruct.</b></li>
  <li>Restul meselor, la fel.</li></ul></div>
 <div class="box"><b class="t">Ca să iasă bine</b>
  <ul><li>Proteină la <b>fiecare</b> masă; carbohidrații mari doar <b>după sală</b>; seara <b>fără</b> carbohidrați.</li>
  <li>Gătești toată cantitatea crudă, o lași 5 min, apoi împarți porțiile gătite pe cântar, direct în cutii.</li>
  <li>Uleiul se măsoară cu lingurița (1 linguriță ≈ 45 kcal), nu din sticlă.</li>
  <li>±10 g nu contează. Legumele și salata pot fi oricât.</li></ul></div>
 </div>
</div>
<p class="foot">Gramajele sunt din ghidul lui Cem (noiembrie 2026). Caloriile și proteinele sunt estimări calculate din ele; ghidul lui nu dă un total. Pentru o schimbare mare de meniu, întreabă-l pe Cem.</p>
</div>
</body></html>"""


def main():
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "farfuria.html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(HTML)
        js = os.path.join(d, "pdf.js")
        with open(js, "w") as f:
            f.write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2],{waitUntil:'load'});await p.pdf({path:process.argv[3],printBackground:true,preferCSSPageSize:true});await b.close();})();""")
        subprocess.run(["node", js, src, OUT], check=True)
    print(OUT)


if __name__ == "__main__":
    sys.exit(main())
