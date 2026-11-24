"""Reproducible industrial forecasting case studies #061-#070.

All series are deterministically SYNTHETIC, not real quotes, emissions, weather,
manufacturing readings or industrial transactions. Actual statsmodels and Prophet
estimators run without accessing future observations. Plotly renders evaluated
out-of-sample forecasts. No production validation or business impact claimed.
"""
from __future__ import annotations
import argparse
import json
import logging
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
CONFIG = {int(k):v for k,v in json.loads((ROOT / "config.json").read_text(encoding="utf-8")).items()}
ORIGINS = (168, 192, 216)
HORIZON = 8
PERIODS = 240
SEASONAL_LAG = 13

def synthetic_series(project: int, n: int = PERIODS, seed: int = 2026) -> pd.DataFrame:
    if project not in CONFIG:
        raise ValueError("Unknown project")
    if not isinstance(n,int) or isinstance(n,bool) or not 240 <= n <= 2000:
        raise ValueError("n must be an integer between 240 and 2000")
    c = CONFIG[project]
    rng = np.random.default_rng(seed + project)
    t = np.arange(n,dtype=float)
    annual = np.sin(2*np.pi*t/52 + project/5)
    quarterly = np.sin(2*np.pi*t/13 + project/7)
    # Numeric levels and yearly/quarterly seasonality are physically plausible
    # SIMULATIONS. Innovations are independent of future information.
    shock = np.zeros(n)
    epsilon = rng.normal(0,c["noise_sigma"],n)
    for i in range(1,n):
        shock[i] = 0.37*shock[i-1] + epsilon[i]
    structural = (t >= 138).astype(float) * c["season_amplitude"] * .17
    if project == 68:
        structural = (t >= 138).astype(float) * .22
    y = (c["base"] + c["trend_per_week"]*t +
         c["season_amplitude"]*(.70*annual+.30*quarterly) +
         structural + shock)
    if project == 68:
        y = np.maximum(y,.05)
    elif project == 67:
        y = np.clip(y,0,100)
    else:
        y = np.maximum(y,0)
    dates = pd.date_range("2021-01-04",periods=n,freq="W-MON")
    return pd.DataFrame({"observation_date":dates,"target_value":np.round(y,5),
                         "sample_id":[f"P{project:03d}-{i:05d}" for i in range(n)],
                         "data_origin":"SYNTHETIC"})

def validate_frame(project: int, frame: pd.DataFrame) -> None:
    if project not in CONFIG:
        raise ValueError("Unknown project")
    required = {"observation_date","target_value","sample_id","data_origin"}
    if not required.issubset(frame.columns) or len(frame) < PERIODS:
        raise ValueError("Missing columns or too few observations")
    if frame[list(required)].isna().any().any() or frame.sample_id.duplicated().any():
        raise ValueError("Missing values or duplicated IDs")
    ds = pd.to_datetime(frame.observation_date,errors="coerce")
    if ds.isna().any() or ds.duplicated().any() or not ds.is_monotonic_increasing:
        raise ValueError("Time index must be complete, sorted, and unique")
    expected = pd.date_range(ds.iloc[0],periods=len(ds),freq="W-MON")
    if not (ds.to_numpy() == expected.to_numpy()).all():
        raise ValueError("Missing/irregular weekly timestamps")
    values = pd.to_numeric(frame.target_value, errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Invalid numeric target")
    if project == 67 and (values>100).any():
        raise ValueError("Occupancy must be 0-100 percent")
    if not frame.data_origin.eq("SYNTHETIC").all():
        raise ValueError("Provenance is not synthetic")

def _clip(project: int, forecast: np.ndarray) -> np.ndarray:
    pred = np.maximum(0,np.asarray(forecast,dtype=float))
    return np.minimum(pred,100) if project == 67 else pred

def seasonal_naive(history: np.ndarray, horizon: int=HORIZON) -> np.ndarray:
    if len(history) < SEASONAL_LAG:
        raise ValueError("Insufficient seasonal history")
    if not 1 <= horizon <= SEASONAL_LAG:
        raise ValueError("Supported horizon 1..13 weeks")
    return np.asarray(history[-SEASONAL_LAG:][:horizon],dtype=float)

def statsmodels_forecast(history: np.ndarray, horizon: int, project: int) -> np.ndarray:
    if len(history) < 2*SEASONAL_LAG:
        raise ValueError("Insufficient history to train ETS")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        fitted = ExponentialSmoothing(
            history, trend="add", damped_trend=True, seasonal="add",
            seasonal_periods=SEASONAL_LAG, initialization_method="estimated"
        ).fit(optimized=True, use_brute=False)
    predicted = np.asarray(fitted.forecast(horizon),dtype=float)
    if not np.isfinite(predicted).all():
        raise ValueError("Nonfinite ETS forecast")
    return _clip(project,predicted)

def prophet_forecast(history: pd.DataFrame, horizon: int, project: int) -> dict:
    try:
        from prophet import Prophet
    except ImportError as exc:
        raise RuntimeError("Prophet is required; install requirements/timeseries.txt") from exc
    logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
    logging.getLogger("prophet").setLevel(logging.WARNING)
    frame = pd.DataFrame({"ds":pd.to_datetime(history.observation_date),
                          "y":history.target_value.to_numpy(dtype=float)})
    model = Prophet(
        yearly_seasonality=5, weekly_seasonality=False, daily_seasonality=False,
        seasonality_mode="additive", interval_width=.8, uncertainty_samples=100,
        mcmc_samples=0, changepoint_prior_scale=.08,
    )
    model.fit(frame)
    future = pd.DataFrame({"ds":pd.date_range(frame.ds.iloc[-1]+pd.Timedelta(days=7),
                                              periods=horizon, freq="W-MON")})
    forecast = model.predict(future)
    values = _clip(project,forecast.yhat.to_numpy(dtype=float))
    lower = _clip(project,forecast.yhat_lower.to_numpy(dtype=float))
    upper = _clip(project,forecast.yhat_upper.to_numpy(dtype=float))
    return {"forecast":values,"lower":np.minimum(lower,upper),
            "upper":np.maximum(lower,upper),"model":"Prophet additive with yearly seasonality"}

def errors(y: np.ndarray, predicted: np.ndarray) -> dict:
    y=np.asarray(y,dtype=float)
    pred=np.asarray(predicted,dtype=float)
    if len(y)!=len(pred) or len(y)==0 or not np.isfinite(pred).all():
        raise ValueError("Invalid forecast vector")
    diff = np.abs(y-pred)
    denom = np.maximum((np.abs(y)+np.abs(pred))/2,1e-6)
    return {"mae":round(float(diff.mean()),5),
            "rmse":round(float(np.sqrt(np.mean((y-pred)**2))),5),
            "wape_pct":round(float(100*diff.sum()/max(float(np.abs(y).sum()),1e-6)),5),
            "smape_pct":round(float(100*np.mean(diff/denom)),5),
            "mape_pct_nonzero":round(float(100*np.mean(diff/np.maximum(np.abs(y),1e-6))),5)}

def splits(frame: pd.DataFrame) -> list[tuple[np.ndarray,np.ndarray,dict]]:
    """Expanding window training; no future observations reach any forecast fit."""
    y = frame.target_value.to_numpy(dtype=float)
    results = []
    for origin in ORIGINS:
        train, actual = y[:origin].copy(),y[origin:origin+HORIZON].copy()
        assert len(actual)==HORIZON and origin+HORIZON < PERIODS-HORIZON
        results.append((train,actual,{"train_end_date":str(frame.observation_date.iloc[origin-1].date()),
                                      "validation_start_date":str(frame.observation_date.iloc[origin].date()),
                                      "train_rows":origin,"validation_rows":HORIZON}))
    return results

def evaluate(project: int,frame: pd.DataFrame | None=None,save: bool=False) -> dict:
    if frame is None:
        frame=synthetic_series(project)
    else:
        frame=frame.copy()
    frame["observation_date"]=pd.to_datetime(frame["observation_date"])
    validate_frame(project,frame)
    if len(frame) != PERIODS:
        raise ValueError("Use exact 240 weekly observations in this reproducible benchmark")
    all_y = frame.target_value.to_numpy(dtype=float)
    backtest = []
    residuals = {"seasonal_naive":[],"statsmodels_ets":[]}
    for train, actual, meta in splits(frame):
        # Each model sees strictly historical y up to meta.train_end_date.
        predictions = {
            "seasonal_naive":_clip(project,seasonal_naive(train,HORIZON)),
            "statsmodels_ets":statsmodels_forecast(train,HORIZON,project),
        }
        row={"fold":len(backtest)+1,**meta,"model_metrics":{}}
        for model,pred in predictions.items():
            residuals[model].extend((actual-pred).tolist())
            row["model_metrics"][model]=errors(actual,pred)
        backtest.append(row)
    means={name:round(float(np.mean([fold["model_metrics"][name]["mae"] for fold in backtest])),5)
           for name in residuals}
    selected=min(means,key=lambda name:(means[name],name))
    test_start = PERIODS-HORIZON
    observed = all_y[test_start:]
    training = all_y[:test_start]
    candidate_preds={
        "seasonal_naive":_clip(project,seasonal_naive(training,HORIZON)),
        "statsmodels_ets":statsmodels_forecast(training,HORIZON,project),
    }
    # Prophet is FIT using the training window only, scored on the untouched
    # test, and explicitly not selected according to test-set performance.
    prophet=prophet_forecast(frame.iloc[:test_start],HORIZON,project)
    candidate_preds["prophet"]=prophet["forecast"]
    q=float(np.quantile(np.abs(residuals[selected]),.8,method="higher"))
    selected_pred = candidate_preds[selected]
    empirical_low=_clip(project,selected_pred-q)
    empirical_high=_clip(project,selected_pred+q)
    test_metrics={name:errors(observed,pred) for name,pred in candidate_preds.items()}
    result = {
        "project_id":project,"title":CONFIG[project]["title"],
        "unit":CONFIG[project]["unit"],"data_origin":"SYNTHETIC deterministic simulator",
        "cadence":"weekly (Monday)","total_rows":PERIODS,
        "model_selection":"lowest validation MAE over three expanding-origin folds, comparing naive and ETS only",
        "backtest_folds":backtest,"validation_mae":means,
        "selected_model":selected,
        "final_train_rows":test_start,"untouched_test_rows":HORIZON,
        "test_start_date":str(frame.observation_date.iloc[test_start].date()),
        "test_end_date":str(frame.observation_date.iloc[-1].date()),
        "test_metrics":test_metrics,
        "interval_note":"ETS-selected empirical 80th percentile historical absolute residual, not guaranteed coverage",
        "empirical_interval_coverage":round(float(np.mean((observed>=empirical_low)&(observed<=empirical_high))),5),
        "prophet_interval_note":"Prophet 80 percent model interval, uncalibrated; diagnostic only",
        "prophet_interval_coverage":round(float(np.mean((observed>=prophet["lower"]) & (observed<=prophet["upper"]))),5),
        "actuals":np.round(observed,5).tolist(),
        "forecasts":{name:np.round(pred,5).tolist() for name,pred in candidate_preds.items()},
        "selected_interval_lower":np.round(empirical_low,5).tolist(),
        "selected_interval_upper":np.round(empirical_high,5).tolist(),
        "prophet_lower":np.round(prophet["lower"],5).tolist(),
        "prophet_upper":np.round(prophet["upper"],5).tolist(),
        "capabilities":["Pandas","NumPy","statsmodels ExponentialSmoothing",
                        "Prophet.fit and predict","Plotly graphs"],
        "limitations":"All target data are synthetic. No real forecast accuracy, actual commodities/weather/FX, ESG certification or observed industrial benefit."
    }
    if save:
        for directory in ("data","reports","figures"):
            (ROOT / directory).mkdir(exist_ok=True)
        frame.to_csv(ROOT/"data"/f"{project:03d}.csv",index=False)
        (ROOT/"reports"/f"{project:03d}.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        predictions=pd.DataFrame({
            "date":frame.observation_date.iloc[test_start:].dt.strftime("%Y-%m-%d"),
            "actual":observed,
            "seasonal_naive":candidate_preds["seasonal_naive"],
            "statsmodels_ets":candidate_preds["statsmodels_ets"],
            "prophet":candidate_preds["prophet"],
            "selected_lower":empirical_low,"selected_upper":empirical_high,
            "prophet_lower":prophet["lower"],"prophet_upper":prophet["upper"],
        })
        predictions.to_csv(ROOT/"reports"/f"{project:03d}_predictions.csv",index=False)
        figure=go.Figure()
        figure.add_trace(go.Scatter(x=frame.observation_date.iloc[-78:], y=all_y[-78:],
                                    mode="lines",name="Historical + actual (synthetic)"))
        future_dates=frame.observation_date.iloc[test_start:]
        figure.add_trace(go.Scatter(x=future_dates,y=selected_pred,
                                    mode="lines+markers",name=f"Chosen: {selected}"))
        figure.add_trace(go.Scatter(x=future_dates,y=prophet["forecast"],
                                    mode="lines+markers",name="Prophet (diagnostic)"))
        figure.add_trace(go.Scatter(x=future_dates,y=empirical_low,mode="lines",
                                    line={"width":0},showlegend=False))
        figure.add_trace(go.Scatter(x=future_dates,y=empirical_high,mode="lines",
                                    fill="tonexty",name="Historical error band (unverified coverage)",
                                    line={"width":0}))
        figure.update_layout(title=f"#{project:03d}: synthetic forecasting holdout",
                             xaxis_title="Week",yaxis_title=CONFIG[project]["unit"],
                             template="plotly_dark")
        figure.write_html(ROOT/"figures"/f"{project:03d}.html",
                          include_plotlyjs=True,full_html=True)
    return result


def forecast_future(project: int, frame: pd.DataFrame | None=None,
                    horizon: int=HORIZON, save: bool=False) -> dict:
    """Forecast FUTURE weeks beyond observed history with models fitted only on past."""
    if not isinstance(horizon,int) or isinstance(horizon,bool) or not 1<=horizon<=HORIZON:
        raise ValueError("Future forecasting horizon must be between 1 and 8 weeks")
    frame=synthetic_series(project) if frame is None else frame.copy()
    frame["observation_date"]=pd.to_datetime(frame["observation_date"])
    validate_frame(project,frame)
    if len(frame)!=PERIODS:
        raise ValueError("This benchmark expects 240 weekly observations")
    val= splits(frame)
    validation_mae={}
    for model in ("seasonal_naive","statsmodels_ets"):
        scores=[]
        for train,actual,_ in val:
            pred=(seasonal_naive(train,HORIZON) if model=="seasonal_naive"
                  else statsmodels_forecast(train,HORIZON,project))
            scores.append(float(np.mean(np.abs(actual-_clip(project,pred)))))
        validation_mae[model]=round(float(np.mean(scores)),5)
    selected=min(validation_mae,key=lambda name:(validation_mae[name],name))
    history=frame.target_value.to_numpy(dtype=float)
    fitted={
        "seasonal_naive":_clip(project,seasonal_naive(history,horizon)),
        "statsmodels_ets":statsmodels_forecast(history,horizon,project),
        "prophet":prophet_forecast(frame,horizon,project),
    }
    dates=pd.date_range(frame.observation_date.iloc[-1]+pd.Timedelta(days=7),
                        periods=horizon,freq="W-MON")
    result={
        "project_id":project,"data_origin":"SYNTHETIC",
        "forecast_origin_date":str(frame.observation_date.iloc[-1].date()),
        "future_dates":dates.strftime("%Y-%m-%d").tolist(),
        "selected_model":selected,
        "selection_validation_mae":validation_mae,
        "selected_forecast":np.round(fitted[selected],5).tolist(),
        "prophet_forecast":np.round(fitted["prophet"]["forecast"],5).tolist(),
        "prophet_uncalibrated_lower":np.round(fitted["prophet"]["lower"],5).tolist(),
        "prophet_uncalibrated_upper":np.round(fitted["prophet"]["upper"],5).tolist(),
        "actual_values_available":False,
        "limitations":"Simulated weekly series; forecast is not verified against future measurements",
    }
    if save:
        (ROOT/"reports").mkdir(exist_ok=True)
        (ROOT/"reports"/f"{project:03d}_future.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result

def cli(project: int | None=None):
    parser=argparse.ArgumentParser(description="10 real forecasts of synthetic time series")
    if project is None:
        parser.add_argument("project",type=int,choices=sorted(CONFIG))
    parser.add_argument("--save",action="store_true")
    parser.add_argument("--future",action="store_true",help="Forecast eight future weeks beyond synthetic history")
    args=parser.parse_args()
    chosen=project if project is not None else args.project
    result=(forecast_future(chosen,save=args.save) if args.future else evaluate(chosen,save=args.save))
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    cli()
