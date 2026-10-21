> **Status de implementação #096: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #096 — Motor de Recomendação de Parâmetros de Setup (MES)
## Real-Time MES Setup Recommendation Engine

- **Categoria / Route:** `/projetos/advanced/96` (`10 / 10`)
- **Diretório GitHub:** `projetos/10-advanced/096-real-time-mes-setup-recommendation-engine`
- **Benchmark de Referência:** `96 Real-Time Recommendation Engine`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Docker, FastAPI, Kafka, Streamlit, Power BI`
- **Fluxo de Engenharia (How It Flows):** `Stream IIoT/SAP -> Pipeline ETL -> Modelo IA/BI -> Deploy Prod` (`Data Stream -> Pipeline -> Model -> Deploy`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Sugestão em tempo real de parâmetros ótimos de máquina para maximizar OEE na troca de lote.

## 2. Industrial & Motorsport Context (EN-US)
Real-time suggestion of optimal machine parameters to maximize OEE during batch changeover.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
