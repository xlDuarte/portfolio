"""Actually fit TensorFlow and PyTorch CNNs; training data never use test seeds."""
import unittest
import os
import numpy as np
from vision_batch.engine import train_tensorflow_ppe,train_torch_microstructure

@unittest.skipUnless(os.environ.get("RUN_VISION_DEEP")=="1", "CNN fitting is validated in separate dedicated GitHub Actions job")
class DeepVisionAcceptance(unittest.TestCase):
    def test_tensorflow_trains_real_conv2d(self):
        r=train_tensorflow_ppe()
        self.assertIn("TensorFlow/Keras",r["architecture"])
        self.assertEqual((r["train_rows"],r["unseen_test_rows"]),(32,2))
        self.assertEqual(len(r["losses"]),2)
        self.assertTrue(all(np.isfinite(r["losses"])))
        self.assertEqual(np.asarray(r["test_probabilities"]).shape,(2,2))
        np.testing.assert_allclose(np.sum(r["test_probabilities"],axis=1),1,atol=1e-4)
    def test_torch_trains_real_conv2d(self):
        r=train_torch_microstructure()
        self.assertIn("PyTorch",r["architecture"])
        self.assertEqual((r["train_rows"],r["unseen_test_rows"]),(48,3))
        self.assertEqual(len(r["training_losses"]),3)
        self.assertTrue(all(np.isfinite(r["training_losses"])))
        self.assertEqual(np.asarray(r["test_probabilities"]).shape,(3,3))
        np.testing.assert_allclose(np.sum(r["test_probabilities"],axis=1),1,atol=1e-4)
if __name__=="__main__":unittest.main()
