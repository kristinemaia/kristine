#!/usr/bin/env python3
"""
Lista de cumpărături comună, Kristine + Cem (o săptămână obișnuită), ca PDF A4.

Sursele: ghidul de bucătărie al lui Cem (fără orez, fără lactoză, fără roșii) și
PROGRAM-ALIMENTATIE.md (Kristine: pescetariană, fără carne).

Rulezi:   python3 library/build_lista_comuna.py        (română)
          python3 library/build_lista_comuna.py en     (engleză, ca s-o înțeleagă amândoi)
Rezultat: LISTA-CUMPARATURI-KRISTINE-CEM.pdf / LISTA-CUMPARATURI-KRISTINE-CEM-EN.pdf
"""
import html
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LANG = "en" if len(sys.argv) > 1 and sys.argv[1] == "en" else "ro"
OUT = os.path.join(REPO, "LISTA-CUMPARATURI-KRISTINE-CEM%s.pdf" % ("-EN" if LANG == "en" else ""))

A, C, K = "amandoi", "cem", "kristine"
WHO = {A: "Amândoi", C: "Cem", K: "Kristine"}

# (produs, în magazin (TR), cât în total, pentru cine, notă)
SECTIONS = [
    ("Pește și carne", [
        ("ton în apă (conservă)", "Ton balığı, suda", "7 conserve", A, "Cem 3 + Kristine 4. Aceeași marcă pentru amândoi: pe etichetă doar ton, apă, sare."),
        ("biban de mare sau doradă", "Levrek / çipura fileto", "Cem 3 × 220 g · Kristine 5 × 130 g", A, "Același pește pentru amândoi, gătit împreună. La pescărie, curățat, făcut file și porționat; pungile etichetate pe nume. Nemarinat, fără pané."),
        ("somon", "Somon fileto", "Cem 1 × 180 g · Kristine 2 × 120 g", A, "Același somon pentru amândoi. Simplu, nu teriyaki sau marinat."),
        ("creveți congelați, curățați", "Dondurulmuş karides (ayıklanmış)", "300 g", K, "Pentru 2 prânzuri cu paste."),
        ("piept de pui (file)", "Tavuk göğüs fileto", "2,1 kg", C, "1,4 kg duminică + 0,7 kg miercuri. Nemarinat, fără condimente."),
        ("pulpe de pui dezosate, fără piele", "Tavuk but, derisiz kemiksiz", "600 g", C, "Cu os ≈800 g."),
        ("carne tocată de vită slabă (10–15%)", "Az yağlı dana kıyma", "500 g", C, "Tocată la măcelar din pulpă sau spată. Nu «köftelik»."),
        ("carne de vită cuburi, slabă", "Az yağlı dana kuşbaşı", "800 g", C, "Pulpă, antricot sau mușchi. Nemarinată."),
    ]),
    ("Ouă", [
        ("ouă", "Yumurta", "1 cofraj de 30 + 12 ouă", A, "Cem 30 + Kristine 12."),
        ("albuș lichid pasteurizat", "Pastörize sıvı yumurta akı", "≈900 ml", A, "Cem 500 ml + Kristine 400 ml. Doar albuș, fără «süt» sau arome."),
    ]),
    ("Lactate (doar Kristine: au lactoză)", [
        ("chefir", "Kefir (sade)", "2 l", K, "În fiecare zi, în shake (250 ml). Simplu, fără arome."),
        ("lapte 1,5%", "Yarım yağlı süt", "500 ml", K, "Pentru clătite."),
        ("iaurt grecesc 2% (strecurat)", "Light süzme yoğurt", "500 g", K, "Bolul de miercuri, mousse-ul de joi, sosul de la wrap."),
        ("brânză de vaci slabă", "Lor peyniri", "250 g", K, "La micul dejun, luni și joi. Lorul e slab și are multă proteină."),
        ("skyr (sau încă iaurt strecurat)", "Skyr · süzme yoğurt", "150 g", K, "Pentru desertul cu banană la air fryer."),
        ("parmezan (bucată mică)", "Parmesan", "50 g", K, "10 g la fiecare porție de paste cu creveți."),
    ]),
    ("Pâine, cereale, paste", [
        ("lipie integrală (lavaș)", "Tam buğday lavaş", "2 pachete", A, "Câte unul. Aceeași marcă verificată: fără «yoğurt», «süt», «pirinç»."),
        ("pâine integrală", "Tam buğday ekmeği", "2 pâini", A, "Cem 1 + Kristine 1 (a ei ține ~3 săptămâni, 4 felii pe săptămână). Feliată și congelată câte 2 felii. Fără «süt tozu», «margarin», «pirinç unu»."),
        ("fulgi de ovăz", "Yulaf ezmesi", "500 g", A, "Simpli, nu instant sau cu arome. Ajung ~2 săptămâni amândurora."),
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
        ("cartofi", "Patates", "≈2,6 kg", A, "Cem 1 kg + Kristine 1,6 kg. Fără părți verzi sau încolțite."),
        ("roșii · roșii cherry", "Domates · çeri domates", "5 bucăți · 250 g", K, "Doar Kristine: le ții separat și le tai pe placa ta, după mâncarea lui Cem."),
        ("ciuperci champignon", "Kültür mantarı", "1 kg", A, "Cem 800 g + Kristine 200 g (omletele ei)."),
        ("morcovi", "Havuç", "1 kg", C, ""),
        ("praz", "Pırasa", "2 fire", C, ""),
        ("rucola", "Roka", "3 legături", C, "Se ofilește repede."),
        ("pătrunjel · mărar · ceapă verde", "Maydanoz · dereotu · yeşil soğan", "3 · 1 · 1 legături", C, ""),
        ("cartofi dulci (batat)", "Tatlı patates", "400 g", C, ""),
        ("vinete · conopidă · varză roșie", "Patlıcan · karnabahar · kırmızı lahana", "1–2 · ½ · ¼", C, "Vinetele și conopida, opțional."),
        ("avocado", "Avokado", "1 bucată", C, ""),
    ]),
    ("Fructe", [
        ("banane", "Muz", "5 bucăți", A, "Cem 3 + Kristine 2."),
        ("mere", "Elma", "5 bucăți", A, "Cem 3 + Kristine 2."),
        ("lămâi", "Limon", "14 bucăți", A, "Cem 10 + Kristine 4."),
        ("curmale Medjool", "İri hurma (Medjool)", "6 bucăți", A, "Cem 2 + Kristine 4. Fără zahăr sau sirop adăugat."),
        ("rodii", "Nar", "3 bucăți", A, "Cem 1 + Kristine 2. Kristine le iubește: în bol, la desert, pe salate."),
        ("portocale · mandarine · pere", "Portakal · mandalina · armut", "3 · 4 · 1", C, ""),
    ]),
    ("Congelate", [
        ("fructe de pădure congelate", "Dondurulmuş orman meyveleri", "500 g", K, "Opțional: în shake-ul cu chefir."),
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
        ("sos de roșii (passata)", "Domates püresi / passata", "1 borcan mic (~350 g)", K, "Doar Kristine (pastele cu ton în sos de roșii). Pe raftul ei."),
    ]),
    ("Dulce și suplimente (Kristine)", [
        ("cacao neîndulcită", "Şekersiz kakao", "1 cutie mică", K, "Mousse, mug cake, bile cu curmale."),
        ("ciocolată neagră 85%", "%85 bitter çikolata", "1 tabletă", K, "2 pătrățele pe zi, cel mult. Tocată, ține loc de fulgi pe clătite."),
        ("stevia (picături sau pudră)", "Stevia", "opțional", K, "Nu mai e în meniu. Nu xilitol: e otrăvitor pentru câini și pisici."),
        ("praf de copt · vanilie", "Kabartma tozu · vanilya özü", "1 plic · opțional", K, "Praful de copt pentru clătite; vanilia nu mai e în meniu."),
        ("proteină whey", "Whey protein", "când se termină", K, "Are lactoză: shaker-ul și lingura ei stau separat."),
        ("creatină monohidrat", "Kreatin monohidrat", "1 cutie (ține ~2 luni)", K, "3–5 g pe zi."),
    ]),
    ("Casă și curățenie", [
        ("acetonă (pentru oje)", "Aseton (oje çıkarıcı)", "1 flacon (~100–200 ml)", K, ""),
        ("Vanish, pentru pete", "Vanish leke çıkarıcı", "1 (~1 l lichid sau ~500 g pudră)", A, "Pentru rufe."),
        ("clor (înălbitor)", "Çamaşır suyu", "1 l", A, "Nu-l amesteca niciodată cu alte produse de curățenie (oțet, amoniac, Vanish): face gaze toxice. Departe de pisici."),
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
    ("La pescărie", "Peștele se ia o dată pentru amândoi, porționat: <b>Cem</b> 3 × 220 g biban sau doradă + somon 180 g · <b>Kristine</b> 5 × 130 g din același biban sau aceeași doradă + 2 × 120 g somon. Pungile, cu nume și dată."),
]


# ----------------------------------------------------------------------
# English version (same rows, same order) — so Kristine and Cem both read it
# ----------------------------------------------------------------------
WHO_EN = {A: "Both", C: "Cem", K: "Kristine"}

SECTIONS_EN = [
    ("Fish and meat", [
        ("tuna in water (can)", "Ton balığı, suda", "7 cans", A, "Cem 3 + Kristine 4. Same brand for both: label says only tuna, water, salt."),
        ("sea bass or sea bream", "Levrek / çipura fileto", "Cem 3 × 220 g · Kristine 5 × 130 g", A, "Same fish for both, cooked together. At the fish counter: cleaned, filleted and portioned; bags labelled with names. Not marinated, not breaded."),
        ("salmon", "Somon fileto", "Cem 1 × 180 g · Kristine 2 × 120 g", A, "Same salmon for both. Plain, not teriyaki or marinated."),
        ("frozen shrimp, peeled", "Dondurulmuş karides (ayıklanmış)", "300 g", K, "For 2 pasta lunches."),
        ("chicken breast (fillet)", "Tavuk göğüs fileto", "2.1 kg", C, "1.4 kg Sunday + 0.7 kg Wednesday. Not marinated, no seasoning."),
        ("boneless skinless chicken thighs", "Tavuk but, derisiz kemiksiz", "600 g", C, "Bone-in ≈800 g."),
        ("lean minced beef (10–15% fat)", "Az yağlı dana kıyma", "500 g", C, "Minced at the butcher from leg or shoulder. Not «köftelik»."),
        ("lean beef cubes", "Az yağlı dana kuşbaşı", "800 g", C, "Leg, sirloin or tenderloin. Not marinated."),
    ]),
    ("Eggs", [
        ("eggs", "Yumurta", "1 tray of 30 + 12 eggs", A, "Cem 30 + Kristine 12."),
        ("pasteurised liquid egg white", "Pastörize sıvı yumurta akı", "≈900 ml", A, "Cem 500 ml + Kristine 400 ml. Egg white only, no «süt» or flavourings."),
    ]),
    ("Dairy (Kristine only: contains lactose)", [
        ("kefir", "Kefir (sade)", "2 l", K, "Every day, in her shake (250 ml). Plain, unflavoured."),
        ("milk 1.5%", "Yarım yağlı süt", "500 ml", K, "For pancakes."),
        ("Greek yoghurt 2% (strained)", "Light süzme yoğurt", "500 g", K, "Wednesday bowl, Thursday mousse, wrap sauce."),
        ("low-fat cottage cheese", "Lor peyniri", "250 g", K, "Monday and Thursday breakfast. Lor is low fat, high protein."),
        ("skyr (or more strained yoghurt)", "Skyr · süzme yoğurt", "150 g", K, "For the air-fryer banana dessert."),
        ("parmesan (small piece)", "Parmesan", "50 g", K, "10 g on each shrimp pasta."),
    ]),
    ("Bread, grains, pasta", [
        ("wholewheat flatbread (lavash)", "Tam buğday lavaş", "2 packs", A, "One each. Same checked brand: no «yoğurt», «süt», «pirinç»."),
        ("wholewheat bread", "Tam buğday ekmeği", "2 loaves", A, "Cem 1 + Kristine 1 (hers lasts ~3 weeks, 4 slices a week). Sliced and frozen 2 slices at a time. No «süt tozu», «margarin», «pirinç unu»."),
        ("rolled oats", "Yulaf ezmesi", "500 g", A, "Plain, not instant or flavoured. Lasts ~2 weeks for both."),
        ("pasta (wholewheat if you like)", "Makarna · tam buğday makarna", "500 g", K, "Lasts ~2 weeks."),
        ("coarse bulgur for pilaf", "Pilavlık bulgur (iri)", "1 kg", C, "Lasts ~3 weeks. Bulgur only, not «pilav karışımı»."),
        ("quinoa", "Kinoa", "500 g", C, "Lasts ~4 weeks."),
        ("buckwheat", "Karabuğday", "500 g", C, "Lasts ~5 weeks."),
    ]),
    ("Vegetables", [
        ("cucumbers", "Salatalık", "≈3 kg", A, "Cem 2 kg + Kristine 1 kg."),
        ("red kapia peppers", "Kırmızı kapya biber", "1.6 kg", A, "Cem 1.3 kg + Kristine 300 g."),
        ("long green peppers (sweet)", "Sivri / çarliston biber", "≈10 pieces (300 g)", C, "Not the hot ones."),
        ("yellow onions · red onions", "Kuru soğan · mor soğan", "1.3 kg · 800 g", A, "Cem 1 kg + 600 g · Kristine 3 + 2 pieces."),
        ("garlic", "Sarımsak", "3 heads", A, "Cem 2 + Kristine 1."),
        ("courgettes", "Kabak", "1.8 kg", A, "Cem 1.2 kg + Kristine 600 g."),
        ("broccoli", "Brokoli", "1 kg", A, "Cem 600 g + Kristine 400 g."),
        ("spinach", "Ispanak", "600 g", A, "Cem 300 g + Kristine 300 g."),
        ("lettuce / iceberg", "Marul / göbek marul", "3 heads", A, "Cem 2 + Kristine 1."),
        ("potatoes", "Patates", "≈2.6 kg", A, "Cem 1 kg + Kristine 1.6 kg. No green or sprouting parts."),
        ("tomatoes · cherry tomatoes", "Domates · çeri domates", "5 pieces · 250 g", K, "Kristine only: kept apart and cut on her board, after Cem's food."),
        ("button mushrooms", "Kültür mantarı", "1 kg", A, "Cem 800 g + Kristine 200 g (her omelettes)."),
        ("carrots", "Havuç", "1 kg", C, ""),
        ("leeks", "Pırasa", "2", C, ""),
        ("rocket", "Roka", "3 bunches", C, "Wilts quickly."),
        ("parsley · dill · spring onion", "Maydanoz · dereotu · yeşil soğan", "3 · 1 · 1 bunches", C, ""),
        ("sweet potatoes", "Tatlı patates", "400 g", C, ""),
        ("aubergine · cauliflower · red cabbage", "Patlıcan · karnabahar · kırmızı lahana", "1–2 · ½ · ¼", C, "Aubergine and cauliflower are optional."),
        ("avocado", "Avokado", "1", C, ""),
    ]),
    ("Fruit", [
        ("bananas", "Muz", "5", A, "Cem 3 + Kristine 2."),
        ("apples", "Elma", "5", A, "Cem 3 + Kristine 2."),
        ("lemons", "Limon", "14", A, "Cem 10 + Kristine 4."),
        ("Medjool dates", "İri hurma (Medjool)", "6", A, "Cem 2 + Kristine 4. No added sugar or syrup."),
        ("pomegranates", "Nar", "3", A, "Cem 1 + Kristine 2. Kristine loves them: in her bowl, as dessert, on salads."),
        ("oranges · mandarins · pear", "Portakal · mandalina · armut", "3 · 4 · 1", C, ""),
    ]),
    ("Frozen", [
        ("frozen mixed berries", "Dondurulmuş orman meyveleri", "500 g", K, "Optional: in her kefir shake."),
        ("frozen green beans", "Dondurulmuş taze fasulye", "1 bag (450 g)", K, "Plain, no sauce."),
    ]),
    ("Legumes", [
        ("cooked chickpeas (jar)", "Haşlanmış nohut (kavanoz)", "1 jar (≈400 g)", C, "Chickpeas, water, salt only. Not hummus."),
    ]),
    ("Oil, nuts, olives", [
        ("extra virgin olive oil", "Sızma zeytinyağı", "1 l a month", A, "Both measure it with a teaspoon."),
        ("walnut halves", "Ceviz içi", "300 g", A, "Cem 200 g + Kristine 100 g."),
        ("almonds (optional)", "Badem", "100 g", K, ""),
        ("black olives", "Siyah zeytin", "1 jar (≈200 g)", C, "Olives, water, salt."),
        ("tahini · sesame seeds", "Tahin · susam", "1 small jar · 1 small pack", C, "Burger sauce and burger buns."),
    ]),
    ("Spices and sauces", [
        ("thyme (or oregano), cumin, black pepper, chilli flakes", "Kekik, kimyon, karabiber, pul biber", "one pack each", A, "Single spices, not «tavuk/köfte/et baharatı» mixes."),
        ("turmeric, sweet paprika, cinnamon", "Zerdeçal, tatlı toz kırmızı biber, tarçın", "one pack each", A, "Cinnamon also goes in Kristine's desserts."),
        ("dried mint, rosemary, bay leaves, dried dill", "Kuru nane, biberiye, defne, kuru dereotu", "one pack each", C, ""),
        ("pure garlic granules · pure onion powder", "Saf sarımsak tozu · saf soğan tozu", "one pack each", A, "Label says only garlic or onion."),
        ("honey", "Bal", "1 small jar", A, ""),
        ("salt", "Tuz", "1 pack", A, "No stock cubes or bouillon."),
        ("mustard · apple cider vinegar · pomegranate molasses", "Hardal · elma sirkesi · nar ekşisi (saf)", "one each", C, "No «domates», no «pirinç sirkesi»."),
        ("tomato passata", "Domates püresi / passata", "1 small jar (~350 g)", K, "Kristine only (pasta with tuna in tomato sauce). On her shelf."),
    ]),
    ("Sweet things and supplements (Kristine)", [
        ("unsweetened cocoa", "Şekersiz kakao", "1 small tin", K, "Mousse, mug cake, date balls."),
        ("85% dark chocolate", "%85 bitter çikolata", "1 bar", K, "2 squares a day at most. Chopped, it replaces chocolate chips on pancakes."),
        ("stevia (drops or powder)", "Stevia", "optional", K, "No longer in the menu. Not xylitol: it is poisonous to dogs and cats."),
        ("baking powder · vanilla", "Kabartma tozu · vanilya özü", "1 sachet · optional", K, "Baking powder for the pancakes; vanilla is no longer in the menu."),
        ("whey protein", "Whey protein", "when it runs out", K, "Contains lactose: her shaker and scoop stay separate."),
        ("creatine monohydrate", "Kreatin monohidrat", "1 tub (lasts ~2 months)", K, "3–5 g a day."),
    ]),
    ("Household and cleaning", [
        ("nail polish remover (acetone)", "Aseton (oje çıkarıcı)", "1 bottle (~100–200 ml)", K, ""),
        ("Vanish stain remover", "Vanish leke çıkarıcı", "1 (~1 l liquid or ~500 g powder)", A, "For laundry."),
        ("bleach", "Çamaşır suyu", "1 l", A, "Never mix it with other cleaners (vinegar, ammonia, Vanish): toxic fumes. Keep away from the cats."),
    ]),
    ("Other", [
        ("pickled gherkins", "Kornişon turşu", "1 jar", C, "Not «domatesli karışık turşu»."),
        ("roasted peppers in a jar (spare)", "Közlenmiş kırmızı biber (kavanoz)", "1 jar", C, "Peppers, water, salt, apple or grape vinegar."),
        ("lactose-free kaşar / mozzarella (optional)", "Laktozsuz kaşar / mozzarella", "100 g", C, "On pizza 25 g at most."),
        ("baking paper, foil, zip freezer bags", "Yağlı kağıt, folyo, streç, dondurucu poşeti", "one roll each · ≈20 bags", A, "The fish bags get names on them."),
    ]),
]

ROTATIE_EN = [
    ("Every 2 weeks", "lean minced beef 1 kg (burgers) · red lentils 250 g (soup)", C),
    ("Every 4 weeks", "wholewheat flour 1 kg · white flour 100 g · dry yeast 2 sachets · fresh basil 2 bunches (pesto)", C),
    ("When it runs out", "bulgur · quinoa · buckwheat · oats · pasta · olive oil · Kristine's protein and creatine", A),
]

REGULI_EN = [
    ("Cem doesn't eat", "<b>rice</b> (no rice flour, starch or vinegar either), <b>lactose</b> (milk, yoghurt, cheese, butter, whey) or <b>tomatoes</b> (no paste, ketchup or sauce). Words to look for on Turkish labels: «pirinç», «süt», «süt tozu», «peyniraltı suyu», «laktoz», «tereyağı», «yoğurt», «domates», «salça»."),
    ("Kristine doesn't eat", "<b>meat</b> (chicken, beef). She eats fish, eggs and dairy."),
    ("Keeping things apart", "Kristine's dairy, tomatoes, passata and protein powder live on <b>her shelf in the fridge</b>, marked with pink tape. Cem's food is cooked first, with clean pans; tomatoes are cut last, on Kristine's board."),
    ("At the fish counter", "Buy the fish once for both of you, portioned: <b>Cem</b> 3 × 220 g sea bass or sea bream + 180 g salmon · <b>Kristine</b> 5 × 130 g of the same sea bass or sea bream + 2 × 120 g salmon. Bags labelled with name and date."),
]

TEXT = {
    "ro": {"lang": "ro", "title": "Lista de cumpărături · Kristine + Cem", "h1": "Lista de cumpărături<br>Kristine + Cem",
           "sub": "O săptămână obișnuită · Istanbul · noiembrie 2026 · bifezi în magazin",
           "th": ["Produs", "În magazin (TR)", "Cât", "Pentru", "Notă"], "rot": "Nu în fiecare săptămână",
           "foot": "Făcută din ghidul de bucătărie al lui Cem și din programul de definire al Kristinei. Cantitățile „Amândoi” sunt totalul; în notă scrie cât e al fiecăruia. Când schimbați marca la ton, pâine, lipie sau condimente, citiți din nou eticheta.",
           "page": "pagina", "of": "din"},
    "en": {"lang": "en", "title": "Shopping list · Kristine + Cem", "h1": "Shopping list<br>Kristine + Cem",
           "sub": "A normal week · Istanbul · November 2026 · tick it off in the shop",
           "th": ["Item", "In the shop (TR)", "How much", "For", "Note"], "rot": "Not every week",
           "foot": "Made from Cem's kitchen guide and Kristine's cutting plan. Amounts marked “Both” are the total; the note says how much is whose. When you switch brands for tuna, bread, flatbread or spices, read the label again.",
           "page": "page", "of": "of"},
}

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
    T = TEXT[LANG]
    who = WHO_EN if LANG == "en" else WHO
    sections = SECTIONS_EN if LANG == "en" else SECTIONS
    rotatie = ROTATIE_EN if LANG == "en" else ROTATIE
    reguli = REGULI_EN if LANG == "en" else REGULI
    legend = "".join('<span class="who %s">%s</span>' % (k, who[k]) for k in (A, C, K))
    rules = "".join('<div class="rule"><b class="t">%s</b>%s</div>' % (esc(t), body) for t, body in reguli)
    head = "".join("<th>%s</th>" % esc(h) for h in T["th"])
    secs = []
    for name, rows in sections:
        trs = "".join(
            '<tr><td class="box"><span></span></td><td class="p">%s</td><td class="tr">%s</td><td class="q">%s</td>'
            '<td><span class="who %s">%s</span></td><td class="n">%s</td></tr>'
            % (esc(p), esc(tr), esc(q), w, who[w], esc(n)) for p, tr, q, w, n in rows)
        secs.append(
            '<h2>%s</h2><table><colgroup><col class="c1"><col class="c2"><col class="c3"><col class="c4"><col class="c5"><col class="c6"></colgroup>'
            '<thead><tr><th></th>%s</tr></thead><tbody>%s</tbody></table>' % (esc(name), head, trs))
    rot = "".join('<div><b>%s</b><span>%s</span><span class="who %s" style="margin-left:auto">%s</span></div>'
                  % (esc(t), esc(x), w, who[w]) for t, x, w in rotatie)
    return f"""<!doctype html><html lang="{T['lang']}"><head><meta charset="utf-8"><title>{T['title']}</title><style>{CSS}</style></head><body>
<div class="head"><div><h1>{T['h1']}</h1>
<p class="sub">{T['sub']}</p></div><div class="legend">{legend}</div></div>
<div class="rules">{rules}</div>
{''.join(secs)}
<h2>{T['rot']}</h2><div class="rot">{rot}</div>
<p class="foot">{esc(T['foot'])}</p>
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
displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:7pt;color:#5C5466;width:100%;text-align:center;font-family:Inter">Kristine + Cem · @@PAGE@@ <span class=pageNumber></span> @@OF@@ <span class=totalPages></span></div>'});await b.close();})();""")
        with open(js, encoding="utf-8") as f:
            code = f.read().replace("@@PAGE@@", TEXT[LANG]["page"]).replace("@@OF@@", TEXT[LANG]["of"])
        with open(js, "w", encoding="utf-8") as f:
            f.write(code)
        subprocess.run(["node", js, src, OUT], check=True)
    print(OUT)


if __name__ == "__main__":
    sys.exit(main())
