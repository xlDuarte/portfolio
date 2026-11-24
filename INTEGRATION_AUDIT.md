# Auditoria integrada do portfólio — 111 projetos

**Situação atual (22/10/2026):** A integração está **na branch `main`**, no commit `868191141992996ca1190c853aabc54f80778c16`, que incorporou os oito lotes #031–#110 e preservou #001–#030 e #111. Os PRs originais #6–#14 foram fechados sem merge individual porque o conteúdo foi consolidado diretamente. Esta auditoria complementar confere inventário, evidências e declarações tecnológicas individualizadas; não reproduz validação de campo.

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

**Evidência GitHub Actions na `main`:** o job `verify` da execução [39789049369](https://github.com/xlDuarte/portfolio/actions/runs/39789049369) **passou**. Os oito workflows especializados (classificação, NLP, recomendações, séries temporais, visão, BI, avançado e motorsport) também **passaram** no mesmo commit. O job de publicação Pages falhou porque o GitHub Pages não estava habilitado/configurado: `actions/configure-pages@v5` retornou HTTP 404. Isso **não é falha de testes de Python** e não significa que o site foi publicado. A branch de correção isola a verificação do código da publicação e registra um aviso quando Pages está desabilitado. Testes globais requerem `requirements/integration.txt`; frameworks pesados continuam isolados.

A matriz `TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv` passa a distinguir **tecnologias de fato utilizadas em cada projeto #081–#110**, em vez de atribuir toda a stack do domínio a cada entrada. A verificação automatizada `python scripts/audit_integrated_portfolio.py --check` cobre 111 entrypoints, 111 linhas de evidência e lacunas, oito módulos especializados e seus índices web. São **testes estruturais**, não benchmark externo. Consultar `QUALITY_ROADMAP.md` para pendências e `site/cases/` para casos.
