# Power BI integration artifacts — imported synthetic ERP facts

**Deliverable:** Power Query M CSV import function (`CsvTable.pq`), table query definitions (`Queries.pq`) and DAX measure expressions (`Measures.dax`). These are editable **source templates**, **not a tested .pbix/.pbip dashboard**, not a deployed Power BI service workspace, and not DAX validated against the Power BI Desktop calculation engine.

## Procedure
1. Run `python -m business_batch.engine 82 --save` to export all synthetic source tables to `business_batch/exports/raw`.
2. Open Power BI Desktop and set a text parameter `DataFolder` to the absolute `exports/raw` path.
3. Add a function query named `CsvTable`, using `CsvTable.pq`.
4. For each expression in `Queries.pq`, create the indicated query (names must exactly match the DAX table names).
5. Transform numeric, date and identifier fields to proper types using Power Query. For example, `planned_min` and `good_units` to whole number; `ideal_cycle_min` to decimal; `amount_brl` to decimal; date fields to Date.
6. Relate `Dim_Customers[customer_id]` (1) to `Fact_Invoices[customer_id]` (many) and create a date dimension if time-intelligence calculations are required. Do not create unnecessary bidirectional relationships.
7. Create and format measures from `Measures.dax` in Desktop; use KPI cards, slicers by line/period, purchasing Pareto and risk heatmaps.

## Integrity and limitations
The Python implementation **executes SQLite queries** and produces actual figures/metrics. The above Power BI measure expressions are independently authored artifacts and have not been evaluated in DAX by CI. Tableau/Power BI report output or SAP API access is NOT implied. Operational use would require approved source credentials, refresh governance, RLS, reconciled accounting logic and automated DAX validation against a compatible Tabular engine.


## Nova entrega PBIP versionável (outubro/2026)

Foi adicionado [Industrial Operations PBIP](../../powerbi-industrial/README.md) com cinco tabelas Import, relacionamentos, 16 medidas DAX e uma página com quatro cartões. O antigo diretório Power Query/DAX permanece como material histórico. **A abertura, execução DAX e renderização no Power BI Desktop ainda não foram verificadas**; não há homologação do dashboard ou dataset industrial real.
