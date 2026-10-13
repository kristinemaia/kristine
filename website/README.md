# Site-ul Kristine Maia

Site static (HTML + CSS + puțin JavaScript), fără abonamente lunare și fără platformă. Merge pe orice găzduire gratuită.

## Paginile
| Fișier | Ce e |
|---|---|
| `index.html` | Prima pagină: contorul „How many hours did you sit today?” (sliderul, omulețul care se cocoșează, pauza de 60 s), banda roz cu PDF-ul gratuit („5:00”), evaluarea video și ce urmează (e-book, programul de 30 de zile), despre tine + programul de pe Twitch |
| `free.html` | 3 rutine gratuite (gât, încheieturi, șolduri) + formularul pentru PDF |
| `shop.html` | Evaluarea video (€55), sesiunea pentru abonați, clasele mici (€12), e-book-ul (€12), programul de 30 de zile (waitlist), codurile de reducere, întrebări |
| `live.html` | Programul de pe Twitch, avantajul pentru abonați, regulile de chat |
| `about.html` | Povestea ta, ce ești, Jimmy |
| `brands.html` | Pagina pentru branduri (cifre, formate, contact) |
| `terapie.html` | KM Wellness Concept, în română (prețuri, unde, cum rezervi) |
| `legal.html` | Disclaimer, confidențialitate, cumpărături (de verificat cu avocatul) |

Fișierele comune:
- `assets/style.css`: tot designul (culorile „powder” sunt sus, în `:root`).
- `assets/site.js`: meniul pe telefon, formularele, eticheta „Today / Next up” din program și contorul de pe prima pagină.
- `build_site.py`: generează toate paginile cu același header și footer.

## Ce trebuie completat (caută „TODO” în fișiere)
1. **Pozele:** pune `assets/kristine.jpg` și `assets/kristine-about.jpg`. Pe prima pagină și pe pagina About, literele „KM” țin locul pozei; comentariul TODO de lângă ele îți arată exact ce scrii în loc.
2. **Formularul de email:** fă cont gratuit pe **MailerLite** (sau Kit), creează un formular cu PDF-ul „5-minute desk stretch” ca automatizare de bun venit, copiază codul de embed și pune-l în locul formularului marcat cu TODO (apare pe index, free, shop și about). Până atunci, formularul afișează doar un mesaj de mulțumire.
3. **Evaluarea video:** fă un link de programare cu plată (Calendly + Stripe, sau Payhip ca „serviciu”) și pune-l în `build_site.py` la `"BOOK"`.
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
