# Classification batch #031–#040

Ten independent domain-specific **synthetic** classification experiments. Training is real; observations and outcomes are simulated. Each experiment trains a prior baseline, LogisticRegression and HistGradientBoostingClassifier; stratified 60/20/20 training/calibration/test; tunes threshold only on calibration; reports ROC AUC, AP, F1, precision, recall, Brier and confusion matrix on untouched test.

```bash
python -m pip install -r requirements-classification.txt
python -m unittest discover -s tests -p 'test_classification_batch.py' -v
python -m classification_batch.engine 31
```

**Not suitable for automated credit, employment, security, insurance or personnel decisions.** No real-world validation, deployment, cost-effectiveness study or regulatory approval. Identifiers represent unrelated simulated records.
