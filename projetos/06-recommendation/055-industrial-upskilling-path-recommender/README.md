# #55 — Industrial Upskilling Path Recommender

**Status:** implementado como estudo sintético com código de recomendação executável. Sem acesso a dados corporativos, clientes ou funcionários.

## Escopo realizado
Trilha de treinamento progressiva, respeitando habilidades prévias, dependências entre cursos e limite de horas disponível; cada curso indicado desbloqueia opções posteriores.

**Algoritmo:** Grafo implícito de pré-requisitos; busca gulosa iterativa com orçamento de horas, ranking por lacunas e progressão. A interface interativa usa Streamlit e compartilha o motor auditável.

## Execução
```bash
python -m pip install -r requirements/recommendation.txt
python projetos/06-recommendation/055-industrial-upskilling-path-recommender/main.py --query "python power bi sql" --save
python -m streamlit run projetos/06-recommendation/055-industrial-upskilling-path-recommender/streamlit_app.py
python -m unittest discover -s tests -p test_recommendation_batch.py -v
```

**Proveniência:** [fixtures versionadas](../../../recommendation_batch/fixtures.json) · [regras e testes](../../../recommendation_batch/README.md) · [motor](../../../recommendation_batch/engine.py).

**Limitação:** trilha não certifica proficiência e depende da matriz de pré-requisitos ilustrativa. Não há métricas de impacto real.
