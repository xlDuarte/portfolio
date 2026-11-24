"""Read the public OpenF1 extract of the 2024 Bahrain GP stored in the site and turn it into
(1) a racing line built from every position sample in the replay window and
(2) per-lap speed traces against distance for the drivers in that window.

OpenF1 positions are in decimetres in a circuit-fixed frame; car_data speed is in km/h at roughly
3.7 Hz. Times are ISO 8601 with offset.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

from .track import Track, build_track, fourier_smooth, project

DATA = Path(__file__).resolve().parents[1] / "site" / "motorsport" / "data" / "bahrain-2024-race.json"
UNIT = 0.1          # decimetre → metre


def _t(iso: str) -> float:
    return datetime.fromisoformat(iso).timestamp()


@dataclass
class LapTrace:
    driver: int
    acronym: str
    team: str
    lap: int
    lap_time: float             # official lap duration (s)
    s: np.ndarray               # distance from the timing line (m), on the fitted track
    v: np.ndarray               # measured speed (m/s)
    t: np.ndarray               # time since lap start (s)
    complete: bool


def load(path: Path = DATA) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def racing_line(data: dict, ref_driver: int = 1, ref_lap: int = 3, k: int = 160, ds: float = 2.0):
    """Fit the line to all position samples of the window, parametrised by a reference lap.

    Returns (track, origin_s) where origin_s locates the timing line on the reference arc length.
    """
    win = data["location"]
    lap = next(l for l in data["laps"] if l["driver_number"] == ref_driver and l["lap_number"] == ref_lap)
    t0, t1 = _t(lap["date_start"]), _t(lap["date_start"]) + lap["lap_duration"]
    ref = [p for p in win[str(ref_driver)] if t0 <= _t(p["date"]) <= t1]
    rx = np.array([p["x"] for p in ref]) * UNIT
    ry = np.array([p["y"] for p in ref]) * UNIT
    # first pass: polyline arc length of the reference lap, closed
    seg = np.hypot(np.diff(np.r_[rx, rx[0]]), np.diff(np.r_[ry, ry[0]]))
    s0 = np.concatenate([[0.0], np.cumsum(seg)[:-1]])
    l0 = float(seg.sum())
    fx0, fy0 = fourier_smooth(s0, rx, l0, 60), fourier_smooth(s0, ry, l0, 60)
    dense = np.linspace(0, l0, 8000, endpoint=False)
    lx, ly = fx0(dense), fy0(dense)
    # every sample of every driver in the window, projected on the coarse line
    pts, zs = [], []
    for drv in win.values():
        for p in drv:
            pts.append((p["x"] * UNIT, p["y"] * UNIT))
            zs.append(p["z"] * UNIT)
    pts = np.array(pts)
    s_ref, lateral = project(pts, lx, ly, dense)
    keep = np.abs(lateral) < 12.0          # drop pit-lane or off-line samples
    track = build_track(s_ref[keep] % l0, pts[keep, 0], pts[keep, 1], np.array(zs)[keep], l0, k=k, ds=ds)
    # timing line = reference position at lap start (interpolated in time)
    times = np.array([_t(p["date"]) for p in win[str(ref_driver)]])
    xs = np.array([p["x"] for p in win[str(ref_driver)]]) * UNIT
    ys = np.array([p["y"] for p in win[str(ref_driver)]]) * UNIT
    origin_xy = np.array([[np.interp(t0, times, xs), np.interp(t0, times, ys)]])
    origin, _ = project(origin_xy, track.x, track.y, track.s)
    return rotate(track, float(origin[0])), {"samples": int(keep.sum()), "dropped": int((~keep).sum())}


def rotate(track: Track, origin: float) -> Track:
    """Shift the arc-length origin to the timing line."""
    n = len(track.s)
    shift = int(round(origin / (track.length / n))) % n
    roll = lambda a: np.roll(a, -shift)
    return Track(track.s.copy(), roll(track.x), roll(track.y), roll(track.z), roll(track.kappa), roll(track.grade),
                 track.length, track.fits)


def lap_traces(data: dict, track: Track) -> list[LapTrace]:
    """Speed against distance for every lap that overlaps the replay window."""
    drivers = {d["driver_number"]: d for d in data["drivers"]}
    out = []
    for key, loc in data["location"].items():
        drv = int(key)
        lt = np.array([_t(p["date"]) for p in loc])
        pxy = np.array([[p["x"] * UNIT, p["y"] * UNIT] for p in loc])
        s_raw, _ = project(pxy, track.x, track.y, track.s)
        s_unw = np.unwrap(s_raw * 2 * np.pi / track.length) * track.length / (2 * np.pi)
        tel = data["telemetry"][key]
        tt = np.array([_t(p["date"]) for p in tel])
        vv = np.array([p["speed"] for p in tel], float) / 3.6
        for lap in (l for l in data["laps"] if l["driver_number"] == drv and l["date_start"] and l["lap_duration"]):
            t0 = _t(lap["date_start"])
            t1 = t0 + lap["lap_duration"]
            if t1 < lt[0] or t0 > lt[-1]:
                continue
            m = (tt >= max(t0, lt[0])) & (tt <= min(t1, lt[-1]))
            if m.sum() < 20:
                continue
            s_at = np.interp(tt[m], lt, s_unw)
            if t0 >= lt[0]:
                s_start = np.interp(t0, lt, s_unw)
            else:                                   # lap began before the window: the line is at s = 0 mod L
                first = s_at[0] % track.length
                if first > track.length - 100.0:    # projection noise just behind the line
                    first -= track.length
                s_start = s_at[0] - first
            complete = t0 >= lt[0] and t1 <= lt[-1]
            out.append(LapTrace(drv, drivers[drv]["name_acronym"], drivers[drv]["team_name"], lap["lap_number"],
                                float(lap["lap_duration"]), s_at - s_start, vv[m], tt[m] - t0, complete))
    return out
