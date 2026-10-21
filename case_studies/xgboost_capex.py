"""Actual XGBoost regression evaluated on the versioned synthetic CAPEX dataset.

Data here are synthetic; validation only demonstrates working ML, not industrial ROI.
"""
from __future__ import annotations
import json
import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from .analytics import load


def evaluate_xgboost_capex():
    frame = load('capex_projects.csv').sort_values('project_id')
    features = ['area_m2','robots','utilities_complexity']
    assert frame.project_id.is_unique and frame[features + ['actual_capex_brl']].notna().all().all()
    n=int(0.8*len(frame))
    train, test=frame.iloc[:n],frame.iloc[n:]
    xtr, xte = train[features],test[features]
    ytr, yte = train.actual_capex_brl,test.actual_capex_brl
    baseline=DummyRegressor(strategy='mean').fit(xtr,ytr)
    estimator=XGBRegressor(n_estimators=90,max_depth=3,learning_rate=0.075,
                           objective='reg:squarederror',subsample=0.9,
                           colsample_bytree=1.0,n_jobs=1,random_state=2026)
    estimator.fit(xtr,ytr)
    predictions=estimator.predict(xte)
    assert predictions.shape==(len(test),) and np.isfinite(predictions).all()
    return {
       'case':'CAPEX cost model — actual XGBoost estimator',
       'data_provenance':'SYNTHETIC deterministic CSV; no industrial observations',
       'estimator':type(estimator).__name__,
       'xgboost_trained':True,'n_train':len(train),'n_test':len(test),
       'features':features,'split':'80/20 sorted project_id (synthetic, NOT temporal)',
       'test_mae_brl':round(float(mean_absolute_error(yte,predictions)),2),
       'test_rmse_brl':round(float(np.sqrt(mean_squared_error(yte,predictions))),2),
       'baseline_mae_brl':round(float(mean_absolute_error(yte,baseline.predict(xte))),2),
       'feature_importance':{k:round(float(v),5) for k,v in zip(features,estimator.feature_importances_)},
       'validation_note':'Holdout evaluated once; do not interpret as external generalization.'
    }

if __name__=='__main__':
    print(json.dumps(evaluate_xgboost_capex(),ensure_ascii=False,indent=2))
