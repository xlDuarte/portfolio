# Synthetic regression fixtures (projects #022–#030)

All records and outcome values are deterministic artificial scenarios, not measured business data.

|Project|Outcome|Predictors|Split|
|---|---|---|---|
|#022 Fleet & Vehicle Residual Value Model|target_value (BRL)|age_years, odometer_km, service_score, incident_count, battery_health_pct, original_price_brl, powertrain|Seeded unique record|
|#023 Engineering Compensation & Cost Model|target_value (BRL/month)|experience_years, certifications, responsibility_level, local_cost_index, leadership_years, overtime_hours, specialty|Seeded unique record|
|#024 Technical Certification Score Prediction|target_value (score points)|training_hours, practice_score, prior_score, study_weeks, attendance_pct, difficulty_index, certification_track|Seeded unique record|
|#025 Occupational Safety Cost Prediction|target_value (BRL/year)|exposed_workers, hazard_index, historic_near_misses, training_coverage_pct, machine_age_years, shift_hours, process|Seeded unique record|
|#026 Industrial Equipment Insurance Pricing|target_value (BRL/year)|replacement_value_brl, equipment_age_years, annual_use_hours, maintenance_score, deductible_pct, security_score, equipment_type|Seeded unique record|
|#027 Industrial Forgings Sales Regression|target_value (units/day)|lag1_sales, lag7_sales, past7_mean, announced_price_index, capacity_units, month_sin, month_cos|Chronological|
|#028 Edge & Workstation Hardware Cost Model|target_value (BRL)|cpu_cores, ram_gb, ssd_tb, gpu_tflops, ruggedness_rating, warranty_years, device_quantity, deployment_class|Seeded unique record|
|#029 Furnace & Machining Power Consumption|target_value (kWh/day)|planned_furnace_hours, planned_machine_hours, planned_tonnage, ambient_temp_c, furnace_load_pct, tariff_period_index, process|Chronological|
|#030 Logistics Delivery Time (ETA) Prediction|target_value (hours)|route_distance_km, forecast_traffic_index, stops_planned, cargo_weight_tons, forecast_rain_mm, dispatch_hour, border_crossings, transport_mode|Chronological|

Source generation: `regression_batch.engine.synthetic_data(id, n=420, seed=2026)`; each CSV contains `sample_id`, optional `observation_date`, predictor columns, `target_value`. Rows are not records of real persons, companies, routes or plants.
