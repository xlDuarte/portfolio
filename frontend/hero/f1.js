// F1 view: Sakhir 2024, four real minutes from OpenF1.
// Positions, speed, gear: observed. Accelerations and front-disc temperature: derived in
// scripts/telemetry_physics.py. Chassis pitch/roll follow the derived accelerations through a
// spring-damper (physics.js); disc glow uses the black-body colour of the modelled temperature;
// titanium skid-block sparks appear at full throttle above 265 km/h (illustrative trigger).
import {
  BoxGeometry, BufferAttribute, BufferGeometry, Color, ConeGeometry, CylinderGeometry,
  DirectionalLight, DoubleSide, Group, HemisphereLight, Line, LineBasicMaterial, MathUtils, Mesh,
  MeshStandardMaterial, PerspectiveCamera, PlaneGeometry, Scene, ShadowMaterial, Vector3,
} from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { SparkField, SpringDamper } from "../scene/physics.js";
import { SparkView, BLACKBODY } from "../scene/sparks.js";
import { C } from "./palette.js";

export const DISPLAY = {
  trackScale: 1 / 100,     // decimetre -> scene unit (1 unit = 10 m)
  elevation: 4,            // vertical exaggeration of Sakhir's real elevation
  trackWidth: 3.0,         // scene units (real ~1.4); widened for legibility
  carScale: 2.6,           // cars drawn 2.6x their real size
  trailSeconds: 6,
  pitchDegPerG: 1.2,       // chassis motion exaggerated for legibility
  rollDegPerG: 1.0,
};
const F = { x: 0, y: 1, z: 2, speed: 3, gear: 4, throttle: 5, brake: 6, lap: 7, alat: 8, along: 9, disc: 10 };

const TITANIUM = Object.freeze({
  drag: 0.35, convection: 1.6, radiation: 2e-13, ambientK: 300, visibleK: 1100,
  restitution: 0.45, friction: 0.35, contactCoolingK: 60, maxLife: 1.2,
});

function carModel(colour) {
  const g = new Group();
  const body = new Group();
  const paint = new MeshStandardMaterial({ color: colour, roughness: 0.32, metalness: 0.35 });
  const carbon = new MeshStandardMaterial({ color: 0x1a1d21, roughness: 0.5, metalness: 0.2 });
  const tyre = new MeshStandardMaterial({ color: 0x15171a, roughness: 0.85 });
  const add = (geo, mat, x, y, z, rz = 0) => { const m = new Mesh(geo, mat); m.position.set(x, y, z); m.rotation.z = rz; body.add(m); return m; };
  add(new BoxGeometry(0.34, 0.09, 0.13), paint, 0, 0.07, 0);                 // monocoque
  add(new BoxGeometry(0.2, 0.05, 0.22), paint, -0.05, 0.06, 0);              // sidepods
  add(new ConeGeometry(0.045, 0.22, 10), paint, 0.27, 0.06, 0, -Math.PI / 2); // nose
  add(new BoxGeometry(0.05, 0.012, 0.26), carbon, 0.37, 0.025, 0);            // front wing
  add(new BoxGeometry(0.05, 0.05, 0.2), carbon, -0.2, 0.15, 0);               // rear wing
  add(new BoxGeometry(0.06, 0.07, 0.02), carbon, -0.19, 0.11, 0);             // pillar
  add(new BoxGeometry(0.42, 0.01, 0.2), carbon, 0, 0.012, 0);                 // floor / plank
  const wheels = [], discs = [];
  const wheelGeo = new CylinderGeometry(0.045, 0.045, 0.05, 16);
  const discGeo = new CylinderGeometry(0.026, 0.026, 0.052, 14);
  for (const [x, front] of [[0.2, true], [-0.17, false]]) {
    for (const z of [-0.12, 0.12]) {
      const w = new Mesh(wheelGeo, tyre);
      w.rotation.x = Math.PI / 2;
      w.position.set(x, 0.045, z);
      g.add(w); wheels.push(w);
      if (front) {
        const d = new Mesh(discGeo, new MeshStandardMaterial({ color: 0x222222, emissive: 0x000000, roughness: 0.6 }));
        d.rotation.x = Math.PI / 2;
        d.position.set(x, 0.045, z);
        g.add(d); discs.push(d);
      }
    }
  }
  g.add(body);
  g.traverse((o) => { if (o.isMesh) o.castShadow = true; });
  return { g, body, discs };
}

export function buildF1(f1, env) {
  const scene = new Scene();
  scene.environment = env;
  scene.background = new Color(C.wash);
  const camera = new PerspectiveCamera(26, 1, 1, 2000);

  scene.add(new HemisphereLight(0xffffff, 0xdfe3e8, 0.95));
  const sun = new DirectionalLight(0xffffff, 2.0);
  sun.position.set(-18, 120, 30);
  sun.castShadow = true;
  Object.assign(sun.shadow.camera, { left: -75, right: 75, top: 75, bottom: -75, near: 10, far: 260 });
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.05;
  scene.add(sun);

  const ground = new Mesh(new PlaneGeometry(400, 400), new ShadowMaterial({ opacity: 0.1 }));
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  const ext = f1.track.extent_dm;
  const plinth = new Mesh(new BoxGeometry(ext[0] / 100 + 9, 0.9, ext[1] / 100 + 9),
    new MeshStandardMaterial({ color: 0xf7f8fa, roughness: 0.55 }));
  plinth.position.y = 0.45;
  plinth.castShadow = plinth.receiveShadow = true;
  scene.add(plinth);

  const S = DISPLAY.trackScale, E = DISPLAY.elevation, BASE = 1.2;
  const toV = (p) => new Vector3(p[0] * S, BASE + p[2] * S * E, -p[1] * S);
  const centre = f1.track.points.map(toV);
  const N = centre.length;
  const left = [], right = [];
  for (let i = 0; i < N; i++) {
    const a = centre[(i - 1 + N) % N], b = centre[(i + 1) % N];
    const t = new Vector3(b.x - a.x, 0, b.z - a.z).normalize();
    const n = new Vector3(-t.z, 0, t.x).multiplyScalar(DISPLAY.trackWidth / 2);
    left.push(centre[i].clone().add(n));
    right.push(centre[i].clone().sub(n));
  }
  const topPos = [], topIdx = [];
  for (let i = 0; i < N; i++) topPos.push(...left[i].toArray(), ...right[i].toArray());
  for (let i = 0; i < N; i++) {
    const j = (i + 1) % N, a = 2 * i, b = 2 * i + 1, c = 2 * j, d = 2 * j + 1;
    topIdx.push(a, b, d, a, d, c);
  }
  const topGeo = new BufferGeometry();
  topGeo.setAttribute("position", new BufferAttribute(new Float32Array(topPos), 3));
  topGeo.setIndex(topIdx);
  topGeo.computeVertexNormals();
  const top = new Mesh(topGeo, new MeshStandardMaterial({ color: C.asphalt, roughness: 0.82, metalness: 0.05, side: DoubleSide }));
  top.castShadow = top.receiveShadow = true;
  scene.add(top);
  const wallPos = [];
  for (const edge of [left, right]) {
    for (let i = 0; i < N; i++) {
      const p = edge[i], q = edge[(i + 1) % N];
      wallPos.push(p.x, p.y, p.z, q.x, q.y, q.z, q.x, 0.9, q.z, p.x, p.y, p.z, q.x, 0.9, q.z, p.x, 0.9, p.z);
    }
  }
  const wallGeo = new BufferGeometry();
  wallGeo.setAttribute("position", new BufferAttribute(new Float32Array(wallPos), 3));
  wallGeo.computeVertexNormals();
  const walls = new Mesh(wallGeo, new MeshStandardMaterial({ color: C.resin, roughness: 0.6, side: DoubleSide }));
  walls.castShadow = walls.receiveShadow = true;
  scene.add(walls);
  const edgeMat = new LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.55 });
  for (const edge of [left, right]) {
    const inset = edge.map((p, i) => p.clone().lerp(centre[i], 0.12).setY(p.y + 0.02));
    scene.add(new Line(new BufferGeometry().setFromPoints([...inset, inset[0]]), edgeMat));
  }

  // Racing line coloured by the leader's real speed over the reference lap.
  const lead = f1.cars[0];
  const lapSamples = lead.samples.slice(0, Math.round(97 * f1.sample_hz));
  const speeds = centre.map((_, i) => {
    const p = f1.track.points[i];
    let best = Infinity, sp = 0;
    for (const s of lapSamples) {
      const d = (s[0] - p[0]) ** 2 + (s[1] - p[1]) ** 2;
      if (d < best) { best = d; sp = s[F.speed]; }
    }
    return sp;
  });
  const vMin = Math.min(...speeds), vMax = Math.max(...speeds);
  const ramp = (v) => {
    const t = MathUtils.clamp((v - vMin) / (vMax - vMin), 0, 1);
    return C.slow.map((c, k) => c + (C.fast[k] - c) * t);
  };
  const segPos = [], segCol = [];
  for (let i = 0; i < N; i++) {
    const a = centre[i], b = centre[(i + 1) % N];
    segPos.push(a.x, a.y + 0.03, a.z, b.x, b.y + 0.03, b.z);
    segCol.push(...ramp(speeds[i]), ...ramp(speeds[(i + 1) % N]));
  }
  const racingMat = new LineMaterial({ vertexColors: true, linewidth: 4, worldUnits: false });
  scene.add(new LineSegments2(new LineSegmentsGeometry().setPositions(segPos).setColors(segCol), racingMat));

  const carColours = [C.auto, C.graphite, C.slate];
  const cars = f1.cars.map((car, ci) => {
    const model = carModel(carColours[ci]);
    model.g.scale.setScalar(DISPLAY.carScale);
    scene.add(model.g);
    const segs = Math.round(DISPLAY.trailSeconds * f1.sample_hz * 2);
    const tGeo = new LineSegmentsGeometry().setPositions(new Float32Array(segs * 6)).setColors(new Float32Array(segs * 6));
    const trail = new LineSegments2(tGeo, new LineMaterial({ vertexColors: true, linewidth: 3, worldUnits: false, transparent: true }));
    trail.frustumCulled = false;
    scene.add(trail);
    const sparks = new SparkField(260, TITANIUM);
    const sparkView = new SparkView(sparks, DISPLAY.carScale / 10, { intensity: 1.6, refK: 1800, size: 2.6 });
    sparkView.addTo(scene);
    return { car, model, trail, tGeo, segs, colour: new Color(carColours[ci]), sparks, sparkView,
             pitch: new SpringDamper(2.2, 0.65), roll: new SpringDamper(2.6, 0.7), emitAcc: 0 };
  });

  const total = lead.samples.length / f1.sample_hz;
  const span = total - 0.6;
  function sampleAt(car, t) {
    const s = car.samples, k = t * f1.sample_hz;
    const i = Math.min(Math.floor(k), s.length - 2), f = k - i;
    const a = s[i], b = s[i + 1];
    const lerp = (j) => a[j] + (b[j] - a[j]) * f;
    return {
      x: lerp(F.x) * S, y: BASE + lerp(F.z) * S * E + 0.02, z: -lerp(F.y) * S,
      speed: Math.round(lerp(F.speed)), gear: a[F.gear], lap: a[F.lap], throttle: lerp(F.throttle),
      brake: a[F.brake], aLat: lerp(F.alat), aLong: lerp(F.along), disc: lerp(F.disc),
    };
  }

  let t = 0;
  const readout = [];
  const tmp = new Vector3(), tmp2 = new Vector3(), col = [0, 0, 0];
  const history = [];                  // leader's (aLat, aLong) for the g-g diagram
  function step(dt) {
    t = (((t + dt) % span) + span) % span;
    readout.length = 0;
    for (const c of cars) {
      const p = sampleAt(c.car, t), q = sampleAt(c.car, Math.min(t + 0.25, span));
      const heading = -Math.atan2(q.z - p.z, q.x - p.x);
      c.model.g.position.set(p.x, p.y, p.z);
      c.model.g.rotation.y = heading;
      const pitch = c.pitch.step(MathUtils.degToRad(DISPLAY.pitchDegPerG * p.aLong), dt);
      const roll = c.roll.step(MathUtils.degToRad(DISPLAY.rollDegPerG * p.aLat), dt);
      c.model.body.rotation.set(roll, 0, pitch);
      // Front discs: black-body colour and T⁴ radiance of the modelled temperature.
      const TK = p.disc + 273.15;
      BLACKBODY.sample(TK, col);
      const k = Math.max(0, BLACKBODY.radiance(TK, 1000) - 0.08) * 3.2;
      for (const d of c.model.discs) d.material.emissive.setRGB(col[0] * k, col[1] * k, col[2] * k);

      // Skid-block sparks at full throttle and high speed.
      if (dt > 0 && p.speed > 265 && p.throttle > 97) {
        const gate = 0.5 + 0.5 * Math.sin(t * 13.7 + c.car.number) * Math.sin(t * 5.3);
        c.emitAcc += dt * 140 * Math.max(0, gate);
        const upm = DISPLAY.carScale / 10;
        const vx = (q.x - p.x) / 0.25 / upm, vz = (q.z - p.z) / 0.25 / upm;
        const back = tmp.set(-0.18, 0.004, 0).applyEuler(c.model.g.rotation).multiplyScalar(DISPLAY.carScale).add(c.model.g.position);
        while (c.emitAcc >= 1) {
          c.emitAcc -= 1;
          const f = 0.55 + Math.random() * 0.25;
          c.sparks.emit(back.x / upm, back.y / upm, back.z / upm,
            vx * f + (Math.random() - 0.5) * 3, 1 + Math.random() * 2.5, vz * f + (Math.random() - 0.5) * 3,
            2300 + Math.random() * 400);
        }
      }
      const groundM = (p.y - 0.02) / (DISPLAY.carScale / 10);
      c.sparks.step(dt, () => groundM);
      c.sparkView.update();

      const pos = c.tGeo.attributes.instanceStart.data.array;
      const colArr = c.tGeo.attributes.instanceColorStart.data.array;
      for (let k2 = 0; k2 < c.segs; k2++) {
        const ta = Math.max(0, t - DISPLAY.trailSeconds * (1 - k2 / c.segs));
        const tb = Math.max(0, t - DISPLAY.trailSeconds * (1 - (k2 + 1) / c.segs));
        const a = sampleAt(c.car, ta), b = sampleAt(c.car, tb);
        pos.set([a.x, a.y + 0.06, a.z, b.x, b.y + 0.06, b.z], k2 * 6);
        const fa = k2 / c.segs, fb = (k2 + 1) / c.segs;
        colArr.set([1 - (1 - c.colour.r) * fa, 1 - (1 - c.colour.g) * fa, 1 - (1 - c.colour.b) * fa,
          1 - (1 - c.colour.r) * fb, 1 - (1 - c.colour.g) * fb, 1 - (1 - c.colour.b) * fb], k2 * 6);
      }
      c.tGeo.attributes.instanceStart.data.needsUpdate = true;
      c.tGeo.attributes.instanceColorStart.data.needsUpdate = true;
      readout.push({ code: c.car.code, ...p, world: tmp2.set(p.x, p.y + 1.1, p.z).clone() });
    }
    const L = readout[0];
    if (L) { history.push([L.aLat, L.aLong]); if (history.length > 180) history.shift(); }
  }

  const lines = [racingMat, ...cars.map((c) => c.trail.material)];
  const hx = ext[0] / 200 + 4.5, hz = ext[1] / 200 + 4.5;
  const corners = [];
  for (const x of [-hx, hx]) for (const y of [0, 3]) for (const z of [-hz, hz]) corners.push(new Vector3(x, y, z));
  const ndc = new Vector3(), look = new Vector3(0, 1.5, 0);
  const state = { distance: 1, elevation: 42, azimuth: 1.15, fit: 0.8, parallax: [0, 0], pan: [0, 0] };
  const panX = new Vector3(), panY = new Vector3();
  function place(dist, el, az) {
    camera.position.set(Math.sin(az) * Math.cos(el) * dist, Math.sin(el) * dist, Math.cos(az) * Math.cos(el) * dist);
    camera.lookAt(look);
    camera.updateMatrixWorld();
  }
  function frame(aspect) {
    camera.aspect = aspect;
    camera.updateProjectionMatrix();
    const el = MathUtils.degToRad(state.elevation + state.parallax[1] * 3);
    const az = state.azimuth + state.parallax[0] * 0.08;
    let dist = 200;
    for (let it = 0; it < 3; it++) {
      place(dist, el, az);
      let mx = 0, my = 0;
      for (const c of corners) { ndc.copy(c).project(camera); mx = Math.max(mx, Math.abs(ndc.x)); my = Math.max(my, Math.abs(ndc.y)); }
      dist *= Math.max(mx / (0.93 * state.fit), my / 0.93);
    }
    place(dist * state.distance, el, az);
    // Pan in screen space so the circuit clears the read-out panel (fractions of half-height).
    if (state.pan[0] || state.pan[1]) {
      const half = Math.tan(MathUtils.degToRad(camera.fov / 2)) * camera.position.distanceTo(look);
      panX.setFromMatrixColumn(camera.matrixWorld, 0).multiplyScalar(state.pan[0] * half * camera.aspect);
      panY.setFromMatrixColumn(camera.matrixWorld, 1).multiplyScalar(state.pan[1] * half);
      camera.position.add(panX).add(panY);
      camera.updateMatrixWorld();
    }
  }
  const setShadowSize = (s) => { sun.shadow.mapSize.set(s, s); sun.shadow.map?.dispose(); sun.shadow.map = null; };
  const tint = (amount) => scene.background.setHex(C.wash).lerp(new Color(C.autoWash), amount);
  return { scene, camera, step, frame, setShadowSize, tint, lines, readout, history, state,
           speedRange: [vMin, vMax], aoRadius: 4, aoIntensity: 0.8 };
}
