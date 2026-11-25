// Phase 4a — rolling-element bearings on real CWRU data, shared by three pages:
// #004 envelope diagnosis (root "nv"), #104 anomaly detection (root "an"), #052 signatures (root "sg").
import { $, table, chart, el, text, clear, fmt, pct, getJSON, INK, SLATE, RULE, BLUE, RED, GREEN, AMBER, GREY } from './ui.js';

const URL = '/data/bearings-cwru.json';
const CLS = { N: 'Normal', IR: 'Pista interna', B: 'Esfera', OR: 'Pista externa' };
const COL = { N: GREY, IR: RED, B: AMBER, OR: BLUE };
const set = (root, k, v) => { const e = document.querySelector(`#${root} [data-k="${k}"]`); if (e) e.textContent = v; };
let cache;
const data = () => (cache ||= getJSON(URL));

// ---------------------------------------------------------------- #004
function sesPanel(svg, ex, color) {
  const f = ex.fault_hz;
  chart(svg, [{ x: ex.freq, y: ex.ses_db, color, width: 1.1 }],
    { width: 380, height: 220, xDomain: [0, 600], yDomain: [-5, 30], xLabel: 'frequência (Hz)', yLabel: 'SES (dB acima da mediana)', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0), legend: false,
      vlines: [{ x: f.BPFO, color: BLUE, label: 'BPFO', dy: 4 }, { x: f.BPFI, color: RED, label: 'BPFI', dy: 30 }, { x: f['2BSF'], color: AMBER, label: '2·BSF', dy: 17 },
        { x: 2 * f.BPFO, color: BLUE }, { x: 2 * f.BPFI, color: RED }, { x: 3 * f.BPFO, color: BLUE }, { x: 3 * f.BPFI, color: RED }] });
}

function wavePanel(svg, ex, color) {
  const t = ex.wave.map((_, i) => 1000 * 2 * i / 12000);
  const m = Math.max(...ex.wave.map(Math.abs));
  chart(svg, [{ x: t, y: ex.wave, color, width: 0.9 }], { width: 380, height: 150, xDomain: [0, 100], yDomain: [-m, m], xLabel: 'tempo (ms)', yLabel: 'aceleração (g)',
    xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 1), legend: false });
}

function kurtogram(svg, k) {
  clear(svg);
  const W = 760, H = 40 + k.length * 34 + 36;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const box = { l: 160, r: W - 20, t: 24, b: 24 + k.length * 34 };
  const max = Math.max(...k.flatMap(r => r.sk));
  const x = f => box.l + f / 6000 * (box.r - box.l);
  text(svg, box.l, 14, `Curtose espectral, registro 130 (pista externa, 0,007″, 0 hp); máximo ${fmt(max, 1)}`, { 'font-size': 11, fill: INK });
  k.forEach((r, i) => {
    const y = box.t + i * 34;
    text(svg, box.l - 8, y + 21, `janela ${r.nw} · Δf ${fmt(2 * 12000 / r.nw, 0)} Hz`, { 'text-anchor': 'end', 'font-size': 10.5, fill: SLATE });
    const df = r.freq[1] - r.freq[0];
    r.freq.forEach((f, j) => {
      const v = Math.max(r.sk[j], 0) / max;
      el('rect', { x: x(f - df / 2), y, width: Math.max(x(f + df / 2) - x(f - df / 2), 0.5), height: 30, fill: BLUE, opacity: (0.04 + 0.96 * v).toFixed(3) }, svg);
    });
  });
  for (let f = 0; f <= 6000; f += 1000) text(svg, x(f), box.b + 16, fmt(f / 1000, 0) + ' kHz', { 'text-anchor': 'middle', 'font-size': 10.5, fill: SLATE });
}

function recordGrid(svg, recs) {
  clear(svg);
  const rows = [['N', 0], ['IR', 7], ['IR', 14], ['IR', 21], ['B', 7], ['B', 14], ['B', 21], ['OR', 7], ['OR', 14], ['OR', 21]];
  const W = 560, cw = 100, rh = 26, H = 40 + rows.length * rh + 10;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const l = 150;
  [0, 1, 2, 3].forEach(L => text(svg, l + L * cw + cw / 2, 18, `${L} hp`, { 'text-anchor': 'middle', 'font-size': 11, fill: SLATE }));
  const idx = { OR: 0, IR: 1, B: 2 };
  rows.forEach(([c, s], i) => {
    const y = 28 + i * rh;
    text(svg, l - 10, y + 17, c === 'N' ? 'Normal' : `${CLS[c]} ${fmt(s / 1000, 3)}″`, { 'text-anchor': 'end', 'font-size': 11, fill: INK });
    [0, 1, 2, 3].forEach(L => {
      const r = recs.find(q => q.cls === c && q.size === s && q.load === L);
      if (!r) return;
      const ok = r.majority === c;
      el('rect', { x: l + L * cw + 2, y: y + 2, width: cw - 4, height: rh - 4, rx: 3, fill: ok ? GREEN : RED, opacity: 0.16 + 0.6 * r.acc * (ok ? 1 : 0) + (ok ? 0 : 0.2) }, svg);
      const h = c === 'N' ? Math.max(...r.H) : r.H[idx[c]];
      text(svg, l + L * cw + cw / 2, y + 17, `${ok ? '✓' : '✗'} ${fmt(h, 1)} dB`, { 'text-anchor': 'middle', 'font-size': 11, fill: INK });
    });
  });
}

function confusion(id, d) {
  const names = d.classes.map(c => CLS[c]);
  table(id, ['Real \\ previsto', ...names, 'Acerto'], d.confusion.map((row, i) => [names[i], ...row.map(String), pct(row[i] / row.reduce((a, b) => a + b, 0), 0)]));
}

function detectability(svg, sc, snr) {
  const c = sc.curves;
  chart(svg, [
    { x: snr, y: c.OR.raw, color: GREY, label: 'sem pré-processamento' }, { x: snr, y: c.OR.cpw, color: BLUE, label: 'pré-branqueamento' }, { x: snr, y: c.OR.sk, color: GREEN, label: 'banda da curtose' },
    { x: snr, y: c.IR.raw, color: GREY, dash: '5 3' }, { x: snr, y: c.IR.cpw, color: BLUE, dash: '5 3' }, { x: snr, y: c.IR.sk, color: GREEN, dash: '5 3' },
  ], { width: 460, height: 280, yDomain: [0, 1], xLabel: 'SNR do impacto (dB)', yLabel: 'probabilidade de detecção', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 1) });
}

export async function initNVH() {
  const d = await data(), dg = d.diagnosis.cpw;
  set('nv', 'ir', dg.records_diagnosed.IR);
  set('nv', 'or', dg.records_diagnosed.OR);
  set('nv', 'b', dg.records_diagnosed.B);
  set('nv', 'fa', pct(1 - dg.confusion[0][0] / dg.confusion[0].reduce((a, b) => a + b, 0), 1));
  const o = d.bearing.orders;
  $('nv-kpi-note').textContent = `${d.source.records} registros reais (12 kHz, ${d.bearing.name}: ${d.bearing.n_balls} esferas de ${fmt(d.bearing.ball_d_mm, 2)} mm em diâmetro primitivo de ${fmt(d.bearing.pitch_d_mm, 2)} mm). Frequências de defeito em múltiplos da rotação: BPFO ${fmt(o.BPFO, 4)}, BPFI ${fmt(o.BPFI, 4)}, 2·BSF ${fmt(o['2BSF'], 4)}, gaiola ${fmt(o.FTF, 4)}. Registros diagnosticados por maioria das janelas de 1 s; limiar fixado só com dados saudáveis.`;
  const ex = d.examples;
  [['N', 'nv-ses-n', GREY], ['IR007', 'nv-ses-ir', RED], ['B007', 'nv-ses-b', AMBER], ['OR007', 'nv-ses-or', BLUE]].forEach(([k, id, c]) => sesPanel($(id), ex[k], c));
  [['N', 'nv-w-n', GREY], ['OR007', 'nv-w-or', BLUE]].forEach(([k, id, c]) => wavePanel($(id), ex[k], c));
  kurtogram($('nv-kurt'), ex.OR007.kurtogram);
  recordGrid($('nv-grid'), dg.records);
  confusion('nv-conf-cpw', dg); confusion('nv-conf-sk', d.diagnosis.sk);
  $('nv-conf-note').textContent = `Acurácia balanceada por janela: ${pct(dg.balanced_accuracy, 1)} com pré-branqueamento, ${pct(d.diagnosis.sk.balanced_accuracy, 1)} com a banda da curtose espectral. Limiar τ = ${fmt(dg.tau_db, 2)} dB.`;
  const det = d.detectability;
  detectability($('nv-det-white'), det.scenarios['ruido branco'], det.snr_db);
  detectability($('nv-det-mesh'), det.scenarios['com engrenamento'], det.snr_db);
  const sc = d.sampling_check;
  $('nv-fs').textContent = `Verificação da taxa de amostragem do registro saudável 97: lido a 12 kHz, a linha de 1× rotação (29,9 Hz) fica ${fmt(sc['12000'].shaft_1x_db, 1)} dB acima do fundo local; lido a 48 kHz, a mesma linha fica ${fmt(sc['48000'].shaft_1x_db, 1)} dB. O registro é de 12 kHz, como os de falha.`;
  $('nv-status').textContent = '';
}

// ---------------------------------------------------------------- #104
function bars(svg, groups) {
  clear(svg);
  const W = 760, rh = 22, H = 30 + groups.reduce((a, g) => a + 22 + g.bars.length * rh + 14, 0) + 30;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const l = 230, r = W - 60, x = v => l + v * (r - l);
  for (let v = 0; v <= 1.0001; v += 0.25) {
    el('line', { x1: x(v), x2: x(v), y1: 20, y2: H - 30, stroke: RULE }, svg);
    text(svg, x(v), H - 12, pct(v, 0), { 'text-anchor': 'middle', 'font-size': 10.5, fill: SLATE });
  }
  let y = 26;
  groups.forEach(g => {
    text(svg, 10, y + 12, g.label, { 'font-size': 11.5, 'font-weight': 600, fill: INK });
    y += 22;
    g.bars.forEach(b => {
      el('rect', { x: l, y, width: Math.max(x(b.v) - l, 1), height: rh - 6, fill: b.color }, svg);
      text(svg, l - 8, y + 12, b.name, { 'text-anchor': 'end', 'font-size': 11, fill: SLATE });
      text(svg, x(b.v) + 6, y + 12, pct(b.v, 1), { 'font-size': 11, fill: INK });
      y += rh;
    });
    y += 14;
  });
}

export async function initAnomaly() {
  const d = await data(), m = d.monitoring;
  const P = m.detection.phys, S = m.detection.spec, C = m.classification;
  set('an', 'auc', fmt(Math.min(...Object.values(P.auc).map(a => a.auc)), 2));
  set('an', 'fa0', pct(P.false_alarm_by_load['0'], 0));
  set('an', 'leak', `${pct(C.spec.windows, 0)} → ${pct(C.spec.size, 0)}`);
  set('an', 'phys', pct(C.phys.size, 0));
  $('an-kpi-note').textContent = `${m.windows} janelas de 1 s de ${d.source.records} registros reais. Detector treinado só com o rolamento saudável em três cargas e testado na quarta; classificador com 4 classes avaliado em três protocolos.`;
  chart($('an-roc'), [
    { x: P.roc.map(p => p[0]), y: P.roc.map(p => p[1]), color: BLUE, label: 'indicadores físicos' },
    { x: S.roc.map(p => p[0]), y: S.roc.map(p => p[1]), color: AMBER, dash: '5 3', label: 'espectro em 32 bandas' },
    { x: [0, 1], y: [0, 1], color: GREY, dash: '2 3', width: 1 },
  ], { width: 460, height: 300, xDomain: [0, 1], yDomain: [0, 1], xLabel: 'taxa de falso alarme', yLabel: 'taxa de detecção', xFmt: v => fmt(v, 1), yFmt: v => fmt(v, 1) });
  const ci = a => `${fmt(a.auc, 3)} <small>[${fmt(a.ci95[0], 3)}; ${fmt(a.ci95[1], 3)}]</small>`;
  table('an-det', ['Atributos', 'AUC pista interna', 'AUC esfera', 'AUC pista externa', 'Falso alarme 0 / 1 / 2 / 3 hp', 'Detecção no limiar de 99 %'],
    [['Indicadores físicos (8)', P], ['Espectro em 32 bandas', S]].map(([n, x]) => [n, ci(x.auc.IR), ci(x.auc.B), ci(x.auc.OR),
      [0, 1, 2, 3].map(L => pct(x.false_alarm_by_load[String(L)], 0)).join(' / '), ['IR', 'B', 'OR'].map(c => pct(x.detection_rate[c], 0)).join(' / ')]));
  const h = m.healthy_by_load;
  $('an-healthy').textContent = `O rolamento saudável a 0 hp vibra mais que nas outras cargas (RMS ${fmt(h['0'].rms_g, 3)} g contra ${fmt(Math.min(h['1'].rms_g, h['2'].rms_g, h['3'].rms_g), 3)}–${fmt(Math.max(h['1'].rms_g, h['2'].rms_g, h['3'].rms_g), 3)} g). Um detector treinado nas cargas 1 a 3 marca todas as janelas saudáveis de 0 hp como anomalia. Com atributos espectrais, isso acontece em todas as cargas. A AUC continua perto de 1 porque as falhas pontuam ainda mais alto: ela mede a ordem dos escores, não se o limiar serve.`;
  const rule = d.diagnosis.cpw.balanced_accuracy;
  bars($('an-bars'), [
    { label: 'Janelas sorteadas (70/30)', bars: [{ name: 'espectro em 32 bandas', v: C.spec.windows, color: AMBER }, { name: 'indicadores físicos', v: C.phys.windows, color: BLUE }] },
    { label: 'Carga nova (deixa uma carga de fora)', bars: [{ name: 'espectro em 32 bandas', v: C.spec.load, color: AMBER }, { name: 'indicadores físicos', v: C.phys.load, color: BLUE }] },
    { label: 'Rolamento novo (deixa um tamanho de falha de fora)', bars: [{ name: 'espectro em 32 bandas', v: C.spec.size, color: AMBER }, { name: 'indicadores físicos', v: C.phys.size, color: BLUE }] },
    { label: 'Regra física, sem treino', bars: [{ name: 'envelope + limiar saudável', v: rule, color: GREEN }] },
  ]);
  $('an-status').textContent = '';
}

// ---------------------------------------------------------------- #052
export async function initSignatures() {
  const d = await data(), g = d.signatures;
  set('sg', 'ord', pct(g.order.load.balanced, 0));
  set('sg', 'hz', pct(g.hz.load.balanced, 0));
  set('sg', 'size', pct(g.order.size.balanced, 0));
  set('sg', 'ir', pct(g.order.size.per_class.IR, 0));
  const o = d.bearing.orders;
  chart($('sg-cent'), ['N', 'IR', 'B', 'OR'].map(c => ({ x: g.orders, y: g.centroids[c], color: COL[c], width: c === 'N' ? 1.2 : 1.5, label: CLS[c] })),
    { height: 300, xDomain: [0.5, 16], xLabel: 'ordem (múltiplos da rotação do eixo)', yLabel: 'assinatura normalizada (×100)', xFmt: v => fmt(v, 0), yFmt: v => fmt(v, 0),
      vlines: [{ x: o.BPFO, color: BLUE, label: 'BPFO', dy: 4 }, { x: o.BPFI, color: RED, label: 'BPFI', dy: 30 }, { x: o['2BSF'], color: AMBER, label: '2·BSF', dy: 17 },
        { x: 2 * o.BPFO, color: BLUE }, { x: 2 * o.BPFI, color: RED }, { x: 3 * o.BPFO, color: BLUE }, { x: 3 * o.BPFI, color: RED }] });
  const row = (n, r) => [n, ...['N', 'IR', 'B', 'OR'].map(c => pct(r.per_class[c], 0)), `<strong>${pct(r.balanced, 1)}</strong>`];
  table('sg-tab', ['Biblioteca e eixo', 'Normal', 'Pista interna', 'Esfera', 'Pista externa', 'Média balanceada'], [
    row('0 hp → 1–3 hp, ordens', g.order.load), row('0 hp → 1–3 hp, Hz', g.hz.load),
    row('Outros tamanhos → tamanho novo, ordens', g.order.size), row('Outros tamanhos → tamanho novo, Hz', g.hz.size)]);
  $('sg-status').textContent = '';
}
