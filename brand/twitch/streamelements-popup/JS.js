// Level Up pop-up: apare la fiecare X minute și când cineva scrie !program (sau alt cuvânt din listă) în chat.
let cfg = {}, busy = false, lastChat = 0;
const pop = () => document.getElementById('pop');

function show() {
  if (busy) return;
  busy = true;
  pop().classList.add('show');
  setTimeout(() => { pop().classList.remove('show'); setTimeout(() => { busy = false; }, 700); }, cfg.showSeconds * 1000);
}

window.addEventListener('onWidgetLoad', (obj) => {
  const f = obj.detail.fieldData;
  cfg = {
    everyMinutes: Number(f.everyMinutes) || 10,
    showSeconds: Number(f.showSeconds) || 25,
    commands: String(f.commands || '!program,!levelup,!plan').toLowerCase().split(',').map(s => s.trim()).filter(Boolean),
    chatCooldown: Number(f.chatCooldownSeconds) || 120,
  };
  setTimeout(show, 5000);                                   // o dată la pornire (ca să vezi că merge)
  setInterval(show, cfg.everyMinutes * 60 * 1000);          // apoi la fiecare X minute
});

window.addEventListener('onEventReceived', (obj) => {
  if (!obj.detail || obj.detail.listener !== 'message') return;
  const text = String((obj.detail.event && obj.detail.event.data && obj.detail.event.data.text) || '').trim().toLowerCase();
  const now = Date.now();
  if (cfg.commands && cfg.commands.some(c => text === c || text.startsWith(c + ' ')) && now - lastChat > cfg.chatCooldown * 1000) {
    lastChat = now;
    show();
  }
});
