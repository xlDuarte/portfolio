// three.js view of a SparkField: a glowing head (point sprite) and a motion-blur streak per
// particle. Colour = black-body chromaticity at the particle's temperature; intensity follows
// Stefan–Boltzmann (T⁴) so hot sparks exceed 1.0 in the HDR buffer and feed the bloom pass.
import {
  AdditiveBlending, BufferAttribute, BufferGeometry, CanvasTexture, LineBasicMaterial,
  LineSegments, Points, PointsMaterial,
} from "three";
import { createBlackbodyLUT } from "./blackbody.js";

const LUT = createBlackbodyLUT();

function spriteTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 32;
  const g = c.getContext("2d");
  const grd = g.createRadialGradient(16, 16, 0, 16, 16, 16);
  grd.addColorStop(0, "rgba(255,255,255,1)");
  grd.addColorStop(0.35, "rgba(255,255,255,0.55)");
  grd.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 32, 32);
  return new CanvasTexture(c);
}

export class SparkView {
  /**
   * @param field          SparkField (physics in metres)
   * @param unitsPerMeter  scene units per metre
   * @param opts           { intensity, refK, shutter (s), size (px) }
   */
  constructor(field, unitsPerMeter, opts = {}) {
    this.field = field;
    this.upm = unitsPerMeter;
    this.intensity = opts.intensity ?? 2.2;
    this.refK = opts.refK ?? 1500;
    this.shutter = opts.shutter ?? 0.018;
    const n = field.capacity;
    this.headPos = new Float32Array(n * 3);
    this.headCol = new Float32Array(n * 3);
    this.linePos = new Float32Array(n * 6);
    this.lineCol = new Float32Array(n * 6);
    const hg = new BufferGeometry();
    hg.setAttribute("position", new BufferAttribute(this.headPos, 3));
    hg.setAttribute("color", new BufferAttribute(this.headCol, 3));
    const lg = new BufferGeometry();
    lg.setAttribute("position", new BufferAttribute(this.linePos, 3));
    lg.setAttribute("color", new BufferAttribute(this.lineCol, 3));
    const common = { vertexColors: true, blending: AdditiveBlending, transparent: true, depthWrite: false, toneMapped: true };
    this.heads = new Points(hg, new PointsMaterial({ ...common, size: opts.size ?? 3.2, sizeAttenuation: false, map: spriteTexture() }));
    this.lines = new LineSegments(lg, new LineBasicMaterial(common));
    this.heads.frustumCulled = this.lines.frustumCulled = false;
    this.heads.renderOrder = this.lines.renderOrder = 10;
    this._c = [0, 0, 0];
  }

  addTo(scene) { scene.add(this.heads, this.lines); }

  update() {
    const f = this.field, u = this.upm, n = f.count;
    for (let i = 0; i < n; i++) {
      const x = f.px[i] * u, y = f.py[i] * u, z = f.pz[i] * u;
      const c = LUT.sample(f.temp[i], this._c);
      const k = this.intensity * LUT.radiance(f.temp[i], this.refK);
      this.headPos[i * 3] = x; this.headPos[i * 3 + 1] = y; this.headPos[i * 3 + 2] = z;
      this.headCol[i * 3] = c[0] * k; this.headCol[i * 3 + 1] = c[1] * k; this.headCol[i * 3 + 2] = c[2] * k;
      const s = this.shutter * u;
      this.linePos.set([x, y, z, x - f.vx[i] * s, y - f.vy[i] * s, z - f.vz[i] * s], i * 6);
      this.lineCol.set([c[0] * k, c[1] * k, c[2] * k, c[0] * k * 0.15, c[1] * k * 0.15, c[2] * k * 0.15], i * 6);
    }
    const hg = this.heads.geometry, lg = this.lines.geometry;
    hg.setDrawRange(0, n); lg.setDrawRange(0, n * 2);
    hg.attributes.position.needsUpdate = hg.attributes.color.needsUpdate = true;
    lg.attributes.position.needsUpdate = lg.attributes.color.needsUpdate = true;
  }
}

export { LUT as BLACKBODY };
