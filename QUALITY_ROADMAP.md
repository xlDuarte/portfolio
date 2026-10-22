# Roadmap técnico — auditoria integrada de 111 projetos

## Reconciliação nesta branch

A branch de integração parte da `main` e incorpora **349 objetos de arquivo especializados** dos oito lotes #031–#110, sem sobrescrever automaticamente os seis arquivos compartilhados. Entrypoints, páginas e READMEs #031–#040 foram corrigidos; `README.md`, navegação `site/index.html`, workflow global e suites de testes foram compostos manualmente.

| Escopo | Evidência | Estado |
|---|---|---|
| #001–#030 | Código original na `main`; testes específicos de análise e regressão existentes | Preservado; sem homologação externa |
| #031–#040 | `classification_batch`, dez `main.py` corretos, train/cal/test, Scikit-learn | Demonstrativo, rótulos sintéticos |
| #041–#050 | `nlp_batch`, treino de texto e NLP local | Demonstrativo; nenhum LLM treinado |
| #051–#060 | `recommendation_batch`, algoritmos por caso | Demonstrativo; sem engajamento real |
| #061–#070 | `timeseries_batch`, backtesting temporal, Prophet/Statsmodels | Demonstrativo; séries geradas |
| #071–#080 | `vision_batch`, OpenCV/Tesseract, CNN opcional real | Demonstrativo; imagens artificiais |
| #081–#090 | `business_batch`, SQLite/Scikit-learn/Streamlit, DAX/M de importação | DAX NÃO executado em Power BI Desktop |
| #091–#100 | `advanced_batch`, FastAPI/SQLite, Kafka + Redpanda, Scikit-learn | Broker testado em CI de lote; sem SAP/OT de campo |
| #101–#110 | `motorsport_batch`, XGB, TF LSTM/CNN, Grad-CAM, MLflow, PDF LangChain e SHAP | Simulação sintética; sem F1 GPS/FLIR/ChassisSim reais |
| #111 | `f1-predictive-intelligence`, probabilidade heurística/walk-forward parcial | **Incompleto** para catálogo de modelos anunciado |

## Pendências impeditivas de 100/100

1. Dados reais/licenciados e avaliação externa de cada caso, com validação por especialista e replicabilidade independente.
2. `#111`: treinamento/evidência para o catálogo de modelos anunciado, modelo real da corrida além das probabilidades condicionadas à classificação, validação do produto end-to-end.
3. Arquivos Power BI (.pbip/.pbix) e DAX testado por Tabular Engine; credenciais oficiais SAP/Ariba/MES/OT; integração de produção e autorização.
4. CNNs com imagens reais anotadas, desempenho NDT/visão e telemetria oficial; validação de segurança e privacidade.
5. RAG com avaliação relevante, autenticação, isolamento de clientes e referências de documentação corporativa autorizada.
6. Diagnóstico técnico e merge/revisão dos PRs #6–#14. A existência de CI verde em branches separadas não certifica a árvore integrada.
7. Auditoria de performance frontend, WCAG/Lighthouse, segurança dos containers, atualização de dependências e cobertura E2E de interface.

**Regra de aceite:** uma tecnologia é validada somente quando há código, teste executado, evidência reproduzível e limites declarados. Esta integração não recebe nota 100/100.
