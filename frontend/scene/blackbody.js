// Colour of an incandescent body from first principles.
// Planck's law weighted by the CIE 1931 colour-matching functions (multi-lobe Gaussian fit of
// Wyman, Sloan & Shirley, JCGT 2013), converted XYZ -> linear sRGB (D65).
// Pure module: no three.js, safe to unit-test in Node.

const H = 6.62607015e-34;   // Planck constant, J s
const C = 2.99792458e8;     // speed of light, m/s
const KB = 1.380649e-23;    // Boltzmann constant, J/K

const lobe = (l, mu, s1, s2) => {
  const t = (l - mu) / (l < mu ? s1 : s2);
  return Math.exp(-0.5 * t * t);
};
export const cieX = (l) => 1.056 * lobe(l, 599.8, 37.9, 31.0) + 0.362 * lobe(l, 442.0, 16.0, 26.7) - 0.065 * lobe(l, 501.1, 20.4, 26.2);
export const cieY = (l) => 0.821 * lobe(l, 568.8, 46.9, 40.5) + 0.286 * lobe(l, 530.9, 16.3, 31.1);
export const cieZ = (l) => 1.217 * lobe(l, 437.0, 11.8, 36.0) + 0.681 * lobe(l, 459.0, 26.0, 13.8);

/** Spectral radiance B(lambda, T) in W·sr⁻¹·m⁻³ (lambda in nm). */
export function planck(lambdaNm, tempK) {
  const l = lambdaNm * 1e-9;
  return (2 * H * C * C) / (l ** 5 * (Math.exp((H * C) / (l * KB * tempK)) - 1));
}

/** Chromaticity of a black body as linear sRGB, normalised so the largest channel is 1. */
export function blackbodyRGB(tempK) {
  let X = 0, Y = 0, Z = 0;
  for (let l = 380; l <= 780; l += 5) {
    const b = planck(l, tempK);
    X += b * cieX(l); Y += b * cieY(l); Z += b * cieZ(l);
  }
  let r = 3.2406 * X - 1.5372 * Y - 0.4986 * Z;
  let g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z;
  let bl = 0.0557 * X - 0.2040 * Y + 1.0570 * Z;
  r = Math.max(r, 0); g = Math.max(g, 0); bl = Math.max(bl, 0);
  const m = Math.max(r, g, bl) || 1;
  return [r / m, g / m, bl / m];
}

/**
 * Lookup table from 500 K to 4000 K in 25 K steps; ``sample(T)`` interpolates.
 * Radiance relative to ``refK`` follows Stefan–Boltzmann (T⁴), which drives HDR intensity.
 */
export function createBlackbodyLUT(minK = 500, maxK = 4000, stepK = 25) {
  const n = Math.round((maxK - minK) / stepK) + 1;
  const table = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) table.set(blackbodyRGB(minK + i * stepK), i * 3);
  return {
    sample(tempK, out = [0, 0, 0]) {
      const f = Math.min(Math.max((tempK - minK) / stepK, 0), n - 1.0001);
      const i = Math.floor(f), w = f - i;
      for (let k = 0; k < 3; k++) out[k] = table[i * 3 + k] * (1 - w) + table[(i + 1) * 3 + k] * w;
      return out;
    },
    radiance: (tempK, refK = 1500) => (tempK / refK) ** 4,
  };
}
