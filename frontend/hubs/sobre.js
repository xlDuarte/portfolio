// Sobre: horizontal career timeline. Native horizontal scrolling everywhere (touch, trackpad,
// keyboard); with a mouse it can also be thrown: release velocity decays with exponential
// friction (v' = −k v, k = 4/s). Buttons and arrow keys move one stop at a time; a progress rule
// follows the scroll position.
import { gsap } from "gsap";

export function mount(root) {
  const track = root.querySelector(".tl-scroller");
  const list = root.querySelector(".tl-track");
  const bar = root.querySelector(".tl-progress span");
  const prev = root.querySelector("[data-tl-prev]"), next = root.querySelector("[data-tl-next]");
  if (!track || !list) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  // Scroll offsets that bring each item to the left padding edge.
  const stops = () => {
    const pad = parseFloat(getComputedStyle(list).paddingLeft) || 0;
    const base = track.getBoundingClientRect().left - track.scrollLeft;
    return [...list.querySelectorAll(":scope > li")].map((li) => Math.max(0, li.getBoundingClientRect().left - base - pad));
  };
  const update = () => {
    const max = track.scrollWidth - track.clientWidth;
    const p = max > 0 ? track.scrollLeft / max : 1;
    if (bar) bar.style.transform = `scaleX(${p.toFixed(4)})`;
    if (prev) prev.disabled = track.scrollLeft <= 2;
    if (next) next.disabled = track.scrollLeft >= max - 2;
  };
  const go = (dir) => {
    const x = track.scrollLeft, s = stops();
    const target = dir > 0 ? s.find((v) => v > x + 4) : [...s].reverse().find((v) => v < x - 4);
    if (target === undefined) return;
    if (reduce) track.scrollLeft = target;
    else gsap.to(track, { scrollLeft: target, duration: 0.7, ease: "power3.out", onUpdate: update });
  };
  prev?.addEventListener("click", () => go(-1));
  next?.addEventListener("click", () => go(1));
  track.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") { e.preventDefault(); go(1); }
    if (e.key === "ArrowLeft") { e.preventDefault(); go(-1); }
  });
  track.addEventListener("scroll", update, { passive: true });
  if (!reduce && matchMedia("(pointer: fine)").matches) {
    let down = false, lastX = 0, lastT = 0, vel = 0, raf = 0, moved = 0;
    const glide = () => {
      let t0 = performance.now();
      const tick = (now) => {
        const dt = Math.min(0.05, (now - t0) / 1000); t0 = now;
        vel *= Math.exp(-4 * dt);
        track.scrollLeft -= vel * dt;
        update();
        if (Math.abs(vel) > 20) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    };
    track.style.cursor = "grab";
    track.addEventListener("pointerdown", (e) => {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      cancelAnimationFrame(raf); down = true; moved = 0; vel = 0; lastX = e.clientX; lastT = performance.now();
      track.style.cursor = "grabbing";
    });
    addEventListener("pointermove", (e) => {
      if (!down) return;
      const now = performance.now(), dx = e.clientX - lastX;
      track.scrollLeft -= dx; moved += Math.abs(dx);
      vel = 0.8 * vel + 0.2 * (dx / Math.max(0.008, (now - lastT) / 1000));
      lastX = e.clientX; lastT = now;
    });
    addEventListener("pointerup", () => { if (!down) return; down = false; track.style.cursor = "grab"; glide(); });
    track.addEventListener("click", (e) => { if (moved > 6) { e.preventDefault(); e.stopPropagation(); } }, true);
  }
  update();
  root.dataset.state = "ready";
}
