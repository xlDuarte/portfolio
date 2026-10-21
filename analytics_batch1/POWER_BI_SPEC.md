# Power BI implementation checklist — outstanding

**Status: not a working Power BI report**. There is no `.pbix` or validated `.pbip` for these nine studies. Do not list Power BI as implemented until these acceptance tests are met:

1. Create a PBIP with a semantic model importing the versioned `analytics_batch1/data/*.csv` sources.
2. Explicit relationships and grain per table; validated DAX measures without row/count ambiguity.
3. Nine report pages with slicers, data labels, units, dates, and accessible color scheme.
4. Test interactions in Power BI Desktop and export reproducible screenshots for each project.
5. Provide documentation for Power Query/M transformations and measure validation using independent Python calculations.
6. Note synthetic data source explicitly and avoid enterprise impact claims.

## Proposed measures (not executed or verified in Power BI)

- #001: `Mean Post Score = AVERAGE(Operators[post_score])`
- #002: `Net Sales BRL = SUMX(Sales, (Sales[units_sold]-Sales[units_returned])*Sales[unit_price_brl])`
- #003: `Metadata Completion = DIVIDE(SUM(Documents[completed_fields]),SUM(Documents[required_fields]))`
- #004: spectral charts should use a frequency-domain materialization, not naive DAX over raw samples.
- #005: `Self Service Share = AVERAGE(KB[resolved_without_ticket])`
- #006: purchase cycle time uses a calculated or imported duration column.
- #007: `Total Spend BRL = SUMX(Purchases,Purchases[quantity]*Purchases[unit_price_brl])`
- #008: `kWh per Unit = DIVIDE(SUM(Utilities[kwh]),SUM(Utilities[produced_units]))`
- #009: depreciated value requires a documented valuation date and accounting policy.

These expressions are implementation requirements and have **not** been validated against a Power BI engine.
