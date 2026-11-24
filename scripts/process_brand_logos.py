"""Turn the logo images supplied by the site owner into small transparent WebP marks.

Usage: python scripts/process_brand_logos.py <source_dir> <slug>=<file> [...]

A source that already has transparency keeps its own alpha. Otherwise it is treated as
a raster on a white canvas: the white that touches the canvas border
(the background) becomes transparent; white enclosed by the mark (counters, the inside
of the Mercedes ring) stays as drawn. Anti-aliased edges are un-blended against white
("colour to alpha") so they do not leave a light halo on tinted backgrounds. The result
is trimmed, padded by 4 % and resized to a fixed height. Metadata is not copied.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

OUT = Path(__file__).resolve().parents[1] / "site" / "assets" / "brands"
HEIGHT = 128          # 40 px CSS at 3x density
WHITE_MIN = 232       # a pixel is "near white" when every channel is at least this
EDGE_BAND = 3         # px around the background where anti-aliasing is un-blended


def to_transparent(rgb: np.ndarray) -> np.ndarray:
    """Return RGBA float array in [0, 1] with the border-connected white removed."""
    near_white = (rgb >= WHITE_MIN / 255).all(axis=2)
    labels, _ = ndimage.label(near_white)
    border = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    background = np.isin(labels, border[border > 0])
    band = ndimage.binary_dilation(background, iterations=EDGE_BAND) & ~background

    alpha = np.ones(rgb.shape[:2])
    alpha[background] = 0.0
    # Colour to alpha against white: the smallest alpha that explains the pixel as
    # a blend of some colour over white.
    a_band = np.clip((1.0 - rgb[band]).max(axis=1), 0.0, 1.0)
    alpha[band] = a_band
    out = rgb.copy()
    safe = np.maximum(a_band, 1e-6)[:, None]
    out[band] = np.clip((rgb[band] - (1.0 - a_band)[:, None]) / safe, 0.0, 1.0)
    out[background] = 0.0
    return np.dstack([out, alpha])


def process(src: Path, slug: str) -> tuple[int, int]:
    im = Image.open(src)
    if im.mode in ("RGBA", "LA") and im.getchannel("A").getextrema()[0] < 255:
        # Already cut out by the supplier: keep its alpha, which carries the anti-aliasing.
        rgba = np.asarray(im.convert("RGBA"), dtype=np.float64) / 255.0
        rgba[..., :3] *= rgba[..., 3:4] > 0
    else:
        rgba = to_transparent(np.asarray(im.convert("RGB"), dtype=np.float64) / 255.0)
    ys, xs = np.nonzero(rgba[..., 3] > 0.02)
    if ys.size == 0:
        raise ValueError(f"{src}: no mark found")
    crop = rgba[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]
    h, w = crop.shape[:2]
    pad = int(round(0.04 * max(h, w)))
    canvas = np.zeros((h + 2 * pad, w + 2 * pad, 4))
    canvas[pad: pad + h, pad: pad + w] = crop
    img = Image.fromarray((canvas * 255 + 0.5).astype(np.uint8), "RGBA")
    width = max(1, round(img.width * HEIGHT / img.height))
    img = img.resize((width, HEIGHT), Image.LANCZOS)
    dest = OUT / f"{slug}.webp"
    img.save(dest, "WEBP", quality=90, method=6, exact=False)
    return img.size


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    source = Path(argv[1])
    for pair in argv[2:]:
        slug, name = pair.split("=", 1)
        size = process(source / name, slug)
        print(f"{slug}.webp {size[0]}x{size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
