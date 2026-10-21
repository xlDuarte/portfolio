-- Availability * Performance * Quality, weighted by planned production time.
-- No arithmetic averaging of individual percentages.
SELECT line, SUM(planned_min) AS scheduled_min,
  ROUND(100.0 * SUM(ideal_cycle_min * good_units) / SUM(planned_min), 2) AS weighted_oee_pct,
  SUM(total_units - good_units) AS scrap_units
FROM shifts
GROUP BY line
ORDER BY weighted_oee_pct ASC;
