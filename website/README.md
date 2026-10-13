# Site-ul Kristine Maia

Site static (HTML + CSS + puțin JavaScript), fără abonamente lunare și fără platformă. Merge pe orice găzduire gratuită.

## Paginile
| Fișier | Ce e |
|---|---|
| `index.html` | Prima pagină: promisiunea, pauza de stretching de 60 s, cei 3 pași, programul de stream, despre tine, formularul de email |
| `free.html` | 3 rutine gratuite (gât, încheieturi, șolduri) + formularul pentru PDF |
| `shop.html` | Evaluarea video (€55), sesiunea pentru abonați, clasele mici (€12), e-book-ul (€12), programul de 30 de zile (waitlist), codurile de reducere |
| `live.html` | Programul de pe Twitch, avantajul pentru abonați, regulile de chat |
| `about.html` | Povestea ta și ce ești / ce nu ești |
| `brands.html` | Pagina pentru branduri (cifre, formate, contact) |
| `terapie.html` | KM Wellness Concept, în română (prețuri, unde, cum rezervi) |
| `legal.html` | Disclaimer, confidențialitate, cumpărături (de verificat cu avocatul) |

## Ce trebuie completat (caută „TODO” în fișiere)
1. **Pozele:** pune `assets/kristine.jpg` și `assets/kristine-about.jpg` și înlocuiește căsuța „Your photo here” cu `<img src="assets/kristine.jpg" alt="Kristine Maia">`.
2. **Formularul de email:** fă cont gratuit pe **MailerLite** (sau Kit), creează un formular cu PDF-ul „5-minute desk stretch” ca automatizare de bun venit, copiază codul de embed și pune-l în locul formularului marcat cu TODO (apare pe mai multe pagini).
3. **Evaluarea video:** fă un link de programare cu plată (Calendly + Stripe, sau Payhip ca „serviciu”) și pune-l în `build_site.py` la `BOOK_ASSESSMENT`.
4. **Codurile de reducere:** linkurile și codurile pentru coardă și Revu Natural, în `shop.html`.
5. **E-book-ul și programul:** când sunt gata pe Payhip, schimbi butoanele „Tell me when it's out” / „Join the waitlist” cu linkul Payhip.
6. **Pagina legală:** datele firmei și politica de retur, verificate de avocat.

## Cum modifici textele
- Cel mai simplu: deschizi fișierul `.html` în **Visual Studio Code** și schimbi textul direct.
- Header-ul și footer-ul sunt la fel pe toate paginile. Dacă vrei să schimbi ceva în ele peste tot, modifici `build_site.py` și rulezi `python3 build_site.py` (regenerează toate paginile).

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
