# #54 — Tooling & Spare Parts Recommender

**Status:** implementado como estudo sintético com código de recomendação executável. Sem acesso a dados corporativos, clientes ou funcionários.

## Escopo realizado
Ranking contextual de peças MRO, filtrando compatibilidade com o tipo de ativo, aprovação e disponibilidade de estoque antes de calcular similaridade.

**Algoritmo:** Pandas/Scikit-learn TF-IDF + similaridade cosseno com filtro rígido de compatibilidade e estoque. A interface interativa usa Streamlit e compartilha o motor auditável.

## Execução
```bash
python -m pip install -r requirements-recommendation.txt
python projetos/06-recommendation/054-tooling-spare-parts-recommender/main.py --query "rolamento para bomba hidráulica" --save
python -m streamlit run projetos/06-recommendation/054-tooling-spare-parts-recommender/streamlit_app.py
python -m unittest discover -s tests -p test_recommendation_batch.py -v
```

**Proveniência:** [fixtures versionadas](../../../recommendation_batch/fixtures.json) · [regras e testes](../../../recommendation_batch/README.md) · [motor](../../../recommendation_batch/engine.py).

**Limitação:** catálogo, preços e disponibilidade foram construídos apenas para testes de elegibilidade e ranking. Não há métricas de impacto real.
