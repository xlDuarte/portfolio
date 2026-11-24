// Industrial view: two production lines driven by the OEE case-study data (synthetic).
//   availability -> the belt stops for (1 - A) of every cycle
//   performance  -> belt speed
//   quality      -> share of parts the inspection station rejects; a pneumatic pusher throws
//                   them into the bin, where they fall as rigid bodies
// Station 2 welds every part that passes: sparks are hot steel droplets (physics.js).
// Scene scale: 1 unit = 0.5 m.
import {
  BoxGeometry, CanvasTexture, Color, CylinderGeometry, DirectionalLight, Group, HemisphereLight,
  InstancedMesh, Mesh, MeshStandardMaterial, Object3D, OrthographicCamera, PointLight,
  RepeatWrapping, Scene, SphereGeometry, SRGBColorSpace, Vector3,
} from "three";
import { RigidBody, SparkField, STEEL_SPARK, G0 } from "../scene/physics.js";
import { SparkView, BLACKBODY } from "../scene/sparks.js";
import { C, mulberry32 } from "./palette.js";

const UPM = 2;                       // scene units per metre
const LEN = 17, X0 = -LEN / 2, X1 = LEN / 2, BELT_Y = 0.95, BELT_TOP = BELT_Y + 0.09;
const GAP = 1.15, WELD_X = 0, INSPECT_X = 5.2, PUSH_X = 5.9;
export const DISPLAY = { beltSpeed: 1.7, stopCycle: 24 };

export function buildIndustrial(data, env) {
  const scene = new Scene();
  scene.environment = env;
  scene.background = new Color(C.wash);
  const camera = new OrthographicCamera(-10, 10, 10, -10, 0.1, 200);
  camera.position.set(30, 25, 30);
  camera.lookAt(0, 0.6, 0);
  const base = camera.position.clone();

  scene.add(new HemisphereLight(0xffffff, 0xd8dde3, 0.85));
  const sun = new DirectionalLight(0xffffff, 1.9);
  sun.position.set(-8, 18, 10);
  sun.castShadow = true;
  Object.assign(sun.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 50 });
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.02;
  scene.add(sun);

  const floor = new Mesh(new BoxGeometry(24, 0.3, 14), new MeshStandardMaterial({ color: C.concrete, roughness: 0.92 }));
  floor.position.y = -0.15;
  floor.receiveShadow = true;
  scene.add(floor);
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
  const rubber = new MeshStandardMaterial({ color: 0x2a2e33, roughness: 0.7 });

  const canvas = document.createElement("canvas");
  canvas.width = 64; canvas.height = 8;
  const g = canvas.getContext("2d");
  g.fillStyle = "#3a4048"; g.fillRect(0, 0, 64, 8);
  g.fillStyle = "#4a515a"; g.fillRect(0, 0, 6, 8);
  const beltTex = new CanvasTexture(canvas);
  beltTex.colorSpace = SRGBColorSpace;
  beltTex.wrapS = beltTex.wrapT = RepeatWrapping;
  beltTex.repeat.set(32, 1);

  const rng = mulberry32(20240302);
  const colliders = [{ min: [-12, -1, -7], max: [12, 0, 7] }];

  const lines = data.lines.map((spec, li) => {
    const z = li === 0 ? -2.6 : 2.6;
    const side = li === 0 ? -1 : 1;                    // bins sit on the outer side
    const tex = beltTex.clone();
    tex.needsUpdate = true;
    const belt = new Mesh(new BoxGeometry(LEN, 0.18, 1.3),
      [steelDark, steelDark, new MeshStandardMaterial({ map: tex, roughness: 0.8 }), steelDark, steelDark, steelDark]);
    belt.position.set(0, BELT_Y, z);
    belt.castShadow = belt.receiveShadow = true;
    scene.add(belt);
    colliders.push({ min: [X0, BELT_Y - 0.09, z - 0.65], max: [X1, BELT_TOP, z + 0.65] });
    for (let x = X0 + 0.6; x <= X1; x += 2.8) {
      for (const dz of [-0.55, 0.55]) {
        const leg = new Mesh(new BoxGeometry(0.12, BELT_Y, 0.12), steelDark);
        leg.position.set(x, BELT_Y / 2, z + dz);
        leg.castShadow = true;
        scene.add(leg);
      }
    }
    const lights = [];
    for (const mx of [-5.2, WELD_X, INSPECT_X]) {
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
        new MeshStandardMaterial({ color: C.run, emissive: C.run, emissiveIntensity: 1.6, roughness: 0.3 }));
      lamp.position.set(0, 3.16, 0);
      arch.add(lamp);
      lights.push(lamp);
      arch.position.set(mx, 0, z);
      arch.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
      scene.add(arch);
    }
    // Welding torch hanging from station 2, with an arc flash light.
    const torch = new Group();
    const hose = new Mesh(new CylinderGeometry(0.06, 0.06, 0.8, 12), rubber);
    hose.position.y = 1.8;
    const nozzle = new Mesh(new CylinderGeometry(0.05, 0.11, 0.3, 16), steelDark);
    nozzle.position.y = 1.3;
    const arcGlow = new Mesh(new SphereGeometry(0.07, 12, 8), new MeshStandardMaterial({ color: 0x000000, emissive: 0xbfd6ff, emissiveIntensity: 0 }));
    arcGlow.position.y = 1.13;
    torch.add(hose, nozzle, arcGlow);
    torch.position.set(WELD_X, 0, z);
    torch.traverse((o) => { if (o.isMesh) o.castShadow = true; });
    scene.add(torch);
    const arcLight = new PointLight(0xcfe0ff, 0, 7, 2);
    arcLight.position.set(WELD_X, BELT_TOP + 0.35, z);
    scene.add(arcLight);
    // Inspection laser: green line, flashes red on a reject.
    const laserMat = new MeshStandardMaterial({ color: 0x000000, emissive: 0x18c060, emissiveIntensity: 4 });
    const laser = new Mesh(new BoxGeometry(0.02, 0.02, 1.3), laserMat);
    laser.position.set(INSPECT_X, BELT_TOP + 0.55, z);
    scene.add(laser);
    // Pneumatic pusher on the inner side, throws rejects towards the bin.
    const pusherBody = new Mesh(new BoxGeometry(0.5, 0.35, 0.6), steel);
    pusherBody.position.set(PUSH_X, BELT_TOP + 0.2, z - side * 1.05);
    const ram = new Mesh(new BoxGeometry(0.42, 0.28, 0.12), panel);
    const ramRest = z - side * 0.7;
    ram.position.set(PUSH_X, BELT_TOP + 0.2, ramRest);
    for (const m of [pusherBody, ram]) { m.castShadow = true; scene.add(m); }
    // Reject bin
    const binZ = z + side * 1.95, binX = 6.9;
    const binMat = new MeshStandardMaterial({ color: 0xe9ecef, roughness: 0.7 });
    const rim = new MeshStandardMaterial({ color: C.reject, roughness: 0.5 });
    const binParts = [
      [1.6, 0.08, 1.2, 0, 0.04, 0, binMat], [1.6, 0.55, 0.08, 0, 0.3, 0.6, rim], [1.6, 0.55, 0.08, 0, 0.3, -0.6, rim],
      [0.08, 0.55, 1.2, 0.8, 0.3, 0, binMat], [0.08, 0.55, 1.2, -0.8, 0.3, 0, binMat],
    ];
    for (const [w, h, d, x, y, dz, m] of binParts) {
      const mesh = new Mesh(new BoxGeometry(w, h, d), m);
      mesh.position.set(binX + x, y, binZ + dz);
      mesh.castShadow = mesh.receiveShadow = true;
      scene.add(mesh);
      colliders.push({ min: [binX + x - w / 2, y - h / 2, binZ + dz - d / 2], max: [binX + x + w / 2, y + h / 2, binZ + dz + d / 2] });
    }
    const sparks = new SparkField(700, STEEL_SPARK);
    const sparkView = new SparkView(sparks, UPM, { intensity: 3, size: 4 });
    sparkView.addTo(scene);
    return { spec, z, side, tex, lights, parts: [], phase: li * 0.47, running: true, sparks, sparkView,
             arcLight, arcGlow, laserMat, ram, ramRest, ramT: 1, emitAcc: 0, welding: false };
  });

  const MAX = 160;
  const partGeo = new BoxGeometry(0.42, 0.42, 0.42);
  const partMesh = new InstancedMesh(partGeo, new MeshStandardMaterial({ color: 0xffffff, roughness: 0.55, metalness: 0.05 }), MAX);
  partMesh.castShadow = partMesh.receiveShadow = true;
  const white = new Color(C.part);
  for (let i = 0; i < MAX; i++) partMesh.setColorAt(i, white);
  scene.add(partMesh);
  const dummy = new Object3D();

  // Rejected parts become rigid bodies; a small pool of meshes shows them.
  const bodyMat = new MeshStandardMaterial({ color: C.reject, roughness: 0.5, metalness: 0.05 });
  const bodies = [];
  const pool = Array.from({ length: 14 }, () => {
    const m = new Mesh(partGeo, bodyMat);
    m.castShadow = m.receiveShadow = true;
    m.visible = false;
    scene.add(m);
    return m;
  });

  const spawn = (line, x) => line.parts.push({ x, reject: rng() > line.spec.quality, welded: false });
  for (const line of lines) for (let x = X0; x < X1 - 0.6; x += GAP) spawn(line, x);

  // Ground for sparks, in metres: belt top inside the belt footprint, floor elsewhere.
  const groundFor = (line) => (xm, zm) => {
    const x = xm * UPM, zz = zm * UPM;
    return (x > X0 && x < X1 && Math.abs(zz - line.z) < 0.65) ? BELT_TOP / UPM : 0;
  };
  const grounds = lines.map(groundFor);
  const tmpC = [0, 0, 0], seam = new Color(), hot = new Color();
  let clock = 0;

  function step(dt) {
    clock += dt;
    let n = 0;
    lines.forEach((line, li) => {
      const cyc = ((clock / DISPLAY.stopCycle) + line.phase) % 1;
      line.running = cyc < line.spec.availability;
      const v = line.running ? DISPLAY.beltSpeed * line.spec.performance : 0;
      line.tex.offset.x -= (v * dt) / (LEN / 32);
      const lampColor = line.running ? C.run : C.stop;
      for (const l of line.lights) { l.material.color.setHex(lampColor); l.material.emissive.setHex(lampColor); }
      for (const p of line.parts) p.x += v * dt;

      // Welding: active while a part sits under the torch and the line runs.
      line.welding = line.running && line.parts.some((p) => Math.abs(p.x - WELD_X) < 0.32);
      if (line.welding) {
        line.emitAcc += dt * 900;
        while (line.emitAcc >= 1) {
          line.emitAcc -= 1;
          const th = rng() * Math.PI * 2, up = 0.25 + rng() * 0.75, sp = 2 + rng() * 5;
          const hz = Math.sqrt(1 - up * up);
          line.sparks.emit(WELD_X / UPM, (BELT_TOP + 0.47) / UPM, line.z / UPM,
            Math.cos(th) * hz * sp, up * sp, Math.sin(th) * hz * sp, 1700 + rng() * 350);
        }
      }
      const flicker = line.welding ? 0.55 + 0.45 * Math.sin(clock * 91 + li * 3) * Math.sin(clock * 37) : 0;
      line.arcLight.intensity = line.welding ? 5 + 9 * Math.abs(flicker) : 0;
      line.arcGlow.material.emissiveIntensity = line.welding ? 14 + 10 * flicker : 0;
      line.sparks.step(dt, grounds[li]);
      line.sparkView.update();

      // Inspection + pusher
      let flash = false;
      line.parts = line.parts.filter((p) => {
        if (p.reject && p.x >= PUSH_X) {
          launch(line, p);
          return false;
        }
        if (p.reject && Math.abs(p.x - INSPECT_X) < 0.25) flash = true;
        return p.x <= X1 + 0.4;
      });
      line.laserMat.emissive.setHex(flash ? 0xff2a3a : 0x18c060);
      line.ramT = Math.min(1, line.ramT + dt * 3);
      const ext = Math.sin(Math.min(1, line.ramT * 2) * Math.PI) * 1.1;
      line.ram.position.z = line.ramRest + line.side * ext;

      const last = line.parts.reduce((m, p) => Math.min(m, p.x), Infinity);
      if (line.running && (last === Infinity || last > X0 + GAP)) spawn(line, X0);
      for (const p of line.parts) {
        if (n >= MAX) break;
        dummy.position.set(p.x, BELT_TOP + 0.21, line.z);
        dummy.rotation.set(0, 0, 0);
        dummy.updateMatrix();
        partMesh.setMatrixAt(n, dummy.matrix);
        // After welding the part carries a cooling seam glow (black-body colour).
        if (p.x > WELD_X && p.x < WELD_X + 2.4) {
          const T = 1500 - (p.x - WELD_X) * 520;
          const c = BLACKBODY.sample(T, tmpC);
          const k = Math.max(0, BLACKBODY.radiance(T, 1500)) * 0.35;
          partMesh.setColorAt(n, seam.setHex(C.part).lerp(hot.setRGB(c[0], c[1], c[2]), Math.min(0.8, k)));
        } else {
          partMesh.setColorAt(n, white);
        }
        n++;
      }
    });
    partMesh.count = n;
    partMesh.instanceMatrix.needsUpdate = true;
    if (partMesh.instanceColor) partMesh.instanceColor.needsUpdate = true;

    for (const b of bodies) {
      b.body.step(dt, colliders);
      if (b.body.sleeping) b.slept += dt;
    }
    while (bodies.length && (bodies[0].slept > 7 || bodies.length > pool.length)) {
      bodies.shift().mesh.visible = false;
    }
    for (const b of bodies) {
      b.mesh.position.set(...b.body.p);
      b.mesh.quaternion.set(...b.body.q);
      const fade = b.slept > 6.5 ? Math.max(0.01, 1 - (b.slept - 6.5) * 2) : 1;
      b.mesh.scale.setScalar(fade);
    }
  }

  function launch(line, p) {
    line.ramT = 0;
    const mesh = pool.find((m) => !m.visible) || bodies[0]?.mesh;
    if (!mesh) return;
    if (bodies.length && mesh === bodies[0].mesh) bodies.shift();
    mesh.visible = true;
    const v = line.running ? DISPLAY.beltSpeed * line.spec.performance : 0;
    const body = new RigidBody({
      position: [PUSH_X, BELT_TOP + 0.24, line.z], radius: 0.24, side: 0.42, gravity: G0 * UPM,
      velocity: [v * 0.6, 2.4 + rng() * 0.6, line.side * (3.0 + rng() * 0.6)],
      spin: [(rng() - 0.5) * 9, (rng() - 0.5) * 6, (rng() - 0.5) * 9], restitution: 0.22, friction: 0.6,
    });
    bodies.push({ body, mesh, slept: 0 });
  }

  // Fit the floor slab inside the buffer; `fit` is the share of the width it must occupy.
  camera.updateMatrixWorld();
  const box = [];
  for (const x of [-12, 12]) for (const y of [-0.3, 3.4]) for (const z of [-7, 7]) box.push(new Vector3(x, y, z).applyMatrix4(camera.matrixWorldInverse));
  const bx = Math.max(...box.map((v) => Math.abs(v.x))), by0 = Math.min(...box.map((v) => v.y)), by1 = Math.max(...box.map((v) => v.y));
  const cyv = (by0 + by1) / 2, hy = (by1 - by0) / 2;
  const state = { zoom: 1, fit: 0.8, parallax: [0, 0] };
  function frame(aspect) {
    let h = hy * 1.08, w = h * aspect;
    const needW = (bx * 1.04) / state.fit;
    if (w < needW) { w = needW; h = w / aspect; }
    h /= state.zoom; w /= state.zoom;
    camera.position.set(base.x + state.parallax[0] * 1.6, base.y + state.parallax[1] * 1.2, base.z - state.parallax[0] * 1.6);
    camera.lookAt(0, 0.6, 0);
    Object.assign(camera, { left: -w, right: w, top: cyv + h, bottom: cyv - h });
    camera.updateProjectionMatrix();
  }
  const setShadowSize = (s) => { sun.shadow.mapSize.set(s, s); sun.shadow.map?.dispose(); sun.shadow.map = null; };
  const tint = (amount) => scene.background.setHex(C.wash).lerp(new Color(C.indWash), amount);
  return { scene, camera, step, frame, setShadowSize, tint, lines, state, aoRadius: 0.5, aoIntensity: 0.9 };
}

