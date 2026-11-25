> **Atualização científica (fase 3):** Plackett–Luce ajustado por máxima verossimilhança sobre resultados reais 2022–2024, avaliado em janela crescente nas 46 corridas de 2023–2024. Redução do escore de Brier de 12 % (vitória) e 15 % (pódio) sobre o método anterior de temperatura fixa, com IC 95 % por reamostragem de corridas; diagramas de confiabilidade, ECE e teste de Spiegelhalter. Código em [`race_strategy/ranking.py`](../../../race_strategy/ranking.py), método em [docs/physics/ESTIMATION.md](../../../docs/physics/ESTIMATION.md).

> **Estado auditado #111: protótipo matemático/numérico com entradas sintéticas, não um produto homologado.** Nomes de modelos, ferramentas, APIs, CV/RAG ou métricas no benchmark só indicam inspiração; **não demonstram** execução de terceiros (MLflow, TensorFlow, SHAP, CNN, serviços REST ou treino LSTM) sem código/imports, datasets e testes correspondentes. Não atribuir dados ou indicadores à F1 real.

> **Motor de ranking revisado:** simulação Plackett–Luce condicional à classificação; SHAP não é executado e contribuições são heurísticas.

# Project #111 — F1 Predictive Intelligence Platform (F1-PIP)

Full-stack Formula 1 Predictive Intelligence Platform with Walk-Forward ML, Clean Air Race Pace, UTC Weather, Strategy Simulator, and 100k Monte Carlo Engine.
