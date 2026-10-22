"""Interactive Streamlit UI for all ten synthetic industrial recommendation scenarios.

Run: streamlit run recommendation_batch/app.py
Or use a project's streamlit_app.py entrypoint. No write-back to external apps.
"""
from __future__ import annotations
import json
import streamlit as st
from recommendation_batch.engine import SPECS, FIXTURES, recommend

def run_app(default_project: int = 51) -> None:
    if default_project not in SPECS:
        raise ValueError("Unknown project")
    st.set_page_config(page_title="Industrial Recommendation Lab",layout="wide")
    st.title("Industrial Recommendation Lab")
    st.warning("DADOS E RESULTADOS SINTÉTICOS. Nenhum SAP/Ariba, rota real, notícia externa ou sistema de RH está conectado.")
    keys = list(SPECS)
    p = st.selectbox("Projeto", keys, index=keys.index(default_project),
                     format_func=lambda i: f"#{i:03d} — {SPECS[i]['title']}")
    cfg = SPECS[p]
    query = st.text_input("Consulta / ativo / origem>destino",value=cfg["query"])
    top_k = st.slider("Quantidade máxima de recomendações (exceto BOM completo)",1,12,5)
    filters: dict = {}
    if p == 51:
        filters["asset"] = st.selectbox("Tipo de ativo",["all","pump","motor","gearbox","cnc"])
        filters["language"] = st.selectbox("Idioma",["all","pt","en"])
        filters={k:v for k,v in filters.items() if v!="all"}
    elif p == 53:
        domain = st.selectbox("Domínio",["all","welding","hydraulics","metrology","cnc","procurement","safety","quality"])
        if domain!="all":filters["domain"]=domain
    elif p == 54:
        filters["asset"] = st.selectbox("Ativo",["pump","gearbox","cnc"])
        filters["min_stock"] = st.number_input("Estoque mínimo",min_value=0,max_value=1000,value=1)
    elif p == 55:
        filters["max_hours"] = st.number_input("Horas disponíveis",min_value=1,max_value=500,value=60)
        filters["known_skills"] = st.multiselect("Habilidades já concluídas",
                sorted({c["skill"] for c in FIXTURES["courses"]}),default=[])
    elif p == 56:
        filters["min_hours"] = st.number_input("Disponibilidade mínima (horas)",min_value=1,max_value=500,value=12)
    elif p == 57:
        filters["max_age_days"] = st.slider("Idade máxima do item sintético (dias)",1,120,30)
    elif p == 58:
        filters["category"] = st.selectbox("Categoria",["bearings","hydraulics"])
        filters["quantity"] = st.number_input("Quantidade simulada",1,10000,100)
        filters["max_lead_days"] = st.number_input("Lead time máximo simulado (dias)",1,365,10)
        filters["min_otif"] = st.slider("OTIF mínimo artificial",0.0,1.0,0.9)
    elif p == 59:
        filters["modes"] = st.multiselect("Modais elegíveis",["truck","rail"],default=["truck","rail"])
    elif p == 60:
        filters["units"] = st.number_input("Unidades da manutenção",1,500,2)
        filters["pack_size"] = st.number_input("Múltiplo de embalagem",1,100,5)
        st.info("BOM completo: o limite 'top-K' não descarta componentes obrigatórios.")
    if st.button("Calcular recomendação",type="primary"):
        try:
            result = recommend(p,query,top_k,filters)
        except (ValueError,TypeError) as exc:
            st.error(str(exc))
        else:
            st.metric("Itens elegíveis retornados",result["result_count"])
            st.caption("Resultados exclusivamente demonstrativos, explicações e filtros visíveis no JSON abaixo.")
            st.json(result,expanded=True)

if __name__=="__main__":
    run_app()
