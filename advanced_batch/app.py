"""Read-only presentation UI for the development FastAPI service.

No direct equipment controls, purchasing actions, hiring rejections or safety
actions. API connection must be to a local/development demo with fake data.
"""
from __future__ import annotations
import os
import httpx
import streamlit as st
from .engine import SPECS

def run_app(default_project:int=91)->None:
    if default_project not in SPECS:raise ValueError("Invalid project")
    st.set_page_config(page_title="Advanced Industrial Lab",layout="wide")
    st.title("Advanced Industrial Lab — synthetic streams")
    st.warning("Projeto demonstrativo. Nada se conecta a SAP/OT reais ou comanda equipamento.")
    api=st.text_input("Development-only API URL",value=os.environ.get("ADVANCED_API_URL","http://127.0.0.1:8000"))
    project_ids=sorted(SPECS)
    project=st.selectbox("Projeto",project_ids,index=project_ids.index(default_project),
                         format_func=lambda k:f"#{k:03d} — {SPECS[k]['title']}")
    count=st.slider("Eventos sintéticos",min_value=24,max_value=200,step=8,value=96)
    st.caption(SPECS[project]["description"])
    if st.button("Gerar eventos fictícios e consultar API",type="primary"):
        try:
            # Requests only within explicit user interaction, never on render.
            with httpx.Client(base_url=api,timeout=20.) as client:
                ingested=client.post(f"/v1/projects/{project}/simulate",params={"count":count})
                ingested.raise_for_status()
                response=client.get(f"/v1/projects/{project}/analytics")
                response.raise_for_status()
            report=response.json()
            st.metric("Registros na análise",report["sample_count"])
            st.json(ingested.json())
            st.subheader("Indicadores e artefatos do projeto")
            st.json(report["metrics"],expanded=True)
        except (httpx.HTTPError,ValueError) as exc:
            st.error(f"API local não respondeu: {exc}")
    st.caption("Sem conexão direta a Kafka, banco de produção ou Power BI; API guarda SQLite demonstrativo.")

if __name__=="__main__":
    run_app()
