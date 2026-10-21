# Lote 021–030 — Regressão realmente treinada

Projetos #022–#030: códigos `main.py` próprios, variáveis de domínio próprias, datasets artificiais independentes versionados (`regression_batch/data/*.csv`), 9 modelos XGBRegressor efetivamente treinados (com baselines Ridge e DummyRegressor), separação treino/calibração/teste, intervalos conformal-style, relatórios de métricas calculadas, CSV de predição de teste, SVG de diagnóstico Matplotlib, notebooks executáveis e HTML individuais.

Projeto #021: implementação anterior de Ridge e XGBoost preservada; adicionada página de estudo de caso.

**Evidências exigidas:** executar `python -m unittest discover -s tests -v`; `python -m regression_batch.engine 22 --save`; `python projetos/03-regression/022-fleet-vehicle-residual-value-model/main.py`.

**Limites:** todos os datasets são sintéticos, sem validação financeira/industrial real, sem modelos implantados nem impacto empresarial medido. No caso #027, há dependência explícita de observações históricas defasadas, verificadas contra a série original. Para #029–#030, variáveis são do planejamento/partida, não do futuro realizado.

**Pendente:** validação browser E2E, bibliotecas adicionais não anunciadas nessa categoria e demais lotes #031–#111.
