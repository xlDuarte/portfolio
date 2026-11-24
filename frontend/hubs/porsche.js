// Porsche Cup hub: generic GT car on a turntable with the lab's own load-transfer model
// (site/motorsport/porsche/model.mjs, tested in the repo). Each wheel shows its vertical load as
// a column and a tyre glow; the body pitches and rolls through a spring-damper. Without input the
// car runs a scripted braking → corner → exit cycle; the sliders take over manual control.
import { BoxGeometry, Color, Group, MathUtils, Mesh, MeshStandardMaterial } from "three";
import { mountStage } from "./common.js";
import { studio, bindSpin } from "./studio.js";
import { gtCar } from "../scene/cars.js";
import { SpringDamper } from "../scene/physics.js";
import { C } from "../hero/palette.js";
import { calculate, DEFAULT, LIMITS, ASSUMPTIONS } from "../../site/motorsport/porsche/model.mjs";

export const DISPLAY = { rollDegPerG: 3.2, pitchDegPerG: 2.4 };   // ≈2× a stiff GT race car, for legibility

// Scripted manoeuvre, seconds → inputs within the model's validity limits.
const CYCLE = [
  { t: 0, speed: 230, ax: 0.35, ay: 0 },       // full throttle on the straight
  { t: 3, speed: 238, ax: -0.8, ay: 0 },       // threshold braking
  { t: 5, speed: 130, ax: -0.3, ay: 0.7 },     // trail-braking into the corner
  { t: 6.5, speed: 115, ax: 0, ay: 1.15 },     // apex
  { t: 8.5, speed: 140, ax: 0.3, ay: 0.6 },    // exit
  { t: 10, speed: 190, ax: 0.4, ay: -0.3 },    // flick into the next corner
  { t: 12, speed: 230, ax: 0.35, ay: 0 },
];
const PERIOD = CYCLE[CYCLE.length - 1].t;

function cycleAt(t) {
  const x = t % PERIOD;
  const i = CYCLE.findIndex((k, j) => j < CYCLE.length - 1 && x >= k.t && x < CYCLE[j + 1].t);
  const a = CYCLE[i], b = CYCLE[i + 1];
  const f = (1 - Math.cos(Math.PI * (x - a.t) / (b.t - a.t))) / 2;   // cosine blend, no jerk spikes
  const mix = (k) => a[k] + (b[k] - a[k]) * f;
  return { speed: mix("speed"), ax: mix("ax"), ay: mix("ay") };
}

const clampInput = (p) => Object.fromEntries(Object.entries(p).map(([k, v]) => [k, MathUtils.clamp(v, ...LIMITS[k])]));

export function mount(root) {
  const inputs = { speed: root.querySelector("#pc-speed"), ay: root.querySelector("#pc-ay"), ax: root.querySelector("#pc-ax") };
  const out = root.querySelector("[data-loads]");
  const modeBtn = root.querySelector("[data-auto]");
  let manual = false, t = 0, lastDom = 0, result = null;
  const staticLoad = (ASSUMPTIONS.mass * ASSUMPTIONS.g) / 4;
  const cold = new Color(0x2f6fd6), hot = new Color(C.auto), tmp = new Color();

  const setManual = (on) => {
    manual = on;
    if (modeBtn) { modeBtn.hidden = !on; }
  };
  for (const el of Object.values(inputs)) el?.addEventListener("input", () => setManual(true));
  modeBtn?.addEventListener("click", () => setManual(false));

  return mountStage(root, {
    build(env) {
      const s = studio(env, { washTint: C.autoWash });
      const car = gtCar({ paint: 0xd5d9de, accent: C.auto });
      const holder = new Group();
      holder.position.y = s.plinthTop;
      holder.add(car.root);
      s.scene.add(holder);
      const columns = car.wheels.map((w) => {
        const m = new Mesh(new BoxGeometry(0.18, 1, 0.18),
          new MeshStandardMaterial({ color: 0xffffff, emissive: 0x000000, transparent: true, opacity: 0.85, roughness: 0.3 }));
        m.position.set(w.g.position.x, 0, w.g.position.z * 1.9);   // bar standing beside each wheel
        car.root.add(m);
        return m;
      });
      const pitch = new SpringDamper(1.8, 0.6), roll = new SpringDamper(2.0, 0.65);
      return [Object.assign(s, {
        step(dt) {
          t += dt;
          const p = manual
            ? { speed: +inputs.speed.value, ay: +inputs.ay.value, ax: +inputs.ax.value }
            : cycleAt(t);
          try { result = calculate({ ...DEFAULT, ...clampInput(p) }); } catch { return; }
          if (!manual) for (const [k, el] of Object.entries(inputs)) if (el) el.value = p[k].toFixed(k === "speed" ? 0 : 2);
          holder.rotation.y = s.table.step(dt, s.held?.());
          // Body motion (car faces −x, left = +z). Braking (ax < 0) dives the nose: +θz lowers −x.
          // ay > 0 loads the right wheels (model convention), so the body rolls right: left side (+z) up = −θx.
          car.body.rotation.z = pitch.step(MathUtils.degToRad(-DISPLAY.pitchDegPerG * result.parameters.ax), dt);
          car.body.rotation.x = roll.step(MathUtils.degToRad(-DISPLAY.rollDegPerG * result.parameters.ay), dt);
          result.wheels.forEach((w, i) => {
            const k = w.fz / staticLoad;                      // 1 = static share
            const h = Math.max(0.05, w.fz / 6000);            // 1 m of column per 6 kN
            columns[i].scale.y = h;
            columns[i].position.y = h / 2;
            tmp.copy(cold).lerp(hot, MathUtils.clamp((k - 0.6) / 1.2, 0, 1));
            columns[i].material.color.copy(tmp);
            columns[i].material.emissive.copy(tmp).multiplyScalar(0.25 + 0.6 * MathUtils.clamp(k - 1, 0, 1));
          });
        },
      })];
    },
    warmup() {},
    intro(tl, views) {
      const v = views[0];
      v.state.distance = 1.3;
      tl.to(v.state, { distance: 1, duration: 2 }, 0.2);
      const view = root.querySelector(".hub-view");
      v.held = bindSpin(view, v.table, () => view.getBoundingClientRect()).held;
    },
    onFrame() {
      const now = performance.now();
      if (!result || !out || now - lastDom < 125) return;
      lastDom = now;
      const kN = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2, minimumFractionDigits: 2 });
      out.querySelectorAll("[data-w]").forEach((cell) => {
        const w = result.wheels.find((x) => x.id === cell.dataset.w);
        if (w) cell.textContent = `${kN.format(w.fz / 1000)} kN`;
      });
      const set = (sel, v) => { const el = out.querySelector(sel); if (el) el.textContent = v; };
      set("[data-front]", `${kN.format(result.frontPercent)}%`);
      set("[data-down]", `${kN.format(result.downforce / 1000)} kN`);
      set("[data-util]", `${Math.round(result.utilization * 100)}%`);
      for (const [k, el] of Object.entries(inputs)) {
        const o = root.querySelector(`output[for="${el?.id}"]`);
        if (o) o.textContent = k === "speed" ? `${Math.round(el.value)} km/h` : `${kN.format(+el.value)} g`;
      }
    },
  });
}
