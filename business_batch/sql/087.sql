-- Four-year discounted cash flow candidates (fictional CAPEX).
SELECT project_id,name,capex_k_brl,year1_k_brl,year2_k_brl,
       year3_k_brl,year4_k_brl,strategic_score
FROM fact_capex ORDER BY project_id;
