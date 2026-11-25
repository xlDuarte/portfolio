// #111 — calibration of race-result probabilities: Plackett–Luce by maximum likelihood vs the
// previous fixed-temperature softmax, walk-forward over 2023–2024 (ranking-calibration.json).
import { $, table, chart, reliability, fmt, pct, getJSON, BLUE, RED, GREEN, AMBER } from './ui.js';

const URL = '/motorsport/data/ranking-calibration.json';
const PL = 'Plackett–Luce (MLE)', OLD = 'Ridge + softmax T = 5 (anterior)', GRID = 'Plackett–Luce, só grid', UNI = 'Uniforme';
const MK = { win: 'Vitória', podium: 'Pódio', top10: 'Top 10' };
const bss = s => `${fmt(100 * s.bss, 1)} % <small>[${fmt(100 * s.ci95[0], 1)}; ${fmt(100 * s.ci95[1], 1)}]</small>`;

export async function init() {
  const d = await getJSON(URL);
  const M = d.models;
  const set = (k, v) => { document.querySelector(`#rk [data-k="${k}"]`).textContent = v; };
  set('bss-uni', fmt(100 * M[UNI].skill_of_pl.win.bss, 0) + ' %');
  set('bss-old', fmt(100 * M[OLD].skill_of_pl.podium.bss, 0) + ' %');
  set('ece', fmt(M[PL].reliability.podium.ece, 3));
  set('events', String(d.events_scored));
  $('rk-kpi-note').textContent = `${d.events_scored} corridas previstas uma a uma, a partir de ${d.first_scored}, cada uma só com as corridas anteriores (${d.drivers_scored} previsões piloto × corrida). Ganho no pódio sobre o método anterior: ${fmt(100 * M[OLD].skill_of_pl.podium.bss, 1)} % de redução do escore de Brier, intervalo de 95 % por reamostragem de corridas de ${fmt(100 * M[OLD].skill_of_pl.podium.ci95[0], 1)} a ${fmt(100 * M[OLD].skill_of_pl.podium.ci95[1], 1)} %.`;

  table('rk-scores', ['Modelo', 'Brier vitória', 'Log-loss do vencedor', 'Brier pódio', 'Brier top 10', 'ECE vitória / pódio / top 10'],
    [PL, GRID, OLD, UNI].map(n => [n, fmt(M[n].win.brier, 4), fmt(M[n].win.logloss_winner, 3), fmt(M[n].podium.brier, 4), fmt(M[n].top10.brier, 4),
      M[n].reliability ? ['win', 'podium', 'top10'].map(m => fmt(M[n].reliability[m].ece, 3)).join(' / ') : '—']));
  table('rk-skill', ['Referência', 'Vitória', 'Pódio', 'Top 10'],
    [UNI, GRID, OLD].map(n => [n, ...['win', 'podium', 'top10'].map(m => bss(M[n].skill_of_pl[m]))]));

  for (const m of ['win', 'podium', 'top10']) {
    reliability($(`rk-rel-${m}`), [
      { bins: M[OLD].reliability[m].bins, color: AMBER, fill: false },
      { bins: M[PL].reliability[m].bins, color: BLUE, ci: true },
    ], { title: `${MK[m]} · ECE ${fmt(M[PL].reliability[m].ece, 3)} (antes ${fmt(M[OLD].reliability[m].ece, 3)})` });
  }

  const z = m => M[PL].reliability[m].z;
  const zp = v => 2 * (1 - normCdf(Math.abs(v)));
  $('rk-cal-note').textContent = `Teste de calibração de Spiegelhalter (z ≈ 0 quando calibrado): vitória z = ${fmt(z('win'), 2)} (p = ${fmt(zp(z('win')), 2)}), pódio z = ${fmt(z('podium'), 2)} (p ${zp(z('podium')) < 0.001 ? '< 0,001' : '= ' + fmt(zp(z('podium')), 3)}), top 10 z = ${fmt(z('top10'), 2)} (p = ${fmt(zp(z('top10')), 2)}). No pódio, z negativo vem de previsões pouco confiantes nas duas pontas: probabilidade demais para quem raramente chega lá e de menos para os favoritos. A seção seguinte trata disso.`;

  const T = d.truncation;
  table('rk-trunc', ['k (posições na verossimilhança)', 'Brier vitória 2023', 'Brier pódio 2023', 'Brier top 10 2023', 'Brier vitória 2024', 'Brier pódio 2024', 'Brier top 10 2024'],
    T.grid.map(k => [String(k), ...['2023', '2024'].flatMap(y => ['win', 'podium', 'top10'].map(m => {
      const v = fmt(T.by_k[k][y][m], 4);
      return y === '2023' && T.chosen_on_2023[m] === k ? `<strong>${v}</strong>` : v;
    }))]));
  const t = T.test_2024;
  $('rk-trunc-note').innerHTML = `Escolha em 2023: k = ${t.win.k} para vitória e pódio, k = ${t.top10.k} para top 10 (em negrito). Em 2024, que não participou da escolha, o k menor reduz o Brier da vitória em ${fmt(100 * t.win.skill_vs_k10.bss, 1)} % [${fmt(100 * t.win.skill_vs_k10.ci95[0], 1)}; ${fmt(100 * t.win.skill_vs_k10.ci95[1], 1)}] e o do pódio em ${fmt(100 * t.podium.skill_vs_k10.bss, 1)} % [${fmt(100 * t.podium.skill_vs_k10.ci95[0], 1)}; ${fmt(100 * t.podium.skill_vs_k10.ci95[1], 1)}]. Os intervalos incluem zero: com ${d.coef_path.filter(c => c.year === 2024).length} corridas a melhora é provável, não demonstrada.`;

  const cp = d.coef_path, xi = cp.map((_, i) => i + 1);
  const col = [BLUE, RED, GREEN];
  chart($('rk-coef'), d.features.map((f, j) => ({ x: xi, y: cp.map(c => c.w[j]), color: col[j], label: f,
    band: { lo: cp.map(c => c.w[j] - 1.96 * c.se[j]), hi: cp.map(c => c.w[j] + 1.96 * c.se[j]) } })),
    { height: 260, xLabel: 'corrida prevista (ordem cronológica, 2023 → 2024)', yLabel: 'peso na utilidade por posição', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 2) });

  table('rk-bah', ['Piloto', 'Chegada real', 'P(vitória)', 'P(pódio)', 'P(top 10)', 'P(vitória), método anterior'],
    d.bahrain_2024.slice(0, 12).map(r => [r.driver, String(r.pos), pct(r.win, 1), pct(r.podium, 0), pct(r.top10, 0), pct(r.win_old, 1)]));
  $('rk-status').textContent = '';
}

// standard normal CDF (Abramowitz–Stegun 7.1.26 for erf, |error| < 1.5e-7)
function normCdf(x) {
  const t = 1 / (1 + 0.3275911 * Math.abs(x) / Math.SQRT2);
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x / 2);
  return x >= 0 ? (1 + y) / 2 : (1 - y) / 2;
}
