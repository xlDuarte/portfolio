-- Analysis of a deliberately randomized synthetic treatment assignment.
SELECT prospect_id, segment, treated, observed_margin_brl, campaign_spend_brl
FROM fact_campaigns ORDER BY prospect_id;
