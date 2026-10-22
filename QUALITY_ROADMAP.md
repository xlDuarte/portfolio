# Plano de maturidade técnica — transparência de evidências

## Entregas comprováveis por lote nesta linha de desenvolvimento
- Cinco estudos de caso iniciais: OEE, OTIF, CAPEX, churn e previsão de demanda, com dados sintéticos e métricas calculadas.
- Nove regressões especializadas #022–#030 com modelos realmente ajustados. Atenção: métricas de referência XGBoost podem variar entre versões, exigindo identificação do ambiente e reexecução.
- Dez projetos NLP #041–#050 com código real de classificação textual, consistência de evidências fornecidas, scanner textual de governança e sumarização **extrativa**. Modelos treinados apenas em frases geradas artificialmente; ferramentas não executam verificação jurídica, seleção de pessoas ou medidas de segurança automatizadas.
- Projetos ainda não convertidos continuam protótipos; não reutilizar os antigos totais de "95 demonstrações" após entregas subsequentes. A homologação geral exige auditoria por arquivo e relatório CI.
- Motor F1: validação de timezone, horizontes, drivers e taxa DNF; Monte Carlo Plackett–Luce gera somas coerentes de vitória/pódio/pontos, **condicionais à classificação**, sem simular DNF; análise de contribuições é heurística, **não SHAP**.
- Estratégias de parada restringidas a voltas possíveis e parâmetros válidos.
- Publicação de estudos de caso navegáveis com dados e figura reais (de dados sintéticos), independentes de JavaScript.

## Não entregue — impedem nota 100/100
1. Implementação individual, testável e auditável de todos os escopos ainda genéricos ou parcialmente implementados.
2. Autorização e governança de datasets industriais reais; métricas de impacto e validação externa não podem ser inventadas.
3. MLOps operacional MLflow/Docker/FastAPI e modelos reais CNN/SHAP/LSTM para os protótipos #101–#111 onde anunciados.
4. Testes E2E reais desktop/mobile, CI verde verificado, Lighthouse/WCAG, observabilidade Vercel, scans de dependências e avaliação de recrutadores.
5. Conversão para arquitetura frontend modular, com páginas individuais indexáveis e componentes acessíveis em todos os 111 projetos.

## Aceite
Toda afirmação de tecnologia deve corresponder a código executável e teste; todo resultado deve ter origem, recorte, baseline e limitações. Não usar pontuação de auditoria como substituto de evidência.
