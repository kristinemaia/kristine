"""Builds the tickable shopping list page (Romanian only) from LISTA-CUMPARATURI-RO.md.

Usage: python3 library/build_lista_bifat.py <output.html>
The page keeps the ticks in the artifact's db (collection "bife", one doc per ticked item).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "LISTA-CUMPARATURI-RO.md"

ITEM = re.compile(r"^(\d+)\. \*\*(.+?)\*\* — (.+)$")
ACASA = re.compile(r"\s*·\s*\*\*AVEM ACASĂ: luați doar diferența\*\*")


def bold(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def who_of(rest, section):
    groups = " ".join(re.findall(r"\(([^)]*)\)", rest))
    c = bool(re.search(r"\bC\b", groups))
    k = bool(re.search(r"\bK\b", groups))
    if c and k:
        return "CK"
    if c:
        return "C"
    if k:
        return "K"
    if "Kristine" in section:
        return "K"
    return "CK"


def parse():
    parts, part, sec = [], None, None
    for line in MD.read_text(encoding="utf-8").splitlines():
        if line.startswith("# PARTEA"):
            label = line[2:].strip()
            part = {"title": label, "note": "", "sections": []}
            if "PARTEA 2" in label:
                part["title"] = "Partea 2 · Dulap"
                part["note"] = "Ține multe săptămâni. Verificați întâi ce aveți și bifați și ce e deja în dulap."
            else:
                part["title"] = "Partea 1 · Săptămânal"
                part["note"] = "Proaspete, în fiecare săptămână."
            parts.append(part)
            continue
        if line.startswith("## "):
            name = line[3:].strip()
            if name.startswith("Casă"):
                part = {"title": "Casă și curățenie", "note": "", "sections": []}
                parts.append(part)
            if name.startswith("Nu în fiecare"):
                part = {"title": "Nu în fiecare săptămână", "note": "Doar pentru Cem. Bifați doar când e săptămâna lor.", "sections": []}
                parts.append(part)
            sec = {"name": "Produse" if name.startswith("Casă") else name, "items": []}
            part["sections"].append(sec)
            continue
        m = ITEM.match(line)
        if m:
            n, name, rest = m.groups()
            acasa = bool(ACASA.search(rest))
            rest = ACASA.sub("", rest)
            sec["items"].append({
                "id": "p" + n, "n": int(n), "name": name, "qty": bold(rest),
                "who": who_of(rest, sec["name"]), "acasa": acasa,
            })
    # the "not every week" lines become their own tickable items (Cem)
    extra = [
        ("x1", "Carne tocată de vită slabă", "<b>1.000 g</b> (burger)", "la 2 săptămâni"),
        ("x2", "Linte roșie", "<b>250 g</b> (supă)", "la 2 săptămâni"),
        ("x3", "Făină integrală", "<b>1.000 g</b>", "la 4 săptămâni"),
        ("x4", "Făină albă", "<b>100 g</b>", "la 4 săptămâni"),
        ("x5", "Drojdie uscată", "<b>2 × 10 g</b>", "la 4 săptămâni"),
        ("x6", "Busuioc proaspăt", "<b>≈100 g</b> (pesto)", "la 4 săptămâni"),
    ]
    last = parts[-1]
    last["sections"] = [{"name": "Pentru Cem", "items": [
        {"id": i, "n": None, "name": nm, "qty": q, "who": "C", "acasa": False, "when": w}
        for i, nm, q, w in extra
    ]}]
    return parts


PAGE = r"""<title>Cumpărături Kristine + Cem</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">
<style>
/* Layout: one narrow column like a till receipt; sticky bar with progress and filters, rows you tap in the shop. */
:root{
  --bg:#FFF9F6; --paper:#FFFFFF; --ink:#2B2431; --muted:#5C5466; --line:#EDE2EA; --track:#F4ECF1;
  --pink:#F8DCE6; --pink-ink:#8A3459; --p-fill:#D9779F;
  --blue:#DDE9F7; --blue-ink:#2A5580;
  --lilac:#E9E1F7; --lilac-ink:#4C3A78;
  --mint:#D8F0E4; --mint-ink:#1C6550; --done:#2E9C75;
  --warn:#FCEBD9; --warn-ink:#8A4B12;
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --body:"Figtree",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#1A1620; --paper:#241F2B; --ink:#F3EEF5; --muted:#B8AEC1; --line:#3A3242; --track:#322B3A;
  --pink:#4A2638; --pink-ink:#F3A9C7; --p-fill:#E58DB2;
  --blue:#1F3147; --blue-ink:#A6C8EE;
  --lilac:#2F2847; --lilac-ink:#CBBDF2;
  --mint:#1D3A30; --mint-ink:#93DEC0; --done:#5CC69F;
  --warn:#3D2A17; --warn-ink:#F2C08F;
  color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#1A1620; --paper:#241F2B; --ink:#F3EEF5; --muted:#B8AEC1; --line:#3A3242; --track:#322B3A;
  --pink:#4A2638; --pink-ink:#F3A9C7; --p-fill:#E58DB2;
  --blue:#1F3147; --blue-ink:#A6C8EE;
  --lilac:#2F2847; --lilac-ink:#CBBDF2;
  --mint:#1D3A30; --mint-ink:#93DEC0; --done:#5CC69F;
  --warn:#3D2A17; --warn-ink:#F2C08F;
  color-scheme:dark}

*,*::before,*::after{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.45;-webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
h1,h2,h3,p,ul{margin:0}
ul{padding:0;list-style:none}
h1,h2,h3{font-family:var(--display);letter-spacing:-.02em;line-height:1.1;text-wrap:balance}
button,input{font:inherit;color:inherit}
button{cursor:pointer;-webkit-tap-highlight-color:transparent}
:focus-visible{outline:3px solid var(--ink);outline-offset:2px;border-radius:10px}
.num{font-variant-numeric:tabular-nums}
.pad{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.col{max-width:640px;margin:0 auto}

/* bara de sus */
.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}
.top-in{padding-block:12px 12px;display:flex;flex-direction:column;gap:10px}
.row1{display:flex;align-items:baseline;justify-content:space-between;gap:12px}
.kicker{font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--pink-ink)}
h1{font-size:24px;font-weight:800}
.count{font-family:var(--display);font-weight:800;font-size:22px;white-space:nowrap}
.count small{font-family:var(--body);font-weight:500;font-size:14px;color:var(--muted)}
.bar{height:8px;border-radius:99px;background:var(--track);overflow:hidden}
.bar i{display:block;height:100%;width:0;background:var(--done);border-radius:99px;transition:width .25s ease}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.seg{display:flex;background:var(--track);border-radius:12px;padding:3px;gap:2px}
.seg button{border:0;background:none;padding:7px 12px;border-radius:9px;font-weight:600;font-size:14px;color:var(--muted)}
.seg button[aria-pressed="true"]{background:var(--paper);color:var(--ink);box-shadow:0 1px 3px rgba(43,36,49,.12)}
.toggle{margin-left:auto;border:1px solid var(--line);background:var(--paper);border-radius:12px;padding:7px 12px;font-weight:600;font-size:14px}
.toggle[aria-pressed="true"]{background:var(--mint);color:var(--mint-ink);border-color:transparent}

.wrap{padding-block:18px 56px;display:flex;flex-direction:column;gap:30px}
.banner{border-radius:14px;padding:12px 14px;background:var(--warn);color:var(--warn-ink);font-size:14px}
.rules{font-size:14px;color:var(--muted);display:flex;flex-direction:column;gap:2px}
.rules b{color:var(--ink)}

/* părți și secțiuni */
.part{display:flex;flex-direction:column;gap:18px}
.part-head{display:flex;flex-direction:column;gap:4px;padding-bottom:10px;border-bottom:2px solid var(--ink)}
.part-head h2{font-size:22px;font-weight:800}
.part-head p{font-size:14px;color:var(--muted)}
.sec{display:flex;flex-direction:column;gap:6px}
.sec-head{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.sec-head h3{font-family:var(--body);font-size:13px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.sec-head span{font-size:13px;color:var(--muted)}
.sec-head span.full{color:var(--mint-ink);font-weight:700}

/* rândurile */
.items{display:flex;flex-direction:column;background:var(--paper);border:1px solid var(--line);border-radius:16px;overflow:hidden}
.item{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:start;padding:10px 14px;border-top:1px solid var(--line);cursor:pointer;-webkit-tap-highlight-color:transparent}
.items .item:first-child{border-top:0}
.item input{position:absolute;opacity:0;width:1px;height:1px;pointer-events:none}
.box{width:28px;height:28px;border-radius:9px;border:2px solid var(--line);background:var(--bg);display:grid;place-items:center;margin-top:1px;transition:background .15s,border-color .15s}
.box svg{width:16px;height:16px;opacity:0;transform:scale(.6);transition:opacity .15s,transform .15s}
.item input:focus-visible + .box{outline:3px solid var(--ink);outline-offset:2px}
.item.on .box{background:var(--done);border-color:var(--done)}
.item.on .box svg{opacity:1;transform:none}
.txt{min-width:0;display:flex;flex-direction:column;gap:2px}
.name{font-weight:600;font-size:16px}
.name .n{color:var(--muted);font-weight:500;margin-right:6px}
.qty{font-size:14px;color:var(--muted);overflow-wrap:anywhere}
.qty b{color:var(--ink);font-weight:700}
.meta{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-size:12px;font-weight:700;padding:2px 8px;border-radius:99px;letter-spacing:.02em}
.chip.C{background:var(--blue);color:var(--blue-ink)}
.chip.K{background:var(--pink);color:var(--pink-ink)}
.chip.CK{background:var(--lilac);color:var(--lilac-ink)}
.chip.acasa{background:var(--warn);color:var(--warn-ink)}
.chip.when{background:var(--track);color:var(--muted)}
.item.on .name{text-decoration:line-through;text-decoration-thickness:2px;color:var(--muted)}
.item.on .qty,.item.on .chips{opacity:.55}
.item.ro{cursor:default}

.empty{text-align:center;padding:28px 12px;border:1px dashed var(--line);border-radius:16px;color:var(--muted)}
.empty b{display:block;font-family:var(--display);font-size:20px;color:var(--ink);margin-bottom:4px}

.foot{display:flex;flex-direction:column;gap:14px;padding-top:8px;border-top:1px solid var(--line)}
.foot p{font-size:14px;color:var(--muted)}
.reset{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.btn{border:1px solid var(--line);background:var(--paper);border-radius:12px;padding:10px 14px;font-weight:600}
.btn.danger{background:var(--pink-ink);border-color:var(--pink-ink);color:var(--bg)}
.status{font-size:13px;color:var(--muted)}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media (max-width:420px){h1{font-size:21px}.toggle{margin-left:0}}
</style>

<header class="top">
  <div class="top-in col pad">
    <div class="row1">
      <div>
        <div class="kicker">Kristine + Cem · o săptămână</div>
        <h1>Lista de cumpărături</h1>
      </div>
      <div class="count num" id="count" aria-live="polite">0 <small>din 0</small></div>
    </div>
    <div class="bar" aria-hidden="true"><i id="barFill"></i></div>
    <div class="controls">
      <div class="seg" role="group" aria-label="Arată produsele">
        <button type="button" id="f-all" data-f="all" aria-pressed="true">Toate</button>
        <button type="button" id="f-K" data-f="K" aria-pressed="false">Kristine</button>
        <button type="button" id="f-C" data-f="C" aria-pressed="false">Cem</button>
      </div>
      <button type="button" class="toggle" id="hideDone" aria-pressed="false">Ascunde bifate</button>
    </div>
  </div>
</header>

<main class="wrap col pad">
  <div class="banner" id="banner" hidden></div>
  <div class="rules">
    <div><b>Cem nu mănâncă:</b> orez, lactoză, roșii. <b>Kristine nu mănâncă:</b> carne.</div>
    <div>Atinge un produs ca să-l bifezi. Bifele rămân salvate până apeși „Golește bifele”.</div>
  </div>
  <div id="list"></div>
  <div class="empty" id="allDone" hidden><b>Totul e bifat</b>Apasă „Ascunde bifate” ca să vezi din nou lista.</div>
  <footer class="foot">
    <p><b>Când se termină:</b> bulgur · quinoa · hrișcă · ovăz · paste · ulei de măsline · proteina și creatina Kristinei.</p>
    <div class="reset" id="resetBox">
      <button type="button" class="btn" id="resetBtn">Golește bifele (săptămână nouă)</button>
    </div>
    <div class="status" id="status">Se încarcă bifele…</div>
  </footer>
</main>

<script>
const DATA = __DATA__;
const CHECK = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8.5l3.2 3L13 4.8" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const WHO = {C:"Cem", K:"Kristine", CK:"amândoi"};
const LS_KEY = "lista-bifat-v1", LS_PREF = "lista-bifat-pref";

const $ = id => document.getElementById(id);
const rows = new Map();      // id -> {el, input, item, sec}
const sections = [];         // {el, items:[id], countEl}
const parts = [];            // {el, sections:[...]}
let server = new Set();      // ticks the store (or this device) holds
const desired = new Map();   // id -> bool while a write is on its way
const inflight = new Map();  // id -> count
const queues = {};
const written = new Map();
let db = null, mode = "loading", readOnly = false;
let filter = "all", hideDone = false;

function lsGet(k){ try{ return JSON.parse(localStorage.getItem(k)||"null"); }catch(e){ return null; } }
function lsSet(k,v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }

function isOn(id){ return inflight.get(id) ? desired.get(id) : server.has(id); }
function matches(item){ return filter==="all" || item.who===filter || item.who==="CK"; }
function setBanner(t){ const b=$("banner"); b.textContent=t||""; b.hidden=!t; }
function setStatus(t){ $("status").textContent=t; }

function build(){
  const list = $("list");
  list.style.display="flex"; list.style.flexDirection="column"; list.style.gap="34px";
  DATA.forEach(p=>{
    const pe=document.createElement("section"); pe.className="part";
    pe.innerHTML='<div class="part-head"><h2></h2>'+(p.note?'<p></p>':'')+'</div>';
    pe.querySelector("h2").textContent=p.title;
    if(p.note) pe.querySelector("p").textContent=p.note;
    const pr={el:pe, sections:[]};
    p.sections.forEach(s=>{
      const se=document.createElement("div"); se.className="sec";
      se.innerHTML='<div class="sec-head"><h3></h3><span class="num"></span></div><ul class="items"></ul>';
      se.querySelector("h3").textContent=s.name;
      const ul=se.querySelector("ul");
      const sr={el:se, items:[], countEl:se.querySelector(".sec-head span")};
      s.items.forEach(it=>{
        const li=document.createElement("li");
        const lab=document.createElement("label"); lab.className="item";
        const inp=document.createElement("input"); inp.type="checkbox"; inp.id="c-"+it.id;
        const box=document.createElement("span"); box.className="box"; box.innerHTML=CHECK;
        const txt=document.createElement("span"); txt.className="txt";
        const nm=document.createElement("span"); nm.className="name";
        if(it.n){ const n=document.createElement("span"); n.className="n num"; n.textContent=it.n+"."; nm.appendChild(n); }
        nm.appendChild(document.createTextNode(it.name));
        const q=document.createElement("span"); q.className="qty"; q.innerHTML=it.qty;
        const ch=document.createElement("span"); ch.className="chips";
        ch.innerHTML='<span class="chip '+it.who+'">'+WHO[it.who]+'</span>'
          +(it.acasa?'<span class="chip acasa">avem acasă: doar diferența</span>':'')
          +(it.when?'<span class="chip when">'+it.when+'</span>':'');
        const meta=document.createElement("span"); meta.className="meta"; meta.append(q,ch);
        txt.append(nm,meta); lab.append(inp,box,txt); li.appendChild(lab); ul.appendChild(li);
        inp.addEventListener("change",()=>toggle(it.id, inp.checked));
        rows.set(it.id,{el:li, lab, input:inp, item:it});
        sr.items.push(it.id);
      });
      pe.appendChild(se); pr.sections.push(sr); sections.push(sr);
    });
    list.appendChild(pe); parts.push(pr);
  });
}

function render(){
  let tot=0, done=0;
  rows.forEach((r,id)=>{
    const on=isOn(id), vis=matches(r.item);
    r.input.checked=on; r.input.disabled=readOnly;
    r.lab.classList.toggle("on",on); r.lab.classList.toggle("ro",readOnly);
    r.el.hidden = !vis || (hideDone && on);
    if(vis){ tot++; if(on) done++; }
  });
  sections.forEach(s=>{
    let t=0,d=0,shown=0;
    s.items.forEach(id=>{ const r=rows.get(id); if(matches(r.item)){ t++; if(isOn(id)) d++; } if(!r.el.hidden) shown++; });
    s.countEl.textContent = t ? d+" / "+t : "";
    s.countEl.classList.toggle("full", t>0 && d===t);
    s.el.hidden = shown===0;
  });
  parts.forEach(p=>{ p.el.hidden = p.sections.every(s=>s.el.hidden); });
  $("allDone").hidden = !(hideDone && tot>0 && done===tot);
  $("count").innerHTML = done+' <small>din '+tot+'</small>';
  $("barFill").style.width = tot ? (done/tot*100)+"%" : "0";
}

function toggle(id,on){
  if(readOnly){ render(); return; }
  desired.set(id,on);
  render();
  persist(id);
}

function persist(id){
  if(mode!=="db"){
    if(desired.get(id)) server.add(id); else server.delete(id);
    lsSet(LS_KEY,[...server]);
    return Promise.resolve();
  }
  inflight.set(id,(inflight.get(id)||0)+1);
  const p=(queues[id]||Promise.resolve()).then(async()=>{
    const want=desired.get(id);
    if(written.get(id)===want) return;
    const ref=db.collection("bife").doc(id);
    try{
      if(want) await ref.set({done:true, at:new Date().toISOString()});
      else await ref.delete();
    }catch(e){
      if(e && e.code==="unavailable"){
        await new Promise(r=>setTimeout(r,600+Math.random()*900));
        if(want) await ref.set({done:true, at:new Date().toISOString()}); else await ref.delete();
      } else throw e;
    }
    written.set(id,want);
    if(want) server.add(id); else server.delete(id);
  }).catch(e=>{
    if(e && e.code==="invalid_argument"){ readOnly=true; setBanner("Aici lista se poate doar vedea, nu și bifa. Kristine îți poate da acces de Contributor."); }
    else if(e && e.code==="quota_exceeded"){ setBanner("Nu mai e loc pentru bife noi. Golește bifele și încearcă din nou."); }
    else { setBanner("O bifă nu s-a salvat. Verifică internetul și atinge din nou produsul."); }
  }).finally(()=>{
    const n=(inflight.get(id)||1)-1;
    if(n<=0){ inflight.delete(id); desired.delete(id); } else inflight.set(id,n);
    render();
  });
  queues[id]=p;
  return p;
}

/* Golește bifele: confirmare în pagină */
function showReset(confirming){
  const box=$("resetBox"); box.innerHTML="";
  if(!confirming){
    const b=document.createElement("button"); b.type="button"; b.className="btn"; b.id="resetBtn";
    b.textContent="Golește bifele (săptămână nouă)"; b.disabled=readOnly;
    b.onclick=()=>showReset(true); box.appendChild(b); return;
  }
  const yes=document.createElement("button"); yes.type="button"; yes.className="btn danger"; yes.id="resetYes";
  yes.textContent="Da, golește toate bifele";
  const no=document.createElement("button"); no.type="button"; no.className="btn"; no.id="resetNo";
  no.textContent="Renunță";
  no.onclick=()=>showReset(false);
  yes.onclick=async()=>{
    const ids=[...rows.keys()].filter(isOn);
    ids.forEach(id=>desired.set(id,false));
    showReset(false); render();
    for(let i=0;i<ids.length;i+=6) await Promise.all(ids.slice(i,i+6).map(persist));
    setStatus("Bifele au fost golite. Lista e gata pentru săptămâna nouă.");
  };
  box.append(yes,no); yes.focus();
}

function setFilter(f){
  filter=f;
  document.querySelectorAll(".seg button").forEach(b=>b.setAttribute("aria-pressed", b.dataset.f===f ? "true":"false"));
  savePref(); render();
}
function savePref(){ lsSet(LS_PREF,{filter, hideDone}); }

function startLocal(why){
  mode="local";
  server=new Set(lsGet(LS_KEY)||[]);
  setStatus(why);
  render();
}

async function boot(){
  const pref=lsGet(LS_PREF);
  if(pref){ filter=["all","K","C"].includes(pref.filter)?pref.filter:"all"; hideDone=!!pref.hideDone; }
  build();
  document.querySelectorAll(".seg button").forEach(b=>b.addEventListener("click",()=>setFilter(b.dataset.f)));
  $("hideDone").addEventListener("click",()=>{ hideDone=!hideDone; $("hideDone").setAttribute("aria-pressed",hideDone?"true":"false"); savePref(); render(); });
  $("hideDone").setAttribute("aria-pressed",hideDone?"true":"false");
  setFilter(filter);
  showReset(false);

  const C=window.claude;
  if(!C || !C.use){ startLocal("Bifele se salvează doar pe acest dispozitiv."); return; }
  let d=null;
  try{ d=await C.use("db"); }catch(e){ d=null; }
  if(!d){ startLocal("Bifele se salvează doar pe acest dispozitiv (intră în contul Claude ca să le vezi și pe telefon, și pe laptop)."); return; }
  db=d; mode="db";
  C.use("user").then(u=>{
    if(!u || !u.can) return;
    Promise.resolve(u.can("data.write")).then(ok=>{ if(ok===false){ readOnly=true; setBanner("Aici lista se poate doar vedea, nu și bifa. Kristine îți poate da acces de Contributor."); showReset(false); render(); } }).catch(()=>{});
  }).catch(()=>{});
  let timer=setTimeout(()=>setStatus("Bifele nu se pot încărca acum. Verifică internetul; lista rămâne aici."),10000);
  db.collection("bife").onSnapshot(snap=>{
    const s=new Set();
    snap.docs.forEach(doc=>{ if(doc.exists) s.add(doc.id); });
    server=s;
    rows.forEach((r,id)=>{ if(!inflight.get(id)) written.set(id, s.has(id)); });
    if(!snap.metadata.fromCache){ clearTimeout(timer); timer=null; setStatus("Bifele se salvează singure, pe orice dispozitiv."); }
    render();
  }, e=>{
    clearTimeout(timer);
    setStatus("Bifele nu se mai sincronizează. Redeschide pagina.");
  });
}

boot();
</script>
"""


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "lista-bifat.html"
    parts = parse()
    n = sum(len(s["items"]) for p in parts for s in p["sections"])
    html = PAGE.replace("__DATA__", json.dumps(parts, ensure_ascii=False))
    out.write_text(html, encoding="utf-8")
    print(f"{out}: {n} produse, {len(parts)} părți")


if __name__ == "__main__":
    main()
