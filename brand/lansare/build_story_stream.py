#!/usr/bin/env python3
"""Story-urile din 24 nov: „Am anunțat Level Up în stream” (3 cadre, 1080×1920).
Rulezi: python3 brand/lansare/build_story_stream.py -> brand/lansare/out/stream-*.png"""
import os
from build_lansare import OUT, ROOT, FOTO, b64, s, render, STICK

CARD = b64(os.path.join(ROOT, 'brand/twitch/panels/popup-level-up-card.png'), 'image/png')
STORIES = [
 ('stream-1-announced', s('''<div style="position:absolute;inset:0;background:radial-gradient(circle at 30%% 20%%,#3a2a4a,#141118 70%%)"></div>
  <div style="position:absolute;left:80px;top:150px"><span class="tag" style="background:#e91916">● LIVE</span>
   <span class="tag" style="background:#9146ff;margin-left:14px">twitch.tv/kristinemaia</span></div>
  <h1 class="white" style="position:absolute;left:80px;right:80px;top:330px;font-size:132px">Announced it<br>live tonight<br>🎮💗</h1>
  <div style="position:absolute;left:60px;right:60px;top:880px;transform:rotate(-2deg);filter:drop-shadow(0 30px 50px rgba(0,0,0,.5))"><img src="%s" style="width:100%%"></div>
  <p class="white" style="position:absolute;left:80px;right:80px;bottom:240px;font-size:46px;font-weight:700;line-height:1.3;opacity:.92">Thank you chat for the love 🥹<br>Type <b style="color:#c9a7ff">!program</b> on my next stream</p>''' % CARD)),
 ('stream-2-open', s('''<img class="photo" src="%s" style="object-position:42%% 30%%"><div class="shade"></div>
  <div style="position:absolute;left:80px;right:80px;bottom:420px"><span class="tag">NOW OPEN 🚀</span>
  <h1 class="white" style="font-size:140px;margin-top:30px">Level Up</h1>
  <p class="white" style="font-size:50px;font-weight:700;margin:26px 0 0;line-height:1.3">2-min quiz → your plan<br>gym or home · step by step</p></div>''' % FOTO + STICK % (1660, 'link: kristinemaia.com/training'))),
 ('stream-3-price', s('''<div class="sh" style="width:1000px;height:1000px;left:-300px;top:-300px;background:var(--pink)"></div>
  <div class="sh" style="width:600px;height:600px;right:-200px;bottom:-160px;background:var(--lilac)"></div>
  <div style="position:absolute;left:80px;right:80px;top:300px;text-align:center"><span class="tag">FOUNDING PRICE</span>
  <h1 style="font-size:300px;margin-top:40px">$10</h1><p style="font-size:56px;font-weight:800;margin:0">per month</p>
  <p class="sub" style="font-size:46px;margin:40px 0 0;line-height:1.3">only for the first 50 💗<br>kept for as long as you stay.<br>Cancel anytime.</p></div>''' + STICK % (1400, 'link: payhip.com/b/gWIHB'))),
]

if __name__ == '__main__':
    render([(os.path.join(OUT, n + '.png'), h) for n, h in STORIES])
    print('gata')
