> **Status de implementação #020: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #020 — Causas-Raiz de Atrasos em Fretes Críticos e Aéreos
## Critical Freight Delay Root-Cause EDA

- **Categoria / Route:** `/projetos/eda/20` (`02 / 10`)
- **Diretório GitHub:** `projetos/02-eda/020-critical-freight-delay-root-cause-eda`
- **Benchmark de Referência:** `20 Flight Delay Analysis`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Seaborn, Matplotlib, Plotly, SQL`
- **Fluxo de Engenharia (How It Flows):** `Dataset Bruto -> Distribuições -> Correlações -> Diagnóstico` (`Dataset -> Distributions -> Correlations -> Findings`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Decomposição de atrasos logísticos por modal, desembaraço fiscal e gargalos de terminal.

## 2. Industrial & Motorsport Context (EN-US)
Breakdown of logistics delays by transport mode, tax clearance, and terminal bottlenecks.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
