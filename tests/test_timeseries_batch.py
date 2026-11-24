"""Actual forecasting, forward-chaining, artifact and leakage checks #061–#070."""
from __future__ import annotations
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from timeseries_batch.engine import (
    CONFIG, HORIZON, ORIGINS, PERIODS, errors, evaluate, seasonal_naive,
    splits, synthetic_series, validate_frame,
)

ROOT = Path(__file__).resolve().parents[1]

class TestForecastingBatch(unittest.TestCase):
    def test_ten_distinct_domains_and_deterministic_time_series(self):
        self.assertEqual(set(CONFIG),set(range(61,71)))
        self.assertEqual(len({v["slug"] for v in CONFIG.values()}),10)
        self.assertEqual(len({v["unit"] for v in CONFIG.values()}),10)
        for project in CONFIG:
            with self.subTest(project=project):
                frame=synthetic_series(project)
                validate_frame(project,frame)
                pd.testing.assert_frame_equal(frame,synthetic_series(project))
                self.assertEqual(len(frame),240)
                self.assertTrue((frame.target_value>=0).all())
                self.assertTrue(frame.data_origin.eq("SYNTHETIC").all())
                if project==67:self.assertLessEqual(frame.target_value.max(),100)

    def test_expanding_backtests_never_train_on_future(self):
        for project in CONFIG:
            frame=synthetic_series(project)
            folds=splits(frame)
            self.assertEqual(len(folds),3)
            self.assertEqual([meta["train_rows"] for _,_,meta in folds],list(ORIGINS))
            for train,holdout,meta in folds:
                with self.subTest(project=project,origin=meta["train_rows"]):
                    self.assertEqual(len(holdout),HORIZON)
                    self.assertLess(meta["train_end_date"],meta["validation_start_date"])
                    np.testing.assert_array_equal(
                        train,frame.target_value.iloc[:meta["train_rows"]].to_numpy())
                    np.testing.assert_array_equal(
                        holdout,frame.target_value.iloc[meta["train_rows"]:meta["train_rows"]+HORIZON].to_numpy())
                    self.assertLess(meta["train_rows"]+len(holdout),PERIODS-HORIZON)

    def test_real_estimators_and_untouched_holdout(self):
        for project in CONFIG:
            with self.subTest(project=project):
                report=evaluate(project)
                self.assertEqual(report["project_id"],project)
                self.assertEqual(report["final_train_rows"],232)
                self.assertEqual(report["untouched_test_rows"],8)
                self.assertIn(report["selected_model"],("seasonal_naive","statsmodels_ets"))
                self.assertEqual(set(report["test_metrics"]),{"seasonal_naive","statsmodels_ets","prophet"})
                self.assertEqual(len(report["backtest_folds"]),3)
                self.assertEqual(len(report["actuals"]),8)
                self.assertEqual(len(report["forecasts"]["prophet"]),8)
                self.assertIn("statsmodels ExponentialSmoothing",report["capabilities"])
                self.assertIn("Prophet.fit and predict",report["capabilities"])
                self.assertEqual(report["data_origin"],"SYNTHETIC deterministic simulator")
                for model,metric in report["test_metrics"].items():
                    self.assertGreaterEqual(metric["mae"],0)
                    for key in ("rmse","wape_pct","smape_pct","mape_pct_nonzero"):
                        self.assertTrue(np.isfinite(metric[key]),(project,model,key))
                for low,actual_hi in zip(report["selected_interval_lower"],
                                          report["selected_interval_upper"]):
                    self.assertLessEqual(low,actual_hi)
                self.assertTrue(0 <= report["empirical_interval_coverage"] <= 1)
                self.assertTrue(0 <= report["prophet_interval_coverage"] <= 1)

    def test_future_forecast_has_only_future_dates_and_no_actuals(self):
        from timeseries_batch.engine import forecast_future
        result=forecast_future(61,horizon=8)
        self.assertEqual(result["project_id"],61)
        self.assertEqual(len(result["future_dates"]),8)
        self.assertEqual(len(result["selected_forecast"]),8)
        self.assertEqual(len(result["prophet_forecast"]),8)
        self.assertFalse(result["actual_values_available"])
        self.assertTrue(all(x > result["forecast_origin_date"] for x in result["future_dates"]))
        with self.assertRaises(ValueError):
            forecast_future(61,horizon=0)

    def test_mae_and_seasonal_naive_baseline(self):
        np.testing.assert_equal(seasonal_naive(np.arange(30),horizon=3),[17,18,19])
        metric=errors(np.array([2.,4.]),np.array([3.,4.]))
        self.assertAlmostEqual(metric["mae"],.5)
        self.assertGreater(metric["wape_pct"],0)
        with self.assertRaises(ValueError):
            seasonal_naive(np.array([1,2,3]),horizon=4)
        with self.assertRaises(ValueError):
            errors(np.array([1.,2.]),np.array([1.]))

    def test_malformed_data_rejected(self):
        base=synthetic_series(61)
        variants={}
        d=base.copy();d.loc[0,"target_value"]=float("nan");variants["nan"]=d
        d=base.copy();d.loc[2,"sample_id"]=d.loc[1,"sample_id"];variants["duplicate"]=d
        d=base.copy();d.loc[0,"target_value"]=-1;variants["negative"]=d
        d=base.copy();d.loc[5,"observation_date"]=pd.Timestamp("2020-01-01");variants["nonmonotonic"]=d
        d=base.copy();d.loc[5,"observation_date"]=d.loc[4,"observation_date"];variants["repeat_date"]=d
        d=base.copy();d.loc[5,"observation_date"]=d.loc[5,"observation_date"]+pd.Timedelta(days=2);variants["irregular"]=d
        d=base.copy().iloc[:80];variants["too_few"]=d
        for name,data in variants.items():
            with self.subTest(name=name),self.assertRaises(ValueError):
                validate_frame(61,data)
        with self.assertRaises(ValueError):synthetic_series(61,n=3)
        with self.assertRaises(ValueError):synthetic_series(0)

    def test_run_export_and_html_plot(self):
        with tempfile.TemporaryDirectory() as folder:
            from timeseries_batch import engine
            with patch.object(engine,"ROOT",Path(folder)):
                report=evaluate(61,save=True)
                output=Path(folder)
                self.assertTrue((output/"data/061.csv").exists())
                self.assertTrue((output/"reports/061.json").exists())
                self.assertTrue((output/"reports/061_predictions.csv").exists())
                html=(output/"figures/061.html").read_text()
                self.assertIn("plotly",html.lower())
                self.assertIn("Prophet",html)
                stored=json.loads((output/"reports/061.json").read_text())
                self.assertEqual(stored,report)
                predictions=pd.read_csv(output/"reports/061_predictions.csv")
                self.assertEqual(len(predictions),8)

    def test_canonical_entrypoints_and_pages(self):
        for project,cfg in CONFIG.items():
            folder=ROOT/"projetos"/"07-timeseries"/cfg["slug"]
            with self.subTest(project=project):
                for name in ("main.py","README.md"):
                    self.assertTrue((folder/name).exists())
                self.assertIn("timeseries_batch.engine",(folder/"main.py").read_text())
                page=ROOT/"site"/"cases"/"timeseries"/f"{project:03d}"/"index.html"
                self.assertTrue(page.exists())
        self.assertTrue((ROOT/"site"/"cases"/"timeseries"/"index.html").exists())
        self.assertIn("/cases/timeseries/",(ROOT/"site"/"industrial"/"index.html").read_text())

if __name__=="__main__":
    unittest.main()
