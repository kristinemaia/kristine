# Verificarea conținutului (pe laptopul tău)

Programul caută paginile cu numele tău și verifică dacă mai sunt online. La fiecare site îți arată ce mai ai de trimis. Nu descarcă și nu afișează poze.

## O singură dată
1. Instalezi **Python** de pe python.org/downloads. La instalare bifezi **„Add Python to PATH”**.
2. Pui în același folder fișierul **linkuri.txt**, cu un link pe fiecare rând.
3. **Căutarea pe Google și Bing** (gratuită, durează 10 minute):
   - Îți faci cont pe **serpapi.com**, cu emailul separat. Planul gratuit are 250 de căutări pe lună, iar programul folosește cam 25 pe săptămână.
   - Copiezi cheia: Dashboard → **Your Private API Key**.
   - Deschizi **chei.txt** (apare în folder după prima rulare) și lipești cheia după `SERPAPI=`.
   - Fără cheie, programul merge în continuare, dar verifică doar linkurile pe care le știe deja.

## De fiecare dată
- Dai dublu-click pe **verificare.bat**. Durează 1–3 minute, apoi raportul se deschide în browser.
- **Fereastra neagră rămâne deschisă** cât lucrezi în raport. Când termini, o închizi.
- Dacă vrei doar să bifezi ce ai trimis, fără o verificare nouă, folosești **raport.bat**.

## Ce vezi în raport
- **Sus**: câte site-uri mai ai de trimis și lista lor.
- **📮 De trimis**: câte un card pentru fiecare site, cu patru căsuțe: **Google, Bing, Site-ul, Hosting**.
  - 🔴 **Roșu = de trimis.** Apeși „Copiază linkurile”, le lipești în formular și trimiți, apoi apeși **„Am trimis”**.
  - 🟢 **Verde = trimis**, cu data. Cu „✎ data” schimbi data sau ștergi bifa.
  - 🟠 **Portocaliu = revenire.** Site-ul n-a șters în 7 zile, hostingul n-a șters în 14 zile sau linkul încă apare în Google la 2 săptămâni după cerere.
  - Căsuța **Hosting** devine roșie singură după 7 zile, dacă site-ul n-a șters. Cardul îți arată dacă site-ul e pe Cloudflare (cu formularul lor) sau adresa de abuz a firmei.
- **⏳ Trimis, aștept**: site-urile la care ai trimis tot.
- **🟢 Șterse**, cu data la care au dispărut. Dacă o pagină ștearsă încă apare în Google, raportul îți dă formularul ca s-o scoți.
- La fiecare link ai trei butoane:
  - **„E șters (am verificat)”** și **„Mai e online”** sunt pentru site-urile blocate, după ce le deschizi cu VPN.
  - **„Ascunde (nu e furat)”** scoate linkul din listă, de exemplu un interviu sau o pagină a ta. Pe card ai același buton pentru tot site-ul.
- **➕ Adaugă linkuri**: lipești linkurile noi direct în raport, nu mai trebuie să deschizi linkuri.txt.
- Ai trimis deja lista mare la Google (21 nov)? Sus în raport apeși „Am trimis tot la Google” și scrii data.

## Ce face singur
- **O dată pe săptămână** caută numele tale (kristinemaia, kristinemaia11, crismaia, missfoxyfire, „kristine maia”) pe Google, Google Imagini, Bing și Yandex. Ce găsește nou apare cu 🆕.
- Din fiecare link găsit învață adresa de profil a site-ului. Apoi verifică acolo și celelalte nume ale tale.
- Află unde e găzduit fiecare site (Cloudflare sau altă firmă).
- Paginile tale oficiale (site-ul, Instagram, TikTok, Twitch, Payhip) nu apar în raport.
- Numele, paginile oficiale și cât de des caută le găsești la începutul fișierului verificare.py.

## Ce nu poate
- Nu trimite cererile în locul tău, pentru că ele cer semnătura ta.
- Din Turcia multe site-uri sunt blocate și apar ca „neverificate”. Cu VPN sau din România, verifică tot.
- Pentru fiecare nume vede doar primele ~20 de rezultate din Google. Ce e mai jos poate să-i scape, așa că alerta Google rămâne utilă.

## Unde stau linkurile
Doar în folderul ăsta, pe laptopul tău: **linkuri.txt, chei.txt, stare.json** (evidența, cu o copie de rezervă, stare.json.bak) și **raport.html**. Niciunul nu intră în proiect. La SerpApi ajung doar numele tale, ca să le caute, nu și linkurile.
