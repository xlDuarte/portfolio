// F1 hub: the Sakhir 2024 replay in full width, with the same derived physics as the home hero
// (chassis pitch/roll, brake-disc glow, skid-block sparks) and a larger telemetry read-out.
import { Vector3 } from "three";
import { mountStage, getJSON } from "./common.js";
import { buildF1 } from "../hero/f1.js";
import { GGDiagram, formatG, placeTags } from "../hero/hud.js";

export async function mount(root) {
  const data = await getJSON("/assets/hero/hero-data.json");
  const view = root.querySelector(".hub-view");
  const tags = data.f1.cars.map(() => {
    const el = document.createElement("span");
    el.className = "car-tag";
    el.setAttribute("aria-hidden", "true");
    view.append(el);
    return el;
  });
  const $ = (s) => root.querySelector(s);
  const gg = $("canvas.gg") ? new GGDiagram($("canvas.gg")) : null;
  const rows = data.f1.cars.map((c) => $(`[data-car="${c.code}"]`));
  const proj = new Vector3();
  let f1, lastDom = 0;
  return mountStage(root, {
    build(env) {
      f1 = buildF1(data.f1, env);
      f1.state.elevation = 38;
      return [f1];
    },
    onResize(W, H) { for (const m of f1.lines) m.resolution.set(W, H); gg?.resize(); },
    warmup(views) { views[0].step(30); },
    intro(tl, views) {
      Object.assign(views[0].state, { distance: 1.35, elevation: 72 });
      tl.to(views[0].state, { distance: 1, elevation: 38, duration: 2.2 }, 0.1);
    },
    onFrame(dt, ctx) {
      if (!ctx.reduce) f1.state.azimuth += dt * ((Math.PI * 2) / 240);
      placeTags(f1.readout, tags, ctx.rects[0], ctx.stage.layout.buffer[0], ctx.H, f1.camera, proj);
      const now = performance.now();
      if (now - lastDom > 120) {
        lastDom = now;
        f1.readout.forEach((r, i) => {
          tags[i].textContent = `${r.code} ${r.speed}`;
          const row = rows[i];
          if (!row) return;
          row.querySelector("[data-v]").textContent = `${r.speed} km/h`;
          row.querySelector("[data-g]").textContent = `${r.gear}ª`;
          row.querySelector("[data-lat]").textContent = formatG(r.aLat);
          row.querySelector("[data-lon]").textContent = `${r.aLong < 0 ? "−" : "+"}${formatG(r.aLong)}`;
          row.querySelector("[data-disc]").textContent = `${Math.round(r.disc)} °C`;
        });
        const lap = f1.readout[0]?.lap;
        if (lap) { const el = $("[data-lap]"); if (el) el.textContent = `Volta ${lap} de ${data.f1.race_laps}`; }
      }
      gg?.draw(f1.history);
    },
  });
}
