# 031–040 Industrial classifiers — canonical entrypoints audited

Ten project-specific classification models are actually trained and evaluated using Scikit-learn pipelines. Numeric predictors are standardized; categorical predictors are one-hot encoded on **training rows only**. DummyClassifier, LogisticRegression and HistGradientBoostingClassifier are fitted; a threshold is selected using calibration data and an untouched test set provides ROC-AUC, average precision, F1, confusion matrix and Brier loss.

No XGBoost, TensorFlow, business credit-approval service, automated hiring, live SAP, external data, or fraud verdict is implemented in this batch. **All labels are generated synthetically from a versioned configuration**; 100% portfolio completion cannot be inferred.

The canonical `main.py` for every case #031–#040 now uses `classification_batch.engine.evaluate(number)`. The old duplicated `classification_main.py` scripts are compatibility entrypoints and must not be mistaken for additional projects.

```bash
python -m pip install -r requirements/classification.txt
python -m unittest discover -s tests -p test_classification_batch.py -v
python projetos/04-classification/031-b2b-industrial-contract-churn-prediction/main.py
python -m classification_batch.engine 40
```

The synthetic label-generation equation is interpreted with a restricted arithmetic AST, never Python `eval`. Metrics quantify only in-sample simulated distribution generalization. No validated real-client, vendor, worker, cybersecurity, machine, lubricant or procurement dataset is present.
