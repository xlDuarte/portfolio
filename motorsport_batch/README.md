# Motorsport F1 / MLOps #101–#110 — Evidence and boundaries

**No real Formula 1 telemetry, FIA timing feed, camera footage, branded FLIR thermal measurements, ChassisSim commercial solver, team data, or production ML service was used.** Every dataset is synthetic and reproducible. This patch **preserves** already meaningful engineering code for #101/#102/#103/#109/#110 and adds code to replace incomplete or numerical-placeholding frameworks for #104–#108.

| # | Verified implementation location | Real algorithms | Important exclusions |
|---|---|---|---|
| 101 | original pit-stop `main.py` plus `race_ml.py` | Stint optimization, RandomForestRegressor + XGBRegressor, session-disjoint holdout | No real lap timing or calibrated tire simulation |
| 102 | existing `main.py` | Scalar EKF recursion with simulated yaw/lateral sensors | No production sensor fusion calibration or multi-state EKF |
| 103 | existing `motorsport/optical_flow.py` | OpenCV Lucas–Kanade, robust feature displacement on rendered frames | No true onboard video/calibrated depth |
| 104 | `vibration.py` | Fitted TensorFlow LSTM autoencoder, RMS baseline, held-out fault classification | No actual bearing vibration sensor readings |
| 105 | `xray.py` | Fitted Keras CNN, TensorFlow GradientTape Grad-CAM, synthetic mask IoU | No actual X-rays or certified NDT |
| 106 | `mlops.py`, `service.py`, Dockerfile | Two tracked **real MLflow runs**, saved/reloaded sklearn RF, PSI, FastAPI inference | No remote model registry, secured deployment, CI/CD to production |
| 107 | `rag.py` | Generate real fictional PDFs, parse pypdf pages, LangChain splitter/RunnableLambda, TF-IDF retrieval and grounded quotes | **Not a generative LLM** or private corporate documents |
| 108 | `explain.py` | SMOTE applied only to train, XGBClassifier fit, genuine SHAP TreeExplainer | No industrial labels or causal guarantee |
| 109 | preserved replay engine plus `replay.py` | Multi-car synthetic telemetry and Plotly/Streamlit manual time-slider circuit rendering | Geometry is a fictional parametric loop, not real Interlagos GPS/real-time data |
| 110 | preserved math and `performance.py` | Three-zone artificial thermal surface, tyre stiffness sweep, damper histogram, QSS-like lap-time proxy | **Not FLIR image analysis or proprietary ChassisSim** |

## Installation and verification

```bash
python -m pip install -r requirements-motorsport-core.txt
python -m unittest discover -s tests -p test_motorsport_batch.py -v
python projetos/11-motorsport-f1-mlops/101-f1-predictive-race-strategy-pit-stop-window-simulator/main.py --fit-ml
python -m streamlit run motorsport_batch/replay.py
python -m streamlit run motorsport_batch/performance.py
```

Heavy frameworks are installed separately for CI resource isolation:

```bash
python -m pip install -r requirements-motorsport-tf.txt
RUN_MOTORSPORT_TF=1 python -m unittest discover -s tests -p test_motorsport_advanced.py -v

python -m pip install -r requirements-motorsport-mlops.txt
RUN_MOTORSPORT_ADVANCED=1 python -m unittest discover -s tests -p test_motorsport_advanced.py -v
```

Full model execution (required to validate the advertised advanced stack, not just inspect synthetic sample shape):

```bash
python -m motorsport_batch.cli 104 --run
python -m motorsport_batch.cli 105 --run
python -m motorsport_batch.cli 106 --run --output /tmp/motorsport-mlflow
python -m motorsport_batch.cli 107 --run --output /tmp/motorsport-rag
python -m motorsport_batch.cli 108 --run
```

**Do not interpret the default CLI without `--run` for #104–#108 as evidence that LSTM/CNN/MLflow/LangChain/SHAP were executed.** The dedicated CI jobs are the evidence of full execution. Model thresholds, statistics and physics proxies are evaluated only on the artificial datasets; comparisons cannot be generalized to motorsport engineering.

## MLflow/FastAPI service

Project #106 locally writes MLflow tracking runs. The inference service can load a run URI from a previously saved local model when `MLOPS_MODEL_URI` and the MLflow tracking URI are configured for the same artifact directory. It is not publicly authenticated; use only in isolated development environments. The Dockerfile packages the service but does not include a trained model artifact.

## Validation required for production

Licensed timing, GPS and track maps; proprietary solver verification, independent tests with measured tyre/radiographic/thermal samples, reproducibility across tracks, proper simulation parameter identification, model registry controls, latency and reliability SLAs, API authorization/TLS, real RAG relevance evaluation, and operator sign-off remain outstanding. Passing synthetic CI is not a 100/100 production audit.
