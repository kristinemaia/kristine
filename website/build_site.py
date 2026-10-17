# -*- coding: utf-8 -*-
"""
Generatorul site-ului Kristine Maia.

Rulează din folderul website:   python3 build_site.py
Scrie din nou toate paginile (index, free, shop, live, about, brands, terapie, legal)
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
    "KM_INSTA": "https://www.instagram.com/kmwellnessconcept/",
    "EMAIL": "kristinemaia527@gmail.com",
    # TODO: înlocuiește cu linkul real de programare și plată (Calendly + Stripe sau Payhip)
    "BOOK": "#TODO-link-programare-si-plata",
}

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">'
)

# Meniul de sus (terapie.html și legal.html sunt doar în footer)
NAV = [
    ("index.html", "Home"),
    ("free.html", "Free routines"),
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
        <li><a href="shop.html">{shop}</a></li>
        <li><a href="live.html">Live</a></li>
        <li><a href="about.html">{about}</a></li>
        <li><a href="brands.html">{brands}</a></li>
        <li><a href="terapie.html" lang="ro" hreflang="ro">Terapie · KM Wellness</a></li>
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
<!-- PDF-ul gratuit: 5-minute desk stretch -->
<section class="free" id="free" aria-labelledby="free-title">
  <div class="wrap free-grid">
    <p class="five" aria-hidden="true">5:00</p>
    <div class="free-copy">
      {chat_line}
      <h2 id="free-title">{title}</h2>
      <p>The free 5-minute desk stretch. All four spots on one printable page: neck, shoulders, wrists and hips, from your chair.</p>
      <!-- TODO: înlocuiește formularul cu codul de embed din MailerLite sau Kit (vezi README) -->
      <form class="form" data-placeholder>
        <label for="email">Your email</label>
        <div class="form-row"><input type="email" id="email" name="email" placeholder="you@example.com" required autocomplete="email"><button class="btn" type="submit">Send me the stretch</button></div>
        <p class="fine">No spam. Unsubscribe in one click.{extra}</p>
        <p class="form-msg" aria-live="polite"></p>
      </form>
    </div>
  </div>
</section>
"""
    chat_line = '<p class="chat-line"><span class="who">kristinemaia</span> ' + chat + '</p>' if chat else ''
    return (html.replace("{chat_line}", chat_line).replace("{title}", title)
                .replace("{extra}", (" " + extra) if extra else ""))


LIST_PERKS = "The list also hears first about the e-book, the 30-day program at the early price and small-group class dates."

# Programul de pe Twitch. data-day: 1 = luni, 3 = miercuri, 5 = vineri (pentru „Today / Next up”).
# Duminica nu are data-day, pentru că e doar în unele săptămâni.
WEEK_HOME = """
      <ul class="days">
        <li data-day="1"><span class="dw dw-mint">Mon</span><p><b>Move Monday</b><span class="desc">A live mobility session. Follow along from your chair.</span></p></li>
        <li data-day="3"><span class="dw dw-pink">Wed</span><p><b>Cook with me</b><span class="desc">Quick healthy meals for long days.</span></p></li>
        <li data-day="5"><span class="dw dw-blue">Fri</span><p><b>Game night</b><span class="desc">With a 2-minute stretch break every hour. My signature.</span></p></li>
        <li><span class="dw dw-lilac some">Sun</span><p><b>Chill Sunday</b><span class="desc">Some weeks: painting or recovery.</span></p></li>
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
      <p class="next m-done"><a href="#assessment">Want moves picked for how you sit? Assessment, €55</a></p>
      <p class="spots m-done"><span>Which spot complained most?</span><a href="free.html#neck">Neck</a><a href="free.html#wrists">Wrists</a><a href="free.html#hips">Hips</a></p>
      <p class="m-done"><button class="link-btn" id="again" type="button">Do it again</button></p>

      <p class="note">Gentle range only, stop if anything hurts. Not medical advice.</p>
      <p class="sr" id="say" aria-live="polite"></p>
    </div>

    <div class="intro">
      <p>I'm <strong>Kristine</strong>, a sports science graduate and certified recovery massage therapist. On my Twitch game nights we stop for a 2-minute stretch every hour. Your turn.</p>
      <p class="small"><a href="#free">Or skip to the free 5-minute desk stretch</a></p>
    </div>
  </div>
</section>
""" + free_band("Now make it <em>five</em> minutes.", LIST_PERKS, chat="Want the longer one on paper?") + """
<!-- 3. Când un minut nu e destul: evaluarea + ce urmează -->
<section class="more" aria-labelledby="more-title">
  <div class="wrap">
    <div class="block-head">
      <p class="kicker">When a minute isn't enough</p>
      <h2 id="more-title">Want a plan made for how you sit?</h2>
    </div>
    <div class="more-grid">
      <article class="offer" id="assessment">
        <h3>Video mobility assessment</h3>
        <p class="price">€55<small>30-minute video call</small></p>
        <p>We look at how you sit, move and train. You get a written plan with 3–5 moves.</p>
        <p class="fine">Education and load management. Not a diagnosis or treatment.</p>
        <a class="btn" href="{BOOK}">Book the assessment</a>
      </article>
      <div class="soon">
        <p class="kicker">Coming soon</p>
        <p>The Stream Day Kitchen e-book (new edition) and the 30-day Desk &amp; Gamer Mobility program. People on the email list hear first and get the early price.</p>
        <p class="all"><a href="#free">Join the list</a> · <a href="shop.html">See the shop</a></p>
      </div>
    </div>
  </div>
</section>

<!-- 4. Cine sunt + săptămâna pe Twitch -->
<section class="me" aria-labelledby="me-title">
  <div class="wrap me-grid">
    <div class="bio">
      <div class="hi">
        <!-- TODO: pune o poză cu tine în locul literelor KM: <span class="mono"><img src="assets/kristine.jpg" alt="Kristine Maia"></span> -->
        <span class="mono" aria-hidden="true">KM</span>
        <p class="kicker">Who's counting</p>
      </div>
      <h2 id="me-title">Hi, I'm Kristine. I sit for a living too.</h2>
      <p>Twitch Partner, 72K followers, 5 years live. My chat kept telling me about stiff necks, sore wrists and whatever food was closest. So we work on it together, a few minutes at a time.</p>
      <ul class="creds">
        <li>Sports science graduate <span>(degree in Physical Education and Sport)</span></li>
        <li>Certified recovery massage therapist <span>(recovery &amp; sports massage, lymphatic drainage)</span></li>
        <li>Mobility &amp; recovery coach</li>
      </ul>
      <p><a class="tl" href="about.html">More about me</a></p>
    </div>

    <div class="week">
      <p class="kicker">Every week on Twitch</p>
      <h3>Your week on Twitch.</h3>
""" + WEEK_HOME + """
      <p class="perk">Subs get a monthly live 30-minute mobility session, with recordings in Discord.</p>
      <p class="small muted">Exact times are on my <a href="{TWITCH}/schedule">Twitch schedule</a>.</p>
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
    <div class="routine-head"><p class="kicker">Routine 1 · 3 minutes</p><h2>Neck after 4 hours of gaming</h2></div>
    <ol class="moves">
      <li><strong>Chin tucks</strong><span>Sit tall. Slide your chin straight back without tilting your head, hold 2 seconds, release.</span><span class="dose">8 slow reps</span></li>
      <li><strong>Side neck stretch</strong><span>Drop one ear toward your shoulder. Hold the chair seat with the other hand to keep that shoulder down.</span><span class="dose">20–30 s per side</span></li>
      <li><strong>Shoulder blade squeeze</strong><span>Pull your shoulder blades back and down, hold 3 seconds, release.</span><span class="dose">10 reps</span></li>
    </ol>
  </article>
  <article class="routine r-pink" id="wrists">
    <div class="routine-head"><p class="kicker">Routine 2 · 3 minutes</p><h2>Wrists for mouse and keyboard</h2></div>
    <ol class="moves">
      <li><strong>Wrist flexor stretch</strong><span>Arm straight in front, palm up. Gently pull your fingers back with the other hand.</span><span class="dose">20 s per hand</span></li>
      <li><strong>Wrist extensor stretch</strong><span>Arm straight, palm down. Gently press the back of your hand toward you.</span><span class="dose">20 s per hand</span></li>
      <li><strong>Tendon glides</strong><span>Open hand, hook fist, full fist, flat fist, straight fingers. Move slowly through each shape.</span><span class="dose">5 rounds</span></li>
    </ol>
  </article>
  <article class="routine r-blue" id="hips">
    <div class="routine-head"><p class="kicker">Routine 3 · 4 minutes</p><h2>Hips after a long stream</h2><p class="tag-line">Needs a bit of floor</p></div>
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

<section class="wrap pb-s" aria-labelledby="work-title">
  <h2 class="sr" id="work-title">Work with me</h2>
  <div class="more-grid">
    <article class="offer" id="assessment">
      <p class="kicker">1:1 on video · book now</p>
      <h2>Video mobility assessment</h2>
      <p class="price">€55<small>30-minute video call</small></p>
      <ul><li>We look at how you sit, move and train</li><li>A written plan with 3–5 moves made for you</li></ul>
      <p class="fine">Education and load management. Not a diagnosis or treatment.</p>
      <a class="btn" href="{BOOK}">Book &amp; pay</a>
    </article>
    <div class="soon">
      <p class="kicker">Live, with me</p>
      <div class="item" id="twitch-sub">
        <div class="item-top"><h3>Subscriber mobility session</h3><i></i><span class="p">Twitch sub</span></div>
        <p>A monthly live 30-minute mobility session for subs, with recordings in Discord. Every sub supports the channel directly.</p>
        <a href="{TWITCH}">Subscribe on Twitch</a>
      </div>
      <div class="item" id="classes">
        <div class="item-top"><h3>Small-group live class</h3><i></i><span class="p">€12</span></div>
        <p>45 minutes, 6–8 people. I see you and correct you live. Next dates soon, and they go to the email list first.</p>
        <a href="#free">Get the dates</a>
      </div>
    </div>
  </div>
</section>

<section class="wrap block" aria-labelledby="soon-title">
  <div class="block-head"><p class="kicker">Coming soon · join the waitlist</p><h2 id="soon-title">Good food and a 30-day plan</h2></div>
  <div class="duo">
    <article class="panel p-pink" id="kitchen">
      <span class="tag">New edition soon</span>
      <h3>Stream Day Kitchen</h3>
      <p class="p">€12<small>e-book</small></p>
      <ul><li>20 quick recipes, sorted by situation: before a long session, at the desk in 10 minutes, after the stream</li><li>The hand-portion method: eat well without a scale</li><li>Shopping list and a 7-day meal plan</li></ul>
      <a class="btn alt" href="#free">Tell me when it's out</a>
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
    <details><summary>Is this medical treatment?</summary><p>No. I'm a sports science graduate and a certified recovery massage therapist. Everything here is general exercise and education, not a diagnosis or treatment. If you have pain or an injury, see a doctor.</p></details>
    <details><summary>Do I need equipment?</summary><p>A chair, a wall and a bit of floor space. Some routines use a resistance band, which is optional.</p></details>
    <details><summary>How do I get my product after paying?</summary><p>You get an email with your download or access link right after payment.</p></details>
    <details><summary>Refunds</summary><p>See the purchase terms on the <a href="legal.html">legal page</a>.</p></details>
  </div>
</section>
""" + free_band("Start with <em>five</em> minutes.", LIST_PERKS)
page(
    "shop.html",
    "Shop · Kristine Maia",
    "Video mobility assessment, Twitch sub sessions, small-group classes, the Stream Day Kitchen e-book, the 30-day Desk & Gamer Mobility program and discount codes.",
    shop,
)


# =====================================================================
# 4. LIVE (live.html)
# =====================================================================
live = """
<section class="wrap page-head">
  <p class="kicker">Live on Twitch</p>
  <h1>Come for the stream. Stay for the <em>stretch</em>.</h1>
  <p class="lead">Five years live and 72K followers. The streams are relaxed, the chat is kind, and on game night we stand up for two minutes every hour.</p>
  <div class="actions"><a class="btn" href="{TWITCH}">Watch on Twitch</a><a class="tl" href="{TWITCH}/schedule">See the schedule</a></div>
</section>

<section class="wrap pb-m" aria-labelledby="week-title">
  <h2 id="week-title">Your week on Twitch.</h2>
  <ul class="days lg mt-s">
    <li data-day="1"><span class="dw dw-mint">Mon</span><p><b>Move Monday</b><span class="desc">20–60 minutes of mobility inside the stream. Bring a chair, a wall or a mat.</span></p></li>
    <li data-day="3"><span class="dw dw-pink">Wed</span><p><b>Cook with me</b><span class="desc">Recipes from Stream Day Kitchen, made live. Ask anything in chat.</span></p></li>
    <li data-day="5"><span class="dw dw-blue">Fri</span><p><b>Game night</b><span class="desc">Chill gaming, up to three hours, with a 2-minute stretch break every hour.</span></p></li>
    <li><span class="dw dw-lilac some">Sun</span><p><b>Chill Sunday</b><span class="desc">Some weeks: painting or recovery, announced on the day.</span></p></li>
  </ul>
  <p class="small muted mt-s">Exact times are on my <a href="{TWITCH}/schedule">Twitch schedule</a>.</p>
</section>

<section class="wrap block pt-s">
  <div class="duo">
    <div class="panel p-lilac">
      <p class="kicker">For subscribers</p>
      <h2>A monthly live mobility session</h2>
      <p>Once a month, subs get a 30-minute guided session just for them, with the recording in Discord afterwards. It's the best way to support the channel and get something useful back.</p>
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
    "Move Monday, Cook with me and Game night with a 2-minute stretch break every hour. Weekly schedule and subscriber sessions.",
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
    <!-- TODO: pune o poză cu tine în locul literelor KM: <div class="portrait"><img src="assets/kristine-about.jpg" alt="Kristine Maia"></div> -->
    <div class="portrait" aria-hidden="true">KM</div>
    <div class="prose">
      <p class="lead">I help people who sit all day move better, recover faster and eat well, without making it complicated.</p>
      <p>I've streamed on Twitch for five years and built a community of 72,000 people around the world. I studied sport and recovery: I hold a degree in Physical Education and Sport and I'm a certified recovery massage therapist, trained in recovery and sports massage and lymphatic drainage.</p>
      <p>On stream I train, cook, paint and play games. Over the years my chat kept telling me the same thing: stiff necks, sore wrists, tight hips, too much takeaway. So I started doing something about it live, two minutes at a time. That became Move Monday, Cook with me and the hourly stretch break on game night, and it's what everything on this site is built on.</p>
      <h2>What I am</h2>
      <ul class="creds">
        <li>Sports science graduate <span>(degree in Physical Education and Sport)</span></li>
        <li>Certified recovery massage therapist <span>(recovery &amp; sports massage, lymphatic drainage)</span></li>
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
    "Sports science graduate, certified recovery massage therapist and Twitch Partner helping people who sit all day.",
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
    <div class="stat"><strong>5 years</strong><span>streaming, 3–4 streams a week</span></div>
    <div class="stat"><strong>142K</strong><span>Instagram views in the last 30 days</span></div>
    <div class="stat"><strong>12.6K</strong><span>views on my jump-rope affiliate reel</span></div>
  </div>
</section>

<section class="wrap block">
  <div class="cols">
    <div><p class="kicker">Good fits</p><h2>What I promote</h2><ul><li>Ergonomics: desks, chairs, mice and keyboards</li><li>Recovery tools: massage guns, rollers, creams</li><li>Nutrition: quick meals, protein, healthy snacks</li><li>Sportswear, mats and training gear</li></ul><p class="small muted">I say no to anything that doesn't fit a health-focused audience.</p></div>
    <div><p class="kicker">Formats</p><h2>How we can work together</h2><ul><li>Sponsored segment inside Move Monday or Cook with me</li><li>Dedicated sponsored stream</li><li>Instagram reels package (2–4 reels)</li><li>Discount code for my community, tracked</li><li>Longer-term ambassador or advisory role</li></ul><p class="small muted">All sponsored content is clearly labelled.</p></div>
  </div>
  <div class="notice mt-m"><strong>Current partners:</strong> Dope Rope (jump ropes), Revu Natural (recovery creams) and Bewit (natural products), all with tracked discount codes for my community.</div>
</section>
"""
page(
    "brands.html",
    "Partnerships · Kristine Maia",
    "Partner with Kristine Maia: Twitch Partner with 72K followers and a health-focused audience of people who sit all day.",
    brands,
)


# =====================================================================
# 7. TERAPIE (terapie.html) · în română
# =====================================================================
terapie = """
<section class="wrap page-head">
  <p class="kicker">KM Wellness Concept</p>
  <h1>Masaj de <em>recuperare</em></h1>
  <p class="lead">Ședințe de masaj de recuperare și sportiv în București, în săptămânile anunțate pe <a href="{KM_INSTA}">@kmwellnessconcept</a>.</p>
  <p class="small muted">Licențiată în Educație Fizică și Sport · terapeut certificat în masaj de recuperare</p>
  <div class="actions"><a class="btn" href="{KM_INSTA}">Scrie-mi pe Instagram</a><a class="tl nw" href="tel:+40737071122">+40 737 071 122</a></div>
</section>

<section class="wrap pb-s" aria-labelledby="pret-title">
  <h2 class="sr" id="pret-title">Prețuri</h2>
  <div class="prices">
    <article class="panel p-pink"><h3>Masaj de recuperare pe zonă</h3><p class="p">250 lei</p><p class="muted">30–40 min · spate, cervical, lombar sau umeri.</p></article>
    <article class="panel p-blue"><h3>Masaj full body</h3><p class="p">500 lei</p><p class="muted">80–90 min · detensionare completă, de la cap până la picioare.</p></article>
    <article class="panel p-mint"><h3>Masaj capilar</h3><p class="p">200 lei</p><p class="muted">30–40 min · scalp, ceafă și umeri, pentru relaxare profundă.</p></article>
  </div>
</section>

<section class="wrap block pt-s">
  <div class="panel p-lilac narrow">
    <span class="tag">Pachet</span>
    <h2>4 ședințe pe zonă, plătite în avans</h2>
    <p>Valabil 12 luni de la plată, le programezi când îți convine. Include o evaluare video gratuită a mobilității.</p>
  </div>
  <div class="cols mt-m">
    <div><p class="kicker">Unde</p><h2>La tine acasă sau la o locație parteneră</h2><p class="muted">Vin cu masa și tot ce trebuie. Taxa de deplasare este de 50–100 lei, în funcție de zonă.</p></div>
    <div><p class="kicker">Programări</p><h2>Cum rezervi</h2><ul><li>Scrie-mi pe Instagram la <a href="{KM_INSTA}">@kmwellnessconcept</a> sau sună la <a class="nw" href="tel:+40737071122">+40 737 071 122</a>.</li><li>Plata se face în avans, prin transfer bancar sau link de plată.</li><li>Datele disponibile se anunță pe Instagram.</li></ul></div>
  </div>
  <p class="notice mt-m">Ședințele nu înlocuiesc un consult medical. Dacă ai o afecțiune sau o accidentare, discută întâi cu medicul.</p>
</section>
"""
page(
    "terapie.html",
    "KM Wellness Concept · Masaj de recuperare București",
    "Masaj de recuperare și sportiv în București, la domiciliu sau la o locație parteneră. Programări în săptămânile anunțate.",
    terapie,
    lang="ro",
    cur="none",
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
    <p class="muted">All content on this site, in my streams and in my products is general information about exercise, mobility and nutrition. It is not medical advice, diagnosis or treatment. I am a sports science graduate and certified recovery massage therapist, not a medical professional. If you have pain, an injury, a medical condition, are pregnant or take medication, talk to a doctor before starting any routine or changing your diet.</p>
    <h2>Privacy</h2>
    <p class="muted">If you join the email list, your email address is stored by my email provider [TODO: MailerLite / Kit] only to send you the free routine and updates. You can unsubscribe at any time with one click. If you buy something, your order is processed by [TODO: Payhip], which handles payment and delivery. This site does not use advertising cookies. Fonts are loaded from Google Fonts, so your browser sends your IP address to Google when a page loads. To ask about, correct or delete your data, email {EMAIL}.</p>
    <h2>Purchases</h2>
    <p class="muted">Digital products are delivered by email right after payment. [TODO: politica de retur, verificată de avocat: de exemplu, dreptul de retragere pentru conținut digital și momentul în care se pierde]. Online assessments can be rescheduled up to 24 hours before the call.</p>
    <h2>Affiliate links</h2>
    <p class="muted">Some links on this site are affiliate links. If you buy through them I may earn a small commission at no extra cost to you. Sponsored content is always labelled.</p>
  </div>
</section>
"""
page("legal.html", "Legal & Privacy · Kristine Maia", "Legal information, privacy and medical disclaimer.", legal, cur="none")

print("ok: 8 pages written to " + OUT)
