# #037 — Lubricant Degradation Classification

**Escopo comprovável:** classificador industrial de demonstração treinado em observações e rótulos **100% sintéticos**.

Este projeto carrega explicitamente as variáveis numéricas `viscosity_change_pct`, `water_ppm`, `particle_count`, `oxidation_index`, `running_hours` e a variável categórica `lubricant_grade`. Usa Pandas/NumPy, StandardScaler e OneHotEncoder, Scikit-learn LogisticRegression, HistGradientBoostingClassifier e DummyClassifier. O código aplica divisão treino/calibração/teste 60/20/20, seleciona o limiar na calibração e calcula ROC-AUC, F1, average precision, Brier e matriz de confusão no teste.

```bash
python -m pip install -r requirements/classification.txt
python projetos/04-classification/037-lubricant-degradation-classifier/main.py
python -m unittest discover -s tests -p test_classification_batch.py -v
```

**Fontes:** [motor](../../../classification_batch/engine.py) · [configuração específica](../../../classification_batch/config.json) · [auditoria integrada](../../../INTEGRATION_AUDIT.md).

**Limites:** sem SAP, XGBoost, TensorFlow, serviço externo, dados corporativos, impacto de negócio validado ou decisões automatizadas. O resultado não qualifica modelos comerciais/de crédito/segurança como homologados.
