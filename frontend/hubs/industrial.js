// Industrial hub: an isometric digital twin with one station per case study. Every motion is
// driven by that study's (synthetic) numbers from hub-data.json / hero-data.json:
//   OEE       belt stops for (1 − availability), runs at the performance rate
//   Supply    AGV with a trapezoidal velocity profile (a ≤ 0.6 m/s², v ≤ 1.4 m/s); each delivery
//             is on time with the study's on-time share (green) or late (amber)
//   CAPEX     hydraulic press, ram on a spring-damper, stamping cycle
//   Forecast  silo level follows the last 140 days of real series; the ring marks the 7-day
//             seasonal-naive forecast used in the study
//   Churn     trucks leave the dock; the study's churn rate of them are red
// Scene scale: 1 unit = 0.5 m. Clicking a station opens its case study.
import {
  BoxGeometry, Color, CylinderGeometry, DirectionalLight, Group, HemisphereLight, Mesh,
  MeshStandardMaterial, OrthographicCamera, Raycaster, Scene, TorusGeometry, Vector2, Vector3,
} from "three";
import { mountStage, getJSON } from "./common.js";
import { SpringDamper, SparkField, STEEL_SPARK } from "../scene/physics.js";
import { SparkView } from "../scene/sparks.js";
import { C, mulberry32 } from "../hero/palette.js";
import { placeTags } from "../hero/hud.js";

const UPM = 2;

/** Trapezoidal motion along a closed polyline: accelerate, cruise, brake into each stop. */
class AGV {
  constructor(points, { vmax = 1.4 * UPM, amax = 0.6 * UPM, dwell = 1.2 } = {}) {
    this.pts = points; this.vmax = vmax; this.amax = amax; this.dwell = dwell;
    this.seg = 0; this.s = 0; this.v = 0; this.wait = 0; this.deliveries = 0;
  }
  step(dt) {
    if (this.wait > 0) { this.wait -= dt; return; }
    const a = this.pts[this.seg], b = this.pts[(this.seg + 1) % this.pts.length];
    const len = a.distanceTo(b), remaining = len - this.s;
    const brakeDist = (this.v * this.v) / (2 * this.amax);
    this.v = remaining <= brakeDist ? Math.max(0.15, this.v - this.amax * dt) : Math.min(this.vmax, this.v + this.amax * dt);
    this.s += this.v * dt;
    if (this.s >= len) {
      this.s = 0; this.v = 0; this.seg = (this.seg + 1) % this.pts.length; this.wait = this.dwell;
      if (this.seg % 2 === 0) this.deliveries++;
    }
  }
  pose(out) {
    const a = this.pts[this.seg], b = this.pts[(this.seg + 1) % this.pts.length];
    out.copy(a).lerp(b, Math.min(1, this.s / a.distanceTo(b)));
    return Math.atan2(-(b.z - a.z), b.x - a.x);
  }
}

export async function mount(root) {
  const [hub, hero] = await Promise.all([getJSON("/assets/hubs/hub-data.json"), getJSON("/assets/hero/hero-data.json")]);
  const view = root.querySelector(".hub-view");
  const stations = [];
  const labelEls = [];
  let scene, camera, hovered = null;
  const rng = mulberry32(7);

  const mat = (color, o = {}) => new MeshStandardMaterial({ color, roughness: 0.55, ...o });
  const steel = mat(C.steel, { metalness: 0.75, roughness: 0.32 });
  const steelDark = mat(C.steelDark, { metalness: 0.6, roughness: 0.45 });
  const panel = mat(C.ind, { metalness: 0.2, roughness: 0.4 });
  const box = (w, h, d, m, x, y, z, parent) => {
    const o = new Mesh(new BoxGeometry(w, h, d), m);
    o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; parent.add(o); return o;
  };

  function station(slug, title, x, z, build) {
    const g = new Group();
    g.position.set(x, 0, z);
    g.scale.setScalar(1.3);
    const pad = box(5.6, 0.06, 5.6, mat(0xe6eaee, { roughness: 0.9 }), 0, 0.03, 0, g);
    const accent = box(5.6, 0.065, 0.12, mat(0xe6eaee, { emissive: C.ind, emissiveIntensity: 0 }), 0, 0.035, 2.74, g);
    const api = build(g) || {};
    scene.add(g);
    g.traverse((o) => { o.userData.station = slug; });
    const s = { slug, title, g, pad, accent, ...api, world: new Vector3(x, 5.8, z) };
    stations.push(s);
    const el = document.createElement("span");
    el.className = "car-tag station-tag";
    el.textContent = title;
    el.setAttribute("aria-hidden", "true");
    view.append(el);
    labelEls.push(el);
    return s;
  }

  const raycaster = new Raycaster(), ndc = new Vector2();
  const pick = (e) => {
    const r = view.getBoundingClientRect();
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    raycaster.setFromCamera(ndc, camera);
    const hit = raycaster.intersectObjects(stations.map((s) => s.g), true)[0];
    return hit ? stations.find((s) => s.slug === hit.object.userData.station) : null;
  };
  view.addEventListener("pointermove", (e) => {
    hovered = pick(e);
    view.style.cursor = hovered ? "pointer" : "";
  });
  view.addEventListener("pointerleave", () => { hovered = null; });
  view.addEventListener("click", (e) => { const s = pick(e); if (s) location.href = `/cases/${s.slug}/`; });

  const proj = new Vector3();
  const oeeLines = hero.industrial.lines;
  const series = hub.forecast.demand_last_days;
  const sMin = Math.min(...series), sMax = Math.max(...series);
  let clock = 0;

  return mountStage(root, {
    build(env) {
      scene = new Scene();
      scene.environment = env;
      scene.background = new Color(C.wash);
      camera = new OrthographicCamera(-10, 10, 10, -10, 0.1, 300);
      camera.position.set(40, 34, 40);
      camera.lookAt(0, 0, 0);
      const base = camera.position.clone();
      scene.add(new HemisphereLight(0xffffff, 0xd8dde3, 0.85));
      const sun = new DirectionalLight(0xffffff, 1.9);
      sun.position.set(-10, 24, 14);
      sun.castShadow = true;
      Object.assign(sun.shadow.camera, { left: -22, right: 22, top: 22, bottom: -22, near: 1, far: 80 });
      sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
      scene.add(sun);
      box(48, 0.3, 26, mat(C.concrete, { roughness: 0.92 }), 0, -0.15, 0, scene);

      // 1 — OEE line
      station("oee", "OEE", -9.2, 9.2, (g) => {
        const belt = box(4.6, 0.16, 1.1, mat(0x3a4048, { roughness: 0.8 }), 0, 0.9, 0, g);
        for (const x of [-1.9, 1.9]) for (const z of [-0.45, 0.45]) box(0.1, 0.85, 0.1, steelDark, x, 0.42, z, g);
        box(1.3, 2.1, 0.26, steel, 0, 1.05, -0.8, g); box(1.3, 2.1, 0.26, steel, 0, 1.05, 0.8, g);
        box(1.5, 0.8, 1.9, steel, 0, 2.4, 0, g); box(0.04, 0.4, 1.3, panel, 0.76, 2.4, 0, g);
        const lamp = new Mesh(new CylinderGeometry(0.14, 0.14, 0.2, 16), mat(C.run, { emissive: C.run, emissiveIntensity: 1.6 }));
        lamp.position.set(0, 2.9, 0); g.add(lamp);
        const parts = Array.from({ length: 4 }, (_, i) => box(0.36, 0.36, 0.36, mat(C.part), -2 + i * 1.15, 1.16, 0, g));
        const l = oeeLines[0];
        return {
          step(dt) {
            const run = ((clock / 24) % 1) < l.availability;
            lamp.material.color.setHex(run ? C.run : C.stop); lamp.material.emissive.setHex(run ? C.run : C.stop);
            if (run) for (const p of parts) { p.position.x += 1.7 * l.performance * dt; if (p.position.x > 2.1) p.position.x -= 4.6; }
          },
        };
      });

      // 2 — Supply: racks + AGV
      station("supply", "Supply chain", -4.6, 4.6, (g) => {
        for (const x of [-1.6, 1.6]) {
          for (const y of [0.05, 1.05, 2.05]) box(1.2, 0.06, 3.6, steelDark, x, y, 0, g);
          for (const z of [-1.75, 1.75]) box(0.08, 2.6, 0.08, mat(0xd97a12), x - 0.56, 1.3, z, g), box(0.08, 2.6, 0.08, mat(0xd97a12), x + 0.56, 1.3, z, g);
          for (let i = 0; i < 6; i++) box(0.9, 0.55, 0.9, mat(i % 3 ? 0xc9a77a : 0xb48a59), x, 0.36 + Math.floor(i / 2) * 1.0, -1.2 + (i % 2) * 2.4, g);
        }
        const agv = new Group();
        box(0.9, 0.28, 0.6, mat(0xf2c230, { metalness: 0.2 }), 0, 0.2, 0, agv);
        const light = box(0.16, 0.08, 0.16, mat(C.run, { emissive: C.run, emissiveIntensity: 2 }), 0, 0.4, 0, agv);
        const load = box(0.6, 0.4, 0.5, mat(0xc9a77a), 0, 0.55, 0, agv);
        g.add(agv);
        const path = [new Vector3(0, 0, 2.4), new Vector3(0, 0, -2.4), new Vector3(2.5, 0, -2.4), new Vector3(2.5, 0, 2.4)];
        const bot = new AGV(path);
        const tmp = new Vector3();
        let onTime = true, last = 0;
        return {
          step(dt) {
            bot.step(dt);
            const yaw = bot.pose(tmp);
            agv.position.copy(tmp); agv.rotation.y = yaw;
            if (bot.deliveries !== last) { last = bot.deliveries; onTime = rng() * 100 < hub.supply.on_time_pct; }
            const c = onTime ? C.run : C.stop;
            light.material.color.setHex(c); light.material.emissive.setHex(c);
            load.visible = bot.seg < 2;
          },
        };
      });

      // 3 — CAPEX: hydraulic press
      station("capex", "CAPEX", 0.0, -0.0, (g) => {
        box(2.6, 0.5, 2.0, steel, 0, 0.25, 0, g);
        for (const x of [-1.1, 1.1]) box(0.3, 3.6, 0.3, steelDark, x, 1.8, 0, g);
        box(2.8, 0.6, 1.4, steel, 0, 3.7, 0, g);
        box(0.04, 0.4, 1.0, panel, 1.42, 3.7, 0, g);
        const ram = box(1.6, 0.5, 1.2, mat(0x6d757e, { metalness: 0.8, roughness: 0.3 }), 0, 2.4, 0, g);
        const blank = box(1.0, 0.08, 0.8, mat(0xdfe3e7, { metalness: 0.6 }), 0, 0.54, 0, g);
        const spring = new SpringDamper(1.6, 0.35, 2.4);
        const sparks = new SparkField(240, { ...STEEL_SPARK, visibleK: 900 });
        const view3 = new SparkView(sparks, UPM, { intensity: 2.6, size: 3.5 });
        view3.addTo(g);
        let hit = false;
        return {
          step(dt) {
            const down = ((clock / 3.2) % 1) < 0.45;
            const y = spring.step(down ? 0.84 : 2.4, dt);
            ram.position.y = Math.max(0.84, y);
            if (y <= 0.86 && !hit) {
              hit = true;
              for (let i = 0; i < 40; i++) {
                const a = rng() * Math.PI * 2, sp = 1.5 + rng() * 2.5;
                sparks.emit(0, 0.6 / UPM, 0, Math.cos(a) * sp, 0.8 + rng() * 1.6, Math.sin(a) * sp, 1500 + rng() * 300);
              }
              blank.scale.y = 0.6;
            }
            if (!down) { hit = false; blank.scale.y = 1; }
            sparks.step(dt, () => 0.29 / UPM);
            view3.update();
          },
        };
      });

      // 4 — Forecast: silo following the real series, ring = seasonal-naive forecast
      station("forecast", "Previsão", 4.6, -4.6, (g) => {
        const H = 3.6;
        const shell = new Mesh(new CylinderGeometry(1.3, 1.3, H, 48, 1, true),
          new MeshStandardMaterial({ color: 0xdfe4ea, transparent: true, opacity: 0.35, roughness: 0.2, metalness: 0.4, depthWrite: false }));
        shell.position.y = H / 2 + 0.3; g.add(shell);
        const fill = new Mesh(new CylinderGeometry(1.24, 1.24, 1, 48), mat(0x2f6fd6, { roughness: 0.35 }));
        g.add(fill);
        const ring = new Mesh(new TorusGeometry(1.36, 0.05, 8, 64), mat(C.auto, { emissive: C.auto, emissiveIntensity: 0.8 }));
        ring.rotation.x = Math.PI / 2; g.add(ring);
        for (const a of [0, 1, 2, 3]) box(0.12, 0.3, 0.12, steelDark, Math.cos(a * Math.PI / 2) * 1.2, 0.15, Math.sin(a * Math.PI / 2) * 1.2, g);
        const level = (v) => 0.3 + 0.2 + ((v - sMin) / (sMax - sMin)) * (H - 0.5);
        let shown = level(series[7]);
        return {
          step(dt) {
            const day = 7 + Math.floor(clock / 0.6) % (series.length - 7);
            shown += (level(series[day]) - shown) * (1 - Math.exp(-dt * 5));
            fill.scale.y = shown - 0.3; fill.position.y = 0.3 + (shown - 0.3) / 2;
            ring.position.y = level(series[day - 7]);
          },
        };
      });

      // 5 — Churn: dock with departing trucks
      station("churn", "Churn B2B", 9.2, -9.2, (g) => {
        g.rotation.y = Math.PI / 4;                       // trucks leave towards the viewer
        box(5.2, 1.0, 1.2, mat(0xd5dae0), 0, 0.5, -2.1, g);
        const trucks = Array.from({ length: 3 }, (_, i) => {
          const t = new Group();
          const cargo = box(1.8, 1.0, 0.9, mat(C.part), -0.3, 0.75, 0, t);
          box(0.6, 0.7, 0.85, mat(0x59616b), 0.95, 0.6, 0, t);
          for (const x of [-0.8, 0.9]) for (const z of [-0.45, 0.45]) {
            const w = new Mesh(new CylinderGeometry(0.2, 0.2, 0.12, 16), mat(0x17191c));
            w.rotation.x = Math.PI / 2; w.position.set(x, 0.2, z); t.add(w);
          }
          t.position.set(-1.6 + i * 1.6, 0, -0.9);
          t.rotation.y = -Math.PI / 2;
          t.traverse((o) => { if (o.isMesh) o.castShadow = true; });
          g.add(t);
          return { t, cargo, v: 0, leaving: false, x0: -1.6 + i * 1.6, wait: 1 + i * 2.2, churned: false };
        });
        return {
          step(dt) {
            for (const k of trucks) {
              if (!k.leaving) {
                k.wait -= dt;
                if (k.wait <= 0) { k.leaving = true; k.churned = rng() < hub.churn.positive_rate_train; k.cargo.material.color.setHex(k.churned ? C.auto : C.part); }
                continue;
              }
              k.v += 1.2 * dt;                                  // constant acceleration away from the dock
              k.t.position.z += k.v * dt;
              if (k.t.position.z > 3.4) { k.t.position.z = -0.9; k.v = 0; k.leaving = false; k.wait = 2 + rng() * 3; k.cargo.material.color.setHex(C.part); }
            }
          },
        };
      });

      // Camera fit to the floor.
      camera.updateMatrixWorld();
      const pts = [];
      for (const st of stations) for (const dx of [-3.8, 3.8]) for (const y of [0, 6]) for (const dz of [-3.8, 3.8]) pts.push(new Vector3(st.g.position.x + dx, y, st.g.position.z + dz).applyMatrix4(camera.matrixWorldInverse));
      const bx = Math.max(...pts.map((v) => Math.abs(v.x))), y0 = Math.min(...pts.map((v) => v.y)), y1 = Math.max(...pts.map((v) => v.y));
      const state = { fit: 1, parallax: [0, 0], zoom: 1 };
      const highlight = new Color(C.indWash);
      return [{
        scene, camera, state, aoRadius: 0.6, aoIntensity: 0.9,
        setShadowSize: (s) => { sun.shadow.mapSize.set(s, s); sun.shadow.map?.dispose(); sun.shadow.map = null; },
        frame(aspect) {
          let h = ((y1 - y0) / 2) * 1.06, w = h * aspect;
          if (w < bx * 1.04) { w = bx * 1.04; h = w / aspect; }
          h /= state.zoom; w /= state.zoom;
          camera.position.set(base.x + state.parallax[0] * 2, base.y + state.parallax[1] * 1.5, base.z - state.parallax[0] * 2);
          camera.lookAt(0, 0, 0);
          const cy = (y0 + y1) / 2;
          Object.assign(camera, { left: -w, right: w, top: cy + h, bottom: cy - h });
          camera.updateProjectionMatrix();
        },
        step(dt) {
          clock += dt;
          for (const s of stations) {
            s.step?.(dt);
            const on = hovered === s;
            s.accent.material.emissiveIntensity += ((on ? 2.4 : 0) - s.accent.material.emissiveIntensity) * Math.min(1, dt * 10);
            s.pad.material.color.setHex(0xe6eaee);
            s.accent.material.color.setHex(on ? C.ind : 0xe6eaee);
            if (on) s.pad.material.color.lerp(highlight, 0.9);
          }
        },
      }];
    },
    warmup(views) { for (let i = 0; i < 60; i++) views[0].step(1 / 30); },
    intro(tl, views) {
      views[0].state.zoom = 0.85;
      tl.to(views[0].state, { zoom: 1, duration: 1.8 }, 0.1);
    },
    onFrame(_dt, ctx) {
      placeTags(stations, labelEls, ctx.rects[0], ctx.stage.layout.buffer[0], ctx.H, camera, proj);
      stations.forEach((s, i) => labelEls[i].classList.toggle("is-hot", hovered === s));
    },
  });
}
