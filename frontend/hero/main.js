// Home hero, "Telemetria viva": one WebGL canvas, two viewports.
//   left  = isometric production line driven by the OEE case-study data (synthetic)
//   right = Sakhir 2024 replay driven by OpenF1 positions and telemetry (observed)
// Every moving value comes from /assets/hero/hero-data.json, built by
// scripts/build_hero_data.py from files in the repository.
import {
  ACESFilmicToneMapping, BoxGeometry, BufferAttribute, BufferGeometry, Color, ConeGeometry,
  CylinderGeometry, DirectionalLight, DoubleSide, Group, HemisphereLight, InstancedMesh,
  Line, LineBasicMaterial, MathUtils, Matrix4, Mesh, MeshStandardMaterial, Object3D,
  OrthographicCamera, PCFShadowMap, PerspectiveCamera, PlaneGeometry, PMREMGenerator,
  Scene, ShadowMaterial, SRGBColorSpace, Vector3, WebGLRenderer, CanvasTexture,
  RepeatWrapping,
} from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { gsap } from "gsap";

// ---------------------------------------------------------------------------
// Palette (mirrors docs/ART-DIRECTION.md). Data colours are never used for text.
const C = {
  ind: 0x1d4e9e, auto: 0xb8122b, graphite: 0x1c2128, slate: 0x59616b,
  steel: 0xcfd5dc, steelDark: 0x9aa3ad, concrete: 0xeceff2, aisle: 0xd9dee4,
  belt: 0x3a4048, asphalt: 0x2f343b, resin: 0xc9cfd6, run: 0x1b7a48, stop: 0xc58a00,
  part: 0xf4f6f8, reject: 0xb8122b, slow: [0.93, 0.94, 0.95], fast: [1.0, 0.19, 0.28],
};
const NUM = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1, minimumFractionDigits: 1 });
const INT = new Intl.NumberFormat("pt-BR");
const pct = (v) => `${NUM.format(v * 100)}%`;

// Display-only scalings, declared so nobody mistakes them for measurements.
const DISPLAY = {
  trackScale: 1 / 100,      // decimetre -> scene unit (1 unit = 10 m)
  elevation: 4,             // vertical exaggeration of Sakhir's real elevation
  trackWidth: 3.0,          // scene units (real ~1.4); widened for legibility
  carScale: 2.6,            // cars drawn 2.6x their real size
  trailSeconds: 6,
  beltSpeed: 1.7,           // scene units/s at 100% performance
  stopCycle: 24,            // seconds; each line stops (1 - availability) of every cycle
};

function mulberry32(seed) {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------------------------------------------------------------------------
// Industrial scene
function buildIndustrial(data, envMap) {
  const scene = new Scene();
  scene.environment = envMap;
  const camera = new OrthographicCamera(-10, 10, 10, -10, 0.1, 200);
  camera.position.set(30, 25, 30);
  camera.lookAt(0, 0.6, 0);

  scene.add(new HemisphereLight(0xffffff, 0xd8dde3, 0.9));
  const sun = new DirectionalLight(0xffffff, 2.1);
  sun.position.set(-8, 18, 10);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  Object.assign(sun.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 50 });
  sun.shadow.radius = 4;
  sun.shadow.bias = -0.0004;
  scene.add(sun);

  const floor = new Mesh(new BoxGeometry(24, 0.3, 14),
    new MeshStandardMaterial({ color: C.concrete, roughness: 0.92, metalness: 0 }));
  floor.position.y = -0.15;
  floor.receiveShadow = true;
  scene.add(floor);
  // Painted aisle lines: the only texture on the floor, as on a real shop floor.
  const aisleMat = new MeshStandardMaterial({ color: C.aisle, roughness: 0.9 });
  for (const z of [-6.2, 0, 6.2]) {
    const m = new Mesh(new BoxGeometry(23, 0.02, z === 0 ? 0.08 : 0.16), aisleMat);
    m.position.set(0, 0.01, z);
    m.receiveShadow = true;
    scene.add(m);
  }

  const steel = new MeshStandardMaterial({ color: C.steel, metalness: 0.75, roughness: 0.32, envMapIntensity: 1.1 });
  const steelDark = new MeshStandardMaterial({ color: C.steelDark, metalness: 0.6, roughness: 0.45 });
  const panel = new MeshStandardMaterial({ color: C.ind, metalness: 0.2, roughness: 0.4 });

  // Belt surface texture: cleats every 0.5 unit, scrolled while the line runs.
  const canvas = document.createElement("canvas");
  canvas.width = 64; canvas.height = 8;
  const g = canvas.getContext("2d");
  g.fillStyle = "#3a4048"; g.fillRect(0, 0, 64, 8);
  g.fillStyle = "#4a515a"; g.fillRect(0, 0, 6, 8);
  const beltTex = new CanvasTexture(canvas);
  beltTex.colorSpace = SRGBColorSpace;
  beltTex.wrapS = beltTex.wrapT = RepeatWrapping;
  beltTex.repeat.set(32, 1);

  const LEN = 17, X0 = -LEN / 2, X1 = LEN / 2, BELT_Y = 0.95;
  const rng = mulberry32(20240302);
  const lines = data.lines.map((spec, li) => {
    const z = li === 0 ? -2.6 : 2.6;
    const tex = beltTex.clone();
    tex.needsUpdate = true;
    const belt = new Mesh(new BoxGeometry(LEN, 0.18, 1.3),
      [steelDark, steelDark, new MeshStandardMaterial({ map: tex, roughness: 0.8 }), steelDark, steelDark, steelDark]);
    belt.position.set(0, BELT_Y, z);
    belt.castShadow = belt.receiveShadow = true;
    scene.add(belt);
    for (let x = X0 + 0.6; x <= X1; x += 2.8) {
      for (const dz of [-0.55, 0.55]) {
        const leg = new Mesh(new BoxGeometry(0.12, BELT_Y, 0.12), steelDark);
        leg.position.set(x, BELT_Y / 2, z + dz);
        leg.castShadow = true;
        scene.add(leg);
      }
    }
    const lights = [];
    for (const mx of [-5.2, 0, 5.2]) {
      const arch = new Group();
      for (const dz of [-0.95, 0.95]) {
        const pillar = new Mesh(new BoxGeometry(1.5, 2.3, 0.3), steel);
        pillar.position.set(0, 1.15, dz);
        arch.add(pillar);
      }
      const top = new Mesh(new BoxGeometry(1.7, 0.9, 2.3), steel);
      top.position.y = 2.6;
      arch.add(top);
      const face = new Mesh(new BoxGeometry(0.04, 0.5, 1.6), panel);
      face.position.set(0.87, 2.6, 0);
      arch.add(face);
      const lamp = new Mesh(new CylinderGeometry(0.16, 0.16, 0.22, 20),
        new MeshStandardMaterial({ color: C.run, emissive: C.run, emissiveIntensity: 0.9, roughness: 0.3 }));
      lamp.position.set(0, 3.16, 0);
      arch.add(lamp);
      lights.push(lamp);
      arch.position.set(mx, 0, z);
      arch.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
      scene.add(arch);
    }
    // Reject bin beside the last station: diverted parts land here.
    const binZ = z + (li === 0 ? -1.9 : 1.9);
    const bin = new Group();
    const binMat = new MeshStandardMaterial({ color: 0xe9ecef, roughness: 0.7 });
    const rim = new MeshStandardMaterial({ color: C.reject, roughness: 0.5 });
    const base = new Mesh(new BoxGeometry(1.6, 0.08, 1.2), binMat); base.position.y = 0.04; bin.add(base);
    for (const [w, d, x, zz, m] of [[1.6, 0.08, 0, 0.6, rim], [1.6, 0.08, 0, -0.6, rim], [0.08, 1.2, 0.8, 0, binMat], [0.08, 1.2, -0.8, 0, binMat]]) {
      const wall = new Mesh(new BoxGeometry(w, 0.55, d), m);
      wall.position.set(x, 0.3, zz);
      bin.add(wall);
    }
    bin.position.set(6.9, 0, binZ);
    bin.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
    scene.add(bin);
    return { spec, z, binZ, tex, lights, parts: [], phase: li * 0.47, running: true, good: 0, rejected: 0 };
  });

  const MAX = 160;
  const partMesh = new InstancedMesh(new BoxGeometry(0.42, 0.42, 0.42),
    new MeshStandardMaterial({ color: 0xffffff, roughness: 0.55, metalness: 0.05 }), MAX);
  partMesh.castShadow = true;
  partMesh.receiveShadow = true;
  const white = new Color(C.part), red = new Color(C.reject);
  for (let i = 0; i < MAX; i++) partMesh.setColorAt(i, white);
  scene.add(partMesh);
  const dummy = new Object3D();
  const GAP = 1.15, INSPECT_X = 5.9;

  function spawn(line, x) {
    line.parts.push({ x, reject: rng() > line.spec.quality, off: 0 });
  }
  // Pre-fill the belts so the first frame already shows a working line.
  for (const line of lines) for (let x = X0; x < X1 - 0.6; x += GAP) spawn(line, x);

  let clock = 0;
  function step(dt) {
    clock += dt;
    let n = 0;
    for (const line of lines) {
      const cyc = ((clock / DISPLAY.stopCycle) + line.phase) % 1;
      line.running = cyc < line.spec.availability;
      const v = line.running ? DISPLAY.beltSpeed * line.spec.performance : 0;
      line.tex.offset.x -= (v * dt) / (LEN / 32);
      const lampColor = line.running ? C.run : C.stop;
      for (const l of line.lights) { l.material.color.setHex(lampColor); l.material.emissive.setHex(lampColor); }
      for (const p of line.parts) {
        if (p.reject && p.x >= INSPECT_X) {
          p.off = Math.min(1, p.off + dt * 1.6);   // slide sideways into the bin
          if (p.off >= 1 && !p.counted) { p.counted = true; line.rejected++; p.landed = clock; }
        } else {
          p.x += v * dt;
        }
      }
      line.parts = line.parts.filter((p) => {
        if (!p.reject && p.x > X1 + 0.4) { line.good++; return false; }
        return !(p.reject && p.landed && clock - p.landed > 6);
      });
      const last = line.parts.filter((p) => !(p.reject && p.x >= INSPECT_X)).reduce((m, p) => Math.min(m, p.x), Infinity);
      if (line.running && (last === Infinity || last > X0 + GAP)) spawn(line, X0);
      for (const p of line.parts) {
        if (n >= MAX) break;
        const zOff = p.reject && p.x >= INSPECT_X ? MathUtils.lerp(0, line.binZ - line.z, p.off) : 0;
        const y = p.reject && p.x >= INSPECT_X ? MathUtils.lerp(BELT_Y + 0.3, 0.32, p.off * p.off) : BELT_Y + 0.3;
        const x = p.reject && p.x >= INSPECT_X ? INSPECT_X + p.off * 1.0 : p.x;
        dummy.position.set(x, y, line.z + zOff);
        dummy.rotation.set(0, p.off * 1.2, p.off * 0.6);
        dummy.updateMatrix();
        partMesh.setMatrixAt(n, dummy.matrix);
        partMesh.setColorAt(n, p.reject && p.x >= INSPECT_X - 1.5 ? red : white);
        n++;
      }
    }
    partMesh.count = n;
    partMesh.instanceMatrix.needsUpdate = true;
    if (partMesh.instanceColor) partMesh.instanceColor.needsUpdate = true;
  }

  camera.updateMatrixWorld();
  const box = [];
  for (const x of [-12, 12]) for (const y of [-0.3, 3.4]) for (const z of [-7, 7]) box.push(new Vector3(x, y, z).applyMatrix4(camera.matrixWorldInverse));
  const bx = Math.max(...box.map((v) => Math.abs(v.x))), by0 = Math.min(...box.map((v) => v.y)), by1 = Math.max(...box.map((v) => v.y));
  const cyv = (by0 + by1) / 2, hy = (by1 - by0) / 2;
  function frame(aspect, zoom) {
    let h = hy * 1.08, w = h * aspect;
    if (w < bx * 1.06) { w = bx * 1.06; h = w / aspect; }
    h /= zoom; w /= zoom;
    Object.assign(camera, { left: -w, right: w, top: cyv + h, bottom: cyv - h });
    camera.updateProjectionMatrix();
  }
  return { scene, camera, step, frame, lines, state: { zoom: 1 } };
}

// ---------------------------------------------------------------------------
// F1 scene
function buildF1(f1, envMap) {
  const scene = new Scene();
  scene.environment = envMap;
  const camera = new PerspectiveCamera(26, 1, 1, 2000);

  scene.add(new HemisphereLight(0xffffff, 0xdfe3e8, 1.0));
  const sun = new DirectionalLight(0xffffff, 2.2);
  sun.position.set(-18, 120, 30);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -75, right: 75, top: 75, bottom: -75, near: 10, far: 260 });
  sun.shadow.radius = 5;
  sun.shadow.bias = -0.0006;
  scene.add(sun);

  const ground = new Mesh(new PlaneGeometry(400, 400), new ShadowMaterial({ opacity: 0.1 }));
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  const ext = f1.track.extent_dm;
  const plinth = new Mesh(new BoxGeometry(ext[0] / 100 + 9, 0.9, ext[1] / 100 + 9),
    new MeshStandardMaterial({ color: 0xf7f8fa, roughness: 0.55, metalness: 0 }));
  plinth.position.y = 0.45;
  plinth.castShadow = plinth.receiveShadow = true;
  scene.add(plinth);
  const S = DISPLAY.trackScale, E = DISPLAY.elevation, BASE = 1.2;
  const toV = (p) => new Vector3(p[0] * S, BASE + p[2] * S * E, -p[1] * S);
  const centre = f1.track.points.map(toV);
  const N = centre.length;

  // Ribbon: asphalt top surface plus resin side walls down to the ground,
  // so the circuit reads as a machined model whose wall height is the real elevation.
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
      if (d < best) { best = d; sp = s[3]; }
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
  const racingGeo = new LineSegmentsGeometry().setPositions(segPos).setColors(segCol);
  const racingMat = new LineMaterial({ vertexColors: true, linewidth: 4, worldUnits: false });
  scene.add(new LineSegments2(racingGeo, racingMat));

  // Cars: a body and a nose, oriented along the heading. Not a model of any real car.
  const carColours = [C.auto, C.graphite, C.slate];
  const cars = f1.cars.map((car, ci) => {
    const g = new Group();
    const mat = new MeshStandardMaterial({ color: carColours[ci], roughness: 0.35, metalness: 0.3 });
    const body = new Mesh(new BoxGeometry(0.42, 0.14, 0.2), mat);
    const nose = new Mesh(new ConeGeometry(0.07, 0.26, 12), mat);
    nose.rotation.z = -Math.PI / 2;
    nose.position.x = 0.33;
    const wing = new Mesh(new BoxGeometry(0.06, 0.08, 0.26), mat);
    wing.position.set(-0.22, 0.08, 0);
    g.add(body, nose, wing);
    g.scale.setScalar(DISPLAY.carScale);
    g.traverse((o) => { if (o.isMesh) o.castShadow = true; });
    scene.add(g);
    const segs = Math.round(DISPLAY.trailSeconds * f1.sample_hz * 2);
    const tGeo = new LineSegmentsGeometry().setPositions(new Float32Array(segs * 6)).setColors(new Float32Array(segs * 6));
    const tMat = new LineMaterial({ vertexColors: true, linewidth: 3, worldUnits: false, transparent: true });
    const trail = new LineSegments2(tGeo, tMat);
    trail.frustumCulled = false;
    scene.add(trail);
    return { car, g, trail, tGeo, segs, colour: new Color(carColours[ci]) };
  });

  const total = lead.samples.length / f1.sample_hz;
  const tmp = new Vector3(), tmp2 = new Vector3();
  function sampleAt(car, t) {
    const s = car.samples, k = t * f1.sample_hz;
    const i = Math.min(Math.floor(k), s.length - 2), f = k - i;
    const a = s[i], b = s[i + 1];
    return {
      x: (a[0] + (b[0] - a[0]) * f) * S,
      y: BASE + (a[2] + (b[2] - a[2]) * f) * S * E + 0.2,
      z: -(a[1] + (b[1] - a[1]) * f) * S,
      speed: Math.round(a[3] + (b[3] - a[3]) * f), gear: a[4], lap: a[7],
    };
  }
  let t = 0;
  const readout = [];
  function step(dt) {
    const span = total - 0.6;
    t = (((t + dt) % span) + span) % span;
    readout.length = 0;
    for (const c of cars) {
      const p = sampleAt(c.car, t), q = sampleAt(c.car, Math.min(t + 0.25, total - 0.6));
      c.g.position.set(p.x, p.y, p.z);
      c.g.rotation.y = -Math.atan2(q.z - p.z, q.x - p.x);
      const pos = c.tGeo.attributes.instanceStart.data.array;
      const col = c.tGeo.attributes.instanceColorStart.data.array;
      for (let k = 0; k < c.segs; k++) {
        const ta = Math.max(0, t - DISPLAY.trailSeconds * (1 - k / c.segs));
        const tb = Math.max(0, t - DISPLAY.trailSeconds * (1 - (k + 1) / c.segs));
        const a = sampleAt(c.car, ta), b = sampleAt(c.car, tb);
        pos.set([a.x, a.y - 0.12, a.z, b.x, b.y - 0.12, b.z], k * 6);
        const fa = k / c.segs, fb = (k + 1) / c.segs;
        col.set([1 - (1 - c.colour.r) * fa, 1 - (1 - c.colour.g) * fa, 1 - (1 - c.colour.b) * fa,
          1 - (1 - c.colour.r) * fb, 1 - (1 - c.colour.g) * fb, 1 - (1 - c.colour.b) * fb], k * 6);
      }
      c.tGeo.attributes.instanceStart.data.needsUpdate = true;
      c.tGeo.attributes.instanceColorStart.data.needsUpdate = true;
      readout.push({ code: c.car.code, ...p, world: tmp.set(p.x, p.y + 0.9, p.z).clone() });
    }
  }
  const lines = [racingMat, ...cars.map((c) => c.trail.material)];
  const centreY = BASE + 1;
  const hx = ext[0] / 200 + 4.5, hz = ext[1] / 200 + 4.5;
  const corners = [];
  for (const x of [-hx, hx]) for (const y of [0, 3]) for (const z of [-hz, hz]) corners.push(new Vector3(x, y, z));
  const ndc = new Vector3();
  function frame(aspect, s) {
    camera.aspect = aspect;
    camera.updateProjectionMatrix();
    const el = MathUtils.degToRad(s.elevation), az = s.azimuth;
    let dist = 200;
    for (let it = 0; it < 3; it++) {
      camera.position.set(Math.sin(az) * Math.cos(el) * dist, Math.sin(el) * dist, Math.cos(az) * Math.cos(el) * dist);
      camera.lookAt(tmp2.set(0, 1.5, 0));
      camera.updateMatrixWorld();
      let m = 0;
      for (const c of corners) { ndc.copy(c).project(camera); m = Math.max(m, Math.abs(ndc.x), Math.abs(ndc.y)); }
      dist *= m / 0.93;
    }
    dist *= s.distance;
    camera.position.set(Math.sin(az) * Math.cos(el) * dist, Math.sin(el) * dist, Math.cos(az) * Math.cos(el) * dist);
    camera.lookAt(tmp2.set(0, 1.5, 0));
  }
  return { scene, camera, step, frame, lines, readout, speedRange: [vMin, vMax], state: { distance: 1, elevation: 42, azimuth: 1.15 } };
}

// ---------------------------------------------------------------------------
export async function mountHero(root) {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const canvas = root.querySelector("canvas");
  const res = await fetch("/assets/hero/hero-data.json");
  if (!res.ok) throw new Error(`hero data ${res.status}`);
  const data = await res.json();

  const renderer = new WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.outputColorSpace = SRGBColorSpace;
  renderer.toneMapping = ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = PCFShadowMap;
  renderer.setClearColor(0x000000, 0);
  const pmrem = new PMREMGenerator(renderer);
  const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

  const ind = buildIndustrial(data.industrial, env);
  const f1 = buildF1(data.f1, env);

  // Static facts in the captions come from the same payload as the scene.
  const set = (sel, txt) => { const el = root.querySelector(sel); if (el) el.textContent = txt; };
  set("[data-oee]", pct(data.industrial.oee_weighted));
  set("[data-speed-range]", `de ${f1.speedRange[0]} a ${f1.speedRange[1]} km/h`);
  const lineRows = data.industrial.lines.map((l, i) => root.querySelector(`[data-line="${i}"]`));
  data.industrial.lines.forEach((l, i) => {
    const row = lineRows[i];
    if (!row) return;
    row.querySelector("[data-a]").textContent = pct(l.availability);
    row.querySelector("[data-p]").textContent = pct(l.performance);
    row.querySelector("[data-q]").textContent = pct(l.quality);
  });
  const carRows = data.f1.cars.map((c) => root.querySelector(`[data-car="${c.code}"]`));
  const statusEls = data.industrial.lines.map((_, i) => root.querySelector(`[data-status="${i}"]`));
  const lapEl = root.querySelector("[data-lap]");
  const tags = data.f1.cars.map((c) => {
    const el = document.createElement("span");
    el.className = "car-tag";
    el.setAttribute("aria-hidden", "true");
    root.querySelector(".stage-view").append(el);
    return el;
  });

  // Split between the two viewports, 0..1 = share of the industrial side.
  const split = { value: 0.5, target: 0.5 };
  const halves = [...root.querySelectorAll(".half")];
  const vertical = () => matchMedia("(max-width: 720px)").matches;
  halves.forEach((h, i) => {
    const on = () => { if (!vertical()) split.target = i === 0 ? 0.62 : 0.38; };
    const off = () => { split.target = 0.5; };
    h.addEventListener("pointerenter", on);
    h.addEventListener("focusin", on);
    h.addEventListener("pointerleave", off);
    h.addEventListener("focusout", off);
  });

  const view = root.querySelector(".stage-view");
  let W = 0, H = 0;
  const resize = () => {
    const r = view.getBoundingClientRect();
    W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
    renderer.setSize(W, H, false);
    for (const m of f1.lines) m.resolution.set(W, H);
  };
  new ResizeObserver(resize).observe(view);
  resize();

  const proj = new Vector3();
  let lastDom = 0;
  function render(dt, now) {
    split.value += (split.target - split.value) * (reduce ? 1 : 1 - Math.exp(-dt * 7));
    root.style.setProperty("--split", split.value.toFixed(4));
    ind.step(dt);
    f1.step(dt);
    if (!reduce) f1.state.azimuth += dt * ((Math.PI * 2) / 240);   // one slow orbit per replay
    const v = vertical();
    const a = v ? { x: 0, y: H / 2, w: W, h: H / 2 } : { x: 0, y: 0, w: W * split.value, h: H };
    const b = v ? { x: 0, y: 0, w: W, h: H / 2 } : { x: a.w, y: 0, w: W - a.w, h: H };
    ind.frame(a.w / a.h, ind.state.zoom);
    f1.frame(b.w / b.h, f1.state);
    renderer.setScissorTest(true);
    for (const [vp, s] of [[a, ind], [b, f1]]) {
      renderer.setViewport(vp.x, vp.y, vp.w, vp.h);
      renderer.setScissor(vp.x, vp.y, vp.w, vp.h);
      renderer.render(s.scene, s.camera);
    }
    // Car tags follow the projected positions inside the F1 viewport; stacked when they collide.
    const placed = f1.readout.map((r, i) => {
      proj.copy(r.world).project(f1.camera);
      return { i, x: b.x + (proj.x + 1) / 2 * b.w, y: (H - b.y - b.h) + (1 - proj.y) / 2 * b.h, off: proj.z > 1 };
    }).sort((p, q) => q.y - p.y);
    placed.forEach((p, k) => {
      for (let j = 0; j < k; j++) {
        const o = placed[j];
        if (Math.abs(o.x - p.x) < 62 && Math.abs(o.y - p.y) < 22) p.y = o.y - 22;
      }
      const tag = tags[p.i];
      tag.style.transform = `translate(${p.x.toFixed(1)}px, ${p.y.toFixed(1)}px)`;
      tag.hidden = p.off || p.x < b.x || p.x > b.x + b.w;
    });
    if (now - lastDom > 120) {
      lastDom = now;
      f1.readout.forEach((r, i) => {
        tags[i].textContent = v ? `${r.code} ${r.speed}` : r.code;
        const row = carRows[i];
        if (row) {
          row.querySelector("[data-v]").textContent = `${r.speed} km/h`;
          row.querySelector("[data-g]").textContent = `${r.gear}ª`;
        }
      });
      const lap = f1.readout[0] && f1.readout[0].lap;
      if (lapEl && lap) lapEl.textContent = `Volta ${lap} de ${data.f1.race_laps}`;
      ind.lines.forEach((l, i) => {
        const st = statusEls[i];
        if (st) {
          st.textContent = l.running ? "em operação" : "parada";
          st.dataset.state = l.running ? "run" : "stop";
        }
      });
    }
  }

  // One authored moment: the name opens like a gauge, the models settle, captions follow.
  const title = document.querySelector(".hero-name");
  const name = { w: reduce ? 100 : 62 };
  const applyName = () => {
    if (!title) return;
    const vh = innerHeight || 800;
    const scrollW = 112 - Math.min(1, scrollY / (vh * 0.6)) * 42;
    title.style.fontStretch = `${Math.min(name.w, scrollW).toFixed(1)}%`;
  };
  if (!reduce) addEventListener("scroll", applyName, { passive: true });

  let running = true, visible = true, last = performance.now();
  const loop = (now) => {
    if (!running) return;
    const dt = Math.min(0.05, Math.max(0, (now - last) / 1000));
    last = now;
    if (visible && !document.hidden) render(dt, now);
    requestAnimationFrame(loop);
  };

  canvas.addEventListener("webglcontextlost", (e) => { e.preventDefault(); running = false; root.dataset.state = "fallback"; });
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(root);

  if (reduce) {
    ind.step(0.016);
    f1.step(30);           // a representative, fully static frame
    render(0, performance.now());
    root.dataset.state = "ready";
    return;
  }

  ind.state.zoom = 0.82;
  Object.assign(f1.state, { distance: 1.3, elevation: 76 });
  render(0.016, performance.now());
  root.dataset.state = "ready";
  const tl = gsap.timeline({ defaults: { ease: "expo.out" } });
  tl.to(canvas, { opacity: 1, duration: 0.6, ease: "power1.out" }, 0)
    .to(name, { w: 112, duration: 1.6, onUpdate: applyName }, 0)
    .to(ind.state, { zoom: 1, duration: 1.8 }, 0.1)
    .to(f1.state, { distance: 1, elevation: 42, duration: 2.2 }, 0.1)
    .from(root.querySelectorAll(".cap > *"), { y: 14, opacity: 0, duration: 0.9, stagger: 0.06 }, 0.5);
  requestAnimationFrame(loop);
}
