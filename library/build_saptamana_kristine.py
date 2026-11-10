#!/usr/bin/env python3
"""
„Kristine's food week”: meniul Kristinei pe o săptămână obișnuită, în engleză, pentru Cem,
ca să înțeleagă de ce e fiecare produs pe lista de cumpărături comună.

Se potrivește cu PROGRAM-ALIMENTATIE.md și cu library/build_lista_comuna.py (cantitățile Kristinei).

Rulezi:   python3 library/build_saptamana_kristine.py
Rezultat: KRISTINE-FOOD-WEEK-EN.pdf (A4 orizontal)
"""
import html
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "KRISTINE-FOOD-WEEK-EN.pdf")

# (zi, antrenament, [mic dejun, prânz, gustare, cină, desert], kcal pe zi, cine cu Cem?)
WEEK = [
    ("Mon", "Legs A", ["Protein oats", "Tuna pasta", "Kefir shake", "Salmon + boiled potatoes + broccoli", "Air-fryer banana + skyr"], "≈1,660", True),
    ("Tue", "Upper A + intervals", ["Eggs & flatbread", "Tuna wrap + apple", "Kefir shake", "Shakshuka (red, with tomato)", "2 squares of 85% chocolate"], "≈1,590", False),
    ("Wed", "Easy cardio", ["Yoghurt bowl", "Shrimp pasta", "Lor + berries", "Sea bass + potatoes + veg", "2 date balls"], "≈1,580", True),
    ("Thu", "Legs B", ["Protein oats", "Tuna & potato salad", "Kefir shake", "Sea bream + potatoes + veg", "Chocolate mousse"], "≈1,670", False),
    ("Fri", "Upper B", ["Protein oats", "Tuna pasta", "Kefir shake", "Sea bream + potatoes + veg", "Baked apple + lor"], "≈1,650", True),
    ("Sat", "Long cardio", ["Oat & banana pancakes", "Salmon + potatoes", "Lor + berries", "Free meal: one plate of anything + dessert", "(in the free meal)"], "≈1,000 + free meal", False),
    ("Sun", "Rest", ["Eggs & flatbread", "Shrimp pasta", "Kefir shake", "Fish night: sea bass or sea bream + potatoes + veg", "2 date balls"], "≈1,620", True),
]

# (nume, ce conține, kcal · proteină)
MEALS = [
    ("Breakfast", [
        ("Protein oats", "40 g oats (dry) cooked in water + 1 scoop whey stirred in + 150 ml milk + 100 g frozen berries", "≈385 kcal · 31 g"),
        ("Eggs & flatbread", "Omelette of 2 eggs + 100 ml egg white with spinach and peppers · 1 wholewheat lavash · cucumber, tomato", "≈425 kcal · 31 g"),
        ("Yoghurt bowl", "200 g Greek yoghurt 2% + 30 g oats + 1 small banana + 10 g walnuts", "≈410 kcal · 27 g"),
        ("Oat & banana pancakes", "30 g oats + 1 egg + 100 ml egg white + ½ banana, blended, 2–3 small pancakes · 50 g yoghurt + berries on top", "≈350 kcal · 27 g"),
    ]),
    ("Lunch", [
        ("Tuna pasta", "140 g cooked pasta (60 g dry) + 1 can tuna in water + tomato, cucumber, red onion + 1 tsp olive oil + lemon", "≈430 kcal · 39 g"),
        ("Tuna wrap", "1 lavash + 1 can tuna + 2 tbsp garlic yoghurt + lettuce, cucumber · 1 apple", "≈455 kcal · 39 g"),
        ("Tuna & potato salad", "200 g boiled potatoes + 1 can tuna + 1 boiled egg + green beans, tomato + 1 tsp olive oil", "≈450 kcal · 42 g"),
        ("Shrimp pasta", "140 g cooked pasta + 120 g cooked shrimp + cherry tomatoes, garlic + 1 tsp olive oil + 10 g parmesan", "≈445 kcal · 41 g"),
        ("Salmon + potatoes", "95 g cooked salmon + 150 g oven potatoes + vegetables", "≈445 kcal · 32 g"),
    ]),
    ("Snack (after training)", [
        ("Kefir shake", "250 ml kefir + 1 scoop whey", "≈240 kcal · 32 g"),
        ("Lor + berries", "200 g lor + 100 g berries", "≈215 kcal · 27 g"),
    ]),
    ("Dinner", [
        ("Sea bass / sea bream plate", "≈100 g cooked fish (130 g raw), no extra oil · 150 g oven or air-fryer potatoes · 200 g vegetables", "≈370–385 kcal · 31 g"),
        ("Salmon plate", "95 g cooked salmon (120 g raw) · 150 g boiled potatoes · 200 g broccoli", "≈410 kcal · 31 g"),
        ("Shakshuka", "2 eggs + 150 ml egg white cooked in passata with pepper and onion · 1 slice wholewheat bread", "≈410 kcal · 38 g"),
    ]),
    ("Dessert (every evening, already counted)", [
        ("Air-fryer banana + skyr", "Banana cut lengthwise, cinnamon, 8 min at 180 °C · 150 g skyr", "≈200 kcal · 18 g"),
        ("Chocolate mousse", "150 g Greek yoghurt + ½ scoop chocolate whey + 1 tsp cocoa + stevia · 5 g grated 85% chocolate", "≈210 kcal · 28 g"),
        ("Baked apple + lor", "Apple halves with cinnamon, 12–15 min at 180 °C · 100 g lor with vanilla · 5 g walnuts", "≈215 kcal · 14 g"),
        ("2 date balls", "1 Medjool date + 10 g oats + ¼ scoop whey + ½ tsp cocoa, blended and rolled", "≈140 kcal · 8 g"),
        ("85% chocolate", "2 squares (10 g)", "≈60 kcal"),
    ]),
]

# (produs, unde intră, cât pe săptămână)
WHY = [
    ("Tuna in water", "Tuna pasta (Mon, Fri) · tuna wrap (Tue) · tuna & potato salad (Thu)", "4 cans"),
    ("Sea bass / sea bream", "Dinners Wed, Thu, Fri, Sun", "4 × 130 g raw"),
    ("Salmon", "Mon dinner · Sat lunch", "2 × 120 g raw"),
    ("Frozen shrimp", "Shrimp pasta (Wed, Sun)", "300 g"),
    ("Eggs · egg white", "Eggs & flatbread (Tue, Sun) · shakshuka (Tue) · pancakes (Sat) · salad (Thu)", "10 eggs · 500 ml"),
    ("Kefir · whey", "Shake on Mon, Tue, Thu, Fri, Sun · whey also in oats, mousse, date balls", "1.5 l · ≈9 scoops"),
    ("Milk", "Protein oats (Mon, Thu, Fri)", "1 l"),
    ("Greek yoghurt · skyr", "Wed bowl, Thu mousse, wrap sauce, pancake topping · Mon dessert", "500 g · 150 g"),
    ("Lor", "Snack on Wed and Sat · baked apple (Fri)", "500 g"),
    ("Parmesan", "Shrimp pasta", "50 g"),
    ("Oats", "Protein oats ×3 · yoghurt bowl · pancakes · date balls", "≈220 g"),
    ("Pasta", "Tuna pasta ×2 · shrimp pasta ×2 (cooked for 2 days at a time)", "240 g dry"),
    ("Lavash · bread", "Breakfast on Tue and Sun · Tue wrap · 1 slice with the shakshuka", "3 · 1 slice"),
    ("Potatoes", "Dinners Mon, Wed, Thu, Fri, Sun · Thu salad · Sat lunch", "≈1.35 kg raw"),
    ("Tomatoes · cherry tomatoes · passata", "Tuna pasta, salads · shrimp pasta · shakshuka (all mine, kept on my shelf)", "5 · 250 g · 1 jar"),
    ("Frozen berries · green beans", "Oats, lor snacks, pancakes · Thu salad", "500 g · 1 bag"),
    ("Bananas · apples · dates", "Bowl, pancakes, banana dessert · wrap, baked apple · date balls", "4 · 4 · 4"),
    ("Cocoa · 85% chocolate · stevia", "Mousse, date balls, chocolate squares", "small packs, last weeks"),
    ("Shared vegetables", "Cucumber, peppers, onion, courgette, broccoli, spinach, lettuce in every lunch and dinner", "see the list"),
]

KITCHEN = [
    "<b>My shelf in the fridge</b> (pink tape): dairy, tomatoes, passata, whey. Nothing from it goes into your food.",
    "<b>Your food is cooked first</b>, with clean pans. I cut tomatoes last, on my own board, and my whey shaker stays separate.",
    "<b>Pasta for 2 days:</b> I weigh it dry (120 g for 2 portions), weigh it cooked, and split it in two boxes.",
    "<b>Saturday dinner</b> is my free meal: we can eat out or order, and you order following your rules.",
]

CSS = """
@page { size: A4 landscape; margin: 11mm 12mm 13mm; }
:root { --ink:#2B2431; --muted:#5C5466; --line:#E6DCE3; --soft:#FAF5F7;
  --k:#F8DCE6; --k-ink:#8A3459; --c:#DDE9F7; --c-ink:#2A5580; --l:#E9E1F7; --l-ink:#4C3A78; --m:#D8F0E4; --m-ink:#1C6550; }
* { box-sizing:border-box; }
body { margin:0; font-family:"Inter",sans-serif; color:var(--ink); font-size:9pt; line-height:1.35; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
h1 { font-family:"Inter Display","Inter",sans-serif; font-weight:800; font-size:24pt; letter-spacing:-.02em; margin:0; line-height:1.05; }
h2 { font-family:"Inter Display","Inter",sans-serif; font-weight:800; font-size:13pt; margin:10px 0 6px; letter-spacing:-.01em; break-after:avoid; }
h3 { font-size:8pt; letter-spacing:.08em; text-transform:uppercase; color:var(--k-ink); margin:0 0 4px; }
.head { display:flex; justify-content:space-between; align-items:flex-end; gap:16px; padding-bottom:8px; border-bottom:2px solid var(--ink); margin-bottom:9px; }
.sub { color:var(--muted); margin:4px 0 0; font-size:10pt; }
.facts { display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end; max-width:55%; }
.facts span { font-weight:700; font-size:8.3pt; border-radius:99px; padding:3px 9px; }
.facts span:nth-child(1){ background:var(--k); color:var(--k-ink);} .facts span:nth-child(2){ background:var(--m); color:var(--m-ink);}
.facts span:nth-child(3){ background:var(--l); color:var(--l-ink);} .facts span:nth-child(4){ background:var(--c); color:var(--c-ink);}
table.week { width:100%; border-collapse:collapse; table-layout:fixed; }
.week th { text-align:left; font-size:7.5pt; letter-spacing:.07em; text-transform:uppercase; color:var(--muted); font-weight:700; padding:4px 6px; border-bottom:1.5px solid var(--ink); }
.week td { padding:5px 7px; border-bottom:1px solid var(--line); vertical-align:top; font-size:9.3pt; }
.week td.day { width:12%; }
.week td.day b { font-family:"Inter Display","Inter",sans-serif; font-size:12pt; display:block; line-height:1; }
.week td.day span { color:var(--muted); font-size:8pt; }
.week td.kc { width:9%; font-weight:700; text-align:right; white-space:nowrap; }
.week td.din { background:var(--soft); }
.with { display:inline-block; margin-top:3px; font-size:7.5pt; font-weight:700; background:var(--c); color:var(--c-ink); border-radius:99px; padding:1px 7px; }
.note { margin-top:6px; break-inside:avoid; display:grid; grid-template-columns:1fr 1.15fr 1fr; gap:8px; }
.box { background:var(--soft); border-radius:8px; padding:7px 9px; font-size:8.3pt; line-height:1.3; }
.box ul { margin:0; padding-left:15px; } .box li { margin:2px 0; }
.page2 { break-before:page; }
.grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px 14px; }
.cat { break-inside:avoid; }
.meal { padding:4px 0; border-bottom:1px solid var(--line); }
.meal b { display:flex; justify-content:space-between; gap:8px; font-size:9pt; }
.meal b em { font-style:normal; color:var(--k-ink); font-weight:700; white-space:nowrap; font-size:8.3pt; }
.meal p { margin:1px 0 0; color:var(--muted); font-size:8.3pt; }
table.why { width:100%; border-collapse:collapse; table-layout:fixed; }
.why th { text-align:left; font-size:7.3pt; letter-spacing:.07em; text-transform:uppercase; color:var(--muted); font-weight:700; padding:3px 5px; border-bottom:1.3px solid var(--ink); }
.why td { padding:4px 6px; border-bottom:1px solid var(--line); vertical-align:top; font-size:9.2pt; }
.why td:first-child { font-weight:700; width:22%; } .why td:last-child { width:16%; font-weight:600; }
.two { display:block; break-before:page; }
.kitchen ul { columns:2; column-gap:22px; }
.kitchen li { break-inside:avoid; }
.two h2 { margin-top:0; }
.why tr { break-inside:avoid; }
"""


def esc(s):
    return html.escape(s, quote=True)


def build():
    rows = []
    for d, tr, meals, kc, with_cem in WEEK:
        cells = []
        for i, m in enumerate(meals):
            extra = '<br><span class="with">with Cem</span>' if (i == 3 and with_cem) else ""
            cls = ' class="din"' if i == 3 else ""
            cells.append("<td%s>%s%s</td>" % (cls, esc(m), extra))
        rows.append('<tr><td class="day"><b>%s</b><span>%s</span></td>%s<td class="kc">%s</td></tr>' % (esc(d), esc(tr), "".join(cells), esc(kc)))
    week = ('<table class="week"><thead><tr><th>Day</th><th>Breakfast</th><th>Lunch</th><th>Snack (after training)</th>'
            '<th>Dinner</th><th>Dessert</th><th style="text-align:right">kcal</th></tr></thead><tbody>%s</tbody></table>' % "".join(rows))
    cats = "".join(
        '<div class="cat"><h3>%s</h3>%s</div>' % (esc(c), "".join(
            '<div class="meal"><b>%s<em>%s</em></b><p>%s</p></div>' % (esc(n), esc(k), esc(x)) for n, x, k in items))
        for c, items in MEALS)
    why = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (esc(a), esc(b), esc(c)) for a, b, c in WHY)
    kitchen = "".join("<li>%s</li>" % k for k in KITCHEN)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Kristine's food week</title><style>{CSS}</style></head><body>
<div class="head"><div><h1>Kristine's food week</h1>
<p class="sub">What I eat in a normal week, so the shopping list makes sense · November 2026</p></div>
<div class="facts"><span>Pescatarian: fish, eggs, dairy · no meat</span><span>≈1,600 kcal a day · 120–130 g protein</span><span>4 meals + a small dessert</span><span>All weights are cooked weights</span></div></div>
{week}
<div class="note">
  <div class="box"><h3>How it works</h3><ul>
    <li>Same 4 meals every day; the options rotate, so the shopping is the same every week.</li>
    <li>I cook fresh (10–20 minutes), except pasta, which I cook for 2 days.</li>
    <li>The dessert is planned and already in the calories: it keeps the evening sweet cravings away.</li>
  </ul></div>
  <div class="box"><h3>In the kitchen</h3><ul>{kitchen}</ul></div>
  <div class="box"><h3>Dinners we share</h3><ul>
    <li><b>Mon</b> salmon · <b>Wed</b> sea bass · <b>Fri</b> sea bream · <b>Sun</b> fish night.</li>
    <li>Same fish from the same order, same seasoning (lemon, garlic, thyme), cooked together in the air fryer. Your piece 180 g, mine ≈100 g cooked.</li>
    <li>I add potatoes on my plate; your dinner stays protein + veg + salad, as in your plan.</li>
  </ul></div>
</div>
<div class="page2">
<h2>What's in each meal</h2>
<div class="grid">{cats}</div>
<div class="two">
  <h2>Why my things are on the shopping list</h2>
  <table class="why"><thead><tr><th>Item</th><th>Goes into</th><th>Per week</th></tr></thead><tbody>{why}</tbody></table>
</div>
</div>
</body></html>"""


def main():
    page = build()
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "week.html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(page)
        js = os.path.join(d, "pdf.js")
        with open(js, "w") as f:
            f.write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2],{waitUntil:'load'});await p.pdf({path:process.argv[3],printBackground:true,preferCSSPageSize:true,
displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:7pt;color:#5C5466;width:100%;text-align:center;font-family:Inter">Kristine\\'s food week · page <span class=pageNumber></span> of <span class=totalPages></span></div>'});await b.close();})();""")
        subprocess.run(["node", js, src, OUT], check=True)
    print(OUT)


if __name__ == "__main__":
    sys.exit(main())
