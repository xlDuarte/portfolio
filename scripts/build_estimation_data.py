"""Build site/motorsport/data/estimation-bahrain.json (phase 3, project #102).

    python scripts/build_estimation_data.py

Monte Carlo comparison of sideslip estimators on a simulated truth driven by the calibrated
Bahrain lap: raw-sensor integrator, EKF with a linear tyre, EKF and UKF with the Magic Formula,
and a UKF that also estimates the friction scale λ. Two truths: tyres as calibrated, and worn
tyres with 10 % less friction that no filter is told about. Deterministic (fixed seeds).
"""
from __future__ import annotations

import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from state_estimation.filters import EKF, UKF, Model, fy_linear, run  # noqa: E402
from state_estimation.scenario import Sensors, consistency, integrator_baseline, make_truth, sensors  # noqa: E402

OUT = ROOT / "site" / "motorsport" / "data" / "estimation-bahrain.json"
N_RUNS = 40
SPEED_FACTOR, YAW_GAIN = 0.95, 0.8
WARMUP = 50                                  # samples (1 s) excluded from the statistics
r3 = lambda x: round(float(x), 3)


def tuned_q(sens: Sensors, dt: float, augmented: bool = False):
    """Process noise tuned on the nominal truth so the UKF median NEES sits inside the χ² band
    (documented in docs/physics/ESTIMATION.md); it is not re-tuned for the worn-tyre case."""
    q = [0.05 ** 2, 0.2 ** 2, 0.02 ** 2, (sens.gyro_bias_rw * np.sqrt(dt)) ** 2]
    if augmented:
        q.append(0.001 ** 2)
    return np.diag(q)


def main() -> None:
    sens = Sensors()
    dt = 1.0 / sens.rate_hz
    R = np.diag([sens.gyro ** 2, sens.accel ** 2, sens.wheel_speed ** 2])
    out = {"schema": 1, "generated_by": "scripts/build_estimation_data.py",
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
           "sensors": {k: (float(v) if not isinstance(v, str) else v) for k, v in asdict(sens).items()},
           "runs": N_RUNS, "rate_hz": sens.rate_hz, "speed_factor": SPEED_FACTOR, "scenarios": {}}
    for label, lam_scale in (("nominal", 1.0), ("gasto", 0.9)):
        truth, p, tyre = make_truth(lam_scale=lam_scale, speed_factor=SPEED_FACTOR, yaw_gain=YAW_GAIN)
        U, Z, bias = sensors(truth, sens, N_RUNS, seed=102)
        X = np.concatenate([np.repeat(truth.x[None], N_RUNS, 0), bias[..., None]], -1)
        x0 = np.column_stack([Z[:, 0, 2], np.zeros(N_RUNS), Z[:, 0, 0], np.zeros(N_RUNS)])
        P0 = np.repeat(np.diag([0.2 ** 2, 0.5 ** 2, 0.05 ** 2, sens.gyro_bias0 ** 2])[None], N_RUNS, 0)
        lam_f = tyre.lambda_muy                              # the filters' (calibrated) friction
        beta_t = truth.beta
        rows, series = {}, {}

        def score(name, xs, Ps, nis, seconds, est_beta=None):
            be = np.arctan2(xs[..., 1], xs[..., 0]) if est_beta is None else est_beta
            e = np.degrees(be - beta_t[None])[:, WARMUP:]
            run_rmse = np.sqrt(np.mean(e ** 2, axis=1))
            row = {"beta_rmse_deg": r3(run_rmse.mean()), "beta_rmse_ci95": [r3(x) for x in np.quantile(run_rmse, [0.025, 0.975])],
                   "beta_max_abs_err_deg": r3(np.abs(e).max()), "ms_per_step": r3(1000 * seconds / (len(truth.t) * N_RUNS))}
            if Ps is not None:
                sd = np.sqrt(Ps[..., 1, 1]) / np.maximum(xs[..., 0], 1.0)
                row["beta_cover95"] = r3(np.mean(np.abs(be - beta_t[None])[:, WARMUP:] <= 1.96 * sd[:, WARMUP:]))
                err = xs[..., :4] - X
                avg, (lo, hi) = consistency(err[:, WARMUP:], Ps[:, WARMUP:, :4, :4], N_RUNS)
                row["anees_median"] = r3(np.median(avg))
                row["anees_band"] = [r3(lo), r3(hi)]
                row["anees_in_band"] = r3(np.mean((avg >= lo) & (avg <= hi)))
                row["anis_mean"] = r3(np.nanmean(nis[:, WARMUP:]))
                row["gyro_bias_rmse_deg_s"] = r3(np.degrees(np.sqrt(np.mean((xs[:, -1, 3] - bias[:, -1]) ** 2))))
                series[name] = {"beta_deg": np.round(np.degrees(be[0, ::5]), 3).tolist(),
                                "sd2_deg": np.round(np.degrees(2 * sd[0, ::5]), 3).tolist(),
                                "anees": [None if np.isnan(v) else v for v in
                                          np.round(np.concatenate([[np.nan] * WARMUP, avg])[::5], 3).tolist()]}
            else:
                series[name] = {"beta_deg": np.round(np.degrees(be[0, ::5]), 3).tolist()}
            rows[name] = row

        t0 = time.time()
        bi = integrator_baseline(Z, U, dt)
        score("Integrador (sensores brutos)", np.zeros((N_RUNS, len(truth.t), 4)), None, None, time.time() - t0, est_beta=bi)
        for name, F, force in (("EKF, pneu linear", EKF, fy_linear), ("EKF, Magic Formula", EKF, None), ("UKF, Magic Formula", UKF, None)):
            m = Model(p, tyre, dt, False, lam_f) if force is None else Model(p, tyre, dt, False, lam_f, force)
            t0 = time.time()
            xs, Ps, nis = run(F(m, tuned_q(sens, dt), R), x0, P0, U, Z)
            score(name, xs, Ps, nis, time.time() - t0)
        # joint estimation of the friction scale
        ma = Model(p, tyre, dt, True, lam_f)
        x0a = np.column_stack([x0, np.full(N_RUNS, lam_f)])
        P0a = np.repeat(np.diag(list(np.diag(P0[0])) + [0.15 ** 2])[None], N_RUNS, 0)
        t0 = time.time()
        xa, Pa, nisa = run(UKF(ma, tuned_q(sens, dt, True), R), x0a, P0a, U, Z)
        score("UKF + aderência λ", xa, Pa, nisa, time.time() - t0)
        lam_tr = xa[..., 4]
        out["scenarios"][label] = {
            "lam_scale_truth": lam_scale, "lam_truth_axle_model": r3(truth.lam), "lam_filter": r3(lam_f),
            "duration_s": r3(truth.t[-1]), "distance_m": r3(truth.s[-1]),
            "beta_truth_stats_deg": {"rms": r3(np.degrees(np.sqrt(np.mean(beta_t ** 2)))), "max_abs": r3(np.degrees(np.abs(beta_t).max()))},
            "ay_max_g": r3(np.abs(truth.ay).max() / 9.80665),
            "table": rows,
            "lambda_est": {"final_mean": r3(lam_tr[:, -1].mean()), "final_sd_runs": r3(lam_tr[:, -1].std(ddof=1)),
                           "final_sd_filter": r3(np.sqrt(Pa[:, -1, 4, 4]).mean()),
                           "series_mean": np.round(lam_tr.mean(axis=0)[::5], 4).tolist(),
                           "series_sd2": np.round(2 * np.sqrt(Pa[0, :, 4, 4])[::5], 4).tolist()},
            "t": np.round(truth.t[::5], 2).tolist(), "s": np.round(truth.s[::5], 1).tolist(),
            "beta_truth_deg": np.round(np.degrees(beta_t[::5]), 3).tolist(),
            "ay_g": np.round(truth.ay[::5] / 9.80665, 3).tolist(),
            "v_kmh": np.round(truth.x[::5, 0] * 3.6, 1).tolist(),
            "series": series,
        }
        print(label, json.dumps(rows, ensure_ascii=False, indent=1))
        print(label, "lambda", out["scenarios"][label]["lambda_est"]["final_mean"], "truth", truth.lam, "filter", lam_f)
    # relative grip change detected by the joint estimator
    lam_n = out["scenarios"]["nominal"]["lambda_est"]["final_mean"]
    lam_w = out["scenarios"]["gasto"]["lambda_est"]["final_mean"]
    out["grip_drop_detected_pct"] = r3(100 * (1 - lam_w / lam_n))
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False, default=lambda o: o.item()),
                   encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB); grip drop detected {out['grip_drop_detected_pct']} %")


if __name__ == "__main__":
    main()
