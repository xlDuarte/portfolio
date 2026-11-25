// #102 — sideslip estimation with noisy sensors: EKF vs UKF, consistency (NEES/NIS) and the
// joint estimate of the friction scale λ, from the Monte Carlo study in estimation-bahrain.json.
import { $, table, chart, fmt, pct, getJSON, INK, BLUE, RED, GREEN, AMBER, GREY } from './ui.js';

const URL = '/motorsport/data/estimation-bahrain.json';
const UKF_L = 'UKF + aderência λ', UKF = 'UKF, Magic Formula', EKF = 'EKF, Magic Formula', LIN = 'EKF, pneu linear', INT = 'Integrador (sensores brutos)';
let data, scen = 'nominal';

const ci = r => `${fmt(r.beta_rmse_deg, 2)}° <small>[${fmt(r.beta_rmse_ci95[0], 2)}; ${fmt(r.beta_rmse_ci95[1], 2)}]</small>`;

function kpis() {
  const n = data.scenarios.nominal.table, w = data.scenarios.gasto;
  const set = (k, v) => { document.querySelector(`#se [data-k="${k}"]`).textContent = v; };
  set('rmse', fmt(n[UKF_L].beta_rmse_deg, 2) + '°');
  set('ukf', fmt(n[UKF].beta_rmse_deg, 2) + '°');
  set('int', fmt(n[INT].beta_rmse_deg, 0) + '°');
  set('drop', fmt(data.grip_drop_detected_pct, 1) + ' %');
  const lamN = data.scenarios.nominal, drop = 100 * (1 - w.lam_truth_axle_model / lamN.lam_truth_axle_model);
  $('se-kpi-note').textContent = `${data.runs} simulações de Monte Carlo por cenário, volta completa de ${fmt(lamN.distance_m / 1000, 2)} km com sensores a ${data.rate_hz} Hz. A queda real de aderência no cenário de pneu gasto é de ${fmt(drop, 1)} %; o filtro detecta ${fmt(data.grip_drop_detected_pct, 1)} % sem saber que o pneu mudou.`;
}

function betaChart() {
  const s = data.scenarios[scen], ser = s.series;
  const x = s.s.map(v => v / 1000);
  const u = ser[UKF_L];
  chart($('se-beta'), [
    { x, y: s.beta_truth_deg, color: INK, width: 1.4, label: 'β verdadeiro' },
    { x, y: ser[LIN].beta_deg, color: AMBER, dash: '5 3', width: 1.3, label: 'EKF, pneu linear' },
    { x, y: u.beta_deg, color: BLUE, width: 1.5, label: 'UKF + λ (±2σ)', band: { lo: u.beta_deg.map((v, i) => v - u.sd2_deg[i]), hi: u.beta_deg.map((v, i) => v + u.sd2_deg[i]) } },
  ], { height: 300, xLabel: 'distância na volta (km)', yLabel: 'ângulo de deriva β (°)', xFmt: v => fmt(v, 1), yFmt: v => fmt(v, 0) });
}

function aneesChart() {
  const s = data.scenarios[scen], t = s.t, row = s.table[UKF_L];
  const band = row.anees_band;
  chart($('se-anees'), [
    { x: t, y: s.series[EKF].anees, color: AMBER, width: 1.2, label: 'EKF' },
    { x: t, y: s.series[UKF].anees, color: RED, width: 1.2, label: 'UKF' },
    { x: t, y: s.series[UKF_L].anees, color: BLUE, width: 1.5, label: 'UKF + λ' },
  ], { width: 460, height: 300, yDomain: [0, 16], xLabel: 'tempo (s)', yLabel: 'NEES médio (4 estados)', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0),
    hbands: [{ lo: band[0], hi: band[1], color: GREEN, label: 'faixa χ² de 95 %' }] });
}

function lambdaChart() {
  const n = data.scenarios.nominal, w = data.scenarios.gasto;
  const line = (s, c, lab) => ({ x: s.t, y: s.lambda_est.series_mean, color: c, width: 1.6, label: lab,
    band: { lo: s.lambda_est.series_mean.map((v, i) => v - s.lambda_est.series_sd2[i]), hi: s.lambda_est.series_mean.map((v, i) => v + s.lambda_est.series_sd2[i]) } });
  chart($('se-lambda'), [line(n, BLUE, 'pneu como calibrado'), line(w, RED, 'pneu gasto (−10 %)')],
    { width: 460, height: 300, yDomain: [0.75, 1.15], xLabel: 'tempo (s)', yLabel: 'λ estimado', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 2),
      hlines: [{ y: n.lam_filter, color: GREY, dash: '2 3' }, { y: n.lam_truth_axle_model, color: BLUE }, { y: w.lam_truth_axle_model, color: RED }] });
}

function tables() {
  for (const [key, id] of [['nominal', 'se-tab-nom'], ['gasto', 'se-tab-worn']]) {
    const tab = data.scenarios[key].table;
    table(id, ['Estimador', 'RMSE de β [IC 95 % entre execuções]', 'Erro máximo', 'Cobertura de ±1,96σ', 'NEES mediano', 'Tempo na faixa χ²', 'NIS médio (ideal 3)', 'Viés do giroscópio, RMSE'],
      Object.entries(tab).map(([name, r]) => [name, ci(r), fmt(r.beta_max_abs_err_deg, 1) + '°',
        r.beta_cover95 === undefined ? '—' : pct(r.beta_cover95), r.anees_median === undefined ? '—' : fmt(r.anees_median, 1),
        r.anees_in_band === undefined ? '—' : pct(r.anees_in_band), r.anis_mean === undefined ? '—' : fmt(r.anis_mean, 2),
        r.gyro_bias_rmse_deg_s === undefined ? '—' : fmt(r.gyro_bias_rmse_deg_s, 2) + '°/s']));
  }
  const band = data.scenarios.nominal.table[UKF_L].anees_band;
  $('se-tab-note').textContent = `Faixa χ² para o NEES médio de ${data.runs} execuções com 4 estados: ${fmt(band[0], 2)} a ${fmt(band[1], 2)}. NEES acima da faixa indica filtro otimista (covariância pequena demais para o erro real). O primeiro segundo de cada execução fica fora das estatísticas.`;
}

function draw() { betaChart(); aneesChart(); }

export async function init() {
  data = await getJSON(URL);
  kpis(); draw(); lambdaChart(); tables();
  document.querySelectorAll('#se [data-scen]').forEach(b => b.addEventListener('click', () => {
    scen = b.dataset.scen;
    document.querySelectorAll('#se [data-scen]').forEach(o => o.setAttribute('aria-pressed', String(o === b)));
    draw();
  }));
  $('se-status').textContent = '';
}
