// 3D g-g-V envelope. Loaded only when WebGL is available (dynamic import from main.js).
// Axes: x = lateral acceleration (g), y = speed (1 unit = 50 km/h), z = −longitudinal acceleration (g),
// so braking points towards the viewer. The surface is rebuilt from the envelope table each time the
// car changes; rendering happens on demand (no idle animation loop).
import {
  AmbientLight, BufferAttribute, BufferGeometry, Color, DirectionalLight, DoubleSide, Group, LineBasicMaterial,
  LineSegments, Mesh, MeshStandardMaterial, PerspectiveCamera, Points, PointsMaterial, Scene, Vector3, WebGLRenderer,
} from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const V_UNIT = 50;                         // km/h per world unit on the vertical axis
const LOW = new Color('#1d4e9e'), HIGH = new Color('#b8122b');
const DRIVER = { VER: '#1c2128', PER: '#1d4e9e', SAI: '#a85d00' };

export function mountGGV(root, { onReady } = {}) {
  const canvas = root.querySelector('canvas');
  const renderer = new WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'low-power' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  const scene = new Scene();
  const camera = new PerspectiveCamera(36, 1, 0.1, 200);
  camera.position.set(11, 9.5, 12);
  const controls = new OrbitControls(camera, canvas);
  controls.target.set(0, 3.4, -1.2);
  controls.enableDamping = false;
  controls.enablePan = false;
  controls.minDistance = 8;
  controls.maxDistance = 40;
  controls.update();

  scene.add(new AmbientLight(0xffffff, 1.4));
  const sun = new DirectionalLight(0xffffff, 1.6);
  sun.position.set(6, 14, 9);
  scene.add(sun);

  const frame = new Group();
  scene.add(frame);
  frame.add(axesLines());
  const labels = axisLabels(root);

  let surface = null, wire = null, cloud = null;

  function resize() {
    const w = root.clientWidth, h = root.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(h, 1);
    camera.updateProjectionMatrix();
    render();
  }

  function render() {
    renderer.render(scene, camera);
    labels.place(camera, root);
  }

  function setEnvelope(env, G) {
    for (const o of [surface, wire]) if (o) { frame.remove(o); o.geometry.dispose(); }
    const step = 2;                                  // every 2 m/s
    const rows = [];
    for (let i = 0; i < env.v.length; i += step) rows.push(i);
    const nf = env.frac.length;
    const ring = [];                                 // indices (j, side): side 0 = ax_max, 1 = ax_min
    for (let j = nf - 1; j >= 0; j--) ring.push([j, 0, +1]);
    for (let j = 1; j < nf; j++) ring.push([j, 0, -1]);
    for (let j = nf - 1; j >= 0; j--) ring.push([j, 1, -1]);
    for (let j = 1; j < nf - 1; j++) ring.push([j, 1, +1]);
    const m = ring.length;
    const pos = new Float32Array(rows.length * m * 3), col = new Float32Array(rows.length * m * 3);
    const vmax = env.v[env.v.length - 1];
    rows.forEach((i, r) => {
      const y = env.v[i] * 3.6 / V_UNIT;
      const c = LOW.clone().lerp(HIGH, env.v[i] / vmax);
      ring.forEach(([j, side, sign], k) => {
        const ay = sign * env.ayMax[i] * env.frac[j] / G;
        const ax = (side ? env.axMin[i][j] : env.axMax[i][j]) / G;
        const o = 3 * (r * m + k);
        pos[o] = ay; pos[o + 1] = y; pos[o + 2] = -ax;
        col[o] = c.r; col[o + 1] = c.g; col[o + 2] = c.b;
      });
    });
    const idx = [];
    for (let r = 0; r < rows.length - 1; r++) for (let k = 0; k < m; k++) {
      const a = r * m + k, b = r * m + (k + 1) % m, c = (r + 1) * m + k, d = (r + 1) * m + (k + 1) % m;
      idx.push(a, b, c, b, d, c);
    }
    const geo = new BufferGeometry();
    geo.setAttribute('position', new BufferAttribute(pos, 3));
    geo.setAttribute('color', new BufferAttribute(col, 3));
    geo.setIndex(idx);
    geo.computeVertexNormals();
    surface = new Mesh(geo, new MeshStandardMaterial({ vertexColors: true, transparent: true, opacity: 0.42,
      roughness: 0.6, metalness: 0.0, side: DoubleSide, depthWrite: false }));
    // contour rings every 50 km/h-ish
    const seg = [];
    rows.forEach((_, r) => {
      if (r % 7) return;
      for (let k = 0; k < m; k++) {
        const a = 3 * (r * m + k), b = 3 * (r * m + (k + 1) % m);
        seg.push(pos[a], pos[a + 1], pos[a + 2], pos[b], pos[b + 1], pos[b + 2]);
      }
    });
    const wg = new BufferGeometry();
    wg.setAttribute('position', new BufferAttribute(new Float32Array(seg), 3));
    wire = new LineSegments(wg, new LineBasicMaterial({ color: 0x1c2128, transparent: true, opacity: 0.55 }));
    frame.add(surface, wire);
    render();
  }

  function setCloud(groups, visible) {
    if (cloud) { frame.remove(cloud); cloud.traverse(o => o.geometry && o.geometry.dispose()); cloud = null; }
    if (!visible) { render(); return; }
    cloud = new Group();
    groups.forEach(g => {
      const n = g.v_kmh.length, p = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) { p[3 * i] = g.ay_g[i]; p[3 * i + 1] = g.v_kmh[i] / V_UNIT; p[3 * i + 2] = -g.ax_g[i]; }
      const geo = new BufferGeometry();
      geo.setAttribute('position', new BufferAttribute(p, 3));
      cloud.add(new Points(geo, new PointsMaterial({ color: DRIVER[g.driver] || '#1c2128', size: 0.09, sizeAttenuation: true })));
    });
    frame.add(cloud);
    render();
  }

  controls.addEventListener('change', render);
  new ResizeObserver(resize).observe(root);
  resize();
  root.dataset.state = 'ready';
  onReady?.();
  return { setEnvelope, setCloud, render };
}

function axesLines() {
  const seg = [];
  const push = (a, b) => seg.push(...a, ...b);
  push([-5, 0, 0], [5, 0, 0]);               // lateral
  push([0, 0, -2], [0, 0, 7]);               // longitudinal (braking forward)
  push([0, 0, 0], [0, 7.6, 0]);              // speed
  for (let v = 1; v <= 7; v++) push([-0.12, v, 0], [0.12, v, 0]);
  for (let a = -4; a <= 4; a++) if (a) push([a, 0, -0.12], [a, 0, 0.12]);
  for (let a = -1; a <= 6; a++) if (a) push([-0.12, 0, a], [0.12, 0, a]);
  const g = new BufferGeometry();
  g.setAttribute('position', new BufferAttribute(new Float32Array(seg), 3));
  return new LineSegments(g, new LineBasicMaterial({ color: 0x59616b }));
}

function axisLabels(root) {
  const defs = [
    { p: new Vector3(5.3, 0, 0), t: 'aceleração lateral (g)' },
    { p: new Vector3(0, 0, 7.3), t: 'frenagem (g)' },
    { p: new Vector3(0, 0, -2.3), t: 'tração' },
    { p: new Vector3(0, 7.9, 0), t: 'velocidade' },
    { p: new Vector3(0.3, 2, 0), t: '100 km/h' },
    { p: new Vector3(0.3, 4, 0), t: '200 km/h' },
    { p: new Vector3(0.3, 6, 0), t: '300 km/h' },
  ];
  const nodes = defs.map(d => {
    const s = document.createElement('span');
    s.className = 'ls-axis-label';
    s.textContent = d.t;
    root.append(s);
    return s;
  });
  return {
    place(camera, el) {
      const w = el.clientWidth, h = el.clientHeight;
      defs.forEach((d, i) => {
        const v = d.p.clone().project(camera);
        nodes[i].style.transform = `translate(${((v.x + 1) / 2 * w).toFixed(0)}px, ${((1 - v.y) / 2 * h).toFixed(0)}px)`;
        nodes[i].hidden = v.z > 1;
      });
    },
  };
}
