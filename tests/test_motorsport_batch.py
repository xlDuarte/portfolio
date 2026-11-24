"""Core regression tests for #101-#110; no heavyweight neural dependencies."""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
import numpy as np
from motorsport_batch.race_ml import evaluate as race_fit
from motorsport_batch.cli import execute
from motorsport_batch.replay import render,snapshot
from motorsport_batch.performance import scenario,thermal_grid,damper_histogram,sweep
ROOT=Path(__file__).resolve().parents[1]
SLUGS={
101:"101-f1-predictive-race-strategy-pit-stop-window-simulator",
102:"102-vehicle-dynamics-state-estimation-via-extended-kalman-filter-ekf",
103:"103-motorsport-onboard-video-feature-tracking-motion-calibration",
104:"104-mechanical-vibration-time-series-anomaly-detection-lstm-vs-baseline",
105:"105-industrial-x-ray-ndt-defect-detection-with-cnn-grad-cam",
106:"106-end-to-end-mlops-pipeline-with-mlflow-docker-fastapi",
107:"107-industrial-rag-chatbot-chat-with-engineering-pdfs-sops",
108:"108-explainable-ai-shap-imbalanced-fault-risk-modeling-with-smote",
109:"109-f1-telemetry-race-replay-live-gps-track-position-engine-built-from-scratch",
110:"110-complete-motorsport-performance-engineering-suite-tire-physics-flir-setup-hh-timing-laptime-sim"
}
def load(n):
    file=ROOT/"projetos"/"11-motorsport-f1-mlops"/SLUGS[n]/"main.py"
    s=importlib.util.spec_from_file_location(f"project_{n}",file)
    obj=importlib.util.module_from_spec(s)
    sys.modules[s.name]=obj
    s.loader.exec_module(obj)
    return obj

class TestMotorsportCore(unittest.TestCase):
    def test_actual_xgb_and_rf_models_101(self):
        r=race_fit()
        self.assertEqual(r["project_id"],101)
        self.assertTrue(r["session_disjoint"])
        self.assertEqual(set(r["test_mae_seconds"]),{"RandomForestRegressor","XGBRegressor"})
        self.assertTrue(all(np.isfinite(x) and x>=0 for x in r["test_mae_seconds"].values()))
        self.assertGreater(r["train_sessions"],10)
        self.assertGreater(r["test_laps"],0)
    def test_existing_physics_pit_101_preserved(self):
        m=load(101)
        ranked=m.evaluate_pit_strategies(total_laps=17)
        self.assertTrue(ranked)
        self.assertTrue(all(a["total_time_s"]<=b["total_time_s"] for a,b in zip(ranked,ranked[1:])))
        self.assertIn("XGBRegressor",m.fit_synthetic_lap_models()["algorithms_fit"])
    def test_existing_ekf_102_preserved(self):
        m=load(102)
        r=m.run_ekf_sideslip_estimation(n_steps=80,dt=.02)
        self.assertGreaterEqual(r["rmse_deg"],0)
        self.assertTrue(np.isfinite(r["final_beta_deg"]))
    def test_opencv_103_real_features(self):
        m=load(103)
        r=m.run()
        self.assertIn("OpenCV",r["algorithm"])
        self.assertLess(r["endpoint_error_px"],2.5)
        self.assertGreater(r["tracked_features"],20)
    def test_104_to_108_domain_specific_inputs(self):
        for p in range(104,109):
            with self.subTest(p=p):
                r=execute(p,run=False)
                self.assertEqual(r["project_id"],p)
                self.assertFalse(r["requested_full_execution"])
                self.assertIn("source",r)
    def test_109_original_replay_and_interactive_render(self):
        circuit,leaders=snapshot(1200)
        self.assertEqual(len(leaders),3)
        self.assertEqual([x["position"] for x in leaders],[1,2,3])
        self.assertTrue(all(x["speed_kmh"]>0 for x in leaders))
        fig,items=render(750)
        self.assertEqual(len(fig.data),2)
        self.assertEqual(len(items),3)
        self.assertEqual(circuit.length_m,4309.)
        with self.assertRaises(ValueError):snapshot(-1)
    def test_110_five_day_proxy_and_tire_thermal(self):
        results=scenario()
        self.assertEqual(set(results),{"day1","day2_tire","day2_thermal","day3_balance",
                                       "day4_qss_proxy","day5_event_checklist","damper_histogram"})
        self.assertTrue(results["day5_event_checklist"]["engineer_signoff_required"])
        self.assertEqual(thermal_grid().shape,(30,90))
        self.assertEqual(sum(damper_histogram().values()),1200)
        self.assertEqual(len(sweep()),18)
    def test_all_docs_sites_and_new_code(self):
        for i,slug in SLUGS.items():
            with self.subTest(project=i):
                folder=ROOT/"projetos"/"11-motorsport-f1-mlops"/slug
                self.assertTrue((folder/"README.md").is_file())
                self.assertTrue((folder/"main.py").is_file())
                self.assertTrue((ROOT/"site"/"cases"/"motorsport"/str(i)/"index.html").is_file())
        self.assertTrue((ROOT/"site"/"cases"/"motorsport"/"index.html").is_file())
        self.assertIn("/cases/motorsport/",(ROOT/"site"/"automotivo"/"index.html").read_text())
    def test_cli_104_synthetic_input_only(self):
        path=ROOT/"projetos"/"11-motorsport-f1-mlops"/SLUGS[104]/"main.py"
        outcome=subprocess.run([sys.executable,str(path)],capture_output=True,text=True,timeout=25,check=True)
        self.assertEqual(json.loads(outcome.stdout)["project_id"],104)
class TestCalibratedLap(unittest.TestCase):
    def test_bahrain_lap_matches_calibration_and_reacts_to_mass(self):
        from motorsport_batch.performance import bahrain_lap
        base = bahrain_lap()
        self.assertLess(abs(base["lap_time_s"] - base["measured_lap_s"]), 0.5)
        heavier = bahrain_lap(mass=952.0)
        self.assertGreater(heavier["lap_time_s"], base["lap_time_s"] + 0.5)


if __name__=="__main__":unittest.main()
