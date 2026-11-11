#!/usr/bin/env python3
"""
Varianta de telefon a fișelor „Farfuria mea” și „Farfuria lui Cem”: aceleași date, așezate pe o coloană,
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
        f'<div class="part"><div class="lab">{lab}</div>{c}</div>'
        for lab, c in zip(LABELS, cells) if "–" != c.replace('<span class="no">', "").replace("</span>", "")
    )
    return (f'<section class="meal"><h2>{m}</h2><p class="k">{k}</p>'
            + (f'<span class="note">{note}</span>' if note else "") + parts + "</section>")


def page(title, body):
    return (f'<!doctype html><html lang="ro"><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{CSS}</style></head><body><div class="wrap">{body}</div></body></html>')


def build_mea():
    M = importlib.import_module("build_farfuria_mea")
    head = ('<h1>Farfuria mea</h1><p class="sub">La fiecare masă alegi câte o variantă din fiecare parte. '
            '<b>Toate gramele sunt gătite.</b></p>'
            '<div class="tot"><div><span>În fiecare zi</span><b>≈1.600–1.650</b><span>kcal · ≈130 g proteină</span></div>'
            '<div><span>Pe zi</span><b>40–55 g</b><span>grăsimi · 150–175 g carbo</span></div></div>')
    meals = [meal_html(m, k, note, cells) for m, k, note, *cells in M.ROWS]
    desert = ('<section class="meal"><h2>Desertul zilei</h2><p class="k">≈150–250 kcal</p>'
              '<span class="note">După cină, în fiecare zi</span><div class="part"><div class="lab">Alegi unul</div>'
              '<ul class="o">' + "".join(f"<li><b>{n}</b> <small>({k} kcal)</small></li>" for n, k in M.DESERT_ITEMS)
              + f'</ul><p style="margin:8px 0 4px"><small>{M.DESERT_NOTE}</small></p></div></section>')
    p1 = page("Farfuria mea · dimineața și prânzul", head + "".join(meals[:2]))
    p1b = page("Farfuria mea · chefirul, cina și desertul",
               '<p class="sub" style="margin-top:0"><b>Farfuria mea</b> · partea 2 din 3</p>' + "".join(meals[2:]) + desert)

    crud = "".join(f"<tr><td>{a}</td><td>{b}</td><td><b>{c}</b></td></tr>" for a, b, c in M.CRUD)
    p2 = page("Farfuria mea · crud și ziua", f"""
<h1>Cât pui crud și ziua ta</h1><p class="sub"><b>Farfuria mea</b> · partea 3 din 3</p>
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
<p class="foot">Din programul tău de alimentație (11 nov 2026). Cifrele sunt estimări; le ajustăm după primele 2 săptămâni.</p>""")
    return "FARFURIA-MEA-TELEFON", [p1, p1b, p2]


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
    if which != "mea":
        sys.exit("Deocamdată doar: mea")
    shoot(*build_mea())
