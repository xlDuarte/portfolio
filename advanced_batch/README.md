# Advanced Industrial Systems #091–#100 — Executable Synthetic End-to-End Lab

**This is a runnable developer prototype, not a production industrial platform.** All events are deterministic synthetic records. There is NO SAP/Ariba/IIoT data feed, authenticated user management, publicly secure API, real MES commands, hiring automation, maintenance work orders, certified quality alarms, running Power BI semantic model, or production-scale Kafka guarantee.

## Ten domain-specific systems

| ID | Implemented workflow | Actual algorithm or system |
|---|---|---|
| 091 | Vendor governance and risk | Weighted OTIF, QA, approval/document criteria |
| 092 | Incremental transaction and OT anomaly queue | Scikit-learn IsolationForest with chronological split |
| 093 | Fictional project-to-skills matching | Set coverage, project clearance and available hours (NOT hiring) |
| 094 | Stock and industrial S&OP | Ridge demand forecast 12-week holdout, 6-week outlook, reorder point |
| 095 | Fictional B2B contract attrition | LogisticRegression, disjoint train/test, test ROC-AUC/F1 |
| 096 | MES setup suggestion | RPM/feed min/max constraints, NO equipment actuation |
| 097 | Remaining Useful Life forecast | RandomForestRegressor fitted on synthetic asset observations |
| 098 | Engineering, contract, invoice text taxonomy | Scikit-learn TF-IDF + LogisticRegression on synthetic text (NOT PDFs) |
| 099 | Quality/safety command center | Threshold alarms on synthetic device events, NO shutdown |
| 100 | SQL-backed cross-line industrial KPI engine | SQLite JSON1 and weighted OEE/revenue SQL aggregation |

## Local use

```bash
python -m pip install -r requirements-advanced.txt
python -m unittest discover -s tests -p test_advanced_batch.py -v
python -m advanced_batch.engine 92 --save
python -m advanced_batch.engine 100 --save
python -m advanced_batch.export_bi --output advanced_batch/reports/synthetic_bi.csv
uvicorn advanced_batch.api:app --host 127.0.0.1 --port 8000
# In a second terminal:
python -m streamlit run advanced_batch/app.py
```

API: GET /health and /v1/projects; POST /v1/projects/{id}/simulate?count=96; POST /v1/projects/{id}/ingest; GET /v1/projects/{id}/events; GET /v1/projects/{id}/analytics.

Events are enveloped with schema_version=1, event_id, project_id, sequence, occurred_at (offset-aware ISO), payload, origin SYNTHETIC. SQLite stores them with unique identity, duplicate redelivery protection and transaction atomicity. At least 24 records are required before the API runs analytics. Events are not permanently emitted to a remote system by the engine CLI.

## Real Kafka + Docker option

Start a locally isolated developer broker:

```bash
docker compose -f advanced_batch/compose.yaml up -d --build redpanda api
python -m advanced_batch.kafka_bus publish --project 91 --count 96
python -m advanced_batch.kafka_bus consume --count 96 --db advanced_batch/reports/kafka_demo.sqlite3
```

Kafka broker is **Redpanda** (Kafka protocol-compatible). The producer uses KafkaProducer, waits for broker acknowledgements, and the consumer commits offsets only AFTER durable SQLite insertion. Kafka is not an enterprise OT ingestion system here. Explicit CI broker integration must pass before claiming Kafka verified; publishing to a fake in-memory queue does not count. The containerized API is only bound to localhost at port 8000. The Docker image is a development demo, and Redis, monitoring, TLS, authentication, authorization, secrets policies and production rollout are not supplied.

## Business intelligence export

Running `python -m advanced_batch.export_bi` emits typed CSV columns for the fictitious project #100 shift events. The Power Query M and DAX files in powerbi/ may be **manually** imported in Power BI Desktop; they are not evaluated in Desktop/Tabular or packaged into .pbix/.pbip. True Power BI deployment and security are missing.

## Tests and constraints

Core tests validate 10 domain outcomes, synthetic fixture determinism, schema rejection, replay deduplication, data conflict checks, real FastAPI TestClient roundtrip, SQL JSON1 metrics, ML training on synthetic labels, and source files / CLI / pages. The optional Kafka integration test is tagged with RUN_ADVANCED_KAFKA=1 and requires a live Redpanda listener. Accuracy estimates are measured against **generated labels**, not measured industrial outcomes. Models have not undergone independent benchmarking, drift detection, security reviews, model cards for real users, manual labeling, external QA or engineering approval.

Do not use these prototypes for procurement approval, employee hiring/rejection, automated safety enforcement, operational control, financial credit decisions or preventive maintenance scheduling without consent, evaluation and human oversight.
