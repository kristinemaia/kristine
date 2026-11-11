#!/usr/bin/env python3
"""
„Bucătăria mea, pe scurt”: săptămâna de mâncare a Kristinei în același format ca „Bucătăria lui Cem, pe scurt”:
zi cu zi ce mănâncă și ce face, ce adaugă pentru ea când gătește pentru Cem, peștele de scos din congelator,
rețetele pe scurt. Meniul e cel din build_saptamana_kristine.py / PROGRAM-ALIMENTATIE.md (porții gătite).

Rulezi:   python3 library/build_bucataria_mea.py
Rezultat: BUCATARIA-MEA-SIMPLU.pdf (A4)
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
from build_bucataria_cem import CSS, day as _day  # același stil și același tabel pe zile


def day(*a, **k):
    return _day(*a, who="Ce mănânc", **k)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "BUCATARIA-MEA-SIMPLU.pdf")

OVAZ = "<b>Ovăz proteic:</b> 40 g fulgi de ovăz fierți în apă · 1 măsură de whey (30 g) amestecată la final · 150 ml lapte · 100 g fructe de pădure"
OVAZ_TU = "Ovăzul cu apă, 2 min la microunde; amesteci whey-ul și laptele, deasupra fructele (pot fi congelate)."
SHAKE = ("Gustare", "<b>Shake:</b> 250 ml chefir + 1 măsură de whey", "Îl bei după sală.")
LOR = ("Gustare", "<b>Lor cu fructe:</b> 200 g lor + 100 g fructe de pădure", "")

LUNI = day("Luni", ("Picioare A · ≈1.660 kcal", ""), [
 ("09:30", "Mic dejun", OVAZ, "După omleta lui Cem. " + OVAZ_TU),
 ("13:00", "Prânz", "<b>Paste cu ton:</b> 140 g paste fierte · 1 conservă de ton în apă · roșii, castraveți, ceapă roșie · 1 linguriță ulei de măsline · lămâie",
  "Pastele fierte duminică (cutia ta), le amesteci cu tonul și legumele tăiate acum."),
 ("după sală", *SHAKE),
 ("20:30", "Cină, cu Cem", "<b>Somon:</b> 95 g somon gătit (120 g crud) · 150 g cartofi fierți · 200 g broccoli",
  "Somonul tău în air fryer lângă al lui Cem, 180 °C, 8–10 min. Cartofii: 6–8 min la microunde în bol cu capac (sau fierți 20 min). Broccoli din sesiunea de duminică."),
 ("desert", "", "<b>Banană la air fryer + skyr:</b> 1 banană, scorțișoară · 150 g skyr", "Banana tăiată pe lungime, 8 min la 180 °C."),
])
MARTI = day("Marți", ("Upper A + intervale · ≈1.610 kcal", ""), [
 ("09:30", "Mic dejun", "<b>Omleta ta:</b> 2 ouă + 100 ml albuș · 150 g legume (ardei, ceapă, spanac, ciuperci, roșii) · ½ linguriță ulei · 1 lipie mică (≈60 g)",
  "Tai legumele, 3 min în tigaie, apoi ouăle. Lipia 20–30 sec în tigaia uscată."),
 ("13:00", "Prânz", "<b>Wrap cu ton:</b> 1 lipie · 1 conservă de ton · 2 linguri iaurt grecesc cu usturoi · salată verde, castravete · 1 măr", "2 minute, fără gătit."),
 ("după sală", *SHAKE),
 ("20:30", "Cină", "<b>Shakshuka:</b> 2 ouă + 150 ml albuș în 200 g passata cu ardei și ceapă · 1 felie pâine integrală",
  "Sosul cu ardei și ceapă 8 min, spargi ouăle, încă 5–6 min cu capac. Cem are sote-ul lui."),
 ("desert", "", "2 pătrățele de ciocolată 85% (10 g)", ""),
], "22:00 Scoți din congelator în frigider bibanul lui Cem și pe al tău (130 g), pentru miercuri.")
MIERCURI = day("Miercuri", ("cardio ușor · ≈1.580 kcal", ""), [
 ("09:30", "Mic dejun", "<b>Bol cu iaurt și rodie:</b> 200 g iaurt grecesc 2% · 30 g ovăz · 100 g boabe de rodie (½ rodie) · 10 g nuci", "Fără gătit."),
 ("13:00", "Prânz", "<b>Paste cu creveți:</b> 140 g paste fierte · 120 g creveți gătiți (150 g cruzi) · roșii cherry, usturoi · 1 linguriță ulei · 10 g parmezan",
  "Fierbi 120 g paste crude: jumătate acum, jumătate în cutie pentru vineri. Creveții 3–4 min în tigaie cu usturoi (direct congelați: 1–2 min în plus)."),
 ("după cardio", *LOR),
 ("20:30", "Cină, cu Cem", "<b>Biban cu cartofi:</b> ≈100 g biban gătit (130 g crud), fără ulei în plus · 150 g cartofi la cuptor · 200 g legume la cuptor",
  "Cartofii și legumele le faci în sesiunea lui Cem (vezi pagina 1). Bibanul lângă al lui, în air fryer, 180 °C, 8–10 min."),
 ("desert", "", "<b>2 bile cu curmale</b>", ""),
], "22:00 Scoți dorada ta (130 g) pentru joi seara.")
JOI = day("Joi", ("Picioare B · ≈1.650 kcal", ""), [
 ("09:30", "Mic dejun", OVAZ, OVAZ_TU),
 ("13:00", "Prânz", "<b>Salată cu ton și cartofi:</b> 200 g cartofi fierți · 1 conservă de ton · 1 ou fiert · fasole verde, roșii · 1 linguriță ulei",
  "Cartofii fierți miercuri, oul din cutia de duminică, fasolea verde 3 min la microunde."),
 ("după sală", *SHAKE),
 ("20:30", "Cină", "<b>Cartofi cu pește:</b> 200 g cartofi fierți cu mărar sau pătrunjel · ≈100 g doradă gătită · 150 g salată sau legume · lămâie",
  "Dorada în air fryer, 180 °C, 8–10 min. Cartofii fierți miercuri, încălziți 1–2 min. Cem are frigăruile lui."),
 ("desert", "", "<b>Iaurt cu rodie:</b> 150 g iaurt grecesc · 100 g boabe de rodie · ½ linguriță miere", ""),
], "22:00 Scoți dorada lui Cem și pe a ta (130 g), pentru vineri.")
VINERI = day("Vineri", ("Upper B · ≈1.650 kcal", ""), [
 ("09:30", "Mic dejun", OVAZ, OVAZ_TU),
 ("13:00", "Prânz", "<b>Paste cu ton în sos de roșii:</b> 140 g paste fierte · 150 g passata cu usturoi, oregano, busuioc · 1 linguriță ulei · 1 conservă de ton",
  "Pastele din cutia de miercuri. Sosul 5 min în tigaie, apoi tonul și pastele."),
 ("după sală", *SHAKE),
 ("20:30", "Cină, cu Cem", "<b>Doradă cu cartofi:</b> ≈100 g doradă gătită, fără ulei în plus · 150 g cartofi la cuptor · 200 g legume la cuptor",
  "Dorada lângă a lui, în air fryer. Cartofii și legumele din sesiunea de miercuri, încălzite în air fryer 180 °C, 4 min."),
 ("desert", "", "<b>Măr copt cu lor:</b> 1 măr cu scorțișoară · 100 g lor cu vanilie și stevia · 5 g nuci", "Mărul tăiat în jumătăți, 12–15 min la 180 °C în air fryer."),
], "Seara scoți somonul tău (120 g) pentru sâmbătă la prânz.")
SAMBATA = day("Sâmbătă", ("cardio lung · ≈1.000 kcal + masa liberă", " m"), [
 ("09:30", "Mic dejun", "<b>Clătitele tale proteice</b> (2–3): 40 g ovăz măcinat · 1 ou · 100 ml albuș · 60 ml lapte · praf de copt, scorțișoară · deasupra 1 linguriță miere + 5 g fulgi de ciocolată neagră",
  "Mixezi tot, 2–3 clătite mici în tigaia antiaderentă."),
 ("13:00", "Prânz", "<b>Somon cu cartofi:</b> 95 g somon gătit · 150 g cartofi la cuptor · legume", "Cartofii cuburi în air fryer 200 °C, 18–20 min; somonul în ultimele 8–10 min, la 180 °C."),
 ("după cardio", *LOR),
 ("seara", "Masa liberă", "<b>O masă la alegere:</b> o porție normală + desert. Atât: o masă, nu o zi.", "Mâncați în oraș sau comandați; Cem comandă după regulile lui."),
], "22:00 Scoți peștele de duminică pentru amândoi (al tău: 130 g).")
DUMINICA = day("Duminică", ("pauză · ≈1.640 kcal", " k"), [
 ("09:30", "Mic dejun", "<b>Omleta ta:</b> 2 ouă + 100 ml albuș · 150 g legume · ½ linguriță ulei · 2 felii pâine integrală (≈80 g)", "Ca marți, cu pâine în loc de lipie."),
 ("12:30", "Prânz", "<b>Paste cu creveți:</b> 140 g paste fierte · 120 g creveți gătiți · roșii cherry, usturoi · 1 linguriță ulei · 10 g parmezan",
  "Fierbi 120 g paste crude: jumătate acum, jumătate în cutie pentru luni (pastele cu ton)."),
 ("după-amiaza", *SHAKE),
 ("20:00", "Cină, cu Cem", "<b>Pește cu cartofi:</b> ≈100 g biban sau doradă gătit · 150 g cartofi la cuptor · 200 g legume",
  "Cartofii cuburi în air fryer 200 °C, 18–20 min; peștele vostru împreună, 180 °C, 8–10 min."),
 ("desert", "", "<b>2 bile cu curmale</b>", ""),
], "După sesiune: scoți somonul lui Cem și pe al tău (120 g), pentru luni seara.")

HTML = f"""<!doctype html><html lang="ro"><head><meta charset="utf-8"><title>Bucătăria mea, pe scurt</title><style>{CSS}</style></head><body>

<h1>Bucătăria mea, pe scurt</h1>
<p class="sub">Săptămâna mea de mâncare, ca ghidul lui Cem: ce mănânc, ce fac și când. Toate gramele sunt pentru mâncarea gătită.</p>

<div class="grid2">
 <div class="box mint"><b class="t">Ținta mea</b>
  <ul><li><b>≈1.550–1.650 kcal</b> pe zi, <b>120–130 g proteină</b>.</li>
  <li>4 mese + un desert mic în fiecare seară (e deja socotit).</li>
  <li>Sâmbătă seara: masa liberă (o masă, nu o zi).</li>
  <li>Totul se notează în jurnalul de mâncare.</li></ul></div>
 <div class="box"><b class="t">Regulile mele de bucătărie</b>
  <ul><li>Lactatele, roșiile, passata și whey-ul stau pe <b>raftul meu</b> din frigider (bandă roz).</li>
  <li>Mâncarea lui Cem o gătesc prima; roșiile le tai la final, pe placa mea.</li>
  <li>Pastele le fierb pentru 2 zile: 120 g crude → jumătate azi, jumătate în cutie (cel mult 2 zile).</li>
  <li>Peștele crud: 130 g biban sau doradă, 120 g somon. Gătit iese ≈100 g și ≈95 g.</li></ul></div>
</div>

<h2>Săptămâna, dintr-o privire</h2>
<table>
 <thead><tr><th style="width:13%">Zi</th><th style="width:20%">Sala</th><th>Ce mănânc (mic dejun · prânz · gustare · cină · desert)</th></tr></thead>
 <tbody>
 <tr><td><b>Luni</b></td><td>Picioare A</td><td>ovăz proteic · paste cu ton · shake · <b>somon cu Cem</b> · banană cu skyr</td></tr>
 <tr><td><b>Marți</b></td><td>Upper A + intervale</td><td>omleta cu lipie · wrap cu ton · shake · shakshuka · ciocolată 85% · <b>22:00 scot bibanul</b></td></tr>
 <tr><td><b>Miercuri</b></td><td>cardio ușor</td><td>bol cu iaurt și rodie · paste cu creveți · lor · <b>biban cu Cem</b> · bile cu curmale · <b>22:00 scot dorada mea</b></td></tr>
 <tr><td><b>Joi</b></td><td>Picioare B</td><td>ovăz proteic · salată cu ton și cartofi · shake · cartofi cu doradă · iaurt cu rodie · <b>22:00 scot dorada</b></td></tr>
 <tr><td><b>Vineri</b></td><td>Upper B</td><td>ovăz proteic · paste în sos de roșii · shake · <b>doradă cu Cem</b> · măr copt · <b>seara scot somonul</b></td></tr>
 <tr><td><b>Sâmbătă</b></td><td>cardio lung</td><td>clătite proteice · somon cu cartofi · lor · <b>masa liberă</b> · <b>22:00 scot peștele</b></td></tr>
 <tr><td><b>Duminică</b></td><td>pauză</td><td>omleta cu pâine · paste cu creveți · shake · <b>pește cu Cem</b> · bile cu curmale · <b>scot somonul</b></td></tr>
 </tbody></table>

<h2>Când gătesc pentru Cem, pun și pentru mine</h2>
<p class="sub" style="margin-top:0">Câteva minute în plus, în aceeași oală sau tavă. Restul îl fac pe loc, în 10–20 de minute.</p>
<div class="grid2">
 <div class="dev cup"><b class="t">Duminică (sesiunea lui)</b>
  <ul><li><b>Ouă:</b> la cele 14 ale lui mai pui 2 (oul din salata de joi + unul de rezervă).</li>
  <li><b>Broccoli:</b> la cei 550 g ai lui mai pui 250 g (cina mea de luni: 200 g).</li>
  <li><b>Pastele</b> pentru duminică și luni le fierb la prânz, înainte de sesiune.</li></ul></div>
 <div class="dev ar"><b class="t">Miercuri (sesiunea lui)</b>
  <ul><li><b>Cartofi fierți:</b> la cei 400 g ai lui mai pui 400 g (joi: salata 200 g + cina 200 g).</li>
  <li><b>Cartofi felii la air fryer:</b> la cei 450 g ai lui mai pui 450 g, în încă o tranșă (miercuri seara 150 g + vineri seara 150 g).</li>
  <li><b>Legume la cuptor:</b> la cele ≈350 g ale lui mai pui ≈600 g crude, pe a doua tavă (ies ≈400 g: miercuri seara 200 g + vineri seara 200 g).</li>
  <li><b>Pastele</b> pentru miercuri și vineri le fierb la prânz.</li></ul></div>
</div>
<div class="box"><b class="t">Peștele meu, din congelator în frigider (cu o seară înainte)</b>
 Duminică după sesiune: somonul pentru luni · marți 22:00: bibanul pentru miercuri · miercuri 22:00: dorada pentru joi · joi 22:00: dorada pentru vineri · vineri seara: somonul pentru sâmbătă · sâmbătă 22:00: peștele pentru duminică. Creveții merg direct congelați în tigaie.</div>

<div class="page"><h2>Ce mănânc, zi cu zi</h2>{LUNI}{MARTI}</div>
<div class="page">{MIERCURI}{JOI}</div>
<div class="page">{VINERI}{SAMBATA}</div>
<div class="page">{DUMINICA}

<h2 style="margin-top:12px">Rețetele mele, pe scurt</h2>
<div class="cols2">
 <div class="rec"><b>Ovăz proteic</b> · ≈385 kcal · 31 g proteină<br><span>40 g ovăz + apă, 2 min la microunde · 1 măsură whey · 150 ml lapte · 100 g fructe de pădure.</span></div>
 <div class="rec"><b>Omleta mea</b> · ≈445–455 kcal · 31–34 g<br><span>2 ouă + 100 ml albuș · 150 g legume · ½ linguriță ulei · 1 lipie (≈60 g) sau 2 felii pâine (≈80 g).</span></div>
 <div class="rec"><b>Bol cu iaurt și rodie</b> · ≈410 kcal · 27 g<br><span>200 g iaurt grecesc 2% · 30 g ovăz · 100 g rodie · 10 g nuci.</span></div>
 <div class="rec"><b>Clătitele mele proteice</b> · ≈350 kcal · 25 g<br><span>40 g ovăz măcinat · 1 ou · 100 ml albuș · 60 ml lapte · praf de copt · deasupra 1 linguriță miere + 5 g fulgi de ciocolată. Cu ½ măsură whey: ≈410 kcal · 37 g.</span></div>
 <div class="rec"><b>Paste cu ton</b> · ≈430 kcal · 39 g<br><span>140 g paste fierte (60 g crude) · 1 conservă ton · roșii, castraveți, ceapă roșie · 1 linguriță ulei · lămâie.</span></div>
 <div class="rec"><b>Paste cu ton în sos de roșii</b> · ≈430 kcal · 39 g<br><span>140 g paste fierte · 150 g passata cu usturoi, oregano, busuioc · 1 linguriță ulei · 1 conservă ton.</span></div>
 <div class="rec"><b>Paste cu creveți</b> · ≈445 kcal · 41 g<br><span>140 g paste fierte · 120 g creveți gătiți · roșii cherry, usturoi · 1 linguriță ulei · 10 g parmezan.</span></div>
 <div class="rec"><b>Wrap cu ton</b> · ≈455 kcal · 39 g<br><span>1 lipie · 1 conservă ton · 2 linguri iaurt cu usturoi · salată, castravete · 1 măr.</span></div>
 <div class="rec"><b>Salată cu ton și cartofi</b> · ≈450 kcal · 42 g<br><span>200 g cartofi fierți · 1 conservă ton · 1 ou fiert · fasole verde, roșii · 1 linguriță ulei.</span></div>
 <div class="rec"><b>Pește cu cartofi</b> · ≈360–385 kcal · 30 g<br><span>≈100 g biban sau doradă gătit (fără ulei în plus) · 150 g cartofi la cuptor sau 200 g fierți · legume sau salată, lămâie.</span></div>
 <div class="rec"><b>Somon cu cartofi</b> · ≈410–445 kcal · 31 g<br><span>95 g somon gătit · 150 g cartofi · 200 g broccoli sau legume.</span></div>
 <div class="rec"><b>Shakshuka</b> · ≈410 kcal · 38 g<br><span>2 ouă + 150 ml albuș în 200 g passata cu ardei și ceapă · 1 felie pâine integrală.</span></div>
 <div class="rec"><b>Shake</b> · ≈240 kcal · 32 g<br><span>250 ml chefir + 1 măsură whey.</span></div>
 <div class="rec"><b>Lor cu fructe</b> · ≈215 kcal · 27 g<br><span>200 g lor + 100 g fructe de pădure.</span></div>
 <div class="rec"><b>Deserturile</b><br><span>Banană la air fryer + 150 g skyr (≈200 kcal) · iaurt cu rodie: 150 g iaurt + 100 g rodie + ½ linguriță miere (≈200) · măr copt + 100 g lor + 5 g nuci (≈215) · 2 bile cu curmale: 1 curmală Medjool + 10 g ovăz + ¼ măsură whey + ½ linguriță cacao (≈140) · 2 pătrățele de ciocolată 85% (≈60).</span></div>
 <div class="rec"><b>Timpi la air fryer</b><br><span>Biban, doradă: 180 °C, 8–10 min · somon: 180 °C, 8–10 min · cartofi cuburi: 200 °C, 18–20 min · banană: 180 °C, 8 min · măr: 180 °C, 12–15 min.</span></div>
</div>
<p style="color:var(--muted);font-size:8.4pt;margin-top:8px">Același meniu ca în „Kristine's food week” și în programul de definire (Alimentația). Cumpărăturile sunt în lista comună cu Cem.</p>
</div>
</body></html>"""


def main():
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "mea.html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(HTML)
        js = os.path.join(d, "pdf.js")
        with open(js, "w") as f:
            f.write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2],{waitUntil:'load'});await p.pdf({path:process.argv[3],printBackground:true,preferCSSPageSize:true,
displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:7pt;color:#5C5466;width:100%;text-align:center;font-family:Inter">Bucătăria mea, pe scurt · pagina <span class=pageNumber></span> din <span class=totalPages></span></div>'});await b.close();})();""")
        subprocess.run(["node", js, src, OUT], check=True)
    print(OUT)


if __name__ == "__main__":
    sys.exit(main())
