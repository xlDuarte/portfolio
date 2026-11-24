// node --test frontend/
import { test } from "node:test";
import assert from "node:assert/strict";
import { blackbodyRGB, createBlackbodyLUT, planck } from "./blackbody.js";
import { G0, RigidBody, SparkField, SpringDamper, STEEL_SPARK } from "./physics.js";

test("Planck peak follows Wien's displacement law", () => {
  const T = 5000;
  let best = 0, peak = 0;
  for (let l = 200; l <= 2000; l += 1) { const b = planck(l, T); if (b > best) { best = b; peak = l; } }
  assert.ok(Math.abs(peak - 2.897771955e6 / T) < 3, `peak ${peak} nm`);
});

test("black-body colour: D65-like white at 6500 K, orange at 1500 K", () => {
  const [r, g, b] = blackbodyRGB(6500);
  for (const c of [r, g, b]) assert.ok(c > 0.85, `6500 K channel ${c}`);
  const [r2, g2, b2] = blackbodyRGB(1500);
  assert.equal(r2, 1);
  assert.ok(g2 < 0.5 && b2 < 0.1 && g2 > b2, `1500 K ${[r2, g2, b2]}`);
  const lut = createBlackbodyLUT();
  assert.ok(Math.abs(lut.sample(1500)[1] - g2) < 0.02);
  assert.equal(lut.radiance(3000, 1500), 16);
});

test("spark in vacuum-like conditions follows the ballistic parabola", () => {
  const f = new SparkField(1, { ...STEEL_SPARK, drag: 0, convection: 0, radiation: 0, visibleK: 0 });
  f.emit(0, 0, 0, 3, 4, 0, 1800);
  f.step(0.5, () => -1e9);
  assert.ok(Math.abs(f.px[0] - 1.5) < 1e-3);
  assert.ok(Math.abs(f.py[0] - (4 * 0.5 - 0.5 * G0 * 0.25)) < 0.02);
});

test("drag slows sparks and cooling ends them", () => {
  const f = new SparkField(4);
  f.emit(0, 1, 0, 6, 2, 0, 1900);
  f.step(0.1, () => 0);
  assert.ok(Math.hypot(f.vx[0], f.vz[0]) < 6, "drag must reduce horizontal speed");
  for (let i = 0; i < 60; i++) f.step(0.05, () => 0);
  assert.equal(f.count, 0, "spark should cool below the visible threshold within 3 s");
});

test("bounces lose energy (restitution) and never pass through the ground", () => {
  const f = new SparkField(1, { ...STEEL_SPARK, convection: 0, radiation: 0, contactCoolingK: 0, drag: 0 });
  f.emit(0, 1, 0, 0, 0, 0, 1800);
  let apex = 0, falling = true, prev = 1;
  for (let i = 0; i < 400; i++) {
    f.step(1 / 240, () => 0);
    assert.ok(f.py[0] >= 0);
    if (falling && f.vy[0] > 0) falling = false;
    if (!falling) { apex = Math.max(apex, f.py[0]); if (f.vy[0] < 0 && f.py[0] < prev) break; }
    prev = f.py[0];
  }
  const e = STEEL_SPARK.restitution;
  assert.ok(Math.abs(apex - e * e) < 0.03, `apex ${apex} vs ${e * e}`);
});

test("rigid body comes to rest on the floor without gaining energy", () => {
  const floor = { min: [-10, -1, -10], max: [10, 0, 10] };
  const body = new RigidBody({ position: [0, 1, 0], velocity: [1.5, 0, 0], spin: [0, 0, 4], radius: 0.1 });
  let e0 = body.energy();
  for (let i = 0; i < 2400 && !body.sleeping; i++) {
    body.step(1 / 240, [floor]);
    const e = body.energy();
    assert.ok(e <= e0 + 1e-6, "energy must not increase");
    e0 = e;
  }
  assert.ok(body.sleeping, "body should settle");
  assert.ok(Math.abs(body.p[1] - 0.1) < 0.01);
});

test("spring-damper step response overshoot matches theory for ζ = 0.7", () => {
  const s = new SpringDamper(2, 0.7);
  let peak = 0;
  for (let i = 0; i < 480; i++) peak = Math.max(peak, s.step(1, 1 / 240));
  const theory = Math.exp((-0.7 * Math.PI) / Math.sqrt(1 - 0.49));
  assert.ok(Math.abs(peak - 1 - theory) < 0.01, `overshoot ${peak - 1} vs ${theory}`);
});

import { Turntable } from "./physics.js";
test("turntable: a flick decays back to the idle speed, never overshooting into reverse", () => {
  const t = new Turntable({ idle: 0.2 });
  t.impulse(6);
  let minOmega = Infinity;
  for (let i = 0; i < 240 * 30; i++) { t.step(1 / 240); minOmega = Math.min(minOmega, t.omega); }
  assert.ok(Math.abs(t.omega - 0.2) < 0.05, `omega ${t.omega}`);
  assert.ok(minOmega > -1e-9, "must not spin backwards");
});
