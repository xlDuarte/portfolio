// Lap simulator page: loads the calibrated Bahrain dataset, recomputes the envelope and the lap in
// the browser when the car changes, and draws the map, the speed trace, the tables and the 3D g-g-V.
import { carFrom, envelope, simulate, REGIMES, G } from './model.js';
import { el, text, clear, fmt, lines, heat, tornado, richHTML, REGIME_COLORS } from './charts.js';

const DATA_URL = '/motorsport/data/lapsim-bahrain.json';
const root = document.getElementById('lapsim');
const $ = id => document.getElementById(id);

const SLIDERS = [
  { key: 'mass', label: 'Massa', unit: 'kg', min: 780, max: 1000, step: 1, show: v => fmt(v, 0) },
  { key: 'power', label: 'Potência nas rodas', unit: 'kW', min: 400e3, max: 820e3, step: 5e3, show: v => fmt(v / 1e3, 0) },
  { key: 'cla', label: 'Downforce C_L·A', unit: 'm²', min: 1, max: 7, step: 0.05, show: v => fmt(v, 2) },
  { key: 'cda', label: 'Arrasto C_D·A', unit: 'm²', min: 0.6, max: 2.4, step: 0.01, show: v => fmt(v, 2) },
  { key: 'lambda_muy', label: 'Aderência lateral λ_μy', unit: '', min: 0.6, max: 1.4, step: 0.005, show: v => fmt(v, 3) },
  { key: 'lambda_mux', label: 'Aderência longitudinal λ_μx', unit: '', min: 0.4, max: 1.3, step: 0.005, show: v => fmt(v, 3) },
  { key: 'aero_balance', label: 'Balanço aerodinâmico (dianteira)', unit: '%', min: 0.3, max: 0.55, step: 0.005, show: v => fmt(v * 100, 1) },
  { key: 'h_cg', label: 'Altura do CG', unit: 'mm', min: 0.2, max: 0.4, step: 0.005, show: v => fmt(v * 1000, 0) },
];
const DRV_COLOR = { VER: '#b8122b', PER: '#1d4e9e', SAI: '#a85d00' };

let data, track, calibratedCar, calibrated, current, pinned = null, ggv = null, imported = null;
const values = {};

function base(key) {
  return key.startsWith('lambda') ? data.car.tyre[key] : data.car[key];
}

function trackFrom(t) {
  return { s: t.s, kappa: t.kappa, grade: t.grade, length: t.length_m, x: t.x, y: t.y };
}

// ------------------------------------------------------------------------------------- controls
function buildSliders() {
  const box = $('ls-sliders');
  SLIDERS.forEach(s => {
    values[s.key] = base(s.key);
    const id = 'ls-in-' + s.key;
    const row = document.createElement('div');
    row.className = 'ls-slider';
    row.innerHTML = `<label for="${id}">${richHTML(s.label)}</label><output for="${id}" id="${id}-out"></output>
      <input type="range" id="${id}" min="${s.min}" max="${s.max}" step="${s.step}" value="${values[s.key]}">
      <small id="${id}-cal"></small>`;
    box.append(row);
    const input = row.querySelector('input');
    input.addEventListener('input', () => { values[s.key] = Number(input.value); show(s); schedule(); });
    show(s);
  });
}

function show(s) {
  const id = 'ls-in-' + s.key;
  $(id + '-out').textContent = s.show(values[s.key]) + (s.unit ? ' ' + s.unit : '');
  const d = values[s.key] / base(s.key) - 1;
  $(id + '-cal').textContent = Math.abs(d) < 1e-9 ? 'calibrado' : (d > 0 ? '+' : '') + fmt(d * 100, 1) + ' % do calibrado';
}

let pending = 0;
function schedule() {
  cancelAnimationFrame(pending);
  pending = requestAnimationFrame(run);
}

function run() {
  const k = carFrom(data.car, values);
  const env = envelope(k);
  const res = simulate(k, imported || track, env);
  current = { car: k, env, res };
  renderLive();
  if (ggv) ggv.setEnvelope(env, G);
}

// ------------------------------------------------------------------------------------- live output
function renderLive() {
  const r = current.res;
  const set = (k, v) => { root.querySelector(`#ls-live [data-k="${k}"]`).textContent = v; };
  set('lap', fmt(r.lapTime, 3) + ' s');
  const ref = imported ? null : calibrated.lapTime;
  set('delta', ref === null ? '—' : (r.lapTime - ref >= 0 ? '+' : '−') + fmt(Math.abs(r.lapTime - ref), 3) + ' s');
  set('vmax', fmt(Math.max(...r.v) * 3.6, 0) + ' km/h');
  set('vmin', fmt(Math.min(...r.v) * 3.6, 0) + ' km/h');
  regimeBar(r);
  speedChart();
  ggChart();
  drawMap(imported ? mapFromCurvature(imported) : track, r);
}

function regimeBar(r) {
  const n = r.s.length, share = [0, 0, 0, 0];
  for (let i = 0; i < n; i++) {
    const dt = (i + 1 < n ? r.time[i + 1] : r.lapTime) - r.time[i];
    share[r.regime[i]] += dt;
  }
  const bar = $('ls-regime-bar');
  bar.replaceChildren();
  const parts = [];
  share.forEach((t, i) => {
    const pct = 100 * t / r.lapTime;
    parts.push(`${REGIMES[i]} ${fmt(pct, 0)} %`);
    const seg = document.createElement('span');
    seg.style.flexGrow = String(t);
    seg.style.background = REGIME_COLORS[i];
    seg.title = `${REGIMES[i]}: ${fmt(pct, 1)} % do tempo`;
    if (pct >= 9) seg.textContent = `${REGIMES[i]} ${fmt(pct, 0)} %`;
    bar.append(seg);
  });
  bar.setAttribute('aria-label', 'Parcela do tempo de volta em cada regime: ' + parts.join(', '));
}

function speedChart() {
  const svg = $('ls-speed');
  const r = current.res, L = (imported || track).length;
  const series = [];
  const pts = res => res.s.map((s, i) => [s, res.v[i] * 3.6]);
  if (!imported) series.push({ points: pts(calibrated), color: '#8a929c', width: 1.4, dash: '5 4', label: 'Calibrado' });
  if (pinned && pinned.track === (imported || track)) series.push({ points: pts(pinned.res), color: '#59616b', width: 1.4, dash: '2 3', label: 'Referência A' });
  series.push({ points: pts(r), color: '#1c2128', width: 1.9, label: imported ? 'Simulação' : 'Simulação atual' });
  const { x, y, box } = lines(svg, series, { width: 760, height: 320, xLabel: 'distância desde a linha de cronometragem (m)', yLabel: 'km/h',
    xDomain: [0, L], yDomain: [0, 360], xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0) });
  if (!imported) {
    const shown = ['VER', ...[...root.querySelectorAll('[data-drv]')].filter(c => c.checked).map(c => c.dataset.drv)];
    shown.forEach(d => {
      const m = data.measured[d];
      const g = el('g', { fill: DRV_COLOR[d] }, svg);
      m.s.forEach((s, i) => { if (s >= 0 && s <= L) el('circle', { cx: x(s).toFixed(1), cy: y(m.v_kmh[i]).toFixed(1), r: 1.6 }, g); });
      const lx = box.r - 150 + 50 * shown.indexOf(d);
      el('circle', { cx: lx, cy: 10, r: 3, fill: DRV_COLOR[d] }, svg);
      text(svg, lx + 6, 14, d, { 'font-size': 11, fill: '#1c2128' });
    });
  }
  // regime strip
  const strip = el('g', {}, svg);
  const yb = box.b + 2;
  let start = 0;
  for (let i = 1; i <= r.s.length; i++) {
    if (i === r.s.length || r.regime[i] !== r.regime[start]) {
      const s1 = i === r.s.length ? L : r.s[i];
      el('rect', { x: x(r.s[start]).toFixed(1), y: yb, width: Math.max(x(s1) - x(r.s[start]), 0.5).toFixed(1), height: 5, fill: REGIME_COLORS[r.regime[start]] }, strip);
      start = i;
    }
  }
}

function ggChart() {
  const svg = $('ls-gg');
  const r = current.res, env = current.env;
  const box = { l: 56, r: 744, t: 20, b: 290 };
  clear(svg);
  const x = v => box.l + (v + 5) / 10 * (box.r - box.l);            // ay from −5 to +5 g
  const y = v => box.t + (1.8 - v) / 6.8 * (box.b - box.t);          // ax from +1.8 to −5 g
  const g = el('g', { 'font-size': 11, fill: '#59616b' }, svg);
  for (let a = -4; a <= 4; a += 2) { el('line', { x1: x(a), x2: x(a), y1: box.t, y2: box.b, stroke: '#e3e6ea' }, g); text(g, x(a), box.b + 16, fmt(a, 0), { 'text-anchor': 'middle' }); }
  for (let a = -5; a <= 1; a += 1) { el('line', { x1: box.l, x2: box.r, y1: y(a), y2: y(a), stroke: '#e3e6ea' }, g); text(g, box.l - 6, y(a) + 4, fmt(a, 0), { 'text-anchor': 'end' }); }
  text(g, (box.l + box.r) / 2, box.b + 32, 'aceleração lateral (g)', { 'text-anchor': 'middle', fill: '#1c2128' });
  text(g, box.l, box.t - 6, 'aceleração longitudinal (g)', { fill: '#1c2128' });
  [100, 200, 300].forEach((kmh, n) => {
    const i = Math.min(env.v.findIndex(v => v * 3.6 >= kmh), env.v.length - 1);
    if (i < 0) return;
    const pts = [];
    env.frac.forEach((f, j) => pts.push([env.ayMax[i] * f / G, env.axMax[i][j] / G]));
    for (let j = env.frac.length - 1; j >= 0; j--) pts.push([env.ayMax[i] * env.frac[j] / G, env.axMin[i][j] / G]);
    const mirror = pts.map(([a, b]) => [-a, b]).reverse();
    const all = [...pts, ...mirror];
    el('path', { d: all.map(([a, b], k) => (k ? 'L' : 'M') + x(a).toFixed(1) + ' ' + y(b).toFixed(1)).join('') + 'Z', fill: 'none',
      stroke: ['#1d4e9e', '#a85d00', '#b8122b'][n], 'stroke-width': 1.3, 'stroke-dasharray': '4 3' }, svg);
    text(svg, x(env.ayMax[i] / G) + 4, y(0) - 4 - 12 * n, kmh + ' km/h', { 'font-size': 10.5, fill: ['#1d4e9e', '#a85d00', '#b8122b'][n] });
  });
  if (!imported) {
    const m = data.gg_measured.find(c => c.driver === 'VER');
    const pg = el('g', { fill: '#b8122b', 'fill-opacity': 0.55 }, svg);
    m.ay_g.forEach((a, k) => el('circle', { cx: x(a).toFixed(1), cy: y(m.ax_g[k]).toFixed(1), r: 1.7 }, pg));
  }
  let d = '';
  for (let i = 0; i < r.s.length; i += 2) d += (i ? 'L' : 'M') + x(r.ay[i] / G).toFixed(1) + ' ' + y(r.ax[i] / G).toFixed(1);
  el('path', { d, fill: 'none', stroke: '#1c2128', 'stroke-width': 1.1, 'stroke-opacity': 0.85 }, svg);
}

// ------------------------------------------------------------------------------------- map
function mapFromCurvature(t) {
  // integrate heading from curvature to draw an imported track without coordinates
  const x = [0], y = [0];
  let th = 0;
  for (let i = 1; i < t.s.length; i++) {
    const ds = t.s[i] - t.s[i - 1];
    th += t.kappa[i - 1] * ds;
    x.push(x[i - 1] + Math.cos(th) * ds);
    y.push(y[i - 1] + Math.sin(th) * ds);
  }
  return { ...t, x, y };
}

function drawMap(t, r) {
  const svg = $('ls-map');
  clear(svg);
  const W = 600, H = 420, pad = 18;
  const xs = t.x, ys = t.y;
  const minx = Math.min(...xs), maxx = Math.max(...xs), miny = Math.min(...ys), maxy = Math.max(...ys);
  const k = Math.min((W - 2 * pad) / (maxx - minx), (H - 2 * pad) / (maxy - miny));
  const ox = (W - k * (maxx - minx)) / 2, oy = (H - k * (maxy - miny)) / 2;
  const px = v => ox + (v - minx) * k, py = v => H - (oy + (v - miny) * k);
  if (!imported && data.track.ref_x) {
    el('path', { d: data.track.ref_x.map((v, i) => (i ? 'L' : 'M') + px(v).toFixed(1) + ' ' + py(data.track.ref_y[i]).toFixed(1)).join('') + 'Z',
      fill: 'none', stroke: '#c9ced5', 'stroke-width': 7, 'stroke-linejoin': 'round' }, svg);
  }
  let start = 0;
  const n = r.s.length;
  for (let i = 1; i <= n; i++) {
    if (i === n || r.regime[i] !== r.regime[start]) {
      let d = '';
      for (let j = start; j <= Math.min(i, n - 1); j++) d += (j === start ? 'M' : 'L') + px(xs[j]).toFixed(1) + ' ' + py(ys[j]).toFixed(1);
      if (i === n) d += 'L' + px(xs[0]).toFixed(1) + ' ' + py(ys[0]).toFixed(1);
      el('path', { d, fill: 'none', stroke: REGIME_COLORS[r.regime[start]], 'stroke-width': 3.2, 'stroke-linecap': 'round' }, svg);
      start = i;
    }
  }
  // timing line
  el('circle', { cx: px(xs[0]), cy: py(ys[0]), r: 5, fill: '#fff', stroke: '#1c2128', 'stroke-width': 2 }, svg);
  text(svg, px(xs[0]) + 9, py(ys[0]) - 7, 'linha de cronometragem', { 'font-size': 11, fill: '#1c2128' });
  // hover read-out
  const dot = el('circle', { r: 6, fill: 'none', stroke: '#1c2128', 'stroke-width': 2, visibility: 'hidden' }, svg);
  const tip = text(svg, 12, H - 10, '', { 'font-size': 12, fill: '#1c2128' });
  svg.onpointermove = e => {
    const b = svg.getBoundingClientRect();
    const mx = (e.clientX - b.left) * W / b.width, my = (e.clientY - b.top) * H / b.height;
    let best = 0, bd = Infinity;
    for (let i = 0; i < n; i += 2) { const d = (px(xs[i]) - mx) ** 2 + (py(ys[i]) - my) ** 2; if (d < bd) { bd = d; best = i; } }
    if (bd > 900) { dot.setAttribute('visibility', 'hidden'); tip.textContent = ''; return; }
    dot.setAttribute('cx', px(xs[best])); dot.setAttribute('cy', py(ys[best])); dot.setAttribute('visibility', 'visible');
    tip.textContent = `${fmt(r.s[best], 0)} m · ${fmt(r.v[best] * 3.6, 0)} km/h · ${REGIMES[r.regime[best]]} · ` +
      `aₓ ${fmt(r.ax[best] / G, 2)} g · a_y ${fmt(Math.abs(r.ay[best]) / G, 2)} g`;
  };
  svg.onpointerleave = () => { dot.setAttribute('visibility', 'hidden'); tip.textContent = ''; };
}

// ------------------------------------------------------------------------------------- static sections
function table(id, head, rows) {
  const t = $(id);
  t.querySelectorAll('thead,tbody').forEach(e => e.remove());
  const th = t.createTHead().insertRow();
  head.forEach(h => { const c = document.createElement('th'); c.scope = 'col'; c.innerHTML = richHTML(h); th.append(c); });
  const tb = t.createTBody();
  rows.forEach(r => { const tr = tb.insertRow(); r.forEach((v, i) => { const c = i ? tr.insertCell() : document.createElement('th'); if (!i) { c.scope = 'row'; tr.append(c); } c.innerHTML = richHTML(v); }); });
}

const UNIT_FMT = {
  lambda_muy: v => fmt(v, 3), lambda_mux: v => fmt(v, 3), cla: v => fmt(v, 2) + ' m²', cda: v => fmt(v, 2) + ' m²', power: v => fmt(v / 1e3, 0) + ' kW',
};

function staticSections() {
  const c = data.calibration.VER;
  const kp = (k, v) => { root.querySelector(`#ls-kpis [data-k="${k}"]`).textContent = v; };
  kp('sim', fmt(c.lap_time_sim_s, 3) + ' s');
  kp('real', fmt(c.lap_time_meas_s, 3) + ' s');
  kp('rmse', fmt(c.rmse_kmh, 1) + ' km/h');
  kp('r2', fmt(c.r2, 3));
  $('ls-sum-note').textContent = `Volta 3 da corrida, carro com cerca de ${fmt(data.assumptions.mass_kg, 0)} kg (combustível estimado), ` +
    `ar a ${fmt(data.source.weather.air_temperature, 1)} °C e ${fmt(data.assumptions.air_density_kg_m3, 3)} kg/m³. ` +
    `Traçado de ${fmt(data.track.length_m, 0)} m reconstruído das posições do OpenF1. Amostras independentes efetivas: ${fmt(c.n_eff, 0)} de ${c.n}.`;

  const P = data.calibration.params;
  table('ls-params', ['Parâmetro', 'Estimativa', 'Erro-padrão', 'Prior (média ± dp)'], P.map(k => {
    const p = c.params[k], f = UNIT_FMT[k];
    return [p.label, f(p.value), '± ' + f(p.se), `${f(p.prior_mean)} ± ${f(p.prior_sd)}`];
  }));
  heat($('ls-corr'), P.map(k => c.params[k].label), c.corr);

  table('ls-valid', ['Piloto e volta', 'Volta completa na janela', 'Tempo real', 'Erro de velocidade (RMSE)', 'Viés'], data.validation.map(v => [
    `${v.driver} · volta ${v.lap}`, v.complete ? 'sim' : 'parcial', fmt(v.lap_time_meas_s, 3) + ' s', fmt(v.rmse_kmh, 1) + ' km/h', (v.bias_kmh >= 0 ? '+' : '−') + fmt(Math.abs(v.bias_kmh), 1) + ' km/h']));

  const D = data.calibration.per_driver;
  table('ls-drivers', ['Piloto', 'λ_μy', 'λ_μx', 'C_L·A (m²)', 'C_D·A (m²)', 'P (kW)', 'RMSE', 'Volta sim. / real'], Object.entries(D).map(([d, f]) => {
    const pp = k => `${fmt(f.params[k].value, k === 'power' ? 0 : k.startsWith('lambda') ? 3 : 2)}`;
    return [d, pp('lambda_muy') + ' ± ' + fmt(f.params.lambda_muy.se, 3), pp('lambda_mux') + ' ± ' + fmt(f.params.lambda_mux.se, 3),
      pp('cla') + ' ± ' + fmt(f.params.cla.se, 2), pp('cda') + ' ± ' + fmt(f.params.cda.se, 2),
      fmt(f.params.power.value / 1e3, 0) + ' ± ' + fmt(f.params.power.se / 1e3, 0), fmt(f.rmse_kmh, 1) + ' km/h',
      `${fmt(f.lap_time_sim_s, 2)} / ${fmt(f.lap_time_meas_s, 2)} s`];
  }));

  const items = Object.entries(data.sensitivity.items).map(([label, v]) => ({ label, value: v.s_per_pct }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  tornado($('ls-tornado'), items);

  const mc = data.monte_carlo;
  table('ls-mc', ['Estatística', 'Tempo de volta'], [
    ['Sorteios', `${mc.n} (semente ${mc.seed})`], ['Média ± desvio-padrão', `${fmt(mc.mean_s, 2)} ± ${fmt(mc.sd_s, 2)} s`],
    ['Mediana', fmt(mc.q50_s, 2) + ' s'], ['Intervalo de 95 %', `${fmt(mc.q025_s, 2)} a ${fmt(mc.q975_s, 2)} s`]]);

  const conv = data.convergence_ds_m;
  table('ls-conv', ['Passo Δs', 'Tempo de volta'], [
    ...Object.entries(conv).filter(([k]) => k !== 'richardson_s').map(([k, v]) => [fmt(Number(k), 1) + ' m', fmt(v, 3) + ' s']),
    ['Extrapolação de Richardson', fmt(conv.richardson_s, 3) + ' s']]);

  const cor = data.corridor_sensitivity;
  table('ls-corridor', ['Traçado', 'Comprimento', 'Tempo de volta'], [
    ['Mapa do OpenF1 (sem otimizar)', fmt(cor.ref.length_m, 0) + ' m', fmt(cor.ref.lap_time_s, 2) + ' s'],
    ...['3.0', '4.5', '6.0'].map(k => [`Curvatura mínima ±${fmt(Number(k), 1)} m${Number(k) === data.assumptions.half_width_m ? ' (usado)' : ''}`,
      fmt(cor[k].length_m, 0) + ' m', fmt(cor[k].lap_time_s, 2) + ' s'])]);

  // tyre charts
  const T = data.tyre, cols = ['#1d4e9e', '#1b7a48', '#a85d00', '#b8122b'];
  lines($('ls-fy'), T.loads_n.map((fz, i) => ({ points: T.alpha_deg.map((a, j) => [a, T.fy_n[i][j] / 1000]), color: cols[i], label: fmt(fz / 1000, 1) + ' kN' })),
    { width: 420, height: 300, xLabel: 'ângulo de deriva α (°)', yLabel: 'F_y (kN)', xDomain: [0, 14], yDomain: [0, 12], xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0) });
  lines($('ls-mu'), [{ points: T.fz_grid_n.map((fz, i) => [fz / 1000, T.mu_y[i] * data.car.tyre.lambda_muy]), color: '#1c2128', label: 'μ_y de pico' }],
    { width: 420, height: 300, xLabel: 'carga vertical F_z (kN)', yLabel: 'μ', xDomain: [1, 9], yDomain: [1, 2.4], xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 1) });

  const legend = $('ls-map-legend');
  legend.replaceChildren(...REGIMES.map((r, i) => { const li = document.createElement('li'); li.innerHTML = `<span style="background:${REGIME_COLORS[i]}"></span>${r}`; return li; }));
}

// ------------------------------------------------------------------------------------- CSV import
function parseCSV(textIn) {
  const rows = textIn.trim().split(/\r?\n/);
  if (rows.length < 20 || rows.length > 20001) throw Error('Use de 20 a 20.000 linhas.');
  const head = rows[0].split(',').map(h => h.trim());
  const is = head.indexOf('s_m'), ik = head.indexOf('kappa_1pm'), ig = head.indexOf('grade_rad');
  if (is < 0 || ik < 0) throw Error('Faltam as colunas s_m e kappa_1pm.');
  const s = [], kappa = [], grade = [];
  rows.slice(1).forEach((line, n) => {
    const c = line.split(',').map(Number);
    if (!Number.isFinite(c[is]) || !Number.isFinite(c[ik]) || (ig >= 0 && !Number.isFinite(c[ig]))) throw Error(`Valor inválido na linha ${n + 2}.`);
    if (Math.abs(c[ik]) > 0.2) throw Error(`Curvatura acima de 0,2 1/m na linha ${n + 2}.`);
    s.push(c[is]); kappa.push(c[ik]); grade.push(ig >= 0 ? c[ig] : 0);
  });
  for (let i = 1; i < s.length; i++) if (!(s[i] > s[i - 1]) || s[i] - s[i - 1] > 10) throw Error(`s_m deve crescer com passo de até 10 m (linha ${i + 2}).`);
  if (s[0] !== 0) throw Error('A primeira linha deve ter s_m = 0.');
  const step = s[s.length - 1] - s[s.length - 2];
  return { s, kappa, grade, length: s[s.length - 1] + step };
}

function csvControls() {
  const input = $('ls-csv'), back = $('ls-csv-bahrain'), status = $('ls-csv-status');
  input.addEventListener('change', async () => {
    const f = input.files[0];
    if (!f) return;
    try {
      if (f.size > 2e6) throw Error('Arquivo acima de 2 MB.');
      imported = parseCSV(await f.text());
      back.disabled = false;
      status.textContent = `Pista importada: ${f.name}, ${fmt(imported.length, 0)} m, ${imported.s.length} pontos. Mapa redesenhado a partir da curvatura.`;
      run();
    } catch (err) {
      status.textContent = 'Não foi possível usar o arquivo: ' + err.message;
    }
  });
  back.addEventListener('click', () => { imported = null; back.disabled = true; input.value = ''; status.textContent = 'O Bahrein está carregado.'; run(); });
}

// ------------------------------------------------------------------------------------- 3D
function hasWebGL() {
  try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch { return false; }
}

async function mount3D() {
  const box = $('ls-ggv');
  if (!hasWebGL()) { box.dataset.state = 'fallback'; return; }
  const { mountGGV } = await import('./ggv3d.js');
  ggv = mountGGV(box);
  ggv.setEnvelope(current.env, G);
  const cloud = $('ls-cloud');
  const apply = () => ggv.setCloud(data.gg_measured, cloud.checked);
  cloud.addEventListener('change', apply);
  apply();
}

// ------------------------------------------------------------------------------------- boot
async function boot() {
  try {
    const res = await fetch(DATA_URL);
    if (!res.ok) throw Error('HTTP ' + res.status);
    data = await res.json();
  } catch (err) {
    root.dataset.state = 'error';
    $('ls-sum-note').textContent = 'Não foi possível carregar os dados do simulador (' + err.message + '). Recarregue a página.';
    return;
  }
  track = trackFrom(data.track);
  calibratedCar = carFrom(data.car);
  calibrated = simulate(calibratedCar, track);
  buildSliders();
  staticSections();
  run();
  $('ls-reset').addEventListener('click', () => {
    SLIDERS.forEach(s => { values[s.key] = base(s.key); $('ls-in-' + s.key).value = values[s.key]; show(s); });
    run();
  });
  $('ls-pin').addEventListener('click', () => { pinned = { res: current.res, track: imported || track }; speedChart(); });
  root.querySelectorAll('[data-drv]').forEach(c => c.addEventListener('change', speedChart));
  csvControls();
  root.dataset.state = 'ready';
  const start = () => mount3D().catch(() => { $('ls-ggv').dataset.state = 'fallback'; });
  ('requestIdleCallback' in window) ? requestIdleCallback(start, { timeout: 1500 }) : setTimeout(start, 300);
}

boot();
