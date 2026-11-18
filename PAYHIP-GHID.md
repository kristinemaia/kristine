# Payhip, pas cu pas: cum facem pagina pentru Custom Program

> **Actualizat 16 nov (are prioritate peste ce scrie mai jos):** pe Payhip, abonamentul (Membership) nu include cursuri: conținutul lui sunt **postările** (Posts) și **Video Library**. Deci antrenamentele le punem ca **postări video** în abonamentul „Custom Program”, nu ca 4 cursuri separate. Moneda contului nu se schimbă din USD, așa că prețul e **10 USD/lună** (~9 €; Stripe plătește în EUR). Linkul paginii de vânzare: `payhip.com/b/gWIHB` (nepublicat).
>
> **Făcut pe 16 nov:** abonamentul „Custom Program” creat · Settings (comentarii da, notificări da, fără dată, fără listă automată, cu TVA) · planul „Founding member”, Subscription, 10 USD, Every month.
> **Făcut tot pe 16 nov:** pagina de vânzare (textele și pozele din `brand/payhip/membership-*.jpg`).
> **Tot pe 16 nov:** verificat în incognito (nu se vede, nu se poate cumpăra) · pagina de mulțumire · postarea „Start here” cu eticheta `Start here`.
> **Făcut pe 17 nov:** abonamentul **Payhip Videos (5 $/lună)** · cele 4 videouri vorbite urcate în Video Library, ca postări video cu eticheta `Start here` (Start here, How to use your program, Safety first, How to film your form).
> **Făcut pe 17 nov (seara):** toate cele 27 de antrenamente (videouri + textele postărilor, în `WORKOUTS-PAYHIP.md`) și jurnalul de greutăți `kristinemaia.com/log.html` (în zip-ul site-ului). **Schimbat pe 18 nov:** antrenamentele sunt doar pe site; cele 27 de postări se șterg din Payhip (vezi secțiunea 8).
> **Urmează (vechi, păstrat pentru istoric):** · antrenamentele, ca postări cu etichetele traseului (`Get Strong`, `Shape Up`, `Unstiff`, `Desk Reset`, `Home`/`Gym`, `Resets`) · testul cu cupon · Publish doar după răspunsul scris. · urcatul videourilor în Video Library · testul cu cupon · Publish doar după răspunsul scris al contabilei și al avocatului.

**Când:**
- **joi 12 nov, seara (~30 min):** pasul 1, setările contului. Nu depinde de videouri.
- **sâmbătă 14 nov (~1 oră):** pașii 2 și 3, cursurile și abonamentul. Până atunci îți dau videourile exportate și numite în ordine.
- **duminică 15 nov:** pasul 4, testul cu cuponul de 100%, pe telefon.
- **luni 16 nov:** cuponul ajunge la testeri.

_Pe laptop, cu internet bun. Payhip îl ai deja. **Nu publici produsul** (îl lași ascuns) până nu vine răspunsul scris al contabilei și al avocatului despre vânzări._

## 1. Setările contului (o dată)
- [ ] **Settings → Account**: numele magazinului „Kristine Maia”, logo/poză, moneda **EUR**
- [ ] **Settings → Payments**: conectezi **Stripe** (card) și/sau **PayPal**; verifici că banii merg în contul firmei (Revolut Business)
- [ ] **Settings → Taxes**: bifezi **EU VAT** (Payhip calculează și plătește TVA-ul UE pentru produse digitale)
- [ ] **Settings → Legal**: linkuri către Termeni și Confidențialitate (pagina Legal de pe site, după ce o verifică avocatul)

## 2. Cursurile (unul pentru fiecare traseu)
**Products → Add new → Online course.** Faci 4 cursuri: **Unstiff**, **Get Strong**, **Shape Up**, **Desk Reset**. La fiecare:
- [ ] titlul, o descriere scurtă (o scriu eu) și coperta (o fac eu)
- [ ] **secțiunea „Start here”**: cele 4 videouri vorbite
- [ ] **secțiunea „Week 1–4”**: antrenamentele A, B, C (sală și acasă) + Express de 10 min, ca lecții video
- [ ] **secțiunea „Resets”**: resetările de 5 minute
- [ ] **lecția „Your 4-week progression”**: PDF-ul cu progresia
- [ ] **lecția „Your training log”**: linkul spre jurnalul de greutăți (pagina ascunsă de pe site, `kristinemaia.com/log.html`, o fac eu) + varianta PDF de printat. Clientul notează kg și repetări la fiecare set, vede ce a ridicat data trecută și primește sugestia când să crească greutatea. Datele rămân pe telefonul lui, nu se trimit nicăieri.
- [ ] fiecare curs: **Unlisted / Hidden** (nu apare în magazin singur)

Videourile ți le dau eu exportate, numite în ordine (ex. `GS-W1-A-gym.mp4`), ca să le tragi direct.

## 3. Abonamentul
**Products → Add new → Membership.**
- [ ] numele: **Custom Program**
- [ ] prețul lunar (de stabilit: propunerea din „Antrenamentul online”, secțiunea 6) și, opțional, anual cu reducere
- [ ] **include toate cele 4 cursuri** (așa omul își poate schimba traseul fără să plătească din nou)
- [ ] perioadă de probă (opțional): 7 zile
- [ ] **emailul de bun venit** (îl scriu eu): ce curs începe, linkul spre „Start here”, cum îmi scrie

## 4. Testul (înainte de vânzare)

**Ce am testat eu, pe 18 nov (pe telefon, cu fișierele din zip):** quiz-ul, 36 de combinații de răspunsuri (toate dau un plan), 26 din cele 27 de antrenamente de la cap la coadă (videouri, cronometre, pauze, kg și repetări; al 27-lea, Full body B la sală, are aceleași exerciții, cu videourile verificate), salvarea planului după redeschidere, „Last time” la a doua oară, „My weights” și jurnalul. **Nicio eroare, niciun fișier lipsă.** Rămâne de testat de tine doar partea de Payhip (plata și contul).

**Cum se loghează clienții:** prin **Payhip**. La cumpărare, clientul primește de la Payhip un email cu accesul și intră cu **emailul lui** (cu parolă sau cu un link de logare pe email; exact cum arată verifici la testul de mai jos). Așa intră în abonament, unde sunt postările și linkul spre programul de pe site. Pe site nu e nevoie de alt login: planul și greutățile se salvează pe telefonul lor.

**Testul tău, pas cu pas (20 de minute, pe telefon):**
- [ ] **Netlify:** urci zip-ul nou (are și înălțimea și greutatea în quiz) și deschizi `kristinemaia.com/my-program.html` pe telefon: îți faci planul, apeși o zi, Start
- [ ] **Coupons → Add coupon** în Payhip: cod de **100%** (ex. `TESTER100`), pe produsul „Custom Program”, limitat la 10 folosiri
- [ ] **Cumpărarea de probă:** abonamentul e nepublicat, deci întâi verifici în setările produsului dacă poate fi „ascuns” (cumpărabil doar din link, fără să apară în magazin). Dacă singura variantă e „Publish”, decizia e a ta: îl publici 15 minute, seara, cumperi cu `TESTER100` (0 $, nicio vânzare reală) și îl treci imediat înapoi pe nepublicat
- [ ] într-o fereastră incognito, cu **alt email** decât cel de vânzătoare: deschizi pagina de vânzare, pui cuponul, plătești 0 $
- [ ] verifici emailul de la Payhip: link de acces și setarea parolei
- [ ] te loghezi ca o clientă: vezi postările „Start here” (videourile vorbite) și linkul spre program
- [ ] apeși linkul spre `my-program.html`, faci un antrenament întreg
- [ ] **Payhip → Members** (sau Customers): verifici că apare clienta de test, apoi îi **anulezi** abonamentul, ca să nu se reînnoiască
- [ ] îmi trimiți capturi la ce ți s-a părut ciudat sau greu

**Apoi:** cuponul îl dai celor 5–10 testeri (săptămâna 23–29 nov).

## 5. Legătura cu site-ul
- [ ] copiezi linkul abonamentului (payhip.com/b/...) și mi-l trimiți
- [ ] eu schimb butonul „Join your custom program (waitlist)” de pe site în butonul de cumpărare, doar după răspunsul contabilei și al avocatului

## 6. Textele paginilor (16 nov)

### Sales Page (Pages → Sales Page → Edit)
**Titlu:** `Custom Program`

**Subtitlu:**
```
Your gym or home plan, built from a 2-minute quiz. For people who sit all day.
```

**What you get**
```
• Your plan by goal: Get Strong, Shape Up, Unstiff or Desk Reset
• Workouts A, B and C for the gym or at home, plus a 10-minute Express day
• A short follow-along video for every exercise, filmed by me
• A 4-week progression, so you know when to add weight
• Your training log: write down your weights and see what you lifted last time
• 5-minute resets for your neck, back and wrists after long sessions
• New workouts and member posts, with comments open
```

**How it works**
```
1. Take the free 2-minute quiz on kristinemaia.com
2. Join, then open the post "Start here"
3. Train 2–4 times a week, log your weights, switch your goal anytime
```

**Who it's for**
```
Beginners and intermediates who sit a lot: gamers, students, desk jobs. Gym or home: every workout has a version with your bodyweight or light dumbbells.
```

**About me**
```
I'm Kristine. I studied Physical Education and Sport, I'm a certified recovery massage therapist, and as a Twitch Partner I spend long hours at a desk too. I built this program for people like us.
```

**FAQ**
```
Can I cancel anytime?
Yes, from your account. You keep access until the end of the month you paid for.

Do I need a gym?
No. Every workout has a home version.

I'm a total beginner. Is it for me?
Yes. The first weeks teach you the moves with light weights.

What is the founding price?
The first 50 members pay $10 a month and keep that price for as long as they stay.
```

**Jos, cu litere mici:**
```
General fitness guidance, not medical advice. If you are pregnant, under 18 or have a medical condition, check with your doctor before you start.
```

### Thank You Page (Pages → Thank You Page → Edit)
```
Welcome to Custom Program 🎉

Check your email for your login. Then open the post "Start here": it shows you which workouts to begin with, gym or home.

Questions? Comment on any post or reply to the welcome email. See you inside!
```

## 7. Postarea „Start here” (Posts → Create New Post, prima postare)
**Titlu:** `Start here 👋`
```
Welcome! Here's how to use Custom Program.

1. Find your track
Use the result from your quiz:
• Get Strong: build strength in the gym
• Shape Up: tone up and lose fat
• Unstiff: mobility after long hours of sitting
• Desk Reset: short daily routines, no gym needed
Not sure? Start with Get Strong if you go to the gym, Unstiff if you feel stiff.

2. Your week
2 days: A + B · 3 days: A + B + C · 4 days: A + B + C + A
Short on time? Do the 10-minute Express.

3. Every session
Warm up for 5 minutes, do the workout, then write your weights in your training log. When you hit the top of the rep range on every set, add a little weight next time (+2 kg, or +1 kg on small moves).

4. New to the gym?
Weeks 1–2 are for learning the moves with light weights. Finish every set with 2–3 reps left in the tank.

5. Watch these first
Welcome · How to use · Safety · How to film your form

Questions? Comment under any post, I read them all.

General fitness guidance, not medical advice. Stop if anything feels sharp.
```

## 8. Programul pe site (18 nov): Payhip = plata și accesul, antrenamentul = pe site
Antrenamentul se face pe **kristinemaia.com/my-program.html**: omul își alege planul o dată, apoi la fiecare antrenament vede pas cu pas videoul exercițiului, cum se face, seturile, **cronometrul** pentru pauze și pentru exercițiile pe timp, și își scrie kg și repetările (cu „Last time” și sugestia când să crească greutatea). Pagina e ascunsă (noindex), linkul îl primesc doar membrii.

**Adaugi în postarea „Start here”, sus, primul rând:**
```
👉 Your program, step by step: kristinemaia.com/my-program.html
Open it on your phone, build your plan once, then tap your day and press Start. Add it to your home screen so it opens like an app.
```
**Decizia Kristinei (18 nov): toate antrenamentele sunt doar pe site.** Payhip rămâne doar pentru **plată** și pentru **videourile de bun venit** (Start here, How to use, Safety, How to film your form). Cele 27 de postări cu antrenamente urcate pe 17 nov le **ștergi** din Payhip (Posts → postarea → Delete); videourile lor le poți șterge și din Video Library, ca să rămână doar cele 4 de bun venit.
**De știut:** linkul poate fi trimis mai departe de un membru. La început e în regulă; când ai mulți membri, trecem pe o platformă cu cont și parolă.
