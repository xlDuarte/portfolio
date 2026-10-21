# Project #031 — B2B Industrial Contract Churn Prediction

**Status: estudo demonstrativo reproduzível com dados 100% SINTÉTICOS.** Este caso possui cálculo efetivamente executado, dados versionados, teste automatizado e métrica contextualizada. **Não houve implantação em indústria nem resultado econômico comprovado.**

**Projeto completo:** [`case_studies/`](../../../case_studies/README.md) · [Dicionário de dados](../../../case_studies/DATA_DICTIONARY.md) · [Dados](../../../case_studies/data/) · [Código](../../../case_studies/analytics.py) · [Relatório](../../../case_studies/reports/metrics.json).

**Reprodução:**
```bash
python -m pip install -r requirements-case-studies.txt
python projetos/04-classification/031-b2b-industrial-contract-churn-prediction/main.py
python -m unittest discover -s tests -v
```

**Limites:** desempenho estatístico refere-se exclusivamente ao dataset sintético, com baseline explícita e sem validação externa. Para cenário real, são necessários controles de qualidade, autorização dos dados, recorte temporal, drift, custos de erro e revisão com especialistas.
