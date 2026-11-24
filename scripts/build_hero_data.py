"""Build the compact data file and static fallback for the home hero.

Everything the hero draws comes from files already in the repository:

* Sakhir centre line, car positions, speed and gear: the OpenF1 excerpt in
  ``site/motorsport/data/bahrain-2024-race.json`` (observed data, 4-minute window,
  3 drivers).
* Production line availability, performance and quality: ``case_studies/data/oee_shifts.csv``
  (synthetic, seeded) aggregated by planned time, the same way as the OEE case study.

Outputs (deterministic, safe to rerun):
  site/assets/hero/hero-data.json   ~ compact payload for the WebGL scene
  site/assets/hero/hero-fallback.svg static picture used before/without WebGL
"""
from __future__ import annotations

import csv
import json
import math
from bisect import bisect_left
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RACE = ROOT / "site" / "motorsport" / "data" / "bahrain-2024-race.json"
OEE_CSV = ROOT / "case_studies" / "data" / "oee_shifts.csv"
OUT_DIR = ROOT / "site" / "assets" / "hero"

SAMPLE_HZ = 4            # car samples per second in the payload
TRACK_POINTS = 360       # resampled centre-line points
SMOOTH_WINDOW = 5        # moving-average window on the centre line (samples)
LAP_CLOSE_DM = 60        # distance (dm) at which the reference lap is considered closed


def _ts(s: str) -> float:
    return datetime.fromisoformat(s).timestamp()


def _resample_closed(pts: list[tuple[float, float, float]], n: int) -> list[tuple[float, float, float]]:
    """Resample a closed polyline to n points evenly spaced by arc length."""
    ring = pts + [pts[0]]
    seg = [math.dist(ring[i][:2], ring[i + 1][:2]) for i in range(len(ring) - 1)]
    total = sum(seg)
    out, acc, i = [], 0.0, 0
    for k in range(n):
        target = total * k / n
        while acc + seg[i] < target:
            acc += seg[i]
            i += 1
        t = (target - acc) / seg[i] if seg[i] else 0.0
        a, b = ring[i], ring[i + 1]
        out.append(tuple(a[j] + (b[j] - a[j]) * t for j in range(3)))
    return out


def _smooth_closed(pts: list[tuple[float, float, float]], w: int) -> list[tuple[float, float, float]]:
    n, h = len(pts), w // 2
    return [tuple(sum(pts[(i + o) % n][j] for o in range(-h, h + 1)) / (2 * h + 1) for j in range(3))
            for i in range(n)]


def track_and_cars(race: dict) -> tuple[dict, list[dict], dict]:
    window = race["replay_window"]
    t0, t1 = _ts(window["start"]), _ts(window["end"])
    drivers = {d["driver_number"]: d for d in race["drivers"]}

    # Reference lap: driver 1 from the first sample until the line closes on itself.
    ref = race["location"]["1"]
    x0, y0 = ref[0]["x"], ref[0]["y"]
    close = next(i for i in range(50, len(ref)) if math.hypot(ref[i]["x"] - x0, ref[i]["y"] - y0) < LAP_CLOSE_DM)
    lap = [(p["x"], p["y"], p["z"]) for p in ref[:close]]
    centre = _smooth_closed(_resample_closed(lap, TRACK_POINTS), SMOOTH_WINDOW)

    xs, ys = [p[0] for p in centre], [p[1] for p in centre]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    zmin = min(p[2] for p in centre)

    def norm(x, y, z):
        return [round(x - cx), round(y - cy), round(z - zmin)]

    track = {"units": "decimetre", "points": [norm(*p) for p in centre],
             "extent_dm": [round(max(xs) - min(xs)), round(max(ys) - min(ys))]}

    n = int((t1 - t0) * SAMPLE_HZ)
    cars = []
    for num in window["drivers"]:
        loc = race["location"][str(num)]
        tel = race["telemetry"][str(num)]
        lt = [_ts(p["date"]) for p in loc]
        tt = [_ts(p["date"]) for p in tel]
        laps = sorted((_ts(l["date_start"]), l["lap_number"]) for l in race["laps"]
                      if l["driver_number"] == num and l.get("date_start"))
        samples = []
        for k in range(n):
            t = t0 + k / SAMPLE_HZ
            i = min(max(bisect_left(lt, t), 1), len(lt) - 1)
            a, b = loc[i - 1], loc[i]
            f = 0.0 if lt[i] == lt[i - 1] else min(max((t - lt[i - 1]) / (lt[i] - lt[i - 1]), 0.0), 1.0)
            x = a["x"] + (b["x"] - a["x"]) * f
            y = a["y"] + (b["y"] - a["y"]) * f
            z = a["z"] + (b["z"] - a["z"]) * f
            j = min(bisect_left(tt, t), len(tt) - 1)
            s = tel[j]
            lap_no = max((ln for ts, ln in laps if ts <= t), default=None)
            samples.append(norm(x, y, z) + [s["speed"], s["n_gear"], s["throttle"], s["brake"], lap_no])
        d = drivers[num]
        cars.append({"number": num, "code": d["name_acronym"], "name": d["full_name"].title(),
                     "fields": ["x", "y", "z", "speed_kmh", "gear", "throttle_pct", "brake", "lap"],
                     "samples": samples})
    meta = {"provider": race["provider"], "origin": race["origin"],
            "session": f'{race["session"]["circuit_short_name"]} {race["session"]["date_start"][:4]}, '
                       f'{race["session"]["session_name"]}',
            "window": [window["start"], window["end"]], "sample_hz": SAMPLE_HZ,
            "race_laps": max(l["lap_number"] for l in race["laps"])}
    return track, cars, meta


def oee_lines() -> dict:
    agg: dict[str, dict[str, float]] = {}
    with OEE_CSV.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            a = agg.setdefault(r["line"], {"planned": 0.0, "down": 0.0, "ideal": 0.0, "total": 0.0, "good": 0.0})
            a["planned"] += float(r["planned_min"])
            a["down"] += float(r["downtime_min"])
            a["ideal"] += float(r["ideal_cycle_min"]) * float(r["total_units"])
            a["total"] += float(r["total_units"])
            a["good"] += float(r["good_units"])
    lines, planned, good_time = [], 0.0, 0.0
    for name in sorted(agg):
        a = agg[name]
        run = a["planned"] - a["down"]
        availability, performance, quality = run / a["planned"], a["ideal"] / run, a["good"] / a["total"]
        lines.append({"line": name, "availability": round(availability, 4), "performance": round(performance, 4),
                      "quality": round(quality, 4), "oee": round(availability * performance * quality, 4)})
        planned += a["planned"]
        good_time += availability * performance * quality * a["planned"]
    return {"origin": "synthetic", "source": "case_studies/data/oee_shifts.csv",
            "oee_weighted": round(good_time / planned, 4), "lines": lines}


def fallback_svg(track: dict, oee: dict) -> str:
    """A quiet line drawing: isometric production line on the left, Sakhir on the right."""
    w, h = 1200, 560
    pts = track["points"]
    ex, ey = track["extent_dm"]
    scale = min(420 / ex, 420 / ey)
    ox, oy = 900, 280
    path = "M" + " L".join(f"{ox + p[0] * scale:.1f},{oy - p[1] * scale:.1f}" for p in pts) + "Z"

    def iso(x, y, z=0.0):
        return 300 + (x - y) * 0.866 * 22, 300 + (x + y) * 0.5 * 22 - z * 22

    shapes = []
    for lane, dy in enumerate((-2.2, 2.2)):
        a, b = iso(-7, dy - .6), iso(7, dy - .6)
        c, d = iso(7, dy + .6), iso(-7, dy + .6)
        shapes.append(f'<path d="M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f} L{c[0]:.1f},{c[1]:.1f} '
                      f'L{d[0]:.1f},{d[1]:.1f}Z" class="belt"/>')
        for mx in (-4.5, 0, 4.5):
            top = [iso(mx - .9, dy - .9, 1.6), iso(mx + .9, dy - .9, 1.6), iso(mx + .9, dy + .9, 1.6), iso(mx - .9, dy + .9, 1.6)]
            base = [iso(mx + .9, dy - .9), iso(mx + .9, dy + .9), iso(mx - .9, dy + .9)]
            shapes.append('<path d="M' + " L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in top) + 'Z" class="mach"/>')
            for t_, b_ in zip(top[1:], base):
                shapes.append(f'<path d="M{t_[0]:.1f},{t_[1]:.1f} L{b_[0]:.1f},{b_[1]:.1f}" class="edge"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="Linha de produção isométrica e traçado do circuito de Sakhir">'
            '<style>.belt{fill:#e9edf2;stroke:#9aa3ad;stroke-width:1.2}.mach{fill:#f7f9fb;stroke:#1d4e9e;stroke-width:1.6}'
            '.edge{stroke:#1d4e9e;stroke-width:1.2}.trk{fill:none;stroke:#c9ced5;stroke-width:15;stroke-linejoin:round}'
            '.trk2{fill:none;stroke:#b8122b;stroke-width:2;stroke-linejoin:round}</style>'
            + "".join(shapes)
            + f'<path d="{path}" class="trk"/><path d="{path}" class="trk2"/></svg>\n')


def main() -> None:
    race = json.loads(RACE.read_text(encoding="utf-8"))
    track, cars, meta = track_and_cars(race)
    oee = oee_lines()
    payload = {"schema_version": 1, "f1": {**meta, "track": track, "cars": cars}, "industrial": oee,
               "notes": ["F1: observed OpenF1 data; positions between samples are interpolated for display.",
                         "Industrial: synthetic seeded data; belt stops follow availability, speed follows "
                         "performance, diverted parts follow quality."]}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "hero-data.json").write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    (OUT_DIR / "hero-fallback.svg").write_text(fallback_svg(track, oee), encoding="utf-8")
    print("hero-data.json", (OUT_DIR / "hero-data.json").stat().st_size, "bytes;",
          "OEE", oee["oee_weighted"], [(l["line"], l["oee"]) for l in oee["lines"]])


if __name__ == "__main__":
    main()
