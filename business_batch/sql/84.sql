-- Real SQLite aggregation and RFM dimension preparation.
SELECT c.customer_id, COUNT(i.invoice_id) AS orders,
       ROUND(COALESCE(SUM(i.amount_brl),0),2) AS revenue_brl,
       MAX(i.invoice_date) AS last_date
FROM dim_customers c JOIN fact_invoices i ON i.customer_id=c.customer_id
GROUP BY c.customer_id HAVING COUNT(i.invoice_id)>0
ORDER BY revenue_brl DESC, c.customer_id;
