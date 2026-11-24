// Photo-studio set for a single car: turntable plinth, key/rim lights, soft contact shadow.
import {
  Color, CylinderGeometry, DirectionalLight, HemisphereLight, MathUtils, Mesh, MeshStandardMaterial,
  PerspectiveCamera, PlaneGeometry, Scene, ShadowMaterial, SpotLight, Vector3,
} from "three";
import { Turntable } from "../scene/physics.js";
import { C } from "../hero/palette.js";

export function studio(env, { washTint = C.indWash, radius = 3.6, camDist = 11, height = 2.6 } = {}) {
  const scene = new Scene();
  scene.environment = env;
  scene.background = new Color(C.wash);
  const camera = new PerspectiveCamera(30, 1, 0.1, 200);

  scene.add(new HemisphereLight(0xffffff, 0xd9dde2, 0.7));
  const key = new DirectionalLight(0xffffff, 2.2);
  key.position.set(-6, 10, 6);
  key.castShadow = true;
  Object.assign(key.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 30 });
  key.shadow.bias = -0.0003;
  key.shadow.normalBias = 0.02;
  scene.add(key);
  const rim = new SpotLight(0xffffff, 40, 30, MathUtils.degToRad(35), 0.6, 1.6);
  rim.position.set(5, 6, -7);
  scene.add(rim, rim.target);

  const ground = new Mesh(new PlaneGeometry(60, 60), new ShadowMaterial({ opacity: 0.12 }));
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);
  const plinth = new Mesh(new CylinderGeometry(radius, radius + 0.1, 0.3, 96),
    new MeshStandardMaterial({ color: 0xf7f8fa, roughness: 0.4, metalness: 0.05 }));
  plinth.position.y = 0.15;
  plinth.receiveShadow = plinth.castShadow = true;
  scene.add(plinth);
  const ring = new Mesh(new CylinderGeometry(radius + 0.02, radius + 0.02, 0.012, 96, 1, true),
    new MeshStandardMaterial({ color: 0x9aa3ad, roughness: 0.5 }));
  ring.position.y = 0.3;
  scene.add(ring);

  const table = new Turntable();
  const look = new Vector3(0, 0.75, 0);
  const state = { fit: 1, parallax: [0, 0], distance: 1, elevation: 16, azimuth: 0.7 };
  function frame(aspect) {
    camera.aspect = aspect;
    const fitW = Math.min(1, aspect / 1.6) * state.fit;              // keep the car width in view
    const d = (camDist / Math.max(0.55, fitW)) * state.distance;
    const el = MathUtils.degToRad(state.elevation + state.parallax[1] * 4);
    const az = state.azimuth + state.parallax[0] * 0.15;
    camera.position.set(Math.sin(az) * Math.cos(el) * d, height * 0.4 + Math.sin(el) * d, Math.cos(az) * Math.cos(el) * d);
    camera.lookAt(look);
    camera.updateProjectionMatrix();
  }
  const setShadowSize = (s) => { key.shadow.mapSize.set(s, s); key.shadow.map?.dispose(); key.shadow.map = null; };
  const tint = (a) => scene.background.setHex(C.wash).lerp(new Color(washTint), a);
  return { scene, camera, frame, state, table, setShadowSize, tint, plinthTop: 0.3, aoRadius: 0.8, aoIntensity: 0.9 };
}

/** Drag-to-spin with inertia: pointer velocity becomes angular momentum on release. */
export function bindSpin(el, table, getRect) {
  let down = false, lastX = 0, lastT = 0, vel = 0, travel = 0;
  el.addEventListener("pointerdown", (e) => {
    if (e.button !== 0 || e.pointerType === "touch") return;   // touch keeps native scrolling
    down = true; lastX = e.clientX; lastT = performance.now(); vel = 0; travel = 0;
  });
  // A drag must not turn into a click on the link underneath.
  el.addEventListener("click", (e) => { if (travel > 6) { e.preventDefault(); e.stopPropagation(); } travel = 0; }, true);
  el.addEventListener("pointermove", (e) => {
    if (!down) return;
    const now = performance.now(), dx = e.clientX - lastX, w = getRect().width || 1;
    travel += Math.abs(dx);
    const dAng = (dx / w) * Math.PI * 1.5;
    table.theta += dAng;
    vel = 0.7 * vel + 0.3 * (dAng / Math.max(0.008, (now - lastT) / 1000));
    lastX = e.clientX; lastT = now;
  });
  const up = () => { if (!down) return; down = false; table.omega = 0; table.impulse(vel * table.I); };
  el.addEventListener("pointerup", up);
  el.addEventListener("pointercancel", up);
  el.addEventListener("pointerleave", up);
  return { held: () => down };
}
