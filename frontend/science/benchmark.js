// #014 — sector benchmark of the 2024 Bahrain GP corrected for compound, tyre age and race-lap
// trend (benchmark-bahrain.json): forest plot, sector decomposition of the gap, raw vs corrected rank.
import { $, table, forest, el, text, clear, fmt, sgn, pct, getJSON, INK, SLATE, RULE, BLUE, RED, GREEN, AMBER } from './ui.js';

const URL = '/motorsport/data/benchmark-bahrain.json';
const SEC = [BLUE, AMBER, GREEN];

function gapChart(svg, rows) {
  clear(svg);
  const width = 760, rowH = 18, h = 40 + rows.length * rowH + 40;
  svg.setAttribute('viewBox', `0 0 ${width} ${h}`);
  const box = { l: 70, r: width - 20, t: 34, b: 34 + rows.length * rowH };
  const ext = rows.map(r => r.gap_to_best.map(g => g.mean));
  const lo = Math.min(0, ...ext.map(e => e.filter(v => v < 0).reduce((a, b) => a + b, 0)));
  const hi = Math.max(...ext.map(e => e.filter(v => v > 0).reduce((a, b) => a + b, 0)));
  const x = v => box.l + (v - lo) / (hi - lo || 1) * (box.r - box.l);
  const g = el('g', { 'font-size': 11, fill: SLATE }, svg);
  for (let v = 0; v <= hi + 1e-9; v += 0.25) {
    el('line', { x1: x(v), x2: x(v), y1: box.t - 4, y2: box.b, stroke: RULE }, g);
    text(g, x(v), box.b + 16, fmt(v, 2), { 'text-anchor': 'middle' });
  }
  text(g, (box.l + box.r) / 2, box.b + 32, 'diferença para o mais rápido no mesmo pneu, idade e volta (s por volta)', { 'text-anchor': 'middle', fill: INK });
  ['S1', 'S2', 'S3'].forEach((s, k) => {
    el('rect', { x: box.l + k * 70, y: 6, width: 14, height: 10, fill: SEC[k] }, svg);
    text(svg, box.l + k * 70 + 18, 15, `Setor ${k + 1}`, { 'font-size': 11, fill: INK });
  });
  rows.forEach((r, i) => {
    const y = box.t + i * rowH + 3;
    text(svg, box.l - 8, y + 11, r.driver, { 'text-anchor': 'end', 'font-size': 11, fill: INK });
    let pos = 0, neg = 0;
    r.gap_to_best.forEach((gp, k) => {
      const v = gp.mean;
      const a = v >= 0 ? pos : neg + v, b = v >= 0 ? pos + v : neg;
      el('rect', { x: x(a), y, width: Math.max(x(b) - x(a), 0.5), height: rowH - 6, fill: SEC[k] }, svg);
      if (v >= 0) pos += v; else neg += v;
    });
  });
  el('line', { x1: x(0), x2: x(0), y1: box.t - 4, y2: box.b, stroke: INK }, svg);
}

function slope(svg, rows) {
  clear(svg);
  const width = 420, n = rows.length, rowH = 17, h = 50 + n * rowH;
  svg.setAttribute('viewBox', `0 0 ${width} ${h}`);
  const xa = 120, xb = 300, y = r => 36 + (r - 1) * rowH;
  text(svg, xa, 16, 'mediana bruta', { 'text-anchor': 'middle', 'font-size': 11, fill: SLATE });
  text(svg, xb, 16, 'corrigido', { 'text-anchor': 'middle', 'font-size': 11, fill: SLATE });
  const rawRank = [...rows].sort((a, b) => a.raw.median_lap - b.raw.median_lap).map(r => r.driver);
  rows.forEach((r, j) => {
    const ra = rawRank.indexOf(r.driver) + 1, rb = j + 1, moved = Math.abs(ra - rb);
    const c = moved >= 3 ? RED : moved ? INK : '#b9c0c8';
    el('line', { x1: xa + 6, y1: y(ra), x2: xb - 6, y2: y(rb), stroke: c, 'stroke-width': moved >= 3 ? 1.8 : 1.1 }, svg);
    text(svg, xa - 8, y(ra) + 4, `${ra}. ${r.driver}`, { 'text-anchor': 'end', 'font-size': 11, fill: INK });
    text(svg, xb + 8, y(rb) + 4, `${rb}. ${r.driver}`, { 'font-size': 11, fill: INK });
  });
}

export async function init() {
  const d = await getJSON(URL);
  const rows = d.drivers, best = rows[0];
  const set = (k, v) => { document.querySelector(`#bm [data-k="${k}"]`).textContent = v; };
  set('best', `${best.driver} ${sgn(best.lap.mean, 2)} s`);
  set('pbest', pct(best.p_fastest, 0));
  set('moves', `${d.agreement.rank_moves} de ${rows.length}`);
  set('corr', fmt(d.residual_corr['S2-S3'].clean_weights.r, 2));
  $('bm-kpi-note').textContent = `${d.source.laps_clean} voltas limpas de ${rows.length} pilotos (OpenF1). Ritmo comparado no pneu duro com ${d.source.a_ref} voltas de uso, na volta 30, em relação à média do grid. A soma dos três setores reproduz o modelo da volta inteira com correlação ${fmt(d.consistency.corr, 3)} e diferença máxima de ${fmt(d.consistency.max_abs_diff_s, 2)} s.`;

  forest($('bm-forest'), rows.map(r => ({ label: `${r.driver} · ${r.team}`, mean: r.lap.mean, lo: r.lap.q05, hi: r.lap.q95,
    color: r.p_fastest > 0.5 ? RED : INK, note: `bruto ${fmt(r.raw.median_lap, 2)} s · posição ${r.rank90[0] === r.rank90[1] ? r.rank90[0] : r.rank90.join('–')}` })),
  { xLabel: 'ritmo corrigido em relação à média do grid (s por volta), intervalo de 90 %', left: 170, d: 1 });
  gapChart($('bm-gap'), rows);
  slope($('bm-slope'), rows);

  const A = d.agreement;
  table('bm-agree', ['Referência bruta', 'τ de Kendall', 'ρ de Spearman'],
    [['Mediana das voltas limpas', A.median_vs_corrected], ['Melhor volta', A.best_vs_corrected], ['Volta ideal (soma dos melhores setores)', A.ideal_vs_corrected]]
      .map(([n, a]) => [n, fmt(a.kendall_tau, 2), fmt(a.spearman_rho, 2)]));

  const F = d.fixed, keys = ['S1', 'S2', 'S3', 'volta'];
  const c = (s, k, dd = 3) => `${fmt(s[k].mean, dd)} <small>[${fmt(s[k].q05, dd)}; ${fmt(s[k].q95, dd)}]</small>`;
  table('bm-fixed', ['Efeito (s)', 'Setor 1', 'Setor 2', 'Setor 3', 'Volta inteira'], [
    ['Duro − macio (pneu novo)', ...keys.map(k => c(F[k], 'hard'))],
    ['Desgaste do macio, por volta', ...keys.map(k => c(F[k], 'age_soft'))],
    ['Desgaste do duro, por volta', ...keys.map(k => c(F[k], 'age_hard'))],
    ['Tendência por volta de corrida', ...keys.map(k => c(F[k], 'race_lap'))],
    ['Escala do erro σ', ...keys.map(k => fmt(F[k].sigma, 3))],
    ['Graus de liberdade ν (mediana)', ...keys.map(k => fmt(F[k].nu_median, 1))],
  ]);
  const R = d.residual_corr;
  table('bm-corr', ['Par de setores', 'Todas as voltas', 'Voltas com peso pleno (λ̄ > 0,5)'],
    Object.entries(R).map(([k, v]) => [k.replace('-', ' × '), `${fmt(v.all.r, 2)} <small>[${fmt(v.all.ci95[0], 2)}; ${fmt(v.all.ci95[1], 2)}]</small>`,
      `${fmt(v.clean_weights.r, 2)} <small>[${fmt(v.clean_weights.ci95[0], 2)}; ${fmt(v.clean_weights.ci95[1], 2)}]</small>`]));
  $('bm-diag').textContent = `Diagnóstico: ${d.diagnostics.chains} cadeias × ${d.diagnostics.iters - d.diagnostics.burn} sorteios por modelo; maior R̂ dos efeitos de piloto ${fmt(d.diagnostics.rhat_max, 3)}, menor ESS ${fmt(d.diagnostics.ess_min_u, 0)}.`;
  $('bm-status').textContent = '';
}
