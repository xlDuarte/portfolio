> **Status de implementação #038: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #038 — Detecção de Anomalias e Fraudes em Compras (SAP/SOX)
## SAP Procurement Anomaly Detection

- **Categoria / Route:** `/projetos/classification/38` (`04 / 10`)
- **Diretório GitHub:** `projetos/04-classification/038-sap-procurement-anomaly-detection`
- **Benchmark de Referência:** `38 Fraud Transaction Detection`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Atributos -> Treino Modelo -> Matriz Confusão -> Classe Alvo` (`Features -> Train -> Confusion Matrix -> Label`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Identificação de fracionamento de ordens de compra, desvios de alçada e lançamentos atípicos.

## 2. Industrial & Motorsport Context (EN-US)
Detection of split purchase orders, approval bypasses, and atypical ERP entries.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
