// Procedural, generic race cars (not replicas of any real car). 1 unit = 1 metre.
// Each model exposes `body` (sprung mass, for pitch/roll), `wheels` and `discs`.
import {
  BoxGeometry, ConeGeometry, CylinderGeometry, ExtrudeGeometry, Group, Mesh, MeshPhysicalMaterial,
  MeshStandardMaterial, Shape, TorusGeometry,
} from "three";

const tyreMat = () => new MeshStandardMaterial({ color: 0x17191c, roughness: 0.88 });
const rimMat = () => new MeshStandardMaterial({ color: 0x8c939b, metalness: 0.85, roughness: 0.3 });

function wheel(radius, width) {
  const g = new Group();
  const tyre = new Mesh(new CylinderGeometry(radius, radius, width, 40), tyreMat());
  tyre.rotation.x = Math.PI / 2;
  const rim = new Mesh(new CylinderGeometry(radius * 0.62, radius * 0.62, width * 1.02, 24), rimMat());
  rim.rotation.x = Math.PI / 2;
  const disc = new Mesh(new CylinderGeometry(radius * 0.42, radius * 0.42, width * 0.4, 24),
    new MeshStandardMaterial({ color: 0x2a2a2a, roughness: 0.6, emissive: 0x000000 }));
  disc.rotation.x = Math.PI / 2;
  g.add(tyre, rim, disc);
  return { g, tyre, disc };
}

function shadowAll(root) {
  root.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
}

/** Generic GT coupé: extruded side profile, greenhouse, splitter, wing. */
export function gtCar({ paint = 0xd5d9de, accent = 0xb8122b } = {}) {
  const root = new Group();
  const body = new Group();
  const L = 4.6, Wd = 1.92;
  const paintMat = new MeshPhysicalMaterial({ color: paint, metalness: 0.75, roughness: 0.28, clearcoat: 1, clearcoatRoughness: 0.08 });
  const black = new MeshStandardMaterial({ color: 0x15171a, roughness: 0.6 });
  const glass = new MeshPhysicalMaterial({ color: 0x1c2430, metalness: 0.1, roughness: 0.05, transmission: 0, clearcoat: 1 });

  // Side profile: low nose, long hood, fastback roof, short tail with ducktail lip.
  const prof = new Shape();
  prof.moveTo(0, 0.26);
  prof.lineTo(0.02, 0.46);
  prof.quadraticCurveTo(0.12, 0.62, 0.55, 0.68);
  prof.quadraticCurveTo(1.15, 0.74, 1.6, 0.82);
  prof.lineTo(L - 1.0, 0.86);
  prof.quadraticCurveTo(L - 0.3, 0.9, L - 0.12, 0.82);
  prof.lineTo(L, 0.66);
  prof.lineTo(L, 0.26);
  prof.closePath();
  const shell = new Mesh(new ExtrudeGeometry(prof, { depth: Wd, bevelEnabled: true, bevelSize: 0.14, bevelThickness: 0.16, bevelSegments: 6, curveSegments: 16 }), paintMat);
  shell.position.set(-L / 2, 0, -Wd / 2);
  body.add(shell);

  const gh = new Shape();
  gh.moveTo(1.6, 0.82);
  gh.quadraticCurveTo(1.95, 1.12, 2.35, 1.2);
  gh.quadraticCurveTo(2.9, 1.27, 3.25, 1.2);
  gh.quadraticCurveTo(3.55, 1.12, L - 1.0, 0.86);
  gh.closePath();
  const cabin = new Mesh(new ExtrudeGeometry(gh, { depth: Wd - 0.36, bevelEnabled: true, bevelSize: 0.06, bevelThickness: 0.06, bevelSegments: 3 }), glass);
  cabin.position.set(-L / 2, 0, -(Wd - 0.36) / 2);
  body.add(cabin);

  const stripe = new Mesh(new BoxGeometry(L * 0.98, 0.06, 0.02), new MeshStandardMaterial({ color: accent, roughness: 0.4 }));
  stripe.position.set(0, 0.5, Wd / 2 + 0.09);
  const stripe2 = stripe.clone(); stripe2.position.z = -Wd / 2 - 0.09;
  const splitter = new Mesh(new BoxGeometry(0.35, 0.04, Wd + 0.1), black);
  splitter.position.set(-L / 2 + 0.05, 0.2, 0);
  const wing = new Mesh(new BoxGeometry(0.32, 0.04, Wd - 0.1), black);
  wing.position.set(L / 2 - 0.25, 1.3, 0);
  body.add(stripe, stripe2, splitter, wing);
  for (const z of [-0.55, 0.55]) {
    const up = new Mesh(new BoxGeometry(0.06, 0.42, 0.04), black);
    up.position.set(L / 2 - 0.3, 1.08, z);
    body.add(up);
  }
  root.add(body);

  const wheels = [], discs = [];
  // Facing −x with +y up, the car's left side is +z. Order: FL, FR, RL, RR.
  const pos = [[-L / 2 + 0.95, Wd / 2 - 0.05], [-L / 2 + 0.95, -Wd / 2 + 0.05], [L / 2 - 0.95, Wd / 2 - 0.05], [L / 2 - 0.95, -Wd / 2 + 0.05]];
  for (const [x, z] of pos) {
    const w = wheel(0.34, 0.3);
    w.g.position.set(x, 0.34, z);
    root.add(w.g);
    wheels.push(w); discs.push(w.disc);
  }
  shadowAll(root);
  return { root, body, wheels, discs, length: L, width: Wd, frontSign: -1 };
}

/** Generic open-wheel single-seater with halo. */
export function openWheeler({ paint = 0x1c2128, accent = 0xb8122b } = {}) {
  const root = new Group();
  const body = new Group();
  const paintMat = new MeshPhysicalMaterial({ color: paint, metalness: 0.5, roughness: 0.32, clearcoat: 1, clearcoatRoughness: 0.1 });
  const accentMat = new MeshStandardMaterial({ color: accent, roughness: 0.35, metalness: 0.2 });
  const carbon = new MeshStandardMaterial({ color: 0x141619, roughness: 0.45, metalness: 0.3 });
  const add = (m, x, y, z) => { m.position.set(x, y, z); body.add(m); return m; };
  add(new Mesh(new BoxGeometry(2.6, 0.42, 0.62), paintMat), 0, 0.42, 0);              // monocoque + engine cover
  add(new Mesh(new BoxGeometry(1.5, 0.34, 1.5), paintMat), 0.35, 0.36, 0);             // sidepods
  const nose = add(new Mesh(new ConeGeometry(0.2, 1.7, 16), accentMat), -2.05, 0.34, 0);
  nose.rotation.z = Math.PI / 2;
  add(new Mesh(new BoxGeometry(0.5, 0.05, 1.95), carbon), -2.75, 0.12, 0);              // front wing
  add(new Mesh(new BoxGeometry(0.45, 0.12, 1.05), carbon), 2.45, 0.95, 0);               // rear wing
  add(new Mesh(new BoxGeometry(0.1, 0.5, 0.06), carbon), 2.4, 0.68, 0);
  add(new Mesh(new BoxGeometry(5.3, 0.03, 1.4), carbon), 0, 0.06, 0);                    // floor
  add(new Mesh(new BoxGeometry(0.5, 0.5, 0.28), accentMat), 0.6, 0.85, 0);              // airbox
  const halo = add(new Mesh(new TorusGeometry(0.42, 0.03, 8, 32, Math.PI), carbon), -0.55, 0.78, 0);
  halo.rotation.set(Math.PI / 2, 0, Math.PI / 2);
  root.add(body);
  const wheels = [], discs = [];
  for (const [x, front] of [[-1.75, true], [1.85, false]]) {
    for (const z of [-0.82, 0.82]) {
      const w = wheel(0.36, front ? 0.34 : 0.42);
      w.g.position.set(x, 0.36, z);
      root.add(w.g);
      wheels.push(w); discs.push(w.disc);
    }
  }
  shadowAll(root);
  return { root, body, wheels, discs, length: 5.6, width: 2.0, frontSign: -1 };
}
