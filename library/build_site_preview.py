# -*- coding: utf-8 -*-
"""Site-ul Kristine Maia, într-un singur fișier HTML (pentru previzualizare ca pagină publicată).

Rulezi:  python3 library/build_site_preview.py [ieșire.html]
Cele 7 pagini devin secțiuni; meniul le schimbă fără să reîncarce; imaginile, stilul și scriptul sunt incluse.
"""
import base64, os, re, sys
SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'website')
PAGES = ['index', 'free', 'training', 'shop', 'live', 'about', 'brands', 'legal']
rd = lambda p: open(os.path.join(SITE, p), encoding='utf-8').read()

def inline_img(m):
    p = m.group(1); ext = p.rsplit('.', 1)[1].lower().replace('jpg', 'jpeg')
    data = base64.b64encode(open(os.path.join(SITE, p), 'rb').read()).decode()
    return 'src="data:image/%s;base64,%s"' % (ext, data)

first = rd('index.html')
head = re.search(r'<header class="top">.*?</header>', first, re.S).group(0)
head = re.sub(r' aria-current="page"', '', head)
foot = re.search(r'<footer class="foot">.*?</footer>', first, re.S).group(0)
title = re.search(r'<title>(.*?)</title>', first, re.S).group(1)
secs = []
for p in PAGES:
    m = re.search(r'<main id="main">(.*?)</main>', rd(p + '.html'), re.S).group(1)
    m = re.sub(r'src="(assets/[^"]+\.(?:jpg|png))"', inline_img, m)
    secs.append('<main class="page" data-page="%s" hidden>%s</main>' % (p, m))
css = rd('assets/style.css'); js = rd('assets/site.js')
router = """
(function(){
  var pages=[].slice.call(document.querySelectorAll('main.page'));
  function show(name,anchor){
    if(!pages.some(function(p){return p.dataset.page===name;})) name='index';
    pages.forEach(function(p){p.hidden=p.dataset.page!==name;});
    [].forEach.call(document.querySelectorAll('.nav a'),function(a){
      if(a.dataset.go===name) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current');});
    var cur=document.querySelector('main.page[data-page="'+name+'"]');
    var el=anchor&&cur.querySelector('#'+anchor);
    if(el) el.scrollIntoView(); else window.scrollTo(0,0);
  }
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href]'); if(!a) return;
    var h=a.getAttribute('href'), m=h.match(/^(index|free|training|shop|live|about|brands|legal)\\.html(?:#(.+))?$/);
    if(m){e.preventDefault(); show(m[1],m[2]); try{history.replaceState(null,'','#'+m[1]);}catch(x){}
      var nav=document.getElementById('nav-links'); if(nav&&nav.classList.contains('open')) document.querySelector('.menu-btn').click(); return;}
    if(h==='#main'){e.preventDefault(); window.scrollTo(0,0); return;}
    if(h.charAt(0)==='#'&&h.length>1){var cur=document.querySelector('main.page:not([hidden])'), t=cur&&cur.querySelector(h);
      if(t){e.preventDefault(); t.scrollIntoView();}}
  });
  [].forEach.call(document.querySelectorAll('a[href$=".html"],a[href*=".html#"]'),function(a){
    var m=a.getAttribute('href').match(/^(index|free|training|shop|live|about|brands|legal)\\.html/); if(m) a.dataset.go=m[1];});
  show((location.hash||'').replace('#','')||'index');
})();
"""
out = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
 '<title>Kristine Maia site preview</title>'
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">'
 '<style>' + css + '\nmain.page[hidden]{display:none!important}</style></head><body>'
 '<a class="skip" href="#main">Skip to content</a>' + head + ''.join(secs) + foot +
 '<script>' + js + '</script><script>' + router + '</script></body></html>')
dst = sys.argv[1] if len(sys.argv) > 1 else 'site-preview-single.html'
open(dst, 'w', encoding='utf-8').write(out); print('gata', dst, round(len(out) / 1024), 'KB')
