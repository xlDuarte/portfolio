# #57 — Industrial Market Intelligence Feed

**Status:** pipeline real e reproduzível exclusivamente com dados fictícios. Sem integração com sistemas externos.

## Funcionalidade entregue
Feed de inteligência industrial baseado em notícias fictícias versionadas, com ranking TF-IDF e ponderação por recência; não pesquisa notícias reais.

**Tecnologia:** Pandas e Scikit-learn TF-IDF/cosine_similarity, score de recência via NumPy. Interface Streamlit disponível.

## Reproduzir
```bash
python -m pip install -r requirements/recommendation.txt
python projetos/06-recommendation/057-industrial-market-intelligence-feed/main.py --query "steel logistics energy" --save
python -m streamlit run projetos/06-recommendation/057-industrial-market-intelligence-feed/streamlit_app.py
python -m unittest discover -s tests -p test_recommendation_batch.py -v
```

**Códigos e dados:** [motor](../../../recommendation_batch/engine.py), [fixtures](../../../recommendation_batch/fixtures.json), [documentação](../../../recommendation_batch/README.md).

**Limitações:** itens não foram publicados por veículos reais; não representam inteligência de mercado atual. Nenhum resultado operacional é reivindicado.
