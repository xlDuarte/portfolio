// Cross-check of the browser SDP against the Python reference values in strategy-bayes.json, and
// two closed-form checks.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { sdp, simulate, lapCost, S, H } from './sdp.js';

const data = JSON.parse(readFileSync(new URL('../../site/motorsport/data/strategy-bayes.json', import.meta.url)));
const base = data.sdp;

test('expected strategy cost matches Python for every safety-car rate', () => {
  for (const row of base.rows) {
    const r = sdp(base.pace, { pitGreen: base.pit_green_s, pitSC: base.pit_sc_ratio * base.pit_green_s, pSC: row.p_sc, scLaps: base.sc_laps, laps: 57, startCompound: S, startAge: 3 });
    assert.ok(Math.abs(r.expected - row.sdp_expected_start_soft_s) < 1e-3, `${r.expected} vs ${row.sdp_expected_start_soft_s}`);
  }
});

test('without safety cars the policy cost equals the best fixed plan', () => {
  const p = base.pace, plan = base.static_plan;
  const bounds = [0, ...plan.stops, 57];
  let cost = 0;
  plan.compounds.forEach((c, i) => { for (let a = (i === 0 && c === S ? 3 : 0), n = bounds[i]; n < bounds[i + 1]; n++, a++) cost += lapCost(p, c, a); });
  cost += plan.stops.length * base.pit_green_s;
  const r = sdp(p, { pitGreen: base.pit_green_s, pitSC: base.pit_green_s / 2, pSC: 0, laps: 57 });
  assert.ok(Math.abs(r.expected - cost) < 1e-6, `${r.expected} vs ${cost}`);
});

test('Monte Carlo of the policy agrees with its expectation', () => {
  const opts = { pitGreen: base.pit_green_s, pitSC: base.pit_green_s / 2, pSC: 0.02, scLaps: 4, laps: 57 };
  const r = sdp(base.pace, opts);
  const mc = simulate(base.pace, r, { ...opts, races: 6000, seed: 3 });
  const mean = mc.reduce((a, b) => a + b, 0) / mc.length;
  const sd = Math.sqrt(mc.reduce((a, b) => a + (b - mean) ** 2, 0) / (mc.length - 1));
  assert.ok(Math.abs(mean - r.expected) < 4 * sd / Math.sqrt(mc.length), `${mean} vs ${r.expected}`);
});
