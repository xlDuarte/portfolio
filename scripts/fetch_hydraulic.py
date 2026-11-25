"""Fetch the UCI hydraulic-rig data (ZeMA), verify it and cache what phase 4b uses.

    python scripts/fetch_hydraulic.py [--source DIR] [--fixture]

Without --source, makes a sparse, blob-filtered clone of the mirror named in
data/hydraulic/manifest.json at its pinned commit (≈ 730 MB of text). Every file must match the
SHA-256 in the manifest. Output: data/external/hydraulic/cycles.npz (git-ignored) with
10 Hz pressure PS1 and motor power EPS1, flow FS1, cycle means of the temperatures, mean and std
of all 17 channels, plateau features and the condition labels. With --fixture, also rewrites the
committed test excerpt (36 cycles, one per pump × cooler × valve condition).
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from degradation.hydraulics import CACHE, FIXTURE, SENSORS, manifest, plateau_features  # noqa: E402


def clone(m: dict, dest: Path) -> Path:
    run = lambda *a: subprocess.run(a, cwd=dest, check=True, capture_output=True, text=True)
    subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", "-q", m["mirror"] + ".git", str(dest)], check=True)
    run("git", "config", "gc.auto", "0")
    run("git", "sparse-checkout", "set", "--no-cone", *m["files"].keys())
    run("git", "checkout", "-q", m["mirror_commit"])
    return dest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path)
    ap.add_argument("--fixture", action="store_true")
    args = ap.parse_args()
    m = manifest()
    with tempfile.TemporaryDirectory() as tmp:
        src = args.source or clone(m, Path(tmp) / "mirror")
        for name, h in m["files"].items():
            got = hashlib.sha256((src / name).read_bytes()).hexdigest()
            if got != h:
                raise SystemExit(f"checksum mismatch for {name}: {got}")
        raw = {s: np.loadtxt(src / f"{s}.txt", dtype=np.float64) for s in SENSORS}
        profile = np.loadtxt(src / "profile.txt", dtype=int)
    to10 = lambda a: a.reshape(len(a), 600, -1).mean(axis=2)
    p10, e10, q10 = to10(raw["PS1"]), to10(raw["EPS1"]), raw["FS1"]
    stats = np.column_stack([np.c_[raw[s].mean(1), raw[s].std(1)] for s in SENSORS])
    out = {"PS1_10": p10.astype(np.float32), "EPS1_10": e10.astype(np.float32), "FS1": q10.astype(np.float32),
           "TS1": raw["TS1"].astype(np.float32), "TS1_mean": raw["TS1"].mean(1), "TS2_mean": raw["TS2"].mean(1),
           "TS3_mean": raw["TS3"].mean(1), "TS4_mean": raw["TS4"].mean(1), "SE_mean": raw["SE"].mean(1),
           "stats": stats, "plateau": plateau_features(p10, q10, e10), "profile": profile}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CACHE, **out)
    print(f"verified {len(m['files'])} files; wrote {CACHE.relative_to(ROOT)} ({CACHE.stat().st_size / 1e6:.1f} MB)")
    if args.fixture:
        pick = []
        for pump in (0, 1, 2):
            for cooler in (3, 20, 100):
                for valve in (100, 90, 80, 73):
                    idx = np.where((profile[:, 2] == pump) & (profile[:, 0] == cooler) & (profile[:, 1] == valve) & (profile[:, 4] == 0))[0]
                    if len(idx):
                        pick.append(idx[len(idx) // 2])
        pick = np.array(pick)
        np.savez_compressed(FIXTURE, idx=pick, PS1_10=p10[pick].astype(np.float32), EPS1_10=e10[pick].astype(np.float32),
                            FS1=q10[pick].astype(np.float32), TS1_mean=raw["TS1"].mean(1)[pick], profile=profile[pick])
        print(f"wrote {FIXTURE.relative_to(ROOT)} ({len(pick)} cycles, {FIXTURE.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
