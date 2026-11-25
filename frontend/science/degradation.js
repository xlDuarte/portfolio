// Phase 4b — degradation on real data, shared by three pages: #097 RUL on NASA C-MAPSS (root "ru"),
// #036 pump leakage on the ZeMA hydraulic rig (root "pu"), #037 oil viscosity and ageing (root "ol").
import { $, table, chart, bars, el, text, clear, fmt, pct, getJSON, INK, SLATE, RULE, BLUE, RED, GREEN, AMBER, GREY } from './ui.js';

const URL = '/data/degradation.json';
const set = (root, k, v) => { const e = document.querySelector(`#${root} [data-k="${k}"]`); if (e) e.textContent = v; };
let cache;
const data = () => (cache ||= getJSON(URL));
const LEAK = ['sem vazamento', 'vazamento leve', 'vazamento severo'];
const LEAKC = [BLUE, AMBER, RED];

// ---------------------------------------------------------------- #097
function pathsChart(svg, c) {
  const series = c.train_paths.map(p => ({ x: p.t, y: p.s, color: GREY, width: 0.7 }));
  chart(svg, series, { height: 280, xLabel: 'ciclo', yLabel: 'indicador de saúde S', yDomain: [-0.6, 1.6], xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 1), legend: false,
    hbands: [{ lo: c.model.mD - 2 * c.model.sD, hi: c.model.mD + 2 * c.model.sD, color: RED, label: 'limiar de falha (±2σ)' }] });
}

function exampleChart(svg, ex, c) {
  const end = ex.t_obs[ex.t_obs.length - 1] + ex.true_rul;
  chart(svg, [
    { x: ex.t_obs, y: ex.s_obs, color: INK, width: 0.9 },
    { x: ex.t_grid, y: ex.band[1], color: BLUE, width: 1.6, band: { lo: ex.band[0], hi: ex.band[2] } },
  ], { width: 380, height: 240, xDomain: [0, Math.max(end + 20, ex.t_obs[ex.t_obs.length - 1] + 60)], yDomain: [-0.6, 1.8], xLabel: 'ciclo', yLabel: 'S', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 1), legend: false,
    hlines: [{ y: c.model.mD, color: RED }], vlines: [{ x: ex.t_obs[ex.t_obs.length - 1], color: SLATE, label: 'hoje' }, { x: end, color: RED, label: 'falha real' }] });
}

function fanChart(svg, c) {
  clear(svg);
  const u = [...c.units].sort((a, b) => a.true - b.true);
  const W = 760, H = 320, box = { l: 52, r: W - 14, t: 34, b: H - 40 };
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const ymax = Math.min(320, Math.max(...u.map(r => r.q[4]), ...u.map(r => r.true)) * 1.05);
  const x = i => box.l + (i + 0.5) / u.length * (box.r - box.l), y = v => box.b - Math.min(v, ymax) / ymax * (box.b - box.t);
  for (let v = 0; v <= ymax; v += 50) {
    el('line', { x1: box.l, x2: box.r, y1: y(v), y2: y(v), stroke: RULE }, svg);
    text(svg, box.l - 6, y(v) + 4, fmt(v, 0), { 'text-anchor': 'end', 'font-size': 10.5, fill: SLATE });
  }
  text(svg, box.l, 22, 'vida útil restante (ciclos)', { 'font-size': 11, fill: SLATE });
  text(svg, (box.l + box.r) / 2, H - 10, `${u.length} motores de teste, ordenados pela vida restante real`, { 'text-anchor': 'middle', 'font-size': 11, fill: INK });
  u.forEach((r, i) => {
    el('line', { x1: x(i), x2: x(i), y1: y(r.q[0]), y2: y(r.q[4]), stroke: BLUE, opacity: 0.35, 'stroke-width': 3 }, svg);
    el('circle', { cx: x(i), cy: y(r.q[2]), r: 2.2, fill: BLUE }, svg);
    el('rect', { x: x(i) - 2, y: y(r.ridge) - 2, width: 4, height: 4, fill: AMBER }, svg);
    el('circle', { cx: x(i), cy: y(r.true), r: 2, fill: INK }, svg);
  });
  let lx = box.l + 190;
  [['intervalo de 90 % e mediana (bayesiano)', BLUE], ['ridge com teto de 125', AMBER], ['valor real', INK]].forEach(([l, col]) => {
    el('circle', { cx: lx, cy: 18, r: 4, fill: col }, svg);
    text(svg, lx + 8, 22, l, { 'font-size': 11, fill: INK });
    lx += 24 + l.length * 6;
  });
}

function weibullChart(svg, w) {
  const t = Array.from({ length: 80 }, (_, i) => (i + 1) * Math.max(...w.lives) * 1.1 / 80);
  chart(svg, [
    { x: w.lives, y: w.ecdf, color: INK, dots: true, r: 2.2, opacity: 0.8, label: 'empírica' },
    { x: t, y: t.map(v => 1 - Math.exp(-((v / w.scale) ** w.shape))), color: RED, width: 1.6, label: `Weibull k = ${fmt(w.shape, 2)}, λ = ${fmt(w.scale, 0)}` },
  ], { width: 460, height: 280, yDomain: [0, 1], xLabel: 'vida até a falha (ciclos)', yLabel: 'fração falhada', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 1) });
}

function rulTables(c) {
  const M = c.metrics;
  table('ru-metrics', ['Modelo', 'RMSE (ciclos)', 'Escore PHM 2008', 'CRPS', 'Cobertura 90 % / 50 %', 'Largura média 90 %'], [
    ['Bayesiano, trajetória aleatória', fmt(M.rmse_bayes, 1), fmt(M.score_bayes, 0), fmt(M.crps_bayes, 1), `${pct(M.cover90, 0)} / ${pct(M.cover50, 0)}`, fmt(M.width90, 0)],
    ['Ridge, alvo com teto de 125', fmt(M.rmse_ridge, 1), fmt(M.score_ridge, 0), '—', '—', '—']]);
  table('ru-bins', ['Vida restante real', 'Motores', 'RMSE bayesiano', 'RMSE ridge', 'Cobertura 90 %'],
    Object.entries(c.bins).map(([k, b]) => [k.replace('-+', ' ou mais').replace('-', ' a ') + ' ciclos', String(b.n), fmt(b.rmse_bayes, 1), fmt(b.rmse_ridge, 1), pct(b.cover90, 0)]));
  const d = c.decision;
  table('ru-dec', ['Política', 'Intervenções', 'Falhas em serviço', `Custo (intervenção = 1, falha = ${fmt(d.cost_ratio, 0)})`], [
    [`Bayesiana: intervir se P(falha em ${d.horizon} ciclos) ≥ ${fmt(d.threshold, 2)}`, d.bayes.interventions, d.bayes.failures, d.bayes.cost],
    [`Ridge: intervir se a previsão ≤ ${d.horizon} ciclos`, d.ridge.interventions, d.ridge.failures, d.ridge.cost],
    ['Informação perfeita', d.perfect.interventions, d.perfect.failures, d.perfect.cost],
    ['Nunca intervir', d.never.interventions, d.never.failures, d.never.cost]].map(r => r.map(String)));
  table('ru-cv', ['Candidato', 'CRPS médio na validação cruzada (ciclos)'],
    Object.entries(c.cv_crps).map(([k, v]) => [k === 'aleatório' ? 'γ próprio de cada motor' : `γ comum = ${fmt(+k, 2)}`, k === c.chosen ? `<strong>${fmt(v, 1)}</strong>` : fmt(v, 1)]));
  const w = c.weibull;
  table('ru-wb', ['Forma k', 'Escala λ (ciclos)', 'B10 (ciclos)', 'Teste KS, p'], [[
    `${fmt(w.shape, 2)} <small>[${fmt(w.shape_ci95[0], 2)}; ${fmt(w.shape_ci95[1], 2)}]</small>`,
    `${fmt(w.scale, 0)} <small>[${fmt(w.scale_ci95[0], 0)}; ${fmt(w.scale_ci95[1], 0)}]</small>`, fmt(w.B10, 0), fmt(w.ks_p, 2)]]);
  $('ru-wb-note').textContent = w.ks_p < 0.05
    ? `O teste de Kolmogorov–Smirnov rejeita a Weibull a 5 % (p = ${fmt(w.ks_p, 2)}; com parâmetros estimados nos mesmos dados o teste é conservador, então a rejeição é firme). As vidas têm a cauda direita mais longa que a Weibull permite: a forma e o B10 descrevem o centro da distribuição, não os motores mais duráveis.`
    : `O teste de Kolmogorov–Smirnov não rejeita a Weibull a 5 % (p = ${fmt(w.ks_p, 2)}).`;
}

export async function initRUL() {
  const d = await data();
  let fd = 'FD001';
  const draw = () => {
    const c = d.cmapss[fd];
    set('ru', 'near', `${fmt(c.bins['0-60'].rmse_bayes, 1)} × ${fmt(c.bins['0-60'].rmse_ridge, 1)}`);
    set('ru', 'cover', pct(c.metrics.cover90, 0));
    set('ru', 'cost', `${c.decision.bayes.cost} × ${c.decision.ridge.cost}`);
    set('ru', 'shape', fmt(c.weibull.shape, 1));
    $('ru-kpi-note').textContent = `${fd}: ${c.n_train} motores de treino rodados até a falha e ${c.n_test} de teste cortados antes dela, com a vida restante real publicada pela NASA. Erro perto da falha: RMSE nos motores com menos de 60 ciclos restantes, bayesiano × ridge. Custo de manutenção: política bayesiana × ridge; com informação perfeita seria ${c.decision.perfect.cost}.`;
    pathsChart($('ru-paths'), c);
    c.examples.forEach((ex, i) => exampleChart($(`ru-ex${i}`), ex, c));
    c.examples.forEach((ex, i) => { $(`ru-ex${i}-cap`).textContent = `Motor ${ex.unit}: ${ex.t_obs.length} ciclos observados, vida restante real ${fmt(ex.true_rul, 0)}.`; });
    fanChart($('ru-fan'), c);
    weibullChart($('ru-weib'), c.weibull);
    rulTables(c);
  };
  draw();
  document.querySelectorAll('#ru [data-fd]').forEach(b => b.addEventListener('click', () => {
    fd = b.dataset.fd;
    document.querySelectorAll('#ru [data-fd]').forEach(o => o.setAttribute('aria-pressed', String(o === b)));
    draw();
  }));
  $('ru-status').textContent = '';
}

// ---------------------------------------------------------------- #036
export async function initPump() {
  const d = await data(), h = d.hydraulic, P = h.protocols;
  const phys = P['regime térmico novo']['físicos com compensação'].balanced, st = P['regime térmico novo']['estatísticos'].balanced;
  set('pu', 'loco', `${pct(st, 0)} → ${pct(phys, 0)}`);
  set('pu', 'extrap', `${fmt(h.extrapolation.viscosity_model, 3)} × ${fmt(h.extrapolation.observed_mean, 3)}`);
  set('pu', 'leak', `${fmt(h.by_cooler['100'].deficit[1], 2)} / ${fmt(h.by_cooler['100'].deficit[2], 2)}`);
  set('pu', 'eta', `${pct(h.by_cooler['100'].eta[0], 1)} → ${pct(h.by_cooler['100'].eta[2], 1)}`);
  $('pu-kpi-note').textContent = `${h.cycles} ciclos reais de 60 s do banco hidráulico da ZeMA, com os quatro componentes degradados juntos. Primeiro número: acurácia balanceada em regime térmico nunca visto, atributos estatísticos → físicos com compensação de viscosidade. Segundo: vazão a 156 bar prevista para o óleo a ${fmt(h.extrapolation.T_test_mean, 1)} °C (L/min), modelo × medida.`;
  chart($('pu-scatter'), [
    ...[0, 1, 2].map(k => ({ x: h.scatter[k].T, y: h.scatter[k].q, color: LEAKC[k], dots: true, r: 1.6, opacity: 0.5, label: LEAK[k] })),
    { x: h.curve.T, y: h.curve.q, color: INK, width: 1.6, label: 'bomba sã: Qₜₕ − K/ν(T)' },
  ], { height: 300, yDomain: [7.0, 8.1], xLabel: 'temperatura do óleo TS1 (°C)', yLabel: 'vazão a 156 bar (L/min)', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 1) });
  bars($('pu-bars'), [
    { label: 'Ciclos sorteados (70/30)', bars: [{ name: 'estatísticos (34)', v: P['aleatório']['estatísticos'].balanced, color: GREY }, { name: 'físicos sem compensação', v: P['aleatório']['físicos sem compensação'].balanced, color: AMBER }, { name: 'físicos com compensação', v: P['aleatório']['físicos com compensação'].balanced, color: BLUE }] },
    { label: 'Regime térmico nunca visto (deixa um estado do resfriador de fora)', bars: [{ name: 'estatísticos (34)', v: st, color: GREY }, { name: 'físicos sem compensação', v: P['regime térmico novo']['físicos sem compensação'].balanced, color: AMBER }, { name: 'físicos com compensação', v: phys, color: BLUE }] },
  ]);
  table('pu-state', ['Estado do resfriador', 'Óleo (°C)', 'ν (mm²/s)', 'Déficit de vazão: sem / leve / severo (L/min)', 'Eficiência hidráulica: sem / leve / severo'],
    [['3 % (quase falho)', '3'], ['20 % (reduzido)', '20'], ['100 % (pleno)', '100']].map(([n, k]) => [n, fmt(h.by_cooler[k].T, 1), fmt(h.by_cooler[k].nu, 1),
      h.by_cooler[k].deficit.map(v => fmt(Math.abs(v) < 0.005 ? 0 : v, 2)).join(' / '), h.by_cooler[k].eta.map(v => pct(v, 1)).join(' / ')]));
  table('pu-folds', ['Atributos', 'Teste a ~55 °C', 'Teste a ~45 °C', 'Teste a ~36 °C'],
    ['estatísticos', 'físicos sem compensação', 'físicos com compensação'].map(n => [n, ...P['regime térmico novo'][n].folds.map(v => pct(v, 0))]));
  const K = h.K_by_leak;
  $('pu-k').textContent = `Ajustando Q = Qₜₕ − K/ν(T) separadamente em cada nível de vazamento, K vale ${fmt(K['0'], 2)}, ${fmt(K['1'], 2)} e ${fmt(K['2'], 2)}. Se o vazamento simulado fosse um orifício turbulento, independente da viscosidade, K não mudaria. O aumento indica que parte da vazão perdida também é laminar.`;
  $('pu-status').textContent = '';
}

// ---------------------------------------------------------------- #037
export async function initOil() {
  const d = await data(), h = d.hydraulic, A = h.ageing;
  const kEa = Object.keys(A['3']).filter(k => k.startsWith('factor_'));
  const mid = kEa.sort((a, b) => +a.split('_')[1] - +b.split('_')[1])[1];
  set('ol', 'ratio', `${fmt(A['3'][mid] / A['100'][mid], 1)}×`);
  set('ol', 'nu', `${fmt(A['3'].nu_mean, 0)} × ${fmt(A['100'].nu_mean, 0)}`);
  set('ol', 'ea', `${fmt(h.ea_doubling_kj, 1)} kJ/mol`);
  set('ol', 'val', `${fmt(Math.abs(h.extrapolation.viscosity_model - h.extrapolation.observed_mean) * 1000, 0)} mL/min`);
  $('ol-kpi-note').textContent = `Temperaturas medidas em ${h.cycles} ciclos reais do banco hidráulico; óleo suposto ISO VG 46 (ν₄₀ = ${fmt(h.oil.nu40, 0)}, ν₁₀₀ = ${fmt(h.oil.nu100, 1)} mm²/s). Primeiro número: oxidação com o resfriador quase falho contra o pleno.`;
  const tv = h.viscosity_curve;
  chart($('ol-visc'), [{ x: tv.T, y: tv.nu, color: BLUE, width: 1.8 }], { width: 460, height: 280, xLabel: 'temperatura (°C)', yLabel: 'viscosidade cinemática (mm²/s)', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0), legend: false,
    vlines: [{ x: A['100'].T_mean, color: BLUE, label: 'pleno' }, { x: A['20'].T_mean, color: AMBER, label: '20 %', dy: 14 }, { x: A['3'].T_mean, color: RED, label: '3 %', dy: 28 }] });
  const T = Array.from({ length: 61 }, (_, i) => 30 + i * 0.5);
  const R = 8.314462618, f = ea => T.map(t => Math.exp(ea / R * (1 / 313.15 - 1 / (t + 273.15))));
  chart($('ol-arr'), [
    { x: T, y: f(50e3), color: GREY, dash: '4 3', label: 'Eₐ = 50 kJ/mol' },
    { x: T, y: f(h.ea_doubling_kj * 1000), color: INK, width: 1.8, label: `Eₐ = ${fmt(h.ea_doubling_kj, 0)} kJ/mol` },
    { x: T, y: f(80e3), color: GREY, dash: '1 3', label: 'Eₐ = 80 kJ/mol' },
  ], { width: 460, height: 280, xLabel: 'temperatura (°C)', yLabel: 'oxidação relativa a 40 °C', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 1),
    vlines: [{ x: A['100'].T_mean, color: BLUE }, { x: A['20'].T_mean, color: AMBER }, { x: A['3'].T_mean, color: RED }] });
  const ks = kEa.sort((a, b) => +a.split('_')[1] - +b.split('_')[1]);
  table('ol-tab', ['Estado do resfriador', 'Óleo médio (°C)', 'Percentil 95 (°C)', 'ν média (mm²/s)', ...ks.map(k => `Oxidação relativa, Eₐ ${k.split('_')[1]} kJ/mol`)],
    [['3 % (quase falho)', '3'], ['20 % (reduzido)', '20'], ['100 % (pleno)', '100']].map(([n, k]) => [n, fmt(A[k].T_mean, 1), fmt(A[k].T_p95, 1), fmt(A[k].nu_mean, 1), ...ks.map(e => fmt(A[k][e], 2) + '×')]));
  $('ol-status').textContent = '';
}
