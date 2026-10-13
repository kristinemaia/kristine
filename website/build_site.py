import os
import os.path
OUT = os.path.dirname(os.path.abspath(__file__))

TWITCH = "https://www.twitch.tv/kristinemaia"
INSTA = "https://www.instagram.com/kristinemaia11/"
LINKTREE = "https://linktr.ee/kristinemaia"
KM_INSTA = "https://www.instagram.com/kmwellnessconcept/"
EMAIL = "kristinemaia527@gmail.com"
# TODO: înlocuiește cu linkurile reale când le ai
BOOK_ASSESSMENT = "#TODO-link-programare-si-plata"

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;600&family=Onest:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">'

NAV = [("index.html", "Home"), ("free.html", "Free routines"), ("shop.html", "Shop"), ("live.html", "Live"), ("about.html", "About"), ("brands.html", "For brands")]


def header(cur):
    items = "".join(
        '<li><a href="%s"%s>%s</a></li>' % (h, ' aria-current="page"' if h == cur else "", t) for h, t in NAV
    )
    return (
        '<a class="skip" href="#main">Skip to content</a>'
        '<header class="site-header"><nav class="nav container" aria-label="Main">'
        '<a class="brand" href="index.html">Kristine <span>Maia</span></a>'
        '<button class="menu-btn" aria-expanded="false" aria-controls="nav-links">Menu</button>'
        '<ul class="nav-links" id="nav-links">%s</ul></nav></header>' % items
    )


def footer(lang="en"):
    if lang == "ro":
        note = "Conținutul nu înlocuiește un consult medical."
    else:
        note = "Not medical advice. If you have pain or an injury, see a doctor or physiotherapist."
    return (
        '<footer class="site-footer"><div class="container"><div class="footer-grid">'
        '<div><a class="brand" href="index.html">Kristine <span>Maia</span></a>'
        '<p class="muted small" style="margin-top:10px;max-width:36ch">Mobility, recovery and good food for people who sit all day.</p></div>'
        '<div><h3>Start</h3><ul><li><a href="free.html">Free desk stretch</a></li><li><a href="shop.html">Shop</a></li><li><a href="live.html">Live schedule</a></li></ul></div>'
        '<div><h3>Follow</h3><ul><li><a href="%s">Twitch</a></li><li><a href="%s">Instagram</a></li><li><a href="%s">All links</a></li></ul></div>'
        '<div><h3>More</h3><ul><li><a href="about.html">About</a></li><li><a href="brands.html">For brands</a></li><li><a href="terapie.html" lang="ro">Terapie în București</a></li><li><a href="legal.html">Legal &amp; privacy</a></li></ul></div>'
        '</div><div class="legal-line"><span>&copy; <span id="year">2026</span> Kristine Maia</span><span>%s</span></div></div></footer>'
        % (TWITCH, INSTA, LINKTREE, note)
    )


def page(fname, title, desc, body, cur=None, lang="en"):
    html = (
        '<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        "<title>%s</title>\n<meta name=\"description\" content=\"%s\">\n"
        '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n'
        "%s\n<link rel=\"stylesheet\" href=\"assets/style.css\">\n</head>\n<body>\n%s\n<main id=\"main\">\n%s\n</main>\n%s\n"
        '<script src="assets/site.js"></script>\n</body>\n</html>\n'
        % (lang, title, desc, title, desc, FONTS, header(cur or fname), body, footer(lang))
    )
    with open(os.path.join(OUT, fname), "w") as f:
        f.write(html)


SIGNUP = """
<section class="section" id="newsletter"><div class="container"><div class="signup">
  <div class="prose">
    <p class="eyebrow">Free, in your inbox</p>
    <h2>The 5-minute desk stretch</h2>
    <p class="muted">A one-page routine you can do in your chair between meetings or matches. You also get new routines and first access to the 30-day program at the early price.</p>
  </div>
  <!-- TODO: înlocuiește formularul cu codul de embed din MailerLite sau Kit (vezi README) -->
  <form class="form" data-placeholder>
    <label for="email-%(id)s">Your email</label>
    <div class="form-row"><input type="email" id="email-%(id)s" name="email" placeholder="you@example.com" required autocomplete="email"><button class="btn" type="submit">Send me the stretch</button></div>
    <p class="small muted">No spam. Unsubscribe in one click.</p>
    <p class="form-msg" aria-live="polite"></p>
  </form>
</div></div></section>
"""

# ---------------- HOME ----------------
home = """
<section class="hero container">
  <div class="hero-copy">
    <p class="eyebrow">Mobility · Recovery · Good food</p>
    <h1>Unstiff after 8 hours in a chair.</h1>
    <p class="lead">Short routines, simple food and honest recovery advice for gamers, streamers and anyone who sits all day. From a sports science graduate and certified recovery massage therapist who does it all live.</p>
    <div class="cta-row"><a class="btn" href="free.html">Get the free 5-minute desk stretch</a><a class="btn ghost" href="%(tw)s">Watch live on Twitch</a></div>
  </div>
  <aside class="breaker" id="breaker" aria-label="60-second stretch break">
    <div class="breaker-top"><span>Stretch break</span><span>60 s</span></div>
    <div class="dial"><div class="dial-inner"><div><div class="dial-time">0:15</div><div class="dial-step">Move 1 of 4</div></div></div></div>
    <p class="move-name" aria-live="polite">Chin tucks</p>
    <p class="move-cue">Slide your chin straight back, like making a double chin. Slow, 5 times.</p>
    <div class="cta-row"><button class="btn small" data-start>Start 60 seconds</button><button class="btn small ghost" data-reset>Reset</button></div>
    <p class="breaker-note">The same break we take every hour on stream. Gentle range only, no pain.</p>
  </aside>
</section>

<section class="proof" aria-label="At a glance"><div class="container"><ul>
  <li><strong>72K</strong><span>followers on Twitch</span></li>
  <li><strong>Partner</strong><span>on Twitch, 5 years live</span></li>
  <li><strong>12.7K</strong><span>on Instagram</span></li>
  <li><strong>BSc</strong><span>Physical Education &amp; Sport</span></li>
  <li><strong>Certified</strong><span>recovery massage therapist</span></li>
</ul></div></section>

<section class="section"><div class="container">
  <div class="section-head"><p class="eyebrow">Start here</p><h2>Three steps, from free to fully guided</h2><p class="muted">Start with five minutes. Go further when you want more structure.</p></div>
  <div class="path">
    <article class="card"><span class="step">Step 1</span><span class="tag">Free</span><h3>5-minute desk stretch</h3><p class="muted">Neck, shoulders, wrists and hips, all from your chair. One page, printable.</p><div class="actions"><a class="btn small" href="free.html">Get it free</a></div></article>
    <article class="card"><span class="step">Step 2</span><span class="tag soon">2026 edition soon</span><h3>Stream Day Kitchen</h3><p class="muted">Quick recipes for long days at the desk, the hand-portion method (no scale needed) and a 7-day meal plan.</p><div class="actions"><a class="btn small ghost" href="shop.html#kitchen">See the e-book</a></div></article>
    <article class="card"><span class="step">Step 3</span><span class="tag soon">Waitlist</span><h3>Desk &amp; Gamer Mobility: 30 days</h3><p class="muted">Ten minutes a day for 30 days. Follow-along videos for the places that hurt after long sessions.</p><div class="actions"><a class="btn small ghost" href="shop.html#program">Join the waitlist</a></div></article>
  </div>
</div></section>

<section class="section" style="padding-top:0"><div class="container">
  <div class="section-head"><p class="eyebrow">Live on Twitch</p><h2>Every week, same rhythm</h2></div>
  <div class="schedule">
    <div class="slot"><span class="day">Monday</span><div><h3>Move Monday</h3><p>A live mobility session for neck, back, wrists and hips. Follow along from your chair or the floor.</p></div><a class="btn small ghost" href="%(tw)s">Follow</a></div>
    <div class="slot"><span class="day">Wednesday</span><div><h3>Cook with me</h3><p>Quick, healthy meals for long days, cooked live with chat.</p></div><a class="btn small ghost" href="%(tw)s">Follow</a></div>
    <div class="slot"><span class="day">Friday</span><div><h3>Game night</h3><p>Relaxed gaming with a 2-minute stretch break at the top of every hour.</p></div><a class="btn small ghost" href="%(tw)s">Follow</a></div>
  </div>
  <p class="small muted" style="margin-top:12px">Exact times are on my <a href="%(tw)s/schedule">Twitch schedule</a>.</p>
</div></section>

<section class="section" style="padding-top:0"><div class="container split">
  <div class="photo"><!-- TODO: pune o poză cu tine: <img src="assets/kristine.jpg" alt="Kristine Maia"> -->Your photo here<br>assets/kristine.jpg</div>
  <div class="prose">
    <p class="eyebrow">Hi, I'm Kristine</p>
    <h2>I sit for a living too</h2>
    <p class="muted">I've streamed for five years, and I trained in sport and recovery before that. My community kept telling me the same thing: their neck hurts, their wrists ache, they eat whatever is closest. So that's what we work on, together, a few minutes at a time.</p>
    <p><a href="about.html">More about me →</a></p>
  </div>
</div></section>
""" % {"tw": TWITCH} + SIGNUP % {"id": "home"}

page("index.html", "Kristine Maia · Mobility & Recovery",
     "Mobility, recovery and good food for gamers, streamers and anyone who sits all day. Free 5-minute desk stretch.",
     home)

# ---------------- FREE ----------------
free = """
<section class="container page-head">
  <p class="eyebrow">Free routines</p>
  <h1>Start with five minutes</h1>
  <p class="lead">Three short routines for the places that hurt most after long sessions. Move slowly, stay in a comfortable range and stop if anything feels sharp.</p>
</section>
""" + SIGNUP % {"id": "free"} + """
<section class="section" style="padding-top:0"><div class="container" style="display:grid;gap:56px">
  <article class="routine" id="neck">
    <div class="section-head" style="margin-bottom:0"><p class="eyebrow">Routine 1 · 3 minutes</p><h2>Neck after 4 hours of gaming</h2></div>
    <ol class="moves">
      <li><strong>Chin tucks</strong><span>Sit tall. Slide your chin straight back without tilting your head, hold 2 seconds, release.</span> <span class="dose">8 slow reps</span></li>
      <li><strong>Side neck stretch</strong><span>Drop one ear toward your shoulder. Hold the chair seat with the other hand to keep that shoulder down.</span> <span class="dose">20–30 s per side</span></li>
      <li><strong>Shoulder blade squeeze</strong><span>Pull your shoulder blades back and down, hold 3 seconds, release.</span> <span class="dose">10 reps</span></li>
    </ol>
  </article>
  <article class="routine" id="wrists">
    <div class="section-head" style="margin-bottom:0"><p class="eyebrow">Routine 2 · 3 minutes</p><h2>Wrists for mouse and keyboard</h2></div>
    <ol class="moves">
      <li><strong>Wrist flexor stretch</strong><span>Arm straight in front, palm up. Gently pull your fingers back with the other hand.</span> <span class="dose">20 s per hand</span></li>
      <li><strong>Wrist extensor stretch</strong><span>Arm straight, palm down. Gently press the back of your hand toward you.</span> <span class="dose">20 s per hand</span></li>
      <li><strong>Tendon glides</strong><span>Open hand, hook fist, full fist, flat fist, straight fingers. Move slowly through each shape.</span> <span class="dose">5 rounds</span></li>
    </ol>
  </article>
  <article class="routine" id="hips">
    <div class="section-head" style="margin-bottom:0"><p class="eyebrow">Routine 3 · 4 minutes</p><h2>Hips after a long stream</h2></div>
    <ol class="moves">
      <li><strong>Half-kneeling hip flexor stretch</strong><span>One knee down on a cushion. Squeeze the glute of the back leg and shift your hips forward a little.</span> <span class="dose">30 s per side</span></li>
      <li><strong>Seated figure-4</strong><span>Ankle on the opposite knee, sit tall, hinge forward slightly from the hips.</span> <span class="dose">30 s per side</span></li>
      <li><strong>Glute bridge</strong><span>On your back, knees bent. Push through your heels and lift your hips, pause at the top.</span> <span class="dose">10 slow reps</span></li>
    </ol>
  </article>
  <p class="notice">Not medical advice. These are general mobility exercises. If you have pain, an injury or a medical condition, check with a doctor or physiotherapist first.</p>
</div></section>
"""
page("free.html", "Free Desk Stretch Routines · Kristine Maia",
     "Free mobility routines for neck, wrists and hips after long hours at the desk, plus the 5-minute desk stretch PDF.", free)

# ---------------- SHOP ----------------
shop = """
<section class="container page-head">
  <p class="eyebrow">Shop</p>
  <h1>Programs, food and 1:1 help</h1>
  <p class="lead">Everything here is built for people who sit for long hours. Start small. You can always go further.</p>
</section>

<section class="section" style="padding-top:8px"><div class="container" style="display:grid;gap:40px">
  <div>
    <div class="section-head"><p class="eyebrow">Available now</p><h2>Work with me online</h2></div>
    <div class="path">
      <article class="card" id="assessment"><span class="tag">Book now</span><h3>Video mobility assessment</h3><p class="price">€55</p>
        <ul><li>30-minute video call</li><li>We look at how you sit, move and train</li><li>A written plan with 3–5 moves made for you</li></ul>
        <p class="small muted">Education and load management. Not a diagnosis or treatment.</p>
        <div class="actions"><a class="btn small" href="%(book)s">Book &amp; pay</a></div></article>
      <article class="card" id="twitch-sub"><span class="tag">On Twitch</span><h3>Subscriber mobility session</h3><p class="price">Twitch sub</p>
        <ul><li>A monthly live 30-minute mobility session for subs</li><li>Recordings in Discord</li><li>Every sub supports the channel directly</li></ul>
        <div class="actions"><a class="btn small ghost" href="%(tw)s">Subscribe on Twitch</a></div></article>
      <article class="card" id="classes"><span class="tag soon">Next dates soon</span><h3>Small-group live class</h3><p class="price">€12</p>
        <ul><li>45 minutes, 6–8 people</li><li>I see you and correct you live</li><li>Dates go to the email list first</li></ul>
        <div class="actions"><a class="btn small ghost" href="#newsletter">Get the dates</a></div></article>
    </div>
  </div>

  <div>
    <div class="section-head"><p class="eyebrow">Coming soon</p><h2>Digital products</h2></div>
    <div class="path two">
      <article class="card" id="kitchen"><span class="tag soon">2026 edition</span><h3>Stream Day Kitchen</h3><p class="price">€12</p>
        <ul><li>20 quick recipes, sorted by situation: before a long session, at the desk in 10 minutes, after the stream</li><li>The hand-portion method: eat well without a scale</li><li>Shopping list and a 7-day stream-day meal plan</li></ul>
        <div class="actions"><a class="btn small ghost" href="#newsletter">Tell me when it's out</a></div></article>
      <article class="card" id="program"><span class="tag soon">Waitlist</span><h3>Desk &amp; Gamer Mobility: 30 days</h3><p class="price">€39 <span class="small muted">· €29 for the email list</span></p>
        <ul><li>10 minutes a day, follow-along videos</li><li>Neck, upper back, wrists, hips and lower back</li><li>Watch on your phone, keep it forever</li></ul>
        <div class="actions"><a class="btn small" href="#newsletter">Join the waitlist</a></div></article>
    </div>
  </div>

  <div id="gear">
    <div class="section-head"><p class="eyebrow">Gear I actually use</p><h2>Discount codes</h2><p class="small muted">Affiliate links: I may earn a small commission at no extra cost to you. I only list things I use on stream.</p></div>
    <div class="path two">
      <article class="card"><h3>Jump rope</h3><p class="muted">My 5-minute warm-up before every gym session.</p><p class="dose">Code: [TODO-COD]</p><div class="actions"><a class="btn small ghost" href="#TODO-link-coarda">Shop the rope</a></div></article>
      <article class="card"><h3>Revu Natural</h3><p class="muted">Recovery creams I use after long streams and training.</p><p class="dose">Code: [TODO-COD]</p><div class="actions"><a class="btn small ghost" href="#TODO-link-revu">Shop Revu Natural</a></div></article>
    </div>
  </div>

  <div>
    <div class="section-head"><p class="eyebrow">Questions</p><h2>Before you buy</h2></div>
    <div class="faq">
      <details><summary>Is this physiotherapy or medical treatment?</summary><p>No. I'm a sports science graduate and a certified recovery massage therapist. Everything here is general exercise and education. If you have pain or an injury, see a doctor or physiotherapist.</p></details>
      <details><summary>Do I need equipment?</summary><p>A chair, a wall and a bit of floor space. Some routines use a resistance band, which is optional.</p></details>
      <details><summary>How do I get my product after paying?</summary><p>You get an email with your download or access link right after payment.</p></details>
      <details><summary>Refunds</summary><p>See the purchase terms on the <a href="legal.html">legal page</a>.</p></details>
    </div>
  </div>
</div></section>
""" % {"book": BOOK_ASSESSMENT, "tw": TWITCH} + SIGNUP % {"id": "shop"}
page("shop.html", "Shop · Kristine Maia",
     "Video mobility assessments, the Stream Day Kitchen e-book and the 30-day Desk & Gamer Mobility program.", shop)

# ---------------- LIVE ----------------
live = """
<section class="container page-head">
  <p class="eyebrow">Live on Twitch</p>
  <h1>Come hang out, then move</h1>
  <p class="lead">Five years live and 72K followers. The streams are relaxed, the chat is kind, and every hour we stand up for two minutes.</p>
  <div class="cta-row"><a class="btn" href="%(tw)s">Watch on Twitch</a><a class="btn ghost" href="%(tw)s/schedule">See the schedule</a></div>
</section>
<section class="section" style="padding-top:24px"><div class="container" style="display:grid;gap:40px">
  <div class="schedule">
    <div class="slot"><span class="day">Monday</span><div><h3>Move Monday</h3><p>20–60 minutes of mobility inside the stream. Bring a chair, a wall or a mat.</p></div><span class="tag">Mobility</span></div>
    <div class="slot"><span class="day">Wednesday</span><div><h3>Cook with me</h3><p>Recipes from Stream Day Kitchen, made live. Ask anything in chat.</p></div><span class="tag">Food</span></div>
    <div class="slot"><span class="day">Friday</span><div><h3>Game night</h3><p>Chill gaming, up to three hours, with a 2-minute stretch break every hour.</p></div><span class="tag">Gaming</span></div>
    <div class="slot"><span class="day">Sunday</span><div><h3>Chill Sunday (some weeks)</h3><p>Painting or recovery, announced on the day.</p></div><span class="tag soon">Bonus</span></div>
  </div>
  <div class="split" style="align-items:start">
    <div class="prose"><p class="eyebrow">For subscribers</p><h2>A monthly live mobility session</h2><p class="muted">Once a month, subs get a 30-minute guided session just for them, with the recording in Discord afterwards. It's the best way to support the channel and get something useful back.</p><p><a class="btn small" href="%(tw)s">Subscribe on Twitch</a></p></div>
    <div class="prose"><p class="eyebrow">Chat rules</p><h2>Kind, curious, on topic</h2><ul class="muted"><li>Be kind to each other and to me.</li><li>No sexual comments. Instant ban.</li><li>No personal questions about my private life.</li><li>Health questions are welcome, but I can't diagnose anyone. Not medical advice.</li></ul></div>
  </div>
</div></section>
""" % {"tw": TWITCH}
page("live.html", "Live on Twitch · Kristine Maia",
     "Move Monday, Cook with me and Game night with hourly stretch breaks. Weekly schedule and subscriber sessions.", live)

# ---------------- ABOUT ----------------
about = """
<section class="container page-head"><p class="eyebrow">About</p><h1>Hi, I'm Kristine</h1></section>
<section class="section" style="padding-top:8px"><div class="container split" style="align-items:start">
  <div class="photo"><!-- TODO: <img src="assets/kristine-about.jpg" alt="Kristine Maia"> -->Your photo here<br>assets/kristine-about.jpg</div>
  <div class="prose">
    <p class="lead">I help people who sit all day move better, recover faster and eat well, without making it complicated.</p>
    <p>I've streamed on Twitch for five years and built a community of 72,000 people around the world. Before and alongside that, I studied sport and recovery. I hold a degree in Physical Education and Sport and I'm a certified recovery massage therapist, trained in recovery and sports massage and lymphatic drainage. I also work with clients one-on-one in Bucharest.</p>
    <p>On stream I train, cook, paint and play games. Over the years my chat kept telling me the same thing: stiff necks, sore wrists, tight hips, too much takeaway. So I started doing something about it live, two minutes at a time. That became Move Monday, Cook with me and the hourly stretch break, and it's what everything on this site is built on.</p>
    <h2 style="font-size:24px;margin-top:8px">What I am and what I'm not</h2>
    <ul class="muted">
      <li>Sports science graduate (Physical Education and Sport)</li>
      <li>Certified recovery massage therapist</li>
      <li>Mobility and recovery coach</li>
      <li>I'm not a doctor or a physiotherapist, and nothing here is medical advice.</li>
    </ul>
    <p class="muted">Jimmy, my dog, lives with my parents and makes the occasional guest appearance.</p>
    <div class="cta-row"><a class="btn" href="free.html">Try the free routines</a><a class="btn ghost" href="%(tw)s">Watch live</a></div>
  </div>
</div></section>
""" % {"tw": TWITCH} + SIGNUP % {"id": "about"}
page("about.html", "About Kristine Maia",
     "Sports science graduate, certified recovery massage therapist and Twitch Partner helping people who sit all day.", about)

# ---------------- BRANDS ----------------
brands = """
<section class="container page-head">
  <p class="eyebrow">For brands</p>
  <h1>Reach people who sit all day</h1>
  <p class="lead">My audience games, streams and works long hours at a desk, and they want to feel better doing it. I partner with brands that genuinely help with that.</p>
  <div class="cta-row"><a class="btn" href="mailto:%(email)s?subject=Partnership">Email me</a><span class="muted small" style="align-self:center">%(email)s · media kit on request</span></div>
</section>
<section class="section" style="padding-top:24px"><div class="container" style="display:grid;gap:48px">
  <div class="stats">
    <div class="stat"><strong>72K</strong><span>Twitch followers · Partner</span></div>
    <div class="stat"><strong>125–230</strong><span>average live viewers per month (last 12 months)</span></div>
    <div class="stat"><strong>12.7K</strong><span>Instagram followers · 142K views in 30 days</span></div>
    <div class="stat"><strong>5 years</strong><span>streaming, 3–4 streams a week</span></div>
    <div class="stat"><strong>18–60</strong><span>international, English-speaking audience</span></div>
    <div class="stat"><strong>12.6K</strong><span>views on my jump-rope affiliate reel</span></div>
  </div>
  <div class="split" style="align-items:start">
    <div class="prose"><p class="eyebrow">Good fits</p><h2>What I promote</h2><ul class="muted"><li>Ergonomics: desks, chairs, mice and keyboards</li><li>Recovery tools: massage guns, rollers, creams</li><li>Nutrition: quick meals, protein, healthy snacks</li><li>Sportswear, yoga mats and training gear</li></ul><p class="small muted">I say no to anything that doesn't fit a health-focused audience.</p></div>
    <div class="prose"><p class="eyebrow">Formats</p><h2>How we can work together</h2><ul class="muted"><li>Sponsored segment inside Move Monday or Cook with me</li><li>Dedicated sponsored stream</li><li>Instagram reels package (2–4 reels)</li><li>Discount code for my community, tracked</li><li>Longer-term ambassador or advisory role</li></ul><p class="small muted">All sponsored content is clearly labelled.</p></div>
  </div>
  <div class="prose"><p class="eyebrow">Current partners</p><p class="muted">Revu Natural (recovery creams) and a jump rope brand, both through affiliate partnerships.</p></div>
</div></section>
""" % {"email": EMAIL}
page("brands.html", "Partnerships · Kristine Maia",
     "Partner with Kristine Maia: Twitch Partner with 72K followers and a health-focused audience of people who sit all day.", brands)

# ---------------- TERAPIE (RO) ----------------
terapie = """
<section class="container page-head">
  <p class="eyebrow">KM Wellness Concept · București</p>
  <h1>Masaj de recuperare</h1>
  <p class="lead">Ședințe de masaj de recuperare și sportiv în București, în săptămânile anunțate pe <a href="%(km)s">@kmwellnessconcept</a>.</p>
  <p class="small muted">Licențiată în Educație Fizică și Sport · terapeut certificat în masaj de recuperare și drenaj limfatic.</p>
</section>
<section class="section" style="padding-top:8px"><div class="container" style="display:grid;gap:40px">
  <div class="path">
    <article class="card"><h3>Masaj de recuperare pe zonă</h3><p class="price">250 lei</p><p class="muted">30–40 min · spate, cervical, lombar sau umeri.</p></article>
    <article class="card"><h3>Masaj full body</h3><p class="price">500 lei</p><p class="muted">80–90 min · detensionare completă, de la cap până la picioare.</p></article>
    <article class="card"><h3>Masaj capilar</h3><p class="price">200 lei</p><p class="muted">30–40 min · scalp, ceafă și umeri, pentru relaxare profundă.</p></article>
  </div>
  <div class="card" style="max-width:760px"><span class="tag">Pachet</span><h3>4 ședințe pe zonă, plătite în avans</h3><p class="muted">Valabil 12 luni, ca să le programezi când sunt în București. Include o evaluare video gratuită a mobilității.</p></div>
  <div class="split" style="align-items:start">
    <div class="prose"><p class="eyebrow">Unde</p><h2>La tine acasă sau la o locație parteneră</h2><p class="muted">Vin cu masa și tot ce trebuie. Taxa de deplasare este de 50–100 lei, în funcție de zonă.</p></div>
    <div class="prose"><p class="eyebrow">Programări</p><h2>Cum rezervi</h2><ul class="muted"><li>Scrie-mi pe Instagram la <a href="%(km)s">@kmwellnessconcept</a> sau sună la +40 737 071 122.</li><li>Plata se face în avans, prin transfer bancar sau link de plată.</li><li>Datele disponibile se anunță pe Instagram.</li></ul></div>
  </div>
  <p class="notice">Ședințele nu înlocuiesc un consult medical. Dacă ai o afecțiune sau o accidentare, discută întâi cu medicul.</p>
</div></section>
""" % {"km": KM_INSTA}
page("terapie.html", "KM Wellness Concept · Masaj de recuperare București",
     "Masaj de recuperare și sportiv în București, la domiciliu sau la locație parteneră. Programări în săptămânile anunțate.",
     terapie, cur="none", lang="ro")

# ---------------- LEGAL ----------------
legal = """
<section class="container page-head"><p class="eyebrow">Legal</p><h1>Legal &amp; privacy</h1>
<p class="notice">TODO: completează datele firmei și roagă avocatul sau contabila să verifice această pagină înainte de lansare.</p></section>
<section class="section" style="padding-top:8px"><div class="container prose">
  <h2 style="font-size:24px">Who runs this site</h2>
  <p class="muted">[TODO: denumirea firmei], CUI [TODO], [TODO: sediul], Romania. Contact: %(email)s.</p>
  <h2 style="font-size:24px">Not medical advice</h2>
  <p class="muted">All content on this site, in my streams and in my products is general information about exercise, mobility and nutrition. It is not medical advice, diagnosis or treatment. I am a sports science graduate and certified recovery massage therapist, not a doctor or physiotherapist. If you have pain, an injury, a medical condition, are pregnant or take medication, talk to a doctor before starting any routine or changing your diet.</p>
  <h2 style="font-size:24px">Privacy</h2>
  <p class="muted">If you join the email list, your email address is stored by my email provider [TODO: MailerLite / Kit] only to send you the free routine and updates. You can unsubscribe at any time with one click. If you buy something, your order is processed by [TODO: Payhip], which handles payment and delivery. This site does not use advertising cookies. To ask about, correct or delete your data, email %(email)s.</p>
  <h2 style="font-size:24px">Purchases</h2>
  <p class="muted">Digital products are delivered by email right after payment. [TODO: politica de retur, verificată de avocat: de exemplu, dreptul de retragere pentru conținut digital și momentul în care se pierde]. Online assessments can be rescheduled up to 24 hours before the call.</p>
  <h2 style="font-size:24px">Affiliate links</h2>
  <p class="muted">Some links on this site are affiliate links. If you buy through them I may earn a small commission at no extra cost to you. Sponsored content is always labelled.</p>
</div></section>
""" % {"email": EMAIL}
page("legal.html", "Legal & Privacy · Kristine Maia", "Legal information, privacy and medical disclaimer.", legal, cur="none")
print("ok")
