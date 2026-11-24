// Shared mounting for hub scenes: Stage set-up, layout (one view, or two split views with a
// hover-driven divider), render loop, visibility pause, reduced motion and pointer parallax.
import { PMREMGenerator } from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { gsap } from "gsap";
import { Stage, TIERS } from "../scene/engine.js";

export function requestedTier() {
  const q = new URLSearchParams(location.search).get("q");
  return q !== null && /^[0-2]$/.test(q) ? Number(q) : null;
}

export const prefersReducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

/**
 * @param root   element with a canvas inside `.hub-view`
 * @param opts   {
 *   build(env, renderer) -> view[]          views: { scene, camera, frame(aspect), state, step(dt), tint?(a) }
 *   split?: boolean                          two views side by side (stacked on narrow screens)
 *   onFrame?(dt, ctx)                        after rendering; ctx = { rects, W, H, views, stage }
 *   intro?(tl, views)                        add tweens to the opening timeline
 * }
 */
export function mountStage(root, opts) {
  const reduce = prefersReducedMotion();
  const canvas = root.querySelector("canvas");
  const view = root.querySelector(".hub-view");
  let views = [];
  const stage = new Stage(canvas, (renderer) => {
    const pmrem = new PMREMGenerator(renderer);
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    views = opts.build(env, renderer);
    return views;
  }, { tier: requestedTier(), onTierChange: (i) => { root.dataset.quality = TIERS[i].name; } });

  const narrow = () => matchMedia("(max-width: 720px)").matches;
  const split = { value: 0.5, target: 0.5 };
  const tint = views.map(() => ({ v: 0, t: 0 }));
  if (opts.split) {
    [...root.querySelectorAll("[data-half]")].forEach((h) => {
      const i = Number(h.dataset.half);
      const on = () => { tint[i].t = 1; if (!narrow()) split.target = i === 0 ? 0.62 : 0.38; };
      const off = () => { tint[i].t = 0; split.target = 0.5; };
      h.addEventListener("pointerenter", on);
      h.addEventListener("focusin", on);
      h.addEventListener("pointerleave", off);
      h.addEventListener("focusout", off);
    });
  }
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
    if (!opts.split) {
      for (const v of views) v.state.fit = 1;
      return { vertical: false, buffer: [{ w: W, h: H }] };
    }
    const v = narrow();
    const bw = v ? W : Math.round(W * 0.62), bh = v ? Math.round(H / 2) : H;
    for (const x of views) x.state.fit = v ? 1 : 0.5 / 0.62;
    return { vertical: v, buffer: [{ w: bw, h: bh }, { w: bw, h: bh }] };
  };
  const resize = () => {
    const r = view.getBoundingClientRect();
    W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
    stage.resize(W, H, layout());
    opts.onResize?.(W, H);
  };
  new ResizeObserver(resize).observe(view);
  resize();

  let time = 0;
  const ctx = { stage, views, rects: [], get W() { return W; }, get H() { return H; }, parallax, reduce };
  root.hubContext = ctx;              // handy for debugging in devtools
  function render(dt) {
    time += dt;
    const k = reduce ? 1 : 1 - Math.exp(-dt * 7);
    split.value += (split.target - split.value) * k;
    tint.forEach((x, i) => { x.v += (x.t - x.v) * k; views[i].tint?.(x.v); });
    const kp = 1 - Math.exp(-dt * 3);
    parallax.x += (parallax.tx - parallax.x) * kp;
    parallax.y += (parallax.ty - parallax.y) * kp;
    for (const v of views) { v.state.parallax = [parallax.x, parallax.y]; v.step(dt); }
    root.style.setProperty("--split", split.value.toFixed(4));
    const lay = stage.layout;
    let rects;
    if (!opts.split) rects = [{ x: 0, y: 0, w: W, h: H }];
    else if (lay.vertical) rects = [{ x: 0, y: H / 2, w: W, h: H / 2 }, { x: 0, y: 0, w: W, h: H / 2 }];
    else rects = [{ x: 0, y: 0, w: W * split.value, h: H }, { x: W * split.value, y: 0, w: W * (1 - split.value), h: H }];
    ctx.rects = rects;
    stage.render(rects, time);
    opts.onFrame?.(dt, ctx);
  }

  let running = true, visible = true, last = performance.now();
  const loop = (now) => {
    if (!running) return;
    const dt = Math.min(0.05, Math.max(0, (now - last) / 1000));
    last = now;
    if (visible && !document.hidden) { render(dt); stage.observe(dt); }
    requestAnimationFrame(loop);
  };
  canvas.addEventListener("webglcontextlost", (e) => { e.preventDefault(); running = false; root.dataset.state = "fallback"; });
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(root);

  if (reduce) {
    opts.warmup?.(views);
    render(0);
    root.dataset.state = "ready";
    return ctx;
  }
  render(1 / 60);
  root.dataset.state = "ready";
  const tl = gsap.timeline({ defaults: { ease: "expo.out" } });
  tl.to(canvas, { opacity: 1, duration: 0.6, ease: "power1.out" }, 0);
  opts.intro?.(tl, views);
  requestAnimationFrame(loop);
  return ctx;
}

/** Fetch JSON relative to the site root; throws on HTTP errors. */
export async function getJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}
