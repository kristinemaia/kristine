#!/usr/bin/env python3
"""Coperta pentru highlight-ul „Free PDF” de pe Instagram (1080 x 1920; Instagram o taie într-un cerc din centru).

Rulezi:  python3 brand/stories/build_highlight.py
Rezultat: out/Highlight-PDF-coperta.png
Totul important stă în pătratul din mijloc (~620 px)."""
import json, os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
CSS = """
:root{--ink:#2B2431;--pink:#F8DCE6;--berry:#8A3459}
*{box-sizing:border-box}html,body{margin:0}
.s{width:1080px;height:1920px;position:relative;overflow:hidden;background:var(--pink);font-family:'Bricolage Grotesque',sans-serif}
.sheet{position:absolute;left:50%;top:50%;width:360px;height:470px;transform:translate(-50%,-50%) rotate(-4deg);background:#fff;border-radius:28px;box-shadow:0 26px 60px rgba(43,36,49,.22)}
.fold{position:absolute;right:0;top:0;width:96px;height:96px;background:linear-gradient(225deg,var(--pink) 50%,#ead0da 50%);border-top-right-radius:28px;border-bottom-left-radius:18px}
.pdf{position:absolute;left:34px;right:34px;top:150px;text-align:center;font-weight:800;font-size:150px;letter-spacing:-.04em;color:var(--berry);line-height:1}
.l{position:absolute;left:46px;right:46px;height:14px;border-radius:7px;background:#EDE3E8}
.cap{position:absolute;left:0;right:0;bottom:34px;text-align:center;font-weight:800;font-size:42px;letter-spacing:.02em;color:var(--ink)}
"""
HTML = ('<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&display=swap" rel="stylesheet"><style>' + CSS + '</style></head><body>'
 '<div class="s"><div class="sheet"><div class="fold"></div>'
 '<div class="pdf">PDF</div>'
 '<div class="l" style="top:340px"></div><div class="l" style="top:372px;right:130px"></div>'
 '<div class="cap">5 min</div></div></div></body></html>')
JS = r"""
const { chromium } = require('playwright'); const [html, out] = JSON.parse(process.argv[2]);
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
 await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
 await p.screenshot({ path: out }); await b.close(); })();
"""
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as t: t.write(JS)
env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
out = os.path.join(OUT, 'Highlight-PDF-coperta.png')
subprocess.run(['node', t.name, json.dumps([HTML, out])], check=True, env=env); os.unlink(t.name); print('gata:', out)
