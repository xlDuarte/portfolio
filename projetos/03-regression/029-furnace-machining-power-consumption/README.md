> **Status de implementação #029: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #029 — Predição de Consumo Elétrico em Fornos e Usinagem
## Furnace & Machining Power Consumption

- **Categoria / Route:** `/projetos/regression/29` (`03 / 10`)
- **Diretório GitHub:** `projetos/03-regression/029-furnace-machining-power-consumption`
- **Benchmark de Referência:** `29 Electricity Consumption Prediction`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Eng. Atributos -> Treinamento -> Avaliação R²/MAE -> Predição` (`Features -> Train -> Evaluate -> Predict`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Regressão multivariada para prever MWh por lote produtivo e evitar ultrapassagem de tarifa ponta.

## 2. Industrial & Motorsport Context (EN-US)
Multivariate regression predicting MWh per batch to prevent peak-tariff penalties.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
