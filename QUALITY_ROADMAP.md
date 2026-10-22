# Plano de maturidade técnica — transparência de evidências

> Lote #071–#080: dez implementações específicas de imagens, OpenCV, OCR Tesseract e treinamentos CNN TensorFlow/PyTorch opcionais; exemplos 100% artificiais. Nada demonstra precisão real em EPI, faces, AGV, metalografia ou produção.

## Entregue nesta branch
- Cinco estudos de caso: OEE auditável, OTIF via SQL, CAPEX Ridge, churn LogisticRegression, demanda rolling-origin; cinco CSVs sintéticos com gerador determinístico, código testável, baselines explícitas e métricas calculadas.
- projetos ainda genéricos identificados como *demonstrações*, com correção dos timestamps ISO/UTC e validação de tamanho de amostra. Não representam implementações das bibliotecas anunciadas.
- Motor F1: validação de timezone, horizontes, drivers e taxa DNF; Monte Carlo Plackett–Luce gera somas coerentes de vitória/pódio/pontos, **condicionais à classificação**, sem simular DNF; análise de contribuições é heurística, **não SHAP**.
- Estratégias de parada restringidas a voltas possíveis e parâmetros válidos.
- Publicação de estudos de caso navegáveis com dados e figura reais (de dados sintéticos), independentes de JavaScript.

## Lote #071–#080 (branch dedicada)
- Funções reais de visão computacional sobre cenas renderizadas, testes de regras, relatórios e PNGs rastreáveis, treinamento CPU em TensorFlow/PyTorch de modelos locais sem transferência de pesos.
- Pendências: datasets industriais reais autorizados, anotações independentes, mAP/IoU/CER/IDF1, avaliação de robustez, segurança, privacidade e homologação.

## Não entregue — impedem nota 100/100
1. Implementação, teste e avaliação externa dos escopos ainda genéricos ou parciais.
2. Autorização e governança de datasets industriais reais; métricas de impacto e validação externa não podem ser inventadas.
3. MLOps operacional MLflow/Docker/FastAPI e modelos reais CNN/SHAP/LSTM para os protótipos #101–#111 onde anunciados.
4. Testes E2E reais desktop/mobile, CI verde verificado, Lighthouse/WCAG, observabilidade Vercel, scans de dependências e avaliação de recrutadores.
5. Conversão para arquitetura frontend modular, com páginas individuais indexáveis e componentes acessíveis em todos os 111 projetos.

## Aceite
Toda afirmação de tecnologia deve corresponder a código executável e teste; todo resultado deve ter origem, recorte, baseline e limitações. Não usar pontuação de auditoria como substituto de evidência.
