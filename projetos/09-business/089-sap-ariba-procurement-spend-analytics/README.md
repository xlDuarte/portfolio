# #89 — SAP Ariba Procurement Spend Analytics

**Status:** análise de negócio funcional com dados industriais inteiramente sintéticos. Sem acesso a sistemas SAP/Ariba e sem medição financeira corporativa.

## Escopo executado
Compras e fornecedores via consultas SQL e Pandas: gasto por categoria, concentração HHI e cumprimento de prazo.

**Metodologia:** Simula dados no formato Ariba, mas não consulta SAP nem valida cadastro de fornecedores. Indicador de prazo não é OTIF completo.

**Tecnologias efetivas:** SQLite SQL, Pandas, NumPy, Matplotlib. Painel Streamlit para explorar o resultado e modelos SQL para consultas.

## Instalação e execução
```bash
python -m pip install -r requirements/business.txt
python projetos/09-business/089-sap-ariba-procurement-spend-analytics/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Arquivos:** `business_batch/exports/89_query.csv` (resultado SQL real), `business_batch/reports/89.json`, `business_batch/figures/89.png`. [Consulta executada](../../../business_batch/sql/089.sql) · [fonte Python](../../../business_batch/engine.py) · [Power Query/DAX](../../../business_batch/powerbi/README.md).

**Limites:** nenhuma homologação externa, conciliação fiscal oficial, nota auditada, cálculo tarifário vigente ou modelo Power BI executado. Estes dados são demonstrações acadêmico-industriais fictícias.
