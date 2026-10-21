# Relatório de implantação — Quality Upgrade (branch de revisão)

**Emissão:** 21/10/2026. **Modo:** alterações em branch isolada; produção não alterada até homologação.

## Entregas mensuráveis

- 111 entradas `main.py` mantidas; execução básica: **111/111** na rodada isolada com threads BLAS limitadas.
- 12 testes de regressão e validação numérica locais: **12 aprovados**.
- 116 arquivos Python passaram por compilação no ambiente local.
- 5 entrypoints HTML: scripts inline passaram no `node --check`.
- **5 implementações analíticas**, com datasets CSV sintéticos versionados, código Pandas/Scikit-learn, consultas SQLite, modelo baseline, artefatos de métricas JSON, gráficos SVG e estudos de caso estáticos.
- **95 demonstrações genéricas** com disclaimers individuais; 11 protótipos F1/Motorsport com limitações explicitadas.
- Prova de conceito F1 corrigida: somas condicionais do simulador de ranking = 1 vitória, 3 pódios, 10 pontuações por corrida de 20 pilotos; probabilidades não calibradas em dados F1 históricos; **contribuições heurísticas NÃO são SHAP**.
- Validações de entrada: timestamps ISO com timezone, dimensão de amostras, parâmetros de pit stop, duplicatas e horizontes.

## Indicadores dos estudos — EXCLUSIVAMENTE SINTÉTICOS

| Caso | Medida apurada em dados gerados | Baseline / observação |
|---|---|---|
| OEE | 77.46% | OEE ponderado pelo tempo programado |
| OTIF | 40.71% | Cumprimento simultâneo prazo e quantidade |
| CAPEX Ridge | MAE BRL 75,359.6 | Baseline MAE BRL 405,962.23 |
| Churn B2B | ROC-AUC 0.812; Brier 0.1443 | Baseline Brier 0.1937 |
| Previsão demanda | MAE 10.27 | Baseline persistência 12.72 |

**Alerta:** estas métricas são calculadas em dados artificialmente gerados, não comprovam aplicabilidade real, generalização ou resultados econômicos.

## Verificações pendentes — impedem nota 100/100

1. 95 projetos não implementam a funcionalidade anunciada pelo título; estão identificados honestamente como demonstrações até sua reconstrução individual.
2. Acurácia e retorno de negócio em dados reais não podem ser confirmados sem fontes legítimas, consentimento, governança e histórico temporal.
3. No motor F1, não há treino de modelos XGBoost/LightGBM/CatBoost, nem calibração com temporadas observadas, nem tratamento da classificação envolvendo DNF na mesma simulação.
4. O HTML legado contém sistema extenso de demonstração; acessibilidade WCAG, performance Lighthouse e fluxos de 111 rotas exigem testes E2E reais desktop/mobile.
5. GitHub Actions e a Vercel só podem ser considerados homologados após logs reais da execução para o commit desta branch.
6. Repositório está privado, portanto avaliadores sem acesso não podem consultar o código-fonte.

**Conclusão:** avanço substancial e auditável, **não 100/100**. Falhas e limitações não são eliminadas por ajuste arbitrário de score.

- #021: `XGBRegressor` adicional, efetivamente treinado e avaliado em holdout (dados sintéticos), comparado a baseline; não afirma uso de TensorFlow ou Power BI.


## Lote incremental adicional #001–#009 — status posterior

- Nove simuladores genéricos substituídos por análises específicas e testadas.
- Novos artefatos: `analytics_batch1/`, nove notebooks, nove arquivos de dados, nove páginas estáticas com SVG, nove novos README e testes de regressão.
- Os 111 scripts passaram em teste de execução básica após as mudanças. Todos os 9 notebooks executaram localmente via `nbclient`.
- **Power BI não testado** e não está implementado nesses estudos; situação apresentada de forma explícita.
- Relatório detalhado: `BATCH_001_009_REPORT.md`.
