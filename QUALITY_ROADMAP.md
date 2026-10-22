# Roadmap técnico — auditoria integrada de 111 projetos

## Reconciliação já incorporada à `main`

O commit `868191141992996ca1190c853aabc54f80778c16` consolidou na `main` os oito lotes #031–#110, preservando os projetos #001–#030 e #111. A integração conciliou **349 objetos Git específicos**, código de entrada canônico, páginas, documentação e testes compartilhados. Os PRs #6–#14 foram encerrados sem merge individual por terem sido substituídos pela árvore consolidada.

| Escopo | Evidência | Estado |
|---|---|---|
| #001–#030 | `analytics_batch1`, `case_studies`, `analytics_eda`, `regression_batch`: testes específicos de domínio presentes | Demonstrativos testados, sem homologação externa |
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
6. Auditoria de mudanças futuras na árvore `main`; os PRs #6–#14 já foram encerrados e substituídos pela consolidação. Os **testes da árvore `main` passaram**, mas nenhuma validação real foi demonstrada.
7. Auditoria de performance frontend, WCAG/Lighthouse, segurança dos containers, atualização de dependências e cobertura E2E de interface.
8. **Publicação do site:** configurar GitHub Pages em *Settings → Pages → Build and deployment → GitHub Actions*. O job de verificação passou, mas o deploy da execução `39789049369` falhou com HTTP 404 (Pages não configurado). O workflow corrigido em branch separada sinaliza a ausência de Pages e não declara publicação concluída.
9. Expandir a auditoria específica de tecnologia para os casos #001–#080, com execução de cada stack anunciada e evidência de imports, runtime e artefatos; os dados seguem sintéticos.

**Regra de aceite:** uma tecnologia é validada somente quando há código, teste executado, evidência reproduzível e limites declarados. Esta integração não recebe nota 100/100.
