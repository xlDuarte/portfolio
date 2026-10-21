> **Status de implementação #070: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #070 — Previsão de Taxa de Consumo (Burn-Rate) de Insumos Químicos
## Consumables Burn-Rate Forecasting

- **Categoria / Route:** `/projetos/timeseries/70` (`07 / 10`)
- **Diretório GitHub:** `projetos/07-timeseries/070-consumables-burn-rate-forecasting`
- **Benchmark de Referência:** `70 Food Demand Forecasting`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Statsmodels, Prophet, Plotly`
- **Fluxo de Engenharia (How It Flows):** `Série Histórica -> Tendência + Sazonal -> Forecast -> Erro MAPE` (`Time Data -> Trend + Season -> Forecast -> MAPE Error`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Previsão semanal de consumo de fluidos de corte, gases industriais e refratários.

## 2. Industrial & Motorsport Context (EN-US)
Weekly consumption forecasting for cutting fluids, industrial gases, and refractories.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
