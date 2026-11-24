// Home hero, "Telemetria viva": one canvas, two views (industrial | F1) on the shared Stage.
// Every moving value comes from /assets/hero/hero-data.json, built by
// scripts/build_hero_data.py from files in the repository.
import { PMREMGenerator, Vector3 } from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { gsap } from "gsap";
import { Stage, TIERS } from "../scene/engine.js";
import { buildIndustrial } from "./industrial.js";
import { buildF1, DISPLAY as F1_DISPLAY } from "./f1.js";
import { GGDiagram, formatG } from "./hud.js";

const NUM = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1, minimumFractionDigits: 1 });
const pct = (v) => `${NUM.format(v * 100)}%`;

function requestedTier() {
  const q = new URLSearchParams(location.search).get("q");
  return q !== null && /^[0-2]$/.test(q) ? Number(q) : null;
}

export async function mountHero(root) {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const canvas = root.querySelector("canvas");
  const res = await fetch("/assets/hero/hero-data.json");
  if (!res.ok) throw new Error(`hero data ${res.status}`);
  const data = await res.json();

  let ind, f1;
  const stage = new Stage(canvas, (renderer) => {
    const pmrem = new PMREMGenerator(renderer);
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    ind = buildIndustrial(data.industrial, env);
    f1 = buildF1(data.f1, env);
    return [ind, f1];
  }, { tier: requestedTier(), onTierChange: (i) => { root.dataset.quality = TIERS[i].name; } });

  const $ = (sel) => root.querySelector(sel);
  const set = (sel, txt) => { const el = $(sel); if (el) el.textContent = txt; };
  set("[data-oee]", pct(data.industrial.oee_weighted));
  set("[data-elevation]", String(F1_DISPLAY.elevation));
  set("[data-speed-range]", `de ${f1.speedRange[0]} a ${f1.speedRange[1]} km/h`);
  const statusEls = data.industrial.lines.map((_, i) => $(`[data-status="${i}"]`));
  const carRows = data.f1.cars.map((c) => $(`[data-car="${c.code}"]`));
  const lapEl = $("[data-lap]"), gLat = $("[data-glat]"), gLong = $("[data-glong]"), discEl = $("[data-disc]");
  const gg = $("canvas.gg") ? new GGDiagram($("canvas.gg")) : null;
  const view = $(".stage-view");
  const tags = data.f1.cars.map(() => {
    const el = document.createElement("span");
    el.className = "car-tag";
    el.setAttribute("aria-hidden", "true");
    view.append(el);
    return el;
  });

  // Split between the views (share of the industrial side) and hover tint per view.
  const vertical = () => matchMedia("(max-width: 720px)").matches;
  const split = { value: 0.5, target: 0.5 };
  const tint = [{ v: 0, t: 0 }, { v: 0, t: 0 }];
  [...root.querySelectorAll(".half")].forEach((h, i) => {
    const on = () => { tint[i].t = 1; if (!vertical()) split.target = i === 0 ? 0.62 : 0.38; };
    const off = () => { tint[i].t = 0; split.target = 0.5; };
    h.addEventListener("pointerenter", on);
    h.addEventListener("focusin", on);
    h.addEventListener("pointerleave", off);
    h.addEventListener("focusout", off);
  });
  const parallax = { x: 0, y: 0, tx: 0, ty: 0 };
  if (!reduce) {
    root.addEventListener("pointermove", (e) => {
      const r = view.getBoundingClientRect();
      parallax.tx = Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width) * 2 - 1));
      parallax.ty = Math.max(-1, Math.min(1, ((e.clientY - r.top) / r.height) * 2 - 1));
    });
    root.addEventListener("pointerleave", () => { parallax.tx = 0; parallax.ty = 0; });
  }

  let W = 1, H = 1;
  const layout = () => {
    const v = vertical();
    const bw = v ? W : Math.round(W * 0.62), bh = v ? Math.round(H / 2) : H;
    ind.state.fit = f1.state.fit = v ? 1 : 0.5 / 0.62;
    f1.state.pan = v ? [0, 0] : [0.1, -0.12];
    return { vertical: v, buffer: [{ w: bw, h: bh }, { w: bw, h: bh }] };
  };
  const resize = () => {
    const r = view.getBoundingClientRect();
    W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
    stage.resize(W, H, layout());
    for (const m of f1.lines) m.resolution.set(W, H);
    gg?.resize();
  };
  new ResizeObserver(resize).observe(view);
  resize();

  const proj = new Vector3();
  let lastDom = 0, time = 0;
  function render(dt, now) {
    time += dt;
    const k = reduce ? 1 : 1 - Math.exp(-dt * 7);
    split.value += (split.target - split.value) * k;
    tint.forEach((x) => { x.v += (x.t - x.v) * k; });
    ind.tint(tint[0].v);
    f1.tint(tint[1].v);
    const kp = 1 - Math.exp(-dt * 3);
    parallax.x += (parallax.tx - parallax.x) * kp;
    parallax.y += (parallax.ty - parallax.y) * kp;
    ind.state.parallax = f1.state.parallax = [parallax.x, parallax.y];
    root.style.setProperty("--split", split.value.toFixed(4));
    ind.step(dt);
    f1.step(dt);
    if (!reduce) f1.state.azimuth += dt * ((Math.PI * 2) / 240);
    const lay = stage.layout;
    const a = lay.vertical ? { x: 0, y: H / 2, w: W, h: H / 2 } : { x: 0, y: 0, w: W * split.value, h: H };
    const b = lay.vertical ? { x: 0, y: 0, w: W, h: H / 2 } : { x: a.w, y: 0, w: W - a.w, h: H };
    stage.render([a, b], time);

    // Car tags: project in buffer space, then apply the same centred crop as the composite.
    const buf = lay.buffer[1];
    const placed = f1.readout.map((r, i) => {
      proj.copy(r.world).project(f1.camera);
      const bx = ((proj.x + 1) / 2) * buf.w, by = ((1 - proj.y) / 2) * buf.h;
      return { i, x: b.x + bx - (buf.w - b.w) / 2, y: (H - b.y - b.h) + by - (buf.h - b.h) / 2, off: proj.z > 1 };
    }).sort((p, q) => q.y - p.y);
    placed.forEach((p, n) => {
      for (let j = 0; j < n; j++) if (Math.abs(placed[j].x - p.x) < 62 && Math.abs(placed[j].y - p.y) < 22) p.y = placed[j].y - 22;
      const tag = tags[p.i];
      tag.style.transform = `translate(${p.x.toFixed(1)}px, ${p.y.toFixed(1)}px)`;
      tag.hidden = p.off || p.x < b.x || p.x > b.x + b.w || p.y < H - b.y - b.h || p.y > H - b.y;
    });

    if (now - lastDom > 120) {
      lastDom = now;
      const v = lay.vertical;
      f1.readout.forEach((r, i) => {
        tags[i].textContent = v ? `${r.code} ${r.speed}` : r.code;
        const row = carRows[i];
        if (row) {
          row.querySelector("[data-v]").textContent = `${r.speed} km/h`;
          row.querySelector("[data-g]").textContent = `${r.gear}ª`;
        }
      });
      const L = f1.readout[0];
      if (L) {
        if (lapEl && L.lap) lapEl.textContent = `Volta ${L.lap} de ${data.f1.race_laps}`;
        if (gLat) gLat.textContent = formatG(L.aLat);
        if (gLong) gLong.textContent = `${L.aLong < -0.05 ? "freando" : L.aLong > 0.05 ? "acelerando" : "constante"} ${formatG(L.aLong)}`;
        if (discEl) discEl.textContent = `${Math.round(L.disc)} °C`;
      }
      ind.lines.forEach((l, i) => {
        const st = statusEls[i];
        if (st) {
          st.textContent = l.running ? (l.welding ? "soldando" : "em operação") : "parada";
          st.dataset.state = l.running ? "run" : "stop";
        }
      });
    }
    if (gg && !lay.vertical) gg.draw(f1.history);
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
    if (visible && !document.hidden) {
      render(dt, now);
      stage.observe(dt);
    }
    requestAnimationFrame(loop);
  };
  canvas.addEventListener("webglcontextlost", (e) => { e.preventDefault(); running = false; root.dataset.state = "fallback"; });
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(root);

  if (reduce) {
    for (let i = 0; i < 30; i++) ind.step(1 / 30);
    f1.step(30);
    render(0, performance.now());
    root.dataset.state = "ready";
    return;
  }
  ind.state.zoom = 0.82;
  Object.assign(f1.state, { distance: 1.3, elevation: 76 });
  render(0.016, performance.now());
  root.dataset.state = "ready";
  gsap.timeline({ defaults: { ease: "expo.out" } })
    .to(canvas, { opacity: 1, duration: 0.6, ease: "power1.out" }, 0)
    .to(name, { w: 112, duration: 1.6, onUpdate: applyName }, 0)
    .to(ind.state, { zoom: 1, duration: 1.8 }, 0.1)
    .to(f1.state, { distance: 1, elevation: 42, duration: 2.2 }, 0.1)
    .from(root.querySelectorAll(".cap > *"), { y: 14, opacity: 0, duration: 0.9, stagger: 0.06 }, 0.5);
  requestAnimationFrame(loop);
}
