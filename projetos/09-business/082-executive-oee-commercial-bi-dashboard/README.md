# #82 — Executive OEE & Commercial BI Dashboard

**Status:** implementação funcional sobre dados ERP fictícios. Não é integração SAP/Ariba ou relatório Power BI executado.

## Escopo entregue
OEE ponderado de três linhas; calcula disponibilidade, performance, qualidade, OEE total e atingimento de meta.

**Método e testes:** Consolida turno por linha em SQL e pondera OEE pela produção ideal boa dividida pelo tempo planejado; evita média simples de percentuais.

**Tecnologias deste projeto:** SQLite SQL, Pandas, Power Query M e expressões DAX fornecidas; DAX não executado em CI.

## Execução verificável
```bash
python -m pip install -r requirements-business.txt
python projetos/09-business/082-executive-oee-commercial-bi-dashboard/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Saídas reais do Python:** `business_batch/exports/82_query.csv` obtido por SQL executado; `business_batch/reports/82.json`, `business_batch/figures/82.png` e onze tabelas raw CSV para exploração.

**Fonte:** [código](../../../business_batch/engine.py) · [SQL deste projeto](../../../business_batch/sql/82.sql) · [documentação Power BI](../../../business_batch/powerbi/README.md) · [auditoria](../../../business_batch/README.md).

## Restrições
Premissas e valores de todas as tabelas são artificiais, sem indicador de desempenho corporativo observado. Fontes SAP não conectadas, nenhuma execução da DAX no CI e nenhuma medição econômica externa.
