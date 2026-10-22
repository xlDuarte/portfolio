-- Non-conclusive SOX-like control flags. These are NOT fraud findings.
WITH flagged AS (
 SELECT p.*,
 CASE WHEN COUNT(*) OVER (PARTITION BY vendor_id,invoice_ref)>1 THEN 1 ELSE 0 END AS duplicate_ref,
 CASE WHEN CAST(strftime('%w',payment_date) AS INTEGER) IN (0,6) THEN 1 ELSE 0 END AS weekend_payment,
 CASE WHEN amount_brl>approval_limit_brl THEN 1 ELSE 0 END AS limit_exceeded,
 COUNT(*) OVER (PARTITION BY vendor_id,payment_date) AS same_day_count,
 SUM(amount_brl) OVER (PARTITION BY vendor_id,payment_date) AS same_day_total
 FROM fact_payments p
)
SELECT payment_id,vendor_id,invoice_ref,payment_date,amount_brl,approval_limit_brl,
       duplicate_ref,weekend_payment,limit_exceeded,
       CASE WHEN same_day_count>=2 AND amount_brl<=approval_limit_brl
                 AND same_day_total>approval_limit_brl THEN 1 ELSE 0 END AS possible_split
FROM flagged ORDER BY payment_id;
