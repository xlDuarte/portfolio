> **Status de implementação #015: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #015 — Auditorias de Qualidade de Lotes e Fornecedores
## Component Quality Audit Ratings EDA

- **Categoria / Route:** `/projetos/eda/15` (`02 / 10`)
- **Diretório GitHub:** `projetos/02-eda/015-component-quality-audit-ratings-eda`
- **Benchmark de Referência:** `15 Movie Ratings Analysis`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Seaborn, Matplotlib, Plotly, SQL`
- **Fluxo de Engenharia (How It Flows):** `Dataset Bruto -> Distribuições -> Correlações -> Diagnóstico` (`Dataset -> Distributions -> Correlations -> Findings`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Distribuição de notas de inspeção técnica de recebimento (IQF) e dispersão de não-conformidades.

## 2. Industrial & Motorsport Context (EN-US)
Distribution of incoming quality inspection scores (IQF) and non-conformity variance.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
