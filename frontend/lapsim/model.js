// Quasi-steady-state lap simulation — browser port of vehicle_dynamics (Python).
// Same equations, same envelope table and the same Heun integration; frontend/lapsim/model.test.mjs
// checks the lap time and speed trace against the Python reference stored in lapsim-bahrain.json.
// SI units throughout.

export const G = 9.80665;

// ---------------------------------------------------------------------------------------------
// Pacejka Magic Formula, pure slip (MF 6.1 structure, no camber)
// ---------------------------------------------------------------------------------------------
export function tyre(p) {
  const dfz = fz => (fz - p.fz0) / p.fz0;
  const dpi = pr => (pr - p.p0) / p.p0;
  const muY = (fz, pr = p.p0) => (p.pDy1 + p.pDy2 * dfz(fz)) * (1 + p.ppy3 * dpi(pr) + p.ppy4 * dpi(pr) ** 2) * p.lambda_muy;
  const muX = fz => (p.pDx1 + p.pDx2 * dfz(fz)) * p.lambda_mux;
  const ky = (fz, pr = p.p0) => p.pKy1 * p.fz0 * (1 + p.ppy1 * dpi(pr)) * Math.sin(2 * Math.atan(fz / (p.pKy2 * (1 + p.ppy2 * dpi(pr)) * p.fz0)));
  const mf = (x, B, C, D, E) => D * Math.sin(C * Math.atan(B * x - E * (B * x - Math.atan(B * x))));
  return {
    muY, muX, ky,
    fy(alpha, fz, pr = p.p0) {
      const D = muY(fz, pr) * fz, C = p.pCy1, B = ky(fz, pr) / (C * D + 1e-12);
      return mf(alpha, B, C, D, Math.min(p.pEy1, 1));
    },
    fx(kappa, fz) {
      const D = muX(fz) * fz, C = p.pCx1, K = fz * (p.pKx1 + p.pKx2 * dfz(fz)), B = K / (C * D + 1e-12);
      return mf(kappa, B, C, D, Math.min(p.pEx1, 1));
    },
  };
}

// ---------------------------------------------------------------------------------------------
// Car: loads, friction-ellipse feasibility, envelope
// ---------------------------------------------------------------------------------------------
export function car(c) {
  const t = tyre(c.tyre);
  const m = c.mass, l = c.wheelbase, h = c.h_cg;
  const b = l * c.front_weight, a = l * (1 - c.front_weight);
  const q = v => 0.5 * c.rho * v * v;
  const capX = fz => (fz > 0 ? t.muX(fz) * fz : 0);
  const capY = fz => (fz > 0 ? t.muY(fz) * fz : 0);

  function loads(ax, ay, v) {
    const lift = q(v) * c.cla;
    const fzf = m * G * b / l - m * ax * h / l + lift * c.aero_balance;
    const fzr = m * G * a / l + m * ax * h / l + lift * (1 - c.aero_balance);
    const dyf = c.roll_share_f * m * ay * h / c.track_f, dyr = (1 - c.roll_share_f) * m * ay * h / c.track_r;
    return [fzf / 2 - dyf, fzf / 2 + dyf, fzr / 2 - dyr, fzr / 2 + dyr];
  }

  function feasible(ax, ay, v, grade = 0) {
    const [fl, fr, rl, rr] = loads(ax, ay, v).map(w => Math.max(w, 0));
    const cxf = capX(fl) + capX(fr), cyf = capY(fl) + capY(fr), cxr = capX(rl) + capX(rr), cyr = capY(rl) + capY(rr);
    const fxTot = m * ax + q(v) * c.cda + c.crr * m * G + m * G * Math.sin(grade);
    const traction = fxTot >= 0;
    const fxf = traction ? 0 : c.brake_balance * fxTot, fxr = traction ? fxTot : (1 - c.brake_balance) * fxTot;
    const fyf = m * ay * b / l, fyr = m * ay * a / l;
    const uf = (fxf / Math.max(cxf, 1e-9)) ** 2 + (fyf / Math.max(cyf, 1e-9)) ** 2;
    const ur = (fxr / Math.max(cxr, 1e-9)) ** 2 + (fyr / Math.max(cyr, 1e-9)) ** 2;
    if (Math.sqrt(Math.max(uf, ur)) > 1) return false;
    return !traction || fxr * Math.max(v, 1e-6) <= c.power;
  }

  const coastAx = (v, grade = 0) => -(q(v) * c.cda + c.crr * m * G) / m - G * Math.sin(grade);

  function ayMax(v, iters = 48) {
    let lo = 0, hi = 8 * G;
    for (let i = 0; i < iters; i++) { const mid = 0.5 * (lo + hi); if (feasible(0, mid, v)) lo = mid; else hi = mid; }
    return lo;
  }

  function axLimits(v, ay, grade = 0, iters = 48) {
    const coast = coastAx(v, grade);
    if (!feasible(coast, ay, v, grade)) return [NaN, NaN];
    let lo = coast, hi = coast + 4 * G;
    for (let i = 0; i < iters; i++) { const mid = 0.5 * (lo + hi); if (feasible(mid, ay, v, grade)) lo = mid; else hi = mid; }
    const axMax = lo;
    lo = coast - 8 * G; hi = coast;
    for (let i = 0; i < iters; i++) { const mid = 0.5 * (lo + hi); if (feasible(mid, ay, v, grade)) hi = mid; else lo = mid; }
    return [axMax, hi];
  }

  function topSpeed() {
    let lo = 1, hi = 200;
    for (let i = 0; i < 80; i++) { const mid = 0.5 * (lo + hi); const need = (q(mid) * c.cda + c.crr * m * G) * mid; if (need < c.power) lo = mid; else hi = mid; }
    return lo;
  }

  return { params: c, tyre: t, loads, feasible, coastAx, ayMax, axLimits, topSpeed, aero: v => [q(v) * c.cda, q(v) * c.cla] };
}

// ---------------------------------------------------------------------------------------------
// g-g-V table and lookup (identical grid to vehicle_dynamics.qss.Envelope)
// ---------------------------------------------------------------------------------------------
export function envelope(k, { dv = 1, nFrac = 33 } = {}) {
  const top = k.topSpeed();
  const v = [];
  for (let x = 2; x < top + 2 * dv - 1e-9; x += dv) v.push(x);
  const frac = Array.from({ length: nFrac }, (_, j) => j / (nFrac - 1));
  const ayMax = v.map(x => k.ayMax(x));
  const axMax = [], axMin = [], power = [];
  const c = k.params;
  v.forEach((x, i) => {
    const rowP = [], rowN = [], rowW = [];
    frac.forEach(f => {
      let [p, n] = k.axLimits(x, ayMax[i] * f);
      const coast = k.coastAx(x);
      if (Number.isNaN(p)) p = coast;
      if (Number.isNaN(n)) n = coast;
      rowP.push(p); rowN.push(n);
      const fx = c.mass * p + k.aero(x)[0] + c.crr * c.mass * G;
      rowW.push(fx * x >= 0.995 * c.power);
    });
    axMax.push(rowP); axMin.push(rowN); power.push(rowW);
  });
  function lookup(speed, ay) {
    let i = 0, hi = v.length - 1;
    // searchsorted(v, speed) - 1, clipped
    let lo = 0;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (v[mid] < speed) lo = mid + 1; else hi = mid; }
    i = Math.min(Math.max(lo - 1, 0), v.length - 2);
    const tv = Math.min(Math.max((speed - v[i]) / (v[i + 1] - v[i]), 0), 1);
    const aym = ayMax[i] * (1 - tv) + ayMax[i + 1] * tv;
    const f = Math.min(Math.abs(ay) / Math.max(aym, 1e-9), 1);
    const nf = frac.length - 1, j = Math.min(Math.floor(f * nf), nf - 1), tf = f * nf - j;
    const bil = tab => (tab[i][j] * (1 - tf) + tab[i][j + 1] * tf) * (1 - tv) + (tab[i + 1][j] * (1 - tf) + tab[i + 1][j + 1] * tf) * tv;
    return [bil(axMax), bil(axMin), aym, tv < 0.5 ? power[i][j] : power[i + 1][j]];
  }
  return { v, frac, ayMax, axMax, axMin, power, lookup };
}

function cornerSpeed(kappa, env) {
  const v = env.v, n = v.length;
  return kappa.map(kk => {
    const k = Math.abs(kk);
    let last = -1;
    for (let i = n - 1; i >= 0; i--) if (env.ayMax[i] - v[i] * v[i] * k >= 0) { last = i; break; }
    if (last < 0) return v[0];
    if (last >= n - 1) return v[n - 1];
    const r0 = env.ayMax[last] - v[last] ** 2 * k, r1 = env.ayMax[last + 1] - v[last + 1] ** 2 * k;
    const out = r0 !== r1 ? v[last] + (v[last + 1] - v[last]) * r0 / (r0 - r1) : v[last];
    return Math.min(out, v[n - 1]);
  });
}

export const REGIMES = ['curva', 'tração · potência', 'tração · aderência', 'frenagem'];

// track: {s:[], kappa:[], grade:[], length}
export function simulate(k, track, env = envelope(k)) {
  const n = track.s.length, L = track.length;
  const ds = track.s.map((s, i) => (i + 1 < n ? track.s[i + 1] : L) - s);
  const kap = track.kappa, gs = track.grade.map(g => G * Math.sin(g));
  const vc = cornerSpeed(kap, env);
  let start = 0;
  for (let i = 1; i < n; i++) if (vc[i] < vc[start]) start = i;
  const order = i => (start + i) % n;

  const fwd = vc.slice(), pl = new Array(n).fill(false);
  let v = vc[start];
  for (let w = 0; w < 2; w++) for (let idx = 0; idx < n; idx++) {
    const i = order(idx), j = order(idx + 1);
    const [axp, , , plim] = env.lookup(v, v * v * kap[i]);
    const vp = Math.sqrt(Math.max(v * v + 2 * (axp - gs[i]) * ds[i], 0));
    const [axq] = env.lookup(vp, vp * vp * kap[j]);
    const vn = Math.min(Math.sqrt(Math.max(v * v + (axp - gs[i] + axq - gs[j]) * ds[i], 0)), vc[j]);
    if (vn < fwd[j]) { fwd[j] = vn; pl[j] = plim; }
    v = vn;
  }
  const bwd = vc.slice();
  v = vc[start];
  for (let w = 0; w < 2; w++) for (let idx = n; idx > 0; idx--) {
    const j = order(idx % n), i = order(idx - 1);
    const [, axn] = env.lookup(v, v * v * kap[j]);
    const vq = Math.sqrt(Math.max(v * v - 2 * (axn - gs[j]) * ds[i], 0));
    const [, axm] = env.lookup(vq, vq * vq * kap[i]);
    const vp = Math.min(Math.sqrt(Math.max(v * v - (axn - gs[j] + axm - gs[i]) * ds[i], 0)), vc[i]);
    bwd[i] = Math.min(bwd[i], vp);
    v = vp;
  }
  const speed = fwd.map((f, i) => Math.min(f, bwd[i]));
  const time = new Array(n), ax = new Array(n), ay = new Array(n), regime = new Array(n);
  let t = 0;
  for (let i = 0; i < n; i++) {
    const nx = speed[(i + 1) % n];
    time[i] = t;
    t += 2 * ds[i] / Math.max(speed[i] + nx, 1e-6);
    ax[i] = (nx * nx - speed[i] ** 2) / (2 * ds[i]);
    ay[i] = speed[i] ** 2 * kap[i];
    regime[i] = speed[i] >= vc[i] - 1e-3 ? 0 : bwd[i] < fwd[i] - 1e-6 ? 3 : pl[i] ? 1 : 2;
  }
  return { s: track.s, v: speed, vCorner: vc, ax, ay, regime, time, lapTime: t };
}

// convenience: build a car from the JSON "car" block with overrides
export function carFrom(json, overrides = {}) {
  const c = { ...json, tyre: { ...json.tyre } };
  for (const [key, val] of Object.entries(overrides)) {
    if (key === 'lambda_muy' || key === 'lambda_mux') c.tyre[key] = val; else c[key] = val;
  }
  return car(c);
}
