# #59 — Optimal Logistics Route and Carrier Engine

**Status:** pipeline real e reproduzível exclusivamente com dados fictícios. Sem integração com sistemas externos.

## Funcionalidade entregue
Motor de rotas em grafo dirigido artificial: enumera caminhos simples entre cidades, exclui transportadores não homologados e compara custos, horas e emissões hipotéticos.

**Tecnologia:** Algoritmo de busca em grafo com enumeração de caminhos simples e objetivo multicritério, com valores numéricos sintéticos. Interface Streamlit disponível.

## Reproduzir
```bash
python -m pip install -r requirements-recommendation.txt
python projetos/06-recommendation/059-optimal-logistics-route-carrier-engine/main.py --query "Pindamonhangaba>Santos" --save
python -m streamlit run projetos/06-recommendation/059-optimal-logistics-route-carrier-engine/streamlit_app.py
python -m unittest discover -s tests -p test_recommendation_batch.py -v
```

**Códigos e dados:** [motor](../../../recommendation_batch/engine.py), [fixtures](../../../recommendation_batch/fixtures.json), [documentação](../../../recommendation_batch/README.md).

**Limitações:** tempo, distância e CO2 são hipóteses inventadas; não há mapa ou serviço de roteirização externa, tráfego real ou capacidade dos modais. Nenhum resultado operacional é reivindicado.
