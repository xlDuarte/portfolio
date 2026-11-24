// Laboratório comum: one point cloud that takes three shapes, each a technique that serves both
// niches. All motion is computed in the vertex shader from closed-form physics:
//   vibração    plate modes of a simply supported plate, w = Σ A_mn sin(mπx/a) sin(nπz/b) cos(ω_mn t),
//               ω_mn ∝ (m/a)² + (n/b)² (Kirchhoff plate)            → projeto #104
//   raio-x      a gear sampled on its surface, with a cluster of "defect" points   → #105
//   fluxo       Rankine vortex: ω(r) = Γ/(2πR²) inside the core, Γ/(2πr²) outside  → #103
import {
  BufferAttribute, BufferGeometry, Color, NormalBlending, PerspectiveCamera, Points, Scene,
  ShaderMaterial, MathUtils, Vector3,
} from "three";
import { gsap } from "gsap";
import { mountStage } from "./common.js";
import { C, mulberry32 } from "../hero/palette.js";

const N = 9000;
export const SHAPES = ["vibracao", "raiox", "fluxo"];

function geometry() {
  const rng = mulberry32(105);
  const plate = new Float32Array(N * 3), gear = new Float32Array(N * 3), vortex = new Float32Array(N * 2), flag = new Float32Array(N);
  const cols = 120, rows = Math.ceil(N / cols);
  for (let i = 0; i < N; i++) {
    const cx = (i % cols) / (cols - 1), cz = Math.floor(i / cols) / (rows - 1);
    plate.set([(cx - 0.5) * 12, 0, (cz - 0.5) * 7.5], i * 3);
    // Gear: 18 teeth, tooth height 0.55, thickness 1.2, sampled on outer rim, faces and bore.
    const th = rng() * Math.PI * 2;
    const tooth = Math.max(0, Math.sin(th * 18)) ** 0.35 * 0.55;
    const pick = rng();
    let r, y;
    if (pick < 0.55) { r = 3.2 + tooth; y = (rng() - 0.5) * 1.2; }
    else if (pick < 0.85) { r = 1.1 + rng() * (2.1 + tooth); y = rng() < 0.5 ? -0.6 : 0.6; }
    else { r = 1.1; y = (rng() - 0.5) * 1.2; }
    gear.set([Math.cos(th) * r, y, Math.sin(th) * r], i * 3);
    // A crack near one tooth root: the kind of defect the radiography model flags.
    flag[i] = Math.abs(th - 0.9) < 0.12 && pick < 0.85 ? 1 : 0;
    vortex.set([Math.sqrt(rng()) * 6.2, rng() * Math.PI * 2], i * 2);
  }
  const g = new BufferGeometry();
  g.setAttribute("position", new BufferAttribute(plate, 3));
  g.setAttribute("aGear", new BufferAttribute(gear, 3));
  g.setAttribute("aVortex", new BufferAttribute(vortex, 2));
  g.setAttribute("aFlag", new BufferAttribute(flag, 1));
  return g;
}

const vertexShader = `
  uniform float uTime, uSize, uPixelRatio;
  uniform vec3 uW;                      // weights: plate, gear, vortex
  attribute vec3 aGear; attribute vec2 aVortex; attribute float aFlag;
  varying vec3 vColor; varying float vAlpha;
  const float PI = 3.141592653589793;
  vec3 ramp(float t){ return mix(vec3(0.18,0.44,0.84), vec3(0.72,0.07,0.17), clamp(t,0.,1.)); }
  void main(){
    // Plate modes (a = 12, b = 7.5); ω ∝ (m/a)² + (n/b)², scaled to a visible frequency.
    float a = 12.0, b = 7.5;
    vec2 u = vec2((position.x + a*0.5)/a, (position.z + b*0.5)/b);
    float w21 = 0.55 * sin(2.0*PI*u.x) * sin(1.0*PI*u.y) * cos(uTime * 40.0 * (4.0/(a*a) + 1.0/(b*b)));
    float w13 = 0.35 * sin(1.0*PI*u.x) * sin(3.0*PI*u.y) * cos(uTime * 40.0 * (1.0/(a*a) + 9.0/(b*b)) + 0.7);
    vec3 pPlate = vec3(position.x, w21 + w13, position.z);
    // Gear spins slowly about y.
    float ga = uTime * 0.25;
    vec3 pGear = vec3(cos(ga)*aGear.x - sin(ga)*aGear.z, aGear.y, sin(ga)*aGear.x + cos(ga)*aGear.z);
    // Rankine vortex: core radius R = 1.6, circulation Γ.
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
  }`;
const fragmentShader = `
  varying vec3 vColor; varying float vAlpha;
  void main(){
    vec2 d = gl_PointCoord - 0.5; float r2 = dot(d,d);
    if (r2 > 0.25) discard;
    gl_FragColor = vec4(vColor, vAlpha * smoothstep(0.25, 0.12, r2));
  }`;

export function mount(root) {
  const buttons = [...root.querySelectorAll("[data-shape]")];
  let material, current = 0, auto = true, timer = 0;
  const weights = { a: 1, b: 0, c: 0 };
  const show = (i, user = false) => {
    current = i;
    if (user) auto = false;
    buttons.forEach((b, j) => b.setAttribute("aria-pressed", String(j === i)));
    const target = { a: i === 0 ? 1 : 0, b: i === 1 ? 1 : 0, c: i === 2 ? 1 : 0 };
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) Object.assign(weights, target);
    else gsap.to(weights, { ...target, duration: 1.6, ease: "power3.inOut" });
    root.querySelectorAll("[data-panel]").forEach((p) => { p.hidden = p.dataset.panel !== SHAPES[i]; });
  };
  buttons.forEach((b, i) => b.addEventListener("click", () => show(i, true)));

  return mountStage(root, {
    build(_env, renderer) {
      const scene = new Scene();
      scene.background = new Color(C.wash);
      const camera = new PerspectiveCamera(35, 1, 0.1, 200);
      material = new ShaderMaterial({
        uniforms: { uTime: { value: 0 }, uSize: { value: 3.4 }, uPixelRatio: { value: renderer.getPixelRatio() }, uW: { value: new Vector3(1, 0, 0) } },
        vertexShader, fragmentShader, transparent: true, depthWrite: false, blending: NormalBlending,
      });
      const pts = new Points(geometry(), material);
      pts.frustumCulled = false;
      scene.add(pts);
      const state = { fit: 1, parallax: [0, 0], distance: 1 };
      let t = 0;
      return [{
        scene, camera, state, aoRadius: 0, aoIntensity: 0,
        frame(aspect) {
          camera.aspect = aspect;
          const d = (16 / Math.min(1, aspect / 1.5)) * state.distance;
          const el = MathUtils.degToRad(32 + state.parallax[1] * 6), az = 0.5 + state.parallax[0] * 0.25;
          camera.position.set(Math.sin(az) * Math.cos(el) * d, Math.sin(el) * d, Math.cos(az) * Math.cos(el) * d);
          camera.lookAt(0, 0, 0);
          camera.updateProjectionMatrix();
        },
        step(dt) {
          t += dt;
          material.uniforms.uTime.value = t;
          material.uniforms.uPixelRatio.value = renderer.getPixelRatio();
          material.uniforms.uW.value.set(weights.a, weights.b, weights.c);
          if (auto && dt > 0) { timer += dt; if (timer > 7) { timer = 0; show((current + 1) % 3); } }
        },
      }];
    },
    warmup() { show(0); },
    intro(tl, views) {
      views[0].state.distance = 1.4;
      tl.to(views[0].state, { distance: 1, duration: 2.2 }, 0.1);
      show(0);
    },
  });
}

