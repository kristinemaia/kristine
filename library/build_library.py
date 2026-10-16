#!/usr/bin/env python3
"""
Construiește „Biblioteca Kristinei”: pagina fixată în claude.ai cu toate PDF-urile,
documentele și folderele (zip) făcute în proiect.

Rulezi:   python3 library/build_library.py
Rezultat: library/dist/   (se publică cu instrumentul Artifact, pagina = dist/index.html)

- Documentele .md sunt convertite în pagini HTML cu pandoc (fără HTML brut).
- PDF-urile au previzualizare din imagini (PDF-ul în sine nu se vede sigur într-un cadru).
- „Salvează” folosește capabilitatea `downloads` (merge doar în vizualizatorul claude.ai).
- Documentele care nu sunt în repo (încărcări, emailuri) se caută în folderul scratchpad
  din variabila de mediu SCRATCH; dacă lipsesc, sunt sărite cu un avertisment.
"""
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST = os.path.join(REPO, "library", "dist")
SCRATCH = os.environ.get(
    "SCRATCH", "/tmp/claude-0/-home-user-kristine/76209f14-ae6c-52ab-b9be-ac2315dadd03/scratchpad"
)
IGDIR = os.environ.get("IGDIR", os.path.join(SCRATCH, "ig"))
TRACKER_URL = "https://claude.ai/artifact/JPWB5qYKDdc63vJ1QG35yM"
TITLE = "Biblioteca Kristinei"

# ----------------------------------------------------------------------
# Ce intră în bibliotecă
# ----------------------------------------------------------------------
# kind: link | pdf | doc | img | site
GROUPS = [
    {
        "id": "studio", "name": "Studio", "note": "PDF-ul gratuit, programul de 30 de zile, reel-urile",
        "zip": ("Studio-Kristine.zip", "studio"),
        "items": [
            {"kind": "doc", "slug": "filmare-apartament", "title": "Reel-urile de filmat în apartament (15–16 oct)",
             "src": "studio/FILMARE-APARTAMENT.md", "desc": "Tabelul cu toate reel-urile, ordinea de filmat și fiecare reel pe rând: poziții, secunde, lumină, text, descriere, hashtag-uri, data postării."},
            {"kind": "pdf", "slug": "desk-stretch", "title": "The 5-minute desk stretch (3 pagini)",
             "src": "studio/5-minute-desk-stretch.pdf", "name": "5-minute-desk-stretch.pdf",
             "desc": "PDF-ul gratuit: afișul de 5 minute, cum faci fiecare mișcare, fișa de 7 zile."},
            {"kind": "pdf", "slug": "poster", "title": "Afișul de o pagină",
             "src": "studio/5-minute-desk-stretch-poster.pdf", "name": "5-minute-desk-stretch-poster.pdf",
             "desc": "Pagina 1 singură, pentru print, Instagram și panoul de Twitch."},
            {"kind": "doc", "slug": "pdf-ghid", "title": "Ghidul PDF-ului", "src": "studio/PDF-GHID.md",
             "desc": "Cum îl refaci cu pozele tale, cum ajunge la oameni pe email, lista de verificare."},
            {"kind": "doc", "slug": "program-30-zile", "title": "Programul de 30 de zile: lista de filmare",
             "src": "studio/PROGRAM-30-ZILE.md",
             "desc": "38 de clipuri, introduceri și încheieri, programul de filmare pe 4 zile, montajul."},
            {"kind": "doc", "slug": "reeluri-studio", "title": "Reel-uri din studio",
             "src": "studio/REELURI-STUDIO.md",
             "desc": "Ce filmezi în living, bucătărie și la birou, și ce repari în e-book înainte să-l arăți."},
            {"kind": "doc", "slug": "ebook-v2", "title": "E-book v2: textele de pus în Canva",
             "src": "studio/EBOOK-V2-TEXTS.md",
             "desc": "Textele noi, pagină cu pagină, corecturile și setările de export. Din discuția cu Claude de pe desktop."},
        ],
    },
    {
        "id": "instagram", "name": "Instagram", "note": "Ce rămâne pe pagină și ce se arhivează",
        "zip": ("Instagram-Kristine.zip", "instagram"),
        "items": [
            {"kind": "doc", "slug": "instagram-curatare", "title": "Instagram: ce rămâne și ce se arhivează",
             "src": "INSTAGRAM-CURATARE.md",
             "desc": "Verdict pe primele 30 de postări, pașii pentru monetizare, regula 70/30."},
            {"kind": "img", "slug": "instagram-foi", "title": "Foile cu verdict (2 imagini)",
             "images": ["verdict-v2-grila-1.png", "verdict-v2-grila-2.png"],
             "desc": "Grila ta în ordine, cu un verdict pe fiecare postare."},
        ],
    },
    {
        "id": "brand", "name": "Brand", "note": "Bannere și imagini pentru conturile tale",
        "zip": ("Brand-Kristine.zip", "brand"),
        "items": [
            {"kind": "img", "slug": "payhip-img", "title": "Imaginile pentru Payhip",
             "base": "brand/payhip", "keep": True,
             "images": ["payhip-logo-1000x1000.png", "payhip-logo-orizontal-1200x300.png", "payhip-produs-1280x720.png", "payhip-produs-1080x1080.png", "payhip-banner-1500x500.png"],
             "desc": "Logo-ul magazinului (pătrat și orizontal, fundal transparent), coperta PDF-ului gratuit (lată și pătrată) și bannerul."},
            {"kind": "img", "slug": "km-carusele", "title": "Carusele KM (20 de imagini)",
             "base": "brand/km/out", "keep": True,
             "images": ["KM-C1-masaj-de-recuperare-%d.png" % i for i in range(1, 6)] + ["KM-C2-drenaj-limfatic-%d.png" % i for i in range(1, 6)] + ["KM-C3-sedinta-pas-cu-pas-%d.png" % i for i in range(1, 6)] + ["KM-C4-obiceiuri-birou-%d.png" % i for i in range(1, 6)],
             "desc": "Patru carusele de câte 5 slide-uri, 1080 × 1350, gata de urcat pe @kmwellnessconcept."},
            {"kind": "img", "slug": "twitch-banner", "title": "Bannerul Twitch (2 mărimi)",
             "base": "brand/twitch", "keep": True,
             "images": ["twitch-banner-2400x960.png", "twitch-banner-1200x480.png"],
             "desc": "Cel nou, în stilul site-ului. Încarci prima imagine; dacă Twitch o refuză, o încerci pe a doua."},
        ],
    },
    {
        "id": "plan", "name": "Plan", "note": "Strategie, conținut, bani, mutare",
        "zip": ("Plan-Kristine.zip", "plan"),
        "items": [
            {"kind": "doc", "slug": "payhip", "title": "Payhip, pas cu pas (PDF-ul gratuit)", "src": "PAYHIP-PAS-CU-PAS.md",
             "desc": "Ce e Payhip, profilul, produsul gratuit, textele în engleză, testul și unde pui linkul."},
            {"kind": "pdf", "slug": "calendar", "title": "Calendarul săptămânal, de printat (17 oct – 15 nov)",
             "src": "calendar/Calendar-saptamanal.pdf", "name": "Calendar-saptamanal.pdf",
             "desc": "O pagină pe săptămână, pe zile, colorat pe tipuri (stream, conținut, postare, bani, sală, viață), cu loc de notițe; plus o pagină goală pentru săptămânile următoare."},
            {"kind": "doc", "slug": "lista-cumparaturi", "title": "Lista de cumpărături pentru weekend (17–18 oct)", "src": "LISTA-CUMPARATURI-WEEKEND.md",
             "desc": "Ingrediente pentru clătite, bolul cu ton și poza de copertă, cu căsuțe de bifat."},
            {"kind": "doc", "slug": "carusele-km", "title": "Carusele pentru contul KM (4, în română)", "src": "CARUSELE-KM.md",
             "desc": "Calendarul, descrierile și hashtag-urile; imaginile sunt în Brand."},
            {"kind": "doc", "slug": "plan-turcia", "title": "Planul 15 octombrie – 15 noiembrie", "src": "PLAN-TURCIA.md",
             "desc": "România până pe 28 oct, Turcia până pe 15 nov: ce filmezi, ce programezi și ce faci zi cu zi."},
            {"kind": "doc", "slug": "emailuri-contabila-avocat", "title": "Emailuri către contabilă și avocat",
             "src": "EMAILURI-CONTABILA-AVOCAT.md", "desc": "Două emailuri gata de copiat, cu întrebările pentru Turcia."},
            {"kind": "doc", "slug": "plan", "title": "Planul Kristinei", "src": "PLAN.md",
             "desc": "Brandul, veniturile și pașii (v5, 11 octombrie)."},
            {"kind": "doc", "slug": "roadmap", "title": "Roadmap, în engleză", "src": "@ROADMAP.md",
             "desc": "Planul pe 90 de zile și produsele, construit pe exemple de oameni care au făcut asta. Încărcat de tine."},
            {"kind": "doc", "slug": "plan-pe-zile", "title": "Planul pe zile, primele 4 săptămâni",
             "src": "@PLAN-PE-ZILE.md", "desc": "Ce faci în fiecare zi: stream-uri, reel-uri, emailuri. Încărcat de tine."},
            {"kind": "doc", "slug": "continut", "title": "Planul de conținut", "src": "CONTINUT.md",
             "desc": "Pilonii, formatele și ritmul pe săptămână."},
            {"kind": "doc", "slug": "filmare-sala", "title": "Filmarea reel-urilor la sală", "src": "@FILMARE-SALA.md",
             "desc": "Pas cu pas, pentru sala din București."},
            {"kind": "doc", "slug": "emailuri-branduri", "title": "Primele 6 emailuri către branduri",
             "src": "EMAILURI-BRANDURI.md", "desc": "Texte gata de trimis și cum le trimiți."},
            {"kind": "doc", "slug": "mutare", "title": "Mutarea din apartament", "src": "MUTARE.md",
             "desc": "Decizia, pașii și mesajul pentru proprietar."},
            {"kind": "doc", "slug": "stergere-continut", "title": "Ștergerea conținutului vechi",
             "src": "STERGERE-CONTINUT.md", "desc": "Ordinea formularelor și șablonul DMCA."},
            {"kind": "doc", "slug": "conversatie", "title": "Conversația noastră, rezumat",
             "src": "CONVERSATIE.md", "desc": "Ce mi-ai spus și ce am răspuns, în ordine cronologică (10–11 octombrie)."},
        ],
    },
    {
        "id": "site", "name": "Site web", "folder": "Site", "note": "kristinemaia.com, înainte să fie online",
        "zip": ("Site-Kristine.zip", "site"),
        "items": [
            {"kind": "site", "title": "Site-ul (previzualizare)", "href": "site/index.html",
             "desc": "Cele 8 pagini: home, free, shop, live, terapie, brands, about, legal."},
            {"kind": "doc", "slug": "site-readme", "title": "Cum pui site-ul online", "src": "website/README.md",
             "desc": "Paginile, ce trebuie completat (TODO) și cum îl publici gratuit."},
        ],
    },
    {
        "id": "tracker", "name": "Tracker", "note": "Bifezi ce ai rezolvat",
        "items": [
            {"kind": "link", "title": "Pașii Kristinei", "url": TRACKER_URL,
             "desc": "Lista ta pe categorii și pe zile, cu săptămâna de studio inclusă."},
        ],
    },
]

KIND_LABEL = {"link": "LINK", "pdf": "PDF", "doc": "DOC", "img": "IMG", "site": "SITE"}
KIND_FILTER = [("all", "Toate"), ("pdf", "PDF"), ("doc", "Documente"), ("img", "Imagini"), ("site", "Site și linkuri")]
FILTER_OF = {"pdf": "pdf", "doc": "doc", "img": "img", "site": "site", "link": "site"}

# ----------------------------------------------------------------------
# Utilitare
# ----------------------------------------------------------------------
warnings = []


def esc(s):
    return html.escape(s, quote=True)


def norm(s):
    import unicodedata
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def fmt_size(n):
    if n < 1024 * 1024:
        return "%d KB" % max(1, round(n / 1024))
    return ("%.1f MB" % (n / 1024 / 1024)).replace(".", ",")


def date_of(path):
    """Data ultimei modificări: din git pentru fișiere din repo, altfel din mtime."""
    rel = os.path.relpath(path, REPO)
    if not rel.startswith(".."):
        try:
            out = subprocess.run(
                ["git", "-C", REPO, "log", "-1", "--format=%cd", "--date=format:%d.%m.%Y", "--", rel],
                capture_output=True, text=True, timeout=20,
            ).stdout.strip()
            if out:
                return out
        except Exception:
            pass
    return datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d.%m.%Y")


def resolve(src):
    """'@NUME.md' = din scratchpad; altfel relativ la repo."""
    if src.startswith("@"):
        return os.path.join(SCRATCH, src[1:])
    return os.path.join(REPO, src)


def ensure(*parts):
    p = os.path.join(DIST, *parts)
    os.makedirs(p, exist_ok=True)
    return p


# ----------------------------------------------------------------------
# CSS și șabloane
# ----------------------------------------------------------------------
FONTS = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700'
    '&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">'
)

BASE_CSS = """
/* Biblioteca: o coloană, grupuri pe foldere; aceleași culori ca trackerul */
:root{
  --bg:#F2F5F4; --surface:#FFFFFF; --fg:#16201D; --muted:#5A6A66; --line:#D6E0DC;
  --accent:#0E7A6A; --accent-soft:#DDF1EC; --accent-ink:#FFFFFF;
  --pdf:#A8372F; --pdf-soft:#F8E3E1; --doc:#2B66A8; --doc-soft:#E1ECF8;
  --img:#8A5A12; --img-soft:#F7ECD9; --site:#5B4B9A; --site-soft:#ECE8F8;
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,sans-serif;
  --body:"Figtree",ui-sans-serif,system-ui,-apple-system,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0E1412; --surface:#16201D; --fg:#E4EDEA; --muted:#91A29D; --line:#273531;
  --accent:#3FC3A8; --accent-soft:#16342D; --accent-ink:#0E1412;
  --pdf:#F0908C; --pdf-soft:#3A1F1E; --doc:#7FB0E8; --doc-soft:#1A2A3C;
  --img:#E3B266; --img-soft:#33281A; --site:#B7A8F0; --site-soft:#251F3D; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0E1412; --surface:#16201D; --fg:#E4EDEA; --muted:#91A29D; --line:#273531;
  --accent:#3FC3A8; --accent-soft:#16342D; --accent-ink:#0E1412;
  --pdf:#F0908C; --pdf-soft:#3A1F1E; --doc:#7FB0E8; --doc-soft:#1A2A3C;
  --img:#E3B266; --img-soft:#33281A; --site:#B7A8F0; --site-soft:#251F3D; color-scheme:dark}
*{box-sizing:border-box}
[hidden]{display:none!important}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.5;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 56px}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
/* documente */
.doc{min-width:0;overflow-wrap:anywhere}
.doc h1{font-family:var(--display);font-size:clamp(26px,5.5vw,34px);line-height:1.12;margin:0 0 .6em;text-wrap:balance;letter-spacing:-.01em}
.doc h2{font-family:var(--display);font-size:clamp(21px,4.4vw,25px);line-height:1.2;margin:1.9em 0 .5em;text-wrap:balance}
.doc h3{font-family:var(--display);font-size:18px;line-height:1.25;margin:1.5em 0 .4em}
.doc h4{font-size:16px;margin:1.2em 0 .3em}
.doc p,.doc li{max-width:70ch}
.doc p{margin:.7em 0}
.doc ul,.doc ol{padding-left:1.4em}
.doc li{margin:.25em 0}
.doc li>p{margin:.2em 0}
.doc hr{border:0;border-top:1px solid var(--line);margin:2em 0}
.doc blockquote{margin:1em 0;padding:8px 16px;border-left:3px solid var(--accent);background:var(--accent-soft);border-radius:0 10px 10px 0}
.doc blockquote p{margin:.4em 0}
.doc code{font-family:var(--mono);font-size:.88em;background:var(--accent-soft);padding:1px 6px;border-radius:5px}
.doc pre{overflow-x:auto;background:var(--surface);border:1px solid var(--line);padding:12px 14px;border-radius:10px}
.doc pre code{background:none;padding:0}
.doc .tw{overflow-x:auto;margin:1em 0;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
.doc table{border-collapse:collapse;font-size:14px;min-width:100%}
.doc th,.doc td{padding:8px 11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.doc th{background:var(--accent-soft);font-weight:600;white-space:nowrap}
.doc tr:last-child td{border-bottom:0}
.doc input[type=checkbox]{margin-right:.5em}
.doc li:has(>input[type=checkbox]){list-style:none;margin-left:-1.2em}
.toc{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 16px;margin:0 0 22px}
.toc summary{cursor:pointer;font-weight:600}
.toc ul{list-style:none;padding-left:14px;margin:6px 0}
.toc>ul{padding-left:0}
.toc li{margin:.3em 0;font-size:15px}
.toc a{text-decoration:none}
.bar{display:flex;align-items:center;gap:12px;max-width:760px;margin:0 auto 14px}
.bar a{font-weight:600;text-decoration:none}
.wrap{max-width:760px;margin:0 auto}
.pages{display:grid;gap:18px}
.pages figure{margin:0}
.pages img{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:8px;background:#fff}
.pages figcaption{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:13px;color:var(--muted);margin-top:8px}
"""

HUB_CSS = """
#app{max-width:760px;margin:0 auto;display:grid;gap:18px}
.top h1{font-family:var(--display);font-size:clamp(28px,6vw,38px);line-height:1.1;margin:0;text-wrap:balance;letter-spacing:-.01em}
.lede{margin:8px 0 0;color:var(--muted);max-width:60ch}
.count{margin:6px 0 0;font-family:var(--mono);font-size:12.5px;color:var(--muted)}
.tools{display:grid;gap:10px}
.search{width:100%;font:inherit;color:var(--fg);background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:11px 14px;min-height:46px}
.search::placeholder{color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font:inherit;font-size:14px;color:var(--fg);border:1px solid var(--line);background:var(--surface);border-radius:99px;padding:6px 13px;cursor:pointer;min-height:36px}
.chip[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.all{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;background:var(--accent-soft);border-radius:14px;padding:12px 16px}
.all p{margin:0;font-size:14.5px}
.grp{background:var(--surface);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.grp>summary{list-style:none;cursor:pointer;padding:14px 16px;display:flex;align-items:center;gap:12px}
.grp>summary::-webkit-details-marker{display:none}
.grp>summary::after{content:"";flex:none;width:8px;height:8px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);transform:rotate(45deg);margin:-3px 4px 0 0;transition:transform .15s}
.grp[open]>summary::after{transform:rotate(-135deg);margin-top:3px}
.gtxt{flex:1;min-width:0}
.grp h2{font-family:var(--display);font-size:20px;margin:0;line-height:1.2}
.gnote{display:block;font-size:13.5px;color:var(--muted)}
.gcount{flex:none;font-family:var(--mono);font-size:13px;color:var(--muted)}
.grp[open]>summary{border-bottom:1px solid var(--line)}
.zipbar{display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:10px 16px;background:var(--bg);border-top:1px solid var(--line);font-size:14px;color:var(--muted)}
ul.list{list-style:none;margin:0;padding:0}
.item{display:grid;grid-template-columns:auto 1fr;gap:6px 12px;padding:13px 16px;border-top:1px solid var(--line)}
.item:first-child{border-top:0}
.tag{font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.05em;padding:3px 0;border-radius:6px;min-width:48px;text-align:center;align-self:start;margin-top:3px}
.tag-pdf{background:var(--pdf-soft);color:var(--pdf)}
.tag-doc{background:var(--doc-soft);color:var(--doc)}
.tag-img{background:var(--img-soft);color:var(--img)}
.tag-site,.tag-link{background:var(--site-soft);color:var(--site)}
.txt{min-width:0}
.t{font-weight:600;font-size:16.5px;text-decoration:none;color:var(--fg);overflow-wrap:anywhere}
.t:hover{text-decoration:underline}
.d{margin:2px 0 0;font-size:14.5px;color:var(--muted)}
.m{margin:3px 0 0;font-family:var(--mono);font-size:12px;color:var(--muted)}
.acts{grid-column:2;display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}
.b{font:inherit;font-size:14px;font-weight:600;border-radius:10px;padding:8px 15px;min-height:40px;border:1px solid var(--line);background:var(--surface);color:var(--fg);cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center}
.b:hover{border-color:var(--accent)}
.b-main{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.b[disabled]{opacity:.55;cursor:default}
@media (min-width:640px){
  .item{grid-template-columns:auto 1fr auto;align-items:center}
  .acts{grid-column:3;margin-top:0}
}
#none,.foot{color:var(--muted);font-size:14px}
.foot{margin:0}
.reader{position:fixed;inset:0;z-index:20;background:var(--bg);overflow:auto;overscroll-behavior:contain;
  padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
.rbar{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:10px;background:var(--bg);border-bottom:1px solid var(--line);
  padding:10px max(16px,env(safe-area-inset-right,0px)) 10px max(16px,env(safe-area-inset-left,0px))}
.rtitle{flex:1;min-width:0;margin:0;font-family:var(--display);font-size:16px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rbody{max-width:760px;margin:0 auto;padding:20px max(16px,env(safe-area-inset-right,0px)) 72px max(16px,env(safe-area-inset-left,0px))}
.status{color:var(--muted)}
#toast{position:fixed;left:50%;bottom:max(22px,env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:30;max-width:min(92vw,440px);
  background:var(--fg);color:var(--bg);padding:11px 16px;border-radius:12px;font-size:14px;box-shadow:0 6px 24px rgba(0,0,0,.25)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@media (prefers-reduced-motion:reduce){.grp>summary::after{transition:none}}
"""

DOC_PAGE = """<!doctype html>
<html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="claude:viewport-fit-sides" content="cover">
<title>@@TITLE@@ · Biblioteca Kristinei</title>
@@FONTS@@
<style>@@CSS@@</style></head>
<body>
<div class="bar"><a href="../index.html">← Biblioteca</a></div>
<main class="doc wrap">
@@BODY@@
</main>
</body></html>
"""

FRAG_TPL = '$if(toc)$<nav id="TOC">\n$toc$\n</nav>\n$endif$\n$body$\n'

JS = r"""
(function(){
  'use strict';
  function $(s, r){ return (r || document).querySelector(s); }
  function $$(s, r){ return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  var COMBINING = new RegExp('[' + String.fromCharCode(768) + '-' + String.fromCharCode(879) + ']', 'g');
  function norm(s){ return String(s).toLowerCase().normalize('NFD').replace(COMBINING, ''); }

  /* ---------- căutare și filtre ---------- */
  var state = { q: '', kind: 'all' };
  function applyFilter(){
    var shown = 0;
    $$('.grp').forEach(function(g){
      var n = 0;
      $$('.item', g).forEach(function(li){
        var okK = state.kind === 'all' || li.dataset.filter === state.kind;
        var okQ = !state.q || li.dataset.text.indexOf(state.q) !== -1;
        li.hidden = !(okK && okQ);
        if (!li.hidden) n++;
      });
      g.hidden = n === 0;
      var c = $('.gcount', g); if (c) c.textContent = n;
      shown += n;
    });
    $('#none').hidden = shown !== 0;
  }
  $('#q').addEventListener('input', function(e){ state.q = norm(e.target.value.trim()); applyFilter(); });
  $$('.chip').forEach(function(c){
    c.addEventListener('click', function(){
      state.kind = c.dataset.kind;
      $$('.chip').forEach(function(x){ x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
      applyFilter();
    });
  });

  /* ---------- salvare (capabilitatea downloads) ---------- */
  var dlP = null;
  function getDl(){
    if (!dlP) {
      dlP = (window.claude && typeof window.claude.use === 'function')
        ? window.claude.use('downloads').catch(function(){ return null; })
        : Promise.resolve(null);
    }
    return dlP;
  }
  var toastT = null;
  function toast(msg){
    var t = $('#toast'); t.textContent = msg; t.hidden = false;
    clearTimeout(toastT); toastT = setTimeout(function(){ t.hidden = true; }, 4500);
  }
  function saveFile(url, name, btn){
    return getDl().then(function(dl){
      if (!dl) { toast('Salvarea directă nu e disponibilă aici. Folosește „Deschide fișierul”.'); return; }
      var old = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Se pregătește…'; }
      return fetch(url)
        .then(function(r){ if (!r.ok) throw { code: 'fetch' }; return r.blob(); })
        .then(function(b){ return dl.save({ filename: name, data: b }); })
        .then(function(){ toast('Salvat: ' + name); })
        .catch(function(e){
          var c = e && e.code;
          if (c === 'declined') return;
          toast(c === 'rate_limited' ? 'Așteaptă o clipă și încearcă din nou.' : 'Nu s-a putut salva. Încearcă „Deschide fișierul”.');
        })
        .then(function(){ if (btn) { btn.disabled = false; btn.textContent = old; } });
    });
  }
  /* fără downloads: butoanele „Salvează” devin linkuri „Deschide fișierul” */
  getDl().then(function(dl){
    if (dl) return;
    $$('[data-act="save"]').forEach(function(b){
      var a = document.createElement('a');
      a.className = b.className; a.href = b.dataset.file; a.target = '_blank'; a.rel = 'noopener';
      a.textContent = 'Deschide fișierul';
      b.parentNode.replaceChild(a, b);
    });
  });


  /* ---------- arhive .zip create în pagină, din fișierele publicate ---------- */
  var CRC = (function(){ var t = new Uint32Array(256); for (var n = 0; n < 256; n++) { var c = n; for (var k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1); t[n] = c >>> 0; } return t; })();
  function crc32(u8){ var c = 0xFFFFFFFF; for (var i = 0; i < u8.length; i++) c = CRC[(c ^ u8[i]) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; }
  function w16(v){ return [v & 255, (v >>> 8) & 255]; }
  function w32(v){ return [v & 255, (v >>> 8) & 255, (v >>> 16) & 255, (v >>> 24) & 255]; }
  function zipStore(files){
    var enc = new TextEncoder(), parts = [], central = [], offset = 0, now = new Date();
    var dt = (now.getHours() << 11) | (now.getMinutes() << 5) | (now.getSeconds() >> 1);
    var dd = ((now.getFullYear() - 1980) << 9) | ((now.getMonth() + 1) << 5) | now.getDate();
    files.forEach(function(f){
      var name = enc.encode(f.name), crc = crc32(f.data), size = f.data.length;
      var local = [].concat(w32(0x04034b50), w16(20), w16(0x0800), w16(0), w16(dt), w16(dd), w32(crc), w32(size), w32(size), w16(name.length), w16(0));
      var cen = [].concat(w32(0x02014b50), w16(20), w16(20), w16(0x0800), w16(0), w16(dt), w16(dd), w32(crc), w32(size), w32(size), w16(name.length), w16(0), w16(0), w16(0), w16(0), w32(0), w32(offset));
      parts.push(new Uint8Array(local), name, f.data);
      central.push(new Uint8Array(cen), name);
      offset += local.length + name.length + size;
    });
    var cdSize = central.reduce(function(a, c){ return a + c.length; }, 0);
    var end = [].concat(w32(0x06054b50), w16(0), w16(0), w16(files.length), w16(files.length), w32(cdSize), w32(offset), w16(0));
    return new Blob(parts.concat(central, [new Uint8Array(end)]), { type: 'application/zip' });
  }
  var ZIPS = {};
  try { ZIPS = JSON.parse($('#zips').textContent.replace(/&lt;/g, '<')); } catch (e) {}
  function saveZip(key, btn){
    var def = ZIPS[key]; if (!def) return;
    return getDl().then(function(dl){
      if (!dl) { toast('Arhivele se pot salva doar în aplicația Claude sau în claude.ai.'); return; }
      var old = btn.textContent; btn.disabled = true;
      var done = 0, total = def.entries.length;
      btn.textContent = 'Se pregătește… 0/' + total;
      return Promise.all(def.entries.map(function(en){
        return fetch(en[1]).then(function(r){ if (!r.ok) throw { code: 'fetch' }; return r.arrayBuffer(); })
          .then(function(buf){ done++; btn.textContent = 'Se pregătește… ' + done + '/' + total; return { name: en[0], data: new Uint8Array(buf) }; });
      })).then(function(files){ return dl.save({ filename: def.name, data: zipStore(files) }); })
        .then(function(){ toast('Salvat: ' + def.name); })
        .catch(function(e){
          var c = e && e.code;
          if (c === 'declined') return;
          toast(c === 'rate_limited' ? 'Așteaptă o clipă și încearcă din nou.' : 'Nu s-a putut crea arhiva.');
        })
        .then(function(){ btn.disabled = false; btn.textContent = old; });
    });
  }
  getDl().then(function(dl){ if (!dl) $$('[data-act="zip"]').forEach(function(b){ var bar = b.closest('.zipbar, .all'); (bar || b).hidden = true; }); });

  /* ---------- cititorul ---------- */
  var reader = $('#reader'), rbody = $('#rbody'), rtitle = $('#rtitle'), rsave = $('#rsave'), rback = $('#rback'), app = $('#app');
  var lastFocus = null;
  function openReader(title){
    lastFocus = document.activeElement;
    rtitle.textContent = title;
    rbody.innerHTML = '';
    rsave.hidden = true; rsave.dataset.file = ''; rsave.dataset.name = '';
    reader.hidden = false;
    try { app.inert = true; } catch (e) {}
    reader.scrollTop = 0;
    rback.focus();
  }
  function closeReader(){
    reader.hidden = true;
    try { app.inert = false; } catch (e) {}
    rbody.innerHTML = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  function setSave(file, name, label){
    rsave.dataset.file = file; rsave.dataset.name = name; rsave.textContent = label; rsave.hidden = false;
    getDl().then(function(dl){
      if (dl) return;
      rsave.hidden = true;
    });
  }
  rback.addEventListener('click', closeReader);
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape' && !reader.hidden) closeReader(); });

  function loadDoc(li){
    openReader(li.dataset.title);
    setSave(li.dataset.src, li.dataset.srcname, 'Salvează .md');
    rbody.innerHTML = '<p class="status">Se încarcă…</p>';
    fetch(li.dataset.href)
      .then(function(r){ if (!r.ok) throw new Error(r.status); return r.text(); })
      .then(function(t){
        var d = new DOMParser().parseFromString(t, 'text/html');
        var m = d.querySelector('main.doc');
        if (!m) throw new Error('fără conținut');
        var art = document.createElement('article');
        art.className = 'doc';
        art.innerHTML = m.innerHTML;
        rbody.innerHTML = '';
        rbody.appendChild(art);
        art.addEventListener('click', function(e){
          var a = e.target.closest('a'); if (!a) return;
          var h = a.getAttribute('href') || '';
          if (h.charAt(0) === '#') {
            e.preventDefault();
            var id = decodeURIComponent(h.slice(1));
            var tgt = art.querySelector('[id="' + id.replace(/"/g, '\\"') + '"]');
            if (tgt) tgt.scrollIntoView({ block: 'start' });
          } else if (/^https?:/i.test(h)) {
            a.target = '_blank'; a.rel = 'noopener';
          }
        });
      })
      .catch(function(){
        rbody.innerHTML = '<p class="status">Nu am putut încărca documentul aici. <a href="' + li.dataset.href + '" target="_blank" rel="noopener">Deschide-l direct</a>.</p>';
      });
  }
  function loadPages(li, isPdf){
    openReader(li.dataset.title);
    var pages = li.dataset.pages.split('|');
    var names = (li.dataset.imgnames || '').split('|');
    if (isPdf) setSave(li.dataset.file, li.dataset.name, 'Salvează PDF');
    var box = document.createElement('div'); box.className = 'pages';
    pages.forEach(function(p, i){
      var fig = document.createElement('figure');
      var img = new Image(); img.src = p; img.alt = li.dataset.title + ', ' + (i + 1) + ' din ' + pages.length;
      fig.appendChild(img);
      var cap = document.createElement('figcaption');
      var s = document.createElement('span'); s.textContent = (isPdf ? 'Pagina ' : 'Imaginea ') + (i + 1) + ' din ' + pages.length;
      cap.appendChild(s);
      if (!isPdf) {
        var b = document.createElement('button'); b.type = 'button'; b.className = 'b'; b.textContent = 'Salvează imaginea';
        b.dataset.act = 'save'; b.dataset.file = p; b.dataset.name = names[i] || ('imagine-' + (i + 1) + '.jpg');
        cap.appendChild(b);
      }
      fig.appendChild(cap); box.appendChild(fig);
    });
    rbody.appendChild(box);
    if (!isPdf) {
      getDl().then(function(dl){
        if (dl) return;
        $$('[data-act="save"]', rbody).forEach(function(b){
          var a = document.createElement('a'); a.className = b.className; a.href = b.dataset.file; a.target = '_blank'; a.rel = 'noopener';
          a.textContent = 'Deschide fișierul'; b.parentNode.replaceChild(a, b);
        });
      });
    }
  }

  /* ---------- clicuri ---------- */
  document.addEventListener('click', function(e){
    var el = e.target.closest('[data-act]');
    if (!el) return;
    var act = el.dataset.act;
    if (act === 'save') {
      e.preventDefault();
      var li = el.closest('.item');
      var file = el.dataset.file || (li && li.dataset.file);
      var name = el.dataset.name || (li && li.dataset.name);
      if (file && name) saveFile(file, name, el);
      return;
    }
    if (act === 'zip') { e.preventDefault(); saveZip(el.dataset.zip, el); return; }
    if (act === 'open') {
      var item = el.closest('.item'); if (!item) return;
      var k = item.dataset.open;
      if (k === 'doc') { e.preventDefault(); loadDoc(item); }
      else if (k === 'pdf') { e.preventDefault(); loadPages(item, true); }
      else if (k === 'img') { e.preventDefault(); loadPages(item, false); }
      /* link și site: se deschid normal, în filă nouă */
    }
  });
  rsave.addEventListener('click', function(){ if (rsave.dataset.file) saveFile(rsave.dataset.file, rsave.dataset.name, rsave); });
  applyFilter();
})();
"""

INDEX = """<title>@@TITLE@@</title>
<meta name="claude:viewport-fit-sides" content="cover">
@@FONTS@@
<style>@@CSS@@</style>
<main id="app">
<header class="top"><h1>@@TITLE@@</h1>
<p class="lede">Tot ce ți-am făcut, într-un singur loc. Atinge un titlu ca să-l citești aici sau „Salvează” ca să-l ai pe telefon.</p>
<p class="count">@@COUNT@@</p></header>
<div class="tools">
<label class="sr" for="q">Caută</label>
<input class="search" id="q" type="search" placeholder="Caută: PDF, program, Instagram, plan…" autocomplete="off">
<div class="chips" role="group" aria-label="Tip de fișier">@@CHIPS@@</div>
</div>
<p id="none" hidden>Nimic găsit. Încearcă alt cuvânt sau alt filtru.</p>
@@GROUPS@@
@@ALL@@
<p class="foot">Actualizat @@UPDATED@@. Când fac fișiere noi, le adaug aici. „Salvează” îți cere o confirmare înainte.</p>
</main>
<div id="reader" class="reader" role="dialog" aria-modal="true" aria-labelledby="rtitle" hidden>
<div class="rbar"><button class="b" id="rback" type="button" aria-label="Înapoi la bibliotecă">← Înapoi</button><h2 class="rtitle" id="rtitle"></h2><button class="b b-main" id="rsave" type="button" hidden></button></div>
<div class="rbody" id="rbody"></div>
</div>
<div id="toast" role="status" aria-live="polite" hidden></div>
<script type="application/json" id="zips">@@ZIPS@@</script>
<script>@@JS@@</script>
"""


# ----------------------------------------------------------------------
# Construcție
# ----------------------------------------------------------------------
def pandoc_fragment(md_path):
    tpl = os.path.join(DIST, "_frag.tpl")
    with open(tpl, "w", encoding="utf-8") as f:
        f.write(FRAG_TPL)
    res = subprocess.run(
        ["pandoc", "-f", "gfm-raw_html", "-t", "html5", "--toc", "--toc-depth=2", "--standalone",
         "--template=" + tpl, md_path],
        capture_output=True, text=True, check=True,
    )
    out = res.stdout
    # cuprins pliabil, doar dacă are destule titluri
    m = re.search(r'<nav id="TOC">(.*?)</nav>', out, re.S)
    if m:
        n_links = m.group(1).count("<a ")
        toc = ('<details class="toc"><summary>Cuprins</summary>' + m.group(1) + "</details>") if n_links >= 5 else ""
        out = out.replace(m.group(0), toc)
    out = out.replace("<table", '<div class="tw"><table').replace("</table>", "</table></div>")
    return out


def build_doc(item, gname):
    src = resolve(item["src"])
    if not os.path.exists(src):
        warnings.append("lipsește: %s (sărit)" % item["src"])
        return False
    slug = item["slug"]
    body = pandoc_fragment(src)
    page = (DOC_PAGE.replace("@@TITLE@@", esc(item["title"])).replace("@@FONTS@@", FONTS)
            .replace("@@CSS@@", BASE_CSS).replace("@@BODY@@", body))
    with open(os.path.join(ensure("docs"), slug + ".html"), "w", encoding="utf-8") as f:
        f.write(page)
    srcname = os.path.basename(src)
    shutil.copyfile(src, os.path.join(ensure("src"), srcname))
    item.update({"href": "docs/%s.html" % slug, "srcfile": "src/" + srcname, "srcname": srcname,
                 "date": date_of(src), "size": os.path.getsize(src)})
    return True


def build_pdf(item):
    src = resolve(item["src"])
    if not os.path.exists(src):
        warnings.append("lipsește: %s (sărit)" % item["src"])
        return False
    shutil.copyfile(src, os.path.join(ensure("pdf"), item["name"]))
    prefix = os.path.join(DIST, "pdf", "prev-" + item["slug"])
    subprocess.run(["pdftoppm", "-r", "140", "-png", src, prefix], check=True)
    pages = sorted(f for f in os.listdir(os.path.join(DIST, "pdf")) if f.startswith("prev-" + item["slug"]) and f.endswith(".png"))
    info = subprocess.run(["pdfinfo", src], capture_output=True, text=True).stdout
    mm = re.search(r"Pages:\s+(\d+)", info)
    item.update({"file": "pdf/" + item["name"], "pages": ["pdf/" + p for p in pages],
                 "npages": int(mm.group(1)) if mm else len(pages),
                 "date": date_of(src), "size": os.path.getsize(src)})
    return True


def build_images(item):
    out = []
    names = []
    # "base": folder din repo (altfel, IGDIR); "keep": fișierul se copiază așa cum e (PNG rămâne PNG)
    base = os.path.join(REPO, item["base"]) if item.get("base") else IGDIR
    for name in item["images"]:
        p = os.path.join(base, name)
        if not os.path.exists(p):
            warnings.append("lipsește: %s (sărit)" % name)
            return False
        if item.get("keep"):
            shutil.copyfile(p, os.path.join(ensure("img"), name))
            out.append("img/" + name)
            names.append(name)
            continue
        jpg = name.rsplit(".", 1)[0] + ".jpg"
        Image.open(p).convert("RGB").save(os.path.join(ensure("img"), jpg), "JPEG", quality=84, optimize=True)
        out.append("img/" + jpg)
        names.append(jpg)
    item.update({"pages": out, "imgnames": names, "date": date_of(os.path.join(base, item["images"][0])),
                 "size": sum(os.path.getsize(os.path.join(DIST, o)) for o in out)})
    # pagină simplă, pentru situația în care JavaScript nu rulează
    figs = "".join('<figure><img src="../%s" alt="%s"></figure>' % (o, esc(item["title"])) for o in out)
    page = (DOC_PAGE.replace("@@TITLE@@", esc(item["title"])).replace("@@FONTS@@", FONTS).replace("@@CSS@@", BASE_CSS)
            .replace("@@BODY@@", '<div class="pages">%s</div>' % figs))
    with open(os.path.join(ensure("docs"), item["slug"] + ".html"), "w", encoding="utf-8") as f:
        f.write(page)
    item["href"] = "docs/%s.html" % item["slug"]
    return True


def build_site():
    srcdir = os.path.join(REPO, "website")
    dst = ensure("site")
    n = 0
    for dp, dn, fn in os.walk(srcdir):
        for f in fn:
            if f in ("build_site.py", "README.md") or f.endswith(".pyc"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), srcdir)
            os.makedirs(os.path.dirname(os.path.join(dst, rel)), exist_ok=True)
            shutil.copyfile(os.path.join(dp, f), os.path.join(dst, rel))
            n += 1
    return n


def zip_entries(groups):
    """Pentru fiecare folder: (nume .zip, [(cale în arhivă, fișier publicat)]). Arhiva se creează în pagină."""
    out = {}
    for g in groups:
        ents = []
        for it in g["items"]:
            if it["kind"] == "pdf":
                ents.append((g.get("folder", g["name"]) + "/" + it["name"], it["file"]))
            elif it["kind"] == "doc":
                ents.append((g.get("folder", g["name"]) + "/" + it["srcname"], it["srcfile"]))
            elif it["kind"] == "img":
                for pth in it["pages"]:
                    ents.append((g.get("folder", g["name"]) + "/" + os.path.basename(pth), pth))
            elif it["kind"] == "site":
                sd = os.path.join(DIST, "site")
                for dp, dn, fn in os.walk(sd):
                    for f in sorted(fn):
                        rel = os.path.relpath(os.path.join(dp, f), sd).replace(os.sep, "/")
                        ents.append((g.get("folder", g["name"]) + "/" + rel, "site/" + rel))
        if ents and g.get("zip"):
            out[g["id"]] = (g["zip"][0], ents)
    allents = []
    for k, (zname, ents) in out.items():
        allents += ents
    out["all"] = ("Kristine-tot.zip", allents)
    return out


def item_html(it, gname):
    kind = it["kind"]
    text = norm(" ".join([it["title"], it["desc"], gname, KIND_LABEL[kind]]))
    attrs = ['class="item"', 'data-kind="%s"' % kind, 'data-open="%s"' % kind, 'data-filter="%s"' % FILTER_OF[kind],
             'data-text="%s"' % esc(text), 'data-title="%s"' % esc(it["title"])]
    acts = []
    meta = []
    if kind == "doc":
        attrs += ['data-href="%s"' % it["href"], 'data-src="%s"' % it["srcfile"], 'data-srcname="%s"' % esc(it["srcname"])]
        href = it["href"]
        acts = ['<a class="b b-main" data-act="open" href="%s">Deschide</a>' % href,
                '<button class="b" type="button" data-act="save" data-file="%s" data-name="%s">Salvează .md</button>' % (it["srcfile"], esc(it["srcname"]))]
        meta = ["Document", fmt_size(it["size"]), it["date"]]
    elif kind == "pdf":
        attrs += ['data-file="%s"' % it["file"], 'data-name="%s"' % esc(it["name"]), 'data-pages="%s"' % "|".join(it["pages"])]
        href = it["file"]
        acts = ['<a class="b b-main" data-act="open" href="%s">Vezi</a>' % href,
                '<button class="b" type="button" data-act="save" data-file="%s" data-name="%s">Salvează PDF</button>' % (it["file"], esc(it["name"]))]
        meta = ["PDF, %d %s" % (it["npages"], "pagină" if it["npages"] == 1 else "pagini"), fmt_size(it["size"]), it["date"]]
    elif kind == "img":
        attrs += ['data-pages="%s"' % "|".join(it["pages"]), 'data-imgnames="%s"' % "|".join(it["imgnames"])]
        href = it["href"]
        acts = ['<a class="b b-main" data-act="open" href="%s">Vezi</a>' % href]
        meta = ["%d imagini" % len(it["pages"]), fmt_size(it["size"]), it["date"]]
    elif kind == "site":
        href = it["href"]
        acts = ['<a class="b b-main" href="%s" target="_blank" rel="noopener">Deschide</a>' % href]
        meta = ["8 pagini"]
    else:  # link
        href = it["url"]
        acts = ['<a class="b b-main" href="%s" target="_blank" rel="noopener">Deschide</a>' % href]
        meta = ["Se deschide în filă nouă"]
    open_attr = ' data-act="open"' if kind in ("doc", "pdf", "img") else ' target="_blank" rel="noopener"'
    return (
        "<li %s><span class=\"tag tag-%s\">%s</span><div class=\"txt\"><a class=\"t\" href=\"%s\"%s>%s</a>"
        "<p class=\"d\">%s</p><p class=\"m\">%s</p></div><div class=\"acts\">%s</div></li>"
        % (" ".join(attrs), kind, KIND_LABEL[kind], esc(href), open_attr, esc(it["title"]), esc(it["desc"]),
           esc(" · ".join(meta)), "".join(acts))
    )


def zip_size(ents):
    return sum(os.path.getsize(os.path.join(DIST, pth)) for _, pth in ents)


def group_html(g, zips):
    items = "".join(item_html(it, g["name"]) for it in g["items"])
    zbar = ""
    if g["id"] in zips:
        zname, ents = zips[g["id"]]
        zbar = ('<div class="zipbar"><span>Tot folderul, %d fișiere</span><button class="b" type="button" data-act="zip" '
                'data-zip="%s">Salvează folderul (.zip, ≈%s)</button></div>' % (len(ents), g["id"], fmt_size(zip_size(ents))))
    return ('<details class="grp" open><summary><div class="gtxt"><h2>%s</h2><span class="gnote">%s</span></div><span class="gcount">%d</span></summary>'
            '<ul class="list">%s</ul>%s</details>' % (esc(g["name"]), esc(g["note"]), len(g["items"]), items, zbar))


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    groups = []
    for g in GROUPS:
        g = dict(g)
        keep = []
        for it in g["items"]:
            it = dict(it)
            ok = True
            if it["kind"] == "doc":
                ok = build_doc(it, g["name"])
            elif it["kind"] == "pdf":
                ok = build_pdf(it)
            elif it["kind"] == "img":
                ok = build_images(it)
            if ok:
                keep.append(it)
        g["items"] = keep
        groups.append(g)
    nsite = build_site()
    zips = zip_entries(groups)

    n_items = sum(len(g["items"]) for g in groups)
    counts = {"all": n_items}
    for g in groups:
        for it in g["items"]:
            counts[FILTER_OF[it["kind"]]] = counts.get(FILTER_OF[it["kind"]], 0) + 1
    chips = "".join(
        '<button class="chip" type="button" data-kind="%s" aria-pressed="%s">%s</button>' % (k, "true" if k == "all" else "false", esc(lbl))
        for k, lbl in KIND_FILTER if counts.get(k)
    )
    updated = datetime.date.today().strftime("%d.%m.%Y")
    all_bar = ('<div class="all"><p>Toate folderele într-un singur fișier.</p><button class="b b-main" type="button" data-act="zip" '
               'data-zip="all">Salvează tot (.zip, ≈%s)</button></div>' % fmt_size(zip_size(zips["all"][1])))
    zjson = json.dumps({k: {"name": v[0], "entries": [[a, b] for a, b in v[1]]} for k, v in zips.items()},
                       ensure_ascii=False, separators=(",", ":")).replace("<", "&lt;")
    page = (INDEX.replace("@@TITLE@@", TITLE).replace("@@FONTS@@", FONTS).replace("@@CSS@@", BASE_CSS + HUB_CSS)
            .replace("@@COUNT@@", "%d fișiere în %d foldere" % (n_items, len(groups)))
            .replace("@@CHIPS@@", chips).replace("@@ALL@@", all_bar)
            .replace("@@GROUPS@@", "\n".join(group_html(g, zips) for g in groups))
            .replace("@@UPDATED@@", updated).replace("@@ZIPS@@", zjson).replace("@@JS@@", JS))
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    os.remove(os.path.join(DIST, "_frag.tpl"))
    reset = (":root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
             "body{margin:0;font:14px/1.4 system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}")
    with open(os.path.join(DIST, "_test.html"), "w", encoding="utf-8") as f:
        f.write('<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">'
                "<style>" + reset + "</style></head><body>" + page + "</body></html>")

    # lista de fișiere de publicat
    pub = []
    for dp, dn, fn in os.walk(DIST):
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), DIST).replace(os.sep, "/")
            if rel == "index.html" or rel.startswith("_"):
                continue
            pub.append(rel)
    pub.sort()
    with open(os.path.join(DIST, "_publish_files.json"), "w", encoding="utf-8") as f:
        json.dump(pub, f, ensure_ascii=False, indent=1)
    total = sum(os.path.getsize(os.path.join(DIST, p)) for p in pub) + os.path.getsize(os.path.join(DIST, "index.html"))
    print("gata: %d elemente în %d foldere, %d fișiere de publicat (%s), site: %d fișiere" % (n_items, len(groups), len(pub) + 1, fmt_size(total), nsite))
    for w in warnings:
        print("AVERTISMENT:", w)


if __name__ == "__main__":
    sys.exit(main())
