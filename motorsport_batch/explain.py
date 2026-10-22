"""#108: actual SMOTE (training ONLY), fitted XGBoost and SHAP TreeExplainer."""
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score,roc_auc_score
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

FEATURES=["vibration_rms","bearing_temp_c","kurtosis","oil_metal_ppm"]
def generate(seed=108,n=480):
    rng=np.random.default_rng(seed)
    x=np.stack([rng.uniform(.9,8,n),rng.uniform(40,113,n),
                rng.uniform(2,9,n),rng.uniform(0,45,n)],axis=1)
    score=(.75*(x[:,0]-5)+.048*(x[:,1]-84)+.19*(x[:,2]-6)+.025*(x[:,3]-26)-3.2)
    probs=1/(1+np.exp(-score))
    y=(rng.uniform(size=n)<probs).astype(int)
    if y.sum()<12:raise ValueError("Synthetic minority too rare")
    return x,y

def evaluate(seed=108):
    import shap
    x,y=generate(seed)
    tr,te=train_test_split(np.arange(len(y)),test_size=.25,stratify=y,random_state=seed)
    scaler=None # XGBoost operates in the original unit and does not require scaling
    xt=x[tr];yt=y[tr]
    sampler=SMOTE(random_state=seed,k_neighbors=3)
    balanced_x,balanced_y=sampler.fit_resample(xt,yt)
    model=XGBClassifier(n_estimators=90,max_depth=3,learning_rate=.065,
                         subsample=.90,colsample_bytree=.9,
                         objective="binary:logistic",eval_metric="logloss",
                         random_state=seed,n_jobs=1)
    model.fit(balanced_x,balanced_y)
    score=model.predict_proba(x[te])[:,1]
    explainer=shap.TreeExplainer(model)
    attributions=np.asarray(explainer.shap_values(x[te][:12]))
    if attributions.shape!=(12,len(FEATURES)):
        raise ValueError("Unexpected SHAP explanation shape")
    importance=np.mean(np.abs(attributions),axis=0)
    return {"project_id":108,"model":"XGBClassifier fitted on training-only SMOTE features",
            "features":FEATURES,
            "original_train_rows":len(tr),"synthetic_smote_train_rows":len(balanced_y),
            "untouched_test_rows":len(te),
            "minority_train_count":int(yt.sum()),
            "minority_after_smote":int(np.sum(balanced_y==1)),
            "heldout_average_precision":round(float(average_precision_score(y[te],score)),5),
            "heldout_roc_auc":round(float(roc_auc_score(y[te],score)),5),
            "shap_engine":"real shap.TreeExplainer on fitted XGBoost",
            "shap_explained_rows":len(attributions),
            "shap_mean_absolute":dict(zip(FEATURES,np.round(importance,6).tolist())),
            "smote_applied_to_test":False,
            "source":"SYNTHETIC industrial bearing fault flags",
            "production_validated":False}
