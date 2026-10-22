-- Summarize facts by operating line BEFORE computing weighted OEE.
SELECT line, SUM(planned_min) AS planned_min,
       SUM(operating_min) AS operating_min,
       SUM(total_units) AS total_units, SUM(good_units) AS good_units,
       MAX(ideal_cycle_min) AS ideal_cycle_min,
       SUM(quota_units) AS quota_units
FROM fact_shifts GROUP BY line ORDER BY line;
