// Înregistrează două demo-uri pe ecran de telefon: chestionarul (training.html) și programul pas cu pas (my-program.html)
const {chromium} = require('playwright');
const SITE = process.argv[2], OUT = process.argv[3];
async function ctx(b) {
  const c = await b.newContext({viewport: {width: 780, height: 1688}, deviceScaleFactor: 1, recordVideo: {dir: OUT, size: {width: 780, height: 1688}}});
  await c.addInitScript(() => {
    window.__spd = 1; const si = window.setInterval; window.setInterval = (f, t) => si(f, t / window.__spd);
    try { localStorage.setItem('km-cp-pop', String(Date.now())); } catch (e) {}
    document.addEventListener('DOMContentLoaded', () => { const st = document.createElement('style'); st.textContent = 'html{zoom:2}'; document.head.appendChild(st); });
  });
  return c;
}
async function slowScroll(p, to, ms) {
  await p.evaluate(async ([to, ms]) => { const from = window.scrollY, n = Math.max(1, Math.round(ms / 16));
    for (let i = 1; i <= n; i++) { window.scrollTo(0, from + (to - from) * i / n); await new Promise(r => setTimeout(r, 16)); } }, [to, ms]);
}
(async () => {
  const b = await chromium.launch();
  // 1. chestionarul
  let c = await ctx(b), p = await c.newPage();
  await p.goto('file://' + SITE + '/training.html'); await p.waitForTimeout(1200);
  const y = await p.evaluate(() => document.getElementById('quiz').getBoundingClientRect().top + scrollY - 10);
  await slowScroll(p, y, 900); await p.waitForTimeout(400);
  await p.fill('input[name="name"]', 'Ana'); await p.waitForTimeout(300);
  const pick = async (n, v) => { const el = await p.$(`input[name="${n}"][value="${v}"]`); if (!el || !(await el.isVisible().catch(() => false))) { const lab = await p.$(`label:has(input[name="${n}"][value="${v}"])`); if (lab) { await lab.scrollIntoViewIfNeeded(); await lab.click(); } } else { await el.scrollIntoViewIfNeeded(); await el.click({force: true}); } await p.waitForTimeout(350); };
  for (const [n, v] of [['sit', '8-12'], ['goal', 'str'], ['ache', 'no'], ['focus', 'lower'], ['exp', 'some'], ['lvl', 'beg'], ['place', 'gym'], ['time', '35'], ['days', '3']]) await pick(n, v);
  const age = await p.$('input[name="age"]'); await age.scrollIntoViewIfNeeded(); await age.fill('27'); await p.waitForTimeout(300);
  await pick('health', 'none');
  const sub = await p.$('#quiz-form button[type="submit"]'); await sub.scrollIntoViewIfNeeded(); await p.waitForTimeout(500); await sub.click();
  await p.waitForTimeout(2600); await slowScroll(p, await p.evaluate(() => scrollY + 500), 2200); await p.waitForTimeout(1200);
  await c.close();
  // 2. programul: (a) planul, ziua, Start și cronometrul de încălzire
  c = await ctx(b); p = await c.newPage();
  await p.goto('file://' + SITE + '/my-program.html'); await p.waitForTimeout(500);
  await p.fill('#nm', 'Ana'); await p.waitForTimeout(400); await p.click('text=Build my plan'); await p.waitForTimeout(1500);
  await p.click('#week .day'); await p.waitForTimeout(1300); await slowScroll(p, 500, 1200); await p.waitForTimeout(300);
  await p.click('#start'); await p.waitForTimeout(1500);
  await p.click('#act'); await p.waitForTimeout(3500);
  await c.close();
  // (b) exercițiul cu greutăți: sare repede până acolo, notează când începe partea bună, ca s-o taie după
  c = await ctx(b); p = await c.newPage(); const T0 = Date.now();
  await p.goto('file://' + SITE + '/my-program.html'); await p.evaluate(() => window.__spd = 300);
  await p.fill('#nm', 'Ana'); await p.click('text=Build my plan'); await p.click('#week .day'); await p.click('#start');
  for (let i = 0; i < 200; i++) {
    if (await p.isVisible('#p-in')) break;
    if (await p.isVisible('#act')) await p.click('#act');
    if (await p.isVisible('#skip')) await p.click('#skip');
    await p.waitForTimeout(60);
  }
  await p.evaluate(() => window.__spd = 1); await p.waitForTimeout(300);
  console.log('START_B', (Date.now() - T0) / 1000);
  await p.waitForTimeout(1500);
  await p.fill('#kg', '20'); await p.waitForTimeout(400); await p.fill('#reps', '10'); await p.waitForTimeout(500);
  await p.click('#act'); await p.waitForTimeout(4500);
  await c.close();
  await b.close();
})();
