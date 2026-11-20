# Formatele noastre de postări (le refolosim)

_17 noiembrie 2026. Aici păstrăm formatele care ne plac, ca să le refacem oricând: tu faci pozele sau clipurile după regulile de mai jos, eu fac slide-urile, textele și descrierea. Pe Instagram, postările-model le salvezi într-o colecție: apeși semnul de salvare de sub postare → **„+ New collection”** → `Idei postări`._

## 1. „Tried and tested” (modelul Caroline O'Mahony)
**Ce e:** carusel de 6–8 slide-uri. Primul ești tu, cu titlul. Apoi câte un lucru pe slide, numerotat, cu 2–3 rânduri personale. La final, o întrebare.
**De ce merge:** pare o recomandare de la o prietenă, nu o reclamă; oamenii salvează lista; se leagă natural de reduceri (Black Friday, Crăciun, ianuarie) și de codurile tale.

**Cum arată slide-urile:**

| Slide | Poza | Textul |
|---|---|---|
| 1 | tu, poză întreagă (selfie la oglindă sau la sală) | titlul: `My tried-and-tested … I'd get again and again 🤍` |
| 2–7 | lucrul respectiv: în mână, pe blat, la sală sau în folosință | `1. Numele 🪢` + 2–3 rânduri: **de ce îl folosești tu**, cu o glumă sau un detaliu din viața ta |
| ultimul | tu din nou, sau cel mai frumos produs | `Which one would you get first? 👇` |

**Pozele (le faci tu):**
- verticale, în **lumina de dimineață**, fără bliț
- **lasă loc gol în treimea de sus**, pentru text (perete, cer, blat); nu ține produsul chiar sub text
- produsul **în folosință** e mai bun decât doar produsul (coarda în timp ce sari, crema pe picior, cacaua în cană, cu aburul)
- fără alte persoane și fără locații exacte în cadru
- îmi trimiți pozele **în ordinea slide-urilor**, cu un rând despre fiecare: ce e și de ce îl folosești

**Textul pe slide:** galben cu contur negru, centrat, Poppins SemiBold, sus. Îl pun eu cu șablonul (`brand/carousels-en/build_produse.py`), emoji-urile ies colorate.

**Descrierea:** începe cu **„ad”** sau **„Affiliate”** dacă există un cod, apoi codurile, câte unul pe rând (Dope Ropes: linkul; Revo: KRISTINE20; Bewit: KRISTINE15), apoi întrebarea și hashtag-urile. Fără „I earn a small commission”.

**Reguli:**
- doar lucruri **pe care le folosești cu adevărat**
- cel mult 2–3 coduri pe postare; restul sunt lucruri fără cod, ca să pară o listă sinceră
- colaborările plătite: „Paid partnership”, ca la orice reclamă

**Ediții viitoare:**

| Când | Titlul |
|---|---|
| 24 nov (Black Friday) | My tried-and-tested gym & gamer girl buys |
| început de decembrie | What's in my gym bag (streamer edition) |
| mijlocul lui decembrie | Gift ideas for the gamer who sits all day |
| ianuarie | My desk setup for long streams (and what fixed my back) |
| ianuarie | Kitchen things that make meal prep easy |

## 2. „Save this workout” (modelul Senada Greca)
**Ce e:** carusel de 7 slide-uri: tu în prima poză, fără text; apoi titlul și câte o parte a antrenamentului pe slide (încălzire, picioare, spate, core), fiecare cu un „de ce”; la final, îndemnul spre Level Up.
**Șablonul:** `brand/carousels-en/build_s1.py` (S1, 20 nov). Fundalul slide-urilor cu text: pozele tale, estompate, câte una diferită pe slide.
**Pozele:** 4–6 selfie-uri la oglindă din aceeași zi, în aceeași ținută.

## 3. Reel estetic de gătit
**Ce e:** cadre scurte, fără mâini în mișcare la tăieturi, tranziții Mix de 0,3 s, un singur titlu mic, sus; la final, cadrul cu toată mâncarea și o întrebare.
**Șablonul:** `studio/montaj/reel_estetic.py`; detaliile pentru CapCut sunt în „Stilul estetic în CapCut”.
**Filmezi:** 3–5 secunde din fiecare pas, telefonul pe trepied, lumina din lateral, la final 3–4 secunde cu tot preparatul gata.

## 4. Reel vorbit cu listă („Top 3 …”)
**Ce e:** vorbești în cameră și arăți fiecare lucru. Textul pe ecran: hook-ul, apoi `1 · …`, `2 · …`, `3 · …`, fiecare cu un rând mic; la final, `Which one are you? 1, 2 or 3 👇`. Subtitrări automate mici.
**Exemplu:** „3 snacks I always keep at home” (trial, 19 nov).

## 5. „Poza + Notes” (modelul Caroline O'Mahony, 18 nov)
**Ce e:** carusel de 2 slide-uri. **1:** o poză cu tine la sală, fără text (selfie la oglindă sau din profil). **2:** antrenamentul zilei, ca o notiță din aplicația **Notes** de pe iPhone: titlul („Glutes 🍑”), 5–6 exerciții numerotate, seriile × repetările și un sfat scurt în paranteză. Descrierea începe cu „Swipe for today's … workout”.
**De ce merge:** poza oprește scroll-ul, notița e salvată (oamenii o fac a doua zi). Pare scris pe loc, nu „conținut”.
**Cum îl faci:** (a) scrii lista în Notes pe telefon și faci screenshot (cel mai autentic), sau (b) îmi dai lista și o fac eu: `python3 brand/carousels-en/build_notes.py brand/carousels-en/specs/<nume>.json`. Fără date despre sală sau oraș în poză.
**Ritmul:** o dată pe săptămână, joia. Exercițiile vin din Level Up, ca oamenii să vadă cum arată o zi din el.
**Ediții:** N1 Glutes (26 nov) · N2 Back & posture (desk hunch) · N3 Home, 20 min, only dumbbells · N4 Upper body for desk people · N5 5-minute desk reset (vineri, după stream) · N6 Leg day for beginners.

## 6. „A Day On My Plate” (modelul Caroline O'Mahony, 18 nov)
**Ce e:** ce mănânci într-o zi, carusel de 6–9 slide-uri. **1:** selfie la oglindă + titlul mare, îngust, alb cu contur închis („A Day On My Plate”) și un subtitlu piersică cu regula ta. **Apoi:** câte o masă pe slide, cu un singur rând mic, cu litere mici, pe poză („oats with banana, walnuts and peanut butter + black tea”). La mijloc poate intra un produs cu cod (cacaua Bewit, Revo), scris la fel de simplu; în descriere scrii codul și pui `#affiliate` la hashtag-uri (fără „ad”, cât timp e doar afiliere; „Paid partnership” doar la colaborările plătite).
**De ce merge:** e liniștit și real, fără calorii pe ecran; oamenii îl salvează pentru idei de mese.
**Pozele:** mâncarea de sus, pe masă, în lumina de dimineață, cu ceaiul sau cana în fundal; lasă loc liber pe o parte, pentru rând.
**Șablonul:** `python3 brand/carousels-en/build_plate.py brand/carousels-en/specs/<nume>.json` (fontul Barlow Condensed).
**Ediții:** D1 (29 nov) · **D2 „How I Stay In Shape As A Streamer”** (3 dec; aceeași formă, cu sala, mâncarea și PDF-ul gratuit pe un slide, „comment STRETCH”) · „A day on my plate: stream day” · „A day on my plate: travel day” (din drumul în România) · „A day on my plate: rest day”.

## 7. „Here's how to fix it” (modelul Caroline O'Mahony, 18 nov)
**Ce e:** carusel educativ de 5–7 slide-uri, cu textul din Instagram „cu fundal” (cutiuțe rotunjite pe fiecare rând). **1:** tu (selfie la oglindă) + o cutie **albă** cu întrebarea: „For the gamers who …, here's how to fix it ➡️”. **Apoi:** câte un motiv pe slide, în cutii **negre**: titlul scurt („You're bored, not hungry.”), apoi 2–3 paragrafe scurte, cu o glumă și un exemplu din viața ta.
**De ce merge:** oamenii se recunosc în prima frază și dau swipe ca să afle „rezolvarea”; se salvează și se trimite prietenilor.
**Pozele:** mâncare, biroul, sala; textul stă sus, peste partea fără subiect. Pe un selfie, textul merge **jos**, peste corp, nu peste față.
**Reguli:** educație generală, fără sfaturi medicale și fără titluri de nutriționist; un produs cu cod poate apărea într-un singur paragraf, simplu.
**Șablonul:** `python3 brand/carousels-en/build_labels.py brand/carousels-en/specs/<nume>.json`. Sau scrii textul chiar în Instagram (Aa → fundal negru), pe pozele tale.
**Ediții:** F1 snacking on stream (30 nov) · „For the girls whose back hurts after a long stream” · „For the beginners scared of the weights section” · „For the ones who start Monday and quit Thursday” (motivație, ianuarie).

## 8. Reel de antrenament cu „harta mușchilor” (exemplul trimis de Kristine, 18 nov)
**Ce e:** 4 exerciții la rând, câte ~3 secunde, ~12 s în total (se reia singur). **Sus:** câte o siluetă pentru fiecare exercițiu, cu mușchiul lucrat în roșu, și o săgeată roșie sub exercițiul de acum. **Jos:** numele mic și seriile mari, roz cu contur alb („3 × 10”). Fără alt text pe ecran; hook-ul e pe copertă și în descriere.
**De ce merge:** se înțelege fără sunet, se salvează („save this workout”) și se uită de mai multe ori.
**Doar pentru reel-uri.** Antrenamentele clienților sunt pe site.
**Șablonul:** `python3 studio/custom-program/build_reels_harta.py` (lista `REELS`: hook-ul și cele 4 exerciții cu seriile). Siluetele: `studio/custom-program/muscle_map.py`.
**Regula (18 nov): doar clipuri la rezoluție mare** (originalele tale, 1080 × 1920, fără text pe ele). Clipurile vechi de 540 × 960 nu intră în reel-uri; scriptul le refuză.
**Gata:** RH1 Warm up like this if you sit all day (marș, step jacks, inchworm, extensia toracică) · RH2 No equipment? Do this at home (jumping jacks, skaters, flotări, hollow hold).
**Ce filmezi pentru următoarele** (câte 4–5 secunde, vertical, lumina de dimineață, tot corpul în cadru, **loc liber sus**): glute day (hip thrust, RDL, fandare înapoi, glute bridge) · spatele (face pull, fluturări inverse, ramat, lat pulldown) · core (dead bug, bird dog, side plank, plank).
