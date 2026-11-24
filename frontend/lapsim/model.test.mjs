// Cross-check of the browser port against the Python reference (vehicle_dynamics) on the same
// calibrated car and the same 4 m track exported in lapsim-bahrain.json.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { carFrom, envelope, simulate, tyre, G } from './model.js';

const data = JSON.parse(readFileSync(new URL('../../site/motorsport/data/lapsim-bahrain.json', import.meta.url)));
const track = { s: data.track.s, kappa: data.track.kappa, grade: data.track.grade, length: data.track.length_m };

test('lap time matches the Python reference within 0.05 %', () => {
  const res = simulate(carFrom(data.car), track);
  assert.ok(Math.abs(res.lapTime / data.sim.site_lap_time_s - 1) < 5e-4, `${res.lapTime} vs ${data.sim.site_lap_time_s}`);
});

test('speed trace matches the Python reference within 1 km/h everywhere', () => {
  const res = simulate(carFrom(data.car), track);
  let worst = 0;
  data.sim.v_kmh.forEach((v, i) => { worst = Math.max(worst, Math.abs(res.v[i] * 3.6 - v)); });
  assert.ok(worst < 1.0, `worst ${worst} km/h`);
});

test('envelope agrees with the Python g-g-V table', () => {
  const env = envelope(carFrom(data.car));
  data.ggv.ay_max_g.forEach((ay, i) => assert.ok(Math.abs(env.ayMax[i] / G - ay) < 2e-3));
});

test('tyre: slope at the origin equals cornering stiffness and the peak equals mu*Fz', () => {
  const t = tyre(data.car.tyre), h = 1e-6;
  const slope = (t.fy(h, 4000) - t.fy(-h, 4000)) / (2 * h);
  assert.ok(Math.abs(slope / t.ky(4000) - 1) < 1e-5);
  let peak = 0;
  for (let a = 0; a < 0.4; a += 1e-5) peak = Math.max(peak, t.fy(a, 3500));
  assert.ok(Math.abs(peak / (t.muY(3500) * 3500) - 1) < 1e-4);
});

test('constant-radius circle: lap time is 2πR/√(μgR)', () => {
  const R = 80, n = 250, mu = 1.6;
  const s = Array.from({ length: n }, (_, i) => i * 2 * Math.PI * R / n);
  const circle = { s, kappa: s.map(() => 1 / R), grade: s.map(() => 0), length: 2 * Math.PI * R };
  const k = carFrom({ ...data.car_base, cla: 0, cda: 0, crr: 0,
    tyre: { ...data.car_base.tyre, pDy1: mu, pDy2: 0, pDx1: mu, pDx2: 0, ppy3: 0, ppy4: 0, lambda_muy: 1, lambda_mux: 1 } });
  const res = simulate(k, circle);
  const expected = 2 * Math.PI * R / Math.sqrt(mu * G * R);
  assert.ok(Math.abs(res.lapTime / expected - 1) < 1e-3, `${res.lapTime} vs ${expected}`);
});
