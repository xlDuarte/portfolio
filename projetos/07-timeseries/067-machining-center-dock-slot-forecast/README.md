> **Status de implementação #067: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #067 — Previsão de Ocupação de Centros de Usinagem e Docas
## Machining Center & Dock Slot Forecast

- **Categoria / Route:** `/projetos/timeseries/67` (`07 / 10`)
- **Diretório GitHub:** `projetos/07-timeseries/067-machining-center-dock-slot-forecast`
- **Benchmark de Referência:** `67 Hotel Booking Forecasting`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Statsmodels, Prophet, Plotly`
- **Fluxo de Engenharia (How It Flows):** `Série Histórica -> Tendência + Sazonal -> Forecast -> Erro MAPE` (`Time Data -> Trend + Season -> Forecast -> MAPE Error`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Modelagem de agendamentos de máquina e janelas de recebimento logístico.

## 2. Industrial & Motorsport Context (EN-US)
Forecasting machine scheduling utilization and logistics receiving dock slots.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
