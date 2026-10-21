> **Status de implementação #028: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #028 — Dimensionamento de Custo de Hardware Industrial / Edge
## Edge & Workstation Hardware Cost Model

- **Categoria / Route:** `/projetos/regression/28` (`03 / 10`)
- **Diretório GitHub:** `projetos/03-regression/028-edge-workstation-hardware-cost-model`
- **Benchmark de Referência:** `28 Laptop Price Prediction`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Eng. Atributos -> Treinamento -> Avaliação R²/MAE -> Predição` (`Features -> Train -> Evaluate -> Predict`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Estimativa de TCO de servidores de borda (GPUs, RAM, proteção IP67) por especificação.

## 2. Industrial & Motorsport Context (EN-US)
TCO estimation for edge servers and industrial workstations by hardware specification.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
