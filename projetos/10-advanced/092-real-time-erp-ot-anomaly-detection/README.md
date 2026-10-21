> **Status de implementação #092: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #092 — Monitoramento em Tempo Real de Anomalias Transacionais ERP
## Real-Time ERP/OT Anomaly Detection

- **Categoria / Route:** `/projetos/advanced/92` (`10 / 10`)
- **Diretório GitHub:** `projetos/10-advanced/092-real-time-erp-ot-anomaly-detection`
- **Benchmark de Referência:** `92 Real-Time Fraud Detection`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Docker, FastAPI, Kafka, Streamlit, Power BI`
- **Fluxo de Engenharia (How It Flows):** `Stream IIoT/SAP -> Pipeline ETL -> Modelo IA/BI -> Deploy Prod` (`Data Stream -> Pipeline -> Model -> Deploy`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Pipeline de streaming via Kafka/FastAPI para auditar movimentações críticas de estoque em tempo real.

## 2. Industrial & Motorsport Context (EN-US)
Kafka/FastAPI streaming pipeline auditing critical inventory movements in real time.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
