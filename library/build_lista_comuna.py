#!/usr/bin/env python3
"""
Lista de cumpărături comună, Kristine + Cem (o săptămână obișnuită), ca PDF A4.

Sursele: ghidul de bucătărie al lui Cem (fără orez, fără lactoză, fără roșii) și
PROGRAM-ALIMENTATIE.md (Kristine: pescetariană, fără carne).

Rulezi:   python3 library/build_lista_comuna.py
Rezultat: LISTA-CUMPARATURI-KRISTINE-CEM.pdf (în rădăcina proiectului)
"""
import html
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "LISTA-CUMPARATURI-KRISTINE-CEM.pdf")

A, C, K = "amandoi", "cem", "kristine"
WHO = {A: "Amândoi", C: "Cem", K: "Kristine"}

# (produs, în magazin (TR), cât în total, pentru cine, notă)
SECTIONS = [
    ("Pește și carne", [
        ("ton în apă (conservă)", "Ton balığı, suda", "8 conserve", A, "Cem 3 + Kristine 5. Aceeași marcă pentru amândoi: pe etichetă doar ton, apă, sare."),
        ("pește alb (biban, doradă, merluciu)", "Levrek / çipura / mezgit fileto", "Cem 3 × 220 g · Kristine 4 × 150 g", A, "La pescărie, curățat, făcut file și porționat; pungile etichetate pe nume. Nemarinat, fără pané."),
        ("somon (sau păstrăv pentru Kristine)", "Somon fileto · alabalık fileto", "Cem 1 × 180 g · Kristine 2 × 120 g", A, "Simplu, nu teriyaki sau marinat."),
        ("creveți congelați, curățați", "Dondurulmuş karides (ayıklanmış)", "300 g", K, "Pentru 2 prânzuri cu paste."),
        ("piept de pui (file)", "Tavuk göğüs fileto", "2,1 kg", C, "1,4 kg duminică + 0,7 kg miercuri. Nemarinat, fără condimente."),
        ("pulpe de pui dezosate, fără piele", "Tavuk but, derisiz kemiksiz", "600 g", C, "Cu os ≈800 g."),
        ("carne tocată de vită slabă (10–15%)", "Az yağlı dana kıyma", "500 g", C, "Tocată la măcelar din pulpă sau spată. Nu «köftelik»."),
        ("carne de vită cuburi, slabă", "Az yağlı dana kuşbaşı", "800 g", C, "Pulpă, antricot sau mușchi. Nemarinată."),
    ]),
    ("Ouă", [
        ("ouă", "Yumurta", "1 cofraj de 30 + 1 de 15", A, "Cem 30 + Kristine 12–15."),
        ("albuș lichid pasteurizat", "Pastörize sıvı yumurta akı", "≈1,25 l", A, "Cem 500 ml + Kristine 750 ml. Doar albuș, fără «süt» sau arome."),
    ]),
    ("Lactate (doar Kristine: au lactoză)", [
        ("chefir", "Kefir (sade)", "2 l", K, "Pentru shake-ul zilnic. Simplu, fără arome."),
        ("lapte 1,5%", "Yarım yağlı süt", "1 l", K, "Ovăz și deserturi."),
        ("iaurt grecesc 2% (strecurat)", "Light süzme yoğurt", "≈1,2 kg", K, "Mic dejun, gustare, mousse, sosul de la wrap."),
        ("brânză de vaci slabă", "Lor peyniri", "400 g", K, "Lorul e varianta turcească: slab și cu multă proteină."),
        ("skyr (sau încă iaurt strecurat)", "Skyr · süzme yoğurt", "300 g", K, "Pentru desertul cu banană la air fryer."),
        ("mozzarella light", "Light mozzarella", "125 g", K, "Quesadilla cu ton."),
        ("feta (opțional) · parmezan (bucată mică)", "Beyaz peynir · parmesan", "100 g · 50 g", K, "Puțin, la salate și paste."),
    ]),
    ("Pâine, cereale, paste", [
        ("lipie integrală (lavaș)", "Tam buğday lavaş", "2 pachete", A, "Câte unul. Aceeași marcă verificată: fără «yoğurt», «süt», «pirinç»."),
        ("pâine integrală", "Tam buğday ekmeği", "2 pâini", A, "Cem 1 + Kristine 1. Feliată și congelată câte 2 felii. Fără «süt tozu», «margarin», «pirinç unu»."),
        ("fulgi de ovăz", "Yulaf ezmesi", "2 pachete × 500 g", A, "Simpli, nu instant sau cu arome. Ajung ~2 săptămâni amândurora."),
        ("paste (integrale, dacă vrei)", "Makarna · tam buğday makarna", "500 g", K, "Ajung ~2 săptămâni."),
        ("bulgur pentru pilaf (bob mare)", "Pilavlık bulgur (iri)", "1 kg", C, "Ajunge ~3 săptămâni. Doar bulgur, nu «pilav karışımı»."),
        ("quinoa", "Kinoa", "500 g", C, "Ajunge ~4 săptămâni."),
        ("hrișcă", "Karabuğday", "500 g", C, "Ajunge ~5 săptămâni."),
    ]),
    ("Legume", [
        ("castraveți", "Salatalık", "≈3 kg", A, "Cem 2 kg + Kristine 1 kg."),
        ("ardei kapia roșu", "Kırmızı kapya biber", "1,6 kg", A, "Cem 1,3 kg + Kristine 300 g."),
        ("ardei verde lung (dulce)", "Sivri / çarliston biber", "≈10 bucăți (300 g)", C, "Să nu fie iuți."),
        ("ceapă galbenă · ceapă roșie", "Kuru soğan · mor soğan", "1,3 kg · 800 g", A, "Cem 1 kg + 600 g · Kristine 3 + 2 bucăți."),
        ("usturoi", "Sarımsak", "3 căpățâni", A, "Cem 2 + Kristine 1."),
        ("dovlecei", "Kabak", "1,8 kg", A, "Cem 1,2 kg + Kristine 600 g."),
        ("broccoli", "Brokoli", "1 kg", A, "Cem 600 g + Kristine 400 g."),
        ("spanac", "Ispanak", "600 g", A, "Cem 300 g + Kristine 300 g."),
        ("salată verde / iceberg", "Marul / göbek marul", "3 bucăți", A, "Cem 2 + Kristine 1."),
        ("cartofi", "Patates", "2–2,5 kg", A, "Cem 1 kg + Kristine 1–1,5 kg. Fără părți verzi sau încolțite."),
        ("roșii · roșii cherry", "Domates · çeri domates", "5 bucăți · 250 g", K, "Doar Kristine: le ții separat și le tai pe placa ta, după mâncarea lui Cem."),
        ("ciuperci champignon", "Kültür mantarı", "800 g", C, ""),
        ("morcovi", "Havuç", "1 kg", C, ""),
        ("praz", "Pırasa", "2 fire", C, ""),
        ("rucola", "Roka", "3 legături", C, "Se ofilește repede."),
        ("pătrunjel · mărar · ceapă verde", "Maydanoz · dereotu · yeşil soğan", "3 · 1 · 1 legături", C, ""),
        ("cartofi dulci (batat)", "Tatlı patates", "400 g", C, ""),
        ("vinete · conopidă · varză roșie", "Patlıcan · karnabahar · kırmızı lahana", "1–2 · ½ · ¼", C, "Vinetele și conopida, opțional."),
        ("avocado", "Avokado", "1 bucată", C, ""),
    ]),
    ("Fructe", [
        ("banane", "Muz", "7 bucăți", A, "Cem 3 + Kristine 4."),
        ("mere", "Elma", "7 bucăți", A, "Cem 3 + Kristine 4."),
        ("lămâi", "Limon", "14 bucăți", A, "Cem 10 + Kristine 4."),
        ("curmale Medjool", "İri hurma (Medjool)", "6 bucăți", A, "Cem 2 + Kristine 4. Fără zahăr sau sirop adăugat."),
        ("portocale · mandarine · pere · rodie", "Portakal · mandalina · armut · nar", "3 · 4 · 1 · 1", C, ""),
    ]),
    ("Congelate", [
        ("fructe de pădure congelate", "Dondurulmuş orman meyveleri", "500 g", K, "Ovăz, iaurt, înghețata de banană."),
        ("fasole verde congelată", "Dondurulmuş taze fasulye", "1 pungă (450 g)", K, "Simplă, fără sos."),
    ]),
    ("Leguminoase", [
        ("năut fiert (borcan)", "Haşlanmış nohut (kavanoz)", "1 borcan (≈400 g)", C, "Doar năut, apă, sare. Nu humus."),
    ]),
    ("Ulei, nuci, măsline", [
        ("ulei de măsline extravirgin", "Sızma zeytinyağı", "1 l pe lună", A, "Amândoi îl măsoară cu lingurița."),
        ("miez de nucă", "Ceviz içi", "300 g", A, "Cem 200 g + Kristine 100 g."),
        ("migdale (opțional)", "Badem", "100 g", K, ""),
        ("măsline negre", "Siyah zeytin", "1 borcan (≈200 g)", C, "Măsline, apă, sare."),
        ("tahini · susan", "Tahin · susam", "1 borcan mic · 1 pachet mic", C, "Sosul și chiflele de burger."),
    ]),
    ("Condimente și sosuri", [
        ("cimbru (sau oregano), chimion, piper, fulgi de ardei", "Kekik, kimyon, karabiber, pul biber", "câte un pachet", A, "Condimente simple, nu amestecuri «tavuk/köfte/et baharatı»."),
        ("turmeric, boia dulce, scorțișoară", "Zerdeçal, tatlı toz kırmızı biber, tarçın", "câte un pachet", A, "Scorțișoara intră și în deserturile Kristinei."),
        ("mentă uscată, rozmarin, dafin, mărar uscat", "Kuru nane, biberiye, defne, kuru dereotu", "câte un pachet", C, ""),
        ("usturoi granulat pur · ceapă pudră pură", "Saf sarımsak tozu · saf soğan tozu", "câte un pachet", A, "Pe etichetă doar usturoi sau ceapă."),
        ("miere", "Bal", "1 borcan mic", A, ""),
        ("sare", "Tuz", "1 pachet", A, "Fără cuburi de supă sau bulion."),
        ("muștar · oțet de mere · concentrat de rodie", "Hardal · elma sirkesi · nar ekşisi (saf)", "câte unul", C, "Fără «domates», fără «pirinç sirkesi»."),
        ("sos de roșii (passata)", "Domates püresi / passata", "1 borcan", K, "Doar Kristine (shakshuka). Pe raftul ei."),
    ]),
    ("Dulce și suplimente (Kristine)", [
        ("cacao neîndulcită", "Şekersiz kakao", "1 cutie mică", K, "Mousse, mug cake, bile cu curmale."),
        ("ciocolată neagră 85%", "%85 bitter çikolata", "1 tabletă", K, "2 pătrățele pe zi, cel mult."),
        ("stevia (picături sau pudră)", "Stevia", "1 flacon", K, "Nu xilitol: e otrăvitor pentru câini și pisici."),
        ("vanilie · praf de copt", "Vanilya özü · kabartma tozu", "câte unul", K, "Pentru deserturi."),
        ("proteină whey", "Whey protein", "când se termină", K, "Are lactoză: shaker-ul și lingura ei stau separat."),
        ("creatină monohidrat", "Kreatin monohidrat", "1 cutie (ține ~2 luni)", K, "3–5 g pe zi."),
    ]),
    ("Altele", [
        ("castraveciori murați (cornișoni)", "Kornişon turşu", "1 borcan", C, "Nu «domatesli karışık turşu»."),
        ("ardei copți în borcan (rezervă)", "Közlenmiş kırmızı biber (kavanoz)", "1 borcan", C, "Ardei, apă, sare, oțet de mere sau de struguri."),
        ("cașcaval / mozzarella fără lactoză (opțional)", "Laktozsuz kaşar / mozzarella", "100 g", C, "Pe pizza maximum 25 g."),
        ("hârtie de copt, folie, pungi de congelator cu fermoar", "Yağlı kağıt, folyo, streç, dondurucu poşeti", "câte o rolă · ≈20 pungi", A, "Pungile pentru pește, pe nume."),
    ]),
]

ROTATIE = [
    ("La 2 săptămâni", "carne tocată de vită slabă 1 kg (burger) · linte roșie 250 g (supă)", C),
    ("La 4 săptămâni", "făină integrală 1 kg · făină albă 100 g · drojdie uscată 2 plicuri · busuioc proaspăt 2 legături (pesto)", C),
    ("Când se termină", "bulgur · quinoa · hrișcă · ovăz · paste · ulei de măsline · proteina și creatina Kristinei", A),
]

REGULI = [
    ("Cem nu mănâncă", "<b>orez</b> (nici făină, amidon sau oțet de orez), <b>lactoză</b> (lapte, iaurt, brânză, unt, zer) și <b>roșii</b> (nici pastă, ketchup, sos). Pe etichete în turcă: «pirinç», «süt», «süt tozu», «peyniraltı suyu», «laktoz», «tereyağı», «yoğurt», «domates», «salça»."),
    ("Kristine nu mănâncă", "<b>carne</b> (pui, vită). Mănâncă pește, ouă și lactate."),
    ("Ca să nu se amestece", "Lactatele, roșiile, passata și proteina Kristinei stau pe <b>raftul ei din frigider</b>, cu bandă roz. Mâncarea lui Cem se face prima, cu vase curate; roșiile se taie la final, pe placa Kristinei."),
    ("La pescărie", "Peștele se ia o dată pentru amândoi, porționat: <b>Cem</b> 3 × 220 g biban sau doradă + somon 180 g · <b>Kristine</b> 4 × 150 g pește alb + 2 × 120 g somon sau păstrăv. Pungile, cu nume și dată."),
]

CSS = """
@page { size: A4; margin: 13mm 12mm 14mm; }
:root { --ink:#2B2431; --muted:#5C5466; --line:#E6DCE3; --soft:#FAF5F7;
  --a:#E9E1F7; --a-ink:#4C3A78; --c:#DDE9F7; --c-ink:#2A5580; --k:#F8DCE6; --k-ink:#8A3459; }
* { box-sizing:border-box; }
body { margin:0; font-family:"Inter",sans-serif; color:var(--ink); font-size:9.3pt; line-height:1.35; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
h1 { font-family:"Inter Display","Inter",sans-serif; font-weight:800; font-size:24pt; letter-spacing:-.02em; margin:0; line-height:1.05; }
.sub { color:var(--muted); margin:4px 0 0; font-size:10pt; }
.head { display:flex; justify-content:space-between; align-items:flex-end; gap:16px; padding-bottom:9px; border-bottom:2px solid var(--ink); margin-bottom:10px; }
.legend { display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end; }
.who { display:inline-block; font-weight:700; font-size:8pt; border-radius:99px; padding:1.5px 7px; white-space:nowrap; }
.who.amandoi { background:var(--a); color:var(--a-ink); } .who.cem { background:var(--c); color:var(--c-ink); } .who.kristine { background:var(--k); color:var(--k-ink); }
.rules { display:grid; grid-template-columns:1fr 1fr; gap:6px 10px; margin-bottom:12px; }
.rule { background:var(--soft); border-radius:8px; padding:7px 9px; font-size:8.6pt; }
.rule b.t { display:block; font-size:8pt; letter-spacing:.06em; text-transform:uppercase; color:var(--k-ink); margin-bottom:2px; }
h2 { font-family:"Inter Display","Inter",sans-serif; font-size:12.5pt; font-weight:800; margin:12px 0 4px; letter-spacing:-.01em; break-after:avoid; }
table { width:100%; border-collapse:collapse; table-layout:fixed; }
thead th { text-align:left; font-size:7.3pt; letter-spacing:.07em; text-transform:uppercase; color:var(--muted); font-weight:700; padding:3px 5px; border-bottom:1px solid var(--ink); }
td { padding:4.5px 5px; border-bottom:1px solid var(--line); vertical-align:top; }
tr { break-inside:avoid; }
td.box { width:18px; } td.box span { display:inline-block; width:10px; height:10px; border:1.3px solid var(--ink); border-radius:2px; margin-top:1px; }
td.p { font-weight:600; }
td.tr { color:var(--c-ink); font-style:italic; }
td.q { font-weight:700; }
td.n { color:var(--muted); font-size:8.3pt; }
col.c1 { width:18px; } col.c2 { width:24%; } col.c3 { width:21%; } col.c4 { width:15%; } col.c5 { width:10%; } col.c6 { width:auto; }
.rot { margin-top:4px; }
.rot div { display:flex; gap:8px; padding:5px 0; border-bottom:1px solid var(--line); }
.rot b { min-width:95px; }
.foot { margin-top:12px; color:var(--muted); font-size:8pt; }
"""


def esc(s):
    return html.escape(s, quote=True)


def build_html():
    legend = "".join('<span class="who %s">%s</span>' % (k, WHO[k]) for k in (A, C, K))
    rules = "".join('<div class="rule"><b class="t">%s</b>%s</div>' % (esc(t), body) for t, body in REGULI)
    secs = []
    for name, rows in SECTIONS:
        trs = "".join(
            '<tr><td class="box"><span></span></td><td class="p">%s</td><td class="tr">%s</td><td class="q">%s</td>'
            '<td><span class="who %s">%s</span></td><td class="n">%s</td></tr>'
            % (esc(p), esc(tr), esc(q), w, WHO[w], esc(n)) for p, tr, q, w, n in rows)
        secs.append(
            '<h2>%s</h2><table><colgroup><col class="c1"><col class="c2"><col class="c3"><col class="c4"><col class="c5"><col class="c6"></colgroup>'
            '<thead><tr><th></th><th>Produs</th><th>În magazin (TR)</th><th>Cât</th><th>Pentru</th><th>Notă</th></tr></thead><tbody>%s</tbody></table>'
            % (esc(name), trs))
    rot = "".join('<div><b>%s</b><span>%s</span><span class="who %s" style="margin-left:auto">%s</span></div>'
                  % (esc(t), esc(x), w, WHO[w]) for t, x, w in ROTATIE)
    return f"""<!doctype html><html lang="ro"><head><meta charset="utf-8"><title>Lista de cumpărături · Kristine + Cem</title><style>{CSS}</style></head><body>
<div class="head"><div><h1>Lista de cumpărături<br>Kristine + Cem</h1>
<p class="sub">O săptămână obișnuită · Istanbul · noiembrie 2026 · bifezi în magazin</p></div><div class="legend">{legend}</div></div>
<div class="rules">{rules}</div>
{''.join(secs)}
<h2>Nu în fiecare săptămână</h2><div class="rot">{rot}</div>
<p class="foot">Făcută din ghidul de bucătărie al lui Cem și din programul de definire al Kristinei. Cantitățile „Amândoi” sunt totalul; în notă scrie cât e al fiecăruia. Când schimbați marca la ton, pâine, lipie sau condimente, citiți din nou eticheta.</p>
</body></html>"""


def main():
    page = build_html()
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "lista.html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(page)
        js = os.path.join(d, "pdf.js")
        with open(js, "w") as f:
            f.write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2],{waitUntil:'load'});await p.pdf({path:process.argv[3],format:'A4',printBackground:true,preferCSSPageSize:true,
displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:7pt;color:#5C5466;width:100%;text-align:center;font-family:Inter">Kristine + Cem · pagina <span class=pageNumber></span> din <span class=totalPages></span></div>'});await b.close();})();""")
        subprocess.run(["node", js, src, OUT], check=True)
    print(OUT)


if __name__ == "__main__":
    sys.exit(main())
