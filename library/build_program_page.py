#!/usr/bin/env python3
"""
Face pagina de telefon pentru programul de definire (se publică cu instrumentul Artifact).

Pagina are o intrare cu trei butoane mari, iar fiecare deschide doar partea lui:
  Antrenamentul (PROGRAM-ANTRENAMENT.md), Alimentația (PROGRAM-ALIMENTATIE.md),
  Cardio și pașii (PROGRAM-CARDIO.md).

Rulezi:   python3 library/build_program_page.py <fișierul.html de ieșire>
Schimbi textul în cele trei fișiere .md, rulezi din nou și republici pagina.
Bifele din liste se țin minte doar pe telefonul pe care le bifezi.
"""
import html
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JURNAL = "https://claude.ai/artifact/JmDEVgEPoyud4noLL78ZSL"

PARTS = [
    {"id": "antrenament", "src": "PROGRAM-ANTRENAMENT.md", "name": "Antrenamentul",
     "tag": "Sala · 4 zile", "desc": "Picioare A și B, Upper A și B: exercițiile, seturile, repetările și pauzele.",
     "facts": ["Luni, marți, joi, vineri", "RIR 1–2", "+2,5 kg când ajungi sus"], "tone": "lilac"},
    {"id": "alimentatie", "src": "PROGRAM-ALIMENTATIE.md", "name": "Alimentația",
     "tag": "Mâncare", "desc": "Mesele (porții gătite), deserturile, pofta de dulce, cumpărăturile și cum ajustăm după cântar.",
     "facts": ["1.550–1.650 kcal", "120–130 g proteină", "desert zilnic"], "tone": "pink"},
    {"id": "cardio", "src": "PROGRAM-CARDIO.md", "name": "Cardio și pașii",
     "tag": "3 pe săptămână", "desc": "Intervalele de marți, banda înclinată, cardio-ul lung de sâmbătă și pașii.",
     "facts": ["13 min intervale", "35–45 min ușor", "8.000–10.000 pași"], "tone": "mint"},
]

CSS = r"""
/* Layout: o intrare cu trei butoane mari; fiecare parte e o pagină separată, cu bară de întoarcere și scurtături spre secțiunile ei. Culorile „powder” din brandul Kristine Maia. */
:root{
  --bg:#FFF9F6; --paper:#FFFFFF; --ink:#2B2431; --muted:#5C5466; --line:#EDE2EA; --track:#F4ECF1;
  --pink:#F8DCE6; --pink-ink:#8A3459; --blue:#DDE9F7; --blue-ink:#2A5580;
  --lilac:#E9E1F7; --lilac-ink:#4C3A78; --mint:#D8F0E4; --mint-ink:#1C6550;
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --body:"Figtree",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#1A1620; --paper:#241F2B; --ink:#F3EEF5; --muted:#B8AEC1; --line:#3A3242; --track:#322B3A;
  --pink:#4A2638; --pink-ink:#F3A9C7; --blue:#1F3147; --blue-ink:#A6C8EE;
  --lilac:#2F2847; --lilac-ink:#CBBDF2; --mint:#1D3A30; --mint-ink:#93DEC0; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#1A1620; --paper:#241F2B; --ink:#F3EEF5; --muted:#B8AEC1; --line:#3A3242; --track:#322B3A;
  --pink:#4A2638; --pink-ink:#F3A9C7; --blue:#1F3147; --blue-ink:#A6C8EE;
  --lilac:#2F2847; --lilac-ink:#CBBDF2; --mint:#1D3A30; --mint-ink:#93DEC0; color-scheme:dark}
*,*::before,*::after{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16.5px;line-height:1.6;-webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
a{color:var(--pink-ink);text-underline-offset:3px;overflow-wrap:anywhere}
button{font:inherit;color:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent}
:focus-visible{outline:3px solid var(--ink);outline-offset:2px;border-radius:8px}
h1,h2,h3{font-family:var(--display);letter-spacing:-.02em;line-height:1.12;text-wrap:balance;margin:0}
.wrap{max-width:760px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}

/* intrarea */
.home{padding-block:28px 56px;display:flex;flex-direction:column;gap:22px}
.kicker{font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--pink-ink)}
.home h1{font-size:clamp(38px,11vw,58px);font-weight:800;letter-spacing:-.035em}
.today{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;font-size:15px}
.today b{font-family:var(--display);font-size:20px;letter-spacing:-.01em}
.tiles{display:flex;flex-direction:column;gap:14px}
.tile{display:flex;flex-direction:column;gap:8px;text-align:left;border:0;border-radius:22px;padding:20px 20px 18px;background:var(--paper);box-shadow:inset 0 0 0 1px var(--line);text-decoration:none;color:var(--ink);position:relative}
.tile .tg{font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase}
.tile h2{font-size:30px;font-weight:800}
.tile p{margin:0;color:var(--muted);font-size:15px;max-width:52ch}
.tile .fx{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px}
.tile .fx span{font-size:13px;font-weight:700;border-radius:999px;padding:3px 10px}
.tile .go{position:absolute;right:18px;top:18px;width:40px;height:40px;border-radius:12px;display:grid;place-items:center;font-size:20px;font-weight:700}
.tile.lilac{background:var(--lilac)} .tile.lilac .tg,.tile.lilac .fx span{color:var(--lilac-ink)} .tile.lilac .fx span,.tile.lilac .go{background:var(--paper)}
.tile.pink{background:var(--pink)} .tile.pink .tg,.tile.pink .fx span{color:var(--pink-ink)} .tile.pink .fx span,.tile.pink .go{background:var(--paper)}
.tile.mint{background:var(--mint)} .tile.mint .tg,.tile.mint .fx span{color:var(--mint-ink)} .tile.mint .fx span,.tile.mint .go{background:var(--paper)}
.jbtn{display:flex;align-items:center;justify-content:space-between;gap:10px;text-decoration:none;font-weight:700;background:var(--ink);color:var(--bg);border-radius:16px;padding:14px 18px}

/* o parte */
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}
.bar-in{max-width:760px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:10px 8px;display:flex;flex-direction:column;gap:8px}
.bar-top{display:flex;align-items:center;gap:10px}
.back{border:1px solid var(--line);background:var(--paper);border-radius:12px;padding:7px 12px;font-weight:700;font-size:14px;flex:none}
.bar-top .ttl{font-family:var(--display);font-weight:800;font-size:19px;letter-spacing:-.01em;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chips{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}
.chips::-webkit-scrollbar{display:none}
.chips button{flex:none;border:1px solid var(--line);background:var(--paper);border-radius:999px;padding:5px 11px;font-size:13.5px;font-weight:600}
.part{padding-block:18px 64px}
.part .head{display:flex;flex-direction:column;gap:6px;margin-bottom:12px}
.part .head h1{font-size:clamp(32px,9vw,46px);font-weight:800;letter-spacing:-.03em}
.doc h2{font-size:26px;font-weight:800;margin:40px 0 12px;padding-top:16px;border-top:2px solid var(--ink);scroll-margin-top:calc(110px + env(safe-area-inset-top,0px))}
.doc h3{font-size:19px;font-weight:800;margin:22px 0 8px}
.doc p,.doc ul,.doc ol{margin:0 0 12px;max-width:68ch}
.doc ul,.doc ol{padding-left:22px}
.doc li{margin:4px 0}
.doc em:first-child:last-child{color:var(--muted)}
.doc blockquote{margin:0 0 16px;padding:14px 16px;border-radius:16px;background:var(--track)}
.doc blockquote p{margin:0}
.doc code{font-size:.92em;background:var(--track);border-radius:6px;padding:1px 5px}
.tbl{overflow-x:auto;margin:0 0 16px;border:1px solid var(--line);border-radius:14px;background:var(--paper)}
.tbl table{border-collapse:collapse;width:100%;font-size:14.5px;font-variant-numeric:tabular-nums}
.tbl th,.tbl td{text-align:left;vertical-align:top;padding:9px 12px;border-bottom:1px solid var(--line)}
.tbl tr:last-child td{border-bottom:0}
.tbl th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);background:var(--track);white-space:nowrap}
.doc ul.task-list{list-style:none;padding-left:0}
.doc ul.task-list li{padding:6px 0;border-bottom:1px solid var(--line);margin:0}
.doc ul.task-list label{display:flex;gap:10px;align-items:flex-start;cursor:pointer}
.doc ul.task-list input{width:20px;height:20px;margin-top:3px;flex:none;accent-color:var(--pink-ink)}
.doc ul.task-list input:checked + span{color:var(--muted);text-decoration:line-through}
.next{display:flex;gap:10px;flex-wrap:wrap;margin-top:36px}
.next button,.next a{border:1px solid var(--line);background:var(--paper);border-radius:14px;padding:10px 14px;font-weight:700;font-size:14.5px;text-decoration:none;color:var(--ink)}
"""

JS = r"""
(function(){
  var views = document.querySelectorAll("[data-view]");
  var ids = Array.prototype.map.call(views, function(v){ return v.dataset.view; });
  function show(){
    var h = (location.hash || "").replace("#","");
    var id = ids.indexOf(h) >= 0 ? h : "acasa";
    views.forEach(function(v){ v.hidden = v.dataset.view !== id; });
    window.scrollTo(0,0);
  }
  window.addEventListener("hashchange", show);
  show();
  document.addEventListener("click", function(e){
    var b = e.target.closest("[data-go]");
    if(b){ e.preventDefault(); var t = b.dataset.go; location.hash = (t === "acasa") ? "" : t; show(); return; }
    var s = e.target.closest("[data-sec]");
    if(s){ var el = document.getElementById(s.dataset.sec); if(el) el.scrollIntoView({behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"}); }
  });

  // ce e azi în plan
  var SPECIAL = {"2026-11-10":"Picioare A","2026-11-11":"Upper A + intervale","2026-11-12":"Cardio ușor 35–40 min","2026-11-13":"Picioare B","2026-11-14":"Upper B + 30 min cardio ușor","2026-11-15":"Pauză"};
  var WEEK = ["Pauză","Picioare A","Upper A + intervale","Cardio ușor 35–40 min","Picioare B","Upper B","Cardio ușor 40–45 min"];
  var d = new Date(), pad = function(n){ return String(n).padStart(2,"0"); };
  var k = d.getFullYear()+"-"+pad(d.getMonth()+1)+"-"+pad(d.getDate());
  var p = SPECIAL[k] || WEEK[d.getDay()];
  if(k >= "2026-12-21" && k <= "2026-12-27" && p !== "Pauză") p += " (săptămâna ușoară)";
  var el = document.getElementById("todayPlan"); if(el) el.textContent = p;

  // bifele, ținute minte pe telefon
  var KEY = "program-definire-bife-v2", state = {};
  try{ state = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; }catch(e){ state = {}; }
  document.querySelectorAll(".doc ul.task-list input[type=checkbox]").forEach(function(b){
    var id = b.dataset.k;
    b.removeAttribute("disabled");
    if(state[id] === true) b.checked = true;
    if(state[id] === false) b.checked = false;
    b.addEventListener("change", function(){
      state[id] = b.checked;
      try{ localStorage.setItem(KEY, JSON.stringify(state)); }catch(e){}
    });
  });
})();
"""


def render_part(part):
    md = open(os.path.join(REPO, part["src"]), encoding="utf-8").read()
    md = re.sub(r"^# .*\n", "", md, count=1)
    body = subprocess.run(["pandoc", "-f", "gfm", "-t", "html5"], input=md, capture_output=True,
                          text=True, check=True).stdout
    secs = []

    def h2(m):
        n = len(secs) + 1
        sid = "%s-%d" % (part["id"], n)
        secs.append(sid)
        return '<h2 id="%s">' % sid
    body = re.sub(r'<h2(?: id="[^"]*")?>', h2, body)
    titles = re.findall(r'<h2 id="[^"]+">(.*?)</h2>', body, flags=re.S)
    body = body.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    cnt = [0]

    def box(m):
        cnt[0] += 1
        return m.group(1).replace("<input ", '<input data-k="%s-%d" ' % (part["id"], cnt[0]), 1) + "<span>" + m.group(2) + "</span>" + m.group(3)
    body = re.sub(r'(<input type="checkbox"[^>]*/>)(.*?)(</label>)', box, body, flags=re.S)

    def short(t):
        t = re.sub(r"<[^>]+>", "", t)
        t = html.unescape(t)
        t = re.split(r"\s[(:·]", t)[0].strip()
        return t
    chips = "".join('<button type="button" data-sec="%s">%s</button>' % (sid, html.escape(short(t)))
                    for sid, t in zip(secs, titles))
    others = [q for q in PARTS if q["id"] != part["id"]]
    nxt = "".join('<button type="button" data-go="%s">%s →</button>' % (q["id"], html.escape(q["name"])) for q in others)
    return f"""<section data-view="{part['id']}" hidden>
  <div class="bar"><div class="bar-in">
    <div class="bar-top"><button class="back" type="button" data-go="acasa">← Program</button><span class="ttl">{html.escape(part['name'])}</span></div>
    <div class="chips" aria-label="Secțiuni">{chips}</div>
  </div></div>
  <div class="wrap part">
    <div class="head"><span class="kicker">{html.escape(part['tag'])}</span><h1>{html.escape(part['name'])}</h1></div>
    <article class="doc">{body}</article>
    <div class="next">{nxt}<a href="{JURNAL}">Jurnalul de mâncare →</a></div>
  </div>
</section>"""


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "program-definire.html")
    tiles = "".join(
        f"""<a class="tile {p['tone']}" href="#{p['id']}" data-go="{p['id']}"><span class="tg">{html.escape(p['tag'])}</span><h2>{html.escape(p['name'])}</h2><p>{html.escape(p['desc'])}</p><span class="fx">{''.join('<span>%s</span>' % html.escape(f) for f in p['facts'])}</span><span class="go" aria-hidden="true">→</span></a>"""
        for p in PARTS)
    parts = "\n".join(render_part(p) for p in PARTS)
    page = f"""<title>Programul de definire</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@400;600;700&display=swap">
<style>{CSS}</style>
<section data-view="acasa">
  <div class="wrap home">
    <div style="display:flex;flex-direction:column;gap:8px"><span class="kicker">Doar pentru tine · 11 nov – 7 feb</span><h1>Programul de definire</h1></div>
    <p class="today">Azi în plan: <b id="todayPlan">vezi Antrenamentul</b></p>
    <nav class="tiles" aria-label="Cele trei părți">{tiles}</nav>
    <a class="jbtn" href="{JURNAL}"><span>Jurnalul de mâncare</span><span aria-hidden="true">→</span></a>
  </div>
</section>
{parts}
<script>{JS}</script>
"""
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(out)


if __name__ == "__main__":
    main()
