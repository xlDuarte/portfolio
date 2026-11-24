# #88 — Industrial Billing & Revenue Projection

**Status:** análise de negócio funcional com dados industriais inteiramente sintéticos. Sem acesso a sistemas SAP/Ariba e sem medição financeira corporativa.

## Escopo executado
Conciliação entre faturamento líquido e lançamentos fictícios do razão; aponta diferenças e estima receita dos próximos três meses.

**Metodologia:** Modelo Ridge treinado em 30 meses com índices temporais e sazonalidade; holdout final de 6 meses, sem valores futuros observados.

**Tecnologias efetivas:** SQLite SQL, Pandas, Scikit-learn Ridge, Matplotlib. Painel Streamlit para explorar o resultado e modelos SQL para consultas.

## Instalação e execução
```bash
python -m pip install -r requirements/business.txt
python projetos/09-business/088-industrial-billing-revenue-projection/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Arquivos:** `business_batch/exports/88_query.csv` (resultado SQL real), `business_batch/reports/88.json`, `business_batch/figures/88.png`. [Consulta executada](../../../business_batch/sql/088.sql) · [fonte Python](../../../business_batch/engine.py) · [Power Query/DAX](../../../business_batch/powerbi/README.md).

**Limites:** nenhuma homologação externa, conciliação fiscal oficial, nota auditada, cálculo tarifário vigente ou modelo Power BI executado. Estes dados são demonstrações acadêmico-industriais fictícias.
