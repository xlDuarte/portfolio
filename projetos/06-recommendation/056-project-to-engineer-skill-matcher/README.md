# #56 — Project to Engineer Skill Matcher

**Status:** implementado como estudo sintético com código de recomendação executável. Sem acesso a dados corporativos, clientes ou funcionários.

## Escopo realizado
Correspondência transparente entre competências solicitadas e perfis profissionais inteiramente fictícios, com controle de disponibilidade e autorização; nenhuma seleção de pessoas reais.

**Algoritmo:** Pandas/NumPy para representação de competências e ordenação determinística por cobertura e horas disponíveis. A interface interativa usa Streamlit e compartilha o motor auditável.

## Execução
```bash
python -m pip install -r requirements-recommendation.txt
python projetos/06-recommendation/056-project-to-engineer-skill-matcher/main.py --query "python sql industrial data" --save
python -m streamlit run projetos/06-recommendation/056-project-to-engineer-skill-matcher/streamlit_app.py
python -m unittest discover -s tests -p test_recommendation_batch.py -v
```

**Proveniência:** [fixtures versionadas](../../../recommendation_batch/fixtures.json) · [regras e testes](../../../recommendation_batch/README.md) · [motor](../../../recommendation_batch/engine.py).

**Limitação:** não permite inferência de empregabilidade nem decisões de RH; perfis são inteiramente inventados. Não há métricas de impacto real.
