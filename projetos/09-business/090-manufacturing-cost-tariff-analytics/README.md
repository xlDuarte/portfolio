# #90 — Manufacturing Cost & Tariff Analytics

**Status:** análise de negócio funcional com dados industriais inteiramente sintéticos. Sem acesso a sistemas SAP/Ariba e sem medição financeira corporativa.

## Escopo executado
Cálculo dos custos de transformação: materiais, energia ponta/fora-ponta, mão de obra, horas extras e orçamento.

**Metodologia:** O custo unitário é ponderado por produção; tarifas e adicionais são hipóteses matemáticas, não folha ou tarifa vigente.

**Tecnologias efetivas:** SQLite SQL, Pandas, NumPy, Matplotlib. Painel Streamlit para explorar o resultado e modelos SQL para consultas.

## Instalação e execução
```bash
python -m pip install -r requirements-business.txt
python projetos/09-business/090-manufacturing-cost-tariff-analytics/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Arquivos:** `business_batch/exports/90_query.csv` (resultado SQL real), `business_batch/reports/90.json`, `business_batch/figures/90.png`. [Consulta executada](../../../business_batch/sql/90.sql) · [fonte Python](../../../business_batch/engine.py) · [Power Query/DAX](../../../business_batch/powerbi/README.md).

**Limites:** nenhuma homologação externa, conciliação fiscal oficial, nota auditada, cálculo tarifário vigente ou modelo Power BI executado. Estes dados são demonstrações acadêmico-industriais fictícias.
