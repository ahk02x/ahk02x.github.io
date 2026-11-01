// Drawer home: light streaks + tab cards.
const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
(() => {
  const c = document.querySelector('.streaks'), x = c.getContext('2d'); let W, H; const P = [];
  for (let i = 0; i < 2200; i++) P.push({ a: Math.random() * 6.283, r: Math.pow(Math.random(), .6), s: .4 + Math.random(), h: (Math.random() - .5) * .08 });
  function rs() { const d = devicePixelRatio || 1; W = innerWidth; H = innerHeight; c.width = W * d; c.height = H * d; x.setTransform(d, 0, 0, d, 0, 0) }
  rs(); addEventListener('resize', rs);
  function draw(t) {
    x.fillStyle = '#000'; x.fillRect(0, 0, W, H);
    const tilt = still ? .9 : .35 + .55 * (.5 + .5 * Math.sin(t / 6000)), R = Math.max(W, H) * .9, cx = W / 2, cy = H * .38, f = still ? 0 : t / 1000;
    x.strokeStyle = '#e8e8e8'; x.lineWidth = 1; x.globalAlpha = .55; x.beginPath();
    for (const p of P) {
      const rr = (p.r + f * .035 * p.s) % 1, r0 = rr * R, r1 = (rr + .022 * p.s) * R;
      x.moveTo(cx + Math.cos(p.a) * r0, cy + (Math.sin(p.a) * r0 * Math.cos(tilt) + p.h * R) * .6);
      x.lineTo(cx + Math.cos(p.a) * r1, cy + (Math.sin(p.a) * r1 * Math.cos(tilt) + p.h * R) * .6);
    }
    x.stroke(); x.globalAlpha = 1;
    if (!still && !document.hidden) requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
  document.addEventListener('visibilitychange', () => { if (!document.hidden && !still) requestAnimationFrame(draw) });
})();
(() => {
  const cards = [...document.querySelectorAll('.drawer .card')];
  cards.forEach((card, i) => {
    card.style.setProperty('--i', i); card.style.setProperty('--x', (8 + (i * 17) % 45) + '%');
    if (i % 2) { card.querySelector('.tab').style.left = 'auto'; card.querySelector('.tab').style.right = (8 + (i * 17) % 45) + '%' }
    card.querySelector('.tab').addEventListener('click', () => pick(card));
  });
  function pick(card) {
    const open = !card.classList.contains('up');
    cards.forEach(c => { const on = c === card && open; c.classList.toggle('up', on); c.querySelector('.tab').setAttribute('aria-expanded', on) });
  }
  pick(cards[cards.length - 1]);
})();
