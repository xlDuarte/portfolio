> **Status de implementação #064: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #064 — Forecasting de Demanda de Energia em Horário de Ponta
## Rolling Mill Electricity Demand Forecast

- **Categoria / Route:** `/projetos/timeseries/64` (`07 / 10`)
- **Diretório GitHub:** `projetos/07-timeseries/064-rolling-mill-electricity-demand-forecast`
- **Benchmark de Referência:** `64 Electricity Demand Forecasting`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Statsmodels, Prophet, Plotly`
- **Fluxo de Engenharia (How It Flows):** `Série Histórica -> Tendência + Sazonal -> Forecast -> Erro MAPE` (`Time Data -> Trend + Season -> Forecast -> MAPE Error`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Previsão horária de carga elétrica industrial para otimização de contratos no mercado livre.

## 2. Industrial & Motorsport Context (EN-US)
Hourly industrial power load forecasting to optimize free-market energy contracts.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
