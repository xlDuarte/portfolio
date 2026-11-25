> **Atualização científica (fase 4b):** vazamento interno de bomba com 2.205 ciclos reais do banco hidráulico da ZeMA (UCI): vazão nos patamares de carga, compensação de viscosidade (Walther) validada fora da amostra e classificação em regime térmico nunca visto (94 % com atributos físicos compensados contra 60 % com estatísticos). Código em [`degradation/hydraulics.py`](../../../degradation/hydraulics.py), método em [docs/physics/DEGRADATION.md](../../../docs/physics/DEGRADATION.md).

# #036 — Hydraulic Pump Failure Classification

**Escopo comprovável:** classificador industrial de demonstração treinado em observações e rótulos **100% sintéticos**.

Este projeto carrega explicitamente as variáveis numéricas `vibration_mm_s`, `oil_temp_c`, `pressure_variation`, `maintenance_age_days`, `particle_count` e a variável categórica `pump_type`. Usa Pandas/NumPy, StandardScaler e OneHotEncoder, Scikit-learn LogisticRegression, HistGradientBoostingClassifier e DummyClassifier. O código aplica divisão treino/calibração/teste 60/20/20, seleciona o limiar na calibração e calcula ROC-AUC, F1, average precision, Brier e matriz de confusão no teste.

```bash
python -m pip install -r requirements/classification.txt
python projetos/04-classification/036-hydraulic-pump-failure-classification/main.py
python -m unittest discover -s tests -p test_classification_batch.py -v
```

**Fontes:** [motor](../../../classification_batch/engine.py) · [configuração específica](../../../classification_batch/config.json) · [auditoria integrada](../../../INTEGRATION_AUDIT.md).

**Limites:** sem SAP, XGBoost, TensorFlow, serviço externo, dados corporativos, impacto de negócio validado ou decisões automatizadas. O resultado não qualifica modelos comerciais/de crédito/segurança como homologados.
