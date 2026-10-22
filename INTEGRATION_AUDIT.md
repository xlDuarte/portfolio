# Auditoria integrada do portfólio — 111 projetos

**Origem:** GitHub `xlDuarte/portfolio`, branch `integration-111-projects-audit`; a base é `main`. Foram reconciliados oito lotes incrementais de #031 a #110 com 349 objetos Git específicos. Os dez entrypoints de classificação antes genéricos agora treinam os classificadores corretos.

## Critérios

| Aspecto | Evidência encontrada | Limitação |
|---|---|---|
| Inventário | 111 programas canônicos numerados 001–111 | Existência do arquivo não certifica escopo |
| Analytics #001–#030 | Nove funções específicas de analytics_batch1 em #001–#009, supply #010, EDA #011–#020 e regressão #021–#030 com testes na main | Não auditados contra dados corporativos reais |
| Classificação #031–#040 | Scikit-learn real, split 60/20/20, threshold via calibração | Fórmulas e rótulos sintéticos |
| NLP #041–#050 | Pipeline local, spaCy/NLTK/tokenizers/Scikit-learn conforme cada caso | Sem pesos Transformer baixados ou inferência LLM |
| Recomendação #051–#060 | Projetos e testes próprios importados | Sem relevância comercial externa |
| Forecasting #061–#070 | Statsmodels/Prophet e backtesting temporais | Sem observações industriais externas |
| Visão #071–#080 | OpenCV/Tesseract, CNN TensorFlow/PyTorch por opção `--deep` | Não há câmera, processo ou exame real |
| BI #081–#090 | SQL SQLite executado, Scikit-learn e painéis Streamlit | **Power BI DAX/M são templates, não runtime validado** |
| Avançado #091–#100 | FastAPI/SQLite/Kafka producer/consumer e CI de Redpanda | Não é implantação industrial segura |
| Motorsport #101–#110 | XGBoost/RF, EKF, OpenCV, TF LSTM/CNN, Grad-CAM, MLflow, LangChain PDFs e SMOTE/SHAP | Sem dados reais de F1, GPS, FLIR ou ChassisSim |
| F1 Predictive Intelligence #111 | Engenharia walk-forward heurística e monte carlo condicional | **Catálogo de modelos previsto não implementado** |

## Resultado

Os pipelines citados são executáveis com **dados synthetic** em ambientes de teste; execução de simuladores não prova efeitos reais. DAX não foi executado no Power BI Desktop, SAP não foi conectado, F1 não forneceu telemetria licenciada, e **o portfólio não é 100/100**.

Esta branch é uma proposta de integração e revisão, **não** um merge automático dos nove PRs anteriores. Testes globais dependem de instalação explícita em `requirements-integration.txt`; trabalhos pesados com TensorFlow/PyTorch/MLflow continuam isolados em workflows específicos.

Ver `TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv` para escopo por cada ID, `QUALITY_ROADMAP.md` para lacunas, e as páginas `site/cases/` para documentação por lote.
