> **Status de implementação #054: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #054 — Recomendação Cruzada de Ferramentaria e Insumos (MRO)
## Tooling & Spare Parts Recommender

- **Categoria / Route:** `/projetos/recommendation/54` (`06 / 10`)
- **Diretório GitHub:** `projetos/06-recommendation/054-tooling-spare-parts-recommender`
- **Benchmark de Referência:** `54 Product Recommendation System`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, NumPy, Scikit-learn, Streamlit`
- **Fluxo de Engenharia (How It Flows):** `Perfil / Ativo -> Similaridade -> Ranking -> Top-N Ações` (`Asset Data -> Similarity -> Rank -> Top-N`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Sugestão de insertos, rolamentos e EPIs complementares na abertura de requisição SAP.

## 2. Industrial & Motorsport Context (EN-US)
Suggesting complementary inserts, bearings, and PPE during SAP requisition entry.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
