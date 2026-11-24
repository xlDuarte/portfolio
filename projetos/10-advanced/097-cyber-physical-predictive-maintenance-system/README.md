# #97 — Cyber-Physical Predictive Maintenance

**Implementação:** Estimativa de vida útil remanescente com regressão supervisionada. Regressão RandomForest de RUL simulado, sem manutenção automática. Realmente processa eventos de domínio, armazena em SQLite via API e calcula indicadores/ML com Scikit-learn quando aplicável.

## Execução
```bash
python -m pip install -r requirements/advanced.txt
python projetos/10-advanced/097-cyber-physical-predictive-maintenance-system/main.py --save
python -m unittest discover -s tests -p test_advanced_batch.py -v
uvicorn advanced_batch.api:app --host 127.0.0.1 --port 8000
```

**Kafka real (local):** `docker compose -f advanced_batch/compose.yaml up -d redpanda`, `python -m advanced_batch.kafka_bus publish --project 97 --count 96`, depois `python -m advanced_batch.kafka_bus consume --count 96`. O CI possui teste separado de broker. O painel Streamlit lê a API; nenhum comando de planta é enviado.

**Stack implementada no conjunto:** FastAPI, SQLite, Scikit-learn, Pandas, NumPy, Streamlit, Kafka-python e Docker; Power BI apenas como template M/DAX não executado em Desktop. [Motor](../../../advanced_batch/engine.py) · [API](../../../advanced_batch/api.py) · [Limitações](../../../advanced_batch/README.md).

**Limites:** dados e rótulos fictícios, sem fonte industrial, autenticação de produção, controle de equipamento, contratação, decisão de crédito ou impacto medido. A API é demonstrativa e deve ficar em rede local.
