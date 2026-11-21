# F1 Insights

Five browser-based analyses integrated into Motorsport Engineering. No invented observations or silent synthetic fallbacks.

## Sources and interpretation

- Corner comparison: existing observed OpenF1 Bahrain 2024 session 9472, first complete lap available for drivers 1 and 11. The demonstration integrates speed to estimate distance from the first sample. This is not a surveyed spatial alignment: different sampling offsets and integration errors can bias a corner comparison. Import FastF1 CSV exports with a common distance origin for another event. CSV provenance is user supplied, not independently verified. Minimum speeds are not necessarily at the same geometric apex.
- Podium: existing `../data/models-real.json`, trained/evaluated models with chronological validation, retrospective Bahrain 2024. No new Kaggle ingestion or live retraining is claimed. Plackett–Luce sampling uses 5,000 runs, seed 111. Temperature is user configurable and not calibrated probability confidence. Full methodology is available in F1-PIP.
- Championship: Jolpica official standings and race points. The included 2024 snapshots were retrieved on 2026-11-21 from `https://api.jolpi.ca/ergast/f1/2024/driverStandings/?limit=100` and `https://api.jolpi.ca/ergast/f1/2024/1/results/?limit=100`. The scenario subtracts the original selected race points and adds hypothetical points. All other points are preserved. Shared ranks represent ties; FIA countback is not implemented. This is a points scenario, not a complete race adjudication engine. Other seasons can be queried from Jolpica.
- Race monitor: existing observed snapshot or OpenF1 API. Historical access is public; real-time access requires a provider subscription. Optional bearer token stays in memory and is sent only to `https://api.openf1.org`. Queries are bounded to 60 seconds for one driver's telemetry. Position and interval rows show available updates in that same window, so absence is not evidence of withdrawal. Missing gaps remain unavailable. Timestamps identify historical/stale results. Auto refresh every 15 seconds, no overlapping fetch, paused on hidden tabs, stopped on errors. No API response fallback invents observations.
- Racing line: `https://github.com/TUMFTM/racetrack-database`, `tracks/Silverstone.csv`, retrieved 2026-11-21. 1,178 centerline points with left/right widths. OSM-derived smoothed geometry and image-derived widths. Attribution: TUMFTM; © OpenStreetMap contributors, ODbL. Original LGPL-3.0 license and upstream README are distributed alongside the source data. Upstream data-quality limitations apply.

## Numerical methods

Corner profiles use linear interpolation over a common distance window. Time delta is B minus A after resetting both clocks at the window entrance. Minima include original samples and interpolated endpoints; displayed profiles use 201 samples. Negative delta means B traversed the selected window faster.

The periodic racing-line optimizer uses coordinate descent on lateral offsets along centerline normals. The objective is the discretized integral of squared three-point curvature, weighted by local arc length. Steps decrease from 0.8 to 0.032 metres. Each accepted step lowers the local objective; no global-optimum guarantee is made. Margin includes vehicle half-width. Bounds apply at discrete nodes, not continuously between them. No tyre model, collision certification, lap-time optimization, CFD or measured racing line is claimed. CSV export contains x, y and signed lateral offset. Derived geometry retains source attribution and ODbL obligations.

## Validation

`node tests/f1_insights_checks.mjs` checks interpolation, rejection of invalid windows, monotonicity, real complete laps, unchanged championship totals, tied standings, latest timestamps and bounds/objective monotonicity for all Silverstone nodes. Existing podium model tests remain applicable. The Python exporter requires FastF1 and network access; syntax validation does not establish successful live FastF1 retrieval.
