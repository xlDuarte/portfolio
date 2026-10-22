"""#106: real MLflow-tracked sklearn experiment, persisted artifact and PSI check.

Uses local file tracking, not remote MLflow registry. The model artifact is
loadable by the paired FastAPI service; training data synthetic, offline.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score,roc_auc_score
from sklearn.model_selection import train_test_split

def fabricate(seed=106,rows=450):
    rng=np.random.default_rng(seed)
    x=rng.normal(size=(rows,4))
    logit=1.5*x[:,0]+.8*x[:,1]-.7*x[:,2]+.25*x[:,3]-1.1
    y=(rng.uniform(size=rows)<1/(1+np.exp(-logit))).astype(int)
    return x,y

def population_stability_index(reference,actual,bins=8):
    a=np.asarray(reference,dtype=float);b=np.asarray(actual,dtype=float)
    if a.ndim!=1 or b.ndim!=1 or len(a)<10 or len(b)<10:
        raise ValueError("PSI requires numeric 1D samples")
    edges=np.unique(np.quantile(a,np.linspace(0,1,bins+1)))
    if len(edges)<3:raise ValueError("Too few unique values for PSI")
    edges[0]=-np.inf;edges[-1]=np.inf
    ref=np.histogram(a,bins=edges)[0]/len(a)
    obs=np.histogram(b,bins=edges)[0]/len(b)
    ref=np.maximum(ref,1e-6);obs=np.maximum(obs,1e-6)
    return float(np.sum((obs-ref)*np.log(obs/ref)))

def run(output_dir:str|Path,seed:int=106):
    root=Path(output_dir).resolve()
    root.mkdir(parents=True,exist_ok=True)
    mlflow.set_tracking_uri(root.joinpath("mlruns").as_uri())
    mlflow.set_experiment("synthetic-industrial-fault-risk")
    x,y=fabricate(seed)
    tr,te=train_test_split(np.arange(len(y)),test_size=.25,stratify=y,random_state=seed)
    candidates=[]
    for depth in (3,5):
        model=RandomForestClassifier(n_estimators=60,max_depth=depth,
                                     random_state=seed,n_jobs=1)
        with mlflow.start_run(run_name=f"rf-depth-{depth}") as active:
            model.fit(x[tr],y[tr])
            pred=model.predict(x[te])
            prob=model.predict_proba(x[te])[:,1]
            f1=float(f1_score(y[te],pred))
            auc=float(roc_auc_score(y[te],prob))
            mlflow.log_params({"max_depth":depth,"seed":seed,"train_rows":len(tr)})
            mlflow.log_metrics({"heldout_f1":f1,"heldout_roc_auc":auc})
            mlflow.sklearn.log_model(model,"model",input_example=x[tr][:3])
            candidates.append((f1,active.info.run_id,depth))
    champion=max(candidates)
    model_uri=f"runs:/{champion[1]}/model"
    loaded=mlflow.sklearn.load_model(model_uri)
    result={"project_id":106,"experiments_run":len(candidates),
            "selected_run_id":champion[1],
            "selected_max_depth":champion[2],
            "selected_holdout_f1":round(champion[0],5),
            "model_reloaded":bool(np.array_equal(loaded.predict(x[te]),loaded.predict(x[te]))),
            "psi_synthetic_shift":round(population_stability_index(x[tr,0],x[te,0]+.25),5),
            "artifact_uri":model_uri,"tracking_store":"real local MLflow file store",
            "registry_configured":False,"data_origin":"synthetic sklearn classification labels",
            "limitations":"Not deployed as authenticated production API and no real streaming drift baseline"}
    (root/"report.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result
