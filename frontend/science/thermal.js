// Phase 5b — furnace heat balance and machining energy (#029, root "fu"), bath kinetics and
// concentrate replenishment (#070, root "bh").
import { $, table, chart, bars, el, text, clear, fmt, pct, getJSON, INK, SLATE, BLUE, RED, GREEN, AMBER, GREY } from './ui.js';

const URL = '/data/thermal.json';
const set = (root, k, v) => { const e = document.querySelector(`#${root} [data-k="${k}"]`); if (e) e.textContent = v; };
let cache;
const data = () => (cache ||= getJSON(URL));

// Diverging horizontal bars for coefficients in [-1, 1].
function diverging(svg, rows) {
  clear(svg);
  const W = 760, rh = 24, H = 30 + rows.length * rh + 30;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const l = 270, r = W - 40, mid = (l + r) / 2, x = v => mid + v * (r - l) / 2;
  [-1, -0.5, 0, 0.5, 1].forEach(v => {
    el('line', { x1: x(v), x2: x(v), y1: 20, y2: H - 30, stroke: v === 0 ? SLATE : '#e3e6ea' }, svg);
    text(svg, x(v), H - 12, fmt(v, 1), { 'text-anchor': 'middle', 'font-size': 10.5, fill: SLATE });
  });
  rows.forEach((row, i) => {
    const y = 24 + i * rh;
    el('rect', { x: Math.min(x(0), x(row.v)), y, width: Math.max(Math.abs(x(row.v) - x(0)), 1), height: rh - 8, fill: row.v >= 0 ? RED : BLUE, opacity: 0.85 }, svg);
    text(svg, l - 10, y + 12, row.name, { 'text-anchor': 'end', 'font-size': 11, fill: INK });
    text(svg, row.v >= 0 ? x(row.v) + 6 : x(row.v) - 6, y + 12, fmt(row.v, 2), { 'text-anchor': row.v >= 0 ? 'start' : 'end', 'font-size': 10.5, fill: SLATE });
  });
}

function histogram(svg, counts, edges, { xLabel, color = BLUE, marks = [] }) {
  clear(svg);
  const W = 760, H = 240, box = { l: 52, r: W - 14, t: 20, b: H - 40 };
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const x = v => box.l + (v - edges[0]) / (edges[edges.length - 1] - edges[0]) * (box.r - box.l);
  const max = Math.max(...counts), y = v => box.b - v / max * (box.b - box.t);
  counts.forEach((c, i) => el('rect', { x: x(edges[i]) + 0.5, y: y(c), width: Math.max(x(edges[i + 1]) - x(edges[i]) - 1, 1), height: box.b - y(c), fill: color, opacity: 0.75 }, svg));
  el('line', { x1: box.l, x2: box.r, y1: box.b, y2: box.b, stroke: SLATE }, svg);
  const n = 6, step = (edges[edges.length - 1] - edges[0]) / n;
  for (let i = 0; i <= n; i++) { const v = edges[0] + i * step; text(svg, x(v), box.b + 16, fmt(v, 0), { 'text-anchor': 'middle', 'font-size': 10.5, fill: SLATE }); }
  text(svg, (box.l + box.r) / 2, H - 6, xLabel, { 'text-anchor': 'middle', 'font-size': 11, fill: SLATE });
  marks.forEach(m => {
    el('line', { x1: x(m.v), x2: x(m.v), y1: box.t, y2: box.b, stroke: m.color || INK, 'stroke-dasharray': '3 3' }, svg);
    text(svg, x(m.v) + 4, box.t + 10, m.label, { 'font-size': 10.5, fill: m.color || INK });
  });
}

// ---------------------------------------------------------------- #029
export async function initFurnace() {
  const d = await data(), f = d.furnace, m = d.machining, E = f.energy_kwh;
  set('fu', 'kwht', `${fmt(f.kwh_per_t, 0)} kWh/t`);
  set('fu', 'eff', pct(f.efficiency, 0));
  set('fu', 'cycle', `${fmt(f.t_cycle_h, 2)} h`);
  set('fu', 'ratio', `${fmt(m.per_m_bar.furnace_kwh / m.per_m_bar.turning_kwh, 1)} ×`);
  $('fu-kpi-note').textContent = `Forno elétrico hipotético de ${f.furnace.inner_m.join(' × ')} m, a ${fmt(f.furnace.T_set, 0)} °C, com ${fmt(f.furnace.P_max_kw, 0)} kW instalados; carga de ${fmt(f.charge.mass, 0)} kg de barras de aço Ø${fmt(f.charge.diameter_mm, 0)} mm, aquecidas até o núcleo chegar a ${fmt(f.charge.T_core_target, 0)} °C e mais ${fmt(f.charge.soak_min, 0)} min de encharque. A última razão compara a energia do tratamento térmico com a de um passe de desbaste no torno, por metro de barra. Faixa de 90 % da energia por tonelada pelas incertezas dos parâmetros: ${fmt(f.mc.p5, 0)} a ${fmt(f.mc.p95, 0)} kWh/t.`;
  const c = f.cycle;
  chart($('fu-cycle'), [
    { x: c.t_min, y: c.T_chamber, color: RED, width: 1.6, label: 'câmara' },
    { x: c.t_min, y: c.T_surf, color: AMBER, width: 1.6, label: 'superfície da barra' },
    { x: c.t_min, y: c.T_core, color: BLUE, width: 1.8, label: 'núcleo da barra' },
  ], { height: 300, xLabel: 'minutos desde a carga', yLabel: 'temperatura (°C)', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0),
    vlines: [{ x: f.t_core_h * 60, color: SLATE, label: 'núcleo no alvo' }], hlines: [{ y: 735, color: GREY, label: '' }] });
  chart($('fu-power'), [{ x: c.t_min, y: c.P_kw, color: INK, width: 1.6, label: 'potência elétrica' }],
    { height: 220, xLabel: 'minutos desde a carga', yLabel: 'kW', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0), yDomain: [0, f.furnace.P_max_kw * 1.1],
      hlines: [{ y: f.furnace.P_max_kw, color: RED, label: '' }] });
  $('fu-power-note').textContent = `Nos primeiros ${fmt(f.power_limited_min, 0)} min a carga fria pede mais do que os ${fmt(f.furnace.P_max_kw, 0)} kW instalados e a câmara cai abaixo do ponto de ajuste; a linha cinza do gráfico de temperatura marca 735 °C, onde o calor específico do aço tem o pico da transformação (EN 1993-1-2) e o núcleo desacelera.`;
  const parts = [['Carga (útil)', E.charge, BLUE], ['Paredes', E.wall, AMBER], ['Porta: radiação', E.door_rad, RED], ['Porta: troca de ar', E.door_conv, GREY]];
  bars($('fu-sankey'), [{ label: `Energia de um ciclo: ${fmt(E.total, 1)} kWh`, bars: parts.map(([n, v, col]) => ({ name: `${n} (${fmt(v, 1)} kWh)`, v: v / E.total, color: col })) }]);
  $('fu-closure').textContent = `Fechamento do balanço: a energia elétrica integrada difere da soma das parcelas em ${fmt(f.closure_pct, 2)} %. A entalpia da carga pelo calor específico da norma, de 25 °C até a temperatura média final de ${fmt(f.T_mean_final, 0)} °C, dá ${fmt(f.enthalpy_check_kwh, 1)} kWh; a simulação acumulou ${fmt(E.charge, 1)} kWh.`;
  table('fu-walls', ['Face', 'Área média (m²)', 'Fluxo (W/m²)', 'Carcaça (°C)', 'Interfaces (°C)', 'Perda (kW)'],
    f.walls.map(w => [w.name, fmt(w.area, 2), fmt(w.q, 0), fmt(w.Ts, 1), w.interfaces.map(t => fmt(t, 0)).join(' → '), fmt(w.Q_kw, 2)]));
  table('fu-layers', ['Camada', 'Espessura (mm)', 'k na face quente', 'k na face fria', 'Face quente (°C)', 'Limite de serviço (°C)'],
    f.layers.map(l => [l.name, fmt(l.L_mm, 0), fmt(l.k_hot, 3), fmt(l.k_cold, 3), fmt(l.T_hot, 0), fmt(l.T_limit, 0)]));
  const dr = f.door;
  $('fu-door').textContent = `Porta aberta (${f.furnace.door_m.join(' × ')} m numa parede de ${fmt(f.furnace.wall_mm, 0)} mm): fator de forma entre as faces da abertura F₁₂ = ${fmt(dr.F12, 3)}, fator de troca com batentes rerradiantes (1 + F₁₂)/2 = ${fmt(dr.Fbar, 3)}, radiação de ${fmt(dr.rad_kw, 1)} kW. A troca de ar pela porta (${fmt(dr.V_m3s, 2)} m³/s) leva ${fmt(dr.conv_kw, 1)} kW com o gás da câmara a ${fmt(dr.T_gas, 0)} °C, limitado pelo calor que o revestimento consegue passar ao ar que entra. Se o ar saísse à temperatura do forno seriam ${fmt(dr.conv_unlimited_kw, 0)} kW, mais que a potência instalada: o limite é o que torna a estimativa física.`;
  histogram($('fu-mc'), f.mc.hist, f.mc.edges, { xLabel: `energia por tonelada (kWh/t), ${f.mc.n} sorteios`, marks: [{ v: f.kwh_per_t, label: 'caso base', color: RED }] });
  diverging($('fu-srrc'), Object.entries(f.mc.srrc).map(([name, v]) => ({ name, v })).sort((a, b) => Math.abs(b.v) - Math.abs(a.v)));
  $('fu-srrc-note').textContent = `Coeficientes de regressão padronizados nos postos (R² = ${fmt(f.mc.r2, 2)}): quanto a energia por tonelada sobe (vermelho) ou desce (azul), em desvios-padrão, para um desvio-padrão do parâmetro. Faixas sorteadas uniformes, descritas no método.`;
  table('fu-weekend', ['Parada (h)', 'Desligado por (h)', 'Reaquecimento (h)', 'Face quente mínima (°C)', 'Manter quente (kWh)', 'Desligar e reaquecer (kWh)', 'Economia (kWh)'],
    f.weekend.map(w => [fmt(w.stop_h, 0), fmt(w.off_h, 1), fmt(w.reheat_h, 1), fmt(w.T_face_min, 0), fmt(w.hold_kwh, 0), fmt(w.off_kwh, 0), `<strong>${fmt(w.saving_kwh, 0)}</strong>`]));
  // machining
  const u = m.u_curve;
  chart($('fu-kienzle'), [
    { x: u.h, y: u.eth_med, color: RED, width: 1.8, label: 'Ck45 medido (ETH), mediana e extremos', band: { lo: u.eth_min, hi: u.eth_max } },
    { x: u.h, y: u.catalog, color: BLUE, width: 1.8, dash: '5 3', label: 'catálogo VDI 3323, aço ≥ 0,25 % C recozido' },
  ], { height: 280, xLabel: 'espessura do cavaco h (mm)', yLabel: 'energia específica de corte (J/mm³)', xFmt: v => fmt(v, 2), yFmt: v => fmt(v, 1) });
  const sc = m.sweep.catalog, se = m.sweep.eth_median;
  chart($('fu-gutowski'), [
    { x: se.mrr.map(v => v / 1000), y: se.e, color: RED, width: 1.8, label: 'eletricidade por volume, k_c medido' },
    { x: sc.mrr.map(v => v / 1000), y: sc.e, color: BLUE, width: 1.8, dash: '5 3', label: 'eletricidade por volume, k_c de catálogo' },
  ], { height: 280, xLabel: 'taxa de remoção (cm³/s), a_p = 5 mm, v_c = 200 m/min, avanço de 0,05 a 0,5 mm', yLabel: 'J/mm³', xFmt: v => fmt(v, 1), yFmt: v => fmt(v, 1) });
  const p = m.pass;
  $('fu-machining-note').textContent = `Passe de desbaste de Ø80 para Ø70 mm em 1 m de barra (v_c = 200 m/min, f = 0,25 mm, a_p = ${fmt(p.ap, 1)} mm): força de corte ${fmt(p.Fc, 0)} N, potência de corte ${fmt(p.Pc / 1000, 1)} kW, ${fmt(p.t / 60, 1)} min, ${fmt(p.E_J / 3.6e6, 2)} kWh no quadro elétrico (${fmt(p.e_J_mm3, 2)} J/mm³, dos quais ${fmt(p.u_J_mm3, 2)} J/mm³ no cavaco). O tratamento térmico do mesmo metro de barra consome ${fmt(m.per_m_bar.furnace_kwh, 1)} kWh. Com avanço baixo o torno gasta ${pct(sc.idle[0], 0)} da eletricidade só para ficar pronto (P₀ = ${fmt(m.lathe.P0_kw, 0)} kW); no avanço máximo, ${pct(sc.idle[sc.idle.length - 1], 0)}.`;
  table('fu-vdi', ['Material (VDI 3323)', 'Resistência (MPa)', 'k_c1.1 (N/mm²)', 'm_c'], m.vdi3323.map(r => [r.name, fmt(r.Rm, 0), fmt(r.kc1, 0), fmt(r.mc, 2)]));
  const kcs = [...m.eth.kc].sort((a, b) => a - b);
  $('fu-eth').textContent = `Medição de Klippel et al. (ETH Zürich) em Ck45 com ${m.eth.Rm} MPa: k_c1.1 de ${fmt(kcs[0], 0)} a ${fmt(kcs[kcs.length - 1], 0)} N/mm² e m_c de ${fmt(Math.min(...m.eth.mc), 2)} a ${fmt(Math.max(...m.eth.mc), 2)} entre as velocidades de corte ensaiadas. O valor de catálogo para esse aço (1.500 N/mm²) fica abaixo de ${m.eth.kc.filter(v => v > 1500).length} das ${m.eth.kc.length} medições: a força real tende a ser maior, e o catálogo serve como ordem de grandeza.`;
  $('fu-status').textContent = '';
}

// ---------------------------------------------------------------- #070
export async function initBath() {
  const d = await data(), b = d.bath, F = b.fits, P = b.policies, sh = b.show;
  set('bh', 'demand', `${fmt(F.single.demand_ci[0], 2)}–${fmt(F.single.demand_ci[1], 2)} kg`);
  set('bh', 'corr', `${fmt(F.single.corr_qr, 3)} → ${fmt(F.two_bands.corr_qr, 2)}`);
  set('bh', 'svc', `${pct(P.fixed_lead.cycle_service, 0)} → ${pct(P.random_lead.cycle_service, 0)}`);
  set('bh', 'cost', `${fmt(P.simulated_optimum.cost / 1000, 1)} mil`);
  $('bh-kpi-note').textContent = `Banho hipotético de ${fmt(b.bath.V, 0)} L mantido entre ${fmt(b.bath.C_min, 0)} e ${fmt(b.bath.C_set, 0)} g/L, titulado a cada 4 h durante quatro semanas (titulações sintéticas, desvio de 0,25 g/L). Consumo de concentrado por dia útil com intervalo de 95 % por bootstrap paramétrico; valor verdadeiro da simulação: ${fmt(F.single.demand_true, 2)} kg. A segunda métrica é a correlação entre as estimativas de arraste e de reação: com uma faixa de concentração, e com duas. A terceira é o nível de serviço por ciclo da regra clássica, ignorando e considerando a variação do prazo do fornecedor. Custo anual em R$ da política ótima simulada.`;
  const days = sh.h.map(h => h / 24);
  chart($('bh-series'), [
    { x: days, y: sh.C, color: BLUE, width: 1.3, label: 'concentração simulada' },
    { x: sh.t_obs.map(h => h / 24), y: sh.y_obs, color: INK, dots: true, r: 1.8, opacity: 0.7, label: 'titulações' },
  ], { height: 280, xLabel: 'dias (segunda a domingo, quatro semanas)', yLabel: 'g/L', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0),
    hlines: [{ y: b.bath.C_min, color: RED, label: '' }, { y: b.bath.C_set, color: GREEN, label: '' }] });
  $('bh-series-note').textContent = `${sh.adds} adições de concentrado em quatro semanas, ${fmt(sh.g_per_add / 1000, 1)} kg de ativo em média por adição. Nos fins de semana não há produção e a queda é só a decomposição: é esse trecho que separa k_d do arraste.`;
  const names = ['k_d (1/h)', 'arraste q (L/h)', 'reação r (g/m²)'];
  const row = (lab, f) => [lab, String(f.n), ...f.theta.map((v, i) => `${fmt(v, i === 0 ? 4 : 2)} <small>± ${fmt(f.se[i], i === 0 ? 5 : 2)}</small>`), fmt(f.corr_qr, 3)];
  table('bh-fits', ['Desenho das titulações', 'n', ...names, 'Correlação q × r'], [
    ['Valor usado na simulação', '—', ...b.truth.map((v, i) => fmt(v, i === 0 ? 4 : 2)), '—'],
    row('Uma faixa (26–30 g/L), com fins de semana', F.single),
    row('Uma faixa, só em dias de produção', F.single_noweekend),
    row('Duas faixas alternadas (26–30 e 18–22 g/L)', F.two_bands),
  ]);
  $('bh-fit-note').textContent = `Com uma faixa estreita de concentração, arraste (proporcional a C) e reação (independente de C) produzem quedas quase iguais e a correlação entre as estimativas chega a ${fmt(F.single.corr_qr, 3)}: o bootstrap dá r entre ${fmt(F.single.boot_r_ci[0], 2)} e ${fmt(F.single.boot_r_ci[1], 2)} g/m². O consumo total, que é o que importa para comprar concentrado, continua preciso. Alternar a faixa de trabalho numa semana separa os dois mecanismos.`;
  const pol = [['Regra clássica, prazo fixo de ' + fmt(b.demand.EL, 1) + ' dias', P.fixed_lead], ['Regra clássica com a variância do prazo', P.random_lead], ['Ótimo da simulação (grade de s e S)', P.simulated_optimum]];
  table('bh-policies', ['Política', 's (kg)', 'S (kg)', 'Pedidos/ano', 'Estoque médio (kg)', 'Dias sem concentrado/ano', 'Serviço por ciclo', 'Custo anual (R$)'],
    pol.map(([n, p]) => [n, fmt(p.s, 0), fmt(p.S, 0), fmt(p.orders_per_year, 1), fmt(p.mean_inventory, 0), fmt(p.stockout_days_per_year, 2), pct(p.cycle_service, 1), fmt(p.cost, 0)]));
  $('bh-policy-note').textContent = `Demanda diária média de ${fmt(b.demand.mean, 1)} kg (desvio ${fmt(b.demand.sd, 1)} kg, zero nos fins de semana). O prazo do fornecedor varia de 4 a 10 dias (média ${fmt(b.demand.EL, 1)}, variância ${fmt(b.demand.VL, 2)} dias²). Ignorar essa variância encolhe o desvio da demanda no prazo de ${fmt(P.random_lead.sdL, 1)} para ${fmt(P.fixed_lead.sdL, 1)} kg e o ponto de pedido cai para ${fmt(P.fixed_lead.s, 0)} kg: o serviço fica em ${pct(P.fixed_lead.cycle_service, 0)} contra a meta de 99 %. Custos: R$ ${fmt(b.costs.K, 0)} por pedido, R$ ${fmt(b.costs.h, 2)} por kg·dia em estoque e R$ ${fmt(b.costs.p_stop / 1000, 0)} mil por dia de linha parada.`;
  $('bh-status').textContent = '';
}

// ---------------------------------------------------------------- #090 and #069
const URL2 = '/data/tariff_plume.json';
let cache2;
const data2 = () => (cache2 ||= getJSON(URL2));
const R$ = v => `R$ ${fmt(v / 1000, 0)} mil`;

export async function initTariff() {
  const d = (await data2()).tariff, B = d.base, tf = d.tariffs;
  const sv = d.sweep.Verde, s3 = sv.find(s => s.alpha === 0.3);
  set('tf', 'verde', R$(B.Verde.annual));
  set('tf', 'azul', R$(B.Azul.annual));
  set('tf', 'shift', R$(B.Verde.annual - s3.annual));
  set('tf', 'mwh', `R$ ${fmt((tf.Verde.E_p - tf.Verde.E_fp) / 1000, 2)}/kWh`);
  $('tf-kpi-note').textContent = `Curva real de 15 minutos de uma siderúrgica (${fmt(d.load.energy_mwh, 0)} MWh em 2018, pico de ${fmt(d.load.max_kw, 0)} kW, fator de carga ${pct(d.load.load_factor, 0)}) faturada nas tarifas de aplicação da EDP São Paulo para o subgrupo A4 (REH 3.541/2025, sem tributos nem bandeira), com a demanda contratada otimizada em cada modalidade. Economia anual na Verde se 30 % da carga de cada intervalo de ponta for deslocada para fora da ponta no mesmo dia (${fmt(s3.moved_mwh, 1)} MWh); a última métrica é quanto vale cada kWh tirado da ponta na Verde.`;
  const p = d.load, x = p.profile_min.map(v => v / 60);
  chart($('tf-profile'), [
    { x, y: p.profile, color: INK, width: 1.6, label: 'dia útil médio, real' },
    { x, y: p.profile_shifted, color: GREEN, width: 1.6, dash: '5 3', label: 'com 30 % da ponta deslocada (PL)' },
  ], { height: 280, xLabel: 'hora do dia', yLabel: 'kW (média de 15 min)', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0),
    vlines: [{ x: 17.5, color: RED, label: 'ponta' }, { x: 20.5, color: RED }] });
  table('tf-tariffs', ['Modalidade', 'Demanda na ponta (R$/kW)', 'Demanda fora da ponta (R$/kW)', 'Energia na ponta (R$/MWh)', 'Energia fora da ponta (R$/MWh)', 'Demanda contratada ótima (kW)', 'Custo anual'],
    ['Verde', 'Azul'].map(n => [n, fmt(tf[n].D_p, 2) + (n === 'Verde' ? ' <small>(única)</small>' : ''), n === 'Verde' ? '—' : fmt(tf[n].D_fp, 2), fmt(tf[n].E_p, 2), fmt(tf[n].E_fp, 2),
      n === 'Verde' ? fmt(B[n].Dc_p, 0) : `${fmt(B[n].Dc_p, 0)} / ${fmt(B[n].Dc_fp, 0)}`, `<strong>${R$(B[n].annual)}</strong>`]));
  $('tf-breakeven').textContent = `A Azul cobra a demanda da ponta (R$ ${fmt(tf.Azul.D_p, 2)}/kW) e barateia a energia da ponta; a Verde faz o contrário. As duas empatam quando cada kW de pico na ponta é usado ${fmt(d.breakeven.hours, 0)} h por mês, de ${fmt(d.breakeven.peak_hours_month, 0)} h de ponta. Esta planta usa sua demanda de ponta entre ${fmt(Math.min(...d.breakeven.plant_hours), 0)} e ${fmt(Math.max(...d.breakeven.plant_hours), 0)} h por mês, abaixo do empate: a Verde é mais barata em todos os meses. Com a ponta das 18 h às 21 h, a Verde custaria ${R$(d.alt_peak_18_21.Verde)} e a Azul ${R$(d.alt_peak_18_21.Azul)}.`;
  const cc = B.Verde.contract_curve;
  chart($('tf-contract'), [{ x: cc.Dc, y: cc.annual.map(v => v / 1000), color: BLUE, width: 1.6, label: 'Verde: custo anual × demanda contratada' }],
    { height: 240, xLabel: 'demanda contratada (kW)', yLabel: 'R$ mil por ano', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0),
      vlines: [{ x: B.Verde.Dc_p, color: RED, label: `ótimo: ${fmt(B.Verde.Dc_p, 0)} kW` }], yDomain: [Math.min(...cc.annual) / 1000 * 0.98, Math.min(...cc.annual) / 1000 * 1.12] });
  const va = d.sweep.Verde, az = d.sweep.Azul;
  chart($('tf-sweep'), [
    { x: va.map(s => s.alpha * 100), y: va.map(s => s.annual / 1000), color: GREEN, width: 1.8, label: 'Verde' },
    { x: az.map(s => s.alpha * 100), y: az.map(s => s.annual / 1000), color: BLUE, width: 1.8, label: 'Azul' },
  ], { height: 260, xLabel: 'parcela da carga de ponta que pode ser deslocada (%)', yLabel: 'R$ mil por ano', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0) });
  $('tf-sweep-note').textContent = `Na Verde, cada MWh tirado da ponta economiza a diferença de tarifa de energia, R$ ${fmt(tf.Verde.E_p - tf.Verde.E_fp, 0)}, e a economia cresce em linha reta: o programa linear não precisa subir a demanda fora da ponta para acomodar a carga. Na Azul, deslocar também derruba a demanda de ponta cobrada, mas não o bastante para a Azul passar a Verde nem com metade da ponta deslocada (${R$(az[az.length - 1].annual)} contra ${R$(va[va.length - 1].annual)}).`;
  table('tf-scale', ['Componente (A4)', 'TUSD do espelho ÷ 100 (R$/kW)', 'Fio B, segundo espelho (R$/kW)'],
    [['Verde, demanda', fmt(tf.Verde.parts.D, 2), fmt(d.fiob['Verde Não se aplica'], 2)], ['Azul, demanda na ponta', fmt(tf.Azul.parts.D_p, 2), fmt(d.fiob['Azul Ponta'], 2)], ['Azul, demanda fora da ponta', fmt(tf.Azul.parts.D_fp, 2), fmt(d.fiob['Azul Fora ponta'], 2)]]);
  $('tf-status').textContent = '';
}

function polarField(svg, field, dirs, xs, { max }) {
  clear(svg);
  const W = 520, c = W / 2, R = W / 2 - 40;
  svg.setAttribute('viewBox', `0 0 ${W} ${W}`);
  const lr = v => Math.log10(v / xs[0]) / Math.log10(xs[xs.length - 1] / xs[0]) * R;
  const edges = xs.map((v, i) => i === 0 ? v : Math.sqrt(v * xs[i - 1]));
  edges.push(xs[xs.length - 1]);
  const step = (dirs[1] - dirs[0]) * Math.PI / 180;
  dirs.forEach((dg, i) => {
    const a0 = dg * Math.PI / 180 - step / 2, a1 = a0 + step;
    field[i].forEach((v, j) => {
      const r0 = lr(edges[j]), r1 = lr(edges[j + 1]);
      const p = (r, a) => `${c + r * Math.sin(a)},${c - r * Math.cos(a)}`;
      const t = Math.min(v / max, 1);
      el('path', { d: `M${p(r0, a0)} L${p(r1, a0)} A${r1},${r1} 0 0 1 ${p(r1, a1)} L${p(r0, a1)} A${r0},${r0} 0 0 0 ${p(r0, a0)} Z`, fill: RED, opacity: (0.04 + 0.9 * Math.sqrt(t)).toFixed(3), stroke: 'none' }, svg);
    });
  });
  [500, 1000, 2000, 5000, 10000].forEach(v => {
    el('circle', { cx: c, cy: c, r: lr(v), fill: 'none', stroke: '#9aa3ad', 'stroke-dasharray': '2 3' }, svg);
    text(svg, c + 3, c - lr(v) - 3, v >= 1000 ? `${v / 1000} km` : `${v} m`, { 'font-size': 10, fill: SLATE });
  });
  [['N', 0], ['L', 90], ['S', 180], ['O', 270]].forEach(([n, a]) => text(svg, c + (R + 16) * Math.sin(a * Math.PI / 180), c - (R + 16) * Math.cos(a * Math.PI / 180) + 4, n, { 'text-anchor': 'middle', 'font-size': 12, fill: INK }));
  el('circle', { cx: c, cy: c, r: 3, fill: INK }, svg);
}

function windRose(svg, rose, bins) {
  clear(svg);
  const W = 420, c = W / 2, R = W / 2 - 40;
  svg.setAttribute('viewBox', `0 0 ${W} ${W}`);
  const tot = rose.map(r => r.reduce((a, b) => a + b, 0)), mx = Math.max(...tot);
  const cols = ['#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c'];
  const step = 22.5 * Math.PI / 180;
  rose.forEach((row, i) => {
    let acc = 0;
    const a0 = i * step - step * 0.42, a1 = i * step + step * 0.42;
    row.forEach((v, k) => {
      const r0 = Math.sqrt(acc / mx) * R, r1 = Math.sqrt((acc + v) / mx) * R;
      acc += v;
      if (v <= 0) return;
      const p = (r, a) => `${c + r * Math.sin(a)},${c - r * Math.cos(a)}`;
      el('path', { d: `M${p(r0, a0)} L${p(r1, a0)} A${r1},${r1} 0 0 1 ${p(r1, a1)} L${p(r0, a1)} A${r0},${r0} 0 0 0 ${p(r0, a0)} Z`, fill: cols[k], stroke: '#fff', 'stroke-width': 0.5 }, svg);
    });
  });
  [['N', 0], ['L', 90], ['S', 180], ['O', 270]].forEach(([n, a]) => text(svg, c + (R + 16) * Math.sin(a * Math.PI / 180), c - (R + 16) * Math.cos(a * Math.PI / 180) + 4, n, { 'text-anchor': 'middle', 'font-size': 12, fill: INK }));
  const labs = bins.map((b, k) => k < bins.length - 1 ? `${b}–${bins[k + 1]}` : `≥ ${b}`);
  labs.forEach((l, k) => { el('rect', { x: 8, y: 8 + k * 16, width: 12, height: 10, fill: cols[k] }, svg); text(svg, 24, 17 + k * 16, `${l} m/s`, { 'font-size': 10.5, fill: SLATE }); });
}

export async function initPlume() {
  const d = (await data2()).plume, R = d.results, o = R.overcast;
  set('pl', 'q', `${fmt(d.q_allow.governing, 0)} g/s`);
  set('pl', 'max24', `${fmt(o.max24, 2)} µg/m³`);
  set('pl', 'calm', pct(d.calm_share, 0));
  set('pl', 'stable', pct((o.classes['4.0'] || 0) + (o.classes['5.0'] || 0), 0));
  $('pl-kpi-note').textContent = `Chaminé hipotética de ${fmt(d.stack.h, 0)} m, Ø${fmt(d.stack.d, 1)} m, gases a ${fmt(d.stack.v, 0)} m/s e ${fmt(d.stack.Ts - 273.15, 0)} °C, emitindo 1 g/s de MP10; tempo real de Taubaté (INMET A728), ${fmt(d.valid, 0)} horas válidas de ${d.years[0]} a ${d.years[d.years.length - 1]}. A primeira métrica é a maior emissão que mantém a máxima média de 24 h e a média anual em qualquer receptor abaixo dos valores-guia da OMS de 2021 (${d.who['24h']} e ${d.who.annual} µg/m³), sem contar a concentração de fundo. Depois, a pior média de 24 h por g/s, a fração de horas de calmaria (< 1 m/s) e a fração de horas estáveis (classes E e F).`;
  windRose($('pl-rose'), d.rose, d.rose_bins);
  polarField($('pl-field'), o.annual, d.dirs, d.xs, { max: o.annual_max });
  $('pl-field-note').textContent = `Média anual ao nível do solo por g/s emitido, receptores a cada 10° entre 100 m e 10 km. Máximo de ${fmt(o.annual_max, 2)} µg/m³ a ${fmt(o.annual_at[1], 0)} m na direção ${fmt(o.annual_at[0], 0)}° a partir da chaminé; a pior média de 24 h (${fmt(o.max24, 2)} µg/m³, ${o.days} dias com pelo menos 18 h válidas) cai a ${fmt(o.max24_at[1], 0)} m na direção ${fmt(o.max24_at[0], 0)}°. Altura efetiva mediana da pluma: ${fmt(o.H_median, 0)} m.`;
  const C = d.centerline, cols = { A: RED, B: AMBER, C: GREEN, D: BLUE, E: INK, F: GREY };
  chart($('pl-center'), Object.entries(C).map(([k, v]) => ({ x: d.xs.map(x => x / 1000), y: v.c, color: cols[k], width: 1.6, label: `${k} (H = ${fmt(v.H, 0)} m)` })),
    { height: 280, xLabel: 'distância a favor do vento (km), vento de 2 m/s a 10 m', yLabel: 'µg/m³ por g/s no eixo', xFmt: v => fmt(v, 1), yFmt: v => fmt(v, 1) });
  table('pl-night', ['Hipótese para a noite', 'Classes E + F', 'Máxima média anual', 'Máxima média de 24 h', 'Percentil 98 das médias de 24 h'],
    [['Nublado (≥ 4/8): classes D e E', R.overcast, 'overcast'], ['Céu limpo (≤ 3/8): classes E e F', R.clear, 'clear']].map(([n, r]) =>
      [n, pct((r.classes['4.0'] || 0) + (r.classes['5.0'] || 0), 0), fmt(r.annual_max, 3), fmt(r.max24, 2), fmt(r.p98_24_max, 2)]));
  $('pl-night-note').textContent = `A estação não registra nebulosidade, então a classe noturna é incerta. As duas hipóteses extremas mudam pouco as máximas, porque elas acontecem perto da fonte com o ar instável do dia, quando a pluma desce rápido; a noite estável leva a pluma longe e diluída. Emissão compatível com a média de 24 h: ${fmt(d.q_allow.by_24h, 1)} g/s; com a média anual: ${fmt(d.q_allow.by_annual, 1)} g/s.`;
  $('pl-status').textContent = '';
}
