> **Status de implementação #036: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #036 — Diagnóstico de Falha Crítica em Bombas e Atuadores
## Hydraulic Pump Failure Classification

- **Categoria / Route:** `/projetos/classification/36` (`04 / 10`)
- **Diretório GitHub:** `projetos/04-classification/036-hydraulic-pump-failure-classification`
- **Benchmark de Referência:** `36 Heart Disease Prediction`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Atributos -> Treino Modelo -> Matriz Confusão -> Classe Alvo` (`Features -> Train -> Confusion Matrix -> Label`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Classificação de saúde de sistemas hidráulicos de alta pressão a partir de pressão, vazão e vibração.

## 2. Industrial & Motorsport Context (EN-US)
Health classification of high-pressure hydraulic systems from pressure, flow, and vibration.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
