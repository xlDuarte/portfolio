"""Interactive, read-only Streamlit dashboard of ten fictional industrial BI cases.

Run: streamlit run business_batch/app.py
No network APIs, SAP clients, credentials or live financial records.
"""
from __future__ import annotations
from pathlib import Path
import streamlit as st
from business_batch.engine import CONFIG,evaluate,ROOT

def run_app(default_project:int=82):
    if default_project not in CONFIG:raise ValueError("Unknown business project")
    st.set_page_config(page_title="Industrial Finance & BI Lab",layout="wide")
    st.title("Industrial Finance & BI Lab")
    st.warning("Dados inteiramente SINTÉTICOS. Nenhuma conexão SAP/Ariba, Power BI Desktop, DAX engine ou dado financeiro real.")
    projects=list(CONFIG)
    p=st.selectbox("Selecione o caso de negócio",projects,index=projects.index(default_project),
                   format_func=lambda x:f"#{x:03d} — {CONFIG[x]['title']}")
    st.caption(CONFIG[p]["desc"])
    if st.button("Executar consultas SQL e atualizar análise",type="primary"):
        report=evaluate(p,save=True)
        m=report["metrics"]
        a,b,c=st.columns(3)
        a.metric("Registros retornados pela consulta SQL",report["sql_result_rows"])
        b.metric("Projeto",f"#{p:03d}")
        c.metric("Fonte","Sintética")
        st.subheader("Métricas calculadas")
        st.json(m,expanded=True)
        figure=ROOT/"figures"/f"{p:03d}.png"
        if figure.exists():
            st.image(str(figure),caption=f"#{p:03d} • figura gerada por Matplotlib",use_container_width=True)
        st.caption("Relatórios JSON, resultados SQL CSV, fontes raw CSV e gráfico PNG exportados localmente.")
if __name__=="__main__":
    run_app()
