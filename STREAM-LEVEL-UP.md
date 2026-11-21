# Level Up pe stream (Twitch)

_20 nov 2026. Ca Level Up să fie promovat și pe stream, nu doar pe social media. Fișierele: `brand/twitch/panels/`._

## De făcut (lista)
- [x] ✅ (21 nov) **StreamElements:** comanda `!program` (+ `!levelup`, `!plan`) și timerul care o afișează singur în chat
- [x] ✅ (21 nov, pus în overlay-ul StreamElements) **OBS:** pop-up-ul `obs-popup-level-up-1920x1080.png`, cu tastă de afișare sau prin rotație
- [ ] **Twitch, panouri:** `panel-4-level-up-320.png`, primul panou, cu linkul `https://kristinemaia.com/training.html`
- [ ] **Titlul stream-ului:** la final adaugi ` · !program`
- [ ] Recompensă cu channel points (mai jos)
- [ ] (opțional) Videoul „Starting soon” cu reel-ul L1 la mijloc. Ți-l fac când vrei.

## 1. StreamElements: comanda
**Chatbot → Chat commands → Custom commands → Add new command**
- Command name: `program`
- Aliases: `levelup`, `plan`
- User level: Everyone · Cooldown: global 30 s, user 60 s
- Response:
```
💪 Level Up is my training program for people who sit all day: a 2-min quiz builds your plan (gym or home), every exercise on video with a timer. Founding price for the first 50 members 👉 kristinemaia.com/training.html
```

## 2. StreamElements: timerul (se derulează singur)
**Chatbot → Timers → Add new timer**
- Name: `Level Up`
- Online interval: **20 min** · Offline: off · Chat lines: **5** (scrie doar dacă s-a vorbit în chat, ca să nu apară în gol)
- Message:
```
🎮 Sitting for hours too? My program Level Up builds your plan from a 2-min quiz → type !program
```
Dacă ai deja timerul pentru `!stretch`, îl pui pe acela la **20 min** și pe ăsta tot la 20, pornit cu 10 minute mai târziu. Așa apare un mesaj la 10 minute, alternativ.

## 3. OBS: pop-up-ul
**Varianta simplă:** Sources → + → **Image** → `obs-popup-level-up-1920x1080.png`. Click dreapta → **Show transition: Fade** (și Hide transition: Fade). Apoi Settings → Hotkeys → „Show/Hide Level Up”, de exemplu F9. Îl arăți 20–30 de secunde când vorbești despre program, după o pauză de stretch sau când cineva scrie `!program`.

**Varianta automată (rotație):** Sources → + → **Image Slide Show**, Slide time **30000 ms**, Transition: Fade, Loop bifat. Fișierele în ordine:
1. `obs-popup-level-up-1920x1080.png`
2. `obs-gol-1920x1080.png` (transparent), pus de **19 ori**

Rezultatul: pop-up-ul apare 30 s la fiecare ~10 minute. Dacă vrei să apară și cel de stretch, după primele 10 goale pui `obs-popup-stretch-1920x1080.png`.

Pop-up-ul stă jos în stânga. Dacă acolo ai camera sau chat-ul, îl muți din OBS, nu trebuie refăcut.

## 3b. Pop-up-ul în StreamElements (în loc de OBS)
Un widget care arată pop-up-ul **singur, la fiecare 10 minute**, și **imediat când cineva scrie `!program`** în chat. Codul e în `brand/twitch/streamelements-popup/` (4 fișiere).
1. streamelements.com → **Streaming tools → Overlays → New overlay** (1920 × 1080), sau deschizi overlay-ul tău.
2. **+ (Add widget) → Static / Custom → Custom widget**.
3. În stânga, la widget → **Open editor**. Sunt 4 tab-uri: **HTML, CSS, JS, Fields**. Ștergi ce e în fiecare și lipești conținutul fișierului cu același nume (`HTML.html`, `CSS.css`, `JS.js`, `FIELDS.json`) → **Done**.
4. În setările widget-ului apare **„Pop-up image”** → încarci `obs-popup-level-up-1920x1080.png`.
5. Întinzi widget-ul pe tot ecranul (0, 0, 1920 × 1080) → **Save**.
6. Linkul overlay-ului (butonul cu lanțul) îl pui în OBS ca **Browser source** (1920 × 1080), peste cameră.
7. Din setări schimbi: la câte minute apare, câte secunde stă și comenzile din chat.

## 4. Idei ca să-l promovezi pe stream
1. **Pauza de stretch = reclamă naturală.** La fiecare pauză (recompensa de 1 sub sau `!stretch`) spui: „this one is from my program, type !program” și arăți pop-up-ul.
2. **„Take the quiz with me”** (5 minute, o dată, la începutul stream-ului): faci quiz-ul pe ecran, cu răspunsuri inventate, și arăți planul și un exercițiu. Oamenii văd cum arată pe dinăuntru.
3. **Channel points, „Pick my workout tomorrow”** (ex. 3.000 de puncte): chat-ul alege un antrenament din Level Up, iar tu postezi a doua zi în story că l-ai făcut. Legi stream-ul de Instagram.
4. **Contorul de fondatori:** „Founding spots left: 38/50”. Îl spui la începutul stream-ului și în timer, cu numărul real din Payhip → Members.
5. **Obiectiv de sub-uri:** „At 10 subs: I do a Level Up workout live (10 min)”. Se poate pune în cardurile de obiective din overlay.
6. **Q&A „Ask me about the program”**, 10 minute pe săptămână, la final de stream. Întrebările bune le folosești și în story-uri.
7. **Starting soon** cu reel-ul L1 („It's open”) la mijloc: cine intră devreme vede programul. Ți-l fac.
8. **Panoul 4** primul sub stream și **ecranul offline** cu „Level Up · !program”. Pe ăsta din urmă ți-l fac la nevoie.

**Regula:** pe stream o spui natural, nu ca reclamă la fiecare 5 minute. Timerul + pop-up-ul se ocupă de restul.
