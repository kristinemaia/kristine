#!/usr/bin/env python3
"""
Bannerul de profil Twitch pentru Kristine Maia (1200 x 480, raport 5:2).

Rulezi:   python3 brand/twitch/build_banner.py
Rezultat: brand/twitch/banner.html  (sursa)
          brand/twitch/twitch-banner-2400x960.png   (încărcarea principală, ascuțită pe ecrane mari)
          brand/twitch/twitch-banner-1200x480.png   (dimensiunea recomandată de Twitch, dacă o refuză pe prima)

Varianta cu poza ta (poza NU se salvează în repo; se pune doar în fișierele din --out-dir):
          python3 brand/twitch/build_banner.py --photo POZA.jpg --out-dir /un/folder --name twitch-banner-poza
          (--photo = un pătrat decupat cu fața la mijloc; apare într-un cerc, în dreapta)

Culorile și fonturile sunt cele ale site-ului (website/assets/style.css). Ilustrațiile sunt cele din PDF-ul
gratuit (studio/_source/pdf/build_pdf.py). Fără poze, fără adresă web (domeniul nu e conectat încă),
fără locație.
"""
import argparse
import base64
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "studio", "_source", "pdf"))
import build_pdf  # noqa: E402  (are protecție __main__, deci nu rulează nimic la import)

NAME = "Kristine Maia"
TAGLINE = 'Mobility, recovery &amp; good food<br>for people who <em>sit</em> all day'
CHIPS = [("blue", "Move"), ("mint", "Cook with me"), ("lilac", "Game night")]
VIBE_TEXT = "good vibes only"
SPARK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0C13 8 16 11 24 12 16 13 13 16 12 24 11 16 8 13 0 12 8 11 11 8 12 0Z"/></svg>'


HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Kristine Maia · banner Twitch</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@500;600;700&display=swap">
<style>
:root{--bg:#FFF9F6;--paper:#fff;--ink:#2B2431;--muted:#5C5466;
  --pink:#F8DCE6;--pink2:#F1C3D6;--berry:#8A3459;--blue:#DDE9F7;--blue-ink:#2A5580;
  --mint:#D8F0E4;--mint-ink:#1C6550;--lilac:#E9E1F7;--lilac-ink:#4C3A78;
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,sans-serif;--body:"Figtree",ui-sans-serif,system-ui,sans-serif}
*{box-sizing:border-box}
html,body{margin:0;background:#fff}
#b{position:relative;width:1200px;height:480px;overflow:hidden;background:var(--bg);color:var(--ink);font-family:var(--body);-webkit-font-smoothing:antialiased}
.sh{position:absolute;border-radius:50%}
.s1{width:640px;height:640px;left:-250px;top:250px;background:var(--pink)}
.s2{width:520px;height:520px;right:-150px;top:-250px;background:var(--lilac)}
.s3{width:340px;height:340px;right:150px;bottom:-210px;background:var(--mint)}
.s4{width:150px;height:150px;left:430px;top:-70px;background:var(--blue)}
.txt{position:absolute;left:250px;top:0;bottom:0;width:560px;display:flex;flex-direction:column;justify-content:center}
h1{margin:0;font-family:var(--display);font-weight:800;font-size:96px;line-height:.92;letter-spacing:-.04em;white-space:nowrap}
.tag{margin:20px 0 0;font-size:30px;line-height:1.22;font-weight:600;letter-spacing:-.005em}
.tag em{font-style:normal;background:linear-gradient(transparent 56%,var(--pink2) 56%,var(--pink2) 92%,transparent 92%);padding:0 .06em}
.chips{display:flex;gap:10px;margin-top:26px}
.chip{font:700 18px/1 var(--body);padding:13px 20px;border-radius:999px;letter-spacing:.01em;white-space:nowrap}
.chip.blue{background:var(--blue);color:var(--blue-ink)}
.chip.mint{background:var(--mint);color:var(--mint-ink)}
.chip.lilac{background:var(--lilac);color:var(--lilac-ink)}
.vibe{position:absolute;display:flex;align-items:center;gap:9px;padding:11px 20px 11px 16px;border-radius:999px;background:var(--pink2);color:var(--berry);font:800 22px/1 var(--display);letter-spacing:-.01em;white-space:nowrap;transform:rotate(-4deg);box-shadow:0 8px 20px rgba(138,52,89,.18)}
.vibe svg{width:22px;height:22px;display:block;fill:var(--berry)}
.sp{position:absolute;display:block;fill:var(--berry);opacity:.9}
.sp.p2{fill:var(--pink2);opacity:1}
.ic{position:absolute;border-radius:50%;background:var(--paper);box-shadow:0 10px 28px rgba(43,36,49,.12);display:grid;place-items:center}
.ic svg{width:72%;height:72%;display:block}
.ic.a{width:196px;height:196px;left:834px;top:34px}
.ic.b{width:172px;height:172px;left:986px;top:166px}
.ic.c{width:156px;height:156px;left:846px;top:270px}
.ph{position:absolute;left:792px;top:52px;width:376px;height:376px;border-radius:50%;border:8px solid var(--paper);box-shadow:0 14px 36px rgba(43,36,49,.16);overflow:hidden;background:var(--paper)}
.ph img{width:100%;height:100%;object-fit:cover;display:block}
.bd{position:absolute;border-radius:50%;background:var(--paper);box-shadow:0 8px 22px rgba(43,36,49,.14);display:grid;place-items:center}
.bd svg{width:74%;height:74%;display:block}
.bd.n{width:104px;height:104px;left:748px;top:318px}
.bd.s{width:92px;height:92px;left:1098px;top:36px}
</style></head><body>
<div id="b">
  <div class="sh s1"></div><div class="sh s2"></div><div class="sh s3"></div><div class="sh s4"></div>
  <div class="txt">
    <h1>__NAME__</h1>
    <p class="tag">__TAG__</p>
    <div class="chips">__CHIPS__</div>
  </div>
  __ART__
  __VIBE__
</div>
</body></html>
"""


def vibe_html(mode):
    """Cu „good vibes”: un autocolant înclinat lângă nume, cu câteva scântei (sticker), sau nimic (none)."""
    if mode == "sticker":
        return ('<div class="vibe" style="left:598px;top:66px">%s%s</div>'
                '<span class="sp" style="left:566px;top:92px;width:16px;height:16px">%s</span>'
                '<span class="sp p2" style="left:790px;top:24px;width:30px;height:30px">%s</span>'
                '<span class="sp" style="left:812px;top:404px;width:20px;height:20px">%s</span>'
                % (SPARK, VIBE_TEXT, SPARK, SPARK, SPARK))
    return ""


def build_html(photo=None, vibe="sticker"):
    chips = "".join('<span class="chip %s">%s</span>' % (c, t) for c, t in CHIPS)

    if photo:
        data = base64.b64encode(open(photo, "rb").read()).decode()
        art = ('<div class="ph"><img src="data:image/jpeg;base64,%s" alt=""></div>'
               '<div class="bd n">%s</div><div class="bd s">%s</div>') % (data, build_pdf.art_neck(), build_pdf.art_shoulders())
    else:
        art = ('<div class="ic a">%s</div><div class="ic b">%s</div><div class="ic c">%s</div>'
               % (build_pdf.art_neck(), build_pdf.art_shoulders(), build_pdf.art_hips()))
    return HTML.replace("__NAME__", NAME).replace("__TAG__", TAGLINE).replace("__CHIPS__", chips).replace("__ART__", art).replace("__VIBE__", vibe_html(vibe))


RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const [html, out, scale] = process.argv.slice(2);
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 480 }, deviceScaleFactor: Number(scale) });
  const p = await ctx.newPage();
  await p.goto('file://' + html, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  const el = await p.$('#b');
  await el.screenshot({ path: out });
  await b.close();
})();
"""


def render(html_path, out_path, scale):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(RENDER_JS)
        js = f.name
    env = dict(os.environ)
    try:
        root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        env["NODE_PATH"] = root
    except Exception:
        pass
    subprocess.run(["node", js, html_path, out_path, str(scale)], check=True, env=env)
    os.unlink(js)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", help="pătrat decupat cu fața la mijloc (JPG); nu se salvează în repo")
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--name", default="twitch-banner")
    ap.add_argument("--vibe", choices=["sticker", "none"], default="sticker",
                    help="„good vibes”: autocolant înclinat lângă nume (implicit) sau nimic")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    html_path = os.path.join(a.out_dir, a.name + ".html") if a.photo else os.path.join(HERE, "banner.html")
    open(html_path, "w", encoding="utf-8").write(build_html(a.photo, a.vibe))
    big = os.path.join(a.out_dir, a.name + "-2400x960.png")
    render(html_path, big, 2)
    from PIL import Image
    im = Image.open(big).convert("RGB")
    assert im.size == (2400, 960), im.size
    im.save(big, optimize=True)
    small = os.path.join(a.out_dir, a.name + "-1200x480.png")
    im.resize((1200, 480), Image.LANCZOS).save(small, optimize=True)
    print("gata:", big, os.path.getsize(big) // 1024, "KB |", small, os.path.getsize(small) // 1024, "KB")


if __name__ == "__main__":
    main()
