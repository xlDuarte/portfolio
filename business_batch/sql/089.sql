-- Synthetic Ariba-like purchase-order facts; no ERP connection.
SELECT po_id,vendor_id,category,order_date,quantity,unit_price_brl,
       quoted_lead_days,actual_lead_days,spend_brl
FROM fact_procurement ORDER BY po_id;
