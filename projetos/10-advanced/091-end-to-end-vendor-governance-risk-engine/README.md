# #91 — Vendor Governance & Risk Engine

**Status:** processamento real em Python sobre eventos exclusivamente **SINTÉTICOS**; código de demonstração, não solução industrial homologada.

## Escopo executado
Avaliação de fornecedores, aprovações e risco auditável. O motor entrega geração de eventos tipados, validação, armazenamento SQLite transacional, processamento por domínio, métricas em JSON e endpoints de API FastAPI. Os classificadores/estimadores aplicáveis ajustam Scikit-learn de fato e produzem resultados de amostras não utilizadas no ajuste.

**Stack funcional:** Python, NumPy, Pandas, Scikit-learn, SQLite, FastAPI, Streamlit, Docker e Kafka via `advanced_batch.kafka_bus` **quando um broker é iniciado e acessível**. A disponibilidade do broker não é presumida; o teste de CI separado a verifica. Arquivos Power BI M/DAX existem para importação manual, sem execução de motor DAX.

## Reprodução
```bash
python -m pip install -r requirements-advanced.txt
python projetos/10-advanced/091-end-to-end-vendor-governance-risk-engine/main.py --save
python -m unittest discover -s tests -p test_advanced_batch.py -v
uvicorn advanced_batch.api:app --host 127.0.0.1 --port 8000
# Outro terminal: python -m streamlit run advanced_batch/app.py
```

Para transporte real (ambiente local), subir `docker compose -f advanced_batch/compose.yaml up -d redpanda` e depois `python -m advanced_batch.kafka_bus publish --project 91 --count 96` / `python -m advanced_batch.kafka_bus consume --count 96`.

**Referências:** [motor](../../../advanced_batch/engine.py), [API](../../../advanced_batch/api.py), [broker](../../../advanced_batch/kafka_bus.py), [protocolo e segurança](../../../advanced_batch/README.md).

## Limitações
Não valida fornecedores reais, certificações, risco de crédito ou transações. Não existe integração SAP, OT, MES ou produção; segurança, auditoria, RLS, autenticação e métricas reais estão fora do escopo.
