#!/usr/bin/env python3
"""Carusele pentru @kmwellnessconcept (română, șablonul B: calm, alb-verde), 1080 x 1350, 5 slide-uri fiecare.
Rulezi: python3 brand/km/build_km.py  ->  brand/km/out/KM-C1-*.png ... + brand/km/KM-carusele.zip"""
import html, os, subprocess, tempfile, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
CRED = 'Masaj de recuperare'
DISC = 'Informații generale, nu sfat medical.'
CTA = ['Salvează postarea pentru zilele lungi', 'Trimite-o unui coleg']
SETS = [
 ('C1', 'masaj-de-recuperare', 'Masaj de recuperare: ce este, de fapt?', [
   ('Un masaj cu presiune medie, adaptat ție', ['Lucrăm pe zonele care se simt încordate după zile lungi: gât, umeri, spate, picioare.', 'Presiunea o alegi tu. Spui „mai ușor” sau „mai apăsat” oricând.', 'Nu e un masaj de relaxare „de spa” și nu înlocuiește un consult medical.']),
   ('Pentru cine e', ['Stai multe ore pe scaun sau în picioare', 'Faci sport și vrei o oră pentru corp', 'Ai zile lungi și cauți un moment de liniște', 'Vrei să te simți mai relaxat(ă) seara']),
   ('Când mergi întâi la medic', ['Dureri puternice sau care apar brusc', 'O afecțiune, o operație sau un tratament în curs', 'Sarcină', 'Febră sau o infecție', 'Un răspuns de la medic vine înainte de orice masaj.']),
 ]),
 ('C2', 'zonele-incordate', 'Unde se adună încordarea după o zi la birou', [
   ('Gât și umeri', ['Capul înainte și umerii ridicați, ore în șir.', 'Seara, gâtul și umerii sunt „de piatră”.', 'Ce ajută: pauze scurte și mișcare, nu doar un masaj.']),
   ('Partea de sus a spatelui', ['Stai aplecat(ă) spre ecran.', 'Între omoplați se adună încordarea.', 'Un masaj de recuperare poate fi un moment de relaxare pentru zona asta.']),
   ('Cum lucrăm', ['Alegem împreună zonele care te deranjează.', 'Presiune medie, pe care o reglezi tu.', 'Nu înlocuiește un consult medical.']),
 ]),
 ('C3', 'sedinta-pas-cu-pas', 'O ședință de masaj de recuperare, pas cu pas', [
   ('1 · Întrebările de la început', ['Te întreb cum dormi, ce zone te deranjează și de când.', 'Te întreb de afecțiuni, operații sau tratamente.', 'Dacă un răspuns ține de medic, te trimit întâi la medic.']),
   ('2 · Ședința', ['Lucrăm doar pe zonele alese.', 'Presiunea o alegi tu.', 'Poți spune „stop” oricând.']),
   ('3 · Finalul', ['Câteva minute de mișcare ușoară.', 'Un pahar cu apă.', 'Te întreb cum te-ai simțit și ce ți s-a potrivit.']),
 ]),
 ('C4', 'obiceiuri-birou', '5 obiceiuri simple pentru cine stă la birou', [
   ('1 · O pauză pe oră', ['Ridică-te 2 minute și plimbă-te prin cameră.', 'Setează o alarmă; fără ea, uiți.', '2 · Umerii jos, apoi 8 rotiri lente înapoi.']),
   ('3 · Ecranul la nivelul ochilor', ['Marginea de sus a ecranului, aproape de ochi.', 'Tălpile pe podea, spatele sprijinit.', 'Coatele aproape de corp.']),
   ('4 și 5 · Apă și mers', ['Un pahar cu apă lângă tine, tot timpul.', '5–10 minute de mers după masa de prânz.', 'Un masaj nu înlocuiește mișcarea de zi cu zi.']),
 ]),
('C5', 'cum-te-pregatesti', 'Cum te pregătești pentru o ședință de masaj', [
   ('Înainte de ședință', ['Mănâncă ușor cu 1–2 ore înainte.', 'Bea apă în ziua aceea.', 'Poartă haine comode.', 'Spune-mi dacă ai afecțiuni, operații sau tratamente în curs.']),
   ('Ce e bine să știi', ['Presiunea o alegi tu: „mai ușor” sau „mai apăsat”.', 'Respiră lent; nu trebuie să faci nimic altceva.', 'Telefonul pe silențios, ca să te poți relaxa.']),
   ('În timpul ședinței', ['Poți spune „stop” oricând.', 'Spune-mi dacă ceva nu e confortabil.', 'La final, un pahar cu apă și o plimbare ușoară.']),
 ]),
 ('C6', 'prima-sedinta-intrebari', 'Prima ședință: ce te întreb și de ce', [
   ('Despre tine', ['Cum dormi și cât stai pe scaun.', 'Ce zone te deranjează și de când.', 'Ce presiune îți place.']),
   ('Despre sănătate', ['Dacă ai afecțiuni, operații sau un tratament în curs.', 'Dacă un răspuns ține de medic, te trimit întâi la medic.', 'Siguranța ta e pe primul loc.']),
   ('Apoi', ['Stabilim zonele pe care lucrăm.', 'Începem doar când te simți la aproape.', 'Poți spune „stop” oricând.']),
 ]),
 ('C7', 'dupa-sedinta', 'După ședință: ce faci în următoarele ore', [
   ('În prima oră', ['Bea un pahar cu apă.', 'Mergi ușor, fără efort intens.', 'Evită să te grăbești imediat spre altceva.']),
   ('Seara', ['Odihnă și un duș călduț.', 'Un somn bun.', 'Observă cum te simți; fiecare corp reacționează diferit.']),
   ('Când vorbești cu medicul', ['Dureri neobișnuite sau care persistă.', 'Amețeală sau orice te îngrijorează.', 'Dacă nu ești sigur(ă), întreabă.']),
 ]),
 ('C8', 'mituri-despre-masaj', '4 mituri despre masaj', [
   ('Mit 1 și 2', ['„Trebuie să doară ca să funcționeze.” Nu: presiunea e confortabilă și o alegi tu.', '„Un masaj înlocuiește mișcarea.” Nu: mersul și pauzele de la birou rămân importante.']),
   ('Mit 3 și 4', ['„O ședință rezolvă tot.” Fiecare corp e diferit; spune-mi ce simți și vedem ce ți se potrivește.', '„Masajul e doar pentru cine face sport.” Nu: e pentru oricine stă mult jos sau în picioare.']),
   ('Ce rămâne valabil', ['Masajul nu înlocuiește un consult medical.', 'Dacă ai o afecțiune, medicul vine primul.', 'Informațiile de aici sunt generale.']),
 ]),
]

CSS = """
:root{--bg:#F3F8F5;--ink:#26322D;--green:#1C6550;--mint:#D8F0E4;--sage:#BFE0D0;--cream:#FFF9F6;--muted:#546A61}
*{box-sizing:border-box}body{margin:0}
.s{position:relative;overflow:hidden;width:1080px;height:1350px;background:var(--bg);color:var(--ink);font-family:Figtree,sans-serif}
.c1,.c2{position:absolute;border-radius:50%}
.tag{position:absolute;left:80px;top:70px;font-weight:700;font-size:28px;color:var(--green);letter-spacing:.04em}
.num{position:absolute;right:80px;top:70px;font-weight:700;font-size:28px;color:var(--muted)}
h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.03em;margin:0;line-height:1.02;color:var(--ink)}
h2{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.02em;margin:0 0 40px;font-size:76px;line-height:1.05}
ul{margin:0;padding:0;list-style:none}
li{font-size:44px;line-height:1.3;margin-bottom:30px;padding-left:56px;position:relative;font-weight:600}
li:before{content:'';position:absolute;left:0;top:16px;width:22px;height:22px;border-radius:50%;background:var(--green)}
.foot{position:absolute;left:80px;right:80px;bottom:60px;font-size:26px;color:var(--muted);line-height:1.4}
.btn{display:inline-block;background:var(--green);color:#fff;font-weight:700;font-size:42px;border-radius:999px;padding:26px 52px;margin-top:40px}
"""
def shapes(k):
    a = [('c1', 'width:760px;height:760px;right:-260px;bottom:-240px;background:var(--mint)'), ('c2', 'width:420px;height:420px;left:-150px;bottom:140px;background:var(--sage);opacity:.55')]
    b = [('c1', 'width:640px;height:640px;left:-240px;top:-220px;background:var(--mint)'), ('c2', 'width:360px;height:360px;right:-120px;bottom:-120px;background:var(--sage);opacity:.6')]
    return ''.join('<div class="%s" style="%s"></div>' % x for x in (a if k % 2 else b))
def slide(n, total, inner, k):
    return '<div class="s" id="s">%s<div class="tag">KM WELLNESS CONCEPT</div><div class="num">%d/%d</div>%s</div>' % (shapes(k), n, total, inner)
def build(code, slug, title, mids):
    out = []
    out.append(slide(1, 5, '<div style="position:absolute;left:80px;right:80px;top:380px"><h1 style="font-size:118px">%s</h1><p style="font-size:38px;color:var(--muted);margin-top:44px;font-weight:600">Trage spre dreapta →</p></div>' % html.escape(title), 1))
    for i, (h, items) in enumerate(mids, 2):
        lis = ''.join('<li>%s</li>' % html.escape(t) for t in items)
        out.append(slide(i, 5, '<div style="position:absolute;left:80px;right:80px;top:210px"><h2>%s</h2><ul>%s</ul></div><div class="foot">%s</div>' % (html.escape(h), lis, DISC), i))
    out.append(slide(5, 5, '<div style="position:absolute;left:80px;right:80px;top:340px"><h1 style="font-size:92px">%s</h1><div class="btn">%s</div><p style="font-size:34px;margin-top:70px;line-height:1.4;font-weight:600">%s</p></div><div class="foot">%s</div>' % (html.escape(CTA[0]), html.escape(CTA[1]), html.escape(CRED), DISC), 5))
    return out
JS = r"""
const { chromium } = require('playwright');
(async () => { const items = JSON.parse(process.argv[2]); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
 for (const [file, html] of items) { await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150); await (await p.$('#s')).screenshot({ path: file }); }
 await b.close(); })();
"""
import json
def main():
    head = '<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@600;700&display=swap" rel="stylesheet"><style>%s</style></head><body>' % CSS
    jobs, files = [], []
    for code, slug, title, mids in SETS:
        for n, inner in enumerate(build(code, slug, title, mids), 1):
            f = os.path.join(OUT, 'KM-%s-%s-%d.png' % (code, slug, n)); jobs.append((f, head + inner + '</body></html>')); files.append(f)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as t:
        t.write(JS)
    env = dict(os.environ); env['NODE_PATH'] = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    subprocess.run(['node', t.name, json.dumps(jobs)], check=True, env=env); os.unlink(t.name)
    z = os.path.join(HERE, 'KM-carusele.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, os.path.basename(f))
    print('gata:', len(files), 'imagini,', z)
main()
