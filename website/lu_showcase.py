# Vitrina Level Up: videoul de lansare într-un telefon, două capturi din program, ce primești și butoanele.
# kind: "home", "shop" sau "training". {BUY} se completează în build_site.fill().

HEAD = {
    "home": ("New · now open", "Level Up your body, <em>step by step</em>"),
    "shop": ("Now open · founding price", "Level Up: your custom program"),
    "training": ("What you get", "Inside <em>Level Up</em>"),
}


def lu_showcase(kind):
    kicker, title = HEAD[kind]
    if kind == "shop":
        price = '<p class="lu-price">$10<small>/month · founding price for the first 50 members · cancel anytime</small></p>'
        btns = '<a class="btn" href="{BUY}">Join Level Up</a> <a class="btn alt" href="training.html#quiz">Take the 2-minute quiz first</a>'
        note = '<p class="small muted">Payment and your account are on Payhip; your workouts open on this site.</p>'
    elif kind == "home":
        price = '<p class="lu-price lu-soft">Founding spots for the first 50 members</p>'
        btns = '<a class="btn" href="training.html#quiz">Take the 2-minute quiz</a> <a class="btn alt" href="training.html#inside">See what\'s inside</a>'
        note = ''
    else:
        price = '<p class="lu-price lu-soft">Founding spots for the first 50 members</p>'
        btns = '<a class="btn" href="#quiz">Build my plan</a>'
        note = ''
    sid = "inside" if kind == "training" else "level-up"
    return f'''
<section class="lu" id="{sid}" aria-labelledby="lu-{kind}"><div class="wrap lu-grid">
  <div class="lu-media">
    <div class="lu-phone"><video src="assets/video/level-up.mp4" poster="assets/video/level-up-poster.jpg" muted loop playsinline autoplay preload="metadata" aria-label="Level Up: a short look at the program"></video></div>
    <img class="lu-shot lu-s1" src="assets/level-up-timer.jpg" alt="The program on a phone: an exercise with its timer" loading="lazy" width="390" height="844">
    <img class="lu-shot lu-s2" src="assets/level-up-rest.jpg" alt="The program on a phone: the rest timer between sets" loading="lazy" width="390" height="844">
  </div>
  <div class="lu-text">
    <p class="kicker">{kicker}</p><h2 id="lu-{kind}">{title}</h2>
    <p class="lead">Stronger, leaner or less stiff: a 2-minute quiz builds your week, gym or home, and every workout opens on your phone, step by step.</p>
    <ul class="lu-list">
      <li><b>🎯 Your plan from the quiz</b><span>Your goal, your time, gym or home, 2 to 4 days a week.</span></li>
      <li><b>🎥 Every exercise on video</b><span>Filmed by me, with how to do it and a timer for your rests and holds.</span></li>
      <li><b>📈 Your weights, saved</b><span>See what you lifted last time and when to go up.</span></li>
      <li><b>🗓 4-week blocks</b><span>A little harder each week, then a lighter week to recover.</span></li>
      <li><b>🌍 In your language</b><span>English, Română, Español, Deutsch, Français, Türkçe.</span></li>
    </ul>
    {price}<div class="row-btns">{btns}</div>{note}
  </div>
</div></section>
'''
