# #58 — Approved Supplier Recommender (Ariba scenario)

**Status:** pipeline real e reproduzível exclusivamente com dados fictícios. Sem integração com sistemas externos.

## Funcionalidade entregue
Pré-qualificação de fornecedores fictícios inspirada em controles Ariba: homologação, certificado, capacidade, OTIF, prazo e preço. Não realiza pedido ou consulta real ao ERP.

**Tecnologia:** Regras de elegibilidade, Pandas para análise de catálogo e ranking matemático ponderado de preço, OTIF e qualidade. Interface Streamlit disponível.

## Reproduzir
```bash
python -m pip install -r requirements/recommendation.txt
python projetos/06-recommendation/058-approved-supplier-recommender-ariba/main.py --query "bearings" --save
python -m streamlit run projetos/06-recommendation/058-approved-supplier-recommender-ariba/streamlit_app.py
python -m unittest discover -s tests -p test_recommendation_batch.py -v
```

**Códigos e dados:** [motor](../../../recommendation_batch/engine.py), [fixtures](../../../recommendation_batch/fixtures.json), [documentação](../../../recommendation_batch/README.md).

**Limitações:** critérios não substituem aprovação real, exigências fiscais, anticorrupção ou compliance de fornecedores. Nenhum resultado operacional é reivindicado.
