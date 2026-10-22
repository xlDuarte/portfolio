"""Manual-time-slider visualization for #109 synthetic telemetry only.

The geometry is inspired by an arbitrary closed parametric circuit; it is NOT
surveyed Interlagos GPS. Dynamic frames derive from preserved kinematic engine.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import plotly.graph_objects as go
import streamlit as st

ORIGINAL=Path(__file__).resolve().parents[1]/"projetos/11-motorsport-f1-mlops/109-f1-telemetry-race-replay-live-gps-track-position-engine-built-from-scratch/main.py"

def original_engine():
    spec=importlib.util.spec_from_file_location("preserved_109",ORIGINAL)
    module=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

def snapshot(time_seconds:float=900):
    if not 0<=time_seconds<=7200:raise ValueError("Elapsed seconds must be 0..7200")
    e=original_engine()
    circuit=e.ParametricCircuitEngine()
    roster=[e.CarEntry("#01","DRV-A","Synthetic A","SOFT",1.72,1.012,6),
            e.CarEntry("#16","DRV-B","Synthetic B","MEDIUM",1.70,1.008,8),
            e.CarEntry("#44","DRV-C","Synthetic C","HARD",1.69,1.005,11)]
    sim=e.TelemetryReplaySimulator(circuit,roster)
    return circuit,sim.snapshot_leaderboard(time_seconds)

def render(time_seconds:float=900):
    circuit,leaders=snapshot(time_seconds)
    samples=[circuit.sample_point(i*circuit.length_m/499) for i in range(500)]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=[r["x_m"] for r in samples],y=[r["y_m"] for r in samples],
                             mode="lines",name="Synthetic closed circuit"))
    fig.add_trace(go.Scatter(x=[r["x_m"] for r in leaders],y=[r["y_m"] for r in leaders],
                             mode="markers+text",text=[r["driver"] for r in leaders],
                             textposition="top center",marker={"size":13},name="Vehicles"))
    fig.update_layout(title=f"Fictional Motorsport Replay · t={time_seconds:.1f}s",
                      xaxis_title="Synthetic X (m)",yaxis_title="Synthetic Y (m)",
                      yaxis={"scaleanchor":"x","scaleratio":1})
    return fig,leaders

def run_app():
    st.set_page_config(page_title="Motorsport telemetry replay",layout="wide")
    st.title("Synthetic F1-style telemetry replay")
    st.warning("Não é GPS real, não reproduz Interlagos geometricamente nem recebe cronometragem ao vivo.")
    t=st.slider("Tempo do replay (segundos)",0.0,3600.0,900.0,step=.5)
    figure,rank=render(t)
    st.plotly_chart(figure,use_container_width=True)
    st.dataframe(rank,use_container_width=True)
if __name__=="__main__":
    run_app()
