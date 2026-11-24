// Palette mirrored from docs/ART-DIRECTION.md. Data colours are never used for text.
export const C = {
  ind: 0x1d4e9e, auto: 0xb8122b, graphite: 0x1c2128, slate: 0x59616b,
  wash: 0xf4f6f8, indWash: 0xe9f0fa, autoWash: 0xf8eef0,
  steel: 0xcfd5dc, steelDark: 0x9aa3ad, concrete: 0xeceff2, aisle: 0xd9dee4,
  asphalt: 0x2f343b, resin: 0xc9cfd6, run: 0x1b7a48, stop: 0xc58a00,
  part: 0xf4f6f8, reject: 0xb8122b, slow: [0.93, 0.94, 0.95], fast: [1.0, 0.19, 0.28],
};

/** Deterministic PRNG (mulberry32) so the synthetic line behaves the same on every visit. */
export function mulberry32(seed) {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
