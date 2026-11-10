#!/usr/bin/env python3
"""
Face pagina de telefon pentru PROGRAM-DEFINIRE.md (se publică cu instrumentul Artifact).

Rulezi:   python3 library/build_program_page.py <fișierul.html de ieșire>
Sursa rămâne PROGRAM-DEFINIRE.md: schimbi acolo, rulezi din nou, republici pagina.
Bifele din liste se țin minte doar pe telefonul pe care le bifezi.
"""
import html
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(REPO, "PROGRAM-DEFINIRE.md")
JURNAL = "https://claude.ai/artifact/JmDEVgEPoyud4noLL78ZSL"

NAV = ["Calendar", "Săptămâna", "Forță", "Cardio", "Mâncare", "Ajustări", "De bifat"]

CSS = r"""
/* Layout: o coloană de citit pe telefon; sus titlul și scurtăturile spre secțiuni, apoi documentul. Culorile „powder” din brandul Kristine Maia. */
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
html{scroll-behavior:smooth;scroll-padding-top:calc(64px + env(safe-area-inset-top,0px))}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16.5px;line-height:1.6;-webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
a{color:var(--pink-ink);text-underline-offset:3px;overflow-wrap:anywhere}
:focus-visible{outline:3px solid var(--ink);outline-offset:2px;border-radius:8px}
.nav{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}
.nav-in{max-width:760px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:10px;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none}
.nav-in::-webkit-scrollbar{display:none}
.nav a{flex:none;text-decoration:none;font-weight:700;font-size:14px;color:var(--ink);background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:6px 12px}
.nav a.j{background:var(--pink);color:var(--pink-ink);border-color:transparent}
.wrap{max-width:760px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 64px}
.hero{display:flex;flex-direction:column;gap:12px;margin-bottom:28px}
.kicker{font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--pink-ink)}
h1,h2,h3{font-family:var(--display);letter-spacing:-.02em;line-height:1.12;text-wrap:balance;margin:0}
.hero h1{font-size:clamp(36px,10vw,56px);font-weight:800;letter-spacing:-.035em}
.facts{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.facts li{font-size:14px;font-weight:700;border-radius:999px;padding:5px 12px;background:var(--lilac);color:var(--lilac-ink)}
.facts li:nth-child(2){background:var(--mint);color:var(--mint-ink)}
.facts li:nth-child(3){background:var(--blue);color:var(--blue-ink)}
.cta{display:inline-flex;align-self:flex-start;align-items:center;gap:8px;text-decoration:none;font-weight:700;background:var(--ink);color:var(--bg);border-radius:14px;padding:11px 16px}
.doc h2{font-size:28px;font-weight:800;margin:44px 0 14px;padding-top:18px;border-top:2px solid var(--ink)}
.doc h3{font-size:20px;font-weight:800;margin:28px 0 10px}
.doc p,.doc ul,.doc ol{margin:0 0 12px;max-width:68ch}
.doc ul,.doc ol{padding-left:22px}
.doc li{margin:4px 0}
.doc em:first-child:last-child{color:var(--muted)}
.doc blockquote{margin:0 0 16px;padding:14px 16px;border-radius:16px;background:var(--pink);color:var(--ink)}
.doc blockquote p{margin:0}
.doc strong{font-weight:700}
.doc code{font-size:.92em;background:var(--track);border-radius:6px;padding:1px 5px}
.tbl{overflow-x:auto;margin:0 0 16px;border:1px solid var(--line);border-radius:14px;background:var(--paper)}
.tbl table{border-collapse:collapse;width:100%;font-size:14.5px;font-variant-numeric:tabular-nums}
.tbl th,.tbl td{text-align:left;vertical-align:top;padding:9px 12px;border-bottom:1px solid var(--line)}
.tbl tr:last-child td{border-bottom:0}
.tbl th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);background:var(--track);white-space:nowrap}
.tbl td:first-child{font-weight:600}
.doc ul.task-list{list-style:none;padding-left:0}
.doc ul.task-list li{display:flex;gap:10px;align-items:flex-start;padding:6px 0;border-bottom:1px solid var(--line);margin:0}
.doc ul.task-list label{display:flex;gap:10px;align-items:flex-start;cursor:pointer;width:100%}
.doc ul.task-list input{width:20px;height:20px;margin-top:3px;flex:none;accent-color:var(--pink-ink)}
.doc ul.task-list input:checked + span{color:var(--muted);text-decoration:line-through}
.foot{color:var(--muted);font-size:13.5px;margin-top:40px}
"""

JS = r"""
(function(){
  var KEY="program-definire-bife";
  var state={};
  try{ state=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ state={}; }
  var boxes=document.querySelectorAll(".doc ul.task-list input[type=checkbox]");
  boxes.forEach(function(b,i){
    var id="b"+i;
    b.removeAttribute("disabled");
    if(state[id]===true) b.checked=true;
    if(state[id]===false) b.checked=false;
    b.addEventListener("change",function(){
      state[id]=b.checked;
      try{ localStorage.setItem(KEY,JSON.stringify(state)); }catch(e){}
    });
  });
})();
"""


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "program-definire.html")
    md = open(SRC, encoding="utf-8").read()
    md = re.sub(r"^# .*\n", "", md, count=1)  # titlul îl pune pagina
    body = subprocess.run(["pandoc", "-f", "gfm", "-t", "html5"], input=md, capture_output=True,
                          text=True, check=True).stdout

    # secțiunile mari primesc id-uri simple (pentru scurtături)
    n = [0]
    def h2(m):
        n[0] += 1
        return '<h2 id="s%d">' % n[0]
    body = re.sub(r'<h2 id="[^"]*">', h2, body)
    body = re.sub(r"<h2>", h2, body)
    # tabelele derulează în cutia lor, nu toată pagina
    body = body.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    # bifele: textul într-un span, ca să se taie când e bifat
    body = re.sub(r'(<input type="checkbox"[^>]*/>)(.*?)(</label>)', r"\1<span>\2</span>\3", body, flags=re.S)

    nav = '<a class="j" href="%s">Jurnalul →</a>' % JURNAL + "".join(
        '<a href="#s%d">%s</a>' % (i + 1, html.escape(t)) for i, t in enumerate(NAV))

    page = f"""<title>Programul de definire</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@400;600;700&display=swap">
<style>{CSS}</style>
<nav class="nav" aria-label="Secțiuni"><div class="nav-in">{nav}</div></nav>
<main class="wrap">
  <header class="hero">
    <span class="kicker">Doar pentru tine · 11 nov – 7 feb</span>
    <h1>Programul de definire</h1>
    <ul class="facts"><li>4 forță + 3 cardio</li><li>1.550–1.650 kcal</li><li>120–130 g proteină</li></ul>
    <a class="cta" href="{JURNAL}">Deschide jurnalul de mâncare →</a>
  </header>
  <article class="doc">
{body}
  </article>
  <p class="foot">Bifele se țin minte pe telefonul pe care le bifezi. Când vrei să schimbăm ceva în program, scrie-i lui Claude.</p>
</main>
<script>{JS}</script>
"""
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(out, n[0], "secțiuni")


if __name__ == "__main__":
    main()
