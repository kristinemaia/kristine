# -*- coding: utf-8 -*-
"""
Generatorul site-ului Kristine Maia.

Rulează din folderul website:   python3 build_site.py
Scrie din nou toate paginile (index, free, shop, live, about, brands, legal)
cu același header și footer. Stilul e în assets/style.css, iar JavaScript-ul
(meniul, formularele, contorul de pe prima pagină) în assets/site.js.

În textele de mai jos poți scrie {TWITCH}, {INSTA}, {LINKTREE}, {KM_INSTA},
{EMAIL} sau {BOOK}: se înlocuiesc automat cu linkurile din LINKS.
"""
import html as _html
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------
# Linkurile. Le schimbi aici și se schimbă pe toate paginile.
# ---------------------------------------------------------------------
LINKS = {
    "TWITCH": "https://www.twitch.tv/kristinemaia",
    "INSTA": "https://www.instagram.com/kristinemaia11/",
    "LINKTREE": "https://linktr.ee/kristinemaia",
    "EMAIL": "kristinemaia527@gmail.com",
    # TODO: pune linkul exact al produsului gratuit din Payhip, după ce îl creezi (marți 20 oct)
    "PAYHIP": "https://payhip.com/b/myR5B",
    # TODO: linkul cărții pe Amazon, după ce actualizezi oferta în KDP
    "AMAZON": "#TODO-link-amazon",
    # TODO: înlocuiește cu linkul real de programare și plată (Calendly + Stripe sau Payhip)
    "BOOK": "#TODO-link-programare-si-plata",
    # Lista de așteptare pentru coaching. Când faci produsul gratuit pe Payhip
    # („1:1 online coaching: waitlist”, 0 €), pui aici linkul lui (payhip.com/b/...).
    "COACHING": "mailto:kristinemaia527@gmail.com?subject=1%3A1%20online%20coaching%20waitlist",
    # Lista de așteptare pentru Custom Program (abonamentul cu programul personalizat). Când există pe Payhip, pui linkul aici.
    "CLUB": "mailto:kristinemaia527@gmail.com?subject=Custom%20Program%20waitlist",
}

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">'
)

# Meniul de sus (legal.html e doar în footer)
NAV = [
    ("index.html", "Home"),
    ("free.html", "Free routines"),
    ("training.html", "Training"),
    ("shop.html", "Shop"),
    ("live.html", "Live"),
    ("about.html", "About"),
    ("brands.html", "For brands"),
]


def fill(html):
    """Înlocuiește {TWITCH}, {EMAIL} etc. cu linkurile din LINKS."""
    for key, value in LINKS.items():
        html = html.replace("{" + key + "}", value)
    return html


NAV_RO = [
    ("index.html", "Acasă"),
    ("free.html", "Rutine gratuite"),
    ("shop.html", "Magazin"),
    ("live.html", "Live"),
    ("about.html", "Despre"),
    ("brands.html", "Pentru branduri"),
]


def header(cur, lang):
    ro = lang == "ro"
    nav = NAV_RO if ro else NAV
    items = "".join(
        '<li><a href="%s"%s%s>%s</a></li>' % (href, ' aria-current="page"' if href == cur else "",
                                               ' hreflang="en"' if ro else "", text)
        for href, text in nav
    )
    return (
        '<a class="skip" href="#main">' + ("Sari la conținut" if ro else "Skip to content") + '</a>\n'
        '<header class="top"><div class="wrap top-in">\n'
        '  <a class="brand" href="index.html">Kristine <span>Maia</span></a>\n'
        '  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav-links">' + ("Meniu" if ro else "Menu") + '</button>\n'
        '  <nav aria-label="' + ("Principal" if ro else "Main") + '"><ul class="nav" id="nav-links">' + items + '</ul></nav>\n'
        "</div></header>"
    )


# Textele din footer. Poți scrie liniștită și semnul % în ele.
FOOT = {
    "en": {"tag": "Mobility, recovery and good food for people who sit all day.", "explore": "Explore",
           "follow": "Follow", "all": "All links", "legal": "Legal &amp; privacy",
           "free": "Free routines", "shop": "Shop", "about": "About", "brands": "For brands",
           "note": "Not medical advice. If something hurts, check with a doctor."},
    "ro": {"tag": "Mobilitate, recuperare și mâncare bună pentru cei care stau toată ziua pe scaun.", "explore": "Explorează",
           "follow": "Urmărește", "all": "Toate linkurile", "legal": "Legal și confidențialitate",
           "free": "Rutine gratuite", "shop": "Magazin", "about": "Despre", "brands": "Pentru branduri",
           "note": "Conținutul nu înlocuiește un consult medical."},
}


def footer(lang):
    t = FOOT["ro" if lang == "ro" else "en"]
    html = """
<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div><a class="brand" href="index.html">Kristine <span>Maia</span></a><p>{tag}</p></div>
      <div><h2>{explore}</h2><ul>
        <li><a href="free.html">{free}</a></li>
        <li><a href="training.html">Training</a></li>
        <li><a href="shop.html">{shop}</a></li>
        <li><a href="live.html">Live</a></li>
        <li><a href="about.html">{about}</a></li>
        <li><a href="brands.html">{brands}</a></li>
        <li><a href="legal.html">{legal}</a></li>
      </ul></div>
      <div><h2>{follow}</h2><ul>
        <li><a href="{TWITCH}">Twitch</a></li>
        <li><a href="{INSTA}">Instagram</a></li>
        <li><a href="{LINKTREE}">{all}</a></li>
      </ul></div>
    </div>
    <div class="legal"><span>&copy; <span id="year">2026</span> Kristine Maia</span><span>{note}</span></div>
  </div>
</footer>"""
    for key, value in t.items():
        html = html.replace("{" + key + "}", value)
    return html


def page(fname, title, desc, body, lang="en", cur=None):
    html = (
        '<!doctype html>\n<html lang="%(lang)s">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        "<title>%(title)s</title>\n"
        '<meta name="description" content="%(desc)s">\n'
        '<meta property="og:title" content="%(title)s">\n'
        '<meta property="og:description" content="%(desc)s">\n'
        '<meta name="theme-color" content="#FFF9F6">\n'
        "%(fonts)s\n"
        '<link rel="stylesheet" href="assets/style.css">\n'
        "</head>\n<body>\n%(header)s\n<main id=\"main\">\n%(body)s\n</main>\n%(footer)s\n"
        '<script src="assets/site.js"></script>\n</body>\n</html>\n'
    ) % {
        "lang": lang,
        "title": _html.escape(title),
        "desc": _html.escape(desc),
        "fonts": FONTS,
        "header": header(cur or fname, lang),
        "body": body.strip("\n"),
        "footer": footer(lang),
    }
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(fill(html))


# ---------------------------------------------------------------------
# Banda roz cu PDF-ul gratuit (apare pe mai multe pagini).
# Câmpul de email are id="email" (butonul din contor pune cursorul acolo).
# ---------------------------------------------------------------------
def free_band(title="Start with five minutes.", extra="", chat="Five minutes, one printable page."):
    # chat = replica mică de deasupra titlului; pune chat="" ca să nu apară. Poți scrie și %.
    html = """
<!-- PDF-ul gratuit: 5-minute desk stretch (Payhip) -->
<section class="free" id="free" aria-labelledby="free-title">
  <div class="wrap free-grid">
    <p class="five" aria-hidden="true">5:00</p>
    <div class="free-copy">
      {chat_line}
      <h2 id="free-title">{title}</h2>
      <p>The free 5-minute desk stretch. All four spots on one printable page: neck, shoulders, wrists and hips, from your chair.</p>
      <div class="free-act">
        <img class="pdf-prev" src="assets/pdf-preview.jpg" alt="Preview of the free 5-minute desk stretch PDF" width="200" height="283" loading="lazy">
        <div>
          <a class="btn" href="{PAYHIP}">Get the free PDF</a>
          <p class="fine">Free, instant download. No spam.{extra}</p>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    chat_line = '<p class="chat-line"><span class="who">kristinemaia</span> ' + chat + '</p>' if chat else ''
    return (html.replace("{chat_line}", chat_line).replace("{title}", title)
                .replace("{extra}", (" " + extra) if extra else ""))


LIST_PERKS = "Download it and you'll also hear first about the updated e-book, the 30-day program at the early price."

# Programul de pe Twitch. data-day: 1 = luni, 3 = miercuri, 5 = vineri (pentru „Today / Next up”).
# Duminica nu are data-day, pentru că e doar în unele săptămâni.
WEEK_HOME = """
      <p class="streams-intro">My streams change from day to day. You might find a workout, a mobility session, yoga, cooking, gaming, just chatting, or simply good vibes.</p>
      <ul class="topics" aria-label="What happens on stream">
        <li>Workouts</li><li>Mobility</li><li>Yoga</li><li>Cooking</li><li>Gaming</li><li>Just chatting</li><li>Good vibes</li>
      </ul>"""


# =====================================================================
# 1. PRIMA PAGINĂ (index.html)
#    Contorul: textele și exercițiile sunt în assets/site.js (BANDS, MOVES).
#    Link care pornește sliderul de la 10 ore: index.html#10h
# =====================================================================
home = """
<!-- 1. Contorul: câte ore ai stat azi? -->
<section class="hero" aria-labelledby="q-title">
  <div class="wrap hero-grid">
    <div class="q">
      <p class="kicker">A 60-second check-in</p>
      <h1 id="q-title">How many hours did you <em>sit</em> today?</h1>
      <p class="hint">Drag the slider. I'll be honest back.</p>
    </div>

    <div class="meter" id="meter" data-mode="count">
      <div class="stage">
        <svg class="fig" viewBox="0 0 240 190" aria-hidden="true" focusable="false" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <ellipse cx="124" cy="183" rx="114" ry="6" fill="#C6E6D6"/>
          <path d="M150 104H234M224 104V180M213 104V94" stroke="#7E95B6" stroke-width="5"/>
          <rect x="207" y="58" width="12" height="38" rx="3" fill="#fff" stroke="#7E95B6" stroke-width="4"/>
          <rect x="160" y="97" width="32" height="5" rx="2.5" fill="#7E95B6"/>
          <path d="M34 56L46 126M42 131H104M72 131V166M50 172H94" stroke="#8B7DB0" stroke-width="6"/>
          <circle cx="52" cy="177" r="4" fill="#8B7DB0"/><circle cx="92" cy="177" r="4" fill="#8B7DB0"/>
          <path id="f-legs" d="M62 124L124 126L124 174L140 174" stroke="#2B2431" stroke-width="9"/>
          <path id="f-spine" d="M62 124Q56 94 62 62" stroke="#2B2431" stroke-width="10"/>
          <path id="f-arm" d="M62 62L86 100L168 98" stroke="#2B2431" stroke-width="8"/>
          <path id="f-neck" d="M62 62L68 36" stroke="#2B2431" stroke-width="8"/>
          <g id="f-head" transform="translate(68 36)">
            <circle r="16" fill="#2B2431"/>
            <path d="M-14 -3Q-1 -36 15 -6" stroke="#A23D66" stroke-width="4.5"/>
            <ellipse cx="-4" cy="2" rx="6" ry="8.5" fill="#E59BB9" stroke="#A23D66" stroke-width="3"/>
          </g>
        </svg>
        <div class="readout">
          <div class="m-count"><p class="big"><span id="h-out">8</span><small>h</small></p><p class="sub" id="m-out">480 min in a chair</p></div>
          <div class="m-break"><p class="big" id="clock">0:15</p><p class="sub" id="step">Move 1 of 4</p></div>
          <div class="m-done"><p class="big">+1<small>min</small></p><p class="sub">back to you</p></div>
        </div>
      </div>

      <div class="m-count">
        <label class="sr" for="hrs">Hours sitting today</label>
        <input type="range" id="hrs" class="nudge" min="0" max="16" step="1" value="8" aria-valuetext="8 hours">
        <div class="ticks" aria-hidden="true"><span>0</span><span>4</span><span>8</span><span>12</span><span>16+</span></div>
      </div>
      <p class="chat m-count"><span class="who">kristinemaia</span><span class="say" id="verdict">A full workday. Your hips have been folded at 90° for 480 minutes. Let's open them.</span></p>
      <p class="plan m-count" id="plan">Your minute: <b>Seated figure-4 · Chin tucks · Shoulder blade squeeze · Wrist stretch</b></p>
      <button class="btn m-count" id="go" type="button">Give 1 minute back</button>

      <div class="segs m-break" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
      <p class="move m-break" id="move">Seated figure-4</p>
      <p class="cue m-break" id="cue">Ankle on the opposite knee, sit tall, hinge forward slightly from the hips. Switch sides halfway.</p>
      <div class="row m-break"><button class="btn" id="pause" type="button">Pause</button><button class="link-btn" id="stop" type="button">Stop</button></div>

      <p class="chat m-done" id="done-chat" tabindex="-1"><span class="who">kristinemaia</span><span class="say" id="done-line">Notice anything? That's 1 of 480 minutes back.</span></p>
      <p class="m-done">Tomorrow, try the 5-minute version. It's free.</p>
      <a class="btn m-done" href="#free" id="to-free">Get the free desk stretch</a>
      <p class="next m-done"><a href="shop.html#program">Coming soon: a 30-day plan. Join the waitlist</a></p>
      <p class="spots m-done"><span>Which spot complained most?</span><a href="free.html#neck">Neck</a><a href="free.html#wrists">Wrists</a><a href="free.html#hips">Hips</a></p>
      <p class="m-done"><button class="link-btn" id="again" type="button">Do it again</button></p>

      <p class="note">Gentle range only, stop if anything hurts. Not medical advice.</p>
      <p class="sr" id="say" aria-live="polite"></p>
    </div>

    <div class="intro">
      <p>I'm <strong>Kristine</strong>. I have a degree in Physical Education and Sport and coach mobility. When I game on Twitch, we stop for a 2-minute stretch every hour. Your turn.</p>
      <p class="small"><a href="#free">Or skip to the free 5-minute desk stretch</a></p>
    </div>
  </div>
</section>
""" + free_band("Now make it <em>five</em> minutes.", LIST_PERKS, chat="Want the longer one on paper?") + """
<!-- 3. Când un minut nu e destul: ce urmează (waitlist) -->
<section class="more" aria-labelledby="more-title">
  <div class="wrap">
    <div class="block-head">
      <p class="kicker">When a minute isn't enough</p>
      <h2 id="more-title">Want to go further?</h2>
    </div>
    <div class="more-grid">
      <article class="offer" id="program-home">
        <h3>Desk &amp; Gamer Mobility: 30 days</h3>
        <p class="price">€39<small>€29 for the email list</small></p>
        <p>10 minutes a day, follow-along videos for neck, upper back, wrists, hips and lower back.</p>
        <p class="fine">General exercise and education. Not medical advice.</p>
        <a class="btn" href="#free">Join the waitlist</a>
      </article>
      <div class="soon">
        <p class="kicker">Coming soon</p>
        <p>The Stream Day Kitchen e-book (new edition): healthy, filling meals and hand-portion basics for people who sit all day. People on the email list hear first and get the early price.</p>
        <p class="mt-s">Also coming: <strong>1:1 online coaching</strong> for a small group. A training plan built around your week, with feedback on your form.</p>
        <p class="all"><a href="#free">Join the list</a> · <a href="shop.html#coaching">Coaching waitlist</a> · <a href="shop.html">See the shop</a></p>
      </div>
    </div>
  </div>
</section>

<!-- 4. Cine sunt + săptămâna pe Twitch -->
<section class="me" aria-labelledby="me-title">
  <div class="wrap me-grid">
    <div class="bio">
      <div class="hi">
        <span class="mono"><img src="assets/kristine.jpg" alt="Kristine Maia smiling" width="72" height="72"></span>
        <p class="kicker">Who's counting</p>
      </div>
      <h2 id="me-title">Hi, I'm Kristine. I sit for a living too.</h2>
      <p>Twitch Partner, 72K followers, 5 years live. My chat kept telling me about stiff necks, sore wrists and whatever food was closest. So we work on it together, a few minutes at a time.</p>
      <ul class="creds">
        <li>Degree in Physical Education and Sport</li>
        <li>Mobility &amp; recovery coach</li>
      </ul>
      <p><a class="tl" href="about.html">More about me</a></p>
    </div>

    <div class="week">
      <p class="kicker">Live on Twitch</p>
      <h3>What's on stream.</h3>
""" + WEEK_HOME + """
      <p class="small muted">Streams are announced on my <a href="{TWITCH}/schedule">Twitch schedule</a>.</p>
      <a class="btn" href="{TWITCH}">Follow on Twitch</a>
    </div>
  </div>
</section>
"""
page(
    "index.html",
    "Kristine Maia · Mobility & Recovery",
    "How many hours did you sit today? Drag the slider, give one minute back with a 60-second stretch break, then get the free 5-minute desk stretch.",
    home,
)


# =====================================================================
# 2. RUTINELE GRATUITE (free.html) · exercițiile și dozele rămân la fel
# =====================================================================
free = """
<section class="wrap page-head">
  <p class="kicker">Free routines · no sign-up</p>
  <h1>Which spot <em>complained</em> most?</h1>
  <p class="lead">Three short routines, three moves each. Move slowly, stay in a comfortable range and stop if anything feels sharp.</p>
  <nav class="jump" aria-label="Pick a routine"><a class="dw dw-mint" href="#neck">Neck</a><a class="dw dw-pink" href="#wrists">Wrists</a><a class="dw dw-blue" href="#hips">Hips</a></nav>
  <p class="small"><a href="#free">Prefer it on one page? Get the free 5-minute desk stretch</a></p>
</section>

<section class="wrap routines" aria-label="Routines">
  <article class="routine r-mint" id="neck">
    <div class="routine-head"><p class="kicker">Routine 1 · 3 minutes</p><h2>Neck after 4 hours of gaming</h2><img class="routine-photo" src="assets/routine-neck.jpg" alt="Kristine doing a chin tuck on a chair, seen from the side" width="340" height="340" loading="lazy"></div>
    <ol class="moves">
      <li><strong>Chin tucks</strong><span>Sit tall. Slide your chin straight back without tilting your head, hold 2 seconds, release.</span><span class="dose">8 slow reps</span></li>
      <li><strong>Side neck stretch</strong><span>Drop one ear toward your shoulder. Hold the chair seat with the other hand to keep that shoulder down.</span><span class="dose">20–30 s per side</span></li>
      <li><strong>Shoulder blade squeeze</strong><span>Pull your shoulder blades back and down, hold 3 seconds, release.</span><span class="dose">10 reps</span></li>
    </ol>
  </article>
  <article class="routine r-pink" id="wrists">
    <div class="routine-head"><p class="kicker">Routine 2 · 3 minutes</p><h2>Wrists for mouse and keyboard</h2><img class="routine-photo" src="assets/routine-wrists.jpg" alt="A wrist stretch: one hand gently pulling the fingers back" width="340" height="340" loading="lazy"></div>
    <ol class="moves">
      <li><strong>Wrist flexor stretch</strong><span>Arm straight in front, palm facing forward, fingers up. Gently pull your fingers back with the other hand.</span><span class="dose">20 s per hand</span></li>
      <li><strong>Wrist extensor stretch</strong><span>Arm straight, palm down. Gently press the back of your hand toward you.</span><span class="dose">20 s per hand</span></li>
      <li><strong>Tendon glides</strong><span>Open hand, hook fist, full fist, flat fist, straight fingers. Move slowly through each shape.</span><span class="dose">5 rounds</span></li>
    </ol>
  </article>
  <article class="routine r-blue" id="hips">
    <div class="routine-head"><p class="kicker">Routine 3 · 4 minutes</p><h2>Hips after a long stream</h2><p class="tag-line">Needs a bit of floor</p><img class="routine-photo" src="assets/routine-hips.jpg" alt="Kristine doing a seated figure-4 hip stretch on a chair" width="340" height="340" loading="lazy"></div>
    <ol class="moves">
      <li><strong>Half-kneeling hip flexor stretch</strong><span>One knee down on a cushion. Squeeze the glute of the back leg and shift your hips forward a little.</span><span class="dose">30 s per side</span></li>
      <li><strong>Seated figure-4</strong><span>Ankle on the opposite knee, sit tall, hinge forward slightly from the hips.</span><span class="dose">30 s per side</span></li>
      <li><strong>Glute bridge</strong><span>On your back, knees bent. Push through your heels and lift your hips, pause at the top.</span><span class="dose">10 slow reps</span></li>
    </ol>
  </article>
  <p class="notice">Not medical advice. These are general mobility exercises. If you have pain, an injury or a medical condition, check with a doctor first.</p>
</section>
""" + free_band("Want it all on <em>one</em> page?", LIST_PERKS, chat="")
page(
    "free.html",
    "Free Desk Stretch Routines · Kristine Maia",
    "Free mobility routines for neck, wrists and hips after long hours at the desk, plus the free 5-minute desk stretch PDF.",
    free,
)


# =====================================================================
# 2b. TRAINING (training.html): chestionarul care potrivește planul (versiunea 2).
#    Răspunsurile rămân în browser (nu se trimit nicăieri).
#    Până se deschide clubul, butoanele duc la lista de așteptare (LINKS["CLUB"]).
# =====================================================================
def q_radio(name, legend, opts, hint="", extra=""):
    o = "".join('<label class="opt"><input type="radio" name="%s" value="%s"><span>%s</span></label>' % (name, v, t) for v, t in opts)
    h = '<p class="small muted">%s</p>' % hint if hint else ""
    return '<fieldset class="qf"%s><legend>%s</legend>%s<div class="opts">%s</div></fieldset>' % (extra, legend, h, o)

def q_check(name, legend, opts, hint="", extra=""):
    o = "".join('<label class="opt"><input type="checkbox" name="%s" value="%s"><span>%s</span></label>' % (name, v, t) for v, t in opts)
    h = '<p class="small muted">%s</p>' % hint if hint else ""
    return '<fieldset class="qf"%s><legend>%s</legend>%s<div class="opts">%s</div></fieldset>' % (extra, legend, h, o)

QUIZ = "".join([
    q_radio("sit", "1. How many hours do you sit on a normal day?", [("lt4", "Under 4"), ("4-8", "4 to 8"), ("8-12", "8 to 12"), ("12", "12 or more")]),
    q_radio("goal", "2. What do you want most right now?", [("mob", "Move without stiffness"), ("str", "Get stronger"), ("fat", "Lose some fat and get fitter"), ("desk", "Feel better at my desk (neck, back, posture)")]),
    q_radio("focus", "3. Which part do you want to work on most?", [("whole", "Whole body"), ("lower", "Legs and glutes"), ("upper", "Upper body and back"), ("core", "Core and posture")]),
    q_radio("exp", "4. How much do you train at the moment?", [("new", "I'm new to training"), ("some", "I trained before, not now"), ("reg", "2 or more times a week")]),
    q_radio("place", "5. Where will you train?", [("home", "At home"), ("gym", "At the gym"), ("both", "Both")]),
    q_check("equip", "6. What do you have at home?", [("bands", "Resistance bands"), ("db", "Dumbbells"), ("kb", "Kettlebell"), ("bar", "Pull-up bar")], "Pick any, or none.", ' id="q-equip" hidden'),
    q_radio("time", "7. How much time per session?", [("10", "10 minutes"), ("20", "20 minutes"), ("35", "30 to 40 minutes")]),
    q_radio("days", "8. How many days a week?", [("2", "2 days"), ("3", "3 days"), ("4", "4 days")]),
    q_check("area", "9. Where do you feel it after a long day?", [("neck", "Neck"), ("upper", "Shoulders and upper back"), ("lower", "Lower back"), ("hips", "Hips"), ("wrists", "Wrists and elbows"), ("knees", "Knees")], "Pick any, or none."),
    q_radio("feel", "10. How does it feel?", [("stiff", "Stiff or tight, and better once I move"), ("pain", "Pain: sharp, constant, wakes me up, numbness or tingling, or after an injury")], "", ' id="q-feel" hidden'),
    q_radio("age", "11. How old are you?", [("u18", "Under 18"), ("18", "18 to 39"), ("40", "40 to 59"), ("60", "60 or more")]),
    q_check("health", "12. Does any of this apply to you?", [
        ("heart", "Heart condition, chest pain or fainting when active"), ("surg6", "Surgery in the last 6 months"),
        ("preg", "Pregnant"), ("doc", "A doctor told me to limit exercise"),
        ("surg", "Older surgery or joint replacement (more than 6 months ago)"), ("spine", "Disc problem or a diagnosed back condition"),
        ("bp", "High blood pressure"), ("diab", "Diabetes"), ("asthma", "Asthma"), ("osteo", "Osteoporosis or low bone density"),
        ("hernia", "Hernia"), ("post", "I had a baby in the last 12 months"), ("none", "None of these")],
        "Pick all that apply. Your answers stay on your phone or computer and are not sent anywhere."),
])

training = """
<section class="wrap page-head">
  <p class="kicker">Online training</p>
  <h1>Your <em>custom</em> program, built around how much you sit.</h1>
  <p class="lead">Your goal, your stiff spots, your time, home or gym. Answer a few quick questions and your program is built from your answers: stronger, leaner, less stiff, or all three.</p>
  <div class="actions"><a class="btn" href="#quiz">Build my program</a></div>
</section>

<section class="wrap block pt-s" aria-labelledby="how-title">
  <div class="block-head"><p class="kicker">How it works</p><h2 id="how-title">Three steps</h2></div>
  <ol class="steps">
    <li><b>Take the quiz.</b> Two minutes. Your answers stay in your browser.</li>
    <li><b>Get your custom program.</b> Your week, day by day, plus short resets for the spots that feel stiff.</li>
    <li><b>Train with me.</b> Follow-along videos filmed in the gym, with home versions, 10 to 40 minutes. When the Custom Program opens, members get their program, every video and a new workout every week.</li>
  </ol>
</section>

<section class="wrap block" id="quiz" aria-labelledby="quiz-title">
  <div class="block-head"><p class="kicker">The quiz</p><h2 id="quiz-title">Build your program</h2></div>
  <form class="quiz" id="quiz-form" novalidate>
    """ + QUIZ + """
    <p class="small muted" id="quiz-err" role="alert" hidden>Please answer every question (6 and 9 are optional; for 12, pick “None of these” if nothing applies).</p>
    <button class="btn" type="submit">Show my custom program</button>
  </form>
</section>

<section class="wrap block pt-s" id="result" aria-live="polite" hidden>
  <article class="panel p-mint plan">
    <span class="tag">Your custom program</span>
    <h2 id="r-track">Track</h2>
    <p class="muted" id="r-level"></p>
    <div id="r-age" class="notice-safe" hidden><b>This program is for adults.</b> If you are under 18, show this page to a parent, a PE teacher or a coach and train with them. The gentle mobility below is a safe place to start.</div>
    <div id="r-safe" class="notice-safe" hidden><b>Check with your doctor first.</b> Because of your health answers, start only with gentle mobility and ask your doctor before you add strength or cardio.</div>
    <div id="r-adj-w" class="notice-safe" hidden><b>Adjusted for you.</b> Show this plan to your doctor or physio before you start.<ul id="r-adj"></ul></div>
    <div id="r-pain" class="notice-safe" hidden><b>About the pain you mentioned.</b> Sharp, constant or night pain, numbness, tingling or pain after an injury should be checked by a doctor or physiotherapist. Until you have the all-clear, skip any exercise that hurts there; the resets for those spots stay out of your plan.</div>
    <h3>Your week</h3>
    <ul id="r-week"></ul>
    <div id="r-extra-w" hidden><h3>Every day</h3><ul id="r-extra"></ul></div>
    <h3 id="r-resets-h">Extra 5-minute resets</h3>
    <ul id="r-resets"></ul>
    <h3>On sitting days</h3>
    <p id="r-breaks"></p>
    <p class="small muted">General exercise and education, not medical or diet advice. Stop if anything feels sharp or painful.</p>
    <div class="row-btns">
      <a class="btn" href="{CLUB}">Join your custom program (waitlist)</a>
      <a class="btn alt" href="{PAYHIP}">Start today: free 5-minute desk stretch</a>
    </div>
    <p class="small"><a href="shop.html#coaching">Want me to check your form? 1:1 coaching waitlist</a> · <button class="link-btn" id="q-again" type="button">Take the quiz again</button></p>
  </article>
</section>

<section class="wrap block" aria-labelledby="club-title">
  <div class="block-head"><p class="kicker">Coming soon · waitlist</p><h2 id="club-title">What makes it custom</h2></div>
  <ul class="steps">
    <li><b>Your goal:</b> no stiffness, stronger, leaner, or feeling better at your desk.</li>
    <li><b>Your focus:</b> whole body, legs and glutes, upper body and back, or core and posture.</li>
    <li><b>Your place:</b> home, gym or both, with the equipment you actually have.</li>
    <li><b>Your time:</b> 10 to 40 minutes, 2 to 4 days a week.</li>
    <li><b>Your body:</b> resets for the spots that feel stiff, and a safer plan if something hurts.</li>
    <li><b>Your health:</b> age, past surgeries and conditions decide what goes in your plan and what stays out.</li>
  </ul>
  <p class="small muted mt-s">Your program is built from these building blocks:</p>
  <div class="tracks">
    <article class="panel p-blue"><h3>Unstiff</h3><p class="muted">Mobility for people who sit all day. 10 to 20 minutes, anywhere.</p></article>
    <article class="panel p-pink"><h3>Get Strong</h3><p class="muted">Strength at home or at the gym, with a focus on legs and glutes, upper body or core. Beginner and intermediate.</p></article>
    <article class="panel p-lilac"><h3>Shape Up</h3><p class="muted">Strength plus short cardio sessions (jump rope, incline walking) and simple daily habits. No crash diets.</p></article>
    <article class="panel p-mint"><h3>Desk Reset</h3><p class="muted">Posture, neck and back: upper-back strength, core and 5-minute resets for the spots that complain.</p></article>
  </div>
  <p class="small muted mt-s">Every program runs in 4-week blocks that get a little harder each week, with gym and home versions. A new workout every week and a monthly live class with me. Want me to check your form and adjust it by hand? That's <a href="shop.html#coaching">1:1 coaching</a>. Founding price for people on the waitlist.</p>
</section>

<section class="wrap block pt-s" aria-labelledby="tfaq-title">
  <div class="block-head"><p class="kicker">Questions</p><h2 id="tfaq-title">Before you start</h2></div>
  <div class="faq">
    <details><summary>Is this medical treatment?</summary><p>No. I have a degree in Physical Education and Sport and coach mobility and strength. This is general exercise and education. If you have pain, an injury or a medical condition, see a doctor first.</p></details>
    <details><summary>Will this help me lose weight?</summary><p>The Shape Up track combines strength, short cardio and daily movement, which supports fat loss together with how you eat. I don't promise kilos or write diets. For personal nutrition, talk to a dietitian.</p></details>
    <details><summary>I'm a complete beginner. Is it for me?</summary><p>Yes. The beginner plans start with short sessions and simple moves, and every exercise has an easier option.</p></details>
    <details><summary>Home or gym?</summary><p>Both work. Every workout has a gym version and a home version, and you can mix them in the same week.</p></details>
    <details><summary>Do you make meal plans?</summary><p>No. I'm not a dietitian, so I don't write personal meal plans. I share general food ideas and quick recipes.</p></details>
  </div>
</section>

<script>
(function(){
  var f=document.getElementById('quiz-form'); if(!f) return;
  var res=document.getElementById('result'), err=document.getElementById('quiz-err');
  var qEquip=document.getElementById('q-equip'), qFeel=document.getElementById('q-feel');
  var AREAS={neck:'Neck reset',upper:'Shoulders and upper back reset',lower:'Lower back reset',hips:'Hips reset',wrists:'Wrists and elbows reset',knees:'Knee-friendly hips and ankles'};
  var BREAKS={'lt4':'One 2-minute stretch break in the middle of the day.','4-8':'A 2-minute stretch break every 2 hours.','8-12':'A 2-minute stretch break every 90 minutes. Set a timer.','12':'A 2-minute stretch break every hour, like we do on stream. Set a timer.'};
  var SPLIT={
    whole:{2:['Full body A','Full body B'],3:['Lower body and core','Upper body and back','Full body'],4:['Lower body','Upper body and back','Lower body','Upper body and core']},
    lower:{2:['Legs and glutes','Full body'],3:['Legs and glutes','Upper body and back','Glutes and core'],4:['Legs','Upper body and back','Glutes and hamstrings','Upper body and core']},
    upper:{2:['Upper body and back','Full body'],3:['Upper body and back','Lower body and core','Shoulders and posture'],4:['Upper body and back','Lower body','Shoulders and posture','Lower body and core']},
    core:{2:['Full body + core finisher','Full body + core finisher'],3:['Lower body + core','Upper body and posture','Core and full body'],4:['Lower body + core','Upper body and posture','Lower body + core','Core and full body']}
  };
  var ADJ={
    surg:'Older surgery: follow the limits your surgeon or physio gave you, and skip moves that load that area until they say it is fine.',
    spine:'Back condition: no heavy bending or twisting under load; a physio should check which moves are right for you.',
    bp:'High blood pressure: breathe out on the effort, never hold your breath, no max lifts, and get up slowly from the floor.',
    diab:'Diabetes: keep water and a quick snack nearby, and ask your doctor how training fits with your treatment.',
    asthma:'Asthma: keep your inhaler nearby, warm up a few extra minutes and build cardio up slowly.',
    osteo:'Low bone density: no jumping and no loaded rounding of the spine (like weighted sit-ups); strength work built up slowly.',
    hernia:'Hernia: no heavy straining or breath-holding, gentle core work only, and check with your doctor first.',
    post:'After a baby: start with breathing and pelvic-floor work; no jumping or crunches until a doctor or pelvic-floor physio clears you.'
  };
  function val(n){var e=f.querySelector('input[name="'+n+'"]:checked');return e?e.value:null}
  function vals(n){return [].map.call(f.querySelectorAll('input[name="'+n+'"]:checked'),function(x){return x.value})}
  function li(t){var l=document.createElement('li');l.textContent=t;return l}
  f.addEventListener('change',function(e){
    var t=e.target; if(t.name!=='health'||!t.checked) return;
    [].forEach.call(f.querySelectorAll('input[name="health"]'),function(x){ if(t.value==='none'?x.value!=='none':x.value==='none') x.checked=false; });
  });
  function sync(){
    var pl=val('place'); qEquip.hidden=!(pl==='home'||pl==='both');
    qFeel.hidden=vals('area').length===0;
  }
  f.addEventListener('change',sync);
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var need=['sit','goal','focus','exp','place','time','days','age','health']; if(!qFeel.hidden) need.push('feel');
    for(var i=0;i<need.length;i++){ if(!val(need[i])){ err.hidden=false; var q=f.querySelector('input[name="'+need[i]+'"]'); q.closest('fieldset').scrollIntoView({behavior:'smooth',block:'center'}); return; } }
    err.hidden=true;
    var a={sit:val('sit'),goal:val('goal'),focus:val('focus'),exp:val('exp'),place:val('place'),time:val('time'),days:+val('days'),age:val('age'),feel:val('feel')};
    var eq=vals('equip'), areas=vals('area'), hl=vals('health'), pain=(a.feel==='pain'&&areas.length>0);
    var has=function(x){return hl.indexOf(x)>-1}, minor=(a.age==='u18');
    var safe=minor||['heart','surg6','preg','doc'].some(has);
    var adj=Object.keys(ADJ).filter(has).map(function(x){return ADJ[x]});
    if(a.age==='60') adj.push('60 or more: two minutes of balance practice next to a wall on training days.');
    var noJump=['osteo','post','hernia'].some(has)||areas.indexOf('knees')>-1;
    var mins={'10':'10','20':'20','35':'30 to 40'}[a.time];
    var level=(a.exp==='reg')?'Intermediate':(a.exp==='some'?'Returning beginner':'Beginner');
    var homeKit=eq.length?('home, with '+eq.map(function(x){return {bands:'bands',db:'dumbbells',kb:'a kettlebell',bar:'a pull-up bar'}[x]}).join(', ')):'home, no equipment';
    var where={home:homeKit,gym:'gym',both:'gym and '+homeKit}[a.place];
    var dayPlace=function(i){ if(a.place!=='both') return ''; return (i%2===0)?' (gym)':' (home)'; };
    var track, week=[], extra=[];
    if(safe){
      track='Unstiff (gentle)'; level='Beginner';
      for(var j=1;j<=a.days;j++) week.push('Day '+j+': gentle mobility, '+(a.time==='35'?'20':mins)+' minutes');
    } else if(a.goal==='mob'){
      track='Unstiff';
      for(var j=1;j<=a.days;j++) week.push('Day '+j+': Unstiff, full-body mobility, '+mins+' minutes');
    } else if(a.goal==='desk'){
      track='Desk Reset';
      var dr=['Upper back and core strength','Unstiff: neck, shoulders and hips','Upper back, glutes and core','Unstiff: full body'];
      for(var j=0;j<a.days;j++) week.push('Day '+(j+1)+': '+dr[j]+dayPlace(j)+', '+mins+' minutes');
      extra.push('A 5-minute reset at your desk, once a day');
    } else {
      var express=(a.time==='10');
      var s=(a.goal==='fat')?Math.max(2,a.days-1):a.days;
      var plan=SPLIT[a.focus][s];
      track=(a.goal==='fat'?'Shape Up':'Get Strong')+(express?' · Express':'');
      plan.forEach(function(p,i){ week.push('Day '+(i+1)+': '+p+dayPlace(i)+', '+mins+' minutes'); });
      if(a.goal==='fat'){
        week.push('Day '+(s+1)+': Cardio, 15 to 20 minutes ('+(noJump?'incline walking or marching in place, no jumping':'jump rope intervals or incline walking')+')'+(a.place==='both'?' (home or gym)':''));
        extra.push('Walk a bit more than you do now, for example 2,000 extra steps a day');
        extra.push('Protein and vegetables at each meal; hand portions instead of a scale (general food ideas, not a diet)');
      }
    }
    var shownAreas=pain?[]:areas;
    document.getElementById('r-track').textContent=track;
    document.getElementById('r-level').textContent='Level: '+level+' · '+where+(safe?'':' · '+a.days+' days a week · '+mins+' minutes');
    document.getElementById('r-age').hidden=!minor;
    document.getElementById('r-safe').hidden=!safe||minor;
    var aj=document.getElementById('r-adj');aj.innerHTML='';adj.forEach(function(t){aj.appendChild(li(t))});
    document.getElementById('r-adj-w').hidden=safe||!adj.length;
    document.getElementById('r-pain').hidden=!pain;
    var w=document.getElementById('r-week');w.innerHTML='';week.forEach(function(t){w.appendChild(li(t))});
    var ex=document.getElementById('r-extra');ex.innerHTML='';extra.forEach(function(t){ex.appendChild(li(t))});
    document.getElementById('r-extra-w').hidden=!extra.length;
    var r=document.getElementById('r-resets');r.innerHTML='';
    if(shownAreas.length){shownAreas.forEach(function(x){r.appendChild(li(AREAS[x]+', 5 minutes, on any day'))})}
    else r.appendChild(li(pain?'Resets for those spots come after your doctor or physio says it is okay.':'No extra resets needed. Keep the stretch breaks.'));
    document.getElementById('r-breaks').textContent=BREAKS[a.sit];
    res.hidden=false; res.scrollIntoView({behavior:'smooth',block:'start'});
  });
  document.getElementById('q-again').addEventListener('click',function(){f.reset();sync();res.hidden=true;document.getElementById('quiz').scrollIntoView({behavior:'smooth'})});
  sync();
})();
</script>
""" + free_band("Start with <em>five</em> minutes.", LIST_PERKS)
page(
    "training.html",
    "Online Training · Kristine Maia",
    "Take the 2-minute quiz and get your custom program, built around how much you sit: stronger, leaner or less stiff, at home, at the gym or both.",
    training,
)


# =====================================================================
# 3. SHOP (shop.html)
#    „Tell me when it's out” / „Join the waitlist” duc la formularul de email (#free).
#    Când e-book-ul și programul sunt pe Payhip, pui linkul Payhip în locul lui #free.
# =====================================================================
shop = """
<section class="wrap page-head">
  <p class="kicker">Shop</p>
  <h1>When a minute isn't <em>enough</em>.</h1>
  <p class="lead">Everything here is built for people who sit for long hours. Start small. You can always go further.</p>
</section>

<section class="wrap block" aria-labelledby="soon-title">
  <div class="block-head"><p class="kicker">Coming soon · join the waitlist</p><h2 id="soon-title">Good food and a 30-day plan</h2></div>
  <div class="duo">
    <article class="panel p-pink" id="kitchen">
      <img class="book" src="assets/ebook-cover.jpg" alt="Cover of the e-book Stream Day Kitchen by Kristine Maia" width="200" height="320" loading="lazy">
      <span class="tag">Waitlist · updated edition</span>
      <h3>Stream Day Kitchen</h3>
      <p class="p">€12<small>e-book</small></p>
      <p class="muted">Healthy, filling meals and hand-portion basics for people who sit all day.</p>
      <ul><li>Quick recipes for long days: protein pancakes, a no-cook tuna and red bean salad, salmon with potatoes and salad and more</li><li>The hand-portion method: eat well without a scale</li><li>A shopping list of what I always keep in my kitchen</li></ul>
      <a class="btn alt" href="#free">Join the waitlist</a>
    </article>
    <article class="panel p-blue" id="program">
      <span class="tag">Waitlist</span>
      <h3>Desk &amp; Gamer Mobility: 30 days</h3>
      <p class="p">€39<small>€29 for the email list</small></p>
      <ul><li>10 minutes a day, follow-along videos</li><li>Neck, upper back, wrists, hips and lower back</li><li>Watch on your phone</li></ul>
      <a class="btn alt" href="#free">Join the waitlist</a>
    </article>
  </div>
</section>

<section class="wrap block" aria-labelledby="coach-title">
  <div class="block-head"><p class="kicker">Coming soon · small group</p><h2 id="coach-title">Train with me, one to one</h2></div>
  <article class="panel p-mint" id="coaching">
    <span class="tag">Waitlist · limited spots</span>
    <h3>1:1 online coaching</h3>
    <p class="p">€49<small>per month</small></p>
    <p class="muted">A training plan built around your week, at the gym or at home, with feedback on your form. Made for people who sit for long hours and want to get stronger and move better.</p>
    <ul><li>A plan for your goal, your schedule and your equipment, adjusted every week</li><li>Send me short videos of your sets: I check your form and tell you what to change</li><li>Strength and mobility together, no extreme diets</li><li>A small group, so every client gets real attention</li></ul>
    <p class="small muted">Not included: personal meal plans or medical advice. I share general food ideas only. If you have pain or an injury, see a doctor first.</p>
    <a class="btn" href="{COACHING}">Join the coaching waitlist</a>
    <p class="small muted">People on the waitlist hear first and get founding-client pricing.</p>
  </article>
</section>

<section class="wrap block" id="gear" aria-labelledby="gear-title">
  <div class="block-head"><p class="kicker">Gear I actually use</p><h2 id="gear-title">Discount codes</h2><p class="small muted">Affiliate links: I may earn a small commission at no extra cost to you. I only list things I use myself.</p></div>
  <div class="codes">
    <!-- TODO: pune linkurile reale de afiliere în locul lui #TODO-link-... -->
    <article class="ticket"><p class="off">10% off</p><h3>Dope Rope</h3><p class="muted">The jump rope I use for my 5-minute warm-up before every gym session.</p><p class="code">Code <b>KRISTINEMAIA</b></p><a class="tl" href="#TODO-link-dope-rope">Shop Dope Rope</a></article>
    <article class="ticket"><p class="off">20% off</p><h3>Revu Natural</h3><p class="muted">Recovery creams I use after long streams and training.</p><p class="code">Code <b>KRISTINE20</b></p><a class="tl" href="#TODO-link-revu-natural">Shop Revu Natural</a></article>
    <article class="ticket"><p class="off">15% off</p><h3>Bewit</h3><p class="muted">Natural products that are part of my daily routine.</p><p class="code">Code <b>KRISTINE15</b></p><a class="tl" href="#TODO-link-bewit">Shop Bewit</a></article>
  </div>
</section>

<section class="wrap block pt-s" aria-labelledby="faq-title">
  <div class="block-head"><p class="kicker">Questions</p><h2 id="faq-title">Before you buy</h2></div>
  <div class="faq">
    <details><summary>Is this medical treatment?</summary><p>No. I have a degree in Physical Education and Sport and coach mobility. Everything here is general exercise and education, not a diagnosis or treatment. If you have pain or an injury, see a doctor.</p></details>
    <details><summary>How does online coaching work?</summary><p>You tell me your goal, your schedule and what equipment you have. I build your plan, you train and send me short videos of your sets, and every week I check your form and adjust the plan. It is exercise coaching, not treatment.</p></details>
    <details><summary>Can you write me a meal plan?</summary><p>No. I'm not a dietitian, so I don't write personal meal plans. I share general food ideas, like the quick recipes in my e-book.</p></details>
    <details><summary>Do I need equipment?</summary><p>A chair, a wall and a bit of floor space. Some routines use a resistance band, which is optional.</p></details>
    <details><summary>How do I get my product after paying?</summary><p>You get an email with your download or access link right after payment.</p></details>
    <details><summary>Refunds</summary><p>See the purchase terms on the <a href="legal.html">legal page</a>.</p></details>
  </div>
</section>
""" + free_band("Start with <em>five</em> minutes.", LIST_PERKS)
page(
    "shop.html",
    "Shop · Kristine Maia",
    "The Stream Day Kitchen e-book, the 30-day Desk & Gamer Mobility program and 1:1 online coaching (all on the waitlist), plus discount codes for gear I use.",
    shop,
)


# =====================================================================
# 4. LIVE (live.html)
# =====================================================================
live = """
<section class="wrap page-head">
  <p class="kicker">Live on Twitch</p>
  <h1>Come for the stream. Stay for the <em>stretch</em>.</h1>
  <p class="lead">Five years live and 72K followers. The streams are relaxed, the chat is kind, and when I game we stand up for two minutes every hour.</p>
  <div class="actions"><a class="btn" href="{TWITCH}">Watch on Twitch</a><a class="tl" href="{TWITCH}/schedule">See the schedule</a></div>
</section>

<section class="wrap pb-m" aria-labelledby="week-title">
  <h2 id="week-title">What's on stream.</h2>
  <p class="lead mt-s">My streams change from day to day. You might find a workout, a mobility session, yoga, cooking, gaming, just chatting, or simply good vibes. Bring a chair, a wall or a mat if you want to move with me.</p>
  <ul class="topics lg" aria-label="What happens on stream">
    <li>Workouts</li><li>Mobility</li><li>Yoga</li><li>Cooking</li><li>Gaming</li><li>Just chatting</li><li>Good vibes</li>
  </ul>
  <p class="small muted mt-s">Streams are announced on my <a href="{TWITCH}/schedule">Twitch schedule</a>.</p>
</section>

<section class="wrap block pt-s">
  <div class="duo">
    <div class="panel p-lilac">
      <p class="kicker">Support the stream</p>
      <h2>Subscribing keeps it going</h2>
      <p>Every sub supports the channel directly and helps me make more mobility and cooking streams. Thank you.</p>
      <a class="btn" href="{TWITCH}">Subscribe on Twitch</a>
    </div>
    <div class="panel plain">
      <p class="kicker">Chat rules</p>
      <h2>Kind, curious, on topic</h2>
      <ul class="muted">
        <li>Be kind to each other and to me.</li>
        <li>No sexual comments. Instant ban.</li>
        <li>No personal questions about my private life.</li>
        <li>Health questions are welcome, but I can't diagnose anyone. Not medical advice.</li>
      </ul>
    </div>
  </div>
</section>
"""
page(
    "live.html",
    "Live on Twitch · Kristine Maia",
    "Live on Twitch: workouts, mobility, yoga, cooking, gaming and just chatting, with a 2-minute stretch break every hour when I game.",
    live,
)


# =====================================================================
# 5. DESPRE (about.html)
# =====================================================================
about = """
<section class="wrap page-head">
  <p class="kicker">About</p>
  <h1>Hi, I'm <em>Kristine</em>.</h1>
</section>

<section class="wrap block pt-0">
  <div class="split">
    <div class="portrait"><img src="assets/kristine-about.jpg" alt="Kristine Maia, standing against a white wall" width="900" height="1125"></div>
    <div class="prose">
      <p class="lead">I help people who sit all day move better, recover faster and eat well, without making it complicated.</p>
      <p>I've streamed on Twitch for five years and built a community of 72,000 people around the world. I studied sport: I hold a degree in Physical Education and Sport, and I coach mobility and recovery for people who sit all day.</p>
      <p>On stream I train, cook, paint and play games. Over the years my chat kept telling me the same thing: stiff necks, sore wrists, tight hips, too much takeaway. So I started doing something about it live, two minutes at a time. That became the hourly stretch break when I game, and it's what everything on this site is built on.</p>
      <h2>What I am</h2>
      <ul class="creds">
        <li>Degree in Physical Education and Sport</li>
        <li>Mobility &amp; recovery coach</li>
      </ul>
      <p class="muted">I'm not a medical professional, and nothing here is medical advice, a diagnosis or a treatment.</p>
      <div class="actions"><a class="btn" href="free.html">Try the free routines</a><a class="tl" href="{TWITCH}">Watch live on Twitch</a></div>
    </div>
  </div>
</section>
""" + free_band("Start with <em>five</em> minutes.", LIST_PERKS)
page(
    "about.html",
    "About Kristine Maia",
    "Degree in Physical Education and Sport, mobility coach and Twitch Partner helping people who sit all day.",
    about,
)


# =====================================================================
# 6. BRANDURI (brands.html)
# =====================================================================
brands = """
<section class="wrap page-head">
  <p class="kicker">For brands</p>
  <h1>Reach people who <em>sit</em> all day.</h1>
  <p class="lead">My audience games, streams and works long hours at a desk, and they want to feel better doing it. I partner with brands that genuinely help with that.</p>
  <div class="actions"><a class="btn" href="mailto:{EMAIL}?subject=Partnership">Email me</a><span class="small muted">{EMAIL} · media kit on request</span></div>
</section>

<section class="wrap pb-s" aria-label="Numbers">
  <div class="stats">
    <div class="stat"><strong>72K</strong><span>Twitch followers · Partner</span></div>
    <div class="stat"><strong>125–230</strong><span>average live viewers per month (last 12 months)</span></div>
    <div class="stat"><strong>12.7K</strong><span>Instagram followers (@kristinemaia11)</span></div>
    <div class="stat"><strong>5 years</strong><span>streaming, 4–5 streams a week</span></div>
    <div class="stat"><strong>142K</strong><span>Instagram views in the last 30 days</span></div>
    <div class="stat"><strong>12.6K</strong><span>views on my jump-rope affiliate reel</span></div>
  </div>
</section>

<section class="wrap block">
  <div class="cols">
    <div><p class="kicker">Good fits</p><h2>What I promote</h2><ul><li>Ergonomics: desks, chairs, mice and keyboards</li><li>Recovery tools: massage guns, rollers, creams</li><li>Nutrition: quick meals, protein, healthy snacks</li><li>Sportswear, mats and training gear</li></ul><p class="small muted">I say no to anything that doesn't fit a health-focused audience.</p></div>
    <div><p class="kicker">Formats</p><h2>How we can work together</h2><ul><li>Sponsored segment inside a stream (a workout, a cooking stream or gaming)</li><li>Dedicated sponsored stream</li><li>Instagram reels package (2–4 reels)</li><li>Discount code for my community, tracked</li><li>Longer-term ambassador or advisory role</li></ul><p class="small muted">All sponsored content is clearly labelled.</p></div>
  </div>
  <div class="notice mt-m"><strong>Current partners:</strong> Dope Rope (jump ropes), Revu Natural (recovery creams) and Bewit (natural products), all with tracked discount codes for my community. Each one gets a short segment on stream and a reel.</div>
</section>
"""
page(
    "brands.html",
    "Partnerships · Kristine Maia",
    "Partner with Kristine Maia: Twitch Partner with 72K followers and a health-focused audience of people who sit all day.",
    brands,
)


# =====================================================================
# 8. LEGAL (legal.html) · de verificat cu avocatul / contabila
# =====================================================================
legal = """
<section class="wrap page-head">
  <p class="kicker">Legal</p>
  <h1>Legal &amp; <em>privacy</em></h1>
  <p class="notice">TODO: completează datele firmei și roagă avocatul sau contabila să verifice această pagină înainte de lansare.</p>
</section>

<section class="wrap block pt-0">
  <div class="prose">
    <h2>Who runs this site</h2>
    <p class="muted">[TODO: denumirea firmei], CUI [TODO], [TODO: sediul]. Contact: {EMAIL}.</p>
    <h2>Not medical advice</h2>
    <p class="muted">All content on this site, in my streams and in my products is general information about exercise, mobility and nutrition. It is not medical advice, diagnosis or treatment. I have a degree in Physical Education and Sport and coach mobility, not a medical professional. If you have pain, an injury, a medical condition, are pregnant or take medication, talk to a doctor before starting any routine or changing your diet.</p>
    <h2>Privacy</h2>
    <p class="muted">If you join the email list, your email address is stored by my email provider [TODO: MailerLite / Kit] only to send you the free routine and updates. You can unsubscribe at any time with one click. If you buy something, your order is processed by [TODO: Payhip], which handles payment and delivery. This site does not use advertising cookies. Fonts are loaded from Google Fonts, so your browser sends your IP address to Google when a page loads. To ask about, correct or delete your data, email {EMAIL}.</p>
    <h2>Purchases</h2>
    <p class="muted">Digital products are delivered by email right after payment. [TODO: politica de retur, verificată de avocat: de exemplu, dreptul de retragere pentru conținut digital și momentul în care se pierde].</p>
    <h2>Affiliate links</h2>
    <p class="muted">Some links on this site are affiliate links. If you buy through them I may earn a small commission at no extra cost to you. Sponsored content is always labelled.</p>
  </div>
</section>
"""
page("legal.html", "Legal & Privacy · Kristine Maia", "Legal information, privacy and medical disclaimer.", legal, cur="none")

print("ok: 8 pages written to " + OUT)
