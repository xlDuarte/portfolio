// Phase 5a — energy and climate on real Brazilian data, shared by three pages:
// #008 change-point regression (root "cp"), #064 peak-load forecast (root "pk"), #063 plant climate (root "cl").
import { $, table, chart, bars, el, text, clear, fmt, pct, getJSON, INK, SLATE, BLUE, RED, GREEN, AMBER, GREY } from './ui.js';

const URL = '/data/energy.json';
const set = (root, k, v) => { const e = document.querySelector(`#${root} [data-k="${k}"]`); if (e) e.textContent = v; };
let cache;
const data = () => (cache ||= getJSON(URL));
const GW = v => fmt(v / 1000, 2);
const NAMES = { '2P': 'Linear (2P)', '3PC': 'Resfriamento (3PC)', '3PH': 'Aquecimento (3PH)', '4P': 'Duas inclinações (4P)', '5P': 'Banda morta (5P)' };

// ---------------------------------------------------------------- #008
export async function initChangepoint() {
  const d = await data(), c = d.changepoint, b = c.models[c.best], ci = c.best_ci;
  set('cp', 'tb', `${fmt(b.cps[0], 1)} °C`);
  set('cp', 'slope', `${GW(b.slopes[1])} GW/°C`);
  set('cp', 'cv', pct(b.cvrmse, 1));
  set('cp', 'neff', `${fmt(b.n_eff, 0)} de ${c.n}`);
  $('cp-kpi-note').textContent = `${c.n} dias úteis de ${c.years[0]} a ${c.years[c.years.length - 1]} (sem feriados, pontes e o confinamento de mar.–jun. de 2020). Ponto de equilíbrio com intervalo de 95 % de ${fmt(ci.cp[0], 1)} a ${fmt(ci.cp[1], 1)} °C; inclinação acima dele de ${GW(ci.slope_above[0])} a ${GW(ci.slope_above[1])} GW/°C (bootstrap em blocos de 28 dias).`;
  chart($('cp-scatter'), [
    { x: c.scatter.T, y: c.scatter.y.map(v => v / 1000), color: BLUE, dots: true, r: 1.7, opacity: 0.35, label: 'dia útil (nível de 2019)' },
    { x: c.curve.T, y: c.curve.y.map(v => v / 1000), color: RED, width: 2, label: `modelo ${c.best}` },
  ], { height: 320, xLabel: 'temperatura média diária, média de São Paulo, Rio e Belo Horizonte (°C)', yLabel: 'carga média do SE/CO (GW)', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0),
    vlines: [{ x: b.cps[0], color: RED, label: `T_b = ${fmt(b.cps[0], 1)} °C` }] });
  table('cp-models', ['Modelo', 'Ponto(s) de mudança (°C)', 'Inclinações (MW/°C)', 'CV(RMSE)', 'NMBE', 'BIC', 'ρ dos resíduos', 'n efetivo'],
    Object.entries(c.models).map(([k, m]) => [k === c.best ? `<strong>${NAMES[k]}</strong>` : NAMES[k], m.cps.length ? m.cps.map(v => fmt(v, 1)).join(' e ') : '—',
      m.slopes.map(v => fmt(v, 0)).join(' / '), pct(m.cvrmse, 2), fmt(Math.abs(m.nmbe) < 5e-6 ? 0 : 100 * m.nmbe, 3) + ' %', fmt(m.bic, 0), fmt(m.rho, 2), fmt(m.n_eff, 0)]));
  table('cp-years', ['Ano', 'Dias úteis', 'Ponto de equilíbrio (°C)', 'Carga base no ponto (GW)', 'Inclinação acima (GW/°C)', 'CV(RMSE)'],
    Object.entries(c.by_year).map(([y, v]) => [y, String(v.n), fmt(v.cp, 1), GW(v.base), GW(v.slope_cool), pct(v.cvrmse, 1)]));
  $('cp-weekend').textContent = `Fins de semana: ponto de equilíbrio ${fmt(c.weekend.cp, 1)} °C, inclinação ${GW(c.weekend.slope_above)} GW/°C, CV(RMSE) ${pct(c.weekend.cvrmse, 1)}. Com menos indústria e comércio funcionando, sobra menos carga para refrigerar.`;
  $('cp-status').textContent = '';
}

// ---------------------------------------------------------------- #064
function heatmap(svg, H) {
  clear(svg);
  const W = 760, cw = (W - 70) / 24, rh = 18, Hh = 30 + 12 * rh + 30;
  svg.setAttribute('viewBox', `0 0 ${W} ${Hh}`);
  const max = Math.max(...H.flat());
  const M = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
  H.forEach((row, i) => {
    text(svg, 60, 30 + i * rh + 13, M[i], { 'text-anchor': 'end', 'font-size': 10.5, fill: SLATE });
    row.forEach((v, h) => el('rect', { x: 70 + h * cw, y: 30 + i * rh, width: cw - 1, height: rh - 1, fill: BLUE, opacity: (v / max).toFixed(3) }, svg));
  });
  for (let h = 0; h < 24; h += 3) text(svg, 70 + h * cw + cw / 2, 30 + 12 * rh + 16, `${h} h`, { 'text-anchor': 'middle', 'font-size': 10.5, fill: SLATE });
  text(svg, 70, 18, 'Hora do pico diário de carga, por mês (2019–2025); mais escuro = mais dias', { 'font-size': 11, fill: INK });
}

export async function initPeak() {
  const d = await data(), f = d.forecast, M = f.metrics;
  const o = M['Temperatura observada (oráculo)'], n = M['Sem temperatura'], p1 = M['Previsão de temperatura com erro de 1 °C, incerteza propagada'], nv = M['Mesmo dia da semana anterior'];
  set('pk', 'mape', `${fmt(o.mape, 2)} %`);
  set('pk', 'naive', `${fmt(nv.mape, 1)} %`);
  set('pk', 'cover', pct(p1.cover90, 0));
  set('pk', 'rec', `${GW(f.peak_record.mw)} GW`);
  $('pk-kpi-note').textContent = `Treino ${f.train[0]} a ${f.train[1]} (${f.n_train} dias, sem o confinamento de 2020); teste ${f.test[0]} a ${f.test[1]} (${f.n_test} dias). Erro percentual médio com a temperatura observada do dia, o melhor caso possível para a temperatura, e com a regra ingênua de repetir a semana anterior. Recorde da série: ${GW(f.peak_record.mw)} GW em ${f.peak_record.date.split('-').reverse().join('/')}.`;
  const idx = f.dates.map((_, i) => i);
  const s = f.series.prop1;
  chart($('pk-series'), [
    { x: idx, y: f.actual.map(v => v / 1000), color: INK, width: 1.2, label: 'pico real' },
    { x: idx, y: s.p.map(v => v / 1000), color: BLUE, width: 1.2, label: 'previsão (temperatura com erro de 1 °C, faixa de 90 %)', band: { lo: s.lo.map(v => v / 1000), hi: s.hi.map(v => v / 1000) } },
  ], { height: 300, xLabel: `dias de ${f.test[0].slice(0, 4)} no teste`, yLabel: 'pico diário de carga do SE/CO (GW)', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0) });
  table('pk-metrics', ['Previsão de um dia à frente', 'Erro % médio', 'RMSE (MW)', 'CRPS (MW)', 'Cobertura 90 %'],
    Object.entries(M).map(([k, v]) => [k, fmt(v.mape, 2) + ' %', fmt(v.rmse, 0), v.crps == null ? '—' : fmt(v.crps, 0), v.cover90 == null ? '—' : pct(v.cover90, 0)]));
  $('pk-value').textContent = `Com a temperatura observada, o modelo erra ${fmt(o.mape, 2)} %; sem temperatura, ${fmt(n.mape, 2)} %. Uma previsão de temperatura com 1 °C de erro já leva o ganho a zero (${fmt(p1.mape, 2)} %, CRPS ${fmt(p1.crps, 0)} contra ${fmt(n.crps, 0)} MW): a carga de ontem, que entra pelo termo autorregressivo (φ = ${fmt(f.phi, 2)}), já carrega a maior parte da informação do tempo. Usar a temperatura prevista como se fosse certa deixa o intervalo estreito demais (cobertura ${pct(M['Previsão de temperatura com erro de 1 °C, valor direto'].cover90, 0)}); propagar a incerteza devolve a cobertura a ${pct(p1.cover90, 0)}.`;
  heatmap($('pk-heat'), f.peak_hour_heatmap);
  bars($('pk-aft'), [{ label: 'Dias com o pico entre 12 h e 16 h', bars: Object.entries(f.afternoon_share).map(([y, v]) => ({ name: y, v, color: AMBER })) }]);
  $('pk-status').textContent = '';
}

// ---------------------------------------------------------------- #063
export async function initClimate() {
  const d = await data(), c = d.climate, R = c.results;
  const mean = (n, k) => Object.values(R[n]).reduce((a, v) => a + v[k], 0) / Object.keys(R[n]).length;
  const S = Object.keys(R);
  set('cl', 'mwh', `${fmt(mean(S[0], 'cooling_mwh'), 0)} × ${fmt(mean(S[3], 'cooling_mwh'), 0)} MWh`);
  set('cl', 'hours', `${fmt(mean(S[0], 'hours_above_30'), 0)} h`);
  set('cl', 'r2', fmt(c.r2_cooling_cdd[S[0]], 2));
  set('cl', 'trend', `p = ${fmt(c.trends_sp.tmean.p, 2)}`);
  $('cl-kpi-note').textContent = `Estação INMET ${c.station.id} (${c.station.name}, ${fmt(c.station.elev_m, 0)} m), anos com pelo menos 330 dias válidos: ${c.sim_years.join(', ')}. Galpão hipotético de ${fmt(c.scenarios[S[0]].area, 0)} m²; energia elétrica anual de resfriamento para manter 26 °C, telha metálica escura × telha sanduíche branca.`;
  const w = c.week, idx = w.t.map((_, i) => i * 2);
  const col = [RED, AMBER, BLUE, GREEN];
  chart($('cl-week'), [
    { x: idx, y: w.T_out, color: INK, width: 1.4, dash: '4 3', label: 'externa' },
    ...S.map((n, i) => ({ x: idx, y: w.Ti[n], color: col[i], width: 1.5, label: n.toLowerCase() })),
  ], { height: 300, xLabel: `horas da semana mais quente dos anos completos (até ${w.t[w.t.length - 1].slice(0, 10).split('-').reverse().join('/')})`, yLabel: 'temperatura (°C), sem ar-condicionado', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0) });
  table('cl-scen', ['Cobertura', 'U do telhado (W/m²K)', 'Absortância', 'Horas acima de 30 °C por ano', 'Resfriamento (MWh/ano)', 'Pico elétrico (kW)', 'R² com graus-dia'],
    S.map(n => {
      const v = Object.values(R[n]);
      const rng = k => `${fmt(Math.min(...v.map(x => x[k])), 0)}–${fmt(Math.max(...v.map(x => x[k])), 0)}`;
      return [n, fmt(c.scenarios[n].U_roof, 1), fmt(c.scenarios[n].alpha, 1), rng('hours_above_30'), rng('cooling_mwh'), rng('peak_kw'), fmt(c.r2_cooling_cdd[n], 2)];
    }));
  table('cl-annual', ['Ano', 'Dias válidos', 'Média (°C)', 'Máxima média (°C)', 'Graus-dia de resfriamento (base 18)', 'Graus-dia de aquecimento', 'Dias ≥ 32 °C'],
    Object.entries(c.annual).map(([y, v]) => [y, fmt(v.days, 0), fmt(v.tmean, 1), fmt(v.tmax_mean, 1), fmt(v.cdd, 0), fmt(v.hdd, 0), fmt(v.hot_days, 0)]));
  const tr = (t, lab) => Object.entries(t).map(([k, v]) => [`${lab}: ${{ tmean: 'temperatura média', cdd: 'graus-dia de resfriamento', hot_days: 'dias ≥ 32 °C' }[k]}`, String(v.n), fmt(v.z, 2), fmt(v.p, 2),
    `${fmt(v.sen, 3)} <small>[${fmt(v.sen_ci95[0], 3)}; ${fmt(v.sen_ci95[1], 3)}]</small>`]);
  table('cl-trend', ['Série', 'Anos', 'z de Mann–Kendall', 'p', 'Inclinação de Sen por ano'], [...tr(c.trends, 'Taubaté'), ...tr(c.trends_sp, 'São Paulo (A701)')]);
  $('cl-status').textContent = '';
}
