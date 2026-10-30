# Site-ul Kristine Maia

> **Actualizat 17 octombrie: așa arată viața ta acum (are prioritate peste ce scrie mai jos dacă se contrazic)**
> - Apartamentul e eliberat din 16 oct; echipamentul e instalat la părinți, în București. Data la notar o ai când spune proprietarul.
> - **Liber joi și duminică.** Stream luni, marți, miercuri, vineri (sâmbăta, opțional). Sală luni, marți, miercuri sau joi, vineri, sâmbătă (cardio + greutăți).
> - **Filmezi doar în weekend, la casa de la țară** (sâmbătă 17 și 24 oct, cu internet; revii duminică seara). Montezi în timpul săptămânii, la București.
> - **TikTok zilnic din 19 oct.** Instagram Kristine Maia: reel-uri 17:00; KM Wellness Concept: reel joi 19:00 și caruselul duminica 19:00.
> - **Zboară joi 29 oct după-amiază** spre Turcia, înapoi pe 15 nov. În Turcia: 23–26 sept (4) + 4–15 oct (12) + 29 oct–15 nov (18) = **34 din 90 de zile**, marjă 56. Frizerie/coafor în Turcia în jur de 1 nov.
> - Din Turcia streamezi de la sală (cu acord scris, fără alți oameni, fără logo sau ferestre în cadru) sau de acasă, cu fundal.
> - **Branduri în rotație:** luni Dope Rope, miercuri Bewit cacao, vineri Revu Natural (cremă de masaj).
> - **Bani reali (terapie):** 4.200 lei încasați între 17 aug și 26 sept (~3.100 lei/lună). Avocat: încă 2 tranșe de 1.500 lei. Asigurarea de sănătate: urgentă, săptămâna asta.
> - Contabila a vorbit cu tine; avocatul nu mai primește documente. Nu trebuie nimic despre eSIM sau ora (ai SIM bun, ceasul se schimbă singur; în România trecem la ora de iarnă pe 25 oct).
> - Planul zilnic complet, cu locuri și ore: `PLAN-TURCIA.md` și Calendarul de printat. Bifezi în Tracker.

> **Site-ul la 30 octombrie (2):** pagina nouă `training.html` („Training” în meniu): chestionarul de 8 întrebări care dă planul (traseu, nivel, zile, minute, resetări, pauze); la „da” pe întrebarea de siguranță, doar mobilitate blândă și mesajul către medic. Butonul „Join the Training Club waitlist” deschide un email către tine; când clubul există pe Payhip, pui linkul în `LINKS`, la `CLUB`.

> **Site-ul la 30 octombrie:** în magazin (`shop.html#coaching`) și pe prima pagină apare **coaching-ul online 1:1** (49 €/lună, pe listă de așteptare, fără planuri de alimentație). Butonul „Join the coaching waitlist” deschide acum un email către tine. Când faci pe Payhip produsul gratuit „1:1 online coaching: waitlist”, pui linkul lui în `LINKS`, la `COACHING`, și rulezi din nou `build_site.py`.

> **Site-ul la 18 octombrie:** fără nimic despre terapie (pagina `terapie.html` a fost scoasă). Rămâne „Licențiată în Educație Fizică și Sport” la credențiale. Pozele tale sunt puse (`assets/kristine.jpg`, `kristine-about.jpg`, pozele din rutine), coperta e-book-ului „Stream Day Kitchen” e în magazin, PDF-ul gratuit are buton spre Payhip și previzualizare. Programul de pe Twitch e cel real: luni, marți, miercuri, vineri; joi și duminică libere. **De completat:** linkul exact al produsului gratuit din Payhip (în `LINKS`, `PAYHIP`) și linkul Amazon al e-book-ului (`AMAZON`).

Site static (HTML + CSS + puțin JavaScript), fără abonamente lunare și fără platformă. Merge pe orice găzduire gratuită.

## Paginile
| Fișier | Ce e |
|---|---|
| `index.html` | Prima pagină: contorul „How many hours did you sit today?” (sliderul, omulețul care se cocoșează, pauza de 60 s), banda roz cu PDF-ul gratuit („5:00”), apoi programul de 30 de zile și e-book-ul (ambele pe waitlist) (e-book, programul de 30 de zile), despre tine + programul de pe Twitch |
| `free.html` | 3 rutine gratuite (gât, încheieturi, șolduri) + formularul pentru PDF |
| `training.html` | Antrenamentul online: chestionarul care dă planul și ce conține Training Club (pe listă de așteptare) |
| `shop.html` | E-book-ul (€12), programul de 30 de zile (€39) și coaching-ul online 1:1 (€49/lună), toate pe waitlist; codurile de reducere; întrebări |
| `live.html` | Programul de pe Twitch, un panou „Support the stream”, regulile de chat |
| `about.html` | Povestea ta și ce ești |
| `brands.html` | Pagina pentru branduri (cifre, formate, contact) |
| `legal.html` | Disclaimer, confidențialitate, cumpărături (de verificat cu avocatul) |

Fișierele comune:
- `assets/style.css`: tot designul (culorile „powder” sunt sus, în `:root`).
- `assets/site.js`: meniul pe telefon, formularele, eticheta „Today / Next up” din program și contorul de pe prima pagină.
- `build_site.py`: generează toate paginile cu același header și footer.

## Ce trebuie completat (caută „TODO” în fișiere)
1. **Pozele:** sunt puse (`assets/kristine.jpg`, `kristine-about.jpg`). Le înlocuiești cu altele cu același nume, dacă vrei.
2. **Formularul de email (opțional, acum PDF-ul se ia din Payhip):** fă cont gratuit pe **MailerLite** (sau Kit), creează un formular cu PDF-ul „5-minute desk stretch” ca automatizare de bun venit, copiază codul de embed și pune-l în locul formularului marcat cu TODO (apare pe index, free, shop și about). Până atunci, formularul afișează doar un mesaj de mulțumire.
3. **(Scos din site pe 21 oct)** Evaluarea video, clasa în grup mic și sesiunea lunară pentru abonați nu mai apar. Le reiei doar după ce discuți cu avocatul și ai clienți din programul de 30 de zile.
4. **Codurile de reducere:** linkurile de afiliere pentru Dope Rope, Revu Natural și Bewit, în `build_site.py` (secțiunea SHOP, `#TODO-link-...`).
5. **E-book-ul și programul:** acum butoanele „Tell me when it's out” / „Join the waitlist” duc la formularul de email. Când sunt gata pe Payhip, pui linkul Payhip în locul lui `#free`.
6. **Pagina legală:** datele firmei și politica de retur, verificate de avocat.

## Contorul de pe prima pagină
- Ce „răspunzi” pentru fiecare număr de ore și cele 4 exerciții ale pauzei sunt în `assets/site.js`, la **BANDS** și **MOVES**. Poți schimba textele fără să atingi restul.
- **Link care pornește de la un anumit număr de ore:** `kristinemaia.com/#10h` (sau `#h10`) deschide pagina cu sliderul pus pe 10 ore. Bun pentru Instagram sau un panou pe Twitch: „I sat 10 hours today, try it”.
- Eticheta „Today / Next up” apare doar la Move Monday, Cook with me și Game night, niciodată la Chill Sunday (e doar în unele săptămâni).

## Cum modifici textele
- Cel mai sigur: modifici textul în `build_site.py` și rulezi `python3 build_site.py` (regenerează toate paginile). În texte poți scrie `{TWITCH}`, `{INSTA}`, `{EMAIL}`, `{BOOK}` etc.; se înlocuiesc singure cu linkurile din `LINKS`.
- Poți schimba și direct în fișierele `.html` cu **Visual Studio Code**, dar dacă rulezi din nou `build_site.py`, schimbările din `.html` se pierd.
- Header-ul și footer-ul sunt la fel pe toate paginile și se schimbă doar din `build_site.py`.

## Cum îl pui online (gratuit)
**Varianta cea mai simplă: Netlify Drop**
1. Intri pe app.netlify.com/drop.
2. Tragi tot folderul `website` în pagină. Site-ul e online în câteva secunde, pe o adresă de tip `nume.netlify.app`.
3. Îți faci cont gratuit ca să-l păstrezi și să-l actualizezi (tragi din nou folderul după fiecare modificare).

**Domeniul kristinemaia.com** (acum e la Wix și nu e conectat la nimic):
- În Netlify: Domain settings → Add a domain → `kristinemaia.com`. Netlify îți arată ce înregistrări DNS să pui.
- În Wix: Domains → kristinemaia.com → Manage DNS records, și pui înregistrările de la Netlify. (Sau muți domeniul de la Wix la alt registrar; e mai complicat, nu e necesar.)
- Durează de la câteva minute la 48 de ore până merge.

## După lansare
- Pui linkul site-ului primul în Linktree și în bio-ul de pe Twitch și Instagram.
- Banner-ul de pe Twitch care scrie www.kristinemaia.com devine din nou corect.
