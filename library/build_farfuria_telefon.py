#!/usr/bin/env python3
"""
Varianta de telefon (și A4 mare) a fișelor „Farfuria mea” și „Farfuria lui Cem”: aceleași date, așezate pe o coloană,
cu text mare, ca imagini clare (PNG, lățime 1290 px), ușor de citit pe ecran.

Rulezi:   python3 library/build_farfuria_telefon.py mea   (sau: cem)
Rezultat: FARFURIA-MEA-TELEFON-1.png (mic dejun, prânz), -2.png (chefir, cină, desert), -3.png (crud → gătit, ziua).
"""
import importlib
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LABELS = ["Proteină (gătită) · alegi una", "Carbohidrați (gătiți) · alegi unul", "Legume", "Grăsime", "Fruct și extra"]

CSS = """
:root{--ink:#2B2431;--muted:#5C5466;--line:#EDE2EA;--soft:#FAF5F7;--k-ink:#8A3459;--k:#F8DCE6;--m:#D8F0E4;--m-ink:#1C6550}
*{box-sizing:border-box}
body{margin:0;background:#FFF9F6;color:var(--ink);font-family:"Inter",sans-serif;font-size:16px;line-height:1.42;-webkit-font-smoothing:antialiased}
.wrap{width:430px;padding:22px 18px 26px}
h1{font-family:"Inter Display","Inter",sans-serif;font-weight:800;font-size:30px;letter-spacing:-.02em;margin:0;line-height:1.05}
.sub{color:var(--muted);font-size:14.5px;margin:6px 0 14px}
.tot{display:flex;gap:8px;margin-bottom:16px}
.tot div{flex:1;background:#fff;border:1px solid var(--line);border-radius:14px;padding:9px 12px}
.tot span{display:block;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.tot b{display:block;font-family:"Inter Display","Inter",sans-serif;font-size:20px;font-weight:800;letter-spacing:-.01em;margin:2px 0}
.meal{background:#fff;border:1px solid var(--line);border-radius:18px;padding:14px 15px 6px;margin-bottom:14px}
.meal h2{font-family:"Inter Display","Inter",sans-serif;font-weight:800;font-size:23px;letter-spacing:-.01em;margin:0}
.meal .k{color:var(--muted);font-size:14px;margin:2px 0 0}
.meal .note{display:inline-block;margin-top:6px;font-size:12.5px;font-weight:700;color:var(--k-ink);background:var(--k);border-radius:99px;padding:2px 10px}
.part{border-top:1px solid var(--line);padding:9px 0 8px;margin-top:10px}
.lab{font-size:11.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--k-ink);margin-bottom:4px}
ul.o{list-style:none;margin:0;padding:0}
ul.o li{position:relative;padding-left:14px;margin:0 0 4px}
ul.o li::before{content:"";position:absolute;left:1px;top:.6em;width:6px;height:6px;border-radius:50%;background:var(--muted)}
small{color:var(--muted);font-size:13.5px}
b{font-weight:700}
.box{background:#fff;border:1px solid var(--line);border-radius:18px;padding:14px 15px;margin-bottom:14px}
.box.mint{background:var(--m);border-color:transparent}
.box .t{display:block;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--k-ink);margin-bottom:8px}
.box.mint .t{color:var(--m-ink)}
table{width:100%;border-collapse:collapse;font-size:15px}
th{text-align:left;font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);padding:4px 4px;border-bottom:1.5px solid var(--ink)}
td{padding:7px 4px;border-bottom:1px solid rgba(43,36,49,.12);vertical-align:top}
td:not(:first-child),th:not(:first-child){text-align:right}
.box ul{margin:8px 0 0;padding-left:18px}.box li{margin:4px 0}
.foot{color:var(--muted);font-size:12.5px;margin-top:4px}
"""


def meal_html(m, k, note, cells):
    parts = "".join(
        f'<div class="part"><div class="lab">{lab}</div><div>{c}</div></div>'
        for lab, c in zip(LABELS, cells) if "–" != c.replace('<span class="no">', "").replace("</span>", "")
    )
    return (f'<section class="meal"><h2>{m}</h2><p class="k">{k}</p>'
            + (f'<span class="note">{note}</span>' if note else "") + parts + "</section>")


def page(title, body):
    return (f'<!doctype html><html lang="ro"><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{CSS}</style></head><body><div class="wrap">{body}</div></body></html>')


def mea_parts():
    M = importlib.import_module("build_farfuria_mea")
    head = ('<h1>Farfuria mea</h1><p class="sub">La fiecare masă alegi câte o variantă din fiecare parte. '
            '<b>Toate gramele sunt gătite.</b></p>'
            '<div class="tot"><div><span>În fiecare zi</span><b>≈1.600–1.650</b><span>kcal · ≈130 g proteină</span></div>'
            '<div><span>Pe zi</span><b>40–55 g</b><span>grăsimi · 150–175 g carbo</span></div></div>')
    meals = [meal_html(m, k, note, cells) for m, k, note, *cells in M.ROWS]
    meals.append('<section class="meal"><h2>Desertul zilei</h2><p class="k">≈150–250 kcal</p>'
                 '<span class="note">După cină, în fiecare zi</span><div class="part"><div class="lab">Alegi unul</div><div>'
                 '<ul class="o">' + "".join(f"<li><b>{n}</b> <small>({k} kcal)</small></li>" for n, k in M.DESERT_ITEMS)
                 + f'</ul><p style="margin:8px 0 4px"><small>{M.DESERT_NOTE}</small></p></div></div></section>')
    crud = "".join(f"<tr><td>{a}</td><td>{b}</td><td><b>{c}</b></td></tr>" for a, b, c in M.CRUD)
    tail = f"""
<div class="box"><span class="t">Cât pui crud ca să iasă porția gătită</span>
<table><thead><tr><th>Aliment</th><th>Crud</th><th>Gătit</th></tr></thead><tbody>{crud}</tbody></table>
<p style="margin:8px 0 0"><small>Pastele pentru 2 zile: le cântărești uscate (120 g), apoi cântărești tot ce a ieșit fiert și împarți la 2.</small></p></div>
<div class="box mint"><span class="t">Ziua ta (zi de sală sau fără sală, la fel)</span>
<table><thead><tr><th>Masa</th><th>kcal</th><th>Proteină</th></tr></thead><tbody>
<tr><td>Mic dejun</td><td>≈400</td><td>≈28 g</td></tr><tr><td>Prânz</td><td>≈440</td><td>≈40 g</td></tr>
<tr><td>Chefirul zilei</td><td>≈240</td><td>≈32 g</td></tr><tr><td>Cină</td><td>≈380</td><td>≈30 g</td></tr>
<tr><td>Desert</td><td>≈150–250</td><td>variază</td></tr><tr><td><b>Totalul zilei</b></td><td><b>≈1.600–1.650</b></td><td><b>≈130 g</b></td></tr>
</tbody></table>
<ul><li>O singură variantă: deficitul tău e mic și același în fiecare zi. În zilele de sală bei chefirul după antrenament.</li>
<li><b>Masa liberă:</b> o dată pe săptămână, o masă (nu o zi), în locul cinei.</li></ul></div>
<div class="box"><span class="t">Ce înlocuiește ce (≈180 kcal fiecare)</span>
<p style="margin:0"><b>1 lipie mică</b> ≈ <b>2 felii pâine integrală</b> ≈ <b>115 g paste fierte</b> ≈ <b>230 g cartofi fierți</b>. Intră una în locul alteia, nu pe lângă.</p>
<ul><li>Proteină la fiecare masă (minim 25–30 g); legume la cel puțin 2 mese.</li><li>Uleiul cu lingurița (1 linguriță ≈ 40 kcal), nu din sticlă.</li></ul></div>
<p class="foot">Din programul tău de alimentație (11 nov 2026). Cifrele sunt estimări; le ajustăm după primele 2 săptămâni.</p>"""
    return {"title": "Farfuria mea", "head": head, "meals": meals, "tail_title": "Cât pui crud și ziua ta", "tail": tail}


def cem_parts():
    M = importlib.import_module("build_farfuria_cem")
    head = ('<h1>Farfuria lui Cem</h1><p class="sub">La fiecare masă alegi câte o variantă din fiecare parte. '
            '<b>Toate gramele sunt gătite</b>: cântărești după gătit, fără os, piele sau zeamă.</p>'
            '<div class="tot"><div><span>Zi de sală</span><b>≈2.400</b><span>kcal · ≈180 g proteină</span></div>'
            '<div><span>Zi de odihnă</span><b>≈2.050</b><span>kcal · ≈170 g proteină</span></div></div>'
            '<div class="box rules"><span class="t">Ca să iasă bine</span><ul style="margin-top:0">'
            '<li>Proteină la <b>fiecare</b> masă; carbohidrații mari doar <b>după sală</b>; seara <b>fără</b> carbohidrați.</li>'
            '<li>Uleiul se măsoară cu lingurița (1 linguriță ≈ 45 kcal), nu din sticlă. ±10 g nu contează; legumele și salata pot fi oricât.</li></ul></div>')
    meals = [meal_html(m, k, note, cells) for m, k, note, *cells in M.ROWS]
    crud = "".join(f"<tr><td>{a}</td><td>{b}</td><td><b>{c}</b></td></tr>" for a, b, c in M.CRUD)
    tail = f"""
<div class="box"><span class="t">Cât pui crud ca să iasă porția gătită</span>
<table><thead><tr><th>Proteina</th><th>Gătit</th><th>Crud</th></tr></thead><tbody>{crud}</tbody></table>
<p style="margin:8px 0 0"><small>Cantitățile crude sunt aproximative. Cel mai sigur: gătești tot, lași 5 min, apoi împarți porțiile gătite pe cântar.</small></p></div>
<div class="box mint"><span class="t">Zi de sală (luni–vineri) și zi de odihnă (sâmbătă, duminică)</span>
<table><thead><tr><th>Masa</th><th>Zi de sală</th><th>Zi de odihnă</th></tr></thead><tbody>
<tr><td>Mic dejun</td><td>≈500</td><td>≈500</td></tr><tr><td>Prânz</td><td>≈550</td><td>≈550</td></tr>
<tr><td>Înainte de sală</td><td>≈100 (fruct)</td><td><b>0</b> (doar cafea)</td></tr>
<tr><td>După sală / după-amiază</td><td>≈850</td><td><b>≈600</b></td></tr><tr><td>Cină</td><td>≈400</td><td>≈400</td></tr>
<tr><td><b>Totalul zilei (kcal)</b></td><td><b>≈2.400</b></td><td><b>≈2.050</b></td></tr>
</tbody></table>
<ul><li>În zilele de odihnă, după-amiază: <b>carbohidrații la jumătate</b> (125 g bulgur, 150 g cartof dulce, 175 g cartofi fierți, 100 g cartofi la cuptor) și <b>fără fruct</b>.</li>
<li>Proteina rămâne aproape la fel; mic dejunul, prânzul și cina nu se schimbă.</li></ul></div>
<p class="foot">Gramajele sunt din ghidul lui Cem (noiembrie 2026). Caloriile și proteinele sunt estimări calculate din ele. Pentru o schimbare mare de meniu, întreabă-l pe Cem.</p>"""
    return {"title": "Farfuria lui Cem", "head": head, "meals": meals, "tail_title": "Cât pui crud, zi de sală și zi de odihnă", "tail": tail}


def build_mea():
    P = mea_parts()
    m = P["meals"]
    p1 = page("Farfuria mea · dimineața și prânzul", P["head"] + "".join(m[:2]))
    p1b = page("Farfuria mea · chefirul, cina și desertul",
               '<p class="sub" style="margin-top:0"><b>Farfuria mea</b> · partea 2 din 3</p>' + "".join(m[2:]))
    p2 = page("Farfuria mea · crud și ziua",
              f'<h1>{P["tail_title"]}</h1><p class="sub"><b>Farfuria mea</b> · partea 3 din 3</p>' + P["tail"])
    return "FARFURIA-MEA-TELEFON", [p1, p1b, p2]


A4_CSS = """
@page{size:A4;margin:13mm 14mm 15mm}
body{background:#fff;font-size:12.6pt;line-height:1.4;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.wrap{width:auto;padding:0}
h1{font-size:27pt}
.sub{font-size:12pt;margin:5px 0 12px}
.tot{margin-bottom:12px}
.tot div{padding:8px 12px;border-radius:12px}
.tot b{font-size:19pt}
.tot span{font-size:8.8pt}
.meal{break-inside:avoid;padding:11px 15px 6px;margin-bottom:11px;border-radius:14px}
.meal h2{font-size:21pt}
.meal .k{font-size:11pt}
.meal .note{font-size:8.6pt;padding:1px 9px}
.part{display:grid;grid-template-columns:46mm 1fr;gap:12px;padding:7px 0 6px;margin-top:7px}
.lab{font-size:9pt;margin:4px 0 0}
ul.o li{margin:0 0 2.5px}
small{font-size:10.8pt}
.box{break-inside:avoid;border-radius:14px;padding:11px 14px;margin-bottom:11px}
.box .t{font-size:9.4pt}
table{font-size:12pt}
th{font-size:8pt}
td{padding:5px 4px}
.foot{font-size:9.6pt}
.pg{break-before:page}
.pg table{font-size:11.2pt}
.pg td{padding:3.5px 4px}
.pg .box{padding:10px 14px;margin-bottom:9px}
"""


def build_a4(parts, name):
    P = parts()
    body = (P["head"] + "".join(P["meals"])
            + f'<div class="pg"><h1 style="font-size:22pt">{P["tail_title"]}</h1>'
            + f'<p class="sub"><b>{P["title"]}</b></p>' + P["tail"] + "</div>")
    html = (f'<!doctype html><html lang="ro"><head><meta charset="utf-8"><title>{P["title"]}</title>'
            f'<style>{CSS}{A4_CSS}</style></head><body><div class="wrap">{body}</div></body></html>')
    out = os.path.join(REPO, f"{name}.pdf")
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "a4.html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(html)
        js = os.path.join(d, "pdf.js")
        foot = P["title"] + " · pagina <span class=pageNumber></span> din <span class=totalPages></span>"
        with open(js, "w") as f:
            f.write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2],{waitUntil:'load'});await p.pdf({path:process.argv[3],printBackground:true,preferCSSPageSize:true,
displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:7.5pt;color:#5C5466;width:100%;text-align:center;font-family:Inter">"""
                    + foot + """</div>'});await b.close();})();""")
        subprocess.run(["node", js, src, out], check=True)
    print(out)
    return out


def shoot(name, pages):
    with tempfile.TemporaryDirectory() as d:
        js = os.path.join(d, "shot.js")
        with open(js, "w") as f:
            f.write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:430,height:900},deviceScaleFactor:3});
for(let i=2;i<process.argv.length;i+=2){await p.goto('file://'+process.argv[i],{waitUntil:'load'});
await p.screenshot({path:process.argv[i+1],fullPage:true});}await b.close();})();""")
        args = []
        for i, html in enumerate(pages, 1):
            src = os.path.join(d, f"p{i}.html")
            with open(src, "w", encoding="utf-8") as f:
                f.write(html)
            args += [src, os.path.join(REPO, f"{name}-{i}.png")]
        subprocess.run(["node", js] + args, check=True)
        for a in args[1::2]:
            print(a)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "mea"
    if which == "mea":
        shoot(*build_mea())
    elif which == "a4":
        build_a4(mea_parts, "FARFURIA-MEA-A4")
        build_a4(cem_parts, "FARFURIA-LUI-CEM-A4")
    else:
        sys.exit("Variante: mea (telefon) sau a4 (amândouă, A4)")
