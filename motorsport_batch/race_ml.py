"""Actual XGBoost/RandomForest lap-time fit for project #101 (synthetic sessions).

Legacy physics pit-window enumerator is preserved in its original main.py.
Fits supervised models on synthetic historical sessions; evaluates on
session-disjoint holdout and compares a physical no-ML baseline.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

FEATURES=["tyre_age_laps","fuel_kg","air_temp_c","track_temp_c","compound_soft","compound_medium","compound_hard"]
def make_laps(seed=101,n_sessions=42,laps_per_session=20):
    if not 10<=n_sessions<=100 or not 10<=laps_per_session<=50:
        raise ValueError("Invalid synthetic race session dimensions")
    rng=np.random.default_rng(seed)
    rows=[]
    for session in range(n_sessions):
        compound=["SOFT","MEDIUM","HARD"][session%3]
        air=float(rng.uniform(19,34))
        track=air+float(rng.uniform(7,20))
        car_offset=float(rng.normal(0,.28))
        for age in range(laps_per_session):
            fuel=max(5.,105-.91*age)
            curve={"SOFT":(.085,.0028,-.65),"MEDIUM":(.048,.0014,0.),"HARD":(.026,.0007,.45)}[compound]
            secs=80.8+curve[2]+fuel*.017+curve[0]*age+curve[1]*age*age+(track-32)*.018+car_offset+float(rng.normal(0,.16))
            rows.append({"session":session,"tyre_age_laps":age,"fuel_kg":fuel,
                         "air_temp_c":air,"track_temp_c":track,
                         "compound_soft":int(compound=="SOFT"),
                         "compound_medium":int(compound=="MEDIUM"),
                         "compound_hard":int(compound=="HARD"),
                         "lap_time_s":round(secs,5)})
    return pd.DataFrame(rows)

def evaluate(seed=101):
    frame=make_laps(seed)
    groups=frame.session.to_numpy()
    tr,te=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=seed).split(frame,groups=groups))
    xtrain=frame.iloc[tr][FEATURES];ytrain=frame.lap_time_s.iloc[tr]
    xtest=frame.iloc[te][FEATURES];ytest=frame.lap_time_s.iloc[te]
    estimators={
        "RandomForestRegressor":RandomForestRegressor(n_estimators=90,min_samples_leaf=2,random_state=seed,n_jobs=1),
        "XGBRegressor":XGBRegressor(n_estimators=120,max_depth=3,learning_rate=.07,
                                   subsample=.9,colsample_bytree=.9,objective="reg:squarederror",
                                   random_state=seed,n_jobs=1)}
    scores={}
    for name,model in estimators.items():
        model.fit(xtrain,ytrain)
        scores[name]=round(float(mean_absolute_error(ytest,model.predict(xtest))),6)
    base=float(ytrain.median())
    return {"project_id":101,"source":"SYNTHETIC fictitious lap observations",
            "train_sessions":int(frame.session.iloc[tr].nunique()),
            "heldout_sessions":int(frame.session.iloc[te].nunique()),
            "session_disjoint":not bool(set(groups[tr]) & set(groups[te])),
            "train_laps":len(tr),"test_laps":len(te),
            "test_mae_seconds":scores,
            "median_baseline_mae_seconds":round(float(mean_absolute_error(ytest,np.full(len(te),base))),6),
            "algorithms_fit":list(scores),
            "physical_pit_strategy_model":"See preserved project main.py enumerator",
            "limitations":"No FastF1 race results, weather feed, validated physical tire model, or real team strategy."}
