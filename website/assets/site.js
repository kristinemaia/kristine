/* =====================================================================
   Kristine Maia · JavaScript comun pentru TOATE paginile
   1. meniul pe telefon   2. anul din footer   3. formularele de email
   4. „Today / Next up” în programul de pe Twitch
   5. contorul de pe prima pagină (textele lui sunt în BANDS și MOVES)
   ===================================================================== */
(function () {
  'use strict';
  var $ = function (s) { return document.querySelector(s); };
  var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 1. Meniul pe telefon
  var menuBtn = $('.menu-btn'), nav = $('#nav-links');
  if (menuBtn && nav) {
    var setMenu = function (open) {
      nav.classList.toggle('open', open);
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      menuBtn.textContent = open ? 'Close' : 'Menu';
    };
    menuBtn.addEventListener('click', function () { setMenu(!nav.classList.contains('open')); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); menuBtn.focus(); }
    });
  }

  // 2. Anul din footer
  var year = $('#year');
  if (year) year.textContent = new Date().getFullYear();

  // 3. Formularele de email: până conectezi MailerLite / Kit (vezi README), afișează doar un mesaj
  document.querySelectorAll('form[data-placeholder]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = f.querySelector('.form-msg');
      if (msg) msg.textContent = 'Thanks! Sign-ups open very soon. Follow on Twitch or Instagram in the meantime.';
    });
  });

  // 4. Programul: marchează streamul de azi sau următorul (doar luni, miercuri, vineri;
  //    duminica nu se marchează niciodată, pentru că e doar în unele săptămâni)
  var shows = document.querySelectorAll('[data-day]');
  if (shows.length) {
    var today = new Date().getDay(), target = -1, label = 'Next up';
    var onDays = [].map.call(shows, function (el) { return +el.getAttribute('data-day'); });
    for (var k = 0; k < 7; k++) {
      var d = (today + k) % 7;
      if (onDays.indexOf(d) > -1) { target = d; if (k === 0) label = 'Today'; break; }
    }
    shows.forEach(function (el) {
      if (+el.getAttribute('data-day') !== target) return;
      var pill = document.createElement('span');
      pill.className = 'pill';
      pill.textContent = label;
      (el.querySelector('b') || el).appendChild(pill);
    });
  }

  // 5. Contorul „How many hours did you sit today?” (doar pe prima pagină)
  var meter = $('#meter');
  if (!meter) return;

  // Exercițiile pauzei. Fiecare durează 15 secunde. ['Nume', 'Ce faci']
  var MOVES = {
    chin:   ['Chin tucks', 'Slide your chin straight back, like making a double chin. Slow, 5 times.'],
    rolls:  ['Shoulder rolls', 'Big, slow circles backwards. Let your shoulders drop at the bottom.'],
    blades: ['Shoulder blade squeeze', 'Pull your shoulder blades back and down, hold 3 seconds, release.'],
    wrist:  ['Wrist stretch', 'Arm straight, palm up. Gently pull your fingers back. Switch hands halfway.'],
    twist:  ['Seated twist', 'Sit tall, hold the back of your chair and turn gently. Switch sides halfway.'],
    fig4:   ['Seated figure-4', 'Ankle on the opposite knee, sit tall, hinge forward slightly from the hips. Switch sides halfway.']
  };

  // Ce îi răspunzi vizitatorului pentru fiecare interval de ore și ce 4 exerciții primește.
  // to = până la câte ore (inclusiv). {m} = minutele, {h} = orele. Numește zona pe care o lucrează exercițiile.
  var BANDS = [
    { to: 0,  say: 'Zero? Early start or total legend. Your shoulders still want this minute.', moves: ['rolls', 'chin', 'wrist', 'twist'] },
    { to: 2,  say: 'A light day. Keep it that way: one minute for your neck and shoulders.', moves: ['rolls', 'chin', 'wrist', 'twist'] },
    { to: 5,  say: '{m} minutes in. Around now, heads drift toward screens. Neck first.', moves: ['chin', 'rolls', 'wrist', 'twist'] },
    { to: 8,  say: "A full workday. Your hips have been folded at 90° for {m} minutes. Let's open them.", moves: ['fig4', 'chin', 'blades', 'wrist'] },
    { to: 11, say: "On my Friday stream that's {h} stretch breaks by now. Hips and back, catch up.", moves: ['fig4', 'twist', 'blades', 'chin'] },
    { to: 16, say: '{m} minutes. Marathon mode. Upper back and hips, then stand up. Chat will survive.', moves: ['blades', 'twist', 'fig4', 'chin'] }
  ];

  var range = $('#hrs'), live = $('#say');
  var hOut = $('#h-out'), mOut = $('#m-out'), verdict = $('#verdict'), plan = $('#plan');
  var clock = $('#clock'), step = $('#step'), moveEl = $('#move'), cue = $('#cue');
  var pauseBtn = $('#pause'), segs = document.querySelectorAll('.segs i');
  var hours = 8, band = BANDS[3], set = [], shown = -1;

  // Ce citește cititorul de ecran (cu o mică pauză, ca să nu vorbească la fiecare pas al sliderului)
  var sayTimer = null;
  function announce(text, wait) {
    clearTimeout(sayTimer);
    sayTimer = setTimeout(function () { live.textContent = text; }, wait || 0);
  }

  // Omulețul de pe scaun: t = 0 stă drept, t = 1 e cocoșat spre ecran
  var fig = { legs: $('#f-legs'), spine: $('#f-spine'), arm: $('#f-arm'), neck: $('#f-neck'), head: $('#f-head') };
  var cur = 0;
  function L(a, b, t) { return Math.round((a + (b - a) * t) * 10) / 10; }
  function pose(t) {
    cur = t;
    var P = [L(62, 68, t), L(124, 126, t)];   // șoldul
    var C = [L(56, 56, t), L(94, 112, t)];    // curba spatelui
    var S = [L(62, 102, t), L(62, 82, t)];    // umărul
    var E = [L(86, 124, t), L(100, 104, t)];  // cotul
    var H = [L(68, 126, t), L(36, 72, t)];    // capul
    fig.spine.setAttribute('d', 'M' + P + ' Q' + C + ' ' + S);
    fig.legs.setAttribute('d', 'M' + P + ' L124,126 L124,174 L140,174');
    fig.arm.setAttribute('d', 'M' + S + ' L' + E + ' L168,98');
    fig.neck.setAttribute('d', 'M' + S + ' L' + H);
    fig.head.setAttribute('transform', 'translate(' + H + ') rotate(' + L(0, 22, t) + ')');
  }
  function tween(to) {
    if (RM) { pose(to); return; }
    var from = cur, t0 = null;
    requestAnimationFrame(function f(ts) {
      t0 = t0 || ts;
      var k = Math.min(1, (ts - t0) / 700);
      k = 1 - Math.pow(1 - k, 3);
      pose(from + (to - from) * k);
      if (k < 1) requestAnimationFrame(f);
    });
  }
  function slouch() { return Math.min(1, hours / 13); }

  function update() {
    hours = +range.value;
    var m = hours * 60;
    for (var i = 0; i < BANDS.length; i++) { if (hours <= BANDS[i].to) { band = BANDS[i]; break; } }
    hOut.textContent = hours === 16 ? '16+' : hours;
    mOut.textContent = m + ' min in a chair';
    verdict.textContent = band.say.replace('{m}', m).replace('{h}', hours);
    plan.innerHTML = 'Your minute: <b>' + band.moves.map(function (k) { return MOVES[k][0]; }).join(' · ') + '</b>';
    range.style.setProperty('--fill', (hours / 16 * 100) + '%');
    range.setAttribute('aria-valuetext', (hours === 16 ? '16 or more hours' : hours + (hours === 1 ? ' hour' : ' hours')));
    pose(slouch());
  }
  range.addEventListener('input', function () { update(); announce(verdict.textContent, 900); });

  // Pulsul de pe slider dispare după prima atingere
  function stopNudge() { range.classList.remove('nudge'); }
  ['pointerdown', 'keydown', 'input'].forEach(function (ev) { range.addEventListener(ev, stopNudge); });

  // Linkuri care setează sliderul: index.html#10h (sau #h10) pornește de la 10 ore
  function fromHash() {
    var hit = /^#h?(\d{1,2})h?$/i.exec(location.hash || '');
    if (!hit) return false;
    range.value = Math.min(16, parseInt(hit[1], 10));
    if (meter.getAttribute('data-mode') !== 'count') { halt(); meter.setAttribute('data-mode', 'count'); }
    update();
    return true;
  }
  window.addEventListener('hashchange', fromHash);

  // Pauza de 60 de secunde: 4 exerciții x 15 secunde
  var PER = 15, TOTAL = 60, left = TOTAL, timer = null;
  function paint() {
    var done = TOTAL - left, i = Math.min(3, Math.floor(done / PER));
    clock.textContent = '0:' + String(PER - (done % PER)).padStart(2, '0');
    step.textContent = 'Move ' + (i + 1) + ' of 4';
    if (i !== shown) {
      shown = i;
      moveEl.textContent = set[i][0];
      cue.textContent = set[i][1];
      announce('Move ' + (i + 1) + ' of 4: ' + set[i][0] + '. ' + set[i][1]);
    }
    segs.forEach(function (s, k) { s.style.setProperty('--f', Math.max(0, Math.min(1, (done - k * PER) / PER))); });
  }
  function run() {
    pauseBtn.textContent = 'Pause';
    timer = setInterval(function () { left--; if (left <= 0) { finish(); return; } paint(); }, 1000);
  }
  function halt() { clearInterval(timer); timer = null; }
  function start() {
    halt(); left = TOTAL; shown = -1;
    set = band.moves.map(function (k) { return MOVES[k]; });
    meter.setAttribute('data-mode', 'break');
    paint(); run(); tween(0); pauseBtn.focus();
  }
  function finish() {
    halt(); left = 0;
    var m = hours * 60;
    $('#done-line').textContent = m
      ? "Notice anything? That's 1 of " + m + ' minutes back.'
      : "Notice anything? That's 1 minute just for you.";
    meter.setAttribute('data-mode', 'done');
    $('#done-chat').focus();
  }
  $('#go').addEventListener('click', start);
  $('#again').addEventListener('click', start);
  pauseBtn.addEventListener('click', function () {
    if (timer) { halt(); pauseBtn.textContent = 'Resume'; announce('Paused'); } else run();
  });
  $('#stop').addEventListener('click', function () {
    halt(); meter.setAttribute('data-mode', 'count'); tween(slouch()); range.focus();
  });
  // „Get the free desk stretch” duce la formular și pune cursorul în câmpul de email
  $('#to-free').addEventListener('click', function () {
    var email = document.getElementById('email');
    if (email) setTimeout(function () { email.focus({ preventScroll: true }); }, RM ? 0 : 450);
  });

  update();
  fromHash();
})();
