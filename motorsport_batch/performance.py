"""Interactive 5-stage *illustrative* performance engineering calculations (#110).

This is NOT ChassisSim, not FLIR camera analysis, and has no calibrated tire
measurements. Existing mathematical classes are reused rather than rewritten.

The illustrative "QSS proxy" of Day 4 is superseded by :mod:`vehicle_dynamics`: Magic Formula
tyre, load transfer, g-g-V envelope and a quasi-steady-state lap simulation calibrated on real
OpenF1 telemetry of the 2024 Bahrain GP (see :func:`bahrain_lap` and docs/physics/LAPSIM.md).
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ORIGINAL=Path(__file__).resolve().parents[1]/"projetos/11-motorsport-f1-mlops/110-complete-motorsport-performance-engineering-suite-tire-physics-flir-setup-hh-timing-laptime-sim/main.py"
def originals():
    s=importlib.util.spec_from_file_location("preserved_110",ORIGINAL)
    m=importlib.util.module_from_spec(s)
    sys.modules[s.name]=m
    s.loader.exec_module(m)
    return m

def thermal_grid(inner=94.,middle=89.,outer=85.,height=30,width=90):
    if not all(np.isfinite(v) for v in (inner,middle,outer)):raise ValueError("Temperatures must be finite")
    row=np.interp(np.linspace(0,2,width),[0,1,2],[inner,middle,outer])
    grid=np.tile(row,(height,1))
    return grid

def damper_histogram(seed=110,n=1200):
    rng=np.random.default_rng(seed)
    velocities=rng.normal(0,31,n)
    velocities=np.clip(velocities,-90,90)
    bands={"low_speed_bump":int(((velocities>=0)&(velocities<25)).sum()),
           "high_speed_bump":int((velocities>=25).sum()),
           "low_speed_rebound":int(((velocities<0)&(velocities>=-25)).sum()),
           "high_speed_rebound":int((velocities<-25).sum())}
    if sum(bands.values())!=n:raise ValueError("Inconsistent histogram")
    return bands

def sweep(pressures=(1.3,1.6,1.9,2.2,2.5,2.8),loads=(3300.,4200.,4800.)):
    e=originals()
    return [{"load_N":load,"pressure_bar":p,
             **e.Day2TirePhysicsAndFLIR.compute_slip_stiffness(load,p)}
            for load in loads for p in pressures]

def scenario(downforce=2.65,drag=.94,grip=1.03):
    m=originals()
    days={
        "day1":m.Day1DataAcquisitionMetrics.evaluate_sector_priorities(268,94.5,1.85,64.2),
        "day2_tire":m.Day2TirePhysicsAndFLIR.compute_slip_stiffness(4243,2.),
        "day2_thermal":m.Day2TirePhysicsAndFLIR.analyze_flir_thermal_patch(94.,89.5,85.),
        "day3_balance":m.Day3DriverBalanceAndDamperSetup.quantify_balance_and_dampers(58,2.51,68,1.92,1650,2900),
        "day4_qss_proxy":m.Day4ChassisSimLaptimeAndQualiDelta.simulate_qss_laptime(downforce,drag,grip),
        "day5_event_checklist":{"tire_pressure_check":True,"sensor_zero_check":True,
                                "brake_temperature_review":True,"engineer_signoff_required":True},
        "damper_histogram":damper_histogram(),
    }
    return days

def bahrain_lap(**overrides) -> dict:
    """Lap of the calibrated car on the Bahrain 2024 line, optionally with changed parameters.

    Keys: mass, power, cla, cda, lambda_muy, lambda_mux, aero_balance, h_cg (SI units)."""
    import json
    from vehicle_dynamics import Car, MagicFormula, Track, simulate
    data = json.loads((Path(__file__).resolve().parents[1] / "site/motorsport/data/lapsim-bahrain.json").read_text(encoding="utf-8"))
    spec = dict(data["car"])
    tyre = MagicFormula(**spec.pop("tyre"))
    car = Car(**spec, tyre=tyre).with_(**overrides) if overrides else Car(**spec, tyre=tyre)
    t = data["track"]
    track = Track(np.array(t["s"]), np.array(t["x"]), np.array(t["y"]), np.array(t["z"]), np.array(t["kappa"]),
                  np.array(t["grade"]), t["length_m"], {})
    res = simulate(car, track)
    return {"lap_time_s": round(res.lap_time, 3), "v_max_kmh": round(float(res.v.max()) * 3.6, 1),
            "v_min_kmh": round(float(res.v.min()) * 3.6, 1), "measured_lap_s": data["calibration"]["VER"]["lap_time_meas_s"]}


def run_app():
    st.set_page_config(page_title="Motorsport Performance Lab",layout="wide")
    st.title("Motorsport Performance Lab — physics proxy")
    st.warning("Termografia gerada numericamente, não FLIR. O cálculo QSS é uma fórmula ilustrativa, não o software ChassisSim.")
    left,right=st.columns(2)
    with left:cl=st.slider("Downforce (coef. fictício)",1.5,4.0,2.65,.05)
    with right:cd=st.slider("Drag (coef. fictício)",.5,1.5,.94,.01)
    metrics=scenario(cl,cd)
    st.metric("Proxy de tempo de volta (fórmula ilustrativa antiga)",f'{metrics["day4_qss_proxy"]["predicted_laptime_s"]:.3f}s')
    lap=bahrain_lap(cla=cl*3.72/2.65, cda=cd*1.633/.94)
    st.metric("Volta QSS calibrada, Bahrein 2024",f'{lap["lap_time_s"]:.3f}s',f'{lap["lap_time_s"]-lap["measured_lap_s"]:+.3f}s vs. volta real de VER')
    st.plotly_chart(go.Figure(data=[go.Heatmap(z=thermal_grid(),colorscale="Hot")])
                    .update_layout(title="Três zonas térmicas — simulação"),use_container_width=True)
    st.dataframe(pd.DataFrame(sweep()),use_container_width=True)
    st.bar_chart(pd.DataFrame([metrics["damper_histogram"]]))
    st.json(metrics)
if __name__=="__main__":run_app()
