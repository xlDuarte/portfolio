// Live read-outs drawn next to the scenes (decorative mirror of the captions, aria-hidden).

const NUM = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1, minimumFractionDigits: 1 });

/** Friction-circle ("g-g") diagram: lateral vs longitudinal acceleration of the leader. */
export class GGDiagram {
  constructor(canvas, maxG = 5) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.maxG = maxG;
    this.resize();
  }

  resize() {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    const s = this.canvas.clientWidth || 132;
    this.canvas.width = this.canvas.height = Math.round(s * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.size = s;
  }

  draw(history) {
    const g = this.ctx, s = this.size, c = s / 2, r = c - 6, k = r / this.maxG;
    g.clearRect(0, 0, s, s);
    g.strokeStyle = "rgba(28,33,40,.14)";
    g.lineWidth = 1;
    for (let ring = 1; ring <= this.maxG; ring++) {
      g.beginPath(); g.arc(c, c, ring * k, 0, Math.PI * 2); g.stroke();
    }
    g.beginPath(); g.moveTo(c - r, c); g.lineTo(c + r, c); g.moveTo(c, c - r); g.lineTo(c, c + r); g.stroke();
    if (!history.length) return;
    // Screen: +x = turning left shown to the left (driver's view), +y = braking shown down.
    const pt = ([lat, lon]) => [c - lat * k, c - lon * k];
    for (let i = 1; i < history.length; i++) {
      const a = pt(history[i - 1]), b = pt(history[i]);
      g.strokeStyle = `rgba(184,18,43,${(i / history.length) * 0.75})`;
      g.lineWidth = 1.6;
      g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke();
    }
    const [x, y] = pt(history[history.length - 1]);
    g.fillStyle = "#b8122b";
    g.beginPath(); g.arc(x, y, 3.6, 0, Math.PI * 2); g.fill();
  }
}

export function formatG(v) {
  return `${NUM.format(Math.abs(v))} g`;
}
