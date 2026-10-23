/* GRD Motorsport cinematic effects — original, self-contained runtime.
 * Uses the reference's palette, motion concepts and timing, not its third-party portrait.
 * Reproduces interactions with procedural research imagery to avoid impersonation. */
const $ = (q, root=document) => root.querySelector(q);
const $$ = (q, root=document) => [...root.querySelectorAll(q)];
const clamp = (v,a=0,b=1) => Math.max(a,Math.min(b,v));
const lerp = (a,b,t) => a+(b-a)*t;
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const coarse = matchMedia('(hover: none) and (pointer: coarse)');
const phone = matchMedia('(max-width: 639px)');
let lastY = scrollY;
try { history.scrollRestoration = 'manual'; } catch (_) {}
if (!location.hash) scrollTo(0,0);
const showError = (where,err) => {
  const b=$('#asset-error'); if(!b)return;
  b.classList.add('is-visible');
  b.textContent = 'Resource / WebGL warning: '+where+'\n'+String(err?.message || err || 'Failed to initialize')+'\nFallback graphics remain available.';
  console.warn(where,err);
};
const listeners = new Set();
let ticking=false, frameHandle=0;
function tick(t) {
  if (!ticking)return;
  for(const sub of [...listeners]){
    const interval=typeof sub.interval==='function'?sub.interval():sub.interval;
    if(t-sub.last>=interval){const dt=Math.min(64,t-(sub.last<0?t-16:sub.last));sub.last=t;try{sub.fn(t,dt)}catch(e){console.error('Animation subscriber',e);listeners.delete(sub)}}
  }
  if(listeners.size)frameHandle=requestAnimationFrame(tick);else ticking=false;
}
function subscribe(fn,interval=0) {
  const sub={fn,interval,last:-1};listeners.add(sub);
  if(!ticking){ticking=true;frameHandle=requestAnimationFrame(tick)}
  return ()=>{listeners.delete(sub);if(!listeners.size){ticking=false;cancelAnimationFrame(frameHandle)}};
}
function spring(value,target,velocity,dt,tension=190,friction=24){
  for(let i=0;i<Math.min(64,Math.ceil(dt));i++){
    const step=Math.min(1,dt-i)/1000;
    if(step<=0)break;
    velocity+=(-tension*(value-target)-friction*velocity)*step;
    value+=velocity*step;
  }
  return [value,velocity];
}
let lenis=null;
async function setupLenis(){
  if(reduced)return;
  try{
    const lib=await import('lenis');
    lenis=new lib.default({smoothWheel:true});
    subscribe(t=>lenis.raf(t),0);
  }catch(e){showError('Lenis import; using native scrolling',e)}
}
/* Word/letter spring reveal, with accessible original label. */
const textSprings=[];
function installReveals(){
  $$('[data-reveal]').forEach(el=>{
    const text=el.textContent.replace(/\s+/g,' ').trim();
    el.setAttribute('aria-label',text);
    let idx=0;
    const type=el.getAttribute('data-reveal');
    const splitNode=node=>{
      for(const child of [...node.childNodes]){
        if(child.nodeType===3){
          const frag=document.createDocumentFragment();
          const parts=type==='letters'?[...child.textContent]:child.textContent.match(/\s+|[^\s]+/g)||[];
          parts.forEach(part=>{
            if(!part.trim()){frag.appendChild(document.createTextNode(part));return}
            const sp=document.createElement('span');
            sp.className='text-unit';sp.textContent=part;sp.setAttribute('aria-hidden','true');
            if(!reduced){sp.style.opacity='0';sp.style.transform='translateY(.35em)';}
            frag.appendChild(sp);
            textSprings.push({node:sp,host:el,index:idx++,v:0,vel:0,started:false,t0:0});
          });node.replaceChild(frag,child);
        }else if(child.nodeType===1 && child.tagName!=='BR')splitNode(child);
      }
    };
    splitNode(el);
  });
  if(reduced)return;
  const visible=new WeakSet();
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){visible.add(e.target);e.target.dataset.visible='1';io.unobserve(e.target)}}),{rootMargin:'0px 0px -12% 0px'});
  $$('[data-reveal]').forEach(x=>io.observe(x));
  subscribe((t,dt)=>{
    for(const sp of textSprings){
      if(!sp.host.dataset.visible)continue;
      if(!sp.started){sp.started=true;sp.t0=t}
      const delay=sp.index*(sp.host.dataset.reveal==='letters'?24:68);
      if(t-sp.t0<delay)continue;
      [sp.v,sp.vel]=spring(sp.v,1,sp.vel,dt,sp.host.dataset.reveal==='letters'?210:90,24);
      if(1-sp.v<.002&&Math.abs(sp.vel)<.02){sp.v=1;sp.vel=0}
      sp.node.style.opacity=String(clamp(sp.v));
      sp.node.style.transform='translateY('+((1-sp.v)*.35)+'em)';
    }
  },0);
}
/* Full-screen accessible nav, eased independently from the page. */
function setupMenu(){
  const sheet=$('#mobile-sheet'),open=$('#open-menu'),close=$('#close-menu');
  if(!sheet||!open||!close)return;
  let eased=0,vel=0,goal=0; let priorFocus=null;
  function setMenu(v){
    priorFocus=v?document.activeElement:priorFocus;
    goal=v?1:0; sheet.classList.toggle('is-open',v);sheet.setAttribute('aria-hidden',String(!v));
    open.setAttribute('aria-expanded',String(v)); document.documentElement.style.overflow=v?'hidden':'';
    if(v)close.focus();else if(priorFocus instanceof HTMLElement)priorFocus.focus();
    if(reduced){sheet.style.opacity=String(goal);return}
  }
  open.addEventListener('click',()=>setMenu(true));close.addEventListener('click',()=>setMenu(false));
  sheet.addEventListener('click',e=>{if(e.target.closest('a'))setMenu(false)});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&goal)setMenu(false);if(e.key==='Tab'&&goal){const a=$$('button,a',sheet);if(!a.length)return;const first=a[0],last=a[a.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}});
  matchMedia('(min-width: 1280px)').addEventListener('change',e=>{if(e.matches&&goal)setMenu(false)});
  subscribe((t,dt)=>{[eased,vel]=spring(eased,goal,vel,dt,190,26);if(!reduced)sheet.style.opacity=String(clamp(eased));});
}
/* sticky cards recede exactly 0.9 at full overlap, 55% dark shade */
function setupStack(){
  const pinned=$$('.stack-panel');
  subscribe(()=>{
    const h=innerHeight||1, timeline=$('#projects');
    pinned.forEach((el,i)=>{
      const next=pinned[i+1]||timeline;
      const p=clamp(1-next.getBoundingClientRect().top/h);
      const inner=$('.panel-inner',el), shade=$('.panel-shade',el);
      inner.style.transform=p>0&&!phone.matches&&!reduced?'scale('+(1-.1*p)+')':'';
      inner.style.visibility=p>=1?'hidden':'visible';
      shade.style.opacity=String(.55*p);
    });
  },12);
}
/* Shared deterministic dissolving checkered flags on all three seams */
function hash(x,y){
  let h=Math.imul(x,374761393)+Math.imul(y,668265263);
  h=Math.imul(h^(h>>>13),1274126177);
  return ((h^(h>>>16))>>>0)/4294967295;
}
function checker(){
  const bands=$$('[data-checker]');
  subscribe(()=>{
    for(const canvas of bands){
      const rect=canvas.getBoundingClientRect(),w=rect.width,h=rect.height;
      if(rect.bottom<0||rect.top>innerHeight)continue;
      const ratio=Math.min(devicePixelRatio||1,2),nw=Math.max(1,Math.round(w*ratio)),nh=Math.max(1,Math.round(h*ratio));
      if(canvas.width!==nw||canvas.height!==nh){canvas.width=nw;canvas.height=nh}
      const c=canvas.getContext('2d'); if(!c)continue;
      c.setTransform(ratio,0,0,ratio,0,0);c.clearRect(0,0,w,h);
      const progress=clamp((innerHeight-rect.top)/innerHeight),cell=24;
      const nx=Math.ceil(w/cell),ny=Math.ceil(h/cell),lift=progress*2;
      for(let y=0;y<ny;y++){
        const depth=y/Math.max(1,ny-1)+lift;if(depth>1)break;
        const solid=depth<=.16,fade=clamp(1-(depth-.16)/.84);
        for(let x=0;x<nx;x++){
          if(!solid && ((x+y)%2!==0 || hash(x,y)>fade))continue;
          c.fillStyle=!solid&&hash(x+101,y+57)<.06?'#02d2e3':canvas.dataset.checker==='dark'?'#0e0f14':'#f7fafb';
          c.fillRect(x*cell,y*cell,cell,cell);
        }
      }
    }
  },33);
}
/* Animated analytic contour field, marching squares: 2D terrain, no bitmap */
function field(x,y,t){
  return Math.sin(x*3.8+Math.sin(y*1.66+t*.5)*.37)+Math.sin(y*3.2+t*.22)+.7*Math.sin((x+y)*2.45-t*.31)+.43*Math.sin(x*5.2-y*2.0+t*.16);
}
function marchingContours(){
  const elements=$$('[data-contours]');
  subscribe((t)=>{
    for(const canvas of elements){
      const r=canvas.getBoundingClientRect();
      if(r.bottom<0||r.top>innerHeight)continue;
      const w=Math.ceil(r.width),h=Math.ceil(r.height),dpr=Math.min(devicePixelRatio||1,1.2);
      if(canvas.width!==Math.ceil(w*dpr)||canvas.height!==Math.ceil(h*dpr)){canvas.width=Math.ceil(w*dpr);canvas.height=Math.ceil(h*dpr)}
      const ctx=canvas.getContext('2d'); if(!ctx)continue;
      ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
      ctx.strokeStyle=canvas.dataset.contours==='dark'?'#e8fafa':'#5f8a91';
      ctx.globalAlpha=canvas.dataset.contours==='dark'?.2:.18;ctx.lineWidth=1;
      const step=Math.max(15,Math.min(23,Math.round(w/60)));
      const cols=Math.ceil(w/step)+1,rows=Math.ceil(h/step)+1,values=new Float32Array(cols*rows),time=reduced?0:t/1000;
      for(let y=0;y<rows;y++)for(let x=0;x<cols;x++)values[y*cols+x]=field(x*step/250,y*step/250,time);
      const levels=[-1.6,-.9,-.2,.5,1.2,1.9];
      ctx.beginPath();
      for(const level of levels)for(let y=0;y<rows-1;y++)for(let x=0;x<cols-1;x++){
        const corners=[values[y*cols+x],values[y*cols+x+1],values[(y+1)*cols+x+1],values[(y+1)*cols+x]];
        const intersections=[];
        const pts=[[x*step,y*step],[(x+1)*step,y*step],[(x+1)*step,(y+1)*step],[x*step,(y+1)*step]];
        for(let j=0;j<4;j++){
          const k=(j+1)%4,a=corners[j],b=corners[k];
          if((a-level)*(b-level)<0){
            const f=(level-a)/(b-a);
            intersections.push([lerp(pts[j][0],pts[k][0],f),lerp(pts[j][1],pts[k][1],f)]);
          }
        }
        for(let j=0;j+1<intersections.length;j+=2){ctx.moveTo(intersections[j][0],intersections[j][1]);ctx.lineTo(intersections[j+1][0],intersections[j+1][1]);}
      }
      ctx.stroke();
    }
  },reduced?1500:80);
}
/* 8004 halftone points, offset axes, point reticle and ping */
function setupMap(){
 const section=$('#systems'),canvas=$('#map-canvas'),reticle=$('#reticle'),stage=$('#map-stage');
 let px=.5,py=.5,hover=false;
 section.addEventListener('pointermove',e=>{
   if(coarse.matches)return;
   const r=section.getBoundingClientRect();px=clamp((e.clientX-r.left)/r.width);py=clamp((e.clientY-r.top)/r.height);
   hover=true;section.classList.add('is-pointer');
   $('.reticle-h',reticle).style.top=(py*100)+'%';$('.reticle-v',reticle).style.left=(px*100)+'%';
 });
 section.addEventListener('pointerleave',()=>{hover=false;section.classList.remove('is-pointer')});
 subscribe(t=>{
   const r=section.getBoundingClientRect();
   if(r.bottom<0||r.top>innerHeight)return;
   const w=canvas.clientWidth,h=canvas.clientHeight,dpr=Math.min(devicePixelRatio||1,1.2);
   if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}
   const c=canvas.getContext('2d');if(!c)return;
   c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,w,h);
   const centerX=w*.65,centerY=h*.54;
   const unit=Math.min(w/110,h/90),time=reduced?0:t/1000;
   const nx=92,ny=87; // 92 × 87 = 8004 points
   for(let iy=0;iy<ny;iy++)for(let ix=0;ix<nx;ix++){
     const u=ix/nx-.5,v=iy/ny-.5;
     const land=Math.sin(u*11+v*5)+Math.sin(u*7-v*18)+Math.cos(u*27+v*4);
     if(land<-.26)continue;
     const x=w*.48+u*w*.92,y=h*.5+v*h*.94;
     if(x<0||x>w||y<0||y>h)continue;
     const dist=Math.hypot(x-centerX,y-centerY);
     const near=hover&&Math.abs(x-px*w)<unit*2.3&&Math.abs(y-py*h)<unit*2.3;
     c.fillStyle=near?'#02d2e3':'#7a7a7a';
     c.globalAlpha=near?.75:clamp((land+.26)/4,.05,.35);
     const radius=near?Math.max(1.1,unit*.22):Math.max(.6,unit*.12);
     if(near){c.fillRect(x-radius,y-radius,radius*2,radius*2)}else{c.beginPath();c.arc(x,y,radius,0,Math.PI*2);c.fill()}
   }
   c.globalAlpha=.23;c.strokeStyle='#4d4d4d';c.lineWidth=1;c.setLineDash([5,12]);
   const offset=(time*25)%17;c.lineDashOffset=-offset;
   for(let n=0;n<13;n++){let y=n*h/12;c.beginPath();c.moveTo(0,y);c.lineTo(w,y);c.stroke()}
   for(let n=0;n<16;n++){let x=n*w/15;c.beginPath();c.moveTo(x,0);c.lineTo(x,h);c.stroke()}
   c.setLineDash([]);c.globalAlpha=.42;c.strokeStyle='#e3edef';
   for(let i=0;i<3;i++){c.beginPath();c.arc(centerX,centerY,27+i*35,0,Math.PI*2);c.stroke()}
   c.strokeStyle='#02d2e3';c.globalAlpha=.35;
   c.beginPath();c.arc(centerX,centerY,((time*86/4.2)%86)+3,0,Math.PI*2);c.stroke();
   c.globalAlpha=1;
 },reduced?1000:33);
}
/* 6s animated clockwise lap, corner-sensitive progress, 4 lighting markers */
function setupCircuit(){
 const section=$('#systems'),track=$('#track-trace'),head=$('#track-head'),markers=$$('.turn-marker');
 if(!track)return;
 const len=track.getTotalLength(),total=6000;
 track.style.strokeDasharray=String(len);track.style.strokeDashoffset=String(len);
 let started=false,start=0,passed=0;
 const sampleCount=240,weights=[];
 for(let i=0;i<sampleCount;i++){
   const at=(i+.5)/sampleCount*len,p1=track.getPointAtLength(Math.max(0,at-8)),p2=track.getPointAtLength(Math.min(len,at+8)),p0=track.getPointAtLength(Math.max(0,at-17)),p3=track.getPointAtLength(Math.min(len,at+17));
   const a=Math.atan2(p2.y-p1.y,p2.x-p1.x),b=Math.atan2(p3.y-p0.y,p3.x-p0.x);
   const turn=Math.abs(Math.atan2(Math.sin(a-b),Math.cos(a-b)));
   weights.push(.64+turn*1.9);
 }
 const cumulative=[0];for(const w of weights)cumulative.push(cumulative.at(-1)+w);
 const full=cumulative.at(-1);
 const io=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting)&&!started){started=true;start=performance.now();io.disconnect()}},{threshold:.07});
 io.observe(section);
 subscribe(t=>{
   if(!started)return;
   const u=reduced?1:clamp((t-start)/total);let i=0;
   while(i<sampleCount&&cumulative[i+1]/full<u)i++;
   const frac=clamp((u-cumulative[i]/full)/((cumulative[i+1]-cumulative[i])/full||1));
   passed=clamp((i+frac)/sampleCount);
   track.style.strokeDashoffset=String(len*(1-passed));
   const p=track.getPointAtLength(passed*len);
   head.setAttribute('cx',String(p.x));head.setAttribute('cy',String(p.y));
   head.style.opacity=passed>=1?'0':'1';
   for(const marker of markers)marker.classList.toggle('is-passed',passed>=Number(marker.dataset.turn));
   track.style.filter=passed>=1?'none':'drop-shadow(0 0 7px #02d2e3aa)';
 },0);
}
/* Seven art-directed pseudo-photographic plates with 3 depth layers / parallax */
function setupTimeline(){
 const rows=$$('.history'),list=$('#timeline-list'),prog=$('#timeline-progress'),mark=$('#timeline-marker');
 const inview=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in-view');inview.unobserve(e.target)}}),{rootMargin:'0px 0px -25% 0px'});
 rows.forEach(r=>inview.observe(r));
 rows.forEach(row=>{
   row.addEventListener('pointerenter',()=>{rows.forEach(other=>{other.style.opacity=other===row?'1':'.5'})});
   row.addEventListener('pointerleave',()=>rows.forEach(other=>other.style.opacity=''));
 });
 let markerRotation=0;
 subscribe((t)=>{
   const rect=list.getBoundingClientRect(),range=Math.max(1,rect.height-innerHeight*.6);
   const p=clamp((innerHeight*.6-rect.top)/range);
   prog.style.height=(p*100)+'%';mark.style.top=(p*100)+'%';
   markerRotation=lerp(markerRotation,p*5*360,.15);
   mark.style.transform='rotate('+markerRotation+'deg)';
   rows.forEach((r,i)=>{
     const canvas=$('canvas[data-art]',r),cr=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,1.5);
     if(cr.bottom<0||cr.top>innerHeight)return;
     const w=Math.max(1,cr.width),h=Math.max(1,cr.height);
     if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}
     const c=canvas.getContext('2d');if(!c)return;c.setTransform(dpr,0,0,dpr,0,0);
     const offset=reduced?0:(innerHeight*.5-cr.top-cr.height*.5)/innerHeight;
     const drift=(t/1000*.06+i),gradient=c.createLinearGradient(0,0,w,h);
     gradient.addColorStop(0,['#0c2328','#121926','#182c31','#162122','#0d2431','#14282c','#071921'][i]);
     gradient.addColorStop(1,'#030608');c.fillStyle=gradient;c.fillRect(0,0,w,h);
     // far plane: glowing light bands
     c.save();c.translate(offset*-11,0);
     for(let j=0;j<21;j++){let x=j*w/17-50,y=h*(.33+.17*Math.sin(j*.8+i));
       c.strokeStyle=j%3?'#416471':'#02d2e3';c.globalAlpha=.12;c.lineWidth=(j%4)+1;c.beginPath();c.moveTo(x-200,y-80);c.lineTo(x+220,y+30);c.stroke()}
     c.restore();
     // mid plane: track perspective
     c.save();c.translate(offset*23,0);c.lineWidth=3;c.strokeStyle='#d9f9fd';c.globalAlpha=.45;
     for(let j=0;j<5;j++){c.beginPath();c.moveTo(-30,h*(.8-j*.11));c.bezierCurveTo(w*.34,h*(.5-j*.12),w*.59,h*(.88-j*.13),w+25,h*(.36-j*.06));c.stroke()}
     c.restore();
     // near plane: instrument shapes (no sourced driver/photograph)
     c.save();c.translate(offset*45,offset*7);
     c.translate(w*.50,h*.5);c.rotate(-.2+Math.sin(i)*.15);c.globalAlpha=.85;
     c.fillStyle='#04121a';c.strokeStyle='#02d2e3';c.lineWidth=3;
     c.beginPath();c.ellipse(0,0,w*.34,h*.19,0,0,Math.PI*2);c.fill();c.stroke();
     c.fillStyle='#112e36';c.beginPath();c.ellipse(0,0,w*.22,h*.1,0,0,Math.PI*2);c.fill();
     c.strokeStyle='#dcf5f7';c.lineWidth=2;c.beginPath();c.moveTo(-w*.25,0);c.lineTo(w*.25,0);c.stroke();c.restore();
     c.globalAlpha=1;c.fillStyle='#02d2e3';c.font='700 12px monospace';c.fillText('MOTORSPORT / '+String([101,102,103,104,106,109,111][i]),19,h-21);
   });
 },reduced?400:33);
}
/* The calendar band's live bracket and connector motion */
function setupCalendar(){
 const items=$$('.round'); let active=true,triggered=false;
 const io=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting))triggered=true},{rootMargin:'0px 0px -20% 0px'});
 io.observe($('#calendar-list'));
 subscribe(t=>{
  if(!triggered||reduced)return;
  const glow=.18+.13*(.5+.5*Math.sin(t/680));
  const current=$('.round.is-current');
  if(current)current.style.boxShadow='0 0 22px rgba(2,210,227,'+glow+')';
  $('#calendar-list').style.setProperty('--calendar-drift',((t/50)%24)+'px');
  for(const item of items){if(!item.classList.contains('is-current'))item.style.borderTopStyle='dashed'}
 },80);
}
/* Main scene — true 3D geometry, per-fragment shader-based burn/reveal,
   moving normals, two-stage head parallax, analytic contour shader. */
async function setupHeroWebGL() {
 const root=$('#hero-scene'),veil=$('#loading-veil'),progress=$('#loader-bar'),fill=$('#loader-fill');
 const fallback=()=>{root.classList.add('scene-off');$('#hero-fallback').classList.add('is-visible');finishLoader(true)};
 let ready=false,loading=0;
 function finishLoader(failed=false){
   ready=true;
   if(reduced){veil.style.display='none';return}
   veil.dataset.ready='1';
   const t0=performance.now();
   subscribe((t,dt)=>{
      const p=clamp((t-t0)/850);
      veil.style.opacity=String(1-p);veil.style.visibility=p>=1?'hidden':'visible';
      if(p>=1)veil.classList.add('is-out');
   },0);
 }
 subscribe((t,dt)=>{
  if(ready)return;
  loading+=(1-loading)*(dt/2100);
  const p=Math.min(.72,loading);
  progress.style.width=(p*100)+'%';fill.style.height=(p*100)+'%';
 },50);
 let THREE;
 try{THREE=await import('three')}catch(err){showError('three@0.185.0 CDN',err);fallback();return}
 let renderer;
 const tier=()=>{
    const width=innerWidth;
    const mobile=width<768 || (coarse.matches&&width<1024);
    const tablet=!mobile&&(coarse.matches||width<1280);
    return {mobile,coarse:coarse.matches,tablet,dpr:mobile?1:tablet?1.25:1.5,samples:mobile?28:tablet?44:72,outline:!mobile,freeze:reduced,pointer:!coarse.matches&&!reduced,interval:mobile||tablet?1000/60-2:0};
 };
 let settings=tier();
 try{renderer=new THREE.WebGLRenderer({alpha:true,antialias:!settings.mobile&&!settings.tablet,powerPreference:'high-performance'});}
 catch(err){showError('WebGL renderer',err);fallback();return}
 renderer.outputColorSpace=THREE.SRGBColorSpace;
 renderer.setPixelRatio(Math.min(devicePixelRatio||1,settings.dpr));
 renderer.setClearColor(0xf7fafb,0);
 renderer.domElement.setAttribute('aria-hidden','true');
 root.prepend(renderer.domElement);
 const scene=new THREE.Scene();
 const camera=new THREE.OrthographicCamera(-5,5,5,-5,.1,100);camera.position.z=12;
 const uniforms={uTime:{value:0},uPointer:{value:new THREE.Vector2(.5,.5)},uResolution:{value:new THREE.Vector2(1,1)},uIntro:{value:0},uRise:{value:0},uPace:{value:0},uAuto:{value:0},uReveal:{value:1},uTrailCount:{value:72},uTrail:{value:Array.from({length:72},()=>new THREE.Vector2(.5,.5))}};
 const backdropVert=[
 'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}'
 ].join('\n');
 const backgroundFrag=[
 'precision highp float;varying vec2 vUv;uniform float uTime;uniform vec2 uPointer;',
 'float field(vec2 p){p+=vec2(sin(p.y*1.66+uTime*.32),sin(p.x*1.3-uTime*.2))*.37;return sin(p.x*3.8)+sin(p.y*3.1)+.55*sin(dot(p,vec2(2.4,3.5)));}',
 'void main(){vec2 uv=(vUv-.5)*vec2(6.,3.);float f=field(uv);float contour=1.-smoothstep(.022,.07,abs(fract(f*2.5)-.5));',
 'vec3 col=mix(vec3(.969,.98,.985),vec3(.85,.91,.925),contour*.53);col=mix(col,vec3(.81,.91,.93),.10*(1.-smoothstep(0.,1.6,distance(uv,vec2(1.1,0.)))));gl_FragColor=vec4(col,1.);}'
 ].join('\n');
 const bg=new THREE.Mesh(new THREE.PlaneGeometry(2,2),new THREE.ShaderMaterial({vertexShader:backdropVert,fragmentShader:backgroundFrag,uniforms,depthWrite:false,depthTest:false}));
 bg.position.z=-5;scene.add(bg);
 const portraitFrag=[
 'precision highp float;varying vec2 vUv;uniform vec2 uPointer;uniform float uRise;',
 'float sdEllipse(vec2 p,vec2 r){return length(p/r)-1.;}',
 'void main(){vec2 uv=vUv;vec2 p=(uv-.5)*vec2(2.,2.4);p.x+=(uPointer.x-.5)*.01*(1.-uv.y);',
 'float head=1.-smoothstep(-.015,.025,sdEllipse(p-vec2(0.,.26),vec2(.48,.77)));',
 'float shoulders=1.-smoothstep(-.02,.03,sdEllipse(p+vec2(0.,1.09),vec2(1.12,.88)));',
 'float alpha=max(head,shoulders);if(alpha<.01)discard;',
 'vec3 n=normalize(vec3(p.x*.8,p.y*.3,sqrt(max(.15,1.-dot(p*.34,p*.34)))));',
 'vec3 light=normalize(vec3((uPointer.x-.5)*2.2,(uPointer.y-.5)*2.2,.9));',
 'float diffuse=.36+.64*max(0.,dot(n,light));',
 'vec3 dark=vec3(.04,.11,.15),lit=vec3(.38,.54,.6);',
 'float bar=smoothstep(.14,.17,abs(p.x))*(1.-smoothstep(.18,.35,abs(p.x)));',
 'vec3 col=mix(dark,lit,diffuse*.8)+vec3(.0,.11,.14)*bar;',
 'float edge=pow(1.-max(0.,n.z),3.);col+=edge*vec3(.02,.28,.32);',
 'gl_FragColor=vec4(col,alpha*.87);}'
 ].join('\n');
 const portrait=new THREE.Mesh(new THREE.PlaneGeometry(4.6,6.2),new THREE.ShaderMaterial({vertexShader:backdropVert,fragmentShader:portraitFrag,uniforms,transparent:true,depthWrite:false,side:THREE.DoubleSide}));
 portrait.position.z=-1.2;scene.add(portrait);
 const geometry=new THREE.SphereGeometry(1.43,56,36,0,Math.PI*2,.05,Math.PI*.84);
 const helmVert=[
 'varying vec3 vN;varying vec3 vPos;varying vec2 vUv;',
 'void main(){vN=normalize(normalMatrix*normal);vPos=position;vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}'
 ].join('\n');
 const effectFrag=[
 'precision highp float;varying vec3 vN;varying vec3 vPos;varying vec2 vUv;',
 'uniform vec2 uResolution;uniform vec2 uPointer;uniform vec2 uTrail[72];uniform int uTrailCount;',
 'uniform float uIntro;uniform float uTime;uniform float uPace;uniform float uAuto;uniform float uReveal;',
 'float rnd(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
 'float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(rnd(i),rnd(i+vec2(1.,0.)),f.x),mix(rnd(i+vec2(0.,1.)),rnd(i+vec2(1.,1.)),f.x),f.y);}',
 'float capsule(vec2 a,vec2 b,vec2 p,float r){vec2 ab=b-a;float t=clamp(dot(p-a,ab)/max(.0001,dot(ab,ab)),0.,1.);return 1.-smoothstep(r*.8,r,distance(p,a+t*ab));}',
 'void main(){vec3 n=normalize(vN);float light=.46+.54*max(dot(n,normalize(vec3(.7,.8,1.))),0.);',
 'float metallic=pow(1.-max(.0,dot(n,vec3(0.,0.,1.))),2.5);',
 'float stripe=smoothstep(.50,.53,sin(vUv.x*34.+vUv.y*3.));',
 'vec3 navy=vec3(.018,.031,.087),raceBlue=vec3(.075,.16,.35);vec3 base=mix(navy,raceBlue,light);',
 'float gold=step(.72,sin(vUv.x*28.+vUv.y*12.));float red=step(.79,sin(vUv.x*35.-vUv.y*17.));',
 'base=mix(base,vec3(.95,.69,.035),gold*.67);base=mix(base,vec3(.80,.045,.10),red*.83);',
 'base+=metallic*vec3(.16,.20,.27);',
 'vec2 p=gl_FragCoord.xy/max(vec2(1.),uResolution);',
 'float burnNoise=noise(vUv*vec2(15.,20.)+uTime*.08);',
 'float burnAt=mix(1.-vUv.y,burnNoise,.45);',
 'float burnP=smoothstep(.14,1.,uIntro);',
 'float intact=1.-smoothstep(burnAt-.02,burnAt+.02,burnP);',
 'float glow=4.*intact*(1.-intact);',
 'vec2 shift=vec2(noise(p*12.+uTime*.4)-.5,noise(p*12.-uTime*.29+2.)-.5)*.023;',
 'float brush=0.;',
 'for(int i=0;i<71;i++){if(i>=uTrailCount-1)break;float fi=float(i)/float(uTrailCount-1);float taper=pow(1.-fi,mix(3.04,1.9,uPace));',
 'float r=.46*mix(.28,1.,uPace)*taper;',
 'brush=max(brush,capsule(uTrail[i]+shift,uTrail[i+1]+shift,p,r));}',
 'float gate=smoothstep(.06,.21,uPace);',
 'float sweep=capsule(vec2(.3+.3*sin(uTime*.42),.48),vec2(.35+.3*sin(uTime*.42+.3),.54),p,.15)*uAuto;',
 'float revealed=max(brush*gate,sweep);',
 'float revealMask=1.-smoothstep(.075,.085,revealed);',
 'float alpha=mix(intact,1.-revealMask,step(.999,uIntro))*uReveal;',
 'base+=vec3(.0,.53,.59)*glow;',
 'if(alpha<.012)discard;',
 'gl_FragColor=vec4(base,alpha);}'
 ].join('\n');
 const bodyMat=new THREE.ShaderMaterial({vertexShader:helmVert,fragmentShader:effectFrag,uniforms,transparent:true,depthWrite:false,side:THREE.DoubleSide,extensions:{derivatives:true}});
 const pivot=new THREE.Group();scene.add(pivot);
 const shell=new THREE.Mesh(geometry,bodyMat);shell.scale.set(1,1.14,.85);pivot.add(shell);
 const visorGeometry=new THREE.SphereGeometry(1.44,42,24,Math.PI*.94,Math.PI*1.11,.64,.62);
 const visor=new THREE.Mesh(visorGeometry,new THREE.ShaderMaterial({vertexShader:helmVert,fragmentShader:effectFrag,uniforms,transparent:true,depthWrite:false,side:THREE.DoubleSide}));
 visor.rotation.y=Math.PI*.5; visor.position.z=.21;visor.scale.set(1.05,1.06,.87);pivot.add(visor);
 const wireMat=new THREE.ShaderMaterial({
   vertexShader:'varying float vY;void main(){vY=position.y;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
   fragmentShader:'precision highp float;varying float vY;uniform float uTime;uniform float uIntro;void main(){float wave=exp(-pow((vY-(1.4-mod(uTime,3.1)/3.1*2.8))/.15,2.));float reveal=smoothstep(.2,.9,uIntro);gl_FragColor=vec4(.84,.97,1.,.09*wave*reveal);}',
   uniforms,transparent:true,depthWrite:false,depthTest:true
 });
 const wire=new THREE.LineSegments(new THREE.WireframeGeometry(geometry),wireMat);
 wire.scale.copy(shell.scale);pivot.add(wire);
 let trail=Array.from({length:72},()=>new THREE.Vector2(.5,.5)),raw=new THREE.Vector2(.5,.5),ease=new THREE.Vector2(.5,.5);
 let pace=0,rotX=0,rotY=0,velX=0,velY=0,readyAt=0,fitW=0,fitH=0,everRendered=false;
 const resize=()=>{
   const w=Math.max(1,root.clientWidth),h=Math.max(1,root.clientHeight);
   const next=tier();settings=next;
   renderer.setPixelRatio(Math.min(devicePixelRatio||1,settings.dpr));
   renderer.setSize(w,h,false);
   uniforms.uResolution.value.set(renderer.domElement.width,renderer.domElement.height);
   const aspect=w/h,viewH=10,viewW=10*aspect;
   camera.left=-viewW/2;camera.right=viewW/2;camera.top=5;camera.bottom=-5;camera.updateProjectionMatrix();
   bg.scale.set(viewW,viewH,1);
   const targetX=w>=1280?viewW*.22:w>=760?viewW*.13:viewW*.10;
   portrait.position.x=targetX;
   portrait.position.y=-.25;
   pivot.position.x=targetX+.10;
   pivot.position.y=-.7;
   const fit=Math.min(h/740,w/690);
   const scale=Math.max(.66,Math.min(1.36,fit));
   pivot.scale.setScalar(scale);portrait.scale.setScalar(scale);
   wire.visible=settings.outline;
   uniforms.uTrailCount.value=settings.samples;
   uniforms.uAuto.value=settings.mobile?0:coarse.matches?.55:0;
   fitW=w;fitH=h;
 };
 const ro=new ResizeObserver(()=>resize());ro.observe(root);coarse.addEventListener('change',resize);resize();
 let assetEngine=null;
 const params=new URLSearchParams(location.search);
 if(params.has('assetScene')||params.has('referenceScene')){
   try{
     const adapter=await import('./asset-scene.js');
     assetEngine=await adapter.activateAssetScene(THREE,{scene,renderer,pivot,procedural:[shell,visor,wire],portrait,uniforms,camera,error:showError});
     if(params.has('referenceScene')){
       const notice=document.createElement('div');
       notice.setAttribute('role','note');
       notice.style.cssText='position:fixed;top:0;left:0;z-index:650;padding:8px 12px;background:#111;color:#fff;font:12px/1.5 system-ui';
       notice.textContent='Referência visual de terceiros — retrato e capacete não representam Gabriel Reis Duarte.';
       document.body.append(notice);
     }
   }catch(err){showError('Licensed high-fidelity asset scene: check URL/CORS and assets/README.md',err);}
 }
 const onPointer=(e)=>{raw.set(clamp(e.clientX/innerWidth),1-clamp(e.clientY/innerHeight))};
 window.addEventListener('pointermove',onPointer,{passive:true});
 const visibility=()=>document.visibilityState==='visible';
 const loop=subscribe((t,dt)=>{
   if(!visibility()||scrollY>innerHeight*1.25)return;
   const r=root.getBoundingClientRect();if(r.bottom<0||r.top>innerHeight)return;
   if(!readyAt)return;
   if(settings.freeze&&t-readyAt>6300&&everRendered)return;
   const age=t-readyAt;
   uniforms.uTime.value=t/1000;
   uniforms.uIntro.value=clamp((age-400)/4000);
   uniforms.uRise.value=clamp(age/2000);
   // Mobile and reduced-motion visitors need a visible, stable helmet without hover.\n   if(reduced||settings.mobile)uniforms.uIntro.value=0;
   const pointer=settings.pointer?raw:new THREE.Vector2(.65,.5);
   const distance=pointer.distanceTo(ease);
   ease.lerp(pointer,.17);const targetPace=clamp(distance/.029);
   pace=lerp(pace,targetPace,targetPace>pace?.09:.205);
   uniforms.uPace.value=pace;
   const prev=trail[0].clone();trail.pop();trail.unshift(ease.clone());
   // Convert CSS NDC into renderer pixel coordinates with Y measured from bottom.
   uniforms.uTrail.value=trail;
   uniforms.uPointer.value.copy(ease);
   [rotX,velX]=spring(rotX,(ease.y-.5)*2*2.5*Math.PI/180,velX,dt,90,26);
   [rotY,velY]=spring(rotY,(ease.x-.5)*2*2.1*Math.PI/180,velY,dt,90,26);
   pivot.rotation.x=rotX;pivot.rotation.y=rotY;
   const base=fitW>=1280?(10*fitW/fitH)*.22:fitW>=760?(10*fitW/fitH)*.13:(10*fitW/fitH)*.10;
   pivot.position.x=base+.10+(ease.x-.5)*.02;
   portrait.position.x=base+(ease.x-.5)*.03;
   if(assetEngine)assetEngine.update(settings);
   const rise=(1-Math.min(1,age/2000));const dy=rise*200/Math.max(1,fitH)*10;
   pivot.position.y=-.7-dy;portrait.position.y=-.25-dy;
   uniforms.uAuto.value=settings.mobile?0:(coarse.matches?.76:.0);
   renderer.render(scene,camera);everRendered=true;
 },()=>settings.interval);
 try{
   if(renderer.compileAsync)await renderer.compileAsync(scene,camera);
   renderer.render(scene,camera);
   progress.style.width='100%';fill.style.height='100%';
   readyAt=performance.now();finishLoader(false);
 }catch(err){showError('WebGL shader compilation',err);renderer.domElement.style.display='none';fallback()}
}
/* Footer figure rises into frame as the scroll reaches the final panel. */
function setupSignoff(){const block=$('#contact'),figure=$('#signoff-figure');if(!figure)return;subscribe(()=>{const b=block.getBoundingClientRect(),p=clamp((innerHeight-b.top)/(Math.max(innerHeight,b.height)));figure.style.transform='translateY('+(reduced?0:145*(1-p))+'px)'},12)}
/* Initialize non-WebGL interactions immediately; WebGL import can fail independently. */
setupMenu();setupStack();installReveals();checker();marchingContours();setupMap();setupCircuit();setupTimeline();setupCalendar();setupSignoff();setupLenis();
setupHeroWebGL().catch(err=>{showError('Hero scene initialization',err);const veil=$('#loading-veil');veil.classList.add('is-out');veil.style.display='none';$('#hero-fallback').classList.add('is-visible')});

/* Pointer-driven reveal of the opt-in 2D helmet illustration.
   This supplements, and never substitutes for, the procedural Three.js scene. */
function setupConceptHelmetReveal(){
 const hero=document.getElementById('hero');
 const helmet=document.getElementById('concept-helmet');
 if(!hero||!helmet||reduced)return;
 let x=.50,y=.48;
 const update=(nx,ny)=>{
   x=clamp(nx);y=clamp(ny);
   helmet.style.setProperty('--hx',(x*100).toFixed(2)+'%');
   helmet.style.setProperty('--hy',(y*100).toFixed(2)+'%');
   helmet.style.setProperty('--offset-x',((x-.5)*23).toFixed(1)+'px');
   helmet.style.setProperty('--offset-y',((y-.5)*14).toFixed(1)+'px');
 };
 hero.addEventListener('pointermove',e=>{
   if(e.pointerType==='touch'||coarse.matches)return;
   const r=hero.getBoundingClientRect();
   update((e.clientX-r.left)/Math.max(1,r.width),(e.clientY-r.top)/Math.max(1,r.height));
 },{passive:true});
 hero.addEventListener('pointerleave',()=>update(.5,.48),{passive:true});
}
setupConceptHelmetReveal();
