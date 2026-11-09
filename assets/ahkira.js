// ahkira character generator: one gold sun, one crescent moon used as a hand.
const AK = {
  ink:'#14162E', sun:'#F0A93B', shade:'#DD8F26',
  moon:{dark:['#A9BEDF','#E1E9F6'], light:['#7F98C9','#B4C6E6'], alert:['#C2402F','#E8806B']},
  cx:100, cy:104, r:50,
};
// pose: where the moon sits (deg, 0 = right, -90 = up), how far it stands off the body, and the face
const POSES = {
  idle:  {a:-150, span:46, gap:9,  w:25, eyes:'open'},
  hello: {a:-25,  span:42, gap:13, w:25, eyes:'open',  mouth:true},
  think: {a:-150, span:46, gap:9,  w:25, eyes:'up'},
  done:  {a:90,   span:58, gap:7,  w:24, eyes:'happy', dy:-2},
  alert: {a:-42,  span:40, gap:18, w:26, eyes:'wide', alert:true},
  sleep: {a:-132, span:54, gap:4,  w:21, eyes:'shut', zz:true},
};
let akUid = 0;

function akCrescent(rIn, w, span, a, frac){
  // inner edge hugs the body; outer edge swells to w at the middle and tapers to sharp tips
  const N = 40, pts = [], cx = AK.cx, cy = AK.cy, rad = d => d*Math.PI/180;
  for(let i=0;i<=N;i++){ const t=-1+2*i/N, ang=rad(a+t*span); pts.push([cx+rIn*Math.cos(ang), cy+rIn*Math.sin(ang)]); }
  for(let i=N;i>=0;i--){ const t=-1+2*i/N, ang=rad(a+t*span), rr=rIn+w*frac*Math.pow(1-t*t,0.72);
    pts.push([cx+rr*Math.cos(ang), cy+rr*Math.sin(ang)]); }
  return 'M'+pts.map(p=>p[0].toFixed(2)+' '+p[1].toFixed(2)).join('L')+'Z';
}

function akEyes(kind, ink){
  const L=84, R=116, Y=112;
  const cap=(x,y,w,h)=>`<rect x="${x-w/2}" y="${y-h/2}" width="${w}" height="${h}" rx="${w/2}" fill="${ink}"/>`;
  const glint=(x,y)=>`<circle cx="${x}" cy="${y}" r="2.4" fill="#fff"/>`;
  if(kind==='happy') return `<path d="M${L-7} ${Y+2}q7-10 14 0M${R-7} ${Y+2}q7-10 14 0" fill="none" stroke="${ink}" stroke-width="4.2" stroke-linecap="round"/>`;
  if(kind==='shut')  return `<path d="M${L-7} ${Y}q7 6 14 0M${R-7} ${Y}q7 6 14 0" fill="none" stroke="${ink}" stroke-width="3.6" stroke-linecap="round"/>`;
  if(kind==='up')    return cap(L+3,Y-6,11,19)+cap(R+3,Y-6,11,19)+glint(L+5,Y-11)+glint(R+5,Y-11);
  if(kind==='wide')  return cap(L,Y-1,13,23)+cap(R,Y-1,13,23)+glint(L+2,Y-7)+glint(R+2,Y-7);
  return `<g class="ak-blink">${cap(L,Y,11,19)+cap(R,Y,11,19)+glint(L+2,Y-5)+glint(R+2,Y-5)}</g>`;
}

function ahkira({pose='idle', anim=true, onLight=false, mono=null, shadow=true, tuft=true}={}){
  const p = POSES[pose], id = 'ak'+(akUid++);
  const [moonC, litC] = mono ? [mono,mono] : p.alert ? AK.moon.alert : onLight ? AK.moon.light : AK.moon.dark;
  const sun = mono||AK.sun, shade = mono||AK.shade, ink = mono ? (onLight?'#F4F2EC':'#14162E') : AK.ink;
  const rIn = AK.r + p.gap;
  const moon = `<path d="${akCrescent(rIn,p.w,p.span,p.a,1)}" fill="${moonC}"/>`+
               (mono?'':`<path d="${akCrescent(rIn,p.w,p.span*0.92,p.a,0.3)}" fill="${litC}"/>`);
  const moonCls = !anim?'':{idle:'ak-sway',hello:'ak-wave',think:'ak-orbit',alert:'ak-raise',sleep:'',done:''}[pose];
  const bodyCls = !anim?'':{idle:'ak-bob',hello:'ak-bob',think:'',done:'ak-nestle',alert:'ak-hop',sleep:'ak-breathe'}[pose];
  const dy = p.dy||0;
  const mouth = p.mouth ? `<path d="M95 126q5 5 10 0" fill="none" stroke="${ink}" stroke-width="3.4" stroke-linecap="round"/>` : '';
  const zz = p.zz ? `<g class="${anim?'ak-zz':''}" fill="${moonC}" font-family="'M PLUS Rounded 1c',ui-rounded,system-ui,sans-serif" font-weight="800"><text x="150" y="44" font-size="20">z</text><text x="166" y="26" font-size="14">z</text></g>` : '';
  return `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ahkira, ${pose}">
  <defs><clipPath id="${id}"><circle cx="${AK.cx}" cy="${AK.cy}" r="${AK.r}"/></clipPath></defs>
  ${shadow?`<ellipse class="${anim&&bodyCls==='ak-hop'?'ak-shadow':''}" cx="100" cy="182" rx="40" ry="5" fill="#000" opacity="${onLight?.12:.3}"/>`:''}
  <g class="${bodyCls}" transform="translate(0 ${dy})">
    ${tuft?`<path d="M111 60 C112 46 120 38 131 36 C126 44 126 52 129 62Z" fill="${sun}"/>`:''}
    <g class="${moonCls}">${moon}</g>
    <circle cx="${AK.cx}" cy="${AK.cy}" r="${AK.r}" fill="${sun}"/>
    ${mono?'':`<path clip-path="url(#${id})" fill-rule="evenodd" fill="${shade}" d="M40 44h120v120H40zM${AK.cx-8} ${AK.cy-9}m-${AK.r} 0a${AK.r} ${AK.r} 0 1 0 ${AK.r*2} 0a${AK.r} ${AK.r} 0 1 0 -${AK.r*2} 0z"/>`}
    ${akEyes(p.eyes, ink)}${mouth}
  </g>${zz}</svg>`;
}

// 16x16 sprite: hand-set 10px body, 1px shade on the lower-right rim, moon sampled from the vector pose
const PX_BODY=[4,8,8,10,10,10,10,8,8,4];
const PX_EYES={open:[[5,9],[5,10],[10,9],[10,10]], up:[[6,8],[6,9],[11,8],[11,9]], wide:[[5,8],[5,9],[5,10],[10,8],[10,9],[10,10]],
  happy:[[4,10],[5,9],[6,10],[9,10],[10,9],[11,10]], shut:[[4,10],[5,10],[6,10],[9,10],[10,10],[11,10]]};
function akPixel(pose='idle', {onLight=false, cls=''}={}){
  const p=POSES[pose], cx=8, cy=9, map=new Map(), key=(x,y)=>x+','+y;
  const [moonC,litC]=p.alert?AK.moon.alert:onLight?AK.moon.light:AK.moon.dark;
  PX_BODY.forEach((w,r)=>{ const x0=8-w/2; for(let x=x0;x<x0+w;x++) map.set(key(x,4+r),'g'); });
  for(const [k,v] of [...map]){ const [x,y]=k.split(',').map(Number); if((!map.has(key(x+1,y))||!map.has(key(x,y+1)))&&(x-8)+(y-9)>=1) map.set(k,'s'); }
  for(const [x,y] of [[9,3],[10,3],[10,2]]) map.set(key(x,y),'g');
  const rIn=(AK.r+p.gap)/10+0.25, w=p.w/10;
  for(let y=0;y<16;y++)for(let x=0;x<16;x++){
    if(map.has(key(x,y))) continue;
    const dx=x+.5-cx, dy=y+.5-cy, d=Math.hypot(dx,dy);
    const rel=((Math.atan2(dy,dx)*180/Math.PI-p.a+540)%360)-180, t=rel/p.span;
    if(Math.abs(t)>1) continue;
    const out=rIn+w*Math.pow(1-t*t,0.72);
    if(d>=rIn&&d<=out) map.set(key(x,y),(d<rIn+0.85&&Math.abs(t)<0.75)?'l':'m');
  }
  for(const [x,y] of PX_EYES[p.eyes]) map.set(key(x,y),'k');
  const col={g:AK.sun,s:AK.shade,m:moonC,l:litC,k:AK.ink};
  let out='';
  for(const [k,c] of map){ const [x,y]=k.split(',');
    out+=`<rect x="${x}" y="${y}" width="1.04" height="1.04" fill="${col[c]}"${c==='m'||c==='l'?' class="px-moon"':c==='k'?' class="px-eye"':''}/>`; }
  return `<svg class="${cls}" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges" role="img" aria-label="ahkira pixel, ${pose}">${out}</svg>`;
}
