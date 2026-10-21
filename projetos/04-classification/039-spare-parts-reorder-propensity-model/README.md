> **Status de implementação #039: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #039 — Propensão de Recompra de Peças de Reposição
## Spare Parts Reorder Propensity Model

- **Categoria / Route:** `/projetos/classification/39` (`04 / 10`)
- **Diretório GitHub:** `projetos/04-classification/039-spare-parts-reorder-propensity-model`
- **Benchmark de Referência:** `39 Customer Purchase Prediction`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Atributos -> Treino Modelo -> Matriz Confusão -> Classe Alvo` (`Features -> Train -> Confusion Matrix -> Label`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Classificador de probabilidade de reposição de componentes críticos em clientes da carteira.

## 2. Industrial & Motorsport Context (EN-US)
Propensity classifier for critical component reorders across active accounts.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
