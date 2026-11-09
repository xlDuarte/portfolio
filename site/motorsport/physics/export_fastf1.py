"""Export one observed FastF1 lap and a derived (not surveyed) track.
Usage: python export_fastf1.py 2024 Bahrain Q VER --output session
Install: pip install fastf1 numpy pandas
No generated fallback. A failed download exits with an error.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import fastf1

def export(args):
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "cache"
    cache.mkdir(exist_ok=True)
    fastf1.Cache.enable_cache(str(cache))
    session = fastf1.get_session(args.year, args.event, args.session)
    session.load(telemetry=True, weather=False, messages=False)
    laps = session.laps.pick_drivers(args.driver).pick_accurate()
    selected = laps.pick_fastest()
    if selected is None or pd.isna(selected["LapTime"]):
        raise ValueError("No accurate timed lap available.")
    # Car channel export preserves original sample spacing, no position merge.
    car = selected.get_car_data().add_distance()
    if car.empty or car[["Time", "Speed", "Brake"]].isna().any().any():
        raise ValueError("Missing car channels.")
    time = car["Time"].dt.total_seconds().to_numpy()
    telemetry = pd.DataFrame({
        "time_s": time - time[0], "speed_kmh": car["Speed"].to_numpy(),
        "brake": car["Brake"].astype(int).to_numpy()
    })
    if (np.diff(time) <= 0).any():
        raise ValueError("Non-increasing timestamps.")
    telemetry.to_csv(out / "telemetry.csv", index=False)
    # FastF1 position is in decimetres. Geometry is smoothed/resampled, explicitly derived.
    pos = selected.get_pos_data()
    if len(pos) < 20 or pos[["X", "Y"]].isna().any().any():
        raise ValueError("Insufficient position data for derived track.")
    if "Status" in pos and (pos["Status"] != "OnTrack").any():
        raise ValueError("Off-track/missing position flags: inspect acquisition.")
    xy = pos[["X", "Y"]].to_numpy(dtype=float) / 10
    xy = pd.DataFrame(xy).rolling(5, center=True, min_periods=1).mean().to_numpy()
    keep = np.r_[True, np.linalg.norm(np.diff(xy, axis=0), axis=1) > .1]
    xy = xy[keep]
    closure = float(np.linalg.norm(xy[-1]-xy[0]))
    if closure > 100:
        raise ValueError("Position trace is not a closed lap (gap >100 m).")
    if closure > .01:
        xy = np.vstack([xy, xy[0]])
    else:
        xy[-1] = xy[0]
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]
    if (np.diff(d) <= 0).any() or d[-1] < 500:
        raise ValueError("Degenerate track geometry.")
    count = int(np.ceil(d[-1] / 10))
    sample = np.arange(count) * d[-1] / count
    points = np.column_stack([np.interp(sample, d, xy[:, k]) for k in range(2)])
    before, after = np.roll(points, 1, axis=0), np.roll(points, -1, axis=0)
    a, b, c = points-before, after-points, after-before
    denominator = np.linalg.norm(a, axis=1)*np.linalg.norm(b, axis=1)*np.linalg.norm(c, axis=1)
    if (denominator <= 1e-8).any():
        raise ValueError("Degenerate curvature stencil.")
    curvature = 2*(a[:, 0]*b[:, 1]-a[:, 1]*b[:, 0])/denominator
    track = pd.DataFrame({"length_m": np.linalg.norm(b, axis=1), "curvature_1pm": curvature})
    track.to_csv(out / "track.csv", index=False)
    pd.DataFrame({"distance_m": sample, "x_m": points[:, 0], "y_m": points[:, 1]}).to_csv(out/"position-derived.csv", index=False)
    metadata = {
        "source": "FastF1", "fastf1_version": fastf1.__version__,
        "year": args.year, "event": args.event, "session": args.session,
        "driver": args.driver, "lap_number": int(selected["LapNumber"]),
        "observed_laptime_s": selected["LapTime"].total_seconds(),
        "geometry_origin": "derived from observed position; not surveyed",
        "smoothing": "centered five-sample rolling mean, 10 m nominal arc resampling, three-point curvature",
        "closure_gap_m_before_closing": closure,
        "notes": "Telemetry samples do not necessarily cover exact timing-line boundaries. No proprietary aero, battery or MGU-K channels available. Validate track and repeat discretization study."
    }
    (out/"provenance.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Exported telemetry.csv, track.csv, position-derived.csv, provenance.json to", out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("year", type=int)
    parser.add_argument("event")
    parser.add_argument("session")
    parser.add_argument("driver")
    parser.add_argument("--output", default="fastf1-export")
    export(parser.parse_args())
