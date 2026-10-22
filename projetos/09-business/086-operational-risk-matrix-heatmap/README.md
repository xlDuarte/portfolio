# #86 — Operational Risk Matrix & Heatmap

**Status:** processamento real de dados financeiros industriais inteiramente sintéticos, sem conexão corporativa.

## Funcionalidade implementada
Matriz de risco operacional de 5 × 5 com cálculo probabilidade × impacto, agregação de frequência e heatmap.

**Ferramentas efetivamente utilizadas:** SQLite SQL, NumPy, Matplotlib.

## Reproduzir
```bash
python -m pip install -r requirements-business.txt
python projetos/09-business/086-operational-risk-matrix-heatmap/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Dados/relatórios gerados:** `business_batch/exports/86_query.csv`, `business_batch/reports/86.json`, `business_batch/figures/86.png`. O arquivo [SQL](../../../business_batch/sql/86.sql) é executado com SQLite; a fonte de dados é gerada pelo [motor](../../../business_batch/engine.py).

**Limitações:** Escalas e limiar ≥15 são fictícios. Não representa incidente real nem validação de segurança. Templates [DAX](../../../business_batch/powerbi/Measures.dax) só foram escritos; nenhuma execução via Power BI Desktop. Não há dados SAP reais nem conclusão de compliance.
