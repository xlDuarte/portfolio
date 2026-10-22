# #84 — Supplier & Client ABC/RFM Segmentation

**Status:** implementação funcional sobre dados ERP fictícios. Não é integração SAP/Ariba ou relatório Power BI executado.

## Escopo entregue
Agrupa faturamento de clientes por consultas SQL e calcula ABC cumulativo e RFM em quintis.

**Método e testes:** Recência medida contra data fixa de referência, frequência por número de faturas, monetário por receita, com equilíbrio de subtotais.

**Tecnologias deste projeto:** SQLite SQL, Pandas, NumPy, Matplotlib.

## Execução verificável
```bash
python -m pip install -r requirements-business.txt
python projetos/09-business/084-supplier-client-abc-rfm-segmentation/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Saídas reais do Python:** `business_batch/exports/84_query.csv` obtido por SQL executado; `business_batch/reports/84.json`, `business_batch/figures/84.png` e onze tabelas raw CSV para exploração.

**Fonte:** [código](../../../business_batch/engine.py) · [SQL deste projeto](../../../business_batch/sql/84.sql) · [documentação Power BI](../../../business_batch/powerbi/README.md) · [auditoria](../../../business_batch/README.md).

## Restrições
Premissas e valores de todas as tabelas são artificiais, sem indicador de desempenho corporativo observado. Fontes SAP não conectadas, nenhuma execução da DAX no CI e nenhuma medição econômica externa.
