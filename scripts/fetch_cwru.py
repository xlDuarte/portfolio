"""Fetch the 40 CWRU records used in phase 4, verify them and cache the drive-end channel.

    python scripts/fetch_cwru.py [--source DIR]

Without --source, makes a sparse, blob-filtered clone of the mirror named in
data/cwru/manifest.json at its pinned commit (≈ 135 MB of .mat files). With --source, reads the
.mat files from an existing copy laid out like the mirror. Every file must match the SHA-256 in
the manifest or the script stops. Output: data/external/cwru/<id>.npy (float64, git-ignored) and,
with --fixture, the committed test excerpt tests/fixtures/cwru_excerpt.npz.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import scipy.io as sio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bearings.data import CACHE, FIXTURE, NOMINAL_RPM, manifest  # noqa: E402

FIXTURE_IDS = (97, 105, 118, 130)
FIXTURE_N = 24_000


def clone(m: dict, dest: Path) -> Path:
    paths = [r["path"] for r in m["records"]]
    run = lambda *a: subprocess.run(a, cwd=dest, check=True, capture_output=True, text=True)
    subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", "-q", m["mirror"] + ".git", str(dest)], check=True)
    run("git", "config", "gc.auto", "0")
    run("git", "sparse-checkout", "set", "--no-cone", *paths)
    run("git", "checkout", "-q", m["mirror_commit"])
    return dest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, help="existing copy of the mirror")
    ap.add_argument("--fixture", action="store_true", help="also rewrite the committed test excerpt")
    args = ap.parse_args()
    m = manifest()
    CACHE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        src = args.source or clone(m, Path(tmp) / "mirror")
        for r in m["records"]:
            f = src / r["path"]
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            if h != r["sha256"]:
                raise SystemExit(f"checksum mismatch for {r['path']}: {h}")
            x = sio.loadmat(f)[r["de_key"]].ravel().astype(np.float64)
            np.save(CACHE / f"{r['id']}.npy", x)
        print(f"verified and cached {len(m['records'])} records in {CACHE.relative_to(ROOT)}")
    if args.fixture:
        meta, arrays = [], {}
        for r in m["records"]:
            if r["id"] in FIXTURE_IDS:
                arrays[str(r["id"])] = np.load(CACHE / f"{r['id']}.npy")[:FIXTURE_N].astype(np.float32)
                meta.append({"id": r["id"], "class": r["class"], "size_mils": r["size_mils"], "load_hp": r["load_hp"],
                             "rpm": float(r["rpm_file"] or NOMINAL_RPM[r["load_hp"]])})
        FIXTURE.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(FIXTURE, meta=json.dumps(meta), **arrays)
        print(f"wrote {FIXTURE.relative_to(ROOT)} ({FIXTURE.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
