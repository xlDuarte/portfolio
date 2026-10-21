> **Status de implementação #066: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #066 — Previsão de Consumo de Ferramentaria e ICS Críticos
## Critical ICS & Tooling Demand Forecast

- **Categoria / Route:** `/projetos/timeseries/66` (`07 / 10`)
- **Diretório GitHub:** `projetos/07-timeseries/066-critical-ics-tooling-demand-forecast`
- **Benchmark de Referência:** `66 Retail Demand Forecasting`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Statsmodels, Prophet, Plotly`
- **Fluxo de Engenharia (How It Flows):** `Série Histórica -> Tendência + Sazonal -> Forecast -> Erro MAPE` (`Time Data -> Trend + Season -> Forecast -> MAPE Error`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Projeção de ponto de pedido dinâmico para evitar ruptura de itens críticos no SAP.

## 2. Industrial & Motorsport Context (EN-US)
Dynamic reorder-point forecasting to prevent stockouts of critical SAP items.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
