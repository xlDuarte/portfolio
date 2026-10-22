-- Batch-level cost drivers and scenario tariffs.
SELECT batch_id,line,units,peak_kwh,offpeak_kwh,regular_hours,
       overtime_hours,material_cost_brl,budget_unit_brl
FROM fact_costs ORDER BY batch_id;
