# Verificarea conținutului (pe laptopul tău)

Programul verifică dacă paginile cu numele tău mai sunt online și ține evidența până dispar. Nu descarcă și nu afișează poze, doar verifică dacă pagina mai există.

## O singură dată
1. Instalezi **Python** de pe python.org/downloads (la instalare bifezi **„Add Python to PATH”**).
2. Pui în același folder fișierul **linkuri.txt** (ți l-am trimis în chat; un link pe rând).

## De fiecare dată (o dată pe săptămână)
- Dublu-click pe **verificare.bat**. Durează 1–3 minute, apoi se deschide **raport.html**:
  - 🔴 **Încă online**: trimitem cererea mai departe (hosting, Cloudflare, Google).
  - 🟠 **De verificat manual**: site blocat în Turcia sau protejat. Îl deschizi cu VPN sau din România.
  - 🟢 **Șterse**: cu data la care au dispărut.
- Când găsești linkuri noi (Internet Removals, Google), le adaugi la sfârșitul lui **linkuri.txt**.

## Ce caută singur
Pe lângă linkurile tale, verifică paginile de profil de pe ~20 de site-uri cunoscute pentru numele: kristinemaia, kristinemaia11, crismaia, missfoxyfire (lista e la începutul lui verificare.py, în NUME și SABLOANE).

## Ce nu poate
- Nu caută pe tot internetul ca Internet Removals (aceia au acces plătit la motoare de căutare). Găsește ce e pe site-urile din listă și pe linkurile tale.
- Din Turcia multe site-uri sunt blocate → apar „de verificat manual”. Rulat cu VPN sau din România, verifică tot.

Fișierele **linkuri.txt, stare.json și raport.html rămân doar pe laptopul tău** (nu intră în proiect).
