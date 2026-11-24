// Small SVG chart helpers for the lap simulator. No dependencies; every chart is plain SVG with
// text labels so it prints, scales and is readable by assistive technology through its caption.

export const NS = 'http://www.w3.org/2000/svg';
export const REGIME_COLORS = ['#1d4e9e', '#1b7a48', '#a85d00', '#b8122b'];   // curva, potência, aderência, frenagem
const INK = '#1c2128', SLATE = '#59616b', RULE = '#e3e6ea', RULE2 = '#c9ced5';

export const fmt = (x, d = 1) => Number(x).toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });

export function el(name, attrs = {}, parent) {
  const e = document.createElementNS(NS, name);
  for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) e.setAttribute(k, v);
  if (parent) parent.append(e);
  return e;
}

// "C_L·A" → C with subscript L; "λ_μy" → λ with subscript μy. Subscript runs until a space, '·', '(' or end.
const SUB = /_([^\s·()]+)/g;

export function text(parent, x, y, str, attrs = {}) {
  const t = el('text', { x, y, ...attrs }, parent);
  let last = 0;
  String(str).replace(SUB, (m, sub, i) => {
    if (i > last) t.append(document.createTextNode(String(str).slice(last, i)));
    const ts = el('tspan', { 'baseline-shift': 'sub', 'font-size': '0.78em' }, t);
    ts.textContent = sub;
    last = i + m.length;
    return m;
  });
  if (last < String(str).length) t.append(document.createTextNode(String(str).slice(last)));
  return t;
}

export function richHTML(str) {
  const esc = String(str).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  return esc.replace(SUB, (m, sub) => `<sub>${sub}</sub>`);
}

export function scale(d0, d1, r0, r1) {
  const k = (r1 - r0) / (d1 - d0 || 1);
  const f = v => r0 + (v - d0) * k;
  f.invert = p => d0 + (p - r0) / k;
  return f;
}

export function niceTicks(lo, hi, n = 5) {
  const span = hi - lo, raw = span / n, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map(m => m * mag).find(s => s >= raw) || raw;
  const out = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
  return out;
}

export function axes(svg, { x, y, xTicks, yTicks, xLabel, yLabel, box, xFmt = v => fmt(v, 0), yFmt = v => fmt(v, 0) }) {
  const g = el('g', { class: 'axes', 'font-size': 11, fill: SLATE }, svg);
  yTicks.forEach(v => {
    el('line', { x1: box.l, x2: box.r, y1: y(v), y2: y(v), stroke: RULE }, g);
    text(g, box.l - 6, y(v) + 4, yFmt(v), { 'text-anchor': 'end' });
  });
  xTicks.forEach(v => {
    el('line', { x1: x(v), x2: x(v), y1: box.b, y2: box.b + 4, stroke: RULE2 }, g);
    text(g, x(v), box.b + 16, xFmt(v), { 'text-anchor': 'middle' });
  });
  el('line', { x1: box.l, x2: box.r, y1: box.b, y2: box.b, stroke: RULE2 }, g);
  if (xLabel) text(g, (box.l + box.r) / 2, box.b + 32, xLabel, { 'text-anchor': 'middle', fill: INK });
  if (yLabel) text(g, box.l, box.t - 8, yLabel, { 'text-anchor': 'start', fill: INK });
  return g;
}

export function path(points, x, y) {
  let d = '';
  points.forEach(([a, b], i) => { d += (i ? 'L' : 'M') + x(a).toFixed(1) + ' ' + y(b).toFixed(1); });
  return d;
}

export function clear(svg) { while (svg.firstChild) svg.firstChild.remove(); }

// Horizontal bar chart centred at zero (tornado).
export function tornado(svg, items, { unit = 's', width = 420, height = 320 } = {}) {
  clear(svg);
  const box = { l: 170, r: width - 20, t: 10, b: height - 44 };
  const m = Math.max(...items.map(i => Math.abs(i.value))) * 1.1 || 1;
  const x = scale(-m, m, box.l, box.r);
  const row = (box.b - box.t) / items.length;
  axes(svg, { x, y: v => v, xTicks: niceTicks(-m, m, 4), yTicks: [], box, xLabel: `${unit} por +1 %`, xFmt: v => fmt(v, 2) });
  el('line', { x1: x(0), x2: x(0), y1: box.t, y2: box.b, stroke: INK }, svg);
  items.forEach((it, i) => {
    const y0 = box.t + i * row + row * 0.2, h = row * 0.6;
    el('rect', { x: Math.min(x(0), x(it.value)), y: y0, width: Math.abs(x(it.value) - x(0)), height: h,
      fill: it.value < 0 ? '#1b7a48' : '#b8122b', rx: 2 }, svg);
    text(svg, box.l - 8, y0 + h / 2 + 4, it.label, { 'text-anchor': 'end', 'font-size': 11, fill: INK });
    text(svg, it.value < 0 ? x(0) + 4 : x(it.value) + 4, y0 + h / 2 + 4, fmt(it.value, 3),
      { 'text-anchor': 'start', 'font-size': 10.5, fill: SLATE });
  });
}

// Correlation heat map with diverging colour (blue = −1, white = 0, red = +1).
export function heat(svg, labels, matrix) {
  clear(svg);
  const n = labels.length, box = { l: 70, t: 20, size: 220 };
  const c = box.size / n;
  const col = v => {
    const a = Math.min(Math.abs(v), 1);
    const [r, g, b] = v >= 0 ? [184, 18, 43] : [29, 78, 158];
    const mix = (u, w) => Math.round(255 + (u - 255) * w);
    return `rgb(${mix(r, a)},${mix(g, a)},${mix(b, a)})`;
  };
  matrix.forEach((row, i) => row.forEach((v, j) => {
    el('rect', { x: box.l + j * c, y: box.t + i * c, width: c - 1, height: c - 1, fill: col(v) }, svg);
    text(svg, box.l + j * c + c / 2, box.t + i * c + c / 2 + 4, fmt(v, 2),
      { 'text-anchor': 'middle', 'font-size': 10.5, fill: Math.abs(v) > 0.55 ? '#fff' : INK });
  }));
  labels.forEach((l, i) => {
    text(svg, box.l - 6, box.t + i * c + c / 2 + 4, l, { 'text-anchor': 'end', 'font-size': 11, fill: INK });
    text(svg, box.l + i * c + c / 2, box.t + n * c + 16, l, { 'text-anchor': 'middle', 'font-size': 11, fill: INK });
  });
}

// Simple multi-line chart: series = [{points:[[x,y]], color, dash, width, label}]
export function lines(svg, series, { width, height, xLabel, yLabel, xDomain, yDomain, xFmt, yFmt }) {
  clear(svg);
  const box = { l: 48, r: width - 14, t: 44, b: height - 40 };
  const x = scale(xDomain[0], xDomain[1], box.l, box.r), y = scale(yDomain[0], yDomain[1], box.b, box.t);
  axes(svg, { x, y, xTicks: niceTicks(...xDomain, 6), yTicks: niceTicks(...yDomain, 5), box, xLabel, yLabel, xFmt, yFmt });
  series.forEach(s => el('path', { d: path(s.points, x, y), fill: 'none', stroke: s.color, 'stroke-width': s.width || 1.8,
    'stroke-dasharray': s.dash, 'stroke-linejoin': 'round' }, svg));
  const lg = el('g', { 'font-size': 11 }, svg);
  let lx = box.l;
  series.filter(s => s.label).forEach(s => {
    el('line', { x1: lx, x2: lx + 16, y1: 10, y2: 10, stroke: s.color, 'stroke-width': 2.4, 'stroke-dasharray': s.dash }, lg);
    const t = text(lg, lx + 20, 14, s.label, { fill: INK });
    lx += 28 + s.label.length * 6.2;
    return t;
  });
  return { x, y, box };
}
