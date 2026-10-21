> **Status de implementação #004: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #004 — Espectro Acústico e Vibração Veicular (NVH)
## Acoustic NVH & Vibration Spectrum Analysis

- **Categoria / Route:** `/projetos/dados/4` (`01 / 10`)
- **Diretório GitHub:** `projetos/01-dados/004-acoustic-nvh-vibration-spectrum-analysis`
- **Benchmark de Referência:** `04 Spotify Music Analysis`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, NumPy, Matplotlib, Jupyter, Power BI`
- **Fluxo de Engenharia (How It Flows):** `Ingestão SAP/CSV -> Limpeza ETL -> Exploração -> Insights KPI` (`Load Data -> Clean ETL -> Explore -> KPI Insights`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Extração de atributos de frequência sonora e amplitude harmônica em testes de bancada de motores.

## 2. Industrial & Motorsport Context (EN-US)
Frequency attribute extraction and harmonic amplitude profiling in engine test-bench runs.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
