> **Status de implementação #034: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #034 — Predição de Rotatividade (Turnover) em Operações
## Shop-Floor & Tech Attrition Prediction

- **Categoria / Route:** `/projetos/classification/34` (`04 / 10`)
- **Diretório GitHub:** `projetos/04-classification/034-shop-floor-tech-attrition-prediction`
- **Benchmark de Referência:** `34 Employee Attrition Prediction`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Atributos -> Treino Modelo -> Matriz Confusão -> Classe Alvo` (`Features -> Train -> Confusion Matrix -> Label`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Detecção de fatores críticos de retenção de operadores especializados e engenheiros.

## 2. Industrial & Motorsport Context (EN-US)
Detection of critical retention factors for specialized operators and engineers.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
