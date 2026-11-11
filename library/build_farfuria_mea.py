#!/usr/bin/env python3
"""
„Farfuria mea”: fișa de bucătărie a Kristinei (A4 orizontal), la fel ca „Farfuria lui Cem”:
ce pui la fiecare masă, pe componente (proteină, carbohidrați, legume, grăsime, fruct), în grame gătite.

Gramajele vin din PROGRAM-ALIMENTATIE.md (ținta: ~1.550–1.650 kcal, ~120–130 g proteină, 40–55 g grăsimi,
150–175 g carbohidrați). Variantele din aceeași căsuță au cam aceleași calorii. Fără carne; broccoli scos
(nu-i place), chefirul în fiecare zi, fără ovăz amestecat cu proteină.

Rulezi:   python3 library/build_farfuria_mea.py
Rezultat: FARFURIA-MEA.pdf
"""
import os
import subprocess
import sys
import tempfile

from build_bucataria_cem import CSS
from build_farfuria_cem import EXTRA, o

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "FARFURIA-MEA.pdf")

MORE = """
td.ds { font-size:8.3pt; }
td.ds b { white-space:nowrap; }
"""

ROWS = [
    ("Mic dejun", "≈400 kcal · ≈28 g proteină", "",
     o("<b>2 ouă + 100 ml albuș</b>: omletă",
       "<b>2 ouă fierte + 100 g lor</b> (cu mărar, piper)",
       "<b>200 g iaurt grecesc 2%</b>: bol",
       "clătite: <b>1 ou + 100 ml albuș + 60 ml lapte</b>"),
     o("<b>1 lipie mică</b> (≈60 g)",
       "<b>2 felii pâine integrală</b> (≈80 g)",
       "<small>cu lor: <b>1 felie</b> (≈40 g)</small>",
       "<b>30 g ovăz</b> la bol · <b>40 g ovăz măcinat</b> la clătite"),
     o("omletă: <b>150 g</b> ardei, ceapă, spanac, ciuperci, roșii",
       "lângă ouă: roșie, castravete",
       "<small>la bol și clătite: fără</small>"),
     o("omletă: <b>½ linguriță ulei</b>",
       "bol: <b>10 g nuci</b>",
       "<small>la ouăle fierte: nimic</small>"),
     o("bol: <b>1 banană mică</b> sau <b>100 g rodie</b>",
       "clătite: <b>1 linguriță miere + 5 g fulgi de ciocolată</b>",
       "<small>la ouă: fără</small>")),

    ("Prânz", "≈440 kcal · ≈40 g proteină", "",
     o("<b>1 conservă ton în apă</b> (≈120 g scurs)",
       "<b>120 g creveți gătiți</b>",
       "<b>≈100 g pește alb gătit</b>",
       "<small>la salata cu cartofi: ton <b>+ 1 ou fiert</b></small>"),
     o("<b>140 g paste fierte</b> (60 g crude)",
       "<b>1 lipie mică</b> (≈60 g): wrap",
       "<b>200 g cartofi fierți</b>",
       "<b>150 g bulgur</b>"),
     o("<b>150 g</b>: roșii, castraveți, ceapă roșie, salată, fasole verde, roșii cherry",
       "în sos: <b>150 g passata</b>"),
     o("<b>1 linguriță ulei</b>",
       "paste cu creveți: ulei <b>+ 10 g parmezan</b>",
       "wrap: <b>2 linguri iaurt grecesc</b> cu usturoi, fără ulei",
       "sau <b>6 măsline</b>, în loc de ulei"),
     o("wrap: <b>1 măr</b>", "<small>în rest: fără</small>")),

    ("Chefirul zilei", "≈240 kcal · ≈32 g proteină", "În fiecare zi · după sală",
     o("<b>1 măsură whey</b> (30 g) + <b>250 ml chefir</b>"),
     o("<small>doar ce e în chefir</small>"),
     '<span class="no">–</span>',
     o("<small>doar ce e în chefir</small>"),
     o("<small>opțional:</small> <b>100 g fructe de pădure</b>")),

    ("Cină", "≈380 kcal · ≈30 g proteină", "Cu carbohidrați",
     o("<b>≈100 g biban sau doradă</b> gătit",
       "<b>≈95 g somon</b> gătit",
       "<b>≈115 g pește alb</b> gătit (cod, merluciu)",
       "quesadilla: <b>1 conservă ton + 30 g mozzarella light</b>"),
     o("<b>150 g cartofi la cuptor</b> (200 g cruzi)",
       "<b>200 g cartofi fierți</b>",
       "<b>100 g paste fierte</b>",
       "quesadilla: <b>1 lipie mică</b>"),
     o("<b>150–200 g</b>: legume la cuptor (dovlecel, ardei, ceapă), fasole verde",
       "+ salată verde cu lămâie, cât vrei"),
     o("pește alb: <b>1 linguriță ulei</b>",
       "biban, doradă, somon: <b>fără ulei în plus</b>"),
     o("<small>opțional: 2–3 linguri rodie pe salată</small>")),
]

TR = "".join(
    f'<tr><td class="m"><b>{m}</b><span>{k}</span>' + (f"<em>{note}</em>" if note else "") + "</td>"
    + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
    for m, k, note, *cells in ROWS
)

DESERT = """<tr><td class="m"><b>Desertul zilei</b><span>≈150–250 kcal</span><em>După cină, în fiecare zi</em></td>
<td class="ds" colspan="5">Alegi unul (sunt și în jurnal, la „Din plan → Deserturi”):
<b>banană la air fryer + 150 g skyr</b> (≈200) · <b>150 g iaurt grecesc + 100 g rodie + ½ linguriță miere</b> (≈200) ·
<b>măr copt + 100 g brânză de vaci + 5 g nuci</b> (≈215) · <b>înghețată de banană</b> (≈230) ·
<b>mousse de ciocolată</b> (≈250) · <b>mug cake proteic</b> (≈275) · <b>2 bile cu curmale</b> (≈140) ·
<b>2 pătrățele de ciocolată 85%</b> (≈60).<br>
<small>În ziua cu mousse sau mug cake, la micul dejun ia farfuria cu ouă și lor (cea mai ușoară). Fără desert: 15 g nuci + 1 fruct.</small></td></tr>"""

CRUD = [
    ("Paste", "60 g uscate", "≈140 g fierte"),
    ("Cartofi", "200 g cruzi", "200 g fierți · ≈150 g la cuptor"),
    ("Bulgur", "50 g uscat", "≈150 g fiert"),
    ("Biban, doradă", "130 g crud", "≈100 g"),
    ("Somon", "120 g crud", "≈95 g"),
    ("Pește alb (cod, merluciu)", "150 g crud", "≈115 g"),
    ("Creveți", "150 g cruzi", "≈120 g"),
    ("Ovăz", "se cântărește uscat", "30–40 g ≈ 3–4 linguri"),
]
CR = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in CRUD)

HTML = f"""<!doctype html><html lang="ro"><head><meta charset="utf-8"><title>Farfuria mea</title><style>{CSS}{EXTRA}{MORE}</style></head><body>
<div class="top">
 <div><h1>Farfuria mea</h1>
 <p class="sub">La fiecare masă alegi <b>câte o variantă din fiecare coloană</b>. Variantele din aceeași căsuță au cam aceleași calorii, deci ziua iese la fel. <b>Toate gramele sunt gătite</b>: cântărești ce iei din oală sau din tavă.</p></div>
 <div class="tot"><div><span>În fiecare zi</span><b>≈1.600–1.650 kcal</b><span>≈130 g proteină</span></div><div><span>Grăsimi · carbohidrați</span><b>40–55 g · 150–175 g</b><span>pe zi</span></div></div>
</div>
<table class="f">
 <thead><tr><th style="width:12%">Masa</th><th style="width:20%">Proteină (gătită) · alegi una</th><th style="width:20%">Carbohidrați (gătiți) · alegi unul</th><th style="width:19%">Legume</th><th style="width:16%">Grăsime</th><th style="width:13%">Fruct și extra</th></tr></thead>
 <tbody>{TR}{DESERT}</tbody>
</table>
<div class="p2"><h2>Cât pui crud și cum ține ziua</h2>
<div class="low">
 <div class="box"><b class="t">Cât pui crud ca să iasă porția gătită</b>
  <table class="c"><thead><tr><th>Aliment</th><th>Crud / uscat</th><th>Gătit (în farfurie)</th></tr></thead><tbody>{CR}</tbody></table>
  <p style="margin:6px 0 0;color:var(--muted);font-size:8.6pt">Pastele pentru 2 zile: le cântărești uscate (120 g), apoi cântărești tot ce a ieșit fiert și împarți la 2.</p></div>
 <div>
 <div class="box mint"><b class="t">Ziua ta (zi de sală sau zi fără sală, la fel)</b>
  <table class="c" style="margin-bottom:6px"><thead><tr><th>Masa</th><th>kcal</th><th>Proteină</th></tr></thead><tbody>
   <tr><td>Mic dejun</td><td>≈400</td><td>≈28 g</td></tr>
   <tr><td>Prânz</td><td>≈440</td><td>≈40 g</td></tr>
   <tr><td>Chefirul zilei</td><td>≈240</td><td>≈32 g</td></tr>
   <tr><td>Cină</td><td>≈380</td><td>≈30 g</td></tr>
   <tr><td>Desert</td><td>≈150–250</td><td>variază</td></tr>
   <tr><td><b>Totalul zilei</b></td><td><b>≈1.600–1.650</b></td><td><b>≈130 g</b></td></tr>
  </tbody></table>
  <ul><li>Ai o singură variantă, pentru că deficitul tău e mic și același în fiecare zi. În zilele de sală doar bei chefirul după antrenament.</li>
  <li><b>Masa liberă:</b> o dată pe săptămână, o masă (nu o zi), în locul cinei.</li></ul></div>
 <div class="box"><b class="t">Ce înlocuiește ce (≈180 kcal fiecare)</b>
  <ul><li><b>1 lipie mică</b> ≈ <b>2 felii pâine integrală</b> ≈ <b>115 g paste fierte</b> ≈ <b>230 g cartofi fierți</b>. Intră una în locul alteia, nu pe lângă.</li>
  <li>Proteină la fiecare masă (minim 25–30 g); legume la cel puțin 2 mese.</li>
  <li>Uleiul cu lingurița (1 linguriță ≈ 40 kcal), nu din sticlă.</li></ul></div>
 </div>
</div>
<p class="foot">Gramajele și caloriile sunt din programul tău de alimentație (11 nov 2026), estimate. Le ajustăm după primele 2 săptămâni, după media cântarului.</p>
</div>
</body></html>"""


def main():
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "farfuria-mea.html")
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
