/* Home hero intro: the stone A rises out of the ground in the middle of the hero, then slides right
   to its place, and the name and lede slide out to the left from behind it.
   Loaded right after the hero (not deferred) so the first paint is already the centred, text-hidden
   state. stone-a.js fires 'stone:locked' when the A locks; the slide starts then.
   Skipped (everything in place at once) when: reduced motion, ?stone= frames, or any width where the hero
   stacks the A under the words (phones, and narrow desktop windows where it wraps). */
(() => {
'use strict';
const hero = document.querySelector('.home .hero');
const text = hero && hero.firstElementChild;
const mark = hero && hero.querySelector('.hero-mark');
if (!text || !mark) return;
if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
if (matchMedia('(max-width:820px)').matches) return;          // stacked: the A sits under the text, nothing to slide out from
if (new URLSearchParams(location.search).has('stone')) return;

const DUR = 1100, LAG = 120;                // ms: the A moves first, the words follow a beat behind
const EDGE = 0.42;                          // fallback only, if the outline is missing: the A's half-width / box
const ease = u => u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
let geo = null, done = false, sliding = false;

function edgeAt() {                         // f(yFrac) -> the A's left edge as a share of its box, from the real mark
  const cv = mark.querySelector('canvas'), E = cv && cv.stoneLeftEdge;
  if (!E) return () => 0.5 - EDGE;          // stone-a.js not ready: a straight edge
  const N = E.length, inked = [];
  E.forEach((v, i) => { if (v != null) inked.push(i); });
  const r0 = inked[0], r1 = inked[inked.length - 1], k = Math.round(N * 0.12);
  // past the top and bottom of the A, carry its slant on, so the cut stays one clean diagonal
  const up = (E[r0 + k] - E[r0]) / k, down = (E[r1] - E[r1 - k]) / k;
  return f => {
    const r = f * N;
    if (r < r0) return E[r0] + up * (r - r0);
    if (r > r1) return E[r1] + down * (r - r1);
    return E[Math.min(N - 1, Math.max(0, Math.floor(r)))];
  };
}
function measure() {                        // layout with no transforms applied
  mark.style.transform = text.style.transform = '';
  const h = hero.getBoundingClientRect(), m = mark.getBoundingClientRect(), t = text.getBoundingClientRect();
  const markDx = (h.left + h.width / 2) - (m.left + m.width / 2);  // centre of the hero
  const edge = edgeAt();
  let maxX = 0;                             // the A's edge at its narrowest row across the text's height:
  for (let y = -40; y <= t.height + 40; y += 8) maxX = Math.max(maxX, edge((t.top + y - m.top) / m.height));  // start there and no row shows
  const side = m.left >= t.right - 1 && m.top < t.bottom - 1;     // the A beside the words; between ~820px and ~1100px the hero wraps it below them
  return { side, markDx, edge, mL: m.left, mT: m.top, mW: m.width, mH: m.height, tLeft: t.left, tTop: t.top, tW: t.width, tH: t.height,
           textDx: (m.left + markDx + maxX * m.width) - t.left };   // start: all of the text sits behind the A
}
function pose(pm, pt) {                     // pm, pt: 0 = start (centred, hidden), 1 = home
  const g = geo;
  const mdx = g.markDx * (1 - pm), tdx = g.textDx * (1 - pt);
  mark.style.transform = `translateX(${mdx}px)`;
  text.style.transform = `translateX(${tdx}px)`;
  // only the text left of the A's own outline shows, row by row: it reads as coming out from behind the A
  const pts = [], P = 40; let hidden = false;
  for (let y = -P; y <= g.tH + P; y += 4) {
    const ex = g.mL + mdx + g.edge((g.tTop + y - g.mT) / g.mH) * g.mW - (g.tLeft + tdx);  // the edge, in text-box px
    if (ex < g.tW + P) hidden = true;
    pts.push(`${Math.max(-P, ex).toFixed(1)}px ${y}px`);
  }
  text.style.clipPath = hidden ? `polygon(${-P}px ${-P}px, ${pts.join(', ')}, ${-P}px ${g.tH + P}px)` : '';
}
function hold() {
  if (done || sliding) return;              // mid-slide, a resize must not throw the A back to the centre
  geo = measure();
  if (!geo.side) return finish();           // stacked: nothing to come out from behind, show it all
  pose(0, 0);
}
function finish() {
  done = true;
  mark.style.transform = text.style.transform = text.style.clipPath = '';
  mark.style.willChange = text.style.willChange = '';
}
function slide() {
  if (done) return;
  geo = measure(); let t0 = null;
  if (!geo.side) return finish();
  // measure() clears the transforms to read the layout. Put the start pose straight back, in this same task:
  // otherwise this frame paints with the A already at home on the right, then it snaps back to the centre
  // on the next one, and for a frame the logo shows twice.
  pose(0, 0); sliding = true;
  const step = now => {
    if (t0 === null) t0 = now;
    const ms = now - t0;
    const pm = ease(Math.min(1, ms / DUR)), pt = ease(Math.min(1, Math.max(0, ms - LAG) / DUR));
    pose(pm, pt);
    if (ms < DUR + LAG) requestAnimationFrame(step); else finish();
  };
  requestAnimationFrame(step);
}

mark.style.position = 'relative'; mark.style.zIndex = '1';   // the A in front, the words behind it
mark.style.willChange = text.style.willChange = 'transform';
hold();
addEventListener('resize', hold);
if (document.fonts) document.fonts.ready.then(hold);   // the web font changes the words' width, and so whether the hero wraps
hero.addEventListener('stone:locked', slide, { once: true });
setTimeout(slide, 12000);                   // if stone-a.js never runs, the name still arrives
})();
