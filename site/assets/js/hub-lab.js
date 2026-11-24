import{a as V}from"./chunks/chunk-3FHO7SEH.js";import{d as C,e as F}from"./chunks/chunk-RGCLR3M6.js";import{D as y,G as M,N as A,O as G,Q as x,T as R,da as S,g as P,ra as z,ya as W}from"./chunks/chunk-IGBBPGQH.js";import{a as I}from"./chunks/chunk-RMPF43B6.js";var f=9e3,T=["vibracao","raiox","fluxo"];function k(){let a=F(105),p=new Float32Array(f*3),n=new Float32Array(f*3),d=new Float32Array(f*2),g=new Float32Array(f),s=120,m=Math.ceil(f/s);for(let e=0;e<f;e++){let o=e%s/(s-1),l=Math.floor(e/s)/(m-1);p.set([(o-.5)*12,0,(l-.5)*7.5],e*3);let t=a()*Math.PI*2,v=Math.max(0,Math.sin(t*18))**.35*.55,c=a(),u,r;c<.55?(u=3.2+v,r=(a()-.5)*1.2):c<.85?(u=1.1+a()*(2.1+v),r=a()<.5?-.6:.6):(u=1.1,r=(a()-.5)*1.2),n.set([Math.cos(t)*u,r,Math.sin(t)*u],e*3),g[e]=Math.abs(t-.9)<.12&&c<.85?1:0,d.set([Math.sqrt(a())*6.2,a()*Math.PI*2],e*2)}let i=new R;return i.setAttribute("position",new x(p,3)),i.setAttribute("aGear",new x(n,3)),i.setAttribute("aVortex",new x(d,2)),i.setAttribute("aFlag",new x(g,1)),i}var E=`
  uniform float uTime, uSize, uPixelRatio;
  uniform vec3 uW;                      // weights: plate, gear, vortex
  attribute vec3 aGear; attribute vec2 aVortex; attribute float aFlag;
  varying vec3 vColor; varying float vAlpha;
  const float PI = 3.141592653589793;
  vec3 ramp(float t){ return mix(vec3(0.18,0.44,0.84), vec3(0.72,0.07,0.17), clamp(t,0.,1.)); }
  void main(){
    // Plate modes (a = 12, b = 7.5); \u03C9 \u221D (m/a)\xB2 + (n/b)\xB2, scaled to a visible frequency.
    float a = 12.0, b = 7.5;
    vec2 u = vec2((position.x + a*0.5)/a, (position.z + b*0.5)/b);
    float w21 = 0.55 * sin(2.0*PI*u.x) * sin(1.0*PI*u.y) * cos(uTime * 40.0 * (4.0/(a*a) + 1.0/(b*b)));
    float w13 = 0.35 * sin(1.0*PI*u.x) * sin(3.0*PI*u.y) * cos(uTime * 40.0 * (1.0/(a*a) + 9.0/(b*b)) + 0.7);
    vec3 pPlate = vec3(position.x, w21 + w13, position.z);
    // Gear spins slowly about y.
    float ga = uTime * 0.25;
    vec3 pGear = vec3(cos(ga)*aGear.x - sin(ga)*aGear.z, aGear.y, sin(ga)*aGear.x + cos(ga)*aGear.z);
    // Rankine vortex: core radius R = 1.6, circulation \u0393.
    float r = aVortex.x, R = 1.6, G = 9.0;
    float omega = r < R ? G/(2.0*PI*R*R) : G/(2.0*PI*r*r);
    float ang = aVortex.y + omega * uTime;
    vec3 pVortex = vec3(cos(ang)*r, 0.0, sin(ang)*r);
    vec3 p = pPlate*uW.x + pGear*uW.y + pVortex*uW.z;
    float speed = omega * r / (G/(2.0*PI*R));
    vec3 cPlate = ramp(0.5 + (w21 + w13) * 0.9);
    vec3 cGear = mix(vec3(0.23,0.27,0.32), vec3(0.72,0.07,0.17), aFlag);
    vec3 cVortex = ramp(speed);
    vColor = cPlate*uW.x + cGear*uW.y + cVortex*uW.z;
    vAlpha = 0.75 + 0.25*aFlag*uW.y;
    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = uSize * uPixelRatio * (1.0 + aFlag*uW.y*1.6) * (12.0 / -mv.z);
  }`,_=`
  varying vec3 vColor; varying float vAlpha;
  void main(){
    vec2 d = gl_PointCoord - 0.5; float r2 = dot(d,d);
    if (r2 > 0.25) discard;
    gl_FragColor = vec4(vColor, vAlpha * smoothstep(0.25, 0.12, r2));
  }`;function O(a){let p=[...a.querySelectorAll("[data-shape]")],n,d=0,g=!0,s=0,m={a:1,b:0,c:0},i=(e,o=!1)=>{d=e,o&&(g=!1),p.forEach((t,v)=>t.setAttribute("aria-pressed",String(v===e)));let l={a:e===0?1:0,b:e===1?1:0,c:e===2?1:0};matchMedia("(prefers-reduced-motion: reduce)").matches?Object.assign(m,l):I.to(m,{...l,duration:1.6,ease:"power3.inOut"}),a.querySelectorAll("[data-panel]").forEach(t=>{t.hidden=t.dataset.panel!==T[e]})};return p.forEach((e,o)=>e.addEventListener("click",()=>i(o,!0))),V(a,{build(e,o){let l=new G;l.background=new A(C.wash);let t=new W(35,1,.1,200);n=new z({uniforms:{uTime:{value:0},uSize:{value:3.4},uPixelRatio:{value:o.getPixelRatio()},uW:{value:new M(1,0,0)}},vertexShader:E,fragmentShader:_,transparent:!0,depthWrite:!1,blending:P});let v=new S(k(),n);v.frustumCulled=!1,l.add(v);let c={fit:1,parallax:[0,0],distance:1},u=0;return[{scene:l,camera:t,state:c,aoRadius:0,aoIntensity:0,frame(r){t.aspect=r;let h=16/Math.min(1,r/1.5)*c.distance,b=y.degToRad(32+c.parallax[1]*6),w=.5+c.parallax[0]*.25;t.position.set(Math.sin(w)*Math.cos(b)*h,Math.sin(b)*h,Math.cos(w)*Math.cos(b)*h),t.lookAt(0,0,0),t.updateProjectionMatrix()},step(r){u+=r,n.uniforms.uTime.value=u,n.uniforms.uPixelRatio.value=o.getPixelRatio(),n.uniforms.uW.value.set(m.a,m.b,m.c),g&&r>0&&(s+=r,s>7&&(s=0,i((d+1)%3)))}}]},warmup(){i(0)},intro(e,o){o[0].state.distance=1.4,e.to(o[0].state,{distance:1,duration:2.2},.1),i(0)}})}export{T as SHAPES,O as mount};
