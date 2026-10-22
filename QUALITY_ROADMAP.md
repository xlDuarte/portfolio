# Plano de maturidade técnica — transparência de evidências

> Atualização do lote #051–#060: dez recomendadores executáveis com fixtures sintéticas, integrações não presentes, testes de invariantes, UI Streamlit e páginas individuais. PRs de outros lotes podem permanecer abertos; não inferir que estejam integrados na main.

## Entregue nesta branch
- Cinco estudos de caso: OEE auditável, OTIF via SQL, CAPEX Ridge, churn LogisticRegression, demanda rolling-origin; cinco CSVs sintéticos com gerador determinístico, código testável, baselines explícitas e métricas calculadas.
- projetos ainda genéricos identificados como *demonstrações*, com correção dos timestamps ISO/UTC e validação de tamanho de amostra. Não representam implementações das bibliotecas anunciadas.
- Motor F1: validação de timezone, horizontes, drivers e taxa DNF; Monte Carlo Plackett–Luce gera somas coerentes de vitória/pódio/pontos, **condicionais à classificação**, sem simular DNF; análise de contribuições é heurística, **não SHAP**.
- Estratégias de parada restringidas a voltas possíveis e parâmetros válidos.
- Publicação de estudos de caso navegáveis com dados e figura reais (de dados sintéticos), independentes de JavaScript.

## Entrega do lote #051–#060 (branch de trabalho)
- Motores de similaridade TF-IDF, busca por assinatura acústica FFT, regras de elegibilidade, pré-requisitos de aprendizagem, cobertura de competências fictícias, feed sintético, fornecedores qualificados fictícios, grafo logístico hipotético e BOM recursivo, testados com fixtures artificiais.
- Interface Streamlit em dez entrypoints e 11 páginas de portfólio; testes de regras com CI próprio.
- Pendência: nenhum NDCG@K offline anotado por especialistas, impacto industrial mensurado ou homologação de ERP, logística e RH.

## Não entregue — impedem nota 100/100
1. Implementação integral individual das funcionalidades ainda genéricas ou parciais, com aceitação específica por projeto.
2. Autorização e governança de datasets industriais reais; métricas de impacto e validação externa não podem ser inventadas.
3. MLOps operacional MLflow/Docker/FastAPI e modelos reais CNN/SHAP/LSTM para os protótipos #101–#111 onde anunciados.
4. Testes E2E reais desktop/mobile, CI verde verificado, Lighthouse/WCAG, observabilidade Vercel, scans de dependências e avaliação de recrutadores.
5. Conversão para arquitetura frontend modular, com páginas individuais indexáveis e componentes acessíveis em todos os 111 projetos.

## Aceite
Toda afirmação de tecnologia deve corresponder a código executável e teste; todo resultado deve ter origem, recorte, baseline e limitações. Não usar pontuação de auditoria como substituto de evidência.
