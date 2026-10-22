"""Development-only REST inference of #106 registered-in-local-MLflow-run artifact.

Requires MLOPS_MODEL_URI pointing to a previously trained MLflow artifact.
Never fit on request; no remote registry/production auth implied.
"""
import os
import numpy as np
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field

class Sample(BaseModel):
    vibration:float
    temperature:float
    pressure:float
    rpm:float

app=FastAPI(title="Synthetic MLOps demonstration",version="0.1.0")
_model=None

@app.get("/health")
def health():
    return {"status":"ok","synthetic_only":True,"loaded":_model is not None}

@app.post("/predict")
def predict(sample:Sample):
    global _model
    uri=os.environ.get("MLOPS_MODEL_URI")
    if not uri:
        raise HTTPException(503,"No MLflow artifact loaded; set MLOPS_MODEL_URI")
    if _model is None:
        import mlflow.sklearn
        _model=mlflow.sklearn.load_model(uri)
    x=np.asarray([[sample.vibration,sample.temperature,sample.pressure,sample.rpm]],dtype=float)
    probability=float(_model.predict_proba(x)[0,1])
    return {"synthetic_risk_probability":round(probability,6),
            "threshold_class":int(probability>=.5),
            "model_uri":uri,"decision_executed":False}
