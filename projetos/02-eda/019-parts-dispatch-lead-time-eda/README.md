> **Status de implementação #019: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #019 — Tempos de Despacho e Logística Inbound/Outbound
## Parts Dispatch & Lead-Time EDA

- **Categoria / Route:** `/projetos/eda/19` (`02 / 10`)
- **Diretório GitHub:** `projetos/02-eda/019-parts-dispatch-lead-time-eda`
- **Benchmark de Referência:** `19 Food Delivery Analysis`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Seaborn, Matplotlib, Plotly, SQL`
- **Fluxo de Engenharia (How It Flows):** `Dataset Bruto -> Distribuições -> Correlações -> Diagnóstico` (`Dataset -> Distributions -> Correlations -> Findings`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Identificação de outliers em rotas de entrega, janelas de coleta e impacto climático no frete.

## 2. Industrial & Motorsport Context (EN-US)
Outlier detection in delivery routes, pickup windows, and weather impact on freight lead times.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
