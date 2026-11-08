#!/usr/bin/env python3
"""Overlay-ul de stream (PNG transparente 1920x1080, se pun în OBS peste cameră):
  overlay-complet.png   colțuri: comenzile (stânga jos), site-ul (stânga sus), recompensele scurte (dreapta jos),
                        trei carduri goale pentru obiective (dreapta sus) în care pui widget-urile de goal din StreamElements
  recompense.png        doar lista scurtă de recompense (dacă vrei s-o muți singură)
Rulezi: python3 brand/twitch/build_overlay.py → brand/twitch/overlay/"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_stream_videos as B
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overlay'); os.makedirs(OUT, exist_ok=True)
REWARDS = [('1 sub', 'you pick my next 30-second stretch'), ('5 subs', '2-minute move break with chat'),
           ('500 bits', '10 squats live'), ('700 bits', 'flex check 💪'), ('1,000 bits', '1-minute plank'),
           ('2,500 bits', '10-minute mobility flow with chat'), ('5,000 bits', 'chat picks the next Cook with me recipe')]
GOALS = ['MOBILITY TIME', 'NEW GYM GEAR', 'DAILY SUBS']
CARD = 'background:rgba(255,249,246,.92);border:3px solid #EADFE6;border-radius:26px;box-shadow:0 10px 30px rgba(0,0,0,.25)'
def rewards_html():
    rows = ''.join('<div style="display:flex;gap:14px;align-items:baseline;margin-top:10px"><span style="font-weight:800;color:#8A3459;min-width:150px">%s</span>'
                   '<span style="font-weight:600">%s</span></div>' % r for r in REWARDS)
    return ('<div style="%s;padding:20px 26px;width:470px;font-size:21px;color:#2B2431">'
            '<div style="font-family:\'Bricolage Grotesque\';font-weight:800;font-size:30px">Make me move</div>%s</div>') % (CARD, rows)
def goals_html():
    return ''.join('<div style="%s;padding:16px 24px;width:400px;height:112px;margin-bottom:18px">'
                   '<div style="font-weight:800;font-size:22px;letter-spacing:.08em;color:#8A3459">%s</div>'
                   '<div style="margin-top:12px;height:30px;border-radius:99px;border:2px dashed #D9C7D1"></div></div>' % (CARD, g) for g in GOALS)
full = ('<div class="s">'
        '<div style="position:absolute;right:36px;top:36px">' + goals_html() + '</div>'
        '<div style="position:absolute;right:36px;bottom:36px">' + rewards_html() + '</div>'
        '<div style="position:absolute;left:36px;bottom:36px;display:flex;gap:14px">'
        '<span class="pill" style="background:#2B2431;color:#fff;font-size:26px;padding:14px 26px">!stretch every 30 min</span>'
        '<span class="pill" style="background:#8A3459;color:#fff;font-size:26px;padding:14px 26px">!coaching · !program</span></div>'
        '<div style="position:absolute;left:36px;top:36px"><span class="pill" style="background:rgba(255,249,246,.92);color:#2B2431;font-size:24px;padding:12px 24px;border:3px solid #EADFE6">kristinemaia.com</span></div>'
        '</div>')
only = '<div class="s"><div style="position:absolute;right:36px;bottom:36px">' + rewards_html() + '</div></div>'
B.render([(os.path.join(OUT, 'overlay-complet.png'), full), (os.path.join(OUT, 'recompense.png'), only)])
print('gata', OUT)
