# #100 — Industrial BI Data Platform

**Implementação:** Armazenamento SQL e KPIs industriais consultados por API. JSON1 SQLite para métricas BI ponderadas por linha; CSV artificial exportável e templates Power BI não executados.

O motor executa geração de eventos, validação, processamento por projeto e persistência SQLite; a API FastAPI expõe recebimento idempotente e consulta de métricas. Aplicação Streamlit funciona como cliente HTTP da API local. Kafka possui adaptador real com confirmações de broker, sem conectividade implícita.

## Reproduzir
```bash
python -m pip install -r requirements-advanced.txt
python projetos/10-advanced/100-end-to-end-industrial-bi-data-platform/main.py --save
python -m unittest discover -s tests -p test_advanced_batch.py -v
uvicorn advanced_batch.api:app --host 127.0.0.1 --port 8000
```

**Transporte Kafka:** `docker compose -f advanced_batch/compose.yaml up -d redpanda` e `python -m advanced_batch.kafka_bus publish --project 100 --count 96`, seguido de `python -m advanced_batch.kafka_bus consume --count 96`.

**Export BI:** `python -m advanced_batch.export_bi --output advanced_batch/reports/synthetic_bi.csv`. Power Query M/DAX são templates para Power BI Desktop, sem arquivo .pbix ou validação do Tabular Engine.

**Código e método:** [engine.py](../../../advanced_batch/engine.py) · [api.py](../../../advanced_batch/api.py) · [README central](../../../advanced_batch/README.md).

**Restrições:** os dados são sintéticos e não comprovam capacidade de implantação industrial. Sem SAP/ERP real, segurança autenticada em produção, CI/CD de serviço público, workflow de incidentes operacionais ou resultados reais.
