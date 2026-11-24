// Strategy page (#101), section "Decisão sob incerteza": Bayesian pace model, measured pit loss,
// posterior decision analysis, stochastic dynamic programme with safety cars (recomputed in the
// browser) and the tyre energy/thermal link to the lap simulator.
import { el, text, clear, fmt, lines, richHTML } from '../lapsim/charts.js';
import { sdp, simulate, simulateStatic, S, H } from './sdp.js';

const DATA_URL = '/motorsport/data/strategy-bayes.json';
const root = document.getElementById('sb');
const $ = id => document.getElementById(id);
const INK = '#1c2128', SLATE = '#59616b', RULE = '#e3e6ea', SOFT = '#b8122b', HARD = '#59616b', BLUE = '#1d4e9e';
let data;

function table(id, head, rows) {
  const t = $(id);
  t.querySelectorAll('thead,tbody').forEach(e => e.remove());
  const th = t.createTHead().insertRow();
  head.forEach(h => { const c = document.createElement('th'); c.scope = 'col'; c.innerHTML = richHTML(h); th.append(c); });
  const tb = t.createTBody();
  rows.forEach(r => {
    const tr = tb.insertRow();
    r.forEach((v, i) => {
      const c = i ? tr.insertCell() : document.createElement('th');
      if (!i) { c.scope = 'row'; tr.append(c); }
      c.innerHTML = richHTML(v);
    });
  });
}
const sgn = (x, d = 2) => (x >= 0 ? '+' : '−') + fmt(Math.abs(x), d);
const ci = (s, d = 3, u = '') => `${fmt(s.mean, d)}${u} [${fmt(s.q05, d)}; ${fmt(s.q95, d)}]`;

// forest plot: rows [{label, mean, lo, hi, color}]
function forest(svg, rows, { width = 760, rowH = 18, xLabel, zero = true, d = 2 }) {
  clear(svg);
  const h = 30 + rows.length * rowH + 40;
  svg.setAttribute('viewBox', `0 0 ${width} ${h}`);
  const box = { l: 170, r: width - 130, t: 20, b: 20 + rows.length * rowH };
  const lo = Math.min(...rows.map(r => r.lo), zero ? 0 : Infinity), hi = Math.max(...rows.map(r => r.hi), zero ? 0 : -Infinity);
  const pad = (hi - lo) * 0.06 || 1;
  const x = v => box.l + (v - (lo - pad)) / ((hi + pad) - (lo - pad)) * (box.r - box.l);
  const g = el('g', { 'font-size': 11, fill: SLATE }, svg);
  const step = niceStep((hi - lo) / 6);
  for (let v = Math.ceil((lo - pad) / step) * step; v <= hi + pad; v += step) {
    el('line', { x1: x(v), x2: x(v), y1: box.t - 6, y2: box.b, stroke: RULE }, g);
    text(g, x(v), box.b + 16, fmt(Math.abs(v) < 1e-9 ? 0 : v, d), { 'text-anchor': 'middle' });
  }
  if (zero) el('line', { x1: x(0), x2: x(0), y1: box.t - 6, y2: box.b, stroke: INK }, g);
  if (xLabel) text(g, (box.l + box.r) / 2, box.b + 32, xLabel, { 'text-anchor': 'middle', fill: INK });
  rows.forEach((r, i) => {
    const y = box.t + i * rowH + rowH / 2;
    text(svg, box.l - 8, y + 4, r.label, { 'text-anchor': 'end', 'font-size': 11, fill: INK });
    el('line', { x1: x(r.lo), x2: x(r.hi), y1: y, y2: y, stroke: r.color || INK, 'stroke-width': 2 }, svg);
    el('circle', { cx: x(r.mean), cy: y, r: 3.6, fill: r.color || INK }, svg);
    if (r.note) text(svg, box.r + 8, y + 4, r.note, { 'font-size': 10.5, fill: SLATE });
  });
}
function niceStep(raw) { const m = 10 ** Math.floor(Math.log10(raw || 1)); return [1, 2, 5, 10].map(k => k * m).find(s => s >= raw) || raw; }

function bars(svg, values, { width = 420, height = 220, xLabel, color = INK, from = 1 }) {
  clear(svg);
  const box = { l: 36, r: width - 10, t: 14, b: height - 36 };
  const max = Math.max(...values, 1);
  const n = values.length, w = (box.r - box.l) / n;
  values.forEach((v, i) => { if (v) el('rect', { x: box.l + i * w + 0.5, y: box.b - (box.b - box.t) * v / max, width: Math.max(w - 1, 1), height: (box.b - box.t) * v / max, fill: color }, svg); });
  const g = el('g', { 'font-size': 11, fill: SLATE }, svg);
  for (let i = 0; i < n; i += 5) text(g, box.l + i * w + w / 2, box.b + 14, String(i + from - 1 + 1), { 'text-anchor': 'middle' });
  el('line', { x1: box.l, x2: box.r, y1: box.b, y2: box.b, stroke: '#c9ced5' }, g);
  if (xLabel) text(g, (box.l + box.r) / 2, box.b + 30, xLabel, { 'text-anchor': 'middle', fill: INK });
}

function render() {
  const m = data.model, v = data.validation, dec = data.decision, pit = data.pit, sd = m.summary;
  const top = dec.top[0];
  const ver = dec.actual.find(a => a.driver === dec.driver);
  const kp = (k, s) => { root.querySelector(`[data-k="${k}"]`).textContent = s; };
  kp('best', top.label);
  kp('pbest', fmt(top.p_optimal * 100, 0) + ' %');
  kp('ver', sgn(ver.regret.mean, 1) + ' s');
  kp('pit', fmt(pit.median_s, 1) + ' s');
  $('sb-kpi-note').textContent = `Plano ótimo para Verstappen, com largada no macio usado das classificações. A perda por parada vem de ${pit.n_used} paradas medidas, com intervalo de confiança de 95 % de ${fmt(pit.ci95_s[0], 1)} a ${fmt(pit.ci95_s[1], 1)} s. O plano real de VER (${ver.plan}) custou ${fmt(ver.regret.mean, 1)} s [${fmt(ver.regret.q05, 1)}; ${fmt(ver.regret.q95, 1)}] no modelo, sem contar tráfego e posição.`;

  // degradation curves
  const C = data.curves;
  const band = (c, col) => [{ points: c.age.map((a, i) => [a, c.q05[i]]), color: col, width: 1, dash: '3 3' },
    { points: c.age.map((a, i) => [a, c.q95[i]]), color: col, width: 1, dash: '3 3' }];
  lines($('sb-deg'), [...band(C.SOFT, SOFT), ...band(C.HARD, HARD),
    { points: C.SOFT.age.map((a, i) => [a, C.SOFT.q50[i]]), color: SOFT, width: 2.2, label: 'Macio' },
    { points: C.HARD.age.map((a, i) => [a, C.HARD.q50[i]]), color: HARD, width: 2.2, label: 'Duro' }],
  { width: 420, height: 300, xLabel: 'idade do pneu (voltas)', yLabel: 's acima do macio novo', xDomain: [0, 35], yDomain: [-0.5, 5], xFmt: x => fmt(x, 0), yFmt: y => fmt(y, 0) });

  // model table
  const P = [['intercept', 'Ritmo de referência (volta 30, macio novo)', 's'], ['hard', 'Duro − macio, mesma idade', 's'], ['age_soft', 'Degradação do macio', 's/volta'],
    ['age_hard', 'Degradação do duro', 's/volta'], ['race_lap', 'Tendência por volta (combustível + pista)', 's/volta'], ['sigma', 'Desvio residual σ', 's'],
    ['tau_u', 'Dispersão entre pilotos τ_u', 's'], ['tau_v', 'Dispersão da degradação entre pilotos τ_v', 's/volta']];
  table('sb-post', ['Parâmetro', 'Média a posteriori', 'Intervalo de 90 %', 'R̂', 'ESS'], P.map(([k, label, u]) => {
    const s = sd[k];
    return [label, fmt(s.mean, 3) + ' ' + u, `${fmt(s.q05, 3)} a ${fmt(s.q95, 3)}`, fmt(s.rhat, 3), fmt(s.ess, 0)];
  }));
  const tt = m.both['student-t'];
  $('sb-robust').textContent = `Com erros t de Student (ν ≈ ${fmt(tt.nu.mean, 1)}), a degradação fica em ${fmt(tt.age_soft.mean, 3)} s/volta no macio e ${fmt(tt.age_hard.mean, 3)} s/volta no duro, e σ em ${fmt(tt.sigma.mean, 2)} s: a verossimilhança robusta descreve melhor o ritmo limpo, mas prevê pior a corrida real (tabela abaixo).`;

  table('sb-valid', ['Modelo', 'CRPS (s)', 'Erro absoluto médio', 'Viés', 'Cobertura de 90 %', 'Cobertura de 50 %'], [
    ['Bayesiano hierárquico, erros normais' + (v.chosen === 'normal' ? ' (usado)' : ''), fmt(v.bayes_normal.crps_s, 3), fmt(v.bayes_normal.mae_s, 3) + ' s', sgn(v.bayes_normal.bias_s, 3) + ' s', fmt(v.bayes_normal.cover90 * 100, 1) + ' %', fmt(v.bayes_normal.cover50 * 100, 1) + ' %'],
    ['Bayesiano hierárquico, erros t' + (v.chosen !== 'normal' ? ' (usado)' : ''), fmt(v.bayes_t.crps_s, 3), fmt(v.bayes_t.mae_s, 3) + ' s', sgn(v.bayes_t.bias_s, 3) + ' s', fmt(v.bayes_t.cover90 * 100, 1) + ' %', fmt(v.bayes_t.cover50 * 100, 1) + ' %'],
    ['Mínimos quadrados com efeito fixo de piloto', fmt(v.ols.crps_s, 3), fmt(v.ols.mae_s, 3) + ' s', sgn(v.ols.bias_s, 3) + ' s', fmt(v.ols.cover90 * 100, 1) + ' %', '—'],
    ['Persistência (mediana das 5 últimas voltas)', fmt(v.persistence.crps_s, 3), fmt(v.persistence.mae_s, 3) + ' s', '—', '—', '—']]);
  $('sb-valid-note').textContent = `Ajuste nas voltas 2 a ${v.split_lap} (${v.train_laps} voltas), previsão das voltas ${v.split_lap + 1} a 57 (${v.test_laps} voltas). CRPS é uma regra de pontuação própria: menor é melhor, em segundos.`;

  // trend decomposition
  const tr = data.trend;
  table('sb-trend', ['Componente', 'Efeito por volta', 'Intervalo de 90 %', 'Origem'], [
    ['Total medido', sgn(tr.total_s_per_lap.mean, 3) + ' s', `${fmt(tr.total_s_per_lap.q[0], 3)} a ${fmt(tr.total_s_per_lap.q[2], 3)}`, 'dados (posterior)'],
    ['Combustível queimado', '−' + fmt(tr.fuel_s_per_lap.mean, 3) + ' s', `−${fmt(tr.fuel_s_per_lap.q[2], 3)} a −${fmt(tr.fuel_s_per_lap.q[0], 3)}`, `física: ${fmt(tr.physics.s_per_kg * 1000, 1)} ms/kg (simulador de volta) × ${fmt(tr.physics.burn_kg_per_lap, 2)} kg/volta`],
    ['Evolução da pista', sgn(tr.track_s_per_lap.mean, 3) + ' s', `${fmt(tr.track_s_per_lap.q[0], 3)} a ${fmt(tr.track_s_per_lap.q[2], 3)}`, 'resto: total − combustível']]);

  // drivers
  forest($('sb-drivers'), data.drivers.map(d => ({ label: `${d.driver} · ${d.team}`, mean: d.u.mean, lo: d.u.q05, hi: d.u.q95,
    note: `deg. ${sgn(d.v.mean * 1000, 0)} ms/volta` })), { xLabel: 'ritmo em relação à média do grid (s/volta)', d: 1 });

  // plans
  table('sb-plans', ['Plano', 'Tempo esperado vs. melhor', 'Arrependimento (90 %)', 'P(ótimo)'], dec.top.map(t => [
    t.label, sgn(t.expected_vs_best_s, 3) + ' s', `${fmt(t.regret.q05, 2)} a ${fmt(t.regret.q95, 2)} s`, fmt(t.p_optimal * 100, 1) + ' %']));
  bars($('sb-stop1'), dec.first_stop_two_stop.slice(1, 30), { xLabel: '1ª parada (volta) no plano ótimo de 2 paradas', color: SOFT, from: 1 });
  bars($('sb-stop2'), dec.second_stop_two_stop.slice(20, 50), { xLabel: '2ª parada (volta), a partir da volta 20', color: HARD, from: 20 });
  const strategic = dec.actual.filter(a => !/· 1\//.test(a.plan) && !/· 2\//.test(a.plan));
  const forced = dec.actual.filter(a => !strategic.includes(a)).map(a => a.driver);
  $('sb-forced').textContent = forced.length ? `Fora do gráfico: ${forced.join(', ')}, que parou já na primeira ou segunda volta (parada forçada, não escolha de estratégia).` : '';
  forest($('sb-actual'), strategic.map(a => ({ label: `${a.driver} · ${a.plan}`, mean: a.regret.mean, lo: a.regret.q05, hi: a.regret.q95,
    color: a.driver === dec.driver ? SOFT : INK })), { xLabel: 'tempo perdido para o plano ótimo do próprio piloto (s), no modelo', d: 0 });
  const hs = dec.hard_start_vs_soft_start_s;
  $('sb-hardstart').textContent = `Largar de duro novo daria ${fmt(-hs.mean, 1)} s [${fmt(-hs.q95, 1)}; ${fmt(-hs.q05, 1)}] a menos no modelo. Esse número não é uma recomendação: a volta 1 fica fora do ajuste, então o modelo não vê a largada, a tração do macio nem a posição de pista que essa escolha protege.`;

  // tyre physics
  const T = data.tyre;
  const names = ['Dianteiro esq.', 'Dianteiro dir.', 'Traseiro esq.', 'Traseiro dir.'];
  table('sb-energy', ['Pneu', 'Energia de deslizamento por volta', 'Energia de rolagem', 'Deriva máx.', 'Escorregamento máx.'], names.map((n, i) => [
    n, fmt(T.slide_MJ[i], 2) + ' MJ', fmt(T.roll_MJ[i], 2) + ' MJ', fmt(T.max_slip_deg[i], 1) + '°', fmt(T.max_kappa[i] * 100, 1) + ' %']));
  lines($('sb-power'), [
    { points: T.s.map((s, i) => [s, T.power_kw_axle[1][i]]), color: SOFT, width: 1.3, label: 'Eixo traseiro' },
    { points: T.s.map((s, i) => [s, T.power_kw_axle[0][i]]), color: BLUE, width: 1.3, label: 'Eixo dianteiro' }],
  { width: 760, height: 280, xLabel: 'distância (m)', yLabel: 'potência de deslizamento (kW)', xDomain: [0, Math.max(...T.s)], yDomain: [0, Math.ceil(Math.max(...T.power_kw_axle[1]) / 50) * 50], xFmt: x => fmt(x, 0), yFmt: y => fmt(y, 0) });
  const lm = T.lap_means;
  lines($('sb-temp'), [0, 2].flatMap((i, k) => [
    { points: lm.map((x, n) => [n + 1, x.bulk[i]]), color: k ? SOFT : BLUE, width: 2, label: (k ? 'Tras.' : 'Diant.') + ' carcaça' },
    { points: lm.map((x, n) => [n + 1, x.surface[i]]), color: k ? SOFT : BLUE, width: 1.3, dash: '4 3', label: (k ? 'Tras.' : 'Diant.') + ' sup.' }]),
  { width: 420, height: 300, xLabel: 'volta do stint', yLabel: '°C (média da volta, lado esquerdo)', xDomain: [1, lm.length], yDomain: [50, 120], xFmt: x => fmt(x, 0), yFmt: y => fmt(y, 0) });
  table('sb-wear', ['Composto', 'Perda de aderência por volta', 'Por MJ dissipado'], ['SOFT', 'HARD'].map(c => [
    c === 'SOFT' ? 'Macio' : 'Duro', ci(T.wear[c].grip_loss_pct_per_lap, 3, ' %'), ci(T.wear[c].grip_loss_pct_per_MJ, 3, ' %')]));
  $('sb-tyre-note').textContent = `O eixo traseiro dissipa ${fmt(T.rear_share * 100, 0)} % da energia de deslizamento: no Bahrein o carro é limitado pela traseira, na tração das saídas de curva lenta. A temperatura é saída de um modelo térmico de dois nós sem medição para calibrar. Só o coeficiente de convecção foi ajustado (h₁ = ${fmt(T.h1_calibrated, 2)} W/m²K por m/s) para a carcaça traseira estabilizar em ${fmt(T.target_rear_bulk_c, 0)} °C, que é uma hipótese.`;
}

// ------------------------------------------------------------------- SDP, interactive
function sdpControls() {
  const base = data.sdp;
  const pace = base.pace, plan = base.static_plan;
  const inputs = { sc: $('sb-sc'), ratio: $('sb-ratio'), dur: $('sb-dur') };
  const outs = { sc: $('sb-sc-out'), ratio: $('sb-ratio-out'), dur: $('sb-dur-out') };
  let pending = 0;
  const run = () => {
    const perRace = Number(inputs.sc.value), ratio = Number(inputs.ratio.value), dur = Number(inputs.dur.value);
    outs.sc.textContent = fmt(perRace, 1);
    outs.ratio.textContent = fmt(ratio * 100, 0) + ' %';
    outs.dur.textContent = dur + ' voltas';
    const pSC = perRace / 56, opts = { pitGreen: base.pit_green_s, pitSC: ratio * base.pit_green_s, pSC, scLaps: dur, laps: 57, startCompound: S, startAge: 3 };
    const pol = sdp(pace, opts);
    const flex = simulate(pace, pol, { ...opts, races: 3000 });
    const stat = simulateStatic(pace, { compounds: plan.compounds, stops: plan.stops }, { ...opts, races: 3000 });
    const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
    const gain = mean(stat) - mean(flex);
    $('sb-sdp-gain').textContent = sgn(gain, 2).replace('+', '') + ' s';
    $('sb-sdp-exp').textContent = fmt(mean(flex), 1) + ' s';
    $('sb-sdp-static').textContent = fmt(mean(stat), 1) + ' s';
    policyMap($('sb-map-green'), pol, 0, 'Bandeira verde');
    policyMap($('sb-map-sc'), pol, 1, 'Última volta de safety car');
    hist($('sb-dist'), flex, stat);
  };
  Object.values(inputs).forEach(i => i.addEventListener('input', () => { cancelAnimationFrame(pending); pending = requestAnimationFrame(run); }));
  run();
}

// decision map on the hard tyre with both compounds already used: laps (x) × tyre age (y)
function policyMap(svg, pol, s, title) {
  clear(svg);
  const W = 420, Hh = 250, box = { l: 40, r: W - 10, t: 22, b: Hh - 34 };
  const laps = 57, ages = 41;
  const cw = (box.r - box.l) / laps, ch = (box.b - box.t) / ages;
  text(svg, box.l, 14, title, { 'font-size': 12, fill: INK, 'font-weight': 600 });
  for (let n = 1; n <= laps; n++) for (let a = 0; a < ages; a++) {
    if (a > n) continue;                                   // age cannot exceed the lap number
    const act = pol.action(n, s, H, a, 3);
    const fill = act < 0 ? '#eef3fb' : act === S ? '#b8122b' : '#59616b';
    el('rect', { x: box.l + (n - 1) * cw, y: box.b - (a + 1) * ch, width: cw + 0.2, height: ch + 0.2, fill }, svg);
  }
  const g = el('g', { 'font-size': 11, fill: SLATE }, svg);
  [1, 10, 20, 30, 40, 50, 57].forEach(n => text(g, box.l + (n - 0.5) * cw, box.b + 14, String(n), { 'text-anchor': 'middle' }));
  [0, 10, 20, 30, 40].forEach(a => text(g, box.l - 6, box.b - (a + 0.5) * ch + 4, String(a), { 'text-anchor': 'end' }));
  text(g, (box.l + box.r) / 2, box.b + 28, 'volta da corrida', { 'text-anchor': 'middle', fill: INK });
}

function hist(svg, flex, stat) {
  clear(svg);
  const W = 760, Hh = 240, box = { l: 48, r: W - 14, t: 30, b: Hh - 40 };
  const all = [...flex, ...stat].filter(Number.isFinite);
  const lo = Math.floor(Math.min(...all) / 5) * 5, hi = Math.ceil(Math.max(...all) / 5) * 5 + 1;
  const nb = 40, bw = (hi - lo) / nb;
  const count = arr => { const c = new Array(nb).fill(0); arr.forEach(v => { if (Number.isFinite(v)) c[Math.min(nb - 1, Math.floor((v - lo) / bw))]++; }); return c; };
  const cf = count(flex), cs = count(stat), max = Math.max(...cf, ...cs);
  const x = v => box.l + (v - lo) / (hi - lo) * (box.r - box.l), y = c => box.b - (box.b - box.t) * c / max;
  const pathOf = c => c.map((k, i) => `${i ? 'L' : 'M'}${x(lo + i * bw).toFixed(1)} ${y(k).toFixed(1)}H${x(lo + (i + 1) * bw).toFixed(1)}`).join('');
  el('path', { d: pathOf(cs), fill: 'none', stroke: HARD, 'stroke-width': 1.6 }, svg);
  el('path', { d: pathOf(cf), fill: 'none', stroke: SOFT, 'stroke-width': 2 }, svg);
  const g = el('g', { 'font-size': 11, fill: SLATE }, svg);
  for (let v = lo; v <= hi; v += 10) text(g, x(v), box.b + 16, fmt(v, 0), { 'text-anchor': 'middle' });
  el('line', { x1: box.l, x2: box.r, y1: box.b, y2: box.b, stroke: '#c9ced5' }, g);
  text(g, (box.l + box.r) / 2, box.b + 32, 'tempo que depende da estratégia em cada corrida simulada (s)', { 'text-anchor': 'middle', fill: INK });
  el('line', { x1: box.l, x2: box.l + 16, y1: 12, y2: 12, stroke: SOFT, 'stroke-width': 2.4 }, svg);
  text(svg, box.l + 20, 16, 'Política adaptativa (programação dinâmica)', { 'font-size': 11, fill: INK });
  el('line', { x1: box.l + 290, x2: box.l + 306, y1: 12, y2: 12, stroke: HARD, 'stroke-width': 2.4 }, svg);
  text(svg, box.l + 310, 16, `Plano fixo ${data.sdp.best_static}`, { 'font-size': 11, fill: INK });
}

async function boot() {
  try {
    const res = await fetch(DATA_URL);
    if (!res.ok) throw Error('HTTP ' + res.status);
    data = await res.json();
  } catch (err) {
    root.dataset.state = 'error';
    $('sb-kpi-note').textContent = 'Não foi possível carregar os dados (' + err.message + '). Recarregue a página.';
    return;
  }
  render();
  sdpControls();
  root.dataset.state = 'ready';
}

boot();
