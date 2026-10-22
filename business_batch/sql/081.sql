-- Customer-level features and a SIMULATED future margin label.
-- Training must split by customer ID; labels cannot be included in X.
SELECT customer_id, segment, tenure_months, prior_12m_margin_brl,
       orders_12m, late_orders_12m, future_12m_margin_brl
FROM dim_customers ORDER BY customer_id;
