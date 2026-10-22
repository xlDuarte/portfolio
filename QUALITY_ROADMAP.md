# Plano de maturidade técnica — transparência de evidências

> Lote #101–#110: simulações físicas originais preservadas; modelos XGBoost/RF, TensorFlow LSTM/CNN Grad-CAM, MLflow/FastAPI, LangChain PDF retrieval e imbalanced-learn/SHAP implementados em código testável. Fonte inteiramente sintética; sem FastF1/GPS/FLIR/ChassisSim real.

## Entregue nesta branch
- Cinco estudos de caso: OEE auditável, OTIF via SQL, CAPEX Ridge, churn LogisticRegression, demanda rolling-origin; cinco CSVs sintéticos com gerador determinístico, código testável, baselines explícitas e métricas calculadas.
- projetos ainda genéricos identificados como *demonstrações*, com correção dos timestamps ISO/UTC e validação de tamanho de amostra. Não representam implementações das bibliotecas anunciadas.
- Motor F1: validação de timezone, horizontes, drivers e taxa DNF; Monte Carlo Plackett–Luce gera somas coerentes de vitória/pódio/pontos, **condicionais à classificação**, sem simular DNF; análise de contribuições é heurística, **não SHAP**.
- Estratégias de parada restringidas a voltas possíveis e parâmetros válidos.
- Publicação de estudos de caso navegáveis com dados e figura reais (de dados sintéticos), independentes de JavaScript.

## Entregas e lacunas #101–#110
- Simulações matemáticas preservadas; inferência em datasets artificiais com testes de holdout, Grad-CAM TensorFlow, MLflow Tracking, PDF parsing LangChain, SHAP e SMOTE de treino.
- Pendências: dados de corrida reais/licenciados, identificação dos parâmetros físicos com testes, integração FastF1, DRS/track geometry oficial, termografia real, solução ChassisSim proprietária, QA independente, performance em hardware e segurança API de produção.

## Não entregue — impedem nota 100/100
1. Validação e implementação por projeto com benchmarks reais somente após homologação externa.
2. Autorização e governança de datasets industriais reais; métricas de impacto e validação externa não podem ser inventadas.
3. MLOps operacional MLflow/Docker/FastAPI e modelos reais CNN/SHAP/LSTM para os protótipos #101–#111 onde anunciados.
4. Testes E2E reais desktop/mobile, CI verde verificado, Lighthouse/WCAG, observabilidade Vercel, scans de dependências e avaliação de recrutadores.
5. Conversão para arquitetura frontend modular, com páginas individuais indexáveis e componentes acessíveis em todos os 111 projetos.

## Aceite
Toda afirmação de tecnologia deve corresponder a código executável e teste; todo resultado deve ter origem, recorte, baseline e limitações. Não usar pontuação de auditoria como substituto de evidência.
