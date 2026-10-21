> **Status de implementação #058: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #058 — Recomendador de Fornecedores Homologados (ARIBA)
## Approved Supplier Recommender (Ariba)

- **Categoria / Route:** `/projetos/recommendation/58` (`06 / 10`)
- **Diretório GitHub:** `projetos/06-recommendation/058-approved-supplier-recommender-ariba`
- **Benchmark de Referência:** `58 Restaurant Recommendation System`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, NumPy, Scikit-learn, Streamlit`
- **Fluxo de Engenharia (How It Flows):** `Perfil / Ativo -> Similaridade -> Ranking -> Top-N Ações` (`Asset Data -> Similarity -> Rank -> Top-N`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Ranking de fornecedores ideais por histórico de qualidade (IQF), prazo (OTIF) e preço.

## 2. Industrial & Motorsport Context (EN-US)
Ranking optimal suppliers by historical quality (IQF), on-time delivery (OTIF), and cost.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
