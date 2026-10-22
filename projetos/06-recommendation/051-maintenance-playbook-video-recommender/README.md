# #51 — Maintenance Playbook & Video Recommender

**Status:** funcionalidade específica executável, com entradas e dados exclusivamente sintéticos; não é prova de performance em produção.

## Escopo implementado
Playbooks e vídeos ranqueados por TF-IDF e similaridade cosseno; exclusão de documentação obsoleta; filtros por ativo e idioma.

**Ferramentas reais:** Python, Pandas, NumPy, Scikit-learn (TfidfVectorizer/cosine_similarity) e interface Streamlit.

**Código:** [motor](../../../recommendation_batch/engine.py) · [catálogo fictício](../../../recommendation_batch/fixtures.json) · [métodos e restrições](../../../recommendation_batch/README.md).

## Executar
```bash
python -m pip install -r requirements-recommendation.txt
python projetos/06-recommendation/051-maintenance-playbook-video-recommender/main.py --query "vibração em bomba hidráulica rolamento" --save
python -m streamlit run projetos/06-recommendation/051-maintenance-playbook-video-recommender/streamlit_app.py
python -m unittest discover -s tests -p test_recommendation_batch.py -v
```

**Saída:** JSON com IDs, escore ou distância, justificativa e filtros; relatório salvo em `recommendation_batch/reports/51.json` se solicitado. Similaridade lexical é demonstração; qualidade e cobertura de recomendações não foram medidas sobre interações reais.
