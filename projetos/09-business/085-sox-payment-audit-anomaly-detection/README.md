# #85 — SOX Payment Audit & Anomaly Detection

**Status:** processamento real de dados financeiros industriais inteiramente sintéticos, sem conexão corporativa.

## Funcionalidade implementada
Pagamentos fictícios: SQL com funções de janela para duplicidades, finais de semana, valores além da alçada e possível fracionamento.

**Ferramentas efetivamente utilizadas:** SQLite SQL, Pandas, Matplotlib.

## Reproduzir
```bash
python -m pip install -r requirements-business.txt
python projetos/09-business/085-sox-payment-audit-anomaly-detection/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Dados/relatórios gerados:** `business_batch/exports/85_query.csv`, `business_batch/reports/85.json`, `business_batch/figures/85.png`. O arquivo [SQL](../../../business_batch/sql/85.sql) é executado com SQLite; a fonte de dados é gerada pelo [motor](../../../business_batch/engine.py).

**Limitações:** Indicadores são hipóteses para revisão humana, jamais constatação de fraude/SOX. Templates [DAX](../../../business_batch/powerbi/Measures.dax) só foram escritos; nenhuma execução via Power BI Desktop. Não há dados SAP reais nem conclusão de compliance.
