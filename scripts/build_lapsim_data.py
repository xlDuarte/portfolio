"""Build site/motorsport/data/lapsim-bahrain.json: track, calibrated car, validation and the
tables the lap-simulator page draws. Deterministic; takes about three minutes.

    python scripts/build_lapsim_data.py
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.signal import savgol_filter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vehicle_dynamics import Car, Envelope, G, air_density, simulate  # noqa: E402
from vehicle_dynamics import openf1  # noqa: E402
from vehicle_dynamics.calibrate import PARAMS, car_from, fit_lap, monte_carlo, predict_lap, sensitivity  # noqa: E402
from vehicle_dynamics.track import Track, minimum_curvature  # noqa: E402

OUT = ROOT / "site" / "motorsport" / "data" / "lapsim-bahrain.json"
HALF_WIDTH = 4.5          # m, hypothesis: usable corridor either side of the reference line
SITE_STEP = 4.0           # m, resolution of the track shipped to the browser


def resample(track: Track, step: float) -> Track:
    n = int(round(track.length / step))
    s = np.linspace(0, track.length, n, endpoint=False)
    f = lambda a: np.interp(s, track.s, a, period=track.length)
    return Track(s, f(track.x), f(track.y), f(track.z), f(track.kappa), f(track.grade), track.length, track.fits)


def car_dict(car: Car) -> dict:
    keys = ("mass", "wheelbase", "front_weight", "h_cg", "track_f", "track_r", "roll_share_f", "cla", "cda",
            "aero_balance", "power", "brake_balance", "crr", "rho")
    d = {k: round(float(getattr(car, k)), 6) for k in keys}
    t = car.tyre
    d["tyre"] = {k: float(getattr(t, k)) for k in t.__dataclass_fields__}
    return d


def main() -> None:
    data = openf1.load()
    w = data["weather"][0]
    rho = air_density(w["pressure"], w["air_temperature"], w["humidity"])
    base = Car(rho=rho)

    ref, line_info = openf1.racing_line(data)
    track, offset = minimum_curvature(ref, HALF_WIDTH)
    laps = openf1.lap_traces(data, track)
    full = {l.acronym: l for l in laps if l.complete}

    fits = {name: fit_lap(lap, track, base) for name, lap in full.items()}
    ver = fits["VER"]
    car = car_from(ver.theta, base)
    sim = simulate(car, track)
    env = Envelope.of(car)

    corridor = {}
    for hw in (3.0, 4.5, 6.0):
        t_hw = track if hw == HALF_WIDTH else minimum_curvature(ref, hw)[0]
        corridor[str(hw)] = {"length_m": round(t_hw.length, 1), "lap_time_s": round(simulate(car, t_hw).lap_time, 3)}
    corridor["ref"] = {"length_m": round(ref.length, 1), "lap_time_s": round(simulate(car, ref).lap_time, 3)}

    # numerical convergence of the QSS integration in the step Δs (Richardson estimate of the limit)
    conv = {str(h): round(simulate(car, resample(track, h)).lap_time, 4) for h in (8.0, 4.0, 2.0, 1.0, 0.5)}
    t1, t2 = conv["1.0"], conv["0.5"]
    conv["richardson_s"] = round((4 * t2 - t1) / 3, 4)    # second-order scheme: T ≈ T_h + c·h²

    sens = sensitivity(car, track)
    mc = monte_carlo(ver, base, track, n=200)

    # measured g-g cloud of the three complete laps
    cloud = []
    for name, lap in full.items():
        tu = np.arange(lap.t[0], lap.t[-1], 0.24)
        vu = np.interp(tu, lap.t, lap.v)
        su = np.interp(tu, lap.t, lap.s) % track.length
        ax = savgol_filter(vu, 7, 2, deriv=1, delta=0.24)
        ay = vu ** 2 * np.interp(su, track.s, track.kappa, period=track.length)
        cloud.append({"driver": name, "v_kmh": np.round(vu * 3.6, 1).tolist(), "ax_g": np.round(ax / G, 3).tolist(),
                      "ay_g": np.round(ay / G, 3).tolist()})

    # tyre curves
    t = car.tyre
    alpha = np.radians(np.linspace(0, 14, 57))
    kappa = np.linspace(0, 0.25, 51)
    loads = [2000.0, 3500.0, 5000.0, 7000.0]
    fz_grid = np.linspace(1000, 9000, 33)
    p_grid = np.linspace(1.2e5, 2.2e5, 21)
    ky = np.array([[float(t.cornering_stiffness(fz, p)) for fz in fz_grid] for p in p_grid])

    site_track = resample(track, SITE_STEP)
    site_ref = resample(ref, SITE_STEP)
    site_sim = simulate(car, site_track)

    out = {
        "schema": 1,
        "generated_by": "scripts/build_lapsim_data.py",
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "source": {"provider": "OpenF1", "session_key": data["session"]["session_key"],
                   "event": "GP do Bahrein 2024, corrida", "window": data["replay_window"],
                   "weather": {k: w[k] for k in ("air_temperature", "track_temperature", "pressure", "humidity")}},
        "assumptions": {
            "half_width_m": HALF_WIDTH,
            "mass_kg": base.mass,
            "air_density_kg_m3": round(rho, 4),
            "note": "Parâmetros não calibrados são hipóteses de ordem de grandeza; ver vehicle_dynamics/vehicle.py e tyre.py.",
        },
        "line": {"samples": line_info["samples"], "dropped": line_info["dropped"],
                 "lateral_rms_between_drivers_m": None},
        "track": {**site_track.to_dict(), "ref_x": np.round(site_ref.x, 2).tolist(), "ref_y": np.round(site_ref.y, 2).tolist(),
                  "ref_offset_m": np.round(np.interp(site_ref.s, ref.s, offset, period=ref.length), 2).tolist()},
        "corridor_sensitivity": corridor,
        "convergence_ds_m": conv,
        "car_base": car_dict(base),
        "car": car_dict(car),
        "calibration": {"params": list(PARAMS), "VER": ver.to_dict(),
                        "per_driver": {k: f.to_dict() for k, f in fits.items()}},
        "validation": [predict_lap(ver.theta, base, track, l) | {"complete": l.complete} for l in laps],
        "sim": {"lap_time_s": round(sim.lap_time, 3), "site_lap_time_s": round(site_sim.lap_time, 3),
                **{k: v for k, v in site_sim.to_dict().items() if k != "lap_time_s"}},
        "measured": {name: {"lap": l.lap, "lap_time_s": l.lap_time, "s": np.round(l.s, 1).tolist(),
                            "v_kmh": np.round(l.v * 3.6, 1).tolist()} for name, l in full.items()},
        "ggv": {"v_kmh": np.round(env.v * 3.6, 2).tolist(), "ay_max_g": np.round(env.ay_max / G, 4).tolist(),
                "frac": np.round(env.frac, 4).tolist(), "ax_max_g": np.round(env.ax_max / G, 4).tolist(),
                "ax_min_g": np.round(env.ax_min / G, 4).tolist()},
        "gg_measured": cloud,
        "sensitivity": {"base_lap_s": round(sens["base_lap_s"], 3),
                        "items": {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()}
                                  for k, v in sens["items"].items()}},
        "monte_carlo": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in mc.items()},
        "tyre": {"alpha_deg": np.round(np.degrees(alpha), 3).tolist(), "kappa": np.round(kappa, 4).tolist(), "loads_n": loads,
                 "fy_n": [np.round(t.fy(alpha, fz), 1).tolist() for fz in loads],
                 "fx_n": [np.round(t.fx(kappa, fz), 1).tolist() for fz in loads],
                 "mu_y": np.round(t.mu_y(fz_grid), 4).tolist(), "fz_grid_n": fz_grid.tolist(),
                 "p_grid_bar": np.round(p_grid / 1e5, 3).tolist(), "ky_n_per_deg": np.round(ky * np.pi / 180, 1).tolist(),
                 "peak_alpha_deg": [round(np.degrees(t.peak_slip_angle(fz)), 2) for fz in loads]},
    }
    # consistency of the map line between drivers (evidence that OpenF1 positions are map-projected)
    from vehicle_dynamics.track import project
    pts = np.array([[p["x"] * 0.1, p["y"] * 0.1] for drv in data["location"].values() for p in drv])
    _, lat = project(pts, ref.x, ref.y, ref.s)
    out["line"]["lateral_rms_between_drivers_m"] = round(float(np.sqrt(np.mean(lat ** 2))), 3)

    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), default=lambda o: o.item()), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")
    print(json.dumps({"VER": ver.to_dict(), "mc": out["monte_carlo"], "corridor": corridor}, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()
