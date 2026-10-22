-- Full join of invoice net revenue and ledger by month (synthetic).
SELECT b.month,b.gross_brl,b.discount_rate,b.tax_rate,b.net_revenue_brl,
       l.posted_revenue_brl
FROM fact_billing b JOIN fact_ledger l ON b.month=l.month
ORDER BY b.month;
