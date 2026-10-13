(function () {
  // Meniul pe telefon
  var btn = document.querySelector('.menu-btn');
  var links = document.querySelector('.nav-links');
  if (btn && links) {
    btn.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Close' : 'Menu';
    });
  }

  // Anul din footer
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Formularele de email: până conectezi MailerLite / Kit (vezi README), afișează un mesaj
  document.querySelectorAll('form[data-placeholder]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = f.querySelector('.form-msg');
      if (msg) msg.textContent = 'Thanks! Sign-ups open very soon. Follow on Twitch or Instagram in the meantime.';
    });
  });

  // Pauza de stretching de 60 de secunde
  var box = document.getElementById('breaker');
  if (!box) return;
  var MOVES = [
    { name: 'Chin tucks', cue: 'Slide your chin straight back, like making a double chin. Slow, 5 times.' },
    { name: 'Shoulder rolls', cue: 'Big, slow circles backwards. Let your shoulders drop at the bottom.' },
    { name: 'Wrist stretch', cue: 'Arm straight, palm up. Gently pull your fingers back. Switch hands halfway.' },
    { name: 'Seated twist', cue: 'Sit tall, hold the back of your chair and turn gently. Switch sides halfway.' }
  ];
  var PER = 15, TOTAL = PER * MOVES.length;
  var left = TOTAL, timer = null;
  var dial = box.querySelector('.dial');
  var time = box.querySelector('.dial-time');
  var step = box.querySelector('.dial-step');
  var name = box.querySelector('.move-name');
  var cue = box.querySelector('.move-cue');
  var start = box.querySelector('[data-start]');
  var reset = box.querySelector('[data-reset]');

  function paint() {
    var done = TOTAL - left;
    var i = Math.min(MOVES.length - 1, Math.floor(done / PER));
    var inMove = PER - (done % PER);
    if (left === 0) { i = MOVES.length - 1; inMove = 0; }
    time.textContent = left === 0 ? 'Done' : '0:' + String(inMove).padStart(2, '0');
    step.textContent = left === 0 ? 'Nice. Back to it.' : 'Move ' + (i + 1) + ' of ' + MOVES.length;
    if (name.textContent !== MOVES[i].name) { name.textContent = MOVES[i].name; cue.textContent = MOVES[i].cue; }
    dial.style.setProperty('--p', (done / TOTAL).toFixed(3));
  }
  function stop() { clearInterval(timer); timer = null; start.textContent = left === TOTAL ? 'Start 60 seconds' : (left === 0 ? 'Again' : 'Resume'); }
  start.addEventListener('click', function () {
    if (timer) { stop(); return; }
    if (left === 0) left = TOTAL;
    start.textContent = 'Pause';
    timer = setInterval(function () { left--; paint(); if (left <= 0) { left = 0; stop(); paint(); } }, 1000);
    paint();
  });
  reset.addEventListener('click', function () { left = TOTAL; stop(); paint(); });
  paint();
})();
