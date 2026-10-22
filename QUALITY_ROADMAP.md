# Plano de maturidade técnica — transparência de evidências

> Lote #091–#100 implementado em branch: eventos sintéticos reais como código (API FastAPI, SQL SQLite, Scikit-learn, Streamlit, Kafka producer/consumer e Docker Redpanda), testes de transporte real de broker dedicados. Não equivale a integração industrial autorizada nem produção segura.

## Entregue nesta branch
- Cinco estudos de caso: OEE auditável, OTIF via SQL, CAPEX Ridge, churn LogisticRegression, demanda rolling-origin; cinco CSVs sintéticos com gerador determinístico, código testável, baselines explícitas e métricas calculadas.
- projetos ainda genéricos identificados como *demonstrações*, com correção dos timestamps ISO/UTC e validação de tamanho de amostra. Não representam implementações das bibliotecas anunciadas.
- Motor F1: validação de timezone, horizontes, drivers e taxa DNF; Monte Carlo Plackett–Luce gera somas coerentes de vitória/pódio/pontos, **condicionais à classificação**, sem simular DNF; análise de contribuições é heurística, **não SHAP**.
- Estratégias de parada restringidas a voltas possíveis e parâmetros válidos.
- Publicação de estudos de caso navegáveis com dados e figura reais (de dados sintéticos), independentes de JavaScript.

## Lote #091–#100: evidências e lacunas
- Dez pipelines de domínio com geração de eventos artificiais, ETL idempotente, FastAPI real, Scikit-learn, SQLite JSON1 e painel Streamlit.
- Adaptador Kafka producer/consumer com acknowledgements e commit pós-persistência; Dockerfile e compose para testes locais com Redpanda, incluindo CI de broker.
- Ainda falta: credenciais SAP/OT autorizadas, TLS, autenticação, autorização granular, modelo de segurança, produção 24×7, ML drift real, Power BI Tabular executado e validação com eventos industriais reais.

## Não entregue — impedem nota 100/100
1. Implementação, execução e validação externa dos escopos ainda genéricos ou parciais.
2. Autorização e governança de datasets industriais reais; métricas de impacto e validação externa não podem ser inventadas.
3. MLOps operacional MLflow/Docker/FastAPI e modelos reais CNN/SHAP/LSTM para os protótipos #101–#111 onde anunciados.
4. Testes E2E reais desktop/mobile, CI verde verificado, Lighthouse/WCAG, observabilidade Vercel, scans de dependências e avaliação de recrutadores.
5. Conversão para arquitetura frontend modular, com páginas individuais indexáveis e componentes acessíveis em todos os 111 projetos.

## Aceite
Toda afirmação de tecnologia deve corresponder a código executável e teste; todo resultado deve ter origem, recorte, baseline e limitações. Não usar pontuação de auditoria como substituto de evidência.
