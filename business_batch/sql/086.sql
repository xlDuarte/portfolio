-- Observations aggregated into a synthetic 5x5 heatmap.
SELECT likelihood,impact,COUNT(*) AS events
FROM fact_risk GROUP BY likelihood,impact
ORDER BY likelihood,impact;
