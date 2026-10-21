> **Status de implementação #062: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #062 — Previsão S&OP de Faturamento e Demanda Industrial
## S&OP Industrial Sales Forecasting

- **Categoria / Route:** `/projetos/timeseries/62` (`07 / 10`)
- **Diretório GitHub:** `projetos/07-timeseries/062-s-op-industrial-sales-forecasting`
- **Benchmark de Referência:** `62 Sales Forecasting`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Statsmodels, Prophet, Plotly`
- **Fluxo de Engenharia (How It Flows):** `Série Histórica -> Tendência + Sazonal -> Forecast -> Erro MAPE` (`Time Data -> Trend + Season -> Forecast -> MAPE Error`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Decomposição sazonal e projeção de demanda em múltiplos horizontes para alinhamento fabril.

## 2. Industrial & Motorsport Context (EN-US)
Seasonal decomposition and multi-horizon demand forecasting for plant alignment.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
