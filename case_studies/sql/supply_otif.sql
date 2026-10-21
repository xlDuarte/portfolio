-- Example SQLite analytic queries on case_studies/data/supply_orders.csv after ingest.
-- Dates ISO-8601; all data synthetically generated for reproducibility.
SELECT carrier, material, COUNT(*) AS order_count,
       ROUND(100.0 * AVG(CASE WHEN delivered_date <= promised_date AND delivered_qty >= ordered_qty THEN 1.0 ELSE 0 END), 2) AS otif_pct,
       ROUND(SUM((ordered_qty - delivered_qty) * unit_value_brl), 2) AS shortage_exposure_brl
FROM orders
GROUP BY carrier, material
ORDER BY otif_pct ASC, shortage_exposure_brl DESC;
