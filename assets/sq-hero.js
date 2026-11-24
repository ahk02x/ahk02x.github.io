/* SQ -> the mark (astra, approved 11-19). Without script the locked mark above is what shows.
   window.sqHero.renderAt(seconds) draws one frame; ?t=SECONDS freezes on it. Click or tap replays. */
(() => {
  'use strict';
  const art = document.getElementById('sq-anim');
  if (!art || !art.getBBox) return;
  const locked = art.querySelector('.sqa-locked');
  const moving = art.querySelector('.sqa-moving');
  const word = art.querySelector('.sqa-word');
  const [wordS, wordQ] = word.children;
  for (const part of locked.children) moving.append(part.cloneNode(true));
  // The moving copies are coloured per frame, so only the ticks that never change colour keep a class.
  for (const part of moving.children) if (!part.classList.contains('lk-ring') || part.tagName !== 'line') part.removeAttribute('class');
  const ring = moving.firstElementChild;
  const ticks = [...moving.querySelectorAll('line')];
  const letter = moving.lastElementChild;
  const needle = letter.previousElementSibling;
  const ringD = ring.getAttribute('d');
  const needleD = needle.getAttribute('d');
  const svgElement = tag => document.createElementNS(art.namespaceURI, tag);
  const disc = svgElement('circle');
  disc.setAttribute('r', 70);
  disc.setAttribute('fill', 'url(#sqa-cut)');
  moving.insertBefore(disc, ring);
  const glow = svgElement('path');
  for (const [k,v] of [['class','sqa-glow'],['fill','none'],['stroke-width',12],['stroke-linejoin','round'],['filter','url(#sqa-soft)']])
    glow.setAttribute(k, v);
  moving.insertBefore(glow, needle);
  const caps = [svgElement('ellipse'), svgElement('ellipse')];
  moving.append(...caps);
  letter.removeAttribute('transform');
  letter.setAttribute('stroke-linecap', 'butt');

  const clamp = x => Math.min(1, Math.max(0, x));
  const phase = (t, a, b) => clamp((t-a)/(b-a));
  const ease = x => x*x*x*(10+x*(-15+6*x));
  const mix = (a,b,p) => a + (b-a)*p;
  const blend = (a,b,p) => a.map((v,i) => mix(v,b[i],p));
  const rgb = (a,b,p) => 'rgb(' + blend(a,b,p).map(Math.round).join(' ') + ')';
  const radians = Math.PI / 180;

  // The inks are the theme's: the page ink for the letters, the mark's graphite and red (style.css --sq-*).
  let white, graphite, red, hot;
  function readInks() {
    const ink = token => {
      art.style.color = 'var(' + token + ')';
      const v = getComputedStyle(art).color.match(/[\d.]+/g).slice(0, 3).map(Number);
      art.style.color = '';
      return v;
    };
    white = ink('--ink'); graphite = ink('--sq-ring'); red = ink('--sq-red'); hot = ink('--sq-hot');
  }
  readInks();

  function halve(a,b,c,d) {
    const ab = blend(a,b,.5), bc = blend(b,c,.5), cd = blend(c,d,.5);
    const left = blend(ab,bc,.5), right = blend(bc,cd,.5);
    return [...ab,...left,...blend(left,right,.5),...right,...cd,...d];
  }
  /* ---------- the opening wordmark is real type; the geometry is fitted to it ---------- */
  var WORD_FONT = '"Helvetica Neue", Helvetica, Inter, "SF Pro Display", Arial, sans-serif';
  var WORD_WEIGHT = 500, WORD_SIZE = 140, WORD_TRACK = -0.012;   // size in logo units (256 box)
  function measureWordmark() {
    var P = 400, k = WORD_SIZE / P, OX = 100, OY = 520;
    var c = document.createElement('canvas'); c.width = 1400; c.height = 760;
    var g = c.getContext('2d', { willReadFrequently: true });
    g.font = WORD_WEIGHT + ' ' + P + 'px ' + WORD_FONT;
    g.textBaseline = 'alphabetic'; g.fillStyle = 'white';
    function box(ch) {
      var m = g.measureText(ch);
      return { adv: m.width * k, l: -m.actualBoundingBoxLeft * k, r: m.actualBoundingBoxRight * k,
               t: -m.actualBoundingBoxAscent * k, b: m.actualBoundingBoxDescent * k };
    }
    function runs(ch, horizontal, at) {
      g.clearRect(0, 0, c.width, c.height); g.fillText(ch, OX, OY);
      var px = Math.round(at / k), d, n, out = [], len = 0, i;
      if (horizontal) { d = g.getImageData(0, OY + px, c.width, 1).data; n = c.width; }
      else { d = g.getImageData(OX + px, 0, 1, c.height).data; n = c.height; }
      for (i = 0; i < n; i++) {
        if (d[i * 4 + 3] >= 128) len++;
        else if (len) { out.push(len * k); len = 0; }
      }
      if (len) out.push(len * k);
      return out;
    }
    function mean(a) { var s = 0; a.forEach(function (v) { s += v; }); return a.length ? s / a.length : 0; }
    var S = box('S'), Q = box('Q'), O = box('O');
    if (!(S.r - S.l > 10 && O.b - O.t > 10)) {     // no canvas metrics: Helvetica Neue Medium, measured
      S = { adv: 90.72, l: 4.62, r: 86.1, t: -102.34, b: 2.38 };
      Q = { adv: 106.4, l: 5.32, r: 101.08, t: -102.34, b: 9.1 };
      O = { adv: 106.4, l: 5.32, r: 101.08, t: -102.34, b: 2.38 };
    }
    var sw = mean(runs('S', false, (S.l + S.r) / 2));
    var ow = mean(runs('O', true, (O.t + O.b) / 2).concat(runs('O', false, (O.l + O.r) / 2)));
    if (!(sw > 4 && sw < 40)) sw = 15.05;
    if (!(ow > 4 && ow < 40)) ow = 15.93;
    var track = WORD_TRACK * WORD_SIZE;
    var Y = 128 - (O.t + O.b) / 2;
    var right = Math.max(Q.r, O.r);
    var xS = 128 - (S.l + S.adv + track + right) / 2;
    var xQ = xS + S.adv + track;
    return {
      Y: Y, xS: xS, xQ: xQ,
      s: { x0: xS + S.l, x1: xS + S.r, y0: Y + S.t, y1: Y + S.b, w: sw },
      bowl: { cx: xQ + (O.l + O.r) / 2, cy: Y + (O.t + O.b) / 2,
              rx: (O.r - O.l - ow) / 2, ry: (O.b - O.t - ow) / 2, w: ow },
      q: { x1: xQ + Q.r, y1: Y + Q.b }
    };
  }
  const WM = measureWordmark();
  for (const [k,v] of [['font-family',WORD_FONT],['font-weight',WORD_WEIGHT],['font-size',WORD_SIZE]]) word.setAttribute(k,v);
  wordS.setAttribute('x',WM.xS);
  wordQ.setAttribute('x',WM.xQ);
  word.setAttribute('y',WM.Y);
  word.removeAttribute('display');
  const S_FIT = [0.8717,0.3049,0.8688,0.1324,0.6854,0.0763,0.4928,0.0692,0.1968,0.0836,0.1439,0.1962,0.1389,0.2836,
    0.1355,0.4269,0.327,0.4526,0.5446,0.4942,0.8449,0.5255,0.8773,0.5916,0.9076,0.6778,0.9109,0.8099,0.8419,0.8436,
    0.7787,0.8785,0.7243,0.9112,0.5824,0.9281,0.581,0.9281,0.2056,0.942,0.0954,0.8038,0.0942,0.6588];
  const sStart = S_FIT.map((v,i) => i%2 ? WM.s.y0+v*(WM.s.y1-WM.s.y0) : WM.s.x0+v*(WM.s.x1-WM.s.x0));
  const B = WM.bowl, Rx = B.rx+B.w/2, Ry = B.ry+B.w/2;
  const tailAt = (u,v) => [B.cx+u*Rx, B.cy+v*Ry];
  const tailStart = [...tailAt(-.0857,.4261), ...tailAt(.6879,1.0425), 0,0,
    ...tailAt(1.0935,1.0425), ...tailAt(.2978,.4081), 0,0];
  const sEnd = [154,96,
    ...halve([154,96],[146,87],[112,84],[103,95]),
    94,106,100,118,114,124,
    130,131,150,134,154,148,
    ...halve([154,148],[157,163],[143,172],[126,171]),
    113,170,104,164,101,156].map(v => v-3);

  function drawLetter(t,p,pull) {
    const pts = blend(sStart,sEnd,p);
    for (let i=0; i<pts.length; i+=2) pts[i] -= pull;
    let d = 'M ' + pts.slice(0,2).join(' ');
    for (let i=2; i<pts.length; i+=6) d += ' C ' + pts.slice(i,i+6).join(' ');
    letter.setAttribute('d',d);
    const ink = rgb(white,red,ease(phase(t,1.12,1.96)));
    const weight = mix(WM.s.w,13,p);
    letter.setAttribute('stroke',ink);
    letter.setAttribute('stroke-width',weight);
    for (const [i,cap] of caps.entries()) {
      const k = i ? pts.length-2 : 0, j = i ? k-2 : k+2;
      const angle = Math.atan2(pts[j+1]-pts[k+1],pts[j]-pts[k])/radians;
      cap.setAttribute('transform','translate('+pts[k]+' '+pts[k+1]+') rotate('+angle+')');
      cap.setAttribute('rx',p*weight/2);
      cap.setAttribute('ry',weight/2);
      cap.setAttribute('fill',ink);
    }
  }

  function drawRing(p,gap) {
    const cx = mix(B.cx,128,p), cy = mix(B.cy,128,p);
    const rx = mix(B.rx,92,p), ry = mix(B.ry,92,p);
    const at = a => [cx+rx*Math.cos(a*radians),cy+ry*Math.sin(a*radians)].join(' ');
    const arc = ' A '+rx+' '+ry+' 0 0 1 ';
    ring.setAttribute('d',gap===1 ? ringD :
      'M '+at(45+13*gap)+arc+at(225)+arc+at(405-13*gap)+(gap===0?' Z':''));
    ring.setAttribute('stroke',rgb(white,graphite,p));
    ring.setAttribute('stroke-width',mix(B.w,9,p));
  }

  const departures = [2.10,2.195,2.325,2.425,2.57,2.68,2.815,2.915,3.025];
  const kicks = [9,6,8,5,9,7,5.5,8,4.5];
  function limiter(t) {
    let angle = -23*ease(phase(t,1.96,2.052))*(1-ease(phase(t,2.052,2.10)));
    for (let i=0; i<departures.length; i++) {
      const age = t-departures[i];
      const duration = i+1<departures.length ? departures[i+1]-departures[i] : .095;
      if (age<0 || age>=duration) continue;
      const u = age/duration;
      angle -= kicks[i]*ease(phase(u,.03,.53))*(1-ease(phase(u,.53,1)));
      break;
    }
    return angle;
  }
  const hits = departures.map((t,i) => ({t,k:i ? .45+.55*kicks[i-1]/9 : 1}));
  hits.push({t:departures[departures.length-1]+.095, k:.45+.55*kicks[kicks.length-1]/9});
  function glowAt(t) {
    let v = 0;
    for (const h of hits) {
      const dt = t-h.t;
      if (dt<0) break;
      if (dt<.15) v = Math.max(v,h.k*(1-dt/.15)**2);
    }
    const dl = t-settled;
    if (dl>=0 && dl<.5) v = Math.max(v,.55*(1-dl/.5)**2);
    return v;
  }

  const sweepStart=3.43, far=4.49, returning=4.65, arrival=5.63, settled=5.83, END=6.35;
  const handIn=.56, handMid=.66, handOut=.78;
  function sweep(t) {
    if (t<far) return -273*ease(phase(t,sweepStart,far));
    if (t<returning) return -273+3*ease(phase(t,far,returning));
    if (t<arrival) return -270+272.5*ease(phase(t,returning,arrival));
    return 2.5*(1-ease(phase(t,arrival,settled)));
  }
  function crossing(fraction,start,end) {
    let lo=0, hi=1;
    for (let i=0;i<24;i++) {
      const mid=(lo+hi)/2;
      if (ease(mid)<fraction) lo=mid;
      else hi=mid;
    }
    return mix(start,end,(lo+hi)/2);
  }
  const events = ticks.map((line,i) => {
    const x=Number(line.getAttribute('x1')), y=Number(line.getAttribute('y1'));
    const bearing = 135+i*15;
    const travel = 405-bearing;
    return {line,x,y,innerX:Number(line.getAttribute('x2')),innerY:Number(line.getAttribute('y2')),
      drawn:crossing(travel/273,sweepStart,far),
      lit:crossing((270-travel)/272.5,returning,arrival)};
  });
  function drawTicks(t) {
    for (const [i,e] of events.entries()) {
      const p=ease(phase(t,e.drawn,e.drawn+.076));
      e.line.style.opacity=p;
      if (!p) continue;
      e.line.setAttribute('x2',mix(e.x,e.innerX,p));
      e.line.setAttribute('y2',mix(e.y,e.innerY,p));
      if (i>=14) e.line.setAttribute('stroke',rgb(graphite,red,ease(phase(t,e.lit,e.lit+.075))));
    }
  }

  let now = END;
  function draw(t) {
    now = t;
    const done=t>=END;
    locked.style.display=done?'':'none';
    moving.style.display=done?'none':'';
    const typeOn=done?0:1-ease(phase(t,handMid,handOut));
    word.style.display=typeOn>0?'':'none';
    word.setAttribute('opacity',typeOn);
    moving.setAttribute('opacity',ease(phase(t,handIn,handMid)));
    if (done) return;
    const p=ease(phase(t,.91,1.99));
    const pull=2.8*ease(phase(t,.78,.94))*(1-ease(phase(t,.94,1.27)));
    drawRing(p,ease(phase(t,3.11,3.42)));
    drawLetter(t,p,pull);
    const angle=limiter(t);
    const a=blend(tailStart,
      [165.83,175.02,211.09,216.03,3.5,3.5,216.03,211.09,175.02,165.83,6.5,6.5],p);
    const d=p===1?needleD:
      'M '+a[0]+' '+a[1]+' L '+a[2]+' '+a[3]+' A '+a[4]+' '+a[5]+' 0 0 0 '+a[6]+' '+a[7]+
      ' L '+a[8]+' '+a[9]+' A '+a[10]+' '+a[11]+' 0 0 0 '+a[0]+' '+a[1]+' Z';
    const sweepAngle=sweep(t);
    const rotation='rotate('+(angle+sweepAngle)+' 128 128)';
    const travel=ease(clamp(-sweepAngle/19));
    const retract=travel ? ' translate(170.425 170.425) rotate(45) scale('+
      mix(1,.44,travel)+' 1) rotate(-45) translate(-170.425 -170.425)' : '';
    needle.setAttribute('d',d);
    needle.setAttribute('transform',rotation+retract);
    const tailInk=blend(white,red,ease(phase(t,1.67,2.10)));
    const lit=glowAt(t);
    needle.setAttribute('fill',rgb(tailInk,hot,lit*.75));
    glow.style.display=disc.style.display=lit>.002?'':'none';
    if (lit>.002) {
      glow.setAttribute('d',d);
      glow.setAttribute('transform',rotation+retract);
      glow.setAttribute('opacity',.7*lit);
      const turn=(angle+sweepAngle)*radians;
      const mx=(a[0]+a[2]+a[6]+a[8])/4-128, my=(a[1]+a[3]+a[7]+a[9])/4-128;
      disc.setAttribute('cx',128+mx*Math.cos(turn)-my*Math.sin(turn));
      disc.setAttribute('cy',128+mx*Math.sin(turn)+my*Math.cos(turn));
      disc.setAttribute('opacity',.85*lit);
    }
    drawTicks(t);
  }

  let request=0;
  const renderAt = seconds => {
    cancelAnimationFrame(request);
    draw(Math.max(0,Number(seconds)||0));
  };
  // The clock starts on the first painted frame, so a page opened in a background tab still plays when it is seen.
  function play() {
    cancelAnimationFrame(request);
    let start=null;
    draw(0);
    function frame(stamp) {
      if (start===null) start=stamp;
      const t=(stamp-start)/1000;
      draw(t);
      if (t<END) request=requestAnimationFrame(frame);
    }
    request=requestAnimationFrame(frame);
  }
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  art.addEventListener('click', () => { if (!still.matches) play(); });
  // A theme switch mid-play repaints the frame in the new inks; the locked mark follows the tokens by itself.
  const repaint = () => { readInks(); if (now<END) draw(now); };
  new MutationObserver(repaint).observe(document.documentElement, {attributes:true, attributeFilter:['data-theme']});
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', repaint);
  window.sqHero = {renderAt, play, END};
  const frozen = new URLSearchParams(location.search).get('t');
  if (frozen!==null) renderAt(frozen);
  else if (still.matches) renderAt(END);
  else play();
})();
