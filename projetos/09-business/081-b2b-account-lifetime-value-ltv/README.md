# #81 — B2B Account Lifetime Value (LTV)

**Status:** implementação funcional sobre dados ERP fictícios. Não é integração SAP/Ariba ou relatório Power BI executado.

## Escopo entregue
Treina RandomForestRegressor com atributos de 12 meses anteriores e prevê margem de contribuição dos próximos 12 meses por cliente artificial.

**Método e testes:** Usa split por conta (135 treino/45 teste), MAE/R² e baseline mediana; não utiliza rótulo futuro como feature.

**Tecnologias deste projeto:** Scikit-learn, Pandas, SQLite SQL, Matplotlib, Streamlit.

## Execução verificável
```bash
python -m pip install -r requirements-business.txt
python projetos/09-business/081-b2b-account-lifetime-value-ltv/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Saídas reais do Python:** `business_batch/exports/81_query.csv` obtido por SQL executado; `business_batch/reports/81.json`, `business_batch/figures/81.png` e onze tabelas raw CSV para exploração.

**Fonte:** [código](../../../business_batch/engine.py) · [SQL deste projeto](../../../business_batch/sql/081.sql) · [documentação Power BI](../../../business_batch/powerbi/README.md) · [auditoria](../../../business_batch/README.md).

## Restrições
Modelo não está validado sobre contas reais, vendas reais ou políticas comerciais e não apoia decisões de crédito. Fontes SAP não conectadas, nenhuma execução da DAX no CI e nenhuma medição econômica externa.
