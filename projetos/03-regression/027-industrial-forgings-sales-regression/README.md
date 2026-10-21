> **Status de implementação #027: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #027 — Previsão de Volume de Vendas de Forjados e Cilindros
## Industrial Forgings Sales Regression

- **Categoria / Route:** `/projetos/regression/27` (`03 / 10`)
- **Diretório GitHub:** `projetos/03-regression/027-industrial-forgings-sales-regression`
- **Benchmark de Referência:** `27 Sales Forecasting`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Fluxo de Engenharia (How It Flows):** `Eng. Atributos -> Treinamento -> Avaliação R²/MAE -> Predição` (`Features -> Train -> Evaluate -> Predict`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Modelo preditivo de demanda comercial integrando carteira de pedidos, cotas e indicadores setoriais.

## 2. Industrial & Motorsport Context (EN-US)
Commercial demand regression integrating order backlog, quotas, and sector indices.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
