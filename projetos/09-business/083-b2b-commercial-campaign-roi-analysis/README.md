# #83 — B2B Commercial Campaign ROI Analysis

**Status:** implementação funcional sobre dados ERP fictícios. Não é integração SAP/Ariba ou relatório Power BI executado.

## Escopo entregue
Compara margem de contribuição entre campanhas e controles artificiais de alocação aleatória.

**Método e testes:** Calcula lift médio, efeito incremental estimado, despesa de campanha e ROI; cenário experimental sintético, não prova causal real.

**Tecnologias deste projeto:** SQLite SQL, Pandas, NumPy, Matplotlib.

## Execução verificável
```bash
python -m pip install -r requirements/business.txt
python projetos/09-business/083-b2b-commercial-campaign-roi-analysis/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Saídas reais do Python:** `business_batch/exports/83_query.csv` obtido por SQL executado; `business_batch/reports/83.json`, `business_batch/figures/83.png` e onze tabelas raw CSV para exploração.

**Fonte:** [código](../../../business_batch/engine.py) · [SQL deste projeto](../../../business_batch/sql/083.sql) · [documentação Power BI](../../../business_batch/powerbi/README.md) · [auditoria](../../../business_batch/README.md).

## Restrições
Premissas e valores de todas as tabelas são artificiais, sem indicador de desempenho corporativo observado. Fontes SAP não conectadas, nenhuma execução da DAX no CI e nenhuma medição econômica externa.
