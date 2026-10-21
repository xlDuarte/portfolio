> **Status de implementação #025: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #025 — Projeção de Custos de Saúde Ocupacional e Sinistralidade
## Occupational Safety Cost Prediction

- **Categoria / Route:** `/projetos/regression/25` (`03 / 10`)
- **Diretório GitHub:** `projetos/03-regression/025-occupational-safety-cost-prediction`
- **Benchmark de Referência:** `25 Medical Cost Prediction`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Eng. Atributos -> Treinamento -> Avaliação R²/MAE -> Predição` (`Features -> Train -> Evaluate -> Predict`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Estimativa atuarial de despesas médicas/segurança com base em fatores de risco ergonômico.

## 2. Industrial & Motorsport Context (EN-US)
Actuarial estimation of occupational health expenses based on ergonomic risk factors.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
