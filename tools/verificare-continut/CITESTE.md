# Verificarea conținutului (pe laptopul tău)

Programul caută pe Google, Google Imagini, Bing și Yandex tot ce apare cu numele tale, mai ales conținutul adult. Verifică dacă paginile mai sunt online și, la fiecare site, îți arată **cum îl dai jos**: formularul, adresa de email a site-ului, hostingul (sau Cloudflare) și emailul gata scris. Nu descarcă și nu afișează poze.

## Instalarea (o singură dată, ~15 minute)

### 1. Python (~5 minute)
1. Pe laptop, deschizi în browser **python.org/downloads/windows**.
2. Sus, la **„Stable Releases”**, primul rând e cea mai nouă versiune. Sub el apeși **„Download Windows installer (64-bit)”**.
3. Deschizi fișierul descărcat. Îl găsești în **Descărcări**, cu un nume care începe cu `python-3`.
4. În prima fereastră, **jos, bifezi „Add python.exe to PATH”**.
5. Apeși **„Install Now”**. Dacă Windows întreabă dacă permiți modificări, apeși **Da**.
6. Când apare „Setup was successful”, apeși **Close**.
7. Ca să verifici: apeși tasta Windows, scrii **cmd** și apeși Enter, apoi scrii `py --version` și apeși Enter. Trebuie să apară „Python 3…”.
   - Dacă scrie că nu recunoaște comanda, repornești laptopul și încerci din nou.
   - Dacă tot nu merge, deschizi din nou fișierul de instalare și alegi **Repair**.

### 2. Programul
1. Dai click dreapta pe fișierul .zip → **Extragere totală** → alegi **Documente** → **Extragere**.
2. Copiezi în folderul `verificare-continut` fișierul tău **linkuri.txt**, cu un link pe fiecare rând.

### 3. Cheia pentru căutare (SerpApi, gratuit)
1. Intri pe **serpapi.com** → **Register** și îți faci cont cu **emailul separat**. Îți poate cere să confirmi emailul și telefonul.
2. În **Dashboard** găsești **„Your Private API Key”**. O copiezi.
3. În folder deschizi **chei.txt** (se deschide în Notepad), lipești cheia după `SERPAPI=`, fără spații, apeși **Ctrl+S** și închizi.

Planul gratuit are 250 de căutări pe lună. Programul face câte ~25 o dată la 3 zile și le ia pe rând: numele simplu, numele cu „leak”, „nude”, „onlyfans”, Reddit/X/Telegram, apoi „site:” pe fiecare site găsit. Le face pe toate în ~2 săptămâni, apoi o ia de la capăt. Cu planul de 25 $ pe lună (1.000 de căutări), le face pe toate de 4 ori mai des, fără nicio altă setare.

## De fiecare dată
1. Dai dublu-click pe **verificare.bat**. Prima dată, dacă apare „Windows protected your PC”, apeși **More info** → **Run anyway**.
2. Fereastra neagră îți arată cât a verificat. Durează câteva minute.
3. Raportul se deschide singur în browser. **Lași fereastra neagră deschisă** cât lucrezi în raport și o închizi când termini.
4. Dacă vrei doar să bifezi ce ai trimis, fără o verificare nouă, folosești **raport.bat**.

## Ce vezi în raport
- **Sus**: câte site-uri mai ai de trimis și lista lor.
- **Datele tale pentru emailuri**: completezi o singură dată numele legal și emailul separat. Apar singure în emailurile gata scrise.
- **📮 De trimis**: câte un card pentru fiecare site, cu patru căsuțe:
  - **Google** și **Bing**: apeși „Copiază linkurile”, deschizi formularul (link pe card), lipești linkurile și trimiți.
  - **Site-ul**: adresa de email și pagina de DMCA, găsite singur pe site. Butoanele **Take It Down (A)**, **GDPR (B)** și **DMCA (C)** îți deschid emailul gata scris, cu linkurile puse. La un site din UE, GDPR are ★. Tu doar copiezi adresa, subiectul și textul.
  - **Hosting**: unde e găzduit site-ul. Dacă e pe Cloudflare, ai formularul lor. Altfel ai adresa de abuz a firmei și emailul gata scris. Dedesubt ai și firma domeniului, pasul următor dacă nici hostingul nu șterge.
  - După ce trimiți, apeși **„Am trimis”**. 🔴 roșu = de trimis, 🟢 verde = trimis (cu data), 🟠 portocaliu = revenire. Revenirea apare după 7 zile la site și după 14 zile la hosting, cu emailul de revenire gata scris.
- **⏳ Trimis, aștept**: site-urile la care ai trimis tot.
- **❔ Alte pagini cu numele tău**: paginile care nu par conținut adult (articole, reposturi). Dacă e ceva furat, apeși „E conținut furat” și site-ul trece la De trimis.
- **🟢 Șterse**, cu data la care au dispărut. Dacă o pagină ștearsă încă apare în Google, ai formularul ca s-o scoți.
- La fiecare link:
  - **„E șters (am verificat)”** și **„Mai e online”** sunt pentru site-urile blocate în Turcia, după ce le deschizi cu VPN.
  - **„Ascunde (nu e furat)”** scoate linkul din listă.
- **➕ Adaugă linkuri**: lipești linkurile noi direct în raport.
- Ai trimis deja lista mare la Google (21 nov)? Sus apeși „Am trimis tot la Google” și scrii data.

## Ce face singur
- Caută numele tale (kristinemaia, kristinemaia11, crismaia, missfoxyfire, „kristine maia”) pe Google, Google Imagini, Bing și Yandex, cu SafeSearch oprit. Ce găsește nou apare cu 🆕.
- Recunoaște paginile cu conținut adult după cuvintele din adresă, titlu și pagină.
- Pe fiecare site adult găsit caută cu „site:” toate paginile cu numele tale. Învață și adresa de profil a site-ului, apoi verifică acolo și celelalte nume.
- La fiecare site găsește hostingul (sau Cloudflare), firma domeniului, pagina de DMCA și adresa de email, chiar și pe cele ascunse de Cloudflare.
- Paginile tale oficiale (site-ul, Instagram, TikTok, Twitch, Payhip) nu apar în raport.
- Numele, paginile oficiale, căutările și textele emailurilor le găsești la începutul fișierului verificare.py.

## Ce nu poate
- Nu trimite cererile în locul tău, pentru că ele cer semnătura ta.
- Vede doar ce e în Google, Bing și Yandex. Grupurile private (Telegram, Discord) și forumurile cu cont nu apar. Nici pozele postate fără numele tău nu apar; pentru ele te ajută StopNCII.
- Din Turcia multe site-uri sunt blocate, așa că apar „neverificate” și fără adresă de email. Cu VPN sau din România, verifică tot.

## Unde stau linkurile
Doar în folderul ăsta, pe laptopul tău:
- **linkuri.txt**
- **chei.txt**
- **stare.json**: evidența, numele și emailul tău, cu o copie de rezervă în stare.json.bak
- **raport.html**

Niciunul nu intră în proiect. La SerpApi ajung doar căutările cu numele tale, nu și linkurile.
