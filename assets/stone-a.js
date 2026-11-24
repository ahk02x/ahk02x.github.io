/* The stone A: it comes down, the ground gives way, and it rises back out like a snake until it locks.
   Plays once on load (prefers-reduced-motion: the finished mark). Colours are the theme's --ink on the page.
   Built from ~/Projects/brand/a-stone-1118/anim/mythos (Mythos build + front-page pacing), red climber removed. */
(() => {
'use strict';
/* The mark: potrace vector of original-1656.png, in potrace units.
   Drawn through transform(.1,0,0,-.1,0,1656) it lands on the 1656x1656 image grid. */
const MARK = new Path2D("M6742 15128 c-17 -35 -48 -101 -70 -148 -22 -47 -56 -121 -77 -165 -20 -44 -57 -123 -80 -175 -24 -52 -57 -126 -75 -165 -18 -38 -64 -140 -102 -225 -39 -85 -86 -189 -105 -230 -20 -41 -43 -93 -53 -115 -9 -22 -43 -96 -74 -165 -31 -69 -61 -134 -66 -145 -5 -11 -32 -69 -59 -129 -28 -59 -51 -110 -51 -111 0 -2 -20 -45 -44 -97 -49 -105 -54 -116 -182 -398 -51 -113 -106 -233 -123 -268 -17 -34 -31 -65 -31 -68 0 -3 -32 -72 -72 -155 -39 -82 -69 -151 -67 -153 2 -2 182 -5 399 -7 l395 -4 0 279 1 279 113 23 c63 13 115 25 116 26 1 2 11 23 22 48 24 52 225 472 350 730 210 436 258 530 273 530 8 0 60 -25 115 -56 99 -55 292 -160 475 -257 52 -27 115 -61 140 -75 66 -36 148 -80 310 -167 80 -43 179 -96 220 -118 41 -22 151 -82 244 -134 l169 -93 101 11 101 11 215 -82 c118 -45 305 -115 415 -156 110 -40 286 -105 390 -144 105 -39 226 -84 270 -100 l80 -28 3 -261 2 -261 543 -2 c299 -2 551 -2 560 0 26 5 26 6 -68 217 -54 122 -136 306 -165 375 -18 41 -45 103 -61 138 -16 35 -29 65 -29 68 0 2 -77 180 -171 396 -229 527 -237 545 -265 606 -13 29 -24 55 -24 58 0 3 -12 31 -26 62 -14 31 -55 127 -91 212 -116 276 -366 835 -377 842 -6 4 -770 8 -1697 8 l-1686 0 -31 -62z M7092 14048 c-5 -7 -40 -76 -77 -153 -37 -77 -121 -252 -187 -390 -306 -637 -323 -673 -314 -682 14 -14 38 13 55 62 19 53 42 95 52 95 10 0 28 -52 31 -90 4 -44 -1 -44 323 15 390 72 410 77 408 103 -2 17 2 22 22 22 17 0 25 6 25 18 0 20 -52 199 -104 356 -20 61 -36 111 -36 113 0 14 39 -8 118 -67 51 -39 95 -70 97 -70 2 0 1 19 -2 41 l-6 41 44 -28 c24 -16 50 -35 57 -42 20 -19 53 -34 59 -28 3 3 -32 47 -79 98 -115 127 -248 300 -248 324 0 2 56 -25 124 -61 143 -75 145 -76 114 -32 -69 97 -180 195 -315 278 -164 100 -148 93 -161 77z M8790 13175 c-69 -13 -186 -33 -260 -45 -142 -23 -546 -94 -765 -135 -71 -14 -206 -38 -300 -54 -93 -16 -249 -44 -345 -61 -96 -17 -290 -51 -430 -75 -140 -24 -294 -51 -342 -61 l-88 -16 0 -254 c0 -140 2 -254 4 -254 2 0 251 23 553 50 301 28 602 55 668 61 66 5 212 19 325 29 311 30 496 46 825 76 l300 27 120 -22 c66 -12 194 -33 285 -47 91 -14 242 -38 335 -54 488 -84 607 -100 612 -83 3 7 -30 19 -89 32 -128 29 -896 166 -1038 185 -63 9 -139 21 -167 27 l-53 10 0 345 c0 269 -3 344 -12 343 -7 0 -69 -11 -138 -24z M8437 12232 c-3 -4 23 -78 59 -163 36 -84 67 -164 70 -176 l6 -23 -1623 1 c-893 0 -1644 4 -1669 8 l-45 8 40 3 c22 1 54 4 70 6 17 3 80 11 140 19 61 8 227 34 370 57 l260 43 -160 8 c-332 17 -681 4 -970 -36 -318 -44 -636 -86 -730 -98 -38 -4 -137 -17 -220 -28 -82 -12 -158 -21 -167 -21 -17 0 -18 -56 -18 -1035 l0 -1035 1766 0 1766 0 47 23 c25 13 56 30 67 37 19 12 26 10 66 -23 68 -56 78 -45 28 28 l-30 43 53 33 c28 18 71 44 94 58 35 21 49 41 85 114 44 92 45 93 163 157 33 17 70 41 82 52 21 19 22 19 77 2 l56 -18 0 -224 c0 -210 -1 -226 -21 -253 -11 -16 -19 -30 -17 -31 2 -1 208 -5 458 -8 l454 -5 128 -310 c70 -170 127 -313 128 -317 0 -5 -1196 -8 -2657 -8 -2574 0 -2657 1 -2618 19 22 10 53 21 68 25 65 16 809 296 863 325 48 25 80 22 -326 26 -358 3 -333 7 -540 -75 -85 -33 -209 -81 -275 -107 -66 -25 -140 -53 -165 -63 -25 -9 -144 -54 -265 -100 -121 -45 -228 -86 -237 -91 -17 -9 -18 -69 -18 -1039 l0 -1029 768 -3 767 -3 65 23 c36 13 84 31 107 40 38 15 46 15 120 -3 77 -18 292 -37 304 -26 4 3 -28 38 -70 76 l-78 70 56 7 c140 17 233 30 323 45 89 15 106 15 230 -1 807 -105 708 -84 881 -181 l149 -83 51 15 c29 8 55 18 59 22 4 3 -60 40 -142 81 -82 41 -149 78 -150 81 0 4 12 9 28 13 15 3 70 17 122 31 52 14 113 30 135 34 22 5 137 34 255 64 319 83 450 111 462 99 12 -12 -40 -176 -107 -336 -53 -127 -48 -132 63 -64 l81 49 25 77 c14 42 32 98 42 124 l18 46 -29 44 c-38 57 -49 12 97 379 l50 126 156 6 c520 18 986 38 1109 47 78 5 183 10 233 10 105 0 89 -7 290 125 85 56 169 109 185 118 31 17 436 39 1000 54 l229 6 95 49 96 49 123 -27 c127 -28 146 -28 312 -5 36 5 155 21 265 36 254 33 230 27 309 80 37 25 71 45 75 45 5 0 19 9 33 20 23 17 33 18 114 10 182 -19 222 -13 401 66 27 12 51 13 143 3 96 -10 113 -9 128 4 34 29 81 46 216 77 76 17 138 30 139 28 1 -2 1 -360 -1 -795 l-2 -793 -2645 0 -2644 0 -80 -25 c-45 -14 -81 -30 -81 -35 0 -6 354 -10 954 -10 754 0 955 -3 959 -12 3 -7 53 -132 112 -278 59 -146 113 -278 120 -295 21 -46 22 -59 3 -58 -10 0 -1547 1 -3415 2 -3371 2 -3398 2 -3358 22 22 10 117 55 210 100 332 157 525 253 525 261 0 4 -152 8 -338 8 l-339 0 -223 -114 -224 -113 -28 -69 c-55 -132 -68 -164 -89 -216 -11 -29 -29 -71 -39 -93 -26 -57 -220 -525 -220 -530 0 -3 -11 -28 -24 -57 -13 -29 -46 -109 -74 -178 -28 -69 -74 -181 -102 -250 -28 -69 -71 -172 -95 -230 -23 -58 -75 -180 -114 -271 -39 -92 -71 -174 -71 -183 0 -15 194 -16 2288 -16 2267 0 2290 0 2433 21 113 16 189 20 350 20 124 -1 260 4 340 13 74 8 202 22 284 32 91 10 213 16 309 15 l158 -2 102 -52 101 -52 885 -1 c487 -1 1025 -2 1195 -3 l310 -1 39 -103 c21 -56 60 -160 87 -232 l48 -130 -22 -24 c-12 -13 -62 -60 -112 -104 -49 -44 -156 -142 -237 -218 l-146 -139 13 -42 c7 -24 29 -86 48 -138 19 -52 85 -229 146 -393 117 -313 228 -618 256 -702 9 -27 38 -79 64 -115 41 -56 275 -394 434 -627 l49 -72 2046 -3 c1126 -2 2049 -2 2051 -1 2 1 -14 46 -36 100 -22 54 -70 170 -106 258 -36 88 -79 194 -97 235 -17 41 -93 230 -169 420 -119 297 -226 561 -263 650 -6 14 -14 34 -18 45 -4 11 -12 31 -18 45 -5 14 -34 84 -62 155 -29 72 -66 164 -83 205 -16 41 -33 84 -37 95 -5 11 -27 64 -49 118 -23 54 -41 101 -41 106 0 4 -95 75 -211 157 -116 82 -220 157 -232 167 -52 44 -66 46 -355 53 -183 4 -282 3 -286 -4 -3 -6 15 -22 41 -37 27 -15 102 -63 168 -106 188 -123 356 -229 530 -336 l160 -98 -1130 -3 -1130 -2 -245 70 c-252 72 -543 165 -687 220 -80 31 -82 32 -99 78 -34 92 -146 378 -165 420 l-19 43 1112 -6 c611 -3 1114 -8 1117 -10 2 -3 -43 -5 -100 -5 -109 0 -483 -15 -679 -27 l-115 -8 215 -6 c118 -4 527 -7 909 -8 l694 -2 36 23 c20 13 58 36 84 53 l47 30 0 485 0 486 -40 103 c-22 56 -40 109 -40 116 0 8 -21 31 -47 52 -132 106 -321 261 -346 282 -15 14 -76 95 -136 181 -215 310 -218 318 -40 131 68 -72 125 -129 126 -127 3 2 -50 101 -137 259 l-44 77 -165 107 c-91 58 -173 112 -182 120 -13 11 -76 13 -330 11 l-314 -3 90 -48 c321 -173 616 -327 625 -327 5 0 10 -3 10 -7 0 -10 -3052 -5 -3061 5 -10 12 -249 616 -249 631 0 8 6 11 15 7 8 -3 455 -6 993 -7 1102 -2 1386 -9 927 -23 -154 -4 -334 -11 -400 -15 l-120 -7 95 -7 c52 -3 492 -9 977 -13 l881 -6 59 39 c32 22 66 42 76 46 16 6 17 36 17 444 0 241 1 624 2 852 l3 413 -39 34 c-22 19 -78 62 -125 96 -48 34 -88 65 -91 68 -8 9 -350 282 -386 308 -18 12 -85 53 -150 90 -66 38 -164 96 -219 129 l-100 61 -315 3 c-195 3 -317 0 -320 -6 -7 -12 3 -17 310 -145 146 -61 294 -124 330 -140 36 -16 103 -43 150 -62 l85 -33 -1634 -3 c-899 -1 -1638 1 -1642 5 -7 7 -189 455 -238 583 l-19 50 1241 -1 c1223 -2 1464 -9 727 -23 -206 -4 -376 -9 -378 -11 -12 -12 224 -17 963 -18 l840 -2 80 51 80 50 3 723 2 722 -22 19 c-13 11 -99 79 -192 151 -138 107 -371 293 -547 437 -16 13 -125 56 -246 96 l-218 74 -185 -4 c-102 -1 -257 -4 -345 -4 -188 -1 -182 -9 35 -46 80 -13 219 -39 310 -56 l165 -33 -165 -6 c-91 -3 -720 -7 -1398 -8 l-1232 -1 -20 43 c-11 23 -46 105 -78 182 l-58 140 -51 3 c-28 2 -54 -1 -56 -6z m1304 -1016 c63 -13 164 -36 226 -50 138 -32 149 -32 331 0 333 58 390 66 462 65 77 -2 110 -14 69 -26 -68 -21 -216 -100 -197 -106 2 0 108 -7 236 -14 243 -13 258 -12 350 27 50 22 30 26 -55 11 -74 -13 -273 -10 -259 5 3 3 52 21 108 39 l103 35 175 -6 c96 -3 266 -9 377 -13 l202 -6 100 34 99 33 89 -17 c64 -12 141 -17 271 -17 l182 0 -2 -687 -3 -687 -2185 0 -2185 -1 -3 241 -2 241 -68 53 c-37 30 -70 57 -75 60 -4 4 3 57 15 119 19 95 20 113 8 121 -11 7 -8 28 19 122 18 62 45 156 59 208 14 52 26 96 27 98 2 2 186 2 411 1 225 -1 423 -2 439 -1 29 1 332 82 450 120 79 26 93 26 226 -2z m4477 -6266 l-3 -451 -2811 1 c-2993 0 -2852 -2 -2933 44 -26 14 -43 10 344 77 219 38 402 90 876 250 l146 49 352 0 352 0 124 31 c195 47 265 51 1100 55 591 3 815 8 926 19 80 8 208 18 285 21 151 7 154 8 394 102 226 88 311 114 656 202 86 22 159 42 162 45 31 30 32 5 30 -445z M2345 4160 c-16 -12 -127 -81 -247 -156 -119 -74 -221 -140 -226 -147 -5 -7 -26 -52 -46 -102 -20 -49 -41 -98 -46 -107 -6 -10 -10 -22 -10 -28 0 -6 -9 -29 -19 -53 -11 -23 -41 -94 -66 -157 -58 -143 -163 -395 -181 -435 -7 -16 -50 -120 -94 -230 -45 -110 -113 -276 -152 -370 -164 -396 -187 -454 -217 -525 -18 -41 -36 -84 -41 -95 -22 -47 -140 -356 -140 -365 0 -6 8 -10 18 -10 1919 -6 3678 2 3700 16 14 9 63 47 109 85 47 38 92 73 101 78 10 5 39 49 66 98 27 48 69 122 94 163 57 94 145 244 280 475 57 99 135 232 172 295 72 124 206 356 388 670 30 52 70 119 89 148 33 49 35 57 31 113 -3 37 -10 64 -19 70 -9 6 -727 8 -1902 7 -1329 -2 -1887 0 -1887 8 0 5 17 19 38 30 20 12 82 47 137 79 55 32 109 63 120 69 52 29 461 274 604 362 l55 34 -340 0 c-324 0 -340 -1 -369 -20z");

let FG = '#e9eae6';
const SIZE = 1656, GROUND = 1518;
const TAU = Math.PI * 2;

/* pieces, top to bottom: apex, slab1, slab2, slab3, feet */
const CUT = [-20, 444, 694, 971, 1228, 1676];
const CEN = [[846, 286], [828, 569], [836, 833], [826, 1100], [826, 1378]];
const EDGE = [[545, 1145], [385, 1272], [313, 1358], [215, 1433], [88, 1562]];

/* ---------- timeline (seconds) ---------- */
const T_FALL0 = 0.45, T_HIT = 1.15;          // the A comes down, hits
const T_LURCH = 1.50, T_PLUNGE = 1.66;       // the ground gives way
const T_BURIED = 2.22;                       // only the head is left
const T_RISE0 = 3.10, T_RISE1 = 7.70;        // the snake rises
const T_LOCK = [8.28, 8.11, 7.97, 7.85];     // apex, slab1, slab2, slab3 drop home
const T_BUILT = 8.28;
const G_T0 = T_BUILT + 0.20, G_FALL = 0.50, G_LAND = G_T0 + G_FALL;

const SINK1 = 12, SINK2 = 12;
const D0 = GROUND - 435 + 30;                // offset that leaves the apex sitting in the ground
const STRETCH = 13;                          // extra gap per joint while the body is moving

const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const smooth = u => { u = clamp(u, 0, 1); return u * u * (3 - 2 * u); };
const pulse = (u, a) => u <= 0 ? 0 : (u / a) * Math.exp(1 - u / a);
function keys(t, k) {                         // smooth keyframes [[t,v],...]
  if (t <= k[0][0]) return k[0][1];
  for (let i = 1; i < k.length; i++) if (t < k[i][0]) {
    const a = k[i - 1], b = k[i];
    return a[1] + (b[1] - a[1]) * smooth((t - a[0]) / (b[0] - a[0]));
  }
  return k[k.length - 1][1];
}
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let x = Math.imul(seed ^ seed >>> 15, 1 | seed); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; }; }

/* ---------- stone motion ---------- */
let topVis = 0;                               // logo units visible above the square (viewport dependent)

function baseD(t) {
  if (t < T_HIT) {
    const start = -(GROUND + topVis + 90);
    if (t < T_FALL0) return start;
    const u = (t - T_FALL0) / (T_HIT - T_FALL0);
    return start * (1 - u * u);
  }
  if (t < T_PLUNGE) {
    let d = SINK1 * (1 - Math.exp(-(t - T_HIT) / 0.035));
    if (t > T_LURCH) d += SINK2 * (1 - Math.exp(-(t - T_LURCH) / 0.03));
    return d;
  }
  if (t < T_BURIED) {
    const u = (t - T_PLUNGE) / (T_BURIED - T_PLUNGE), d0 = SINK1 + SINK2;
    return d0 + (D0 - d0) * Math.pow(u, 1.9);
  }
  if (t < T_RISE0) return D0;
  if (t < T_RISE1) {
    const u = (t - T_RISE0) / (T_RISE1 - T_RISE0);
    const w = u * u * (3 - 2 * u);
    const r = w + 0.3 * Math.sin(8 * Math.PI * w) / (8 * Math.PI);   // rises in soft surges
    return D0 * (1 - r);
  }
  return 0;
}
function stretch(t, i) {
  const n = 4 - i;
  if (!n || t < T_RISE0) return 0;
  const tl = T_LOCK[i], dur = 0.085 * Math.sqrt(n) + 0.03, full = -n * STRETCH;
  if (t >= tl) return 0;
  if (t > tl - dur) { const u = (t - (tl - dur)) / dur; return full * (1 - u * u); }
  return full * smooth((t - T_RISE0) / 1.2);
}
function yOff(t, i) {
  let y = baseD(t) + stretch(t, i);
  if (t > T_HIT && t < T_HIT + 0.6) y += 3.5 * (4 - i) * pulse(t - T_HIT - (4 - i) * 0.018, 0.045); // stack compresses on landing
  return y;
}
const AMAX = 105, FREQ = 0.45, WAVE_K = TAU / 1350, T_DEC0 = T_RISE0 + 2.2, T_SWAY1 = 7.5;
function sway(t, i) {
  if (t <= T_RISE0 || t >= T_SWAY1) return [0, 0];
  const A = AMAX * smooth((t - T_RISE0) / 1.0) * (1 - smooth((t - T_DEC0) / (T_SWAY1 - T_DEC0)));
  const ph = TAU * FREQ * (t - T_RISE0);
  const hHead = GROUND - (CEN[0][1] + yOff(t, 0));
  const f = h => A * (1 - Math.exp(-Math.max(h, 0) / 330)) * Math.sin(ph - WAVE_K * (hHead - h));
  const h = GROUND - (CEN[i][1] + yOff(t, i));
  const slope = (f(h + 40) - f(h - 40)) / 80;
  const lim = i ? 0.045 : 0.13;                 // wide slabs may only lean a little; the head leads the turn
  return [f(h), lim * Math.tanh(Math.atan(slope) * (i ? 0.13 : 0.34) / lim)];
}
const HEAD_TILT = [[T_BURIED - 0.05, 0], [T_BURIED + 0.14, 0.10], [2.62, 0.10], [2.86, -0.065], [3.08, -0.065], [3.75, 0]];
function pose(t, i) {
  const [x, r] = sway(t, i);
  let rot = r, dx = x;
  if (i === 0 && t > T_BURIED - 0.05 && t < 3.75) { const k = keys(t, HEAD_TILT); rot += k; dx += k * 120; }
  let dy = yOff(t, i);
  if (i === 0) dy -= 285 * Math.abs(Math.sin(rot)) * smooth((t - T_RISE0) / 0.5);   // neck lifts so a tilted head never digs into slab 1
  return [dx, dy, rot];
}

/* ---------- camera shake ---------- */
const IMPACTS = [[T_HIT, 18, 0.12], [T_LURCH, 5, 0.07], [T_BURIED, 11, 0.10],
                 [T_LOCK[3], 2.5, 0.05], [T_LOCK[2], 3, 0.05], [T_LOCK[1], 3.5, 0.05], [T_LOCK[0], 9, 0.08]];
function shake(t) {
  let x = 0, y = 0;
  for (const [t0, a, tau] of IMPACTS) {
    const u = t - t0;
    if (u >= 0 && u < tau * 8) { const e = a * Math.exp(-u / tau); y += e * Math.cos(TAU * 19 * u); x += e * 0.45 * Math.sin(TAU * 23 * u + 1); }
  }
  const w1 = smooth((t - T_PLUNGE) / 0.08) * (1 - smooth((t - T_BURIED) / 0.05));
  if (w1 > 0) { y += 4 * w1 * Math.sin(TAU * 31 * t); x += 3.5 * w1 * Math.sin(TAU * 27 * t + 2); }
  const w2 = smooth((t - 2.55) / 0.3) * (1 - smooth((t - 3.3) / 0.5));
  if (w2 > 0) { y += 2.6 * w2 * Math.sin(TAU * 29 * t); x += 1.6 * w2 * Math.sin(TAU * 24 * t + 2); }
  return [x, y];
}

/* ---------- dust, chips, cracks: all generated once from a fixed seed ---------- */
const puffs = [], chips = [], cracks = [];
(function build() {
  const R = rng(1118), rr = (a, b) => a + (b - a) * R();
  const puff = (t0, x, y, vx, vy, r0, r1, life, a) => puffs.push({ t0, x, y, vx, vy, r0, r1, life, a, k: rr(2.6, 4.2) });
  const chip = (t0, x, y, vx, vy, size, life = 3, col = FG) => {
    const n = 3 + (R() * 3 | 0), v = [];
    for (let j = 0; j < n; j++) { const an = (j + rr(-0.3, 0.3)) / n * TAU, rad = size * rr(0.55, 1); v.push(Math.cos(an) * rad, Math.sin(an) * rad); }
    chips.push({ t0, x, y, vx, vy, v, life, col, rot: rr(0, TAU), w: rr(-14, 14) });
  };
  const out = x => x < 828 ? -1 : 1;
  const footX = () => R() < 0.5 ? rr(88, 590) : rr(1058, 1562);

  // 1. the A lands
  for (let j = 0; j < 60; j++) { const x = footX(); puff(T_HIT + rr(0, 0.05), x, GROUND - rr(0, 16), out(x) * rr(150, 1500), -rr(10, 420), rr(34, 70), rr(110, 230), rr(0.9, 2.4), rr(0.14, 0.3)); }
  for (let j = 0; j < 46; j++) { const x = footX(); chip(T_HIT + rr(0, 0.03), x, GROUND - 4, out(x) * rr(60, 900) + rr(-120, 120), -rr(450, 1650), rr(7, 24)); }
  // 2. the ground lurches
  for (let j = 0; j < 12; j++) { const x = footX(); puff(T_LURCH, x, GROUND - 4, out(x) * rr(60, 400), -rr(20, 160), rr(14, 26), rr(50, 110), rr(0.6, 1.2), rr(0.08, 0.16)); }
  for (let j = 0; j < 10; j++) { const x = footX(); chip(T_LURCH, x, GROUND - 3, rr(-200, 200), -rr(250, 700), rr(4, 11)); }
  // 3. it goes through
  for (let j = 0; j < 80; j++) { const x = rr(70, 1580), tt = T_PLUNGE + rr(0, T_BURIED - T_PLUNGE); puff(tt, x, GROUND - rr(0, 20), rr(-260, 260) + out(x) * rr(0, 380), -rr(120, 1000), rr(20, 44), rr(90, 230), rr(1.0, 2.6), rr(0.08, 0.2)); }
  for (let j = 0; j < 44; j++) { const x = rr(80, 1570), tt = T_PLUNGE + rr(0.04, T_BURIED - T_PLUNGE); chip(tt, x, GROUND - 4, rr(-380, 380), -rr(500, 1700), rr(5, 17)); }
  // 4. the head catches on the rim
  for (let j = 0; j < 26; j++) { const x = rr(520, 1170); puff(T_BURIED + rr(0, 0.04), x, GROUND - rr(0, 18), out(x) * rr(80, 760), -rr(30, 380), rr(18, 34), rr(70, 170), rr(0.9, 2.0), rr(0.1, 0.2)); }
  for (let j = 0; j < 22; j++) { const x = rr(540, 1150); chip(T_BURIED + rr(0, 0.03), x, GROUND - 4, out(x) * rr(40, 520), -rr(350, 1150), rr(4, 15)); }
  // 5. something stirs
  for (let j = 0; j < 14; j++) { const x = rr(520, 1170), tt = rr(2.6, 3.2); puff(tt, x, GROUND - 4, rr(-90, 90), -rr(30, 150), rr(10, 20), rr(40, 80), rr(0.6, 1.1), rr(0.06, 0.13)); if (j % 2) chip(tt, x, GROUND - 3, rr(-120, 120), -rr(200, 520), rr(3, 8)); }
  // 6. each body segment breaks ground
  topVis = 0;
  for (let i = 1; i < 5; i++) {
    let te = T_RISE0;
    while (te < T_RISE1 && CUT[i] + 10 + yOff(te, i) > GROUND) te += 0.004;
    const xs = i < 4 ? EDGE[i] : [88, 590, 1058, 1562];
    for (const ex of xs) {
      for (let j = 0; j < 7; j++) puff(te + rr(0, 0.35), ex + rr(-40, 40), GROUND - rr(0, 10), out(ex) * rr(20, 300) + rr(-60, 60), -rr(40, 300), rr(12, 24), rr(50, 120), rr(0.8, 1.6), rr(0.07, 0.16));
      for (let j = 0; j < 6; j++) chip(te + rr(0, 0.3), ex + rr(-30, 30), GROUND - 3, out(ex) * rr(0, 260) + rr(-80, 80), -rr(260, 800), rr(3, 11));
    }
  }
  for (let j = 0; j < 40; j++) {            // a steady trickle along the rim while it rises
    const tt = rr(T_RISE0 + 0.1, T_RISE1 - 0.5), x = rr(200, 1450);
    puff(tt, x, GROUND - 3, rr(-70, 70), -rr(30, 160), rr(8, 18), rr(34, 80), rr(0.6, 1.3), rr(0.05, 0.11));
    if (j % 3 === 0) chip(tt, x, GROUND - 3, rr(-110, 110), -rr(180, 460), rr(3, 7));
  }
  // 7. the vertebrae drop home, bottom to top
  for (let i = 3; i >= 0; i--) {
    const y = CUT[i + 1], n = i === 0 ? 7 : 3, big = i === 0 ? 1.6 : 1;
    for (const ex of EDGE[i]) {
      for (let j = 0; j < n; j++) puff(T_LOCK[i], ex + rr(-20, 20), y + rr(-6, 6), out(ex) * rr(60, 300) * big, -rr(0, 70), rr(8, 14), rr(28, 60) * big, rr(0.4, 0.75), rr(0.08, 0.16));
      for (let j = 0; j < n - 1; j++) chip(T_LOCK[i], ex + rr(-12, 12), y, out(ex) * rr(60, 340) * big, -rr(120, 420), rr(3, 7), rr(0.3, 0.5));
    }
  }

  // cracks in the ground
  const crack = (t0, x, y, ang, len, w, depth) => {
    const pts = [x, y]; let L = 0, a = ang;
    while (L < len) {
      const seg = rr(26, 74); a = ang + rr(-0.5, 0.5);
      x += Math.cos(a) * seg; y += Math.abs(Math.sin(a)) * seg * 0.6 + 1; L += seg; pts.push(x, y);
      if (depth < 2 && R() < 0.4) crack(t0 + 0.02 + 0.22 * L / len, x, y, ang + rr(-0.9, 0.9), (len - L) * rr(0.4, 0.8), w * 0.7, depth + 1);
    }
    cracks.push({ t0, pts, len: L, w, dur: 0.1 + L / 2600 });
  };
  for (const [x, dir] of [[88, -1], [480, 1], [1143, -1], [1562, 1], [300, -1], [1380, 1]]) crack(T_HIT, x + rr(-10, 10), GROUND, dir > 0 ? rr(0.12, 0.5) : Math.PI - rr(0.12, 0.5), rr(260, 520), 4, 0);
  for (const x of [600, 760, 900, 1040]) crack(T_LURCH, x + rr(-30, 30), GROUND, rr(0.5, 2.6), rr(160, 380), 3.4, 0);
  for (const [x, dir] of [[40, -1], [1610, 1]]) crack(T_PLUNGE + 0.05, x, GROUND, dir > 0 ? rr(0.05, 0.3) : Math.PI - rr(0.05, 0.3), rr(300, 600), 3.4, 0);
})();

/* ---------- drawing ---------- */
const cv = document.getElementById('stone-a');
/* The A's left outline, for the home hero intro (the name slides out from behind it).
   leftEdge[r] = the leftmost inked x in row r, as a share of the mark box; rows are N even bands top to bottom.
   Rows with no ink (the gaps between slabs) take the nearer neighbour, so nothing peeks through a gap. */
cv.stoneLeftEdge = (() => {
  const N = 207, c = document.createElement('canvas'); c.width = c.height = N;
  const g = c.getContext('2d', { willReadFrequently: true });
  g.scale(N / SIZE, N / SIZE); g.transform(0.1, 0, 0, -0.1, 0, SIZE); g.fill(MARK);
  const px = g.getImageData(0, 0, N, N).data, edge = new Array(N).fill(null);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) if (px[(y * N + x) * 4 + 3] > 127) { edge[y] = x / N; break; }
  for (let y = 0; y < N; y++) if (edge[y] === null) {
    for (let d = 1; d < 8; d++) {
      const a = edge[y - d], b = edge[y + d];
      if (a != null || b != null) { edge[y] = Math.min(a ?? 1, b ?? 1); break; }
    }
  }
  // a slab gap holds thin crack lines, which would count as the edge there: take each row's leftmost
  // over its neighbours too (about 3% of the height), so no gap or crack opens a window into the text
  return edge.map((_, y) => {
    let m = null;
    for (let d = -6; d <= 6; d++) { const v = edge[y + d]; if (v != null) m = m === null ? v : Math.min(m, v); }
    return edge[y] === null ? null : m;
  });
})();
if (!cv) return;
const ctx = cv.getContext('2d');
const sprite = document.createElement('canvas'); sprite.width = sprite.height = 128;
function readTheme() {                                   // the mark is the page's ink; the rock is the page itself
  FG = getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() || FG;
  const g = sprite.getContext('2d'); g.clearRect(0, 0, 128, 128);
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, FG); gr.addColorStop(1, 'transparent');
  g.globalAlpha = 1; g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  rockScale = 0;
}

function drawPuffs(t) {
  for (const p of puffs) {
    const u = t - p.t0;
    if (u <= 0 || u >= p.life) continue;
    const q = (1 - Math.exp(-p.k * u)) / p.k, f = u / p.life;
    const x = p.x + p.vx * q, y = p.y + p.vy * q - 14 * u;
    const r = p.r0 + (p.r1 - p.r0) * (1 - Math.exp(-3.2 * f));
    ctx.globalAlpha = p.a * Math.min(1, u / 0.04) * Math.pow(1 - f, 1.4);
    ctx.drawImage(sprite, x - r, y - r, 2 * r, 2 * r);
  }
  ctx.globalAlpha = 1;
}
function drawChips(t) {
  for (const c of chips) {
    const u = t - c.t0;
    if (u <= 0 || u >= c.life) continue;
    const x = c.x + c.vx * u, y = c.y + c.vy * u + 1500 * u * u;
    if (y > GROUND - 1) continue;                    // fell back into the ground
    const k = Math.min(1, (1 - u / c.life) * 4);     // shrink away at end of life
    const a = c.rot + c.w * u, co = Math.cos(a) * k, si = Math.sin(a) * k, v = c.v;
    ctx.beginPath();
    for (let j = 0; j < v.length; j += 2) { const px = x + v[j] * co - v[j + 1] * si, py = y + v[j] * si + v[j + 1] * co; j ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
    ctx.closePath(); ctx.fillStyle = FG; ctx.fill();
  }
}
function drawGround(t) {
  const a = smooth((t - 0.05) / 0.4) * (1 - smooth((t - 8.4) / 0.6));
  if (a <= 0) return;
  ctx.lineCap = 'butt'; ctx.lineJoin = 'miter';
  ctx.strokeStyle = FG; ctx.globalAlpha = 0.2 * a; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(-6000, GROUND + 1.5); ctx.lineTo(6000 + SIZE, GROUND + 1.5); ctx.stroke();
  ctx.globalAlpha = 0.5 * a;
  for (const c of cracks) {
    const u = t - c.t0;
    if (u <= 0) continue;
    let left = c.len * (1 - Math.pow(1 - clamp(u / c.dur, 0, 1), 2));
    const p = c.pts;
    ctx.lineWidth = c.w; ctx.beginPath(); ctx.moveTo(p[0], p[1]);
    for (let j = 2; j < p.length && left > 0; j += 2) {
      const dx = p[j] - p[j - 2], dy = p[j + 1] - p[j - 1], d = Math.hypot(dx, dy), k = Math.min(1, left / d);
      ctx.lineTo(p[j - 2] + dx * k, p[j - 1] + dy * k); left -= d;
    }
    ctx.stroke();
  }
  ctx.globalAlpha = 1;
}
function fillMark() { ctx.save(); ctx.transform(0.1, 0, 0, -0.1, 0, SIZE); ctx.fillStyle = FG; ctx.fill(MARK); ctx.restore(); }
function drawStone(t) {
  if (t >= T_BUILT) { for (let i = 0; i < 4; i++) drawRock(i, t); fillMark(); return; }   // locked: the untouched mark, one fill, no seams
  ctx.save();
  if (t >= T_HIT) { ctx.beginPath(); ctx.rect(-9000, -9000, 18000 + SIZE, 9000 + GROUND); ctx.clip(); }
  for (let i = 4; i >= 0; i--) {
    const [dx, dy, rot] = pose(t, i);
    if (CUT[i] + dy > GROUND + 80) continue;          // wholly underground
    ctx.save();
    ctx.translate(CEN[i][0] + dx, CEN[i][1] + dy); ctx.rotate(rot); ctx.translate(-CEN[i][0], -CEN[i][1]);
    ctx.beginPath(); ctx.rect(-200, CUT[i], SIZE + 400, CUT[i + 1] - CUT[i]); ctx.clip();
    drawRock(i, t);
    fillMark();
    ctx.restore();
  }
  ctx.restore();
}

/* ---------- the rock: the black torn shapes inside the slabs ----------
   Drawn UNDER the white mark, so the mark's own edges cut it: shapes stay exactly the logo's. ?plain=1 turns it off.
   Each rock is painted once into its own little canvas; where a torn shape opens into a gap the texture fades out. */
const PLAIN = false;
const ROCK = [
  { poly: [690, 244, 1036, 244, 1036, 436, 690, 436], slope: 0.0, fades: [['lin', 404, 434]] },
  { poly: [796, 524, 1266, 524, 1266, 676, 850, 676, 796, 640], slope: -0.02, fades: [['rad', 806, 668, 24, 110]] },
  { poly: [766, 784, 1350, 784, 1350, 952, 766, 952], slope: -0.16, fades: [['rad', 796, 962, 18, 80], ['rad', 758, 914, 10, 46]] },
  { poly: [690, 1116, 1426, 1116, 1426, 1209, 850, 1209, 690, 1214], slope: -0.13, fades: [['rad', 770, 1216, 60, 190]] },
];

(function buildRock() {
  const R = rng(4107), rr = (a, b) => a + (b - a) * R();
  for (const k of ROCK) {
    const p = k.poly; let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    for (let j = 0; j < p.length; j += 2) { x0 = Math.min(x0, p[j]); x1 = Math.max(x1, p[j]); y0 = Math.min(y0, p[j + 1]); y1 = Math.max(y1, p[j + 1]); }
    k.box = [x0, y0, x1 - x0, y1 - y0];
    const xm = (x0 + x1) / 2, area = (x1 - x0) * (y1 - y0), lift = Math.abs(k.slope) * (x1 - x0) / 2;
    k.strata = []; k.facets = []; k.ticks = []; k.specks = [];
    for (let y = y0 - lift + 8; y < y1 + lift; y += rr(9, 17)) {           // strata: broken bedding lines running with the ridge
      const w = rr(1.2, 3.2), a = rr(0.04, 0.09);
      let x = x0 - 10, py = y + k.slope * (x - xm) + rr(-2, 2);
      while (x < x1) {
        const nx = x + rr(36, 96), ny = y + k.slope * (nx - xm) + rr(-2.6, 2.6);
        if (R() < 0.7) k.strata.push([x, py, nx, ny, w, a]);
        x = nx; py = ny;
      }
    }
    for (let n = Math.round(area / 16000) + 2; n > 0; n--) {                // facets: flat chiselled planes, a shade lighter
      const cx = rr(x0, x1), cy = rr(y0, y1), w = rr(70, 230), h = rr(14, 44), sh = rr(-26, 26);
      const f = (dx, dy) => [cx + dx, cy + dy + k.slope * dx];
      k.facets.push([...f(-w / 2 + sh, -h / 2), ...f(w / 2 + sh * 0.4, -h / 2 + rr(-5, 5)), ...f(w / 2 - sh, h / 2), ...f(-w / 2 - sh * 0.5, h / 2 + rr(-5, 5)), rr(0.018, 0.04)]);
    }
    for (let n = Math.round(area / 3000); n > 0; n--) {                     // chisel ticks, on the mark's own crack diagonal
      const x = rr(x0, x1), y = rr(y0, y1), an = 1.13 + rr(-0.16, 0.16), l = rr(9, 32);
      k.ticks.push([x, y, x + Math.cos(an) * l, y + Math.sin(an) * l, rr(1.3, 2.4), rr(0.06, 0.105)]);
    }
    for (let n = Math.round(area / 1000); n > 0; n--) k.specks.push([rr(x0, x1), rr(y0, y1), rr(1.6, 3.6), rr(0.06, 0.14)]);   // grain
  }
})();
let rockScale = 0;
function paintRocks(s) {                                   // (re)paint the rock canvases at the current device scale
  rockScale = s;
  for (const k of ROCK) {
    const [bx, by, bw, bh] = k.box, c = k.cv || (k.cv = document.createElement('canvas')), p = k.poly;
    c.width = Math.max(1, Math.ceil(bw * s)); c.height = Math.max(1, Math.ceil(bh * s));
    const g = c.getContext('2d');
    g.setTransform(s, 0, 0, s, -bx * s, -by * s);
    g.save();
    g.beginPath(); g.moveTo(p[0], p[1]); for (let j = 2; j < p.length; j += 2) g.lineTo(p[j], p[j + 1]); g.closePath(); g.clip();
    g.fillStyle = g.strokeStyle = FG; g.lineCap = 'butt';
    for (const f of k.facets) { g.globalAlpha = f[8]; g.beginPath(); g.moveTo(f[0], f[1]); g.lineTo(f[2], f[3]); g.lineTo(f[4], f[5]); g.lineTo(f[6], f[7]); g.closePath(); g.fill(); }
    for (const q of k.strata) { g.globalAlpha = q[5]; g.lineWidth = q[4]; g.beginPath(); g.moveTo(q[0], q[1]); g.lineTo(q[2], q[3]); g.stroke(); }
    for (const q of k.ticks) { g.globalAlpha = q[5]; g.lineWidth = q[4]; g.beginPath(); g.moveTo(q[0], q[1]); g.lineTo(q[2], q[3]); g.stroke(); }
    for (const q of k.specks) { g.globalAlpha = q[3]; g.fillRect(q[0], q[1], q[2], q[2]); }
    g.transform(0.1, 0, 0, -0.1, 0, SIZE); g.lineJoin = 'round';          // faint rim where rock meets white: light catching the ridgeline
    g.globalAlpha = 0.035; g.lineWidth = 200; g.stroke(MARK);
    g.globalAlpha = 0.14; g.lineWidth = 60; g.stroke(MARK);
    g.restore();
    g.globalAlpha = 1; g.globalCompositeOperation = 'destination-in';       // fade out where the torn shape runs into a gap: no cut line
    for (const f of k.fades) {
      const gr = f[0] === 'lin' ? g.createLinearGradient(0, f[1], 0, f[2]) : g.createRadialGradient(f[1], f[2], f[3], f[1], f[2], f[4]);
      gr.addColorStop(0, f[0] === 'lin' ? '#000' : 'rgba(0,0,0,0)'); gr.addColorStop(1, f[0] === 'lin' ? 'rgba(0,0,0,0)' : '#000');
      g.fillStyle = gr; g.fillRect(bx - 2, by - 2, bw + 4, bh + 4);
    }
    g.globalCompositeOperation = 'source-over';
  }
}
function drawRock(i) {
  const k = ROCK[i]; if (!k || PLAIN || !k.cv) return;
  ctx.drawImage(k.cv, k.box[0], k.box[1], k.cv.width / rockScale, k.cv.height / rockScale);
}

/* ---------- frame ---------- */
const WARP = [[0, 0.25], [0.90, 1.15], [1.85, 2.22], [2.30, 3.10], [4.85, 7.70], [5.35, 8.28]];
function warp(r) {
  const L = WARP[WARP.length - 1];
  if (r >= L[0]) return r - L[0] + L[1];
  for (let i = 1; i < WARP.length; i++) if (r < WARP[i][0]) { const a = WARP[i - 1], b = WARP[i]; return a[1] + (b[1] - a[1]) * (r - a[0]) / (b[0] - a[0]); }
}
const END = 9.1 - (WARP[WARP.length - 1][1] - WARP[WARP.length - 1][0]);   // dust settled, ground line gone: the mark alone
function renderAt(seconds) {
  const t = warp(Math.max(0, +seconds || 0));
  frame(t);
}
function frame(t) {
  const W = cv.width, H = cv.height;
  // the canvas is 180% of the mark's box (.hero-mark in index.html) so the dust has room
  let s = Math.min(W, H) / (SIZE * 1.8), ox = (W - SIZE * s) / 2, oy = (H - SIZE * s) / 2;
  topVis = oy / s;
  if (!PLAIN && rockScale !== s) paintRocks(s);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1; ctx.clearRect(0, 0, W, H);
  const [sx, sy] = shake(t);
  ctx.setTransform(s, 0, 0, s, ox + sx * s, oy + sy * s);
  drawPuffs(t);
  drawStone(t);
  drawGround(t);
  drawChips(t);
}
window.renderAt = renderAt;

const SPEED = 0.8;                                   // playback rate: 0.8 = the whole build 25% slower (~7.7 s)
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
let t0 = null, lastT = REDUCED ? END : 0, raf = 0;
let locked = false;                                  // 'stone:locked' fires once, when the A first locks (the home hero slides then)
function fit() {
  const r = cv.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
  const w = Math.max(1, Math.round(r.width * dpr)), h = Math.max(1, Math.round(r.height * dpr));
  if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; rockScale = 0; }
  renderAt(lastT);
}
function tick(now) {
  if (t0 === null) t0 = now;
  lastT = Math.min(END, (now - t0) / 1000 * SPEED);
  renderAt(lastT);
  if (!locked && warp(lastT) >= T_BUILT) { locked = true; cv.dispatchEvent(new Event('stone:locked', { bubbles: true })); }
  raf = lastT < END ? requestAnimationFrame(tick) : 0;
}
const FREEZE = new URLSearchParams(location.search).get('stone');   // ?stone=2.5 holds that moment (for checking frames)
if (FREEZE !== null) lastT = clamp(parseFloat(FREEZE) || 0, 0, END);
function play() { if (REDUCED || FREEZE !== null) return; cancelAnimationFrame(raf); t0 = null; raf = requestAnimationFrame(tick); }
readTheme();
new ResizeObserver(fit).observe(cv);
new MutationObserver(() => { readTheme(); renderAt(lastT); }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { readTheme(); renderAt(lastT); });
cv.parentElement.addEventListener('click', play);       // a click on the mark plays it again
fit();
play();
})();
