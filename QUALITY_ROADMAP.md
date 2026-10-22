# Plano de maturidade técnica — transparência de evidências

> Atualização #081–#090: dez pipelines BI/finanças específicos, com SQL efetivamente executado, Scikit-learn nos projetos 081/088, DAX e M fornecidos como templates de importação sem execução no Power BI Desktop. Dados, relatórios e KPIs são exclusivamente fictícios.

## Entregue nesta branch
- Cinco estudos de caso: OEE auditável, OTIF via SQL, CAPEX Ridge, churn LogisticRegression, demanda rolling-origin; cinco CSVs sintéticos com gerador determinístico, código testável, baselines explícitas e métricas calculadas.
- projetos ainda genéricos identificados como *demonstrações*, com correção dos timestamps ISO/UTC e validação de tamanho de amostra. Não representam implementações das bibliotecas anunciadas.
- Motor F1: validação de timezone, horizontes, drivers e taxa DNF; Monte Carlo Plackett–Luce gera somas coerentes de vitória/pódio/pontos, **condicionais à classificação**, sem simular DNF; análise de contribuições é heurística, **não SHAP**.
- Estratégias de parada restringidas a voltas possíveis e parâmetros válidos.
- Publicação de estudos de caso navegáveis com dados e figura reais (de dados sintéticos), independentes de JavaScript.

## Evidências do lote #081–#090 (branch de trabalho)
- Dez consultas SQL versionadas e executadas com SQLite; dados em onze tabelas ERP artificiais; cálculos de OEE, LTV, ROI, ABC/RFM, SOX-like, CAPEX, forecast de faturamento, compras e custos.
- Testes de métricas, reconciliação, integridade, temporalidade e regras, painéis Streamlit e templates DAX/Power Query.
- Ainda não entregue: acesso SAP/Ariba, modelo .pbix/.pbip executado, DAX testado em engine Tabular, RLS, auditoria fiscal, homologação financeira, métricas de produção ou impacto comprovado.

## Não entregue — impedem nota 100/100
1. Implementação completa, execução e auditoria específica dos escopos ainda genéricos ou parciais.
2. Autorização e governança de datasets industriais reais; métricas de impacto e validação externa não podem ser inventadas.
3. MLOps operacional MLflow/Docker/FastAPI e modelos reais CNN/SHAP/LSTM para os protótipos #101–#111 onde anunciados.
4. Testes E2E reais desktop/mobile, CI verde verificado, Lighthouse/WCAG, observabilidade Vercel, scans de dependências e avaliação de recrutadores.
5. Conversão para arquitetura frontend modular, com páginas individuais indexáveis e componentes acessíveis em todos os 111 projetos.

## Aceite
Toda afirmação de tecnologia deve corresponder a código executável e teste; todo resultado deve ter origem, recorte, baseline e limitações. Não usar pontuação de auditoria como substituto de evidência.
