#!/usr/bin/env python3
"""
Generează 5-minute-desk-stretch.html (A4, 3 pagini) pentru PDF-ul gratuit.

Pagina 1 = afișul de 5 minute (se poate printa separat).
Pagina 2 = cum faci bine fiecare mișcare.
Pagina 3 = cum îl faci obicei: versiuni scurte, momente, fișă de 7 zile, ce urmează.

- Textul din PDF e în secțiunea ROWS de mai jos. Îl poți edita direct.
- Imaginile: dacă pui o poză pătrată în folderul `photos/` cu unul din numele
  neck.jpg, shoulders.jpg, wrists.jpg, hips.jpg, ea înlocuiește automat
  ilustrația desenată pentru acel rând.
- Apoi rulezi:  python3 build_pdf.py   și   node print_pdf.js
  (print_pdf.js transformă HTML-ul în PDF cu Chromium/Playwright).
"""
import base64
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(HERE, "photos")
OUT_HTML = os.path.join(HERE, "5-minute-desk-stretch.html")

# ---------------------------------------------------------------------
# Textul PDF-ului (engleză, pentru publicul internațional)
# ---------------------------------------------------------------------
TITLE_KICKER = "Free guide · Kristine Maia"
SUBTITLE = "Four spots. One chair. No equipment."
INTRO = (
    "Neck, shoulders, wrists and hips: the places a long day of sitting hits first. "
    "Start a 5-minute timer, move slowly and keep every stretch gentle. "
    "A comfortable pull is right. Sharp pain is a stop sign."
)

ROWS = [
    {
        "key": "neck", "tone": "pink", "title": "Neck", "time": "1:20",
        "moves": [
            ("Chin tucks", "Sit tall and glide your chin straight back, like a gentle double chin. Hold 2 seconds.", "8 slow reps"),
            ("Side neck stretch", "Ear toward shoulder. Hold the chair seat with the other hand to keep that shoulder down.", "20 s each side"),
        ],
    },
    {
        "key": "shoulders", "tone": "blue", "title": "Shoulders", "time": "1:00",
        "moves": [
            ("Shoulder rolls", "Lift, roll back and let the shoulders melt down. Big, slow circles, backwards only.", "8 rolls"),
            ("Shoulder blade squeeze", "Pull your shoulder blades back and down, hold 3 seconds, release.", "8 reps"),
        ],
    },
    {
        "key": "wrists", "tone": "mint", "title": "Wrists", "time": "1:10",
        "moves": [
            ("Palm-up stretch", "Arm straight, palm up. Gently pull the fingers back with your other hand.", "15 s each hand"),
            ("Palm-down stretch", "Arm straight, palm down. Gently press the back of the hand toward you.", "15 s each hand"),
            ("Tendon glides", "Open hand, hook fist, full fist, flat fist, straight fingers. Slowly, one shape at a time.", "3 rounds"),
        ],
    },
    {
        "key": "hips", "tone": "lilac", "title": "Hips &amp; back", "time": "1:30",
        "moves": [
            ("Seated figure-4", "Ankle on the opposite knee. Sit tall and hinge forward a little until you feel the hip.", "30 s each side"),
            ("Seated twist", "Hold the chair back and turn gently, starting from your upper back.", "15 s each side"),
        ],
    },
]

FOOT_LEFT_TITLE = "Keep going"
FOOT_LEFT = (
    "Free routines, the 30-day Desk &amp; Gamer Mobility waitlist and my live schedule: "
    "<b>linktr.ee/kristinemaia</b><br>Twitch: twitch.tv/kristinemaia · Instagram: @kristinemaia11"
)
FOOT_RIGHT_TITLE = "Hi, I'm Kristine"
FOOT_RIGHT = (
    "Sports science graduate, certified recovery massage therapist and mobility &amp; recovery coach. "
    "<b>Not medical advice.</b> This is general mobility. If you have pain, an injury or a medical "
    "condition, check with a doctor first, and stop if anything feels sharp."
)

# ---------------------------------------------------------------------
# Pagina 2: cum faci bine fiecare mișcare (în aceeași ordine ca în ROWS)
# fiecare tuplu: (cum o faci, ce simți, varianta mai blândă)
# ---------------------------------------------------------------------
P2_KICKER = "Page 2 · The details"
P2_TITLE = "Do each move well"
P2_SUB = "Slow and gentle beats big and fast."
P2_BADGE = ("9", "moves explained")
P2_INTRO = (
    "Page 1 is the routine. This page shows how to do each move well."
)
DETAIL = {
    "neck": [
        ("Sit tall. Slide your chin straight back, as if making a double chin. Keep your head level. Hold 2 seconds, then release.",
         "A light stretch at the back of your neck.",
         "Fewer reps and a smaller glide."),
        ("Hold the seat with your right hand. Let your left ear drift toward your left shoulder. Then switch sides.",
         "A stretch along the side of the neck that is holding the chair.",
         "Tilt less. Let the weight of your head do the work, no pulling."),
    ],
    "shoulders": [
        ("Lift your shoulders toward your ears, roll them back, then let them melt down. Big, slow circles, backwards only.",
         "Your shoulders loosening up with each circle.",
         "Smaller circles."),
        ("Pull your shoulder blades back and down, as if tucking them into your back pockets. Hold 3 seconds. Keep your neck long.",
         "The work between your shoulder blades, not in your neck.",
         "Hold for 1 to 2 seconds."),
    ],
    "wrists": [
        ("Arm straight, palm up. With your other hand, gently pull the fingers back toward the floor.",
         "A stretch along the inside of your forearm. No pain, no tingling.",
         "Bend the elbow a little and pull less."),
        ("Arm straight, palm down. Gently press the back of the hand toward you, fingers pointing down.",
         "A stretch along the top of your forearm.",
         "Bend the elbow and press less."),
        ("Straight hand, hook fist, full fist, flat fist, straight again. One shape at a time, like playing the keyboard in slow motion.",
         "Smooth, easy movement. Never forced.",
         "One hand at a time, slower."),
    ],
    "hips": [
        ("Cross one ankle over the opposite knee and flex your foot. Sit tall, then hinge forward from the hips until you feel it.",
         "A stretch in the outer hip and glute.",
         "Stay upright. A small lean is enough."),
        ("Hold the chair back with one hand and your opposite knee with the other. Turn gently, starting from your upper back.",
         "A mild turn through your upper and mid back. Keep breathing.",
         "Turn less and keep your breathing easy."),
    ],
}
P2_RULES_TITLE = "Three rules for every move"
P2_RULES = [
    ("Breathe slowly.", "Let the breath out as you go a little deeper."),
    ("Stop before it hurts.", "A comfortable pull is right. Sharp pain is a stop sign."),
    ("Both sides, same effort.", "Keep your shoulders relaxed and your jaw soft."),
]

# ---------------------------------------------------------------------
# Pagina 3: cum îl faci obicei
# ---------------------------------------------------------------------
P3_KICKER = "Page 3 · Make it stick"
P3_TITLE = "Make it a habit"
P3_SUB = "Short and often is easier to keep than long and rare."
P3_BADGE = ("7", "day check-in")
P3_SHORT = [
    {"tone": "pink", "title": "The 1-minute reset", "time": "1:00",
     "moves": ["Chin tucks, 4 slow reps", "Shoulder rolls, 4 backwards", "Palm-up stretch, 8 s each hand", "Seated twist, 8 s each side"],
     "note": "For the gap between two matches."},
    {"tone": "blue", "title": "The 2-minute version", "time": "2:00",
     "moves": ["Chin tucks, 6 slow reps", "Side neck stretch, 10 s each side", "Shoulder rolls, 6 backwards",
               "Palm-up and palm-down stretch, 10 s each hand", "Seated figure-4, 10 s each side"],
     "note": "For the top of the hour."},
]
P3_WHEN_TITLE = "When to do it"
P3_WHEN_SUB = "Pick one trigger and keep it for a week."
P3_WHEN = [
    "After every match, queue or meeting",
    "At the top of each hour, with a repeating timer",
    "Before you start a stream or a work block",
    "Any time your neck or hands feel stuck",
]
P3_CHECK_TITLE = "Your 7-day check-in"
P3_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
P3_CHECK_ROWS = ["5-minute routine", "1-minute reset"]
P3_RATE_TITLE = "How tight does it feel? 0 is not at all, 10 is very tight."
P3_RATE_ROWS = ["Neck &amp; shoulders", "Wrists", "Hips &amp; back"]
P3_NOTES_TITLE = "What I noticed"
P3_RATE_NOTE = "Write your numbers on day 1 and day 7. On day 1 of my 30-day program you rate them again."
P3_NEXT_TITLE = "What's next"
P3_NEXT = (
    "I'm filming a 30-day Desk &amp; Gamer Mobility program: 10 minutes a day, mostly from your chair. "
    "You're on the list, so you'll hear first when it's ready. "
    "Tell me which spot feels worst by replying to my email. It shapes what I make next."
    "<br><b>linktr.ee/kristinemaia</b> · twitch.tv/kristinemaia · @kristinemaia11"
)
P3_STOP_TITLE = "Stop signs"
P3_STOP = (
    "Stop if you feel sharp pain, numbness, tingling or dizziness. If it does not settle, check with a doctor. "
    "<b>Not medical advice.</b> This is general mobility. If you have pain, an injury or a medical condition, "
    "check with a doctor first."
    "<br>Kristine Maia · sports science graduate · certified recovery massage therapist · mobility &amp; recovery coach"
)
FOOTLINE = "The 5-minute desk stretch · Kristine Maia · linktr.ee/kristinemaia"


# ---------------------------------------------------------------------
# Ilustrații simple (stil „pictogramă”), folosite până ai pozele tale
# ---------------------------------------------------------------------
INK = "#2B2431"
BERRY = "#8A3459"
SOFT = "#B7A6DA"      # scaun, podea
PINK2 = "#F1C3D6"

DEFS = (
    '<defs><marker id="ah%(i)s" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="3.3" markerHeight="3.3" orient="auto-start-reverse">'
    '<path d="M1 1 L9 5 L1 9 Z" fill="' + BERRY + '"/></marker></defs>'
)


def svg_wrap(inner, i):
    return (
        '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true">'
        + DEFS % {"i": i} + inner + "</svg>"
    )


def art_neck():
    """Profil, așezat: capul din față (fantomă) vine înapoi, stivuit peste umeri."""
    return svg_wrap(
        f'<line x1="10" y1="111" x2="110" y2="111" stroke="{SOFT}" stroke-width="3" stroke-linecap="round"/>'
        f'<g stroke="{SOFT}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none">'
        '<path d="M20 86 L62 86"/><path d="M20 86 L20 52"/><path d="M24 86 L24 110"/><path d="M58 86 L58 110"/></g>'
        f'<g stroke="{INK}" stroke-linecap="round" stroke-linejoin="round" fill="none">'
        '<path d="M42 86 L42 56" stroke-width="13"/><path d="M42 86 L80 86" stroke-width="9"/>'
        '<path d="M80 86 L80 109" stroke-width="9"/><path d="M80 109 L94 109" stroke-width="8"/>'
        '<path d="M42 58 L50 76 L68 76" stroke-width="6"/><path d="M42 54 L42 44" stroke-width="7"/></g>'
        f'<circle cx="68" cy="34" r="10" fill="none" stroke="{SOFT}" stroke-width="3" stroke-dasharray="4 5"/>'
        f'<circle cx="42" cy="33" r="10" fill="{INK}"/>'
        f'<path d="M50.5 31 L55 34 L50.5 37" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M72 13 L46 13" stroke="{BERRY}" stroke-width="4.5" stroke-linecap="round" fill="none" marker-end="url(#ah0)"/>',
        0,
    )


def art_shoulders():
    """Din față: rotiri ale umerilor (săgeți circulare) de o parte și de alta."""
    return svg_wrap(
        f'<g fill="{INK}" stroke="{INK}" stroke-linejoin="round" stroke-linecap="round">'
        '<path d="M42 54 Q60 46 78 54 L74 100 Q60 104 46 100 Z" stroke-width="6"/>'
        '<path d="M60 40 L60 50" stroke-width="9" fill="none"/>'
        '<path d="M40 58 L31 94" stroke-width="9" fill="none"/><path d="M80 58 L89 94" stroke-width="9" fill="none"/>'
        '<circle cx="60" cy="29" r="12" stroke="none"/></g>'
        f'<g stroke="{BERRY}" stroke-width="4.5" stroke-linecap="round" fill="none">'
        '<path d="M14 52 A10 10 0 1 1 24 62" marker-end="url(#ah1)"/>'
        '<path d="M106 52 A10 10 0 1 0 96 62" marker-end="url(#ah1)"/></g>',
        1,
    )


def art_wrists():
    """Din lateral: antebrațul cu palma în sus, degetele trase în jos de cealaltă mână."""
    return svg_wrap(
        f'<path d="M6 54 L56 58 L56 73 L6 77 Z" fill="{INK}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
        f'<path d="M14 57 L50 60" stroke="{PINK2}" stroke-width="5" stroke-linecap="round"/>'
        f'<rect x="52" y="54" width="38" height="19" rx="9.5" fill="{INK}" transform="rotate(50 58 64)"/>'
        f'<rect x="84" y="82" width="34" height="14" rx="7" fill="{INK}" opacity="0.5" transform="rotate(-38 88 90)"/>'
        f'<path d="M96 56 Q112 74 98 96" stroke="{BERRY}" stroke-width="4.5" stroke-linecap="round" fill="none" marker-end="url(#ah2)"/>',
        2,
    )


def art_hips():
    """Profil, așezat: figura 4 (glezna pe genunchiul opus), aplecare ușoară înainte."""
    return svg_wrap(
        f'<line x1="10" y1="111" x2="110" y2="111" stroke="{SOFT}" stroke-width="3" stroke-linecap="round"/>'
        f'<g stroke="{SOFT}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none">'
        '<path d="M18 88 L62 88"/><path d="M18 88 L18 54"/><path d="M22 88 L22 110"/><path d="M58 88 L58 110"/></g>'
        f'<circle cx="40" cy="85" r="10" fill="{PINK2}"/>'
        f'<g stroke="{INK}" stroke-linecap="round" stroke-linejoin="round" fill="none">'
        '<path d="M42 86 L52 56" stroke-width="13"/><path d="M52 54 L55 44" stroke-width="7"/>'
        '<path d="M42 86 L84 86" stroke-width="9"/><path d="M84 86 L84 109" stroke-width="9"/><path d="M84 109 L98 109" stroke-width="8"/></g>'
        f'<g stroke="{BERRY}" stroke-linecap="round" stroke-linejoin="round" fill="none">'
        '<path d="M42 84 L66 68" stroke-width="9"/><path d="M66 68 L86 80" stroke-width="8"/><path d="M86 80 L96 74" stroke-width="7"/></g>'
        f'<circle cx="57" cy="34" r="10" fill="{INK}"/>'
        f'<path d="M30 66 Q32 46 46 38" stroke="{BERRY}" stroke-width="4.5" stroke-linecap="round" fill="none" marker-end="url(#ah3)"/>',
        3,
    )


ART = {"neck": art_neck, "shoulders": art_shoulders, "wrists": art_wrists, "hips": art_hips}


def picture(key):
    """Poza ta, dacă există în photos/, altfel ilustrația."""
    for ext in ("jpg", "jpeg", "png"):
        p = os.path.join(PHOTOS, f"{key}.{ext}")
        if os.path.exists(p):
            mime = "image/png" if ext == "png" else "image/jpeg"
            data = base64.b64encode(open(p, "rb").read()).decode()
            return f'<img src="data:{mime};base64,{data}" alt="">'
    return ART[key]()


# ---------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------
CSS = """
@page{size:A4;margin:0}
:root{
  --bg:#FFF9F6;--ink:#2B2431;--muted:#5C5466;--line:#EADFE6;
  --pink:#F8DCE6;--pink2:#F1C3D6;--berry:#8A3459;
  --blue:#DDE9F7;--blue-ink:#2F5A86;--mint:#D8F0E4;--mint-ink:#1F6B52;--lilac:#E9E1F7;--lilac-ink:#4E3D7A;
  --display:"Bricolage Grotesque","Trebuchet MS",Arial,sans-serif;
  --body:"Figtree","Segoe UI",Arial,sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;padding:12mm 13mm 11mm;display:flex;flex-direction:column;gap:4mm;background:var(--bg);overflow:hidden}
.head{display:flex;justify-content:space-between;align-items:flex-start;gap:8mm}
.kicker{margin:0 0 2mm;font-size:8.5pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--berry)}
h1{margin:0;font-family:var(--display);font-weight:800;font-size:34pt;line-height:1.02;letter-spacing:-.02em}
.hl{background:linear-gradient(transparent 58%,var(--pink2) 58%);padding:0 1mm;margin:0 -1mm}
.sub{margin:2.5mm 0 0;font-size:12pt;font-weight:600;color:var(--blue-ink)}
.badge{flex:none;width:30mm;height:30mm;border-radius:50%;background:var(--berry);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;line-height:1}
.badge span{font-family:var(--display);font-weight:800;font-size:23pt;letter-spacing:-.02em}
.badge small{margin-top:1.5mm;font-size:6.5pt;font-weight:600;letter-spacing:.06em;text-transform:uppercase;opacity:.9}
.intro{margin:0;font-size:9.6pt;line-height:1.45;color:var(--muted);max-width:158mm}
.rows{display:flex;flex-direction:column;gap:3.4mm;flex:1;min-height:0}
.row{flex:1;min-height:0;display:grid;grid-template-columns:38mm 1fr;gap:5mm;padding:3mm;border-radius:6mm;align-items:stretch}
.row.pink{background:var(--pink)} .row.blue{background:var(--blue)} .row.mint{background:var(--mint)} .row.lilac{background:var(--lilac)}
.pic{margin:0;border-radius:4.5mm;background:#fff;overflow:hidden;display:flex;align-items:center;justify-content:center}
.pic svg,.pic img{width:100%;height:100%;object-fit:cover;display:block}
.pic svg{padding:1.5mm}
.body{display:flex;flex-direction:column;justify-content:center;min-width:0;gap:1.6mm}
.rhead{display:flex;align-items:center;gap:2.5mm}
.num{width:6.4mm;height:6.4mm;border-radius:50%;background:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:8.5pt}
.pink .num,.pink h2{color:var(--berry)} .blue .num,.blue h2{color:var(--blue-ink)} .mint .num,.mint h2{color:var(--mint-ink)} .lilac .num,.lilac h2{color:var(--lilac-ink)}
h2{margin:0;font-family:var(--display);font-weight:800;font-size:15pt;letter-spacing:-.01em;line-height:1}
.time{margin-left:auto;background:#fff;border-radius:99px;padding:.9mm 3mm;font-weight:700;font-size:9pt;font-variant-numeric:tabular-nums}
ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:1.7mm}
li{font-size:8.9pt;line-height:1.3}
li p{margin:.4mm 0 0}
.mv{display:flex;align-items:center;gap:2mm}
li b{font-weight:700;font-size:9.6pt}
li i{font-style:normal;background:#fff;border-radius:99px;padding:.1mm 2.2mm;font-weight:700;font-size:7.6pt;white-space:nowrap}
.foot{display:grid;grid-template-columns:1fr 1.25fr;gap:5mm;align-items:stretch}
.box{border-radius:5mm;padding:3.6mm 4.2mm;font-size:7.9pt;line-height:1.42}
.box h3{margin:0 0 1.2mm;font-family:var(--display);font-size:10.5pt;font-weight:800}
.box.a{background:var(--berry);color:#fff} .box.a b{color:#fff}
.box.b{border:1.2px solid var(--line);background:#fff;color:var(--muted)} .box.b b{color:var(--ink)}
.page{break-after:page;page-break-after:always} .page:last-child{break-after:auto;page-break-after:auto}
.pink{--zone:var(--berry)} .blue{--zone:var(--blue-ink)} .mint{--zone:var(--mint-ink)} .lilac{--zone:var(--lilac-ink)}
.head.sm h1{font-size:25pt}
.head.sm .badge{width:25mm;height:25mm}
.head.sm .badge span{font-size:20pt}
.head.sm .badge small{font-size:6pt;max-width:19mm}
.dcards{display:flex;flex-direction:column;gap:2.6mm}
.dcard{display:grid;grid-template-columns:27mm 1fr;gap:4mm;padding:2.6mm 3mm;border-radius:5mm;align-items:start}
.dcard .pic{width:27mm;height:27mm;border-radius:4mm}
.dcard.pink{background:var(--pink)} .dcard.blue{background:var(--blue)} .dcard.mint{background:var(--mint)} .dcard.lilac{background:var(--lilac)}
.dmain{display:flex;flex-direction:column;gap:1.8mm;min-width:0}
.dmoves{display:grid;gap:4.5mm;grid-template-columns:repeat(var(--n),minmax(0,1fr))}
.dm{font-size:8.1pt;line-height:1.34;min-width:0}
.dm .mv{margin-bottom:1.1mm;flex-wrap:wrap;gap:1mm 2mm}
.dm b{font-size:9.2pt}
.dm p{margin:0 0 1mm}
.lab{font-size:6.3pt;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--zone);margin-right:1mm}
.rules{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;border:1.2px solid var(--line);background:#fff;border-radius:5mm;padding:3.2mm 4.2mm}
.rules h3{grid-column:1/-1;margin:0;font-family:var(--display);font-size:10.5pt;font-weight:800}
.rules p{margin:0;font-size:8.2pt;line-height:1.38;color:var(--muted)} .rules b{display:block;color:var(--ink);font-size:9pt;margin-bottom:.6mm}
.p3{gap:5mm}
.footline{margin-top:auto;display:flex;justify-content:space-between;font-size:7.2pt;color:var(--muted);padding-top:1mm}
.two{display:grid;grid-template-columns:1fr 1fr;gap:4mm}
.scard{border-radius:5mm;padding:3.4mm 4.2mm;display:flex;flex-direction:column;gap:1.8mm}
.scard.pink{background:var(--pink)} .scard.blue{background:var(--blue)} .scard.mint{background:var(--mint)} .scard.lilac{background:var(--lilac)}
.scard h2{font-size:13pt;color:var(--zone)}
.scard ul{gap:1mm}
.scard li{font-size:8.6pt;line-height:1.3;padding-left:3.6mm;position:relative}
.scard li:before{content:"";position:absolute;left:0;top:1.35mm;width:1.7mm;height:1.7mm;border-radius:50%;background:var(--zone)}
.scard .note{margin:auto 0 0;font-size:8pt;color:var(--muted);padding-top:1mm}
.when{display:grid;grid-template-columns:30mm 1fr;gap:4mm;align-items:center}
.when h2{font-size:13pt;color:var(--zone)} .when p{margin:1mm 0 0;font-size:8.2pt;color:var(--muted);line-height:1.3}
.chips{display:flex;flex-wrap:wrap;gap:1.8mm}
.chips span{background:#fff;border-radius:99px;padding:1.2mm 3.2mm;font-size:8.3pt;font-weight:600}
.check{display:flex;flex-direction:column;gap:2.6mm}
.check h2{font-size:13pt;color:var(--zone)}
.grid7{display:grid;grid-template-columns:30mm repeat(7,1fr);gap:1.4mm 1.8mm;align-items:center;font-size:8.4pt}
.grid7 .d{text-align:center;font-weight:700;font-size:7.6pt;letter-spacing:.06em;text-transform:uppercase;color:var(--zone)}
.grid7 .r{font-weight:600}
.box7{height:6.4mm;border-radius:1.6mm;background:#fff;border:1px solid rgba(43,36,49,.28)}
.rate{display:grid;grid-template-columns:30mm 22mm 22mm 1fr;gap:1.6mm 3mm;align-items:center;font-size:8.4pt}
.rate .h{font-weight:700;font-size:7.6pt;letter-spacing:.06em;text-transform:uppercase;color:var(--zone)}
.rate .line{height:6.4mm;border-radius:1.6mm;background:#fff;border:1px solid rgba(43,36,49,.28)}
.rnote{margin:0;font-size:8pt;color:var(--muted);line-height:1.35}
.subq{margin:0;font-size:8.6pt;font-weight:600}
.notes{display:flex;flex-direction:column;gap:2.6mm;padding-top:1mm}
.notes span{display:block;height:5.4mm;border-bottom:1px solid rgba(43,36,49,.3)}
"""


def E(t):
    return html.escape(t, quote=False)


def page1():
    rows = []
    for n, r in enumerate(ROWS, 1):
        lis = "".join(
            f'<li><div class="mv"><b>{html.escape(name)}</b><i>{html.escape(dose)}</i></div><p>{html.escape(text)}</p></li>'
            for name, text, dose in r["moves"]
        )
        rows.append(
            f'<article class="row {r["tone"]}"><figure class="pic">{picture(r["key"])}</figure>'
            f'<div class="body"><div class="rhead"><span class="num">{n}</span><h2>{r["title"]}</h2>'
            f'<span class="time">{r["time"]}</span></div><ul>{lis}</ul></div></article>'
        )
    return f"""<div class="page">
<header class="head"><div><p class="kicker">{TITLE_KICKER}</p><h1>The 5-minute <span class="hl">desk</span> stretch</h1><p class="sub">{SUBTITLE}</p></div>
<div class="badge"><span>5:00</span><small>Start the timer</small></div></header>
<p class="intro">{INTRO}</p>
<section class="rows">{''.join(rows)}</section>
<footer class="foot"><div class="box a"><h3>{FOOT_LEFT_TITLE}</h3>{FOOT_LEFT}</div><div class="box b"><h3>{FOOT_RIGHT_TITLE}</h3>{FOOT_RIGHT}</div></footer>
</div>"""


def small_head(kicker, title, sub, badge):
    return (
        f'<header class="head sm"><div><p class="kicker">{E(kicker)}</p><h1>{E(title)}</h1><p class="sub">{E(sub)}</p></div>'
        f'<div class="badge"><span>{badge[0]}</span><small>{E(badge[1])}</small></div></header>'
    )


def page2():
    cards = []
    for r in ROWS:
        det = DETAIL[r["key"]]
        assert len(det) == len(r["moves"]), r["key"]
        moves = []
        for (name, _text, dose), (how, feel, gentler) in zip(r["moves"], det):
            moves.append(
                f'<div class="dm"><div class="mv"><b>{E(name)}</b><i>{E(dose)}</i></div>'
                f'<p><span class="lab">How</span>{E(how)}</p>'
                f'<p><span class="lab">Feel</span>{E(feel)}</p>'
                f'<p><span class="lab">Gentler</span>{E(gentler)}</p></div>'
            )
        cards.append(
            f'<article class="dcard {r["tone"]}"><figure class="pic">{picture(r["key"])}</figure>'
            f'<div class="dmain"><div class="rhead"><h2>{r["title"]}</h2><span class="time">{r["time"]}</span></div>'
            f'<div class="dmoves" style="--n:{len(moves)}">{"".join(moves)}</div></div></article>'
        )
    rules = "".join(f"<p><b>{E(a)}</b>{E(b)}</p>" for a, b in P2_RULES)
    return f"""<div class="page p2">
{small_head(P2_KICKER, P2_TITLE, P2_SUB, P2_BADGE)}
<p class="intro">{E(P2_INTRO)}</p>
<section class="dcards">{''.join(cards)}</section>
<section class="rules"><h3>{E(P2_RULES_TITLE)}</h3>{rules}</section>
<div class="footline"><span>{E(FOOTLINE)}</span><span>Page 2 of 3</span></div>
</div>"""


def page3():
    short = "".join(
        f'<article class="scard {c["tone"]}"><div class="rhead"><h2>{E(c["title"])}</h2><span class="time">{c["time"]}</span></div>'
        f'<ul>{"".join("<li>" + E(m) + "</li>" for m in c["moves"])}</ul><p class="note">{E(c["note"])}</p></article>'
        for c in P3_SHORT
    )
    chips = "".join(f"<span>{E(t)}</span>" for t in P3_WHEN)
    days = "".join(f'<span class="d">{d}</span>' for d in P3_DAYS)
    check_rows = "".join(
        f'<span class="r">{E(r)}</span>' + "".join('<span class="box7"></span>' for _ in P3_DAYS) for r in P3_CHECK_ROWS
    )
    rate_rows = "".join(
        f'<span class="r">{r}</span><span class="line"></span><span class="line"></span><span></span>' for r in P3_RATE_ROWS
    )
    return f"""<div class="page p3">
{small_head(P3_KICKER, P3_TITLE, P3_SUB, P3_BADGE)}
<section class="two">{short}</section>
<section class="scard mint when"><div><h2>{E(P3_WHEN_TITLE)}</h2><p>{E(P3_WHEN_SUB)}</p></div><div class="chips">{chips}</div></section>
<section class="scard lilac check"><h2>{E(P3_CHECK_TITLE)}</h2>
<div class="grid7"><span></span>{days}{check_rows}</div>
<p class="subq">{E(P3_RATE_TITLE)}</p>
<div class="rate"><span></span><span class="h">Day 1</span><span class="h">Day 7</span><span></span>{rate_rows}</div>
<p class="rnote">{E(P3_RATE_NOTE)}</p>
<p class="subq">{E(P3_NOTES_TITLE)}</p><div class="notes"><span></span><span></span></div></section>
<footer class="foot"><div class="box a"><h3>{E(P3_NEXT_TITLE)}</h3>{P3_NEXT}</div><div class="box b"><h3>{E(P3_STOP_TITLE)}</h3>{P3_STOP}</div></footer>
<div class="footline"><span>{E(FOOTLINE)}</span><span>Page 3 of 3</span></div>
</div>"""


def build():
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>The 5-minute desk stretch · Kristine Maia</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">
<style>{CSS}</style></head>
<body>{page1()}{page2()}{page3()}</body></html>"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    print("ok:", OUT_HTML)


if __name__ == "__main__":
    build()
