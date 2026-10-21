> **Status de implementação #016: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #016 — Telemetria de Pit-Stop e Troca Rápida de Ferramenta (SMED)
## SMED & High-Speed Setup Telemetry EDA

- **Categoria / Route:** `/projetos/eda/16` (`02 / 10`)
- **Diretório GitHub:** `projetos/02-eda/016-smed-high-speed-setup-telemetry-eda`
- **Benchmark de Referência:** `16 IPL Match Analysis`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Seaborn, Matplotlib, Plotly, SQL`
- **Fluxo de Engenharia (How It Flows):** `Dataset Bruto -> Distribuições -> Correlações -> Diagnóstico` (`Dataset -> Distributions -> Correlations -> Findings`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Análise estatística de micro-tempos de setup em usinagem/laminação inspirada em pit-stops de F1.

## 2. Industrial & Motorsport Context (EN-US)
Statistical breakdown of machining/rolling micro-setup times inspired by F1 pit-stops.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
