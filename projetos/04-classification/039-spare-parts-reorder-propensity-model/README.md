# #039 — Spare Parts Reorder Propensity

**Escopo comprovável:** classificador industrial de demonstração treinado em observações e rótulos **100% sintéticos**.

Este projeto carrega explicitamente as variáveis numéricas `days_since_last_order`, `past_orders`, `stockout_events`, `active_machines`, `quoted_discount_pct` e a variável categórica `product_family`. Usa Pandas/NumPy, StandardScaler e OneHotEncoder, Scikit-learn LogisticRegression, HistGradientBoostingClassifier e DummyClassifier. O código aplica divisão treino/calibração/teste 60/20/20, seleciona o limiar na calibração e calcula ROC-AUC, F1, average precision, Brier e matriz de confusão no teste.

```bash
python -m pip install -r requirements-classification.txt
python projetos/04-classification/039-spare-parts-reorder-propensity-model/main.py
python -m unittest discover -s tests -p test_classification_batch.py -v
```

**Fontes:** [motor](../../../classification_batch/engine.py) · [configuração específica](../../../classification_batch/config.json) · [auditoria integrada](../../../INTEGRATION_AUDIT.md).

**Limites:** sem SAP, XGBoost, TensorFlow, serviço externo, dados corporativos, impacto de negócio validado ou decisões automatizadas. O resultado não qualifica modelos comerciais/de crédito/segurança como homologados.
