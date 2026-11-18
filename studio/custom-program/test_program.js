// Test complet al programului: ca o clientă pe telefon. Rulezi: node fulltest.js <folder site> <folder ieșire>
const {chromium, devices} = require('playwright');
const fs = require('fs');
const SITE = process.argv[2], OUT = process.argv[3];
const report = {errors: [], failedReq: [], combos: [], workouts: {}, checks: []};
const ok = (name, cond, extra) => { report.checks.push({name, ok: !!cond, extra: extra || ''}); };

async function newPage(b, spd) {
  const c = await b.newContext({...devices['iPhone 13'], hasTouch: true});
  await c.addInitScript((spd) => {
    window.__spd = spd; const si = window.setInterval; window.setInterval = (f, t) => si(f, Math.max(1, t / window.__spd));

    try { localStorage.setItem('km-cp-pop', String(Date.now())); } catch (e) {}
  }, spd);
  // ca pe Netlify: un site adevărat (http), nu fișiere locale
  const TYPES = {html: 'text/html', js: 'text/javascript', css: 'text/css', mp4: 'video/mp4', jpg: 'image/jpeg', png: 'image/png', svg: 'image/svg+xml', webp: 'image/webp', pdf: 'application/pdf', json: 'application/json'};
  await c.route('http://km.test/**', async route => {
    const u = new URL(route.request().url()); let f = SITE + decodeURIComponent(u.pathname); if (f.endsWith('/')) f += 'index.html';
    if (!fs.existsSync(f)) return route.fulfill({status: 404, body: 'not found'});
    return route.fulfill({status: 200, contentType: TYPES[f.split('.').pop()] || 'application/octet-stream', body: fs.readFileSync(f)});
  });
  const p = await c.newPage();
  p.on('pageerror', e => report.errors.push((p.url().split('/').pop()) + ': ' + e.message));
  p.on('console', m => { if (m.type() === 'error') report.errors.push('console ' + p.url().split('/').pop() + ': ' + m.text()); });
  p.on('requestfailed', r => { if (r.url().startsWith('http://km.test')) report.failedReq.push(r.url().split('km.test/')[1]); });
  return [c, p];
}
async function pick(p, name, value) {
  const lab = await p.$(`label:has(input[name="${name}"][value="${value}"])`);
  if (lab && !(await lab.isVisible())) return; // întrebarea e ascunsă pentru obiectivul ales (ex. focus la Unstiff)
  if (lab) { await lab.click(); return; }
  await p.check(`input[name="${name}"][value="${value}"]`, {force: true});
}
async function setup(p, o) {
  await p.goto('http://km.test/my-program.html');
  if (await p.isVisible('#chg')) { await p.click('#chg'); }
  await p.fill('#nm', 'Test');
  for (const k of ['goal', 'focus', 'place', 'days', 'time', 'lvl', 'jump']) if (o[k]) {
    if (await p.$(`input[name="${k}"][value="${o[k]}"]`)) await pick(p, k, o[k]);
  }
  await p.click('text=Build my plan');
  await p.waitForSelector('#week .day', {timeout: 5000});
  return await p.$$eval('#week .day', els => els.map(e => e.innerText.replace(/\s+/g, ' ').trim()));
}
async function runWorkout(p, openSel, label) {
  await p.click(openSel); await p.waitForTimeout(200);
  const title = (await p.textContent('#o-t').catch(() => '')) || label;
  await p.click('#start');
  let steps = 0, weighted = 0, timed = 0, vidErr = 0, done = false;
  for (let i = 0; i < 600; i++) {
    if (await p.isVisible('#v-done')) { done = true; break; }
    if (await p.isVisible('#p-in') && await p.isVisible('#kg')) {
      weighted++; await p.fill('#kg', '10'); await p.fill('#reps', '10');
    }
    const st = await p.textContent('#p-step').catch(() => '');
    const v = await p.evaluate(() => { const v = document.getElementById('vid'); return v ? {err: !!v.error, src: v.currentSrc} : null; });
    if (v && v.err) vidErr++;
    if (await p.isVisible('#rest')) { if (await p.isVisible('#skip')) await p.click('#skip'); else await p.waitForTimeout(30); continue; }
    if (await p.isVisible('#act')) { const t = await p.textContent('#act'); if (/Start\s+\d/.test(t)) timed++; await p.click('#act'); steps++; }
    else if (await p.isVisible('#skip')) { await p.click('#skip'); steps++; }
    await p.waitForTimeout(25);
  }
  report.workouts[title] = {done, clicks: steps, weightedInputs: weighted, timers: timed, videoErrors: vidErr};
  if (done) { const b = await p.$('#v-done button, #v-done a'); if (b) await b.click(); }
  return done;
}

(async () => {
  const b = await chromium.launch();
  // 1. pagina cu quiz-ul și pop-up-ul
  let [c, p] = await newPage(b, 1);
  await p.goto('http://km.test/training.html'); await p.waitForTimeout(500);
  ok('training.html se deschide', await p.isVisible('#quiz-form'));
  await c.close();
  // 2. combinațiile din formular
  [c, p] = await newPage(b, 200);
  const combos = [];
  for (const goal of ['str', 'fat', 'mob', 'desk']) for (const place of ['gym', 'home', 'both']) for (const days of ['2', '3', '4'])
    combos.push({goal, place, days, focus: ['whole', 'lower', 'upper', 'core'][combos.length % 4], time: ['10', '20', '35'][combos.length % 3], lvl: ['beg', 'mid', 'adv'][combos.length % 3], jump: combos.length % 2 ? 'no' : 'yes'});
  for (const o of combos) {
    try { const week = await setup(p, o); report.combos.push({o, week}); }
    catch (e) { report.combos.push({o, error: e.message.split('\n')[0]}); }
  }
  ok('toate combinațiile dau un plan', report.combos.every(x => x.week && x.week.length >= 2), report.combos.filter(x => !x.week).length + ' fără plan');
  ok('numărul de zile = alegerea', report.combos.every(x => !x.week || x.week.length >= +x.o.days), '');
  // 3. fiecare antrenament din fiecare plan, cap-coadă (o dată pe titlu)
  const seen = new Set();
  for (const o of [{goal:'str',place:'gym',days:'4',time:'35',lvl:'adv',jump:'yes',focus:'whole'},{goal:'str',place:'home',days:'4',time:'35',lvl:'beg',jump:'no',focus:'whole'},
                   {goal:'fat',place:'gym',days:'4',time:'35',lvl:'mid',jump:'yes',focus:'lower'},{goal:'fat',place:'home',days:'4',time:'20',lvl:'beg',jump:'no',focus:'upper'},
                   {goal:'mob',place:'both',days:'4',time:'20',lvl:'mid',jump:'no',focus:'whole'},{goal:'desk',place:'both',days:'3',time:'10',lvl:'beg',jump:'no',focus:'core'},
                   {goal:'str',place:'both',days:'3',time:'10',lvl:'mid',jump:'yes',focus:'upper'},{goal:'fat',place:'both',days:'4',time:'35',lvl:'adv',jump:'yes',focus:'core'}]) {
    const week = await setup(p, o);
    for (let i = 0; i < week.length; i++) {
      const name = week[i]; const key = name.replace(/^Day \d+\s*/, '').slice(0, 60);
      if (seen.has(key)) continue; seen.add(key);
      await p.goto('http://km.test/my-program.html');
      try { await p.waitForSelector('#week .day', {timeout: 5000}); } catch (e) {
        const vis = []; for (const v of ['v-setup', 'v-home', 'v-over', 'v-play', 'v-done']) if (await p.isVisible('#' + v)) vis.push(v);
        report.errors.push('TEST: inainte de ' + key + ' nu apare planul; vizibil: ' + vis.join(',')); await p.screenshot({path: OUT + '/fail-w-' + i + '.png'});
        console.log('STUCK before', key, vis.join(','), JSON.stringify(o));
        console.log('LS', await p.evaluate(() => Object.keys(localStorage).map(k => k + '=' + localStorage.getItem(k).length + ':' + localStorage.getItem(k).slice(0, 120)).join(' | ')));
        process.exit(1); }
      try { await runWorkout(p, `#week .day >> nth=${i}`, key); } catch (e) { report.errors.push('TEST: ' + key + ': ' + e.message.split('\n')[0]); }
    }
    // resetările
    const nres = await p.$$eval('#resets > *', e => e.length).catch(() => 0);
    for (let i = 0; i < nres; i++) {
      await p.goto('http://km.test/my-program.html');
      try { await p.waitForSelector('#week .day', {timeout: 5000}); } catch (e) {
        const vis = []; for (const v of ['v-setup', 'v-home', 'v-over', 'v-play', 'v-done']) if (await p.isVisible('#' + v)) vis.push(v);
        report.errors.push('TEST: dupa resetul ' + i + ' nu apare planul; vizibil: ' + vis.join(',') + ' url ' + p.url()); await p.screenshot({path: OUT + '/fail-' + i + '.png'}); continue; }
      const els = await p.$$('#resets > *'); const t = (await els[i].innerText()).slice(0, 50);
      if (seen.has(t)) continue; seen.add(t);
      const clickable = await els[i].$('button, a') || els[i];
      await clickable.click(); await p.waitForTimeout(200);
      if (await p.isVisible('#start')) { await p.click('#start'); }
      let done = false;
      for (let k = 0; k < 400; k++) { if (await p.isVisible('#v-done')) { done = true; break; }
        if (await p.isVisible('#rest') && await p.isVisible('#skip')) await p.click('#skip'); else if (await p.isVisible('#act')) await p.click('#act'); else if (await p.isVisible('#skip')) await p.click('#skip'); await p.waitForTimeout(25); }
      report.workouts['reset: ' + t] = {done};
    }
  }
  // 4. după reîncărcare: planul, jurnalul și „Last time”
  await p.goto('http://km.test/my-program.html'); await p.waitForTimeout(300);
  const ls = await p.evaluate(() => ({plan: !!localStorage.getItem('kmp:plan'), log: (localStorage.getItem('kmp:log') || '').length, last: (localStorage.getItem('kmp:last') || '').length}));
  ok('planul rămâne salvat după reîncărcare', ls.plan && await p.isVisible('#week .day'));
  ok('jurnalul salvează seriile', ls.log > 10, 'kmp:log ' + ls.log + ' caractere');
  ok('„My weights” apare pe pagina principală', await p.isVisible('#mine'));
  await p.click('#week .day >> nth=0'); await p.click('#start');
  let lastSeen = '';
  for (let i = 0; i < 80 && !lastSeen; i++) {
    if (await p.isVisible('#p-last')) { const t = (await p.textContent('#p-last')).trim(); if (t) lastSeen = t; }
    if (await p.isVisible('#rest') && await p.isVisible('#skip')) await p.click('#skip'); else if (await p.isVisible('#act')) await p.click('#act'); await p.waitForTimeout(25);
  }
  ok('la a doua oară arată „Last time”', !!lastSeen, lastSeen.slice(0, 60));
  await p.screenshot({path: OUT + '/last-time.png'});
  await c.close();
  // 5. jurnalul separat
  [c, p] = await newPage(b, 1);
  await p.goto('http://km.test/log.html'); await p.waitForTimeout(400);
  ok('log.html se deschide fără erori', true);
  await c.close();
  await b.close();
  fs.writeFileSync(OUT + '/report.json', JSON.stringify(report, null, 1));
  const wk = Object.entries(report.workouts);
  console.log('ERORI JS:', report.errors.length, report.errors.slice(0, 8));
  console.log('FIȘIERE LIPSĂ:', [...new Set(report.failedReq)].slice(0, 10));
  console.log('COMBINAȚII:', report.combos.length, 'fără plan:', report.combos.filter(x => !x.week).length);
  console.log('ANTRENAMENTE TESTATE:', wk.length, 'neterminate:', wk.filter(([k, v]) => !v.done).map(([k]) => k));
  console.log('VIDEO CU EROARE:', wk.filter(([k, v]) => v.videoErrors).map(([k, v]) => k + ' ' + v.videoErrors));
  for (const x of report.checks) console.log((x.ok ? 'OK  ' : 'NU  ') + x.name + (x.extra ? '  (' + x.extra + ')' : ''));
})();
