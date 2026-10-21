> **Status de implementação #035: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #035 — Triagem de Alertas de Cibersegurança e Phishing IT/OT
## IT/OT Cybersecurity Alert Classifier

- **Categoria / Route:** `/projetos/classification/35` (`04 / 10`)
- **Diretório GitHub:** `projetos/04-classification/035-it-ot-cybersecurity-alert-classifier`
- **Benchmark de Referência:** `35 Spam Email Detection`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Atributos -> Treino Modelo -> Matriz Confusão -> Classe Alvo` (`Features -> Train -> Confusion Matrix -> Label`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Classificação de comunicações maliciosas e ruído em redes corporativas e industriais.

## 2. Industrial & Motorsport Context (EN-US)
Classification of malicious communications and alert noise across corporate/OT networks.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
