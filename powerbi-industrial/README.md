# Industrial Operations — Power BI semantic model PBIP prototype

**Status: model.bim (TMSL) + DAX authoring artifacts generated; NOT validated in Power BI Desktop.** The report contains a PBIR page with four KPI card definitions; Desktop rendering is NOT verified. Do not call this a delivered PBIX dashboard.

## Architecture

- `IndustrialOperations.SemanticModel/definition.pbism` and `model.bim`: five Import tables and six star-schema single-direction relationships.
- `IndustrialOperations.Report/definition.pbir`: byPath semantic model binding; report shell only.
- `IndustrialOperations.pbip`: Desktop project shortcut.
- Embedded `#table` Power Query M fixtures are fully synthetic, require no external credentials and are reproducible.
- 16 DAX measures for OEE, availability, performance, quality, OTIF, revenue and defect PPM.
- `expected_kpis.json`: independently calculated Python reference figures for manual validation.

## Required Microsoft Desktop acceptance test

1. Open `IndustrialOperations.pbip` in Power BI Desktop (Windows, recent build) and refresh the model.
2. Confirm five tables, six one-to-many relationships, and the 16 DAX measures without errors.
3. Run `DAXQueries/ValidateKPIs.dax` in DAX Query View and compare results to `expected_kpis.json`.
4. Check that four KPI cards render; add slicers and detailed views in Desktop; save PBIP and test cross-filter behavior; record screenshots.
5. Integrate approved production data later, revalidate data types/refresh, DAX and RLS separately.

Never supply internal SAP credentials or production extracts to this demonstration model.

Official PBIP docs: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
