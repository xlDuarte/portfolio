# Plano de maturidade técnica — transparência de evidências

## Entregue nesta branch
- Cinco estudos de caso: OEE auditável, OTIF via SQL, CAPEX Ridge, churn LogisticRegression, demanda rolling-origin; cinco CSVs sintéticos com gerador determinístico, código testável, baselines explícitas e métricas calculadas.
- 95 projetos restantes explicitamente identificados como *demonstrações*, com correção dos timestamps ISO/UTC e validação de tamanho de amostra. Não representam implementações das bibliotecas anunciadas.
- Motor F1: validação de timezone, horizontes, drivers e taxa DNF; Monte Carlo Plackett–Luce gera somas coerentes de vitória/pódio/pontos, **condicionais à classificação**, sem simular DNF; análise de contribuições é heurística, **não SHAP**.
- Estratégias de parada restringidas a voltas possíveis e parâmetros válidos.
- Publicação de estudos de caso navegáveis com dados e figura reais (de dados sintéticos), independentes de JavaScript.

## Não entregue — impedem nota 100/100
1. Implementação integral individual das funcionalidades anunciadas nos 95 protótipos remanescentes.
2. Autorização e governança de datasets industriais reais; métricas de impacto e validação externa não podem ser inventadas.
3. MLOps operacional MLflow/Docker/FastAPI e modelos reais CNN/SHAP/LSTM para os protótipos #101–#111 onde anunciados.
4. Testes E2E reais desktop/mobile, CI verde verificado, Lighthouse/WCAG, observabilidade Vercel, scans de dependências e avaliação de recrutadores.
5. Conversão para arquitetura frontend modular, com páginas individuais indexáveis e componentes acessíveis em todos os 111 projetos.

## Aceite
Toda afirmação de tecnologia deve corresponder a código executável e teste; todo resultado deve ter origem, recorte, baseline e limitações. Não usar pontuação de auditoria como substituto de evidência.
