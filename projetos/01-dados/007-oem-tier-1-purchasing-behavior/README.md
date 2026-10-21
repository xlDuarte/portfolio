> **Status de implementação #007: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #007 — Comportamento de Requisições e Compras (OEM/Tier-1)
## OEM & Tier-1 Purchasing Behavior

- **Categoria / Route:** `/projetos/dados/7` (`01 / 10`)
- **Diretório GitHub:** `projetos/01-dados/007-oem-tier-1-purchasing-behavior`
- **Benchmark de Referência:** `07 Customer Purchase Analysis`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, NumPy, Matplotlib, Jupyter, Power BI`
- **Fluxo de Engenharia (How It Flows):** `Ingestão SAP/CSV -> Limpeza ETL -> Exploração -> Insights KPI` (`Load Data -> Clean ETL -> Explore -> KPI Insights`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Padrões de recorrência em ordens de compra no SAP/ARIBA, lotes econômicos e concentração de demanda.

## 2. Industrial & Motorsport Context (EN-US)
Recurrence patterns in SAP/ARIBA purchase orders, economic lot sizes, and demand concentration.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
