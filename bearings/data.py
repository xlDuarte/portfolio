"""CWRU bearing records: provenance, integrity check and loading.

The raw MATLAB files are not committed (≈ 130 MB). ``scripts/fetch_cwru.py`` takes them from a
public GitHub mirror of the Case Western Reserve University Bearing Data Center at a pinned commit,
checks every file against the SHA-256 recorded in ``data/cwru/manifest.json`` and stores only the
drive-end channel as float64 ``.npy`` in ``data/external/cwru/`` (git-ignored). A 2-second excerpt
of four records is committed under ``tests/fixtures`` so the tests run without the download.

Speed: the RPM stored in the file when present, else the nominal speed of the load condition
published by CWRU (records 98 and 99 have no RPM variable).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "cwru" / "manifest.json"
CACHE = ROOT / "data" / "external" / "cwru"
FIXTURE = ROOT / "tests" / "fixtures" / "cwru_excerpt.npz"
FS = 12_000.0
NOMINAL_RPM = {0: 1797, 1: 1772, 2: 1750, 3: 1730}
CLASSES = ("N", "IR", "B", "OR")
CLASS_PT = {"N": "normal", "IR": "pista interna", "B": "esfera", "OR": "pista externa"}


@dataclass(frozen=True)
class Record:
    id: int
    cls: str
    size_mils: int
    load_hp: int
    rpm: float
    x: np.ndarray                      # drive-end acceleration, g

    @property
    def fr(self) -> float:             # shaft frequency, Hz
        return self.rpm / 60.0

    @property
    def label(self) -> str:
        return "N" if self.cls == "N" else f"{self.cls}{self.size_mils:03d}"


def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def available() -> bool:
    m = manifest()
    return all((CACHE / f"{r['id']}.npy").exists() for r in m["records"])


def load_all() -> list[Record]:
    """All 40 records from the verified cache (run scripts/fetch_cwru.py first)."""
    if not available():
        raise FileNotFoundError("CWRU cache missing: run `python scripts/fetch_cwru.py`")
    out = []
    for r in manifest()["records"]:
        rpm = r["rpm_file"] or NOMINAL_RPM[r["load_hp"]]
        out.append(Record(r["id"], r["class"], r["size_mils"], r["load_hp"], float(rpm), np.load(CACHE / f"{r['id']}.npy")))
    return sorted(out, key=lambda r: (CLASSES.index(r.cls), r.size_mils, r.load_hp))


def load_fixture() -> list[Record]:
    """Committed 2 s excerpts (24 000 samples) of records 97 (N), 105 (IR), 118 (B) and 130 (OR) at 0 hp."""
    z = np.load(FIXTURE)
    meta = json.loads(str(z["meta"]))
    return [Record(m["id"], m["class"], m["size_mils"], m["load_hp"], m["rpm"], z[str(m["id"])].astype(float)) for m in meta]


def windows(x: np.ndarray, n: int, hop: int | None = None) -> np.ndarray:
    """Non-overlapping (default) windows of n samples as a 2-D view."""
    hop = hop or n
    k = 1 + (len(x) - n) // hop
    idx = np.arange(n)[None, :] + hop * np.arange(k)[:, None]
    return x[idx]
