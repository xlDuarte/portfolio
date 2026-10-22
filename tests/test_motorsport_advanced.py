"""Heavy real models; run only when RUN_MOTORSPORT_ADVANCED=1 in dedicated CI."""
import os
import tempfile
import unittest
from pathlib import Path
import numpy as np

class TestRealAdvancedModels(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("RUN_MOTORSPORT_TF")=="1","requires TensorFlow CI job")
    def test_104_genuine_lstm_training(self):
        from motorsport_batch.vibration import evaluate
        r=evaluate(epochs=2)
        self.assertEqual(r["project_id"],104)
        self.assertEqual(r["trained_epoch_count"],2)
        self.assertGreater(r["last_train_loss"],0)
        self.assertEqual(r["untouched_test_fault"],72)
        for name in ("lstm","rms_threshold_baseline"):
            self.assertTrue(0<=r[name]["f1"]<=1)
    @unittest.skipUnless(os.environ.get("RUN_MOTORSPORT_TF")=="1","requires TensorFlow CI job")
    def test_105_real_convnet_gradient_tape_gradcam(self):
        from motorsport_batch.xray import evaluate
        r=evaluate(epochs=2)
        self.assertEqual(r["project_id"],105)
        self.assertEqual(r["train_samples"],120)
        self.assertEqual(r["untouched_test_samples"],24)
        self.assertEqual(r["gradcam_masks_computed"],12)
        self.assertTrue(0<=r["test_accuracy"]<=1)
        self.assertTrue(0<=r["gradcam_mean_iou_on_synthetic_voids"]<=1)
        self.assertEqual(np.asarray(r["example_gradcam_heatmap"]).shape,(64,64))
    @unittest.skipUnless(os.environ.get("RUN_MOTORSPORT_ADVANCED")=="1","requires MLflow/RAG/SHAP CI job")
    def test_106_mlflow_runs_and_loadable_artifact(self):
        from motorsport_batch.mlops import run
        with tempfile.TemporaryDirectory() as directory:
            r=run(directory)
            self.assertEqual(r["experiments_run"],2)
            self.assertTrue(r["model_reloaded"])
            self.assertGreaterEqual(r["psi_synthetic_shift"],0)
            self.assertEqual(r["tracking_store"],"real local MLflow file store")
            self.assertFalse(r["registry_configured"])
            self.assertTrue((Path(directory)/"mlruns").is_dir())
    @unittest.skipUnless(os.environ.get("RUN_MOTORSPORT_ADVANCED")=="1","requires MLflow/RAG/SHAP CI job")
    def test_107_actual_pdfs_and_langchain_runnable(self):
        from motorsport_batch.rag import build_demo_pdfs,ingest_pdfs,runnable
        with tempfile.TemporaryDirectory() as directory:
            pdfs=build_demo_pdfs(directory)
            self.assertEqual(len(pdfs),3)
            docs=ingest_pdfs(pdfs)
            self.assertGreaterEqual(len(docs),6)
            r=runnable(pdfs).invoke("How to inspect pump bearing vibration RMS?")
            self.assertTrue(r["evidence"])
            self.assertEqual(r["evidence"][0]["filename"],"fictional-pump-maintenance.pdf")
            self.assertIn("p.",r["answer"])
            self.assertFalse(r["llm_called"])
            self.assertTrue(r["pdf_pages_extracted"]>=6)
    @unittest.skipUnless(os.environ.get("RUN_MOTORSPORT_ADVANCED")=="1","requires MLflow/RAG/SHAP CI job")
    def test_108_smote_and_real_shap(self):
        from motorsport_batch.explain import evaluate
        r=evaluate()
        self.assertGreater(r["synthetic_smote_train_rows"],r["original_train_rows"])
        self.assertEqual(r["shap_explained_rows"],12)
        self.assertFalse(r["smote_applied_to_test"])
        self.assertEqual(len(r["shap_mean_absolute"]),4)
        self.assertTrue(0<=r["heldout_average_precision"]<=1)
if __name__=="__main__":unittest.main()
