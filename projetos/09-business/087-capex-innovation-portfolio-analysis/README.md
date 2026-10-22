# #87 — CAPEX Innovation Portfolio Analysis

**Status:** processamento real de dados financeiros industriais inteiramente sintéticos, sem conexão corporativa.

## Funcionalidade implementada
VPL dos projetos pela soma descontada de quatro anos de caixa, seguido de otimização exaustiva sob CAPEX máximo.

**Ferramentas efetivamente utilizadas:** SQLite SQL, NumPy, Pandas, otimização combinatória.

## Reproduzir
```bash
python -m pip install -r requirements-business.txt
python projetos/09-business/087-capex-innovation-portfolio-analysis/main.py --save
python -m streamlit run business_batch/app.py
python -m unittest discover -s tests -p test_business_batch.py -v
```

**Dados/relatórios gerados:** `business_batch/exports/87_query.csv`, `business_batch/reports/87.json`, `business_batch/figures/87.png`. O arquivo [SQL](../../../business_batch/sql/87.sql) é executado com SQLite; a fonte de dados é gerada pelo [motor](../../../business_batch/engine.py).

**Limitações:** Compara 2¹² = 4.096 subconjuntos para maximizar VPL, rejeita propostas que excedam orçamento e retorna IDs selecionados. Templates [DAX](../../../business_batch/powerbi/Measures.dax) só foram escritos; nenhuma execução via Power BI Desktop. Não há dados SAP reais nem conclusão de compliance.
