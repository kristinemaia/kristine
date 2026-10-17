# -*- coding: utf-8 -*-
"""Generează studio/PROGRAM-30-ZILE.md și tracker_items.json din program_data.py"""
import json
import os
from collections import defaultdict

from program_data import AREAS, DAYS, LIB, LIB_BY_ID, SETUPS, WEEKS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MD = os.path.join(HERE, "..", "..", "PROGRAM-30-ZILE.md")
OUT_JSON = os.path.join(HERE, "tracker_items.json")

POS_RO = {"C": "pe scaun", "S": "în picioare", "F": "pe podea"}


def ordered_moves(day):
    order = "SCF" if day["warm"] == "R3" else "CSF"
    return sorted(day["moves"], key=lambda m: order.index(LIB_BY_ID[m]["pos"]))


def closer(moves):
    return "R4f" if LIB_BY_ID[moves[-1]]["pos"] == "F" else "R4c"


# în ce zile apare fiecare clip
used_in = defaultdict(list)
for d in DAYS:
    for m in d["moves"]:
        used_in[m].append(d["n"])
    used_in[d["warm"]].append(d["n"])
    used_in[closer(ordered_moves(d))].append(d["n"])

L = []
w = L.append

w("# Programul „Desk & Gamer Mobility: 30 de zile”: lista de filmare")
w("")
w("_Pentru săptămâna de studio de la țară (decembrie) · versiunea 1_")
w("")
w("> **Pe scurt:** nu filmezi 30 de sesiuni de câte 10 minute. Filmezi **38 de clipuri de câte un minut**, **30 de introduceri** și **30 de încheieri**, apoi montezi fiecare zi din ele. În total sunt ~40 de minute de exerciții și ~25 de minute de vorbit, filmate în 4 zile scurte.")
w("")
w("---")
w("")
w("## 1. Ce schimbăm față de ce ți-am spus înainte")
w("")
w("1. **Nu mai filmezi 15 sesiuni pe zi.** Ar fi fost ~2,5 ore de mișcare continuă pe zi, plus refaceri. Cu clipuri de un minut filmezi mult mai puțin și iese același produs: 30 de zile de câte 10 minute.")
w("2. **O singură ținută pentru tot programul**, nu una la 5 zile. O zi de program e făcută din clipuri filmate în momente diferite: dacă ținuta se schimbă, se vede imediat. Ideal ai două seturi identice, ca să o speli între ziua A și ziua B.")
w("3. **Lumină artificială, perdelele trase**, nu lumina ferestrei. Lumina zilei se schimbă între dimineață și după-amiază, iar clipurile nu s-ar mai potrivi între ele. Plus: așa nu apare nicio fereastră în cadru, iar locația rămâne privată.")
w("4. **Programul ăsta e versiunea 1.** Mișcările se repetă în combinații noi (cum fac majoritatea programelor de mobilitate). Dacă se vinde bine, versiunea 2 poate aduce clipuri noi pentru cei care l-au cumpărat deja.")
w("")
w("## 2. Cum arată o zi de 10 minute")
w("")
w("| Minut | Ce e | De unde vine |")
w("|---|---|---|")
w("| 0:00–0:20 (ziua 1: 0:30) | Introducere | filmată special pentru ziua respectivă |")
w("| 0:20–1:00 (ziua 1: 0:30–1:00) | Încălzire | un clip **R1**, **R2** sau **R3**, tăiat la 40 s |")
w("| 1:00–9:00 | **8 mișcări × 1:00** | clipuri din bibliotecă, în ordinea zilei |")
w("| 9:00–9:35 | Respirații de final | **R4c** (scaun) sau **R4f** (pe spate) |")
w("| 9:35–10:00 | Încheiere | filmată special: ce ai făcut azi + ce urmează mâine |")
w("")
w("**Ordinea pe poziții:** ca să nu pierzi timp cu schimbări de poziție, fiecare zi merge scaun → în picioare → podea. Zilele care încep cu **R3** (încălzire în picioare) merg în picioare → scaun → podea. Ordinea e deja calculată mai jos, la fiecare zi.")
w("")
w("## 3. Reguli de filmare")
w("")
w("- **Ținută:** simplă, uni, confortabilă, fără logo-uri mari. Aceeași la toate clipurile, introducerile și încheierile. Păr și machiaj la fel în toate zilele.")
w("- **Lumină:** două lămpi LED (sau un softbox plus un ring light), perdelele trase. Marchezi cu bandă pe podea poziția lămpilor și a trepiedului, ca să fie la fel în ziua B.")
w("- **Fundal:** filmezi **tot programul în aceeași cameră**, în fața aceluiași perete simplu (livingul: ai podea liberă, perete și loc pentru scaun). Dacă o zi de program ar avea clipuri din camere diferite, s-ar vedea fundalul schimbându-se în mijlocul videoclipului. Biroul îl folosești doar pentru reel-uri. Fără obiecte personale, ferestre, animale sau notificări pe ecrane.")
w("- **Cameră:** telefon pe trepied, **orizontal (16:9)**. 4K la 30 fps dacă ai loc pe telefon (~25 GB în total), altfel 1080p la 30 fps. Ține corpul în centru, cu spațiu pe margini: așa poți decupa vertical (9:16) pentru reel-uri din aceleași clipuri.")
w("- **Sunet:** microfon cu clips, aceeași distanță în toate clipurile. Fără muzică în fundal (muzica se pune la montaj).")
w("- **Slate vocal:** înainte de fiecare tură spune ID-ul și tura: „N1, take two”. Apoi 2 secunde de liniște și începi. Îl tai la montaj, dar îți găsești clipul în 10 secunde.")
w("- **2–3 ture pe clip.** Dacă greșești, nu opri: reiei propoziția. Alegi cea mai bună tură la montaj.")
w("- **Durată:** fiecare clip are 1:00–1:10. La montaj se taie la 1:00 exact. Mișcările sunt lente, fără grabă.")
w("- **Vorbești live, în timp ce te miști**, calm, ca într-o conversație. Ai textul pe telefon lângă cameră. Poți spune cu cuvintele tale, dar păstrezi ideea și avertismentele („no pushing”, „nothing sharp”).")
w("")
w("## 4. Biblioteca: cele 38 de clipuri")
w("")
w("Sunt grupate **în ordinea în care le filmezi** (același setup, aceeași cameră). La fiecare clip vezi în ce zile apare, ca să știi cât contează.")
w("")
w("Legendă: **C** = pe scaun, **S** = în picioare, **F** = pe podea.")
w("")

by_setup = defaultdict(list)
for c in LIB:
    by_setup[c["setup"]].append(c)

for sid in ["A1", "A2", "B1", "B2", "B3", "B4"]:
    clips = by_setup[sid]
    w(f"### Setup {sid}: {SETUPS[sid]}")
    w(f"_{len(clips)} clipuri_")
    w("")
    for c in clips:
        area = AREAS[c["id"][0]] if c["id"][0] in AREAS else ""
        days = ", ".join(str(n) for n in sorted(set(used_in[c["id"]])))
        w(f"**{c['id']} · {c['name']}** ({c['pos']}) · {area} · apare în zilele: {days}")
        w("")
        w(f"- Pe ecran: `{c['onscreen']}`")
        w(f"- Spui: „{c['say']}”")
        w(f"- Cum filmezi: {c['note']}")
        w("")

w("## 5. Cele 30 de zile")
w("")
w("### 5.1 Privire de ansamblu")
w("")
w("| Zi | Titlu | Focus | Încălzire | Poziții (în ordine) |")
w("|---|---|---|---|---|")
for d in DAYS:
    mv = ordered_moves(d)
    seq = []
    for m in mv:
        p = LIB_BY_ID[m]["pos"]
        if not seq or seq[-1] != p:
            seq.append(p)
    pos = " → ".join(POS_RO[p] for p in seq)
    w(f"| {d['n']} | {d['title']} | {d['focus']} | {d['warm']} | {pos} |")
w("")
w("**Săptămânile:** " + " · ".join(f"**{v[0]}** ({v[2]})" for v in WEEKS.values()) + ". Zilele 7, 14, 21 și 28 sunt zile de recuperare. Ziua 30 e absolvirea: aceleași trei auto-evaluări (gât și umeri, încheieturi, șolduri, de la 0 la 10) ca în ziua 1.")
w("")
w("### 5.2 Ziua cu ziua")
w("")
w("La fiecare zi: ordinea celor 8 mișcări (1 minut fiecare), ce spui la început și ce spui la sfârșit.")
w("")
cur_week = None
for d in DAYS:
    if d["week"] != cur_week:
        cur_week = d["week"]
        wn = WEEKS[cur_week]
        w(f"#### Săptămâna {cur_week}: {wn[0]} ({wn[1]}) · {wn[2]}")
        w("")
    mv = ordered_moves(d)
    cl = closer(mv)
    intro_t = "0:30" if d["n"] == 1 else "0:20"
    warm_t = "0:30" if d["n"] == 1 else "0:40"
    w(f"**Ziua {d['n']} · {d['title']}** (focus: {d['focus']})")
    w("")
    w(f"- Introducere ({intro_t}) → încălzire **{d['warm']}** {LIB_BY_ID[d['warm']]['name']} ({warm_t})")
    lines = " → ".join(f"{m}" for m in mv)
    w(f"- Mișcările, în ordine: **{lines}**")
    w("- Pe nume: " + " · ".join(f"{LIB_BY_ID[m]['name']} ({LIB_BY_ID[m]['pos']})" for m in mv))
    w(f"- Respirații de final: **{cl}** → încheiere (0:25)")
    w(f"- **Introducere:** „{d['intro']}”")
    w(f"- **Încheiere:** „{d['outro']}”")
    w("")

w("## 6. Programul de filmare: 4 zile scurte")
w("")
w("Ia-ți **o zi liberă între A și B**, ca să nu te obosești. Dacă o zi iese mai lungă, o mutăm: nu forța.")
w("")

setup_clips = {sid: [c["id"] for c in by_setup[sid]] for sid in by_setup}

w("### Ziua A: pe scaun + pozele pentru PDF (~4 ore)")
w("")
w("| Ora | Ce faci |")
w("|---|---|")
w("| 9:30 | Lumină, cameră, microfon. Marchezi cu bandă pozițiile. Clip de test de 1 minut (sunet și lumină). |")
w(f"| 10:00 | **Setup A1** ({SETUPS['A1']}): {', '.join(setup_clips['A1'])} ({len(setup_clips['A1'])} clipuri, ~65 min) |")
w("| 11:15 | Pauză 15 min. Te uiți pe telefon la 2–3 clipuri: sunet, lumină, cadru. |")
w(f"| 11:30 | **Setup A2** ({SETUPS['A2']}): {', '.join(setup_clips['A2'])} (~20 min, muți camera) |")
w("| 12:00 | Pauză de masă |")
w("| 13:00 | **4 poze pentru PDF**, aceeași ținută și același fundal (vezi `PDF-GHID.md`): ~25 min |")
w("| 13:30 | Copie de siguranță în 2 locuri. Bifezi clipurile în tracker. |")
w("")
w("### Ziua B: în picioare + pe podea (~3,5 ore)")
w("")
w("| Ora | Ce faci |")
w("|---|---|")
w("| 9:30 | Lumină, saltea, perna pentru genunchi, scaunul lipit de perete. Aceleași marcaje ca în ziua A. |")
w(f"| 10:00 | **Setup B1** ({SETUPS['B1']}): {', '.join(setup_clips['B1'])} (~15 min) |")
w(f"| 10:15 | **Setup B2** ({SETUPS['B2']}): {', '.join(setup_clips['B2'])} (~25 min) |")
w("| 10:45 | Pauză 15 min |")
w(f"| 11:00 | **Setup B3** ({SETUPS['B3']}): {', '.join(setup_clips['B3'])} ({len(setup_clips['B3'])} clipuri, ~50 min) |")
w("| 12:00 | Pauză |")
w(f"| 12:15 | **Setup B4** ({SETUPS['B4']}): {', '.join(setup_clips['B4'])} (~25 min) |")
w("| 12:45 | Copie de siguranță. Bifezi clipurile în tracker. |")
w("")
w("### Ziua C: vocea + biroul (~3 ore)")
w("")
w("| Ora | Ce faci |")
w("|---|---|")
w("| 10:00 | Aceeași ținută și aceeași lumină. **Cadru strâns, de la piept în sus**, ca să nu conteze dacă ești în picioare sau pe scaun. |")
w("| 10:20 | **Cele 30 de introduceri**, în ordinea zilelor, câte ~20 s (ziua 1: 30 s). Spui „Day 1 intro” înainte de fiecare. ~50 min |")
w("| 11:30 | Pauză |")
w("| 11:45 | **Cele 30 de încheieri**, câte ~25 s. ~45 min |")
w("| 12:45 | Pauză |")
w("| 13:30 | **Reel-uri de la birou: 5 noi** (O1, O3, O4, O7, O8), vezi `REELURI-STUDIO.md` |")
w("| 14:30 | Copie de siguranță |")
w("")
w("### Ziua D: bucătăria + livingul (~4 ore)")
w("")
w("| Ora | Ce faci |")
w("|---|---|")
w("| 10:00 | **Bucătărie:** gătești 4–5 rețete întregi (K1–K5) și iei cadrele scurte K6–K9 între ele. Mâncarea e prânzul tău. Vezi `REELURI-STUDIO.md`. |")
w("| 13:30 | Pauză |")
w("| 14:00 | **Living:** filmezi L6 (reelul fixat în profil) și, dacă vrei, refaci 2–3 mișcări într-un format de reel (L1–L4). Restul reel-urilor le montezi din clipurile din zilele A și B. Vezi `REELURI-STUDIO.md`. |")
w("| 15:30 | Rezervă pentru refaceri și copie de siguranță |")
w("")
w("## 7. Montajul (CapCut)")
w("")
w("1. **Redenumești clipurile** după ID: `N1_chin-tucks.mp4` (doar cea mai bună tură). Le pui într-un folder `Program/Clipuri`.")
w("2. **Faci UN proiect-șablon:** slot de introducere, încălzire, 8 sloturi de câte 1:00, respirații + încheiere. Cu overlay-uri: „Day N of 30”, titlul zilei, bara de progres, numele exercițiului și doza (din „Pe ecran” de mai sus) și un „Not medical advice” mic la început și la sfârșit.")
w("3. **Pentru fiecare zi:** duplici șablonul, înlocuiești clipurile după lista zilei și pui introducerea și încheierea zilei. Țintă: 15–20 de minute pe zi după primele 3 zile.")
w("4. **Subtitrări automate în engleză** (pentru accesibilitate).")
w("5. **Muzică:** foarte slabă sau deloc. Vocea ta conduce mișcarea.")
w("6. **Export:** 1080p, 30 fps, `Day01_Neck-and-shoulders-reset.mp4`. Verifici durata (~10:00), sunetul și cronometrele.")
w("7. **Bifezi** ziua în tracker (categoria „Montaj: cele 30 de zile”). Total estimat: 8–12 ore.")
w("")
w("**Pentru reel-uri:** decupezi vertical (9:16) din aceleași clipuri. Fiecare clip de un minut este deja un reel gata: problemă → soluție.")
w("")
w("## 8. Ce spui și ce nu spui")
w("")
w("- **Spui:** „loosen up”, „ease”, „gentle”, „feels better”, „general mobility”, „make some room”.")
w("- **Nu spui:** „fix”, „cure”, „treat”, „heal”, „relieve pain”, „rehab”, „therapy”, „correct your posture”. Nu pomenești diagnostice (hernie, sciatică, tendinită) și nu promiți că dispare vreo durere.")
w("- **Cum te prezinți:** „degree in Physical Education and Sport, certified recovery massage therapist, mobility & recovery coach”. Nu „kinetoterapeut”, „physiotherapist”, „yoga teacher” sau „nutritionist”.")
w("- **„Not medical advice”:** pe ecran în fiecare zi și spus cu voce tare în ziua 1.")
w("- **Dacă cineva scrie că are durere:** „I can't give medical advice. Please check with your doctor.” și nimic mai mult.")
w("- **Ziua 30:** auto-evaluarea de la 0 la 10 e subiectivă. Nu o numești „rezultat” sau „progres măsurat”.")
w("")
w("## 9. Înainte să vinzi programul")
w("")
w("1. **Un kinetoterapeut sau medic de recuperare autorizat** se uită 30–60 de minute peste lista de exerciții și avertismente. Costă puțin și îți dă încredere și protecție.")
w("2. **Avocatul** verifică termenii de vânzare, disclaimerul și dreptul de retragere pentru conținut digital.")
w("3. **Contabila:** TVA pentru vânzări digitale în UE (OSS) și facturarea.")
w("4. **Test cu 3–5 oameni din comunitate**, gratuit, în schimbul unui feedback. Testimoniale doar reale, cu acordul lor scris.")
w("5. **Platforma de livrare** (unde văd videoclipurile cumpărătorii) se alege după filmare. Nu influențează ce filmezi acum.")
w("")

os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(L))

# ---- date pentru tracker ----
items = {
    "montaj": [{"n": d["n"], "title": d["title"]} for d in DAYS],
    "setups": {sid: setup_clips[sid] for sid in setup_clips},
}
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=1)

print("ok:", os.path.abspath(OUT_MD), len(L), "linii")
