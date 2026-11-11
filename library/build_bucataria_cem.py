#!/usr/bin/env python3
"""
„Bucătăria lui Cem, pe scurt”: ghidul lui Cem (Kristine-ghid-bucatarie1.pdf, 10 nov 2026) rescris simplu,
cu aceleași gramaje: ce mănâncă Cem în fiecare zi, ce faci tu și la ce oră, cele două zile de gătit
(duminică și miercuri) pe pași, cutiile și rețetele pe scurt.

Singura schimbare față de ghid: legumele pentru micul dejun se taie dimineața, pe loc (nu mai sunt pungi
pregătite în sesiune); gramajele rămân aceleași.

Rulezi:   python3 library/build_bucataria_cem.py
Rezultat: BUCATARIA-LUI-CEM-SIMPLU.pdf (A4)
"""
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "BUCATARIA-LUI-CEM-SIMPLU.pdf")

CSS = """
@page { size: A4; margin: 12mm 12mm 13mm; }
:root { --ink:#2B2431; --muted:#5C5466; --line:#E6DCE3; --soft:#FAF5F7;
  --k:#F8DCE6; --k-ink:#8A3459; --c:#DDE9F7; --c-ink:#2A5580; --l:#E9E1F7; --l-ink:#4C3A78; --m:#D8F0E4; --m-ink:#1C6550; --w:#FCEBD9; --w-ink:#8A4B12; }
* { box-sizing:border-box; }
body { margin:0; font-family:"Inter",sans-serif; color:var(--ink); font-size:9.4pt; line-height:1.38; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
h1 { font-family:"Inter Display","Inter",sans-serif; font-weight:800; font-size:25pt; letter-spacing:-.02em; margin:0; line-height:1.05; }
h2 { font-family:"Inter Display","Inter",sans-serif; font-weight:800; font-size:15pt; margin:0 0 6px; letter-spacing:-.01em; break-after:avoid; }
h3 { font-family:"Inter Display","Inter",sans-serif; font-weight:800; font-size:12pt; margin:10px 0 4px; break-after:avoid; }
p { margin:0 0 6px; }
.sub { color:var(--muted); font-size:10pt; margin:4px 0 10px; }
.page { break-before:page; }
.box { background:var(--soft); border-radius:8px; padding:8px 10px; margin:0 0 8px; break-inside:avoid; }
.box.warn { background:var(--w); }
.box.mint { background:var(--m); }
.box b.t { display:block; font-size:8pt; letter-spacing:.07em; text-transform:uppercase; color:var(--k-ink); margin-bottom:3px; }
.box.warn b.t { color:var(--w-ink); } .box.mint b.t { color:var(--m-ink); }
ul, ol { margin:0; padding-left:16px; } li { margin:2px 0; }
table { width:100%; border-collapse:collapse; table-layout:fixed; margin:0 0 8px; }
th { text-align:left; font-size:7.6pt; letter-spacing:.07em; text-transform:uppercase; color:var(--muted); font-weight:700; padding:3px 6px; border-bottom:1.3px solid var(--ink); }
td { padding:5px 6px; border-bottom:1px solid var(--line); vertical-align:top; }
tr { break-inside:avoid; }
td.ora { width:15%; font-weight:700; } td.ora span { display:block; font-weight:500; color:var(--muted); font-size:8.2pt; }
td.tu { width:40%; background:var(--soft); }
.day { break-inside:avoid; margin-bottom:10px; }
.day h3 { display:flex; gap:8px; align-items:baseline; margin-top:4px; }
.day h3 small { font-family:"Inter",sans-serif; font-weight:600; font-size:8.5pt; color:var(--muted); }
.tag { display:inline-block; font-size:7.6pt; font-weight:700; border-radius:99px; padding:1px 7px; background:var(--c); color:var(--c-ink); }
.tag.k { background:var(--k); color:var(--k-ink); } .tag.m { background:var(--m); color:var(--m-ink); } .tag.l { background:var(--l); color:var(--l-ink); }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; }
.dev { border:1px solid var(--line); border-radius:8px; padding:7px 9px; break-inside:avoid; }
.dev b.t { display:block; font-size:8pt; letter-spacing:.07em; text-transform:uppercase; margin-bottom:3px; }
.dev.cup b.t { color:var(--k-ink); } .dev.af b.t { color:var(--l-ink); } .dev.ar b.t { color:var(--c-ink); } .dev.ff b.t { color:var(--m-ink); }
ol.steps { padding-left:0; list-style:none; counter-reset:s; }
ol.steps li { counter-increment:s; position:relative; padding:5px 0 5px 26px; border-bottom:1px solid var(--line); margin:0; break-inside:avoid; }
ol.steps li::before { content:counter(s); position:absolute; left:0; top:4px; width:18px; height:18px; border-radius:6px; background:var(--ink); color:#fff; font-size:8pt; font-weight:700; display:flex; align-items:center; justify-content:center; }
ol.steps li b.h { color:var(--k-ink); }
.rec { border-bottom:1px solid var(--line); padding:5px 0; break-inside:avoid; }
.rec b { font-size:9.6pt; } .rec span { color:var(--muted); font-size:8.4pt; }
.cols2 { columns:2; column-gap:18px; }
"""

def day(name, tag, rows, note="", who="Ce mănâncă Cem"):
    trs = "".join(f'<tr><td class="ora">{o}<span>{m}</span></td><td>{c}</td><td class="tu">{t}</td></tr>' for o, m, c, t in rows)
    n = f'<p style="margin:2px 0 0;color:var(--muted);font-size:8.6pt">{note}</p>' if note else ""
    return (f'<div class="day"><h3>{name} <span class="tag{tag[1]}">{tag[0]}</span></h3>'
            f'<table><thead><tr><th style="width:15%">Ora</th><th>{who}</th><th style="width:40%">Ce faci tu</th></tr></thead><tbody>{trs}</tbody></table>{n}</div>')

TERMOS = "termosul îl încălzești înainte 5 min cu apă clocotită"

LUNI = day("Luni", ("zi de sală", ""), [
 ("09:15", "Mic dejun", "<b>Omletă cu ardei:</b> 2 ouă + 4 albușuri · 150 g ardei kapia, ardei lung dulce și ceapă · 1 linguriță ulei de măsline · 2 felii pâine integrală (≈60 g) · 5 măsline negre · 100 g castravete și rucola · fulgi de ardei și cimbru, după plac",
  "09:00 Tai cei 150 g de ardei și ceapă, îi călești 3 min în 1 linguriță ulei, apoi pui ouăle și albușurile, 2 min (≈6 min). Pâinea din congelator, în prăjitor."),
 ("12:30", "Prânz", "<b>Wrap cu pui:</b> 1 lipie integrală (≈60 g) · 160 g piept de pui · 100 g salată verde, castravete, ceapă roșie, pătrunjel · 50 g ardei copți · 1 linguriță muștar · <b>1 măr</b> feliat",
  "09:55 Îi pui pe masă wrap-ul (cutia „Luni prânz”, în folie) și mărul feliat. Se mănâncă rece."),
 ("14:00", "Înainte de sală", "1 banană + cafea simplă", "Banana intră în geanta de sală."),
 ("16:45", "După sală", "<b>Chiftele cu bulgur:</b> 180 g chiftele · 250 g pilaf de bulgur · 100 g ardei copți · 1 portocală mare",
  f"14:45 Încălzești cutia 2 min la microunde și o pui în termos ({TERMOS}). În geantă: termosul, portocala, banana."),
 ("20:30", "Cină", "<b>Somon:</b> 150 g somon gătit · 150 g broccoli · bol mare de salată verde (salată, rucola, castravete, pătrunjel) cu sos de lămâie și ½ linguriță ulei",
  "20:15 Somonul (scos duminică seara în frigider) în air fryer, 180 °C, 8–10 min (63 °C în mijloc). Broccoli 1 min la microunde. Sosul pe salată."),
])
MARTI = day("Marți", ("zi de sală", ""), [
 ("09:15", "Mic dejun", "<b>Terci de ovăz cu albuș:</b> 60 g fulgi de ovăz + 300 ml apă · 4 albușuri · scorțișoară, fără zahăr · ½ banană · 20 g nucă · 1 ou fiert",
  "09:00 Ovăzul cu apa, 2 min la microunde; amesteci albușurile, încă 30 sec. Deasupra scorțișoară, banana, nuca. Oul fiert din cutia de ouă."),
 ("12:30", "Prânz", "<b>Salată de ton cu năut:</b> 1 conservă ton în apă (≈120 g scurs) · 150 g năut · 150 g castravete, ceapă roșie, pătrunjel, ardei copți · sos: 1 linguriță ulei + lămâie",
  "Borcanul „Marți prânz” din frigider, cu sosul separat. Se mănâncă rece."),
 ("14:00", "Înainte de sală", "2 curmale Medjool + cafea simplă", ""),
 ("16:45", "După sală", "<b>Pizza integrală cu pui</b> (feliată) · 20 g rucola deasupra · 2 mandarine",
  f"14:45 Încălzești pizza în tigaie cu capac (5–6 min) sau în air fryer (180 °C, 4–5 min), nu la microunde. În termos sau în folie; rucola și mandarinele separat, în geantă."),
 ("20:30", "Cină", "<b>Sote de vită:</b> 160 g vită cu 150 g ardei kapia, ceapă și ciuperci · bol mare de salată verde doar cu lămâie",
  "20:15 Încălzești sote-ul 2 min la microunde. Salata din cutie, cu lămâie."),
], "22:00 Scoți bibanul din congelator în frigider, pentru miercuri seara.")
MIERCURI = day("Miercuri", ("zi de sală · a doua zi de gătit", " k"), [
 ("09:15", "Mic dejun", "<b>Omletă cu spanac:</b> 2 ouă + 3 albușuri · 150 g spanac și ciuperci · ½ linguriță ulei · ½ avocado (≈70 g) · 2 felii pâine integrală (≈60 g)",
  "09:00 Tai ciupercile, le călești cu spanacul în ½ linguriță ulei (tigaie antiaderentă), apoi ouăle. Pâinea în prăjitor."),
 ("12:30", "Prânz", "<b>Pui cu pesto și hrișcă:</b> 150 g piept de pui · 240 g hrișcă · 1 lingură pesto · 150 g rucola, castravete, rodie",
  "Cutia „Miercuri prânz”. Se mănâncă rece."),
 ("14:00", "Înainte de sală", "1 banană + cafea simplă", "Banana în geantă."),
 ("16:45", "După sală", "<b>Pulpe cu cartof dulce:</b> 160 g pulpe de pui · 300 g cartof dulce · 200 g legume la cuptor · 1 măr",
  f"14:45 Încălzești cutia 2–3 min la microunde, în termos. Mărul în geantă."),
 ("17:00", "", "", "<b>A doua zi de gătit: 17:00–19:15</b> (vezi pagina „Miercuri”)."),
 ("20:30", "Cină", "<b>Biban:</b> 180 g biban de mare gătit · 200 g broccoli · bol mare de salată verde cu sos de lămâie și 1 linguriță ulei",
  "20:15 Bibanul în air fryer, 180 °C, 8–10 min. Broccoli 1 min la microunde. Sosul pe salată."),
])
JOI = day("Joi", ("zi de sală", ""), [
 ("09:15", "Mic dejun", "<b>Farfurie cu ouă fierte:</b> 3 ouă + 2 albușuri (din 5 ouă fierte, la 2 scoți gălbenușul) · 2 felii pâine integrală (≈60 g) · 100 g castravete · ardei lung · rucola · 1 portocală mare",
  "09:00 Ouăle din cutia de ouă fierte, curățate. Pâinea în prăjitor."),
 ("12:30", "Prânz", "<b>Bol de quinoa cu ton:</b> 1 conservă ton (≈120 g scurs) · 180 g quinoa · 150 g castravete, pătrunjel, ceapă verde, ardei copți · sos: 1 linguriță ulei + lămâie · 1 ou fiert",
  "Borcanul „Joi prânz”, cu sosul și oul separat."),
 ("14:00", "Înainte de sală", "2 mandarine + cafea simplă", ""),
 ("16:45", "După sală", "<b>Burger + cartofi:</b> 1 chiflă integrală (≈85 g) · 150 g chiftea de burger · 2 linguri sos de burger · ≈100 g salată verde, ceapă roșie, cornișoni, ardei copți · 200 g cartofi la cuptor",
  f"14:45 Încălzești chifteaua (tigaie cu capac + 1 lingură apă, 3–4 min) și cartofii (air fryer 190 °C, 4–5 min), în termos. Chifla, sosul și salata separat, în geantă: le asamblează la masă."),
 ("20:30", "Cină", "<b>Frigărui:</b> 160 g frigărui de pui · 250 g sote de dovlecel, ardei, ciuperci și ceapă · bol mare de salată verde doar cu lămâie",
  "20:15 Încălzești cutia 1,5–2 min la microunde. Salata cu lămâie."),
], "22:00 Scoți în frigider, pentru vineri: puiul 120 g, sote-ul de vită 160 g și dorada.")
VINERI = day("Vineri", ("zi de sală", ""), [
 ("09:15", "Mic dejun", "<b>Shakshuka verde:</b> 200 g praz, dovlecel și spanac · 1 linguriță ulei · 3 ouă + 2 albușuri · 2 felii pâine integrală (≈60 g) · 5 măsline negre · fulgi de ardei, după plac",
  "09:00 Tai prazul și dovlecelul, le înmoi în tigaie cu spanacul în 1 linguriță ulei, spargi ouăle deasupra și pui capacul până se fac."),
 ("12:30", "Prânz", "<b>Supă de linte + pui:</b> ≈300 ml supă de linte · 120 g piept de pui în bucăți · 150 g bețe de morcov și castravete · 1 felie pâine integrală (≈30 g)",
  "09:55 Încălzești supa până clocotește și o pui în cana-termos. Pe masă: puiul, bețele de morcov și castravete, felia de pâine."),
 ("14:00", "Înainte de sală", "1 măr + cafea simplă", ""),
 ("16:45", "După sală", "<b>Sote de vită cu cartofi:</b> 160 g sote de vită · 350 g cartofi fierți cu pătrunjel, fulgi de ardei și lămâie · 1 pară",
  f"14:45 Încălzești sote-ul și cartofii 2–3 min la microunde, în termos. Para în geantă."),
 ("20:30", "Cină", "<b>Doradă:</b> 180 g doradă gătită · 200 g legume la cuptor · bol mare de salată verde cu lămâie · 10 g nucă deasupra",
  "20:15 Dorada în air fryer, 180 °C, 8–10 min. Legumele încălzite (air fryer 180 °C, 4 min). Salata cu lămâie și nucă."),
], "Vineri seara nu mai e nimic de făcut.")
SAMBATA = day("Sâmbătă", ("zi de odihnă · fără gătit, doar încălzești (≈20 min)", " m"), [
 ("09:00", "Mic dejun", "<b>Farfurie cu ouă fierte</b>, ca joi: 3 ouă + 2 albușuri · 2 felii pâine · 100 g castravete · ardei lung · rucola · 1 portocală mare", "Ca joi."),
 ("12:30", "Prânz", "<b>Ton cu quinoa:</b> 1 conservă ton + 180 g quinoa · 150 g castravete, pătrunjel, ceapă verde, ardei copți · sos: 1 linguriță ulei + lămâie",
  "Amesteci tonul cu quinoa din cutie, legumele și sosul (4 min)."),
 ("14:00", "", "Doar cafea (nu e antrenament)", ""),
 ("16:45", "Masa de după-amiază", "<b>Burger + cartofi:</b> chiflă, 150 g chiftea, 2 linguri sos, salată-ceapă-cornișoni-ardei · 100 g cartofi la cuptor (jumătate, e zi de odihnă)",
  "Chifteaua crudă congelată în air fryer, 200 °C, 14–16 min (71 °C). Chifla congelată 1–2 min în tigaie. Cartofii încălziți în air fryer."),
 ("20:15", "Cină", "<b>Frigărui:</b> 160 g frigărui · 250 g sote de legume · salată verde cu lămâie", "Încălzești cutia, salata cu lămâie."),
], "22:00 Scoți în frigider, pentru duminică: supa, puiul 120 g, sote-ul de vită 160 g, peștele de duminică seara și (în săptămâna normală) o bilă de aluat de pizza.")
DUMINICA = day("Duminică", ("zi de odihnă · ziua mare de gătit", " k"), [
 ("09:00", "Mic dejun", "<b>Shakshuka verde</b>, ca vineri: 200 g praz, dovlecel, spanac · 3 ouă + 2 albușuri · 2 felii pâine · 5 măsline", "Ca vineri."),
 ("12:30", "Prânz", "<b>Supă de linte + pui:</b> ≈300 ml supă · 120 g pui · 150 g bețe de morcov și castravete · 1 felie pâine", "Încălzești supa până clocotește."),
 ("14:00", "", "Doar cafea", "≈14:00 Cumpărăturile (≈45 min), sau comanzi online cu o seară înainte, cu livrare la 15:00."),
 ("15:00", "", "", "<b>Ziua mare de gătit: 15:00–17:35</b> (vezi pagina „Duminică”)."),
 ("16:45", "Masa de după-amiază", "<b>Sote de vită cu bulgur:</b> 160 g sote · 125 g bulgur (jumătate, e zi de odihnă) · fără fruct", "Bulgurul congelat, cu 1 lingură apă, 2,5 min la microunde; sote-ul 2 min."),
 ("20:00", "Cină (împreună)", "<b>Pește:</b> 180 g biban sau doradă · 150 g broccoli · salata proaspătă din sesiune", "Peștele în air fryer, 180 °C, 8–10 min; broccoli 1 min la microunde."),
], "După sesiune: scoți somonul pentru luni din congelator în frigider și pui cutiile de luni pe raftul din față.")

HTML = f"""<!doctype html><html lang="ro"><head><meta charset="utf-8"><title>Bucătăria lui Cem, pe scurt</title><style>{CSS}</style></head><body>

<h1>Bucătăria lui Cem, pe scurt</h1>
<p class="sub">Ghidul lui Cem (noiembrie 2026), rescris simplu. Aceleași gramaje. Toate gramele sunt pentru mâncarea gătită.</p>

<div class="grid2">
 <div class="box warn"><b class="t">Ce nu intră deloc</b>
  <ul><li><b>Orez</b>, sub orice formă (nici făină, amidon sau oțet de orez).</li>
  <li><b>Lactoză</b>: lapte, iaurt, brânză, unt, smântână, zer. Doar „laktozsuz”, puțin, opțional.</li>
  <li><b>Roșii</b>: nici pastă, ketchup, sos, roșii uscate, praf de roșii.</li>
  <li>Fără sosuri gata, cuburi de supă, bulion, amestecuri de condimente. Doar condimente simple.</li></ul></div>
 <div class="box"><b class="t">Reguli de siguranță</b>
  <ul><li>Termometru: <b>pui 74 °C · carne tocată 71 °C · pește 63 °C · orice reîncălzire 74 °C</b>.</li>
  <li>Mâncarea gătită intră în frigider în cel mult 2 ore. Puiul crud nu se spală, doar se tamponează.</li>
  <li>Decongelezi în frigider, nu pe blat. Ce s-a decongelat nu se mai congelează.</li>
  <li>±10 g nu contează. Cântărești când pui în cutii.</li></ul></div>
</div>

<h2>Săptămâna, dintr-o privire</h2>
<table>
 <thead><tr><th style="width:14%">Zi</th><th>Ce faci tu (≈25–30 min pe zi, plus cele două zile de gătit)</th></tr></thead>
 <tbody>
 <tr><td><b>Luni</b></td><td>09:00 omleta · 09:55 wrap-ul pe masă · 14:45 masa de după sală în termos · 20:15 somonul în air fryer</td></tr>
 <tr><td><b>Marți</b></td><td>09:00 terciul · 14:45 pizza încălzită · 20:15 sote-ul încălzit · <b>22:00 scoți bibanul</b></td></tr>
 <tr><td><b>Miercuri</b></td><td>09:00 omleta cu spanac · 14:45 cutia în termos · <span class="tag k">17:00–19:15 gătești</span> · 20:15 bibanul în air fryer</td></tr>
 <tr><td><b>Joi</b></td><td>09:00 ouăle fierte · 14:45 burgerul în termos · 20:15 frigăruile încălzite · <b>22:00 scoți puiul, sote-ul, dorada</b></td></tr>
 <tr><td><b>Vineri</b></td><td>09:00 shakshuka · 09:55 supa în termos · 14:45 sote cu cartofi în termos · 20:15 dorada în air fryer</td></tr>
 <tr><td><b>Sâmbătă</b></td><td>Fără gătit: doar încălzești și servești (≈20 min) · <b>22:00 scoți supa, puiul, sote-ul, peștele, bila de pizza</b></td></tr>
 <tr><td><b>Duminică</b></td><td>09:00 shakshuka · 14:00 cumpărăturile · <span class="tag k">15:00–17:35 gătești</span> · 20:00 peștele împreună · scoți somonul pentru luni</td></tr>
 </tbody></table>

<div class="grid2">
 <div class="box"><b class="t">Frigiderul</b>Sus: cutiile săptămânii în ordinea zilelor (stânga → dreapta). Mijloc: salata, sosurile, ouăle. Jos: peștele și carnea la decongelat, în cutie închisă.</div>
 <div class="box"><b class="t">Eticheta pe fiecare cutie</b>ZIUA · MASA · ce e + grame · gătit pe · expiră pe. Ex.: „Marți · după sală · pizza cu pui · gătit 15.11 · expiră 18.11”. Pe porțiile congelate scrii și cum se încălzesc.</div>
</div>
<div class="box mint"><b class="t">Zilele de sală și zilele de odihnă</b>Luni–vineri e sală: înainte, un fruct + cafea; după, masa mare cu carbohidrați. Sâmbătă și duminică: doar cafea la 14:00 și jumătate din carbohidrații de după-amiază. Seara Cem mănâncă puțini carbohidrați: proteină + legume + salată.</div>

<div class="page"><h2>Ce mănâncă Cem, zi cu zi</h2>
{LUNI}{MARTI}</div>
<div class="page">{MIERCURI}{JOI}</div>
<div class="page">{VINERI}{SAMBATA}</div>
<div class="page">{DUMINICA}

<h2 style="margin-top:14px">Duminică: ziua mare de gătit · 15:00–17:35</h2>
<p class="sub" style="margin-top:0">Azi gătești pentru luni, marți și miercuri, plus câteva porții pentru congelator. Sunt 11 lucruri la foc, dar 5 merg singure în cuptor și în air fryer.</p>
<div class="grid2">
 <div class="dev cup"><b class="t">Cuptor (3 tăvi, una după alta)</b>
  <ol><li>Piept de pui 1,4 kg + chiftele 10 × 50 g: 220 °C, ≈20 min</li>
  <li>Pulpe de pui 600 g + cartof dulce 400 g + legume 400 g: 200 °C, 25–30 min</li>
  <li>Pizza (1 bilă de aluat): la maxim, 8–10 min</li></ol></div>
 <div class="dev af"><b class="t">Air fryer</b>Ardei kapia întregi, 2 tranșe × 500 g: 200 °C, 12–15 min fiecare</div>
 <div class="dev ar"><b class="t">Aragaz</b>
  <ol><li>14 ouă fierte: 10–11 min</li><li>Pilaf de bulgur 340 g: 15 min + 10 min odihnă</li>
  <li>Sote de vită 800 g: ≈35 min</li><li>Hrișcă 100 g: 12–15 min</li><li>Broccoli 550 g la abur: 4–5 min</li></ol></div>
 <div class="dev ff"><b class="t">Fără foc</b>Salata verde în 4 cutii · borcanul cu sos de salată · borcanul de ton cu năut pentru marți · wrap-ul de luni</div>
</div>
</div><div class="page"><h2>Duminică: ordinea, pas cu pas</h2>
<ol class="steps">
 <li><b class="h">15:00</b> Golești pungile de cumpărături, speli legumele și verdețurile, le lași la scurs. Pui cutiile, borcanele și etichetele pe blat (≈15 min).</li>
 <li><b class="h">15:15</b> Pornești cuptorul la 220 °C cu ventilație. Pui apă la fiert pentru ouă. Scoți air fryer-ul pe blat.</li>
 <li><b class="h">Puiul.</b> Tamponezi 1,4 kg piept și 600 g pulpe; fileurile groase le tai în două pe orizontală (2 cm). Marinezi în 2 boluri (ulei, lămâie, usturoi, cimbru, chimion, turmeric, sare, piper) și le pui la frigider.</li>
 <li><b class="h">Ouăle.</b> 14 ouă cu lingura în apa care fierbe, 10–11 min, apoi 5 min în apă cu gheață. În cutie, cu coajă, cu data scrisă.</li>
 <li><b class="h">Chiftelele.</b> 500 g carne tocată slabă + ½ ceapă rasă și stoarsă + pătrunjel + 1 ou + chimion, piper, sare. Frămânți, faci 10 chiftele plate de 50 g, pe tavă cu hârtie de copt.</li>
 <li><b class="h">Cuptor 220 °C:</b> puiul pe tava de sus, chiftelele jos. <b class="h">Bulgurul:</b> 1 ceapă + 1 ardei căliți 5 min în 1,5 linguri ulei, 340 g bulgur 2 min, apoi 700 ml apă fierbinte + sare; când fierbe, capac și foc mic 15 min.</li>
 <li><b class="h">Air fryer 200 °C:</b> primii 500 g de ardei kapia întregi, 12–15 min.</li>
 <li><b class="h">Sote-ul de vită.</b> Tamponezi 800 g cuburi și le rumenești în tigaia foarte încinsă, în 2 tranșe, câte 3–4 min. Scoți chiftelele (71 °C). În tigaia cu vita călești 5 min ceapa, 250 g ciuperci și ardeiul verde. Ardeii copți în vas cu capac, la transpirat; a doua tranșă în air fryer. La vită: usturoi, cimbru, chimion, 150 ml apă fierbinte, capac, foc mic 30 min.</li>
 <li><b class="h">Scoți puiul</b> (74 °C) și îl acoperi. Cuptorul la 200 °C. Bulgurul de pe foc: prosop de hârtie sub capac, 10 min. Tai 400 g cartof dulce și 400 g legume (dovlecel, vinete, ardei, ceapă), cu ulei și condimente.</li>
 <li><b class="h">Cuptor 200 °C:</b> pulpele pe o tavă, cartoful dulce și legumele pe cealaltă, 25–30 min. <b class="h">Hrișca:</b> 100 g + 200 ml apă + sare, foc mic 12–15 min.</li>
 <li><b class="h">Feliezi și cântărești puiul</b> (porțiile sunt în tabelul de mai jos).</li>
 <li><b class="h">Ardeii:</b> curăți coaja, cotorul și semințele (nu-i speli). Hrișca de pe foc, o afânezi. <b class="h">Broccoli:</b> 550 g la abur 4–5 min, apoi în apă cu gheață, apoi uscat. Ardeii în borcan cu ulei, usturoi, oțet de mere și sare.</li>
 <li><b class="h">Sote-ul:</b> când a scăzut zeama, sare și îl iei de pe foc.</li>
 <li><b class="h">Scoți pulpele</b> (74 °C), cartoful dulce și legumele. Cuptorul la maxim, cu tava întoarsă pe raftul de jos-mijloc, 30 min (pentru pizza). Bila de aluat din frigider pe blat (stă 1 h la temperatura camerei).</li>
 <li><b class="h">Salata:</b> spălată, uscată, tăiată, în 4 cutii cu prosop de hârtie pe fund (duminică seara, luni, marți, miercuri).</li>
 <li><b class="h">Pizza:</b> bila de aluat (scoasă sâmbătă seara) întinsă pe hârtie de copt la 28–30 cm; deasupra ≈50 g sos de ardei (3–4 linguri; în săptămânile normale, 3–4 cuburi din congelator), 130 g pui, ciuperci, ceapă roșie, 5 măsline feliate, cimbru (cașcaval fără lactoză doar dacă vrei, maximum 25 g). Pe tava încinsă, 8–10 min. Între timp faci borcanul cu sos de salată și borcanul de ton cu năut.</li>
 <li><b class="h">Cutiile</b> (tabelul de mai jos). Pizza la răcit, feliată, rucola separat. Bulgurul 2 × 125 g la congelator, în pungi plate, fără aer.</li>
 <li><b class="h">La final:</b> frigiderul pe zile (sus: luni → miercuri), lista de pe ușa congelatorului, vasele și blatul (≈20 min). Seara: peștele împreună; scoți somonul pentru luni.</li>
</ol>
</div>

<div class="page">
<h3 style="margin-top:0">Duminică: ce pui în fiecare cutie</h3>
<table><thead><tr><th style="width:24%">Cutia</th><th>Ce pui (gătit)</th></tr></thead><tbody>
 <tr><td><b>Luni · prânz</b></td><td>Wrap: 1 lipie integrală + 160 g pui + 100 g salată verde, castravete, ceapă roșie, pătrunjel + 50 g ardei copți + 1 linguriță muștar, strâns în folie</td></tr>
 <tr><td><b>Luni · după sală</b></td><td>180 g chiftele + 250 g bulgur + 100 g ardei copți</td></tr>
 <tr><td><b>Marți · prânz</b> (borcan)</td><td>1 conservă ton + 150 g năut + 150 g castravete, ceapă roșie, pătrunjel, ardei copți · sosul (1 linguriță ulei + lămâie) în cutiuță separată</td></tr>
 <tr><td><b>Marți · după sală</b></td><td>Pizza feliată · 20 g rucola separat</td></tr>
 <tr><td><b>Marți · cină</b></td><td>160 g sote de vită (+ ce mai rămâne din sote)</td></tr>
 <tr><td><b>Miercuri · prânz</b></td><td>150 g pui + 240 g hrișcă + 1 lingură pesto + 150 g rucola, castravete, rodie</td></tr>
 <tr><td><b>Miercuri · după sală</b></td><td>160 g pulpe + 300 g cartof dulce + 200 g legume la cuptor</td></tr>
 <tr><td><b>Broccoli</b></td><td>3 cutii: duminică 150 g · luni 150 g · miercuri 200 g</td></tr>
 <tr><td><b>Salată</b></td><td>4 cutii: duminică seara · luni · marți · miercuri</td></tr>
 <tr><td><b>Frigider, comun</b></td><td>14 ouă fierte (cu coajă) · borcanul cu ardei copți (ține până joi) · borcanul cu sos de salată</td></tr>
 <tr><td><b>Congelator</b></td><td>Pui 120 g (vineri) · sote 160 g (vineri) · pui 120 g + sote 160 g (duminica viitoare) · bulgur 2 × 125 g · piept de pui 2 × 160 g · pulpe 2 × 130 g · chiftele 200 g (rezervă)</td></tr>
</tbody></table>
<p style="color:var(--muted);font-size:8.6pt">Puiul (≈1 kg gătit): wrap 160 g · pizza 130 g · miercuri 150 g · vineri 120 g · duminica viitoare 120 g · rezervă 2 × 160 g.</p>

<h2 style="margin-top:12px">Miercuri: a doua zi de gătit · 17:00–19:15</h2>
<p class="sub" style="margin-top:0">Azi gătești pentru joi, vineri și sâmbătă. Sunt 8 lucruri la foc.</p>
<div class="grid2">
 <div class="dev cup"><b class="t">Cuptor</b>
  <ol><li>Frigărui de pui (700 g piept): 230 °C pe grătar, 14–18 min, întoarse la jumătate</li>
  <li>Legume la cuptor ≈350 g: 220 °C, 25–30 min</li></ol></div>
 <div class="dev af"><b class="t">Air fryer</b>Cartofi felii 450 g: 200 °C, 18–22 min, scuturați de 2 ori</div>
 <div class="dev ar"><b class="t">Aragaz</b>
  <ol><li>Cartofi fierți 400 g, cu coajă: ≈30 min</li><li>Quinoa 125 g: 15 min + 10 min odihnă</li>
  <li>Chifteaua de burger pentru joi, în tigaia de fontă</li><li>Sote de legume ≈700 g: 10–12 min, foc mare</li></ol></div>
 <div class="dev ff"><b class="t">Fără foc</b>Sosul de burger · salata în 3 cutii · borcanul de ton cu quinoa pentru joi</div>
</div>
</div><div class="page"><h2>Miercuri: ordinea, pas cu pas</h2>
<ol class="steps">
 <li><b class="h">17:00</b> Golești pungile, speli legumele, pui cutiile și etichetele pe blat (≈15 min).</li>
 <li><b class="h">17:15</b> Cuptorul la 230 °C (pe grill, dacă are). Scoți din congelator 1 chiftea de burger crudă.</li>
 <li><b class="h">Cartofii fierți:</b> 400 g cu coajă în apă rece cu sare, la fiert (≈30 min). Frigăruile de lemn în apă.</li>
 <li><b class="h">Frigăruile:</b> 700 g piept tăiat cuburi de 3 cm, marinat (ulei, lămâie, usturoi, cimbru, chimion, turmeric, sare, piper), pe frigărui cu ceapă roșie și dovlecel, pe rând.</li>
 <li><b class="h">Quinoa:</b> 125 g spălată în sită + 220 ml apă; după ce fierbe, foc mic 15 min, apoi 10 min cu capacul pus.</li>
 <li><b class="h">Frigăruile în cuptor</b>, pe grătar, 14–18 min, întoarse la jumătate. Tai 450 g cartofi felii (ca feliile de măr), 10 min în apă rece. Tai legumele pentru sote (≈700 g: dovlecel, ciuperci, ardei, ceapă, morcov) și pentru cuptor (≈350 g).</li>
 <li><b class="h">Cartofii fierți:</b> scurși, întinși pe tavă. <b class="h">Cartofii felii:</b> uscați, cu ulei și condimente, în air fryer 200 °C, 18–22 min.</li>
 <li><b class="h">Scoți frigăruile</b> (74 °C). Cuptorul la 220 °C, tava cu legume 25–30 min.</li>
 <li><b class="h">Chifteaua de joi:</b> tigaia de fontă foarte încinsă, chifteaua sărată, 5–6 min pe fiecare parte (dacă e încă înghețată; decongelată 3–4 min). 71 °C în mijloc.</li>
 <li><b class="h">Sote-ul de legume:</b> foc mare, 10–12 min: întâi morcovul și ceapa, apoi ciupercile, apoi dovlecelul și ardeiul; la final usturoi și cimbru. Întins pe tavă la răcit.</li>
 <li><b class="h">Sosul de burger</b> în borcan (rețeta pe ultima pagină). Scoți legumele de la cuptor.</li>
 <li><b class="h">Salata</b> în 3 cutii (joi, vineri, sâmbătă).</li>
 <li><b class="h">Cutiile</b> (tabelul de mai jos).</li>
 <li><b class="h">La final:</b> frigiderul pe zile (sus: joi → sâmbătă), lista de stoc, vasele și blatul (≈20 min). 20:15 bibanul pentru Cem.</li>
</ol>
<h3>Miercuri: ce pui în fiecare cutie</h3>
<table><thead><tr><th style="width:24%">Cutia</th><th>Ce pui (gătit)</th></tr></thead><tbody>
 <tr><td><b>Joi · prânz</b> (borcan)</td><td>1 conservă ton + 180 g quinoa + 150 g castravete, pătrunjel, ceapă verde, ardei copți · sosul și 1 ou fiert separat</td></tr>
 <tr><td><b>Joi · după sală</b></td><td>Setul de burger: chifteaua gătită · chifla în pungă separată · 2 linguri sos în cutiuță · ≈100 g salată, ceapă roșie, cornișoni, ardei copți în pungă · + 200 g cartofi la cuptor</td></tr>
 <tr><td><b>Joi · cină</b></td><td>160 g frigărui + 250 g sote de legume</td></tr>
 <tr><td><b>Vineri · după sală</b></td><td>350 g cartofi fierți cu pătrunjel, fulgi de ardei și lămâie (sote-ul de vită vine din congelator)</td></tr>
 <tr><td><b>Vineri · cină</b></td><td>200 g legume la cuptor (dorada vine din congelator)</td></tr>
 <tr><td><b>Sâmbătă · prânz</b></td><td>180 g quinoa (tonul îl amesteci sâmbătă)</td></tr>
 <tr><td><b>Sâmbătă · după-amiază</b></td><td>100 g cartofi la cuptor (chifteaua crudă și chifla vin din congelator)</td></tr>
 <tr><td><b>Sâmbătă · cină</b></td><td>160 g frigărui + 250 g sote de legume</td></tr>
 <tr><td><b>Salată</b></td><td>3 cutii: joi · vineri · sâmbătă</td></tr>
 <tr><td><b>Borcan</b></td><td>Sosul de burger (joi și sâmbătă)</td></tr>
</tbody></table>

<div class="box"><b class="t">Doar din când în când (nu în fiecare săptămână)</b>
 <ul>
 <li><b>Duminică, la 4 săptămâni (+30 min):</b> aluat de pizza (4 bile), pesto, sos de ardei din 300 g ardei copți (în tava de gheață). Pizza de marți ia 50 g de sos.</li>
 <li><b>Miercuri, la 2 săptămâni (+30 min):</b> <b>supă de linte</b> (6 vase: vineri, duminică, 4 la congelator) și <b>5 chiftele de burger</b> din 1 kg carne (una o gătești pentru joi, 4 crude la congelator). Atunci nu mai scoți chifteaua din congelator.</li>
 <li><b>Miercuri, la 4 săptămâni:</b> 8 <b>chifle de burger</b> (1 pentru joi, 1 pentru sâmbătă, 6 tăiate în două la congelator).</li>
 </ul></div>
<div class="box"><b class="t">Dacă nu ai timp</b>
 <ul><li><b>Obosită:</b> salata o speli și o tai în seara dinainte.</li>
 <li><b>Planul B</b> pentru o săptămână aglomerată (≈1 h 45 min cu tot): piept de pui + bulgur + broccoli + salată + 14 ouă fierte; restul din congelator.</li>
 <li><b>Miercuri nu se poate:</b> gătești joi la 15:00; joi la prânz și după sală, porții din congelator și un borcan de ton de 5 minute.</li></ul></div>

<h2 style="margin-top:12px">Rețetele, pe scurt</h2>
<div class="cols2">
 <div class="rec"><b>Piept de pui la cuptor</b> · 1,4 kg → ≈1 kg<br><span>1 lingură ulei, 3 linguri lămâie, 3 căței usturoi, 1 linguriță cimbru, 1 chimion, 1 turmeric, ½ piper, 2 lingurițe sare. 30 min–12 h la frigider. 220 °C, 18–22 min, 74 °C. 5–10 min acoperit, apoi feliat.</span></div>
 <div class="rec"><b>Pulpe de pui</b> · 600 g<br><span>Aceeași marinadă (mai puțină). Fără piele. 200 °C, 25–30 min, 74 °C. Grăsimea din tavă nu intră în cutie.</span></div>
 <div class="rec"><b>Chiftele</b> · 500 g carne → 10 × 50 g<br><span>½ ceapă rasă și stoarsă, pătrunjel, 1 ou, chimion, piper, sare. Fără pâine sau pesmet. 220 °C, 12–15 min, 71 °C.</span></div>
 <div class="rec"><b>Pilaf de bulgur</b> · 340 g → ≈1 kg<br><span>1 ceapă + 1 ardei în 1,5 linguri ulei, bulgurul 2 min, 700 ml apă fierbinte, 1,5 lingurițe sare, ½ piper. 15 min capac, 10 min odihnă, 1 linguriță mentă.</span></div>
 <div class="rec"><b>Sote de vită</b> · 800 g<br><span>Rumenită în 2 tranșe. 1 ceapă, 250 g ciuperci, 2 ardei verzi, 2 căței usturoi, 1 lingură ulei, 1 linguriță cimbru, ½ chimion, ½ piper, 100–150 ml apă. Foc mic 30–40 min, sarea (1 linguriță) la sfârșit. Fără salça.</span></div>
 <div class="rec"><b>Ardei copți</b> · 1 kg → ≈600 g<br><span>Air fryer 200 °C 12–15 min, 10 min la transpirat sub capac, curățați (nespălați). Cu 1 linguriță ulei, 1 cățel usturoi, 1 lingură oțet de mere, ½ linguriță sare.</span></div>
 <div class="rec"><b>Cartof dulce</b> · 400 g<br><span>Cuburi de 3 cm cu coajă, 1 linguriță ulei, ½ linguriță scorțișoară sau chimion, sare, piper. 200 °C, 25–30 min.</span></div>
 <div class="rec"><b>Legume la cuptor</b><br><span>Dovlecel, vinete, ardei, ceapă (și morcov, conopidă, ciuperci), cu ulei, cimbru, chimion, usturoi granulat, sare. Într-un singur strat. 200–220 °C, 25–30 min.</span></div>
 <div class="rec"><b>Hrișcă</b> · 100 g + 200 ml apă<br><span>Spălată, cu sare. Foc mic, capac, 12–15 min, 5 min odihnă.</span></div>
 <div class="rec"><b>Broccoli la abur</b> · 550 g<br><span>4–5 min în coșul de abur, 2 min în apă cu gheață, uscat bine.</span></div>
 <div class="rec"><b>Salata verde</b><br><span>Salată sau iceberg, rucola, castraveți, pătrunjel, mărar, ceapă roșie, morcov ras, varză roșie. Castravetele și rodia separat. Fără sos în cutie.</span></div>
 <div class="rec"><b>Sos de salată</b> (borcan, ține 5–7 zile)<br><span>3 linguri ulei, 6 linguri lămâie, 1 lingură oțet de mere sau nar ekşisi, 1 linguriță muștar, 1 cățel usturoi, 1 linguriță mentă sau cimbru, ½ linguriță sare, piper (1 linguriță miere, opțional). 2 linguri pe salată.</span></div>
 <div class="rec"><b>Pizza cu pui</b> · 1 bilă (≈175 g)<br><span>Cuptorul la maxim cu tava întoarsă, 30 min înainte. Întinsă la 28–30 cm. Sos de ardei, 130 g pui, ciuperci, ¼ ceapă roșie, 5 măsline, ½ linguriță cimbru. 8–10 min. Rucola după.</span></div>
 <div class="rec"><b>Frigărui de pui</b> · 700 g<br><span>Cuburi de 3 cm, marinada de la pui, pe rând cu ceapă roșie și dovlecel. 230 °C pe grătar, 14–18 min, 74 °C.</span></div>
 <div class="rec"><b>Cartofi felii (air fryer)</b> · 450 g<br><span>10 min în apă rece, uscați, cu ulei, cimbru, rozmarin, usturoi granulat, sare, piper. 200 °C, 18–22 min.</span></div>
 <div class="rec"><b>Quinoa</b> · 125 g + 220 ml apă<br><span>Spălată 1 min în sită. Foc mic 15 min, 10 min cu capac, afânată.</span></div>
 <div class="rec"><b>Sote de legume</b> · ≈700 g<br><span>Foc mare: morcov + ceapă 3 min, ciuperci 3 min, dovlecel + ardei 4–5 min, usturoi + cimbru 1 min. 1 lingură ulei.</span></div>
 <div class="rec"><b>Sos de burger</b><br><span>1 lingură tahini + 2 linguri apă, 3 linguri muștar, 3 linguri cornișoni tocați + 1 lingură zeamă, 1 linguriță miere, ½ usturoi granulat, ½ ceapă pudră, piper, ½ turmeric.</span></div>
 <div class="rec"><b>Chiftea de burger</b> · 200 g crudă → 150 g<br><span>Tigaie de fontă foarte încinsă, sare pe ambele părți, 3–4 min pe parte (congelată 5–6). Sau air fryer 200 °C 10–12 min (congelată 14–16). 71 °C.</span></div>
 <div class="rec"><b>Pește</b> (somon, biban, doradă)<br><span>Decongelat în frigider din seara dinainte. Lămâie, usturoi, mărar, ulei, sare, piper. Air fryer 180 °C 8–10 min, 63 °C. Se gătește în ziua în care se mănâncă.</span></div>
 <div class="rec"><b>Supă de linte</b> (la 2 săptămâni) · 6 vase<br><span>1 ceapă + 2 morcovi în 1 lingură ulei 5 min, 250 g linte spălată, 1,8 l apă fierbinte, 1 linguriță chimion, 1 boia dulce; 25 min, mixată, 1,5 lingurițe sare, piper. Lămâia la masă.</span></div>
 <div class="rec"><b>Chiftele de burger</b> (la 2 săptămâni) · 1 kg → 5<br><span>Carne rece, 1 ceapă mică rasă și stoarsă, 2 căței usturoi, 1 linguriță piper. 5 × 200 g, 12 cm, cu adâncitură în mijloc. Fără sare în compoziție.</span></div>
 <div class="rec"><b>Aluat de pizza</b> (la 4 săptămâni) · 4 bile<br><span>400 g făină integrală, 5 g drojdie, 300 ml apă călduță cu 1 linguriță miere; 20 min; 8 g sare + 1 lingură ulei, 8–10 min frământat, 1,5 h la dospit. 3 bile la congelator.</span></div>
 <div class="rec"><b>Chifle de burger</b> (la 4 săptămâni) · 8<br><span>300 g făină integrală + 100 g albă, 7 g drojdie, 1 linguriță miere, 260 ml apă, 7 g sare, 2 linguri ulei. 1 h dospit, 8 bile, încă 30–40 min. Gălbenuș + susan, 200 °C 14–18 min.</span></div>
 <div class="rec"><b>Pesto fără parmezan</b> (la 4 săptămâni)<br><span>60 g busuioc, 30 g nucă, 1 cățel usturoi, 2 linguri lămâie, 2 linguri apă, ½ linguriță sare, 60 ml ulei. Porția: 1 lingură. Restul în tava de gheață.</span></div>
 <div class="rec"><b>Sos de ardei pentru pizza</b> (la 4 săptămâni)<br><span>350 g ardei copți, 2 căței usturoi, 1 lingură ulei, 1 linguriță cimbru, 1 linguriță oțet de mere, ½ sare; mixat, 5–10 min pe foc. În tava de gheață (1 cub ≈ 1 lingură).</span></div>
</div>
<p style="color:var(--muted);font-size:8.4pt;margin-top:8px">Rescris din „Bucătăria lui Cem · ghid pentru Kristine” (noiembrie 2026), cu aceleași gramaje. Singura schimbare: legumele pentru micul dejun le tai dimineața, pe loc. Pentru orice schimbare de meniu, întreabă-l pe Cem.</p>
</div>
</body></html>"""


def main():
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "cem.html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(HTML)
        js = os.path.join(d, "pdf.js")
        with open(js, "w") as f:
            f.write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2],{waitUntil:'load'});await p.pdf({path:process.argv[3],printBackground:true,preferCSSPageSize:true,
displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:7pt;color:#5C5466;width:100%;text-align:center;font-family:Inter">Bucătăria lui Cem, pe scurt · pagina <span class=pageNumber></span> din <span class=totalPages></span></div>'});await b.close();})();""")
        subprocess.run(["node", js, src, OUT], check=True)
    print(OUT)


if __name__ == "__main__":
    sys.exit(main())
