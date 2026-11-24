// /sq/logger.html: the exploded isometric of the logger box. Every part is generated from millimetre
// measurements of the printed case; the page's ledger, pinout and totals are plain HTML and need none of this.
(() => {
'use strict';
const NS = 'http://www.w3.org/2000/svg';
const $ = s => document.querySelector(s);
const svg = $('#rig'), stage = $('#stage'), rigCol = $('#rigcol');
if (!svg || !stage || !rigCol) return;
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- constants (millimetres, measured off the printed case) ---------- */
// Model frame: +X is the back wall (the pigtail exit), X = 0 is the open port face,
// +Y is the adapter-side wall, Y = 0 is the wall beside the Pi's HDMI edge.
const W = 99.8, D = 88.8, CX = W / 2, CY = D / 2, HB = 30.8, WT = 2.3, FL = 2.2, LT = 4.0;
const ER = 5.5, EI = 2.06;                              // corner ear radius, axis inset from the wall faces
const HEX_R = 6 / Math.sqrt(3), PITCH = 7.6, ROW = 6.59; // 6.0 mm across flats, 1.6 mm web
const WROWS = [10.86, 17.45, 24.04];                    // wall vent rows; nothing above z = 27.5
const GAP1 = 62;                                        // the port face is open from ear 0 up to here
const SINP = 0.57735, COSP = 0.8165;          // true isometric elevation
const DEG = Math.PI / 180;
const clamp = v => v < 0 ? 0 : v > 1 ? 1 : v;
const lerp = (a, b, k) => a + (b - a) * k;

function bezier(x1, y1, x2, y2) {
  return x => {
    if (x <= 0) return 0; if (x >= 1) return 1;
    let lo = 0, hi = 1, u = x;
    for (let i = 0; i < 22; i++) {
      u = (lo + hi) / 2;
      const v = 1 - u, bx = 3 * v * v * u * x1 + 3 * v * u * u * x2 + u * u * u;
      if (bx < x) lo = u; else hi = u;
    }
    const v = 1 - u;
    return 3 * v * v * u * y1 + 3 * v * u * u * y2 + u * u * u;
  };
}
const EASE = bezier(.62, .02, .12, 1);   // parts: soft launch, long overshoot-free settle
const ECAM = bezier(.5, 0, .2, 1);       // camera pull-back
const ELAB = bezier(.2, .7, .2, 1);      // leaders and type

function el(name, attrs, parent) {
  const e = document.createElementNS(NS, name);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}

/* ---------- layers ---------- */
const defs = el('defs', {}, svg);
const grad = el('radialGradient', { id: 'sqShadow' }, defs);
el('stop', { offset: '0', style: 'stop-color:var(--shadow)' }, grad);
el('stop', { offset: '1', style: 'stop-color:var(--shadow);stop-opacity:0' }, grad);
const shadow = el('ellipse', { fill: 'url(#sqShadow)' }, svg);
const axisG = el('g', { class: 'axis' }, svg);
const axes = [0, 1, 2, 3, 4].map(() => el('line', {}, axisG));
const partsG = el('g', {}, svg);
const leadLayer = el('g', {}, svg);
const labLayer = el('g', {}, svg);

/* ---------- geometry helpers ---------- */
const parts = [], glints = [];
function mkPart(id, li, delay, delta, z0, rank) {
  const p = { id, li, delay, delta, z0, rank, g: el('g', { class: 'part' }, partsG), prims: [], off: [0, 0, 0] };
  parts.push(p); return p;
}
function P(part, subs, cls) {
  const e = el('path', { class: cls }, part.g);
  part.prims.push({ el: e, subs });
  return e;
}
const mix = k => 'color-mix(in oklab, var(--lit) ' + Math.round(k * 100) + '%, var(--shade))';
const rect = (x, y, w, d) => [[x, y], [x + w, y], [x + w, y + d], [x, y + d]];
function rrect(x, y, w, d, r, n) {
  const out = [], cs = [[x + w - r, y + r, -90], [x + w - r, y + d - r, 0], [x + r, y + d - r, 90], [x + r, y + r, 180]];
  for (const [cx, cy, a0] of cs) for (let i = 0; i <= n; i++) {
    const a = (a0 + 90 * i / n) * DEG; out.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
  }
  return out;
}
function ngon(cx, cy, r, n, rot) {
  const out = [];
  for (let i = 0; i < n; i++) { const a = ((rot || 0) + 360 * i / n) * DEG; out.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); }
  return out;
}
const atZ = (fp, z) => fp.map(q => [q[0], q[1], z]);
// vertical faces along a footprint (closed) or a polyline (open), back-face culled and painted far to near
function skirt(part, fp, z0, h, mat, o) {
  o = o || {};
  const fb = o.bottom || fp, n = fp.length, sides = [];
  for (let i = 0; i < (o.open ? n - 1 : n); i++) {
    const j = (i + 1) % n, a = fp[i], b = fp[j];
    let nx = b[1] - a[1], ny = -(b[0] - a[0]);
    const m = Math.hypot(nx, ny) || 1; nx /= m; ny /= m;
    if (o.inside) { nx = -nx; ny = -ny; }
    const vis = (nx + ny) * 0.7071;
    if (vis < -0.1) continue;
    sides.push({ i, vis, k: clamp(0.5 + 0.5 * (nx - ny)), pts: [[a[0], a[1], z0 + h], [b[0], b[1], z0 + h], [fb[j][0], fb[j][1], z0], [fb[i][0], fb[i][1], z0]] });
  }
  if (!sides.length) return;
  if (o.round) {
    // a curved surface: facets carry the shading without seams, one outline traces each visible run
    let runs = [[sides[0]]];
    for (let q = 1; q < sides.length; q++) { if (sides[q].i === sides[q - 1].i + 1) runs[runs.length - 1].push(sides[q]); else runs.push([sides[q]]); }
    if (!o.open && runs.length > 1 && sides[0].i === 0 && sides[sides.length - 1].i === n - 1) runs = [runs.pop().concat(runs[0])].concat(runs.slice(1));
    for (const s of sides) { const e = P(part, [{ p: s.pts, c: 1 }], 'side ' + mat); e.style.fill = e.style.stroke = mix(s.k); }
    P(part, runs.map(r => ({ p: r.map(s => s.pts[0]).concat([r[r.length - 1].pts[1], r[r.length - 1].pts[2]], r.map(s => s.pts[3]).reverse()), c: 1 })), 'edge ' + mat);
    return;
  }
  sides.sort((p, q) => p.vis - q.vis);
  for (const s of sides) P(part, [{ p: s.pts, c: 1 }], 'side ' + mat).style.fill = mix(s.k);
}
function prism(part, fp, z0, h, mat, o) {
  skirt(part, fp, z0, h, mat, o);
  if (!(o && o.noTop)) P(part, [{ p: atZ(fp, z0 + h), c: 1 }], 'top ' + mat);
}
const box = (part, x, y, z, w, d, h, mat, o) => prism(part, rect(x, y, w, d), z, h, mat, o);
const xface = (part, X, y0, y1, z0, z1, cls) => P(part, [{ p: [[X, y0, z0], [X, y1, z0], [X, y1, z1], [X, y0, z1]], c: 1 }], cls);
const sorted = list => list.sort((a, b) => a[0] - b[0]).forEach(c => c[1]());
function wire(part, pts, cls) {
  P(part, [{ p: pts, c: 0 }], 'wire wc');
  return P(part, [{ p: pts, c: 0 }], 'wire ' + cls);
}

// the inside walls of a through-hole that face the camera, as one polygon
function tunnel(front, back) {
  const n = front.length, c = [0, 0, 0], vis = [];
  for (const q of front) { c[0] += q[0] / n; c[1] += q[1] / n; c[2] += q[2] / n; }
  for (let i = 0; i < n; i++) {
    const a = front[i], b = front[(i + 1) % n];
    vis.push(c[0] + c[1] + c[2] - (a[0] + b[0] + a[1] + b[1] + a[2] + b[2]) / 2 > 1e-6);
  }
  let s = 0;
  while (!(vis[s] && !vis[(s + n - 1) % n])) { if (++s >= n) return null; }
  const f = [front[s]], bk = [back[s]];
  for (let i = s; i < s + n && vis[i % n]; i++) { f.push(front[(i + 1) % n]); bk.push(back[(i + 1) % n]); }
  return { p: f.concat(bk.reverse()), c: 1 };
}
const hexAt = (a, z, r) => ngon(a, z, r || HEX_R, 6, 30);
// one flat wall with its vent field: mkF/mkB map (along, z) onto the near and far faces of the wall
function wall(part, mkF, mkB, a0, a1, z0, z1, holes, mat, k, lights) {
  const tun = holes.map(h => tunnel(h.map(q => mkF(q[0], q[1])), h.map(q => mkB(q[0], q[1]))));
  P(part, tun.filter(Boolean), 'side ' + mat).style.fill = 'var(--bore)';
  for (const [idx, colour, o] of lights || []) {
    if (!tun[idx]) continue;
    const e = P(part, [tun[idx]], 'glint'); e.style.fill = colour; glints.push({ el: e, o });
  }
  const outline = [mkF(a0, z0), mkF(a1, z0), mkF(a1, z1), mkF(a0, z1)];
  P(part, [{ p: outline, c: 1 }].concat(holes.map(h => ({ p: h.map(q => mkF(q[0], q[1])), c: 1 }))), 'side eo ' + mat).style.fill = mix(k);
}
// staggered rows of whole cells, centred on mid
function ventRows(mid, counts) {
  const out = [];
  counts.forEach((n, r) => { for (let i = 0; i < n; i++) out.push([mid + (i - (n - 1) / 2) * PITCH, WROWS[r]]); });
  return out;
}
const nearest = (cells, a, b) => cells.reduce((best, c, i) => Math.hypot(c[0] - a, c[1] - b) < Math.hypot(cells[best][0] - a, cells[best][1] - b) ? i : best, 0);

// case outline: the shell rectangle plus four round ears. Outer and inner loops share indices,
// so a slice of both is a piece of rim. Index 44 is the end of the open port face.
const ARC = 10;
const EARS = [[EI, EI, -1, -1], [W - EI, EI, 1, -1], [W - EI, D - EI, 1, 1], [EI, D - EI, -1, 1]];
function caseLoop(inset) {
  const h = Math.sqrt(ER * ER - (inset - EI) * (inset - EI)), hx = W - inset, hy = D - inset, out = [];
  const J = [
    [[inset, EI + h], [EI + h, inset]],
    [[W - EI - h, inset], [hx, EI + h]],
    [[hx, D - EI - h], [W - EI - h, hy]],
    [[EI + h, hy], [inset, D - EI - h]]
  ];
  const TAU = 2 * Math.PI, mod = v => ((v % TAU) + TAU) % TAU;
  EARS.forEach((e, i) => {
    const a1 = Math.atan2(J[i][0][1] - e[1], J[i][0][0] - e[0]), a2 = Math.atan2(J[i][1][1] - e[1], J[i][1][0] - e[0]);
    const am = Math.atan2(e[3], e[2]) + (inset ? Math.PI : 0);      // outside bulges out, inside bulges into the cavity
    let d = mod(a2 - a1); if (mod(am - a1) > d) d -= TAU;
    for (let k = 0; k <= ARC; k++) { const a = a1 + d * k / ARC; out.push([e[0] + ER * Math.cos(a), e[1] + ER * Math.sin(a)]); }
  });
  return out;
}
const OUT = caseLoop(0), INN = caseLoop(WT);
const SHELL = OUT.slice();                    // closed outline, shared by the lid
OUT.push([0, GAP1]); INN.push([WT, GAP1]);
function rim(part, k0, k1, cap0, cap1) {
  const o = OUT.slice(k0, k1 + 1), i = INN.slice(k0, k1 + 1);
  P(part, [{ p: atZ(o.concat(i.slice().reverse()), HB), c: 1 }], 'top m-pla ns');
  const edges = [{ p: atZ(o, HB), c: 0 }, { p: atZ(i, HB), c: 0 }];
  if (cap0) edges.push({ p: atZ([o[0], i[0]], HB), c: 0 });
  if (cap1) edges.push({ p: atZ([o[o.length - 1], i[i.length - 1]], HB), c: 0 });
  P(part, edges, 'edge m-pla');
}
const tapped = (part, e) => P(part, [{ p: atZ(ngon(e[0], e[1], 1.4, 10), HB), c: 1 }], 'void');

/* ---------- timeline constants ---------- */
const SPAN = 0.5;                                    // how long one part takes to travel, in t
const DELAY = [0, .05, .1, .15, .2, .25, .25];        // screws, lid, rtc, pi, adapter, pigtail, base
const LSTART = [.44, .50, .56, .62, .68, .74, .80];       // when each callout starts drawing

/* ---------- parts (assembled coordinates) ---------- */
const PX0 = 3, PY0 = 5.5, PI_Z = FL + 3.2, BT = PI_Z + 1.4;      // Pi board: USB end at X = 0, GPIO edge toward +Y
const pq = (px, py) => [PX0 + 85 - px, PY0 + 56 - py];          // Pi drawing coordinates into the case
const AX0 = 3, AY0 = 66, AB = FL + 1.6;                         // CAN adapter board origin and top
const TERM = [0, 1, 2].map(i => [58, AY0 + 5.5 + i * 3.5, AB + 3.3]);
const EXIT = [W, 71, 10.5];                                     // centre of the big hex in the back wall

// 06 base, split so parts seated inside the tray sit between its far and near halves
const baseBack = mkPart('baseBack', 6, DELAY[6], [0, 0, -152], 0, 0);
{
  P(baseBack, [{ p: atZ(INN.concat([[0, GAP1], OUT[0]]), FL), c: 1 }], 'floor');
  P(baseBack, [{ p: [[OUT[0][0], OUT[0][1], FL], [INN[0][0], INN[0][1], FL], [INN[0][0], INN[0][1], HB], [OUT[0][0], OUT[0][1], HB]], c: 1 }], 'side m-in');
  // wall beside the HDMI edge: 27 cells, five left out around the USB-C power cut
  const front = ventRows(CX, [11, 10, 11]).filter(c => c[0] < 69 || c[0] > 85);
  wall(baseBack, (a, z) => [a, WT, z], (a, z) => [a, 0, z], INN[ARC][0], INN[ARC + 1][0], FL, HB,
    front.map(c => hexAt(c[0], c[1])).concat([rect(71, 5.6, 12, 6)]), 'm-in', .1);
  // what is left of the port face, with the slot for the adapter's USB-C lead
  wall(baseBack, (a, z) => [WT, a, z], (a, z) => [0, a, z], GAP1, INN[43][1], FL, HB, [rect(AY0 + 4, 3.2, 10, 5.6)], 'm-in', .9);
  for (const c of [0, 1, 3]) skirt(baseBack, INN.slice(c * (ARC + 1), (c + 1) * (ARC + 1)), FL, HB - FL, 'm-in', { inside: true, open: true, round: true });
  rim(baseBack, 0, ARC + 1 + ARC / 2 + 1, true, false);
  rim(baseBack, 3 * (ARC + 1) + ARC / 2 - 1, 44, false, true);
  tapped(baseBack, EARS[0]);
  sorted([[3.5, 3.5], [61.5, 3.5], [3.5, 52.5], [61.5, 52.5]].map(h => { const c = pq(h[0], h[1]); return [c[0] + c[1], () => prism(baseBack, ngon(c[0], c[1], 3, 12), FL, PI_Z - FL, 'm-in', { round: true })]; }));
}
const baseFront = mkPart('baseFront', 6, DELAY[6], [0, 0, -152], 0, 0);
{
  // back wall: 9 / 8 / 9 rows with the cells around the cable exit replaced by one large hex
  const back = ventRows(CY, [9, 8, 9]).filter(c => !(Math.abs(c[0] - EXIT[1]) < 10.6 && Math.abs(c[1] - EXIT[2]) < 11.4));
  wall(baseFront, (a, z) => [W, a, z], (a, z) => [W - WT, a, z], OUT[2 * ARC + 1][1], OUT[2 * ARC + 2][1], 0, HB,
    back.map(c => hexAt(c[0], c[1])).concat([hexAt(EXIT[1], EXIT[2], 12 / Math.sqrt(3))]), 'm-pla', 1);
  // adapter-side wall: 32 cells
  const rear = ventRows(CX, [11, 10, 11]);
  wall(baseFront, (a, z) => [a, D, z], (a, z) => [a, D - WT, z], OUT[3 * ARC + 3][0], OUT[3 * ARC + 2][0], 0, HB,
    rear.map(c => hexAt(c[0], c[1])), 'm-pla', 0,
    [[nearest(rear, 12, WROWS[0]), '#FF4B43', .8], [nearest(rear, 23, WROWS[1]), '#39D98A', .55]]);
  for (const c of [1, 3, 2]) skirt(baseFront, OUT.slice(c * (ARC + 1), (c + 1) * (ARC + 1)), 0, HB, 'm-pla', { open: true, round: true });
  rim(baseFront, ARC + 1 + ARC / 2, 3 * (ARC + 1) + ARC / 2, false, false);
  for (const c of [1, 3, 2]) tapped(baseFront, EARS[c]);
}

// 05 OBD-II pigtail. Inside the case: three wires off the adapter's terminal, gathered into the
// cable jacket and zip-tied. Outside: the cable leaves through the back wall to the plug.
const obdIn = mkPart('obdIn', 5, DELAY[5], [0, 0, -36], 7, 5);
{
  ['w-g', 'w-br', 'w-y'].forEach((cls, i) => {
    const t = TERM[i], y = EXIT[1] + (i - 1) * 1.5;
    const run = [t, [63, t[1], t[2]], [71.5, y, 9.6], [80, y, EXIT[2]]];
    wire(obdIn, run, cls);
    if (cls === 'w-br') P(obdIn, [{ p: run, c: 0 }], 'wire w-wh');
  });
  const jacket = [[79, EXIT[1], EXIT[2]], [W - .3, EXIT[1], EXIT[2]]];
  P(obdIn, [{ p: jacket, c: 0 }], 'cab cabc');
  P(obdIn, [{ p: jacket, c: 0 }], 'cab');
  const band = [[84.2, EXIT[1], EXIT[2]], [86.8, EXIT[1], EXIT[2]]];
  P(obdIn, [{ p: band, c: 0 }], 'tie tiec');
  P(obdIn, [{ p: band, c: 0 }], 'tie');
  box(obdIn, 84, EXIT[1] - 2, EXIT[2] + 3.6, 3, 4, 2.2, 'm-chip');                       // zip-tie head
  P(obdIn, [{ p: [[85.5, EXIT[1] + 1.6, EXIT[2] + 5], [86.5, EXIT[1] - 3.5, EXIT[2] + 8.5], [88.5, EXIT[1] - 8, EXIT[2] + 10.5]], c: 0 }], 'tail');
}
const obdOut = mkPart('obdOut', 5, DELAY[5], [0, 0, -36], 7, 6);
{
  const lead = [[W, EXIT[1], EXIT[2]], [W + 7, EXIT[1], EXIT[2]], [W + 13, EXIT[1], 9.6], [W + 18.5, EXIT[1], 9]];
  P(obdOut, [{ p: lead, c: 0 }], 'cab cabc');
  P(obdOut, [{ p: lead, c: 0 }], 'cab');
  const yc = EXIT[1], x0 = W + 25, x1 = W + 45, zt = 17;
  box(obdOut, W + 17, yc - 10.5, 3, 8, 21, 12, 'm-chip');
  P(obdOut, [{ p: [[x0, yc + 19, zt], [x1, yc + 19, zt], [x1, yc + 16, 0], [x0, yc + 16, 0]], c: 1 }], 'side m-chip').style.fill = 'var(--shade)';
  P(obdOut, [{ p: [[x0, yc - 19, zt], [x1, yc - 19, zt], [x1, yc + 19, zt], [x0, yc + 19, zt]], c: 1 }], 'top m-chip');
  P(obdOut, [{ p: [[x1, yc - 19, zt], [x1, yc + 19, zt], [x1, yc + 16, 0], [x1, yc - 16, 0]], c: 1 }], 'side m-chip');
  P(obdOut, [{ p: [[x1, yc - 16.9, 15.3], [x1, yc + 16.9, 15.3], [x1, yc + 14.5, 1.7], [x1, yc - 14.5, 1.7]], c: 1 }], 'void');
  // looking into the plug: pin 8 on the left, pin 1 on the right
  const pinQ = (i, row) => { const y = yc + (3.5 - i) * 3.6, z = row ? 4.4 : 10; return [[x1, y - 1, z], [x1, y + 1, z], [x1, y + 1, z + 2.5], [x1, y - 1, z + 2.5]]; };
  const plain = [], special = { '0:2': 'var(--w-g)', '0:3': 'var(--w-y)', '1:2': 'var(--w-br)', '1:0': 'var(--void)' };
  for (let row = 0; row < 2; row++) for (let i = 0; i < 8; i++) {
    const key = row + ':' + i;
    if (special[key]) P(obdOut, [{ p: pinQ(i, row), c: 1 }], 'pin').style.fill = special[key];
    else plain.push({ p: pinQ(i, row), c: 1 });
  }
  P(obdOut, plain, 'pin');
}

// 03 Raspberry Pi 4 Model B
const pi = mkPart('pi', 3, DELAY[3], [0, 0, 16], PI_Z, 2);
{
  prism(pi, rrect(PX0, PY0, 85, 56, 3, 3), PI_Z, 1.4, 'm-pi');
  P(pi, [[3.5, 3.5], [61.5, 3.5], [3.5, 52.5], [61.5, 52.5]].map(h => ({ p: atZ(ngon(...pq(h[0], h[1]), 1.35, 10), BT), c: 1 })), 'void');
  const pb = (px, py, w, d, h, mat, extra) => {
    const x = PX0 + 85 - px - w, y = PY0 + 56 - py - d;
    return [x + w / 2 + y + d / 2, () => { box(pi, x, y, BT, w, d, h, mat); if (extra) extra(x, y, w, d, BT + h); }];
  };
  const fins = (x, y, w, d, z) => {
    const lines = [];
    for (let f = 1.4; f < w - .5; f += 2.2) lines.push({ p: [[x + f, y + .5, z], [x + f, y + d - .5, z]], c: 0 });
    P(pi, lines, 'mark');
  };
  const sink = (px, py, w, d, h) => pb(px, py, w, d, h, 'm-met', fins);
  // M2 x 4 hold-down screws in the four mounting holes; they ride with the board
  const m2 = (px, py) => { const c = pq(px, py); return [c[0] + c[1], () => {
    prism(pi, ngon(c[0], c[1], 1.9, 12), BT, 1.2, 'm-m2', { round: true });
    P(pi, [{ p: [[c[0] - 1.1, c[1], BT + 1.2], [c[0] + 1.1, c[1], BT + 1.2]], c: 0 }], 'mark');
  }]; };
  sorted([
    m2(3.5, 3.5), m2(61.5, 3.5), m2(3.5, 52.5), m2(61.5, 52.5),
    pb(7.1, 1, 50.8, 5.1, 2.5, 'm-chip', () => {                       // 40-pin header, far row first
      const pins = [];
      for (let j = 1; j >= 0; j--) for (let i = 19; i >= 0; i--) {
        const c = pq(8.37 + i * 2.54, 2.23 + j * 2.54);
        pins.push({ p: [[c[0], c[1], BT + 2.5], [c[0], c[1], BT + 8.5]], c: 0 });
      }
      P(pi, pins, 'pinl');
    }),
    pb(6.5, 8.5, 12, 10, 1.6, 'm-met'),                                // radio can
    sink(22, 16.5, 14.5, 14.5, 8.4),                                   // SoC under the large heatsink
    sink(40.5, 19.5, 10, 14, 7),                                       // RAM
    sink(55, 29.5, 8.5, 8.5, 5.5),                                     // USB controller
    pb(2, 19, 3, 18, 2.6, 'm-chip'),                                   // display connector
    pb(44.2, 37, 3, 12, 2.6, 'm-chip'),                                // camera connector
    pb(67, 2.25, 21, 16, 13.5, 'm-met'),                               // Ethernet
    pb(70.5, 22.4, 17.5, 13.2, 16, 'm-met'),                           // USB 3
    pb(70.5, 40.4, 17.5, 13.2, 16, 'm-met'),                           // USB 2
    pb(6.7, 49.5, 9, 7.5, 3.2, 'm-met'),                               // USB-C power
    pb(22.5, 50, 7, 7, 3, 'm-met'),                                    // micro-HDMI 0
    pb(36, 50, 7, 7, 3, 'm-met'),                                      // micro-HDMI 1
    pb(50.5, 44.5, 7, 12.5, 6, 'm-chip')                               // audio
  ]);
}

// 02 DS3231 RTC "for Pi": a small black board whose female header presses straight down onto
// the pin-1 end of the GPIO header (odd pins 1 to 9), yellow coin cell under a spring clip on top
const RZ = BT + 2.5, RB = RZ + 8.5 + 1.2;                              // header bottom, board top
const RTC_PINS = [4, 3, 2, 1, 0].map(k => pq(8.37 + k * 2.54, 4.77));  // far to near along the header
const rtc = mkPart('rtc', 2, DELAY[2], [0, 0, 64], RZ, 3);
{
  const hx = RTC_PINS[0][0] - 1.27, hy = RTC_PINS[0][1] - 1.27;
  box(rtc, hx, hy, RZ, 12.7, 2.54, 8.5, 'm-chip');                     // the tall socket block
  P(rtc, [1, 2, 3, 4].map(i => ({ p: [[hx + i * 2.54, hy + 2.54, RZ], [hx + i * 2.54, hy + 2.54, RZ + 8.5]], c: 0 })), 'mark seam');
  const bx = hx - 2.6, by = hy + 2.54 - 17;
  prism(rtc, rrect(bx, by, 18, 17, .8, 2), RB - 1.2, 1.2, 'm-blk');
  P(rtc, [[2.6, 13.4], [5.8, 13.4]].map(q => ({ p: atZ(rect(bx + q[0], by + q[1], 1.8, 1.3), RB), c: 1 })), 'top m-met');   // solder pads
  P(rtc, [{ p: [[bx + 13, by + 14, RB], [bx + 14.8, by + 14, RB]], c: 0 }, { p: [[bx + 13.9, by + 13.1, RB], [bx + 13.9, by + 14.9, RB]], c: 0 }], 'mark silk');   // the + mark
  const cx = bx + 9.2, cy = by + 6.8;
  box(rtc, cx - 7.3, cy - 2.4, RB, 1, 4.8, 3.4, 'm-met');              // clip leg, behind the cell
  prism(rtc, ngon(cx, cy, 6.2, 24), RB, 2.8, 'm-yel', { round: true });
  box(rtc, cx - 7.3, cy - 2.4, RB + 2.8, 10.6, 4.8, .6, 'm-met');       // spring clip across the cell's face
}

// 04 CAN adapter: USB-C and status LEDs at the port end, green screw terminal toward the back
const can = mkPart('can', 4, DELAY[4], [0, 0, -12], FL, 4);
{
  prism(can, rrect(AX0, AY0, 55, 18, 1.2, 2), FL, 1.6, 'm-blk');
  const led = (x, y, colour) => {
    P(can, [{ p: atZ(ngon(x + .9, y + .6, 2.7, 12), AB + .05), c: 1 }], 'halo').style.fill = colour;
    P(can, [{ p: atZ(rect(x, y, 1.8, 1.2), AB + .6), c: 1 }], 'led').style.fill = colour;
  };
  sorted([
    [70, () => box(can, AX0 - .5, AY0 + 4.5, AB, 7.5, 9, 3.2, 'm-met')],
    [80, () => { led(12.5, AY0 + 2, '#3EA8FF'); led(15.6, AY0 + 2, '#39D98A'); }],
    [93, () => led(12.5, AY0 + 14.6, '#FF4B43')],
    [98, () => box(can, 20, AY0 + 5.5, AB, 7, 7, 1, 'm-chip')],
    [109, () => box(can, 32, AY0 + 6.5, AB, 5, 5, 1.3, 'm-chip')],
    [111, () => box(can, 40.5, AY0 + 1.5, AB, 5, 2.6, 4.5, 'm-chip')],
    [129, () => {
      box(can, 49, AY0 + 3.5, AB, 9, 11, 9.5, 'm-grn');
      for (const t of TERM) {
        P(can, [{ p: atZ(ngon(53, t[1], 1.5, 10), AB + 9.5), c: 1 }], 'top m-met');
        P(can, [{ p: [[52, t[1], AB + 9.5], [54, t[1], AB + 9.5]], c: 0 }], 'mark');
        xface(can, 58, t[1] - 1.3, t[1] + 1.3, AB + 1.6, AB + 5, 'void');
      }
    }]
  ]);
}

// 01 honeycomb lid with the pressed-in badge
const lid = mkPart('lid', 1, DELAY[1], [0, 0, 118], HB, 9);
const LTOP = HB + LT;
{
  // badge, drawn in its own frame: u runs along the long side, v toward the adapter-side wall
  const SU = -11, QU = 9.6, RX = 5.9, RY = 4.2, SW = 5.2;      // a plain wordmark, about 39 mm wide
  const sLine = [];
  for (let i = 0; i <= 26; i++) { const a = (25 + 245 * i / 26) * DEG; sLine.push([SU + RX * Math.cos(a), -RY - RY * Math.sin(a)]); }
  for (let i = 1; i <= 26; i++) { const a = (90 - 245 * i / 26) * DEG; sLine.push([SU + RX * Math.cos(a), RY - RY * Math.sin(a)]); }
  const thick = (line, w) => {
    const L = [], R = [];
    line.forEach((q, i) => {
      const a = line[Math.max(0, i - 1)], b = line[Math.min(line.length - 1, i + 1)], m = Math.hypot(b[0] - a[0], b[1] - a[1]);
      const tx = (b[0] - a[0]) / m, ty = (b[1] - a[1]) / m;
      L.push([q[0] - ty * w / 2, q[1] + tx * w / 2]); R.push([q[0] + ty * w / 2, q[1] - tx * w / 2]);
    });
    return L.concat(R.reverse());
  };
  const oval = (a, b) => ngon(0, 0, 1, 40).map(q => [QU + a * q[0], b * q[1]]);
  const tailAt = (back, hw, end) => [[3.8 - back, 5.1 - back, 1], [3.8 - back, 5.1 - back, -1], [10.1 - end, 11.1 - end, -1], [10.1 - end, 11.1 - end, 1]]
    .map(q => [QU + q[0] + q[2] * hw * .7071, q[1] - q[2] * hw * .7071]);
  const on = uv => uv.map(q => [CX + q[0], CY + q[1], LTOP]);

  // the 102 whole cells of the printed lid, straight from its generated point list: thirteen
  // columns 6.58 mm apart, alternate columns offset half a pitch, rows listed per column
  const cells = [];
  [[-6, '123456789'], [-5, '0123456789'], [-4, '0123456789a'], [-3, '012789'], [-2, '01289a'], [-1, '012789'], [0, '01289a'], [1, '012789'], [2, '01289a'], [3, '012789'], [4, '0123456789a'], [5, '0123456789'], [6, '123456789']].forEach(([i, rows]) => {
    for (const ch of rows) cells.push([CX - i * PITCH * Math.sqrt(3) / 2, (i & 1 ? 10.2 : 6.4) + PITCH * parseInt(ch, 16)]);
  });
  const hp = (c, z) => atZ(ngon(c[0], c[1], HEX_R, 6, 0), z);
  const tun = cells.map(c => tunnel(hp(c, LTOP), hp(c, HB)));
  skirt(lid, SHELL, HB, LT, 'm-pla', { round: true });
  P(lid, tun, 'side m-pla').style.fill = 'var(--bore)';
  for (const [x, y, colour, o] of [[17, 71, '#3EA8FF', .5], [23.6, 74.8, '#39D98A', .35]]) {
    const e = P(lid, [tun[nearest(cells, x, y)]], 'glint'); e.style.fill = colour; glints.push({ el: e, o });
  }
  P(lid, [{ p: atZ(SHELL, LTOP), c: 1 }].concat(cells.map(c => ({ p: hp(c, LTOP), c: 1 }))), 'top m-pla eo');

  // two red inlays, pressed in flush: the S and the Q. The Q's counter is a hole in the glyph,
  // so it stays black lid material. The last patch hides the seam where the tail joins the bowl.
  P(lid, [{ p: on(thick(sLine, SW)), c: 1 }], 'top m-red');
  P(lid, [{ p: on(oval(9.9, 11)), c: 1 }, { p: on(oval(4.5, 6)), c: 1 }], 'top m-red eo');
  P(lid, [{ p: on(tailAt(-3.4, 2.1, 0)), c: 1 }], 'top m-red');
  P(lid, [{ p: on(tailAt(-2.2, 1.75, 2)), c: 1 }], 'top m-red ns');

  // what the screws leave behind: a 7.2 mm counterbore around a 3.7 mm clearance hole on each ear
  for (const e of EARS) {
    P(lid, [{ p: atZ(ngon(e[0], e[1], 3.6, 16), LTOP), c: 1 }], 'side m-pla').style.fill = 'var(--bore)';
    P(lid, [{ p: atZ(ngon(e[0], e[1], 1.85, 12), LTOP), c: 1 }], 'void');
  }
}

// 01 four #6-32 x 6 chassis screws, the only fasteners. Pan heads on washers sit proud of the lid;
// the 3.5 mm shanks are their own layer so the lid can hide them while they are still in their holes.
const SCREW_UP = 138;
const scrS = mkPart('scrS', 0, DELAY[0], [0, 0, SCREW_UP], LTOP, 9);
const scrH = mkPart('scrH', 0, DELAY[0], [0, 0, SCREW_UP], LTOP, 9);
for (const c of [0, 1, 3, 2]) {
  const e = EARS[c];
  prism(scrS, ngon(e[0], e[1], 1.75, 10), LTOP - 5.5, 6, 'm-scr', { round: true, noTop: true });
  P(scrS, [1.2, 2.4, 3.6, 4.8].map(d => ({ p: [150, 105, 60, 15, -30].map(a => [e[0] + 1.75 * Math.cos(a * DEG), e[1] + 1.75 * Math.sin(a * DEG), LTOP - 5.5 + d + (150 - a) / 400]), c: 0 })), 'mark thread');
  prism(scrH, ngon(e[0], e[1], 4, 16), LTOP, .5, 'm-scr', { round: true });
  prism(scrH, ngon(e[0], e[1], 3.1, 16), LTOP + .5, 1.7, 'm-scr', { round: true });
  P(scrH, [{ p: [[e[0] - 1.9, e[1], LTOP + 2.2], [e[0] + 1.9, e[1], LTOP + 2.2]], c: 0 }, { p: [[e[0], e[1] - 1.9, LTOP + 2.2], [e[0], e[1] + 1.9, LTOP + 2.2]], c: 0 }], 'mark');
}

/* ---------- callouts ---------- */
const LAB = [
  { n: '01', name: 'CHASSIS SCREWS', wide: '#6-32 × 6 · 4.0 mm in boss', nar: '#6-32 × 6 mm', part: scrH, aR: [EARS[1][0] + 3.1, EARS[1][1], LTOP + 1.4], aL: [EARS[3][0] - 3.1, EARS[3][1], LTOP + 1.4], side: -1 },
  { n: '02', name: 'HONEYCOMB LID', wide: '102 cells · 3180 mm² open', nar: '3180 mm² open', part: lid, aR: [W, 12, HB + 1.8], aL: [12, D, HB + 1.8], side: 1 },
  { n: '03', name: 'DS3231 RTC', wide: '3.3 V only · plugs onto GPIO', nar: '3.3 V · plug-on', part: rtc, aR: [RTC_PINS[4][0] + 3.9, RTC_PINS[4][1] - 15.7, RB], aL: [RTC_PINS[0][0] - 3.9, RTC_PINS[0][1] + 1.27, RB - .6], side: -1 },
  { n: '04', name: 'RASPBERRY PI 4', wide: '2.886 W → 0.1145 W halted', nar: '0.1145 W halted', part: pi, aR: [88, 5.5, BT - .7], aL: [3, 61.5, BT - .7], side: 1 },
  { n: '05', name: 'CANABLE2', wide: 'slcan · 500 kbps · 0.235 W', nar: 'slcan · 500 kbps', part: can, aR: [58, AY0 + 3.5, AB + 5], aL: [3, AY0 + 18, FL + .8], side: -1 },
  { n: '06', name: 'OBD-II PIGTAIL', wide: 'out the back wall · pin 16 open', nar: 'out the back wall', part: obdOut, aR: [W + 8, EXIT[1], EXIT[2]], aL: [W + 25, EXIT[1] + 19, 9], side: 1 },
  { n: '07', name: 'PRINTED BASE', wide: '99.8 × 88.8 × 30.8 mm', nar: '99.8 × 88.8 × 30.8', part: baseFront, aR: [W, 30, 6], aL: [9, D, 15], side: -1 }
];
for (const L of LAB) {
  L.lg = el('g', { class: 'leadg' }, leadLayer);
  L.path = el('path', { class: 'lead', pathLength: '1' }, L.lg);
  L.dot = el('circle', { class: 'dot', r: '2.2' }, L.lg);
  L.g = el('g', { class: 'lab' }, labLayer);
  L.t1 = el('text', { class: 'l1' }, L.g);
  const num = el('tspan', { class: 'num' }, L.t1); num.textContent = L.n + '  ';
  L.t1.appendChild(document.createTextNode(L.name));
  L.t2 = el('text', { class: 'l2' }, L.g);
}

// screen-space extent of the whole stack at t (unit scale, neutral yaw); the layout fits to these
function poseBox(t) {
  let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
  for (const p of parts) for (const pr of p.prims) for (const sub of pr.subs) for (const q of sub.p) {
    const x = q[0] - CX, y = q[1] - CY, sx = (x - y) * .7071, sy = SINP * (x + y) * .7071 - COSP * (q[2] + p.delta[2] * t);
    if (sx < x0) x0 = sx; if (sx > x1) x1 = sx; if (sy < y0) y0 = sy; if (sy > y1) y1 = sy;
  }
  return { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, hw: (x1 - x0) / 2, h: y1 - y0 };
}
const EX = poseBox(1), AS = poseBox(0);

/* ---------- camera + projection ---------- */
const cam = { c: .7071, s: .7071, S: 2, X0: 0, Y0: 0 };
function proj(x, y, z) {
  x -= CX; y -= CY;
  return [cam.X0 + cam.S * (x * cam.c - y * cam.s), cam.Y0 + cam.S * (SINP * (x * cam.s + y * cam.c) - COSP * z)];
}
function draw(part) {
  const ox = part.off[0] - CX, oy = part.off[1] - CY, oz = part.off[2];
  const c = cam.c, s = cam.s, S = cam.S, ky = S * SINP, kz = S * COSP, X0 = cam.X0, Y0 = cam.Y0;
  for (const pr of part.prims) {
    let d = '';
    for (const sub of pr.subs) {
      const pts = sub.p;
      for (let i = 0; i < pts.length; i++) {
        const q = pts[i], x = q[0] + ox, y = q[1] + oy;
        d += (i ? 'L' : 'M') + (X0 + S * (x * c - y * s)).toFixed(2) + ' ' + (Y0 + ky * (x * s + y * c) - kz * (q[2] + oz)).toFixed(2);
      }
      if (sub.c) d += 'Z';
    }
    pr.el.setAttribute('d', d);
  }
}

/* ---------- layout (runs on resize) ---------- */
let LY = null;
function layout() {
  const r = stage.getBoundingClientRect(), Wp = r.width, Hp = r.height;
  if (!Wp || !Hp) return;
  svg.setAttribute('viewBox', '0 0 ' + Wp.toFixed(1) + ' ' + Hp.toFixed(1));
  const wide = Wp >= 720, hS = (Hp - 52) / EX.h, col = 140, ew = 2 * EX.hw;
  svg.classList.toggle('narrow', !wide);
  let SE, oxE;
  if (wide) { SE = Math.min(hS, (Wp / 2 - 34 - 196) / EX.hw); oxE = Wp / 2; }
  else { SE = Math.min(hS, (Wp - 22 - col) / ew); oxE = (Wp - (ew * SE + 18 + col)) / 2 + EX.hw * SE; }
  const SA = Math.min(SE * (wide ? 1.5 : 1.25), (Wp / 2 - 12) / (AS.hw + 6), (Hp - 90) / (AS.h + 6));
  LY = { Wp, Hp, SE, SA, oxE, oxA: Wp / 2, cy: Hp / 2 + 6, wide };
  // callout rest positions come from the fully exploded pose at the neutral yaw
  cam.c = cam.s = .7071; cam.S = SE; cam.X0 = oxE - SE * EX.cx; cam.Y0 = LY.cy - SE * EX.cy;
  for (const L of LAB) {
    L.sd = wide ? L.side : 1;
    L.a = L.sd > 0 ? L.aR : L.aL;
    const d = L.part.delta, p = proj(L.a[0] + d[0], L.a[1] + d[1], L.a[2] + d[2]);
    L.lx = wide ? oxE + L.sd * (EX.hw * SE + 34) : oxE + EX.hw * SE + 18;
    L.ly = p[1] - 16;
    for (const t of [L.t1, L.t2]) { t.setAttribute('x', L.lx.toFixed(1)); t.setAttribute('text-anchor', L.sd > 0 ? 'start' : 'end'); }
    L.t1.setAttribute('y', (L.ly + 4).toFixed(1));
    L.t2.setAttribute('y', (L.ly + 18).toFixed(1));
    L.t2.textContent = wide ? L.wide : L.nar;
  }
}

/* ---------- the one driver: everything below reads state.t ---------- */
const state = { t: reduced ? 1 : 0, playing: !reduced, phase: 'holdIn', ph: 900, yaw: 45, focus: -1 };
const DUR = { out: 6500, holdOut: 4200, in: 4200, holdIn: 1500 };
const ledgerItems = Array.from(document.querySelectorAll('#ledger li'));
const scrub = $('#scrub'), readout = $('#readout'), playBtn = $('#play'), icPlay = $('#icPlay'), icPause = $('#icPause');
const tickNums = [];
{
  const host = $('#ticks');
  LSTART.forEach((v, i) => {
    const pos = 'calc(6px + ' + v + ' * (100% - 12px))';
    const a = document.createElement('i'); a.style.left = pos; host.appendChild(a);
    const b = document.createElement('b'); b.style.left = pos; b.textContent = '0' + (i + 1); host.appendChild(b);
    tickNums.push(b);
  });
}
let lastOrder = '', lastActive = -2, lastRead = '', lastFocus = -2, lastPlaying = null, lastGlow = -1;

function render() {
  if (!LY) return;
  const t = state.t, ec = ECAM(clamp(t / 0.72));
  cam.c = Math.cos(state.yaw * DEG); cam.s = Math.sin(state.yaw * DEG);
  cam.S = lerp(LY.SA, LY.SE, ec);
  cam.X0 = lerp(LY.oxA, LY.oxE, ec) - cam.S * lerp(AS.cx, EX.cx, ec);
  cam.Y0 = LY.cy - cam.S * lerp(AS.cy, EX.cy, ec);
  svg.style.setProperty('--mm', cam.S.toFixed(3));

  // part offsets
  for (const p of parts) {
    p.off[2] = p.delta[2] * EASE(clamp((t - p.delay) / SPAN));
  }
  // LED light caught in the vent cells, only while the box is closed
  const glow = Math.round(clamp(1 - t / .09) * 50) / 50;
  if (glow !== lastGlow) { lastGlow = glow; for (const g of glints) g.el.style.opacity = (g.o * glow).toFixed(2); }
  // paint order: seated parts sit between the tray's back and front halves
  const baseZ = baseBack.off[2];
  // (the cable outside the back wall is always nearer than the wall it leaves through)
  const key = p => p === baseBack ? 0 : p === baseFront ? 50 : p === lid ? 99 : p === scrH ? 101 : p === scrS ? (scrS.off[2] - lid.off[2] > 6.5 ? 100 : 98) : p === obdOut ? 60 + p.rank
    : (p.z0 + p.off[2] - baseZ < HB - 7 ? 10 : 60) + p.rank;
  const order = parts.slice().sort((a, b) => key(a) - key(b));
  const sig = order.map(p => p.id).join();
  if (sig !== lastOrder) { lastOrder = sig; for (const p of order) partsG.appendChild(p.g); }
  for (const p of parts) draw(p);

  // ground shadow + assembly axes
  const sp = proj(CX + 9, CY + 4, baseZ);
  shadow.setAttribute('cx', sp[0].toFixed(1)); shadow.setAttribute('cy', sp[1].toFixed(1));
  shadow.setAttribute('rx', (cam.S * 92).toFixed(1)); shadow.setAttribute('ry', (cam.S * 52).toFixed(1));
  shadow.setAttribute('opacity', lerp(1, .6, ec).toFixed(3));
  // two screw axes, the clock module's drop onto its header pins, and the pigtail's path: terminal down to the wire ends, cable down to its hole in the back wall
  [[EARS[3][0], EARS[3][1], baseZ + HB, scrH.off[2] + LTOP], [EARS[1][0], EARS[1][1], baseZ + HB, scrH.off[2] + LTOP],
   [TERM[1][0], TERM[1][1], obdIn.off[2] + TERM[1][2], can.off[2] + TERM[1][2]],
   [EXIT[0], EXIT[1], baseZ + EXIT[2], obdOut.off[2] + EXIT[2]],
   [RTC_PINS[2][0], RTC_PINS[2][1] + 1.27, pi.off[2] + BT + 8.5, rtc.off[2] + RZ]].forEach((c, i) => {
    const a = proj(c[0], c[1], c[2]), b = proj(c[0], c[1], c[3]);
    const ln = axes[i];
    ln.setAttribute('x1', a[0].toFixed(1)); ln.setAttribute('y1', a[1].toFixed(1));
    ln.setAttribute('x2', b[0].toFixed(1)); ln.setAttribute('y2', b[1].toFixed(1));
  });
  axisG.setAttribute('opacity', (ec * .9).toFixed(3));

  // callouts
  let active = -1;
  LAB.forEach((L, i) => {
    const lp = ELAB(clamp((t - LSTART[i]) / .12)), tp = ELAB(clamp((t - LSTART[i] - .05) / .12));
    if (tp > .02) active = i;
    if (lp <= 0) { L.lg.setAttribute('visibility', 'hidden'); L.g.setAttribute('opacity', '0'); return; }
    L.lg.setAttribute('visibility', 'visible');
    const o = L.part.off, a = proj(L.a[0] + o[0], L.a[1] + o[1], L.a[2] + o[2]);
    const endx = L.lx - L.sd * 8;
    let kx = a[0] + L.sd * Math.abs(a[1] - L.ly);
    if (L.sd * (kx - endx) > 0) kx = endx;
    L.path.setAttribute('d', 'M' + a[0].toFixed(1) + ' ' + a[1].toFixed(1) + 'L' + kx.toFixed(1) + ' ' + L.ly.toFixed(1) + 'L' + endx.toFixed(1) + ' ' + L.ly.toFixed(1));
    L.path.style.strokeDashoffset = (1 - lp).toFixed(3);
    L.dot.setAttribute('cx', a[0].toFixed(1)); L.dot.setAttribute('cy', a[1].toFixed(1));
    L.dot.setAttribute('opacity', clamp(lp * 4).toFixed(2));
    L.g.setAttribute('opacity', tp.toFixed(3));
    L.g.setAttribute('transform', 'translate(' + (L.sd * (1 - tp) * -8).toFixed(1) + ' 0)');
  });
  if (state.focus >= 0) active = state.focus;
  if (active !== lastActive) {
    lastActive = active;
    LAB.forEach((L, i) => { L.g.classList.toggle('on', i === active); L.lg.classList.toggle('on', i === active); });
    ledgerItems.forEach((li, i) => li.classList.toggle('on', i === active));
    tickNums.forEach((b, i) => b.classList.toggle('on', i === active));
  }
  if (state.focus !== lastFocus) {
    lastFocus = state.focus;
    for (const p of parts) p.g.style.opacity = state.focus < 0 || p.li === state.focus ? '' : '.22';
  }

  // transport
  const v = Math.round(t * 1000);
  if (+scrub.value !== v) scrub.value = v;
  scrub.style.setProperty('--p', (t * 100).toFixed(2) + '%');
  const rd = 't ' + t.toFixed(2) + ' · yaw ' + state.yaw.toFixed(1) + '°';
  if (rd !== lastRead) { lastRead = rd; readout.textContent = rd; }
  if (state.playing !== lastPlaying) {
    lastPlaying = state.playing;
    // the icons are SVG elements, which have no .hidden property; the attribute is what the stylesheet reads
    icPlay.toggleAttribute('hidden', state.playing); icPause.toggleAttribute('hidden', !state.playing);
    playBtn.setAttribute('aria-label', state.playing ? 'Pause' : 'Play');
  }
}

/* ---------- clock: autoplay only ever moves state.t ---------- */
let last = 0, orbitT = 0, par = 0, parTarget = 0, running = false;
function advance(dt) {
  if (!state.playing) return;
  if (state.phase === 'out') { state.t += dt / DUR.out; if (state.t >= 1) { state.t = 1; state.phase = 'holdOut'; state.ph = 0; } }
  else if (state.phase === 'in') { state.t -= dt / DUR.in; if (state.t <= 0) { state.t = 0; state.phase = 'holdIn'; state.ph = 0; } }
  else { state.ph += dt; if (state.ph >= DUR[state.phase]) state.phase = state.phase === 'holdOut' ? 'in' : 'out'; }
}
function frame(now) {
  const dt = Math.min(now - last, 64); last = now;
  advance(dt);
  if (!reduced) {
    orbitT += dt;
    par += (parTarget - par) * Math.min(1, dt / 420);
    state.yaw = 45 + 5.5 * Math.sin(orbitT / 16000 * 2 * Math.PI) + par * 2.5;
  }
  render();
  if (reduced && !state.playing) { running = false; return; }
  requestAnimationFrame(frame);
}
function start() { if (running) return; running = true; last = performance.now(); requestAnimationFrame(frame); }

/* ---------- controls ---------- */
scrub.addEventListener('input', () => {
  state.playing = false;
  state.t = scrub.value / 1000;
  if (!running) render();
});
playBtn.addEventListener('click', () => {
  state.playing = !state.playing;
  if (state.playing) {
    if (state.t >= .999) { state.phase = 'holdOut'; state.ph = DUR.holdOut - 500; }
    else { state.phase = 'out'; }
    start();
  } else if (!running) render();
});
const setFocus = i => { state.focus = i; if (!running) render(); };
ledgerItems.forEach((li, i) => {
  li.addEventListener('pointerenter', () => setFocus(i));
  li.addEventListener('pointerleave', () => setFocus(-1));
  li.addEventListener('focus', () => setFocus(i));
  li.addEventListener('blur', () => setFocus(-1));
});
if (!reduced) {
  stage.addEventListener('pointermove', e => {
    if (e.pointerType !== 'mouse') return;
    const r = stage.getBoundingClientRect();
    parTarget = clamp((e.clientX - r.left) / r.width) * 2 - 1;
  });
  stage.addEventListener('pointerleave', () => { parTarget = 0; });
}
// Everything above built without throwing, so the drawing can take its place: the rig and its controls
// ship hidden, and the ledger only becomes focusable once focusing a row does something.
rigCol.hidden = false;
rigCol.parentNode.classList.add('lg-live');
ledgerItems.forEach(li => { li.tabIndex = 0; });
new ResizeObserver(() => { layout(); render(); }).observe(stage);
layout(); render();
if (!reduced) start();
})();
