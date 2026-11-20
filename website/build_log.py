#!/usr/bin/env python3
"""Jurnalul de greutăți pentru membrii Custom Program: kristinemaia.com/log.html (pagină ascunsă, nu apare în meniu, noindex).
Alegi antrenamentul (aceleași ca postările de pe Payhip), scrii kg și repetări la fiecare set, vezi „Last time” și primești sugestia când să crești.
Totul rămâne în telefonul sau calculatorul omului (localStorage); nu se trimite nimic nicăieri.
Rulezi: python3 website/build_log.py -> website/log.html (intră în zip-ul site-ului, ca restul paginilor)"""
import html, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'studio/custom-program'))
from workouts import ALL, NAMES, HOME_NAMES

def nm(cid, home): return HOME_NAMES.get(cid, NAMES[cid]) if home else NAMES[cid]
data = []
for wk in ALL:
    if any(t in wk['tags'] for t in ('Resets', 'Cardio', 'Unstiff')): continue
    data.append({'t': wk['title'], 'x': [[nm(c, wk['home']), s] for c, s in wk['main']]})

page = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Training log · Level Up</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Figtree:wght@400;600;700&display=swap">
<style>
:root{--bg:#FFF9F6;--paper:#fff;--ink:#2B2431;--muted:#5C5466;--line:#EDE2EA;--pink:#F8DCE6;--pink-ink:#8A3459;--mint:#D8F0E4;--mint-ink:#1C6550}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1A1620;--paper:#241F2B;--ink:#F3EEF5;--muted:#B7ADBF;--line:#3A3243;--pink:#4A2A3A;--pink-ink:#F4B4CE;--mint:#1E3B31;--mint-ink:#9BE0C2}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:Figtree,system-ui,sans-serif;font-size:17px;line-height:1.5;padding:20px 16px 60px}
.wrap{max-width:640px;margin:0 auto}h1,h2{font-family:"Bricolage Grotesque",system-ui,sans-serif;letter-spacing:-.02em;line-height:1.1}
h1{font-size:32px;margin:0 0 6px}.muted{color:var(--muted)}select,input,button{font:inherit}
select{width:100%;padding:12px;border-radius:12px;border:1px solid var(--line);background:var(--paper);color:var(--ink);margin:14px 0 8px}
.ex{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin:12px 0}
.ex h2{font-size:19px;margin:0}.target{font-size:14px;color:var(--pink-ink);font-weight:700}
.last{font-size:14px;color:var(--muted);margin:4px 0 8px}.tip{font-size:14px;background:var(--mint);color:var(--mint-ink);border-radius:10px;padding:6px 10px;margin:6px 0}
.sets{display:grid;grid-template-columns:auto 1fr 1fr;gap:6px 8px;align-items:center}
.sets input{width:100%;padding:9px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);min-width:0}
.sets span{font-size:14px;color:var(--muted)}
button{border:0;border-radius:999px;padding:14px 22px;background:var(--pink-ink);color:#fff;font-weight:700;width:100%;margin-top:14px;cursor:pointer}
.ok{color:var(--mint-ink);font-weight:700;text-align:center;margin-top:10px}
.hist{font-size:14px;color:var(--muted);margin-top:4px}
</style></head><body><div class="wrap">
<p class="muted" style="margin:0">Level Up · Kristine Maia</p>
<h1>Your training log</h1>
<p class="muted">Pick today's workout, write your weight and reps for every set, then save. Next time you'll see what you lifted. Everything stays on this phone, nothing is sent anywhere.</p>
<select id="w" aria-label="Workout"></select>
<div id="list"></div>
<button id="save" type="button">Save today's workout</button>
<p class="ok" id="ok" hidden>Saved. See you next session 💪</p>
<p class="muted" style="font-size:14px;margin-top:28px">Tip: add this page to your home screen (Share → Add to Home Screen) so it opens like an app. General exercise, not medical advice.</p>
</div>
<script>
(function(){
var W=__DATA__;
var sel=document.getElementById('w'),list=document.getElementById('list');
W.forEach(function(w,i){var o=document.createElement('option');o.value=i;o.textContent=w.t;sel.appendChild(o)});
function key(i){return 'km-log:'+W[i].t}
function load(i){try{return JSON.parse(localStorage.getItem(key(i))||'[]')}catch(e){return []}}
function store(i,v){try{localStorage.setItem(key(i),JSON.stringify(v))}catch(e){}}
function nsets(t){var m=t.match(/^(\d)\s*×/);return m?+m[1]:3}
function topRep(t){var m=t.match(/×\s*(\d+)(?:–(\d+))?/);return m?+(m[2]||m[1]):0}
function render(){
  var i=+sel.value,hist=load(i),last=hist[hist.length-1];list.innerHTML='';
  W[i].x.forEach(function(ex,k){
    var d=document.createElement('div');d.className='ex';var n=nsets(ex[1]);
    var h='<h2>'+ex[0]+'</h2><div class="target">'+ex[1]+'</div>';
    var prev=last&&last.e[k];
    if(prev&&prev.length){
      h+='<div class="last">Last time: '+prev.map(function(s){return (s[0]||'–')+' kg × '+(s[1]||'–')}).join(' · ')+'</div>';
      var t=topRep(ex[1]);if(t&&prev.every(function(s){return +s[1]>=t})) h+='<div class="tip">You hit the top of the range on every set. Add 1–2 kg today.</div>';
    }
    h+='<div class="sets">';
    for(var s=0;s<n;s++){var p=prev&&prev[s]||[];h+='<span>Set '+(s+1)+'</span><input inputmode="decimal" placeholder="kg'+(p[0]?' ('+p[0]+')':'')+'" aria-label="Set '+(s+1)+' kg"><input inputmode="numeric" placeholder="reps'+(p[1]?' ('+p[1]+')':'')+'" aria-label="Set '+(s+1)+' reps">';}
    h+='</div>';
    if(hist.length>1){var f=hist[0].e[k];if(f&&f[0]&&f[0][0]) h+='<div class="hist">First time: '+f[0][0]+' kg · Latest: '+(prev&&prev[0]?prev[0][0]:'–')+' kg</div>';}
    d.innerHTML=h;list.appendChild(d);
  });
  document.getElementById('ok').hidden=true;
}
sel.addEventListener('change',function(){try{localStorage.setItem('km-log:last',sel.value)}catch(e){}render()});
document.getElementById('save').addEventListener('click',function(){
  var i=+sel.value,e=[];
  [].forEach.call(list.querySelectorAll('.ex'),function(d){var ins=d.querySelectorAll('input'),sets=[];for(var j=0;j<ins.length;j+=2){if(ins[j].value||ins[j+1].value)sets.push([ins[j].value,ins[j+1].value])}e.push(sets)});
  var h=load(i);h.push({d:new Date().toISOString().slice(0,10),e:e});store(i,h);render();document.getElementById('ok').hidden=false;
});
try{var l=localStorage.getItem('km-log:last');if(l!==null&&W[+l])sel.value=l}catch(e){}
render();
})();
</script></body></html>
"""
open(os.path.join(HERE, 'log.html'), 'w').write(page.replace('__DATA__', json.dumps(data, ensure_ascii=False)))
print('gata: website/log.html,', len(data), 'antrenamente')
