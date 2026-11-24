// Stochastic dynamic programme for pit stops with safety cars — browser port of
// race_strategy.strategy.sdp (Python). Same state space, same Bellman recursion, same cost model;
// frontend/strategy/sdp.test.mjs checks the expected values against the Python reference.

export const S = 0, H = 1;

// pace: {delta_h, beta_s, beta_h, v}
export function lapCost(p, c, a) {
  const b = (c === H ? p.beta_h : p.beta_s) + p.v;
  return (c === H ? p.delta_h : 0) + b * a;
}

export function sdp(p, { pitGreen, pitSC, pSC, scLaps = 4, laps = 57, startCompound = S, startAge = 3, maxAge = 60 }) {
  const A = maxAge + 1, INF = 1e9, NS = scLaps + 1;
  const idx = (s, c, a, m) => ((s * 2 + c) * A + a) * 4 + m;
  let V = new Float64Array(NS * 2 * A * 4).fill(INF);
  for (let s = 0; s < NS; s++) for (let c = 0; c < 2; c++) for (let a = 0; a < A; a++) V[idx(s, c, a, 3)] = 0;
  // policy[n][s][c][a][m] packed: −1 stay, 0 pit soft, 1 pit hard
  const policy = new Int8Array((laps + 1) * NS * 2 * A * 4).fill(-1);
  const pidx = (n, s, c, a, m) => (((n * NS + s) * 2 + c) * A + a) * 4 + m;
  for (let n = laps; n >= 1; n--) {
    const Vn = new Float64Array(V.length).fill(INF);
    for (let c = 0; c < 2; c++) for (let m = 0; m < 4; m++) {
      if (!((m >> c) & 1)) continue;
      for (let s = 0; s < NS; s++) {
        const under = s > 0;
        const nxt = under ? [[s - 1, 1]] : (n < laps ? [[0, 1 - pSC], [scLaps, pSC]] : [[0, 1]]);
        for (let a = 0; a < A; a++) {
          const lap = under ? 0 : lapCost(p, c, a);
          const an = Math.min(a + 1, maxAge);
          let best = 0;
          for (const [s2, w] of nxt) best += w * V[idx(s2, c, an, m)];
          let act = -1;
          if (n < laps) {
            const loss = under ? pitSC : pitGreen;
            for (let c2 = 0; c2 < 2; c2++) {
              const m2 = m | (1 << c2);
              let go = loss;
              for (const [s2, w] of nxt) go += w * V[idx(s2, c2, 0, m2)];
              if (go < best) { best = go; act = c2; }
            }
          }
          Vn[idx(s, c, a, m)] = lap + best;
          policy[pidx(n, s, c, a, m)] = act;
        }
      }
    }
    V = Vn;
  }
  return {
    expected: V[idx(0, startCompound, startAge, 1 << startCompound)],
    action: (n, s, c, a, m) => policy[pidx(n, s, c, Math.min(a, maxAge), m)],
  };
}

// Monte Carlo of a policy (seeded so the page is reproducible)
export function mulberry32(seed) {
  let t = seed >>> 0;
  return () => { t += 0x6D2B79F5; let r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; };
}

export function simulate(p, pol, { pitGreen, pitSC, pSC, scLaps = 4, laps = 57, startCompound = S, startAge = 3, races = 2000, seed = 11 }) {
  const rnd = mulberry32(seed), out = new Float64Array(races);
  for (let r = 0; r < races; r++) {
    let c = startCompound, a = startAge, m = 1 << startCompound, s = 0, cost = 0;
    for (let n = 1; n <= laps; n++) {
      const under = s > 0;
      if (!under) cost += lapCost(p, c, a);
      const act = pol.action(n, s, c, a, m);
      if (n < laps && act >= 0) { cost += under ? pitSC : pitGreen; c = act; a = 0; m |= 1 << act; } else a += 1;
      if (under) s -= 1; else if (n < laps && rnd() < pSC) s = scLaps;
    }
    out[r] = m === 3 ? cost : Infinity;
  }
  return out;
}

// Fixed plan that does not react to safety cars. plan: {compounds:[...], stops:[...]}
export function simulateStatic(p, plan, { pitGreen, pitSC, pSC, scLaps = 4, laps = 57, startAge = 3, races = 2000, seed = 11 }) {
  const rnd = mulberry32(seed), out = new Float64Array(races);
  const bounds = [0, ...plan.stops, laps], comp = new Int8Array(laps + 1);
  plan.compounds.forEach((c, i) => { for (let n = bounds[i] + 1; n <= bounds[i + 1]; n++) comp[n] = c; });
  const pits = new Set(plan.stops);
  for (let r = 0; r < races; r++) {
    let a = plan.compounds[0] === S ? startAge : 0, s = 0, cost = 0;
    for (let n = 1; n <= laps; n++) {
      const under = s > 0;
      if (!under) cost += lapCost(p, comp[n], a);
      if (pits.has(n)) { cost += under ? pitSC : pitGreen; a = 0; } else a += 1;
      if (under) s -= 1; else if (n < laps && rnd() < pSC) s = scLaps;
    }
    out[r] = cost;
  }
  return out;
}
