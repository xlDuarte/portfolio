> **Status de implementação #094: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #094 — Sistema Integrado de Previsão de Demanda e Estoque Crítico
## Integrated S&OP & ICS Demand System

- **Categoria / Route:** `/projetos/advanced/94` (`10 / 10`)
- **Diretório GitHub:** `projetos/10-advanced/094-integrated-s-op-ics-demand-system`
- **Benchmark de Referência:** `94 Demand Prediction System`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Docker, FastAPI, Kafka, Streamlit, Power BI`
- **Fluxo de Engenharia (How It Flows):** `Stream IIoT/SAP -> Pipeline ETL -> Modelo IA/BI -> Deploy Prod` (`Data Stream -> Pipeline -> Model -> Deploy`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Solução ponta a ponta conectando previsão estatística à geração de requisições SAP.

## 2. Industrial & Motorsport Context (EN-US)
End-to-end solution connecting statistical forecasting to automated SAP requisitions.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
