#!/usr/bin/env python3
"""Black Friday 27–30 nov 2026: ultimul weekend la prețul de fondator de $10 (de pe 1 dec, $15 pentru membrii noi).
Rulezi: python3 brand/lansare/build_story_bf.py -> brand/lansare/out/bf-*.png"""
import os
from build_lansare import OUT, FOTO, FOTO2, TIMER, REST, s, render, STICK

NEGRU = '<div style="position:absolute;inset:0;background:radial-gradient(circle at 75% 15%,#3a2236,#0e0c10 65%)"></div>'
BF = '<span class="tag" style="background:#fff;color:#0e0c10">🖤 BLACK FRIDAY</span>'
STORIES = [
 ('bf-1-last-weekend', s('''<img class="photo" src="%s" style="object-position:42%% 30%%"><div class="shade" style="background:linear-gradient(180deg,rgba(0,0,0,.15) 20%%,rgba(0,0,0,.85) 70%%)"></div>
  <div style="position:absolute;left:80px;right:80px;bottom:330px">%s
  <h1 class="white" style="font-size:132px;margin-top:30px">Last weekend<br>at $10</h1>
  <p class="white" style="font-size:48px;font-weight:700;margin:28px 0 0;line-height:1.3">Level Up, my training program.<br>Founding price ends Monday.</p></div>''' % (FOTO, BF))),
 ('bf-2-price', s(NEGRU + '''<div style="position:absolute;left:80px;right:80px;top:280px;text-align:center">%s
  <h1 class="white" style="font-size:300px;margin-top:40px">$10</h1><p class="white" style="font-size:56px;font-weight:800;margin:0">per month</p>
  <p style="color:#F8DCE6;font-size:46px;font-weight:700;margin:50px 0 0;line-height:1.35">Join by Monday and keep $10<br>for as long as you stay.</p>
  <p style="color:rgba(255,255,255,.7);font-size:40px;font-weight:600;margin:40px 0 0;line-height:1.35">From Tuesday, 1 December,<br>new members pay $15/month.<br>Cancel anytime.</p></div>''' % BF + STICK % (1500, 'link: payhip.com/b/gWIHB'))),
 ('bf-3-what-you-get', s(NEGRU + '''<div style="position:absolute;left:80px;right:80px;top:200px">%s
  <h1 class="white" style="font-size:104px;margin-top:28px">Your plan,<br>step by step</h1>
  <p style="color:rgba(255,255,255,.8);font-size:42px;font-weight:600;margin:26px 0 0;line-height:1.35">2-min quiz → your week. Gym or home,<br>a video for every exercise, a timer,<br>your weights saved.</p></div>
  <div class="ph" style="width:380px;left:130px;top:960px;transform:rotate(-5deg)"><img src="%s"></div>
  <div class="ph" style="width:380px;left:570px;top:1010px;transform:rotate(5deg)"><img src="%s"></div>''' % (BF, TIMER, REST))),
 ('bf-4-last-day', s(NEGRU + '''<div style="position:absolute;left:80px;right:80px;top:330px;text-align:center">%s
  <h1 class="white" style="font-size:170px;margin-top:40px">LAST<br>DAY</h1>
  <p class="white" style="font-size:54px;font-weight:800;margin:30px 0 0">$10/month ends tonight</p>
  <p style="color:rgba(255,255,255,.7);font-size:42px;font-weight:600;margin:30px 0 0;line-height:1.35">Tomorrow new members pay $15.<br>Join today, keep $10 for as long as you stay.</p></div>''' % BF + STICK % (1460, 'countdown sticker + link: payhip.com/b/gWIHB'))),
]

if __name__ == '__main__':
    render([(os.path.join(OUT, n + '.png'), h) for n, h in STORIES])
    print('gata')
