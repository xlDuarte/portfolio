> **Status de implementação #037: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #037 — Classificação de Degradação Química de Lubrificantes
## Lubricant Degradation Classifier

- **Categoria / Route:** `/projetos/classification/37` (`04 / 10`)
- **Diretório GitHub:** `projetos/04-classification/037-lubricant-degradation-classifier`
- **Benchmark de Referência:** `37 Diabetes Prediction`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Atributos -> Treino Modelo -> Matriz Confusão -> Classe Alvo` (`Features -> Train -> Confusion Matrix -> Label`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Análise físico-química de óleo industrial (viscosidade, partículas, acidez) para troca preditiva.

## 2. Industrial & Motorsport Context (EN-US)
Physicochemical oil analysis (viscosity, particles, acidity) for predictive oil change.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
