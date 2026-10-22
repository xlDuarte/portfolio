import unittest
import numpy as np
from classification_batch.engine import CONFIG,synthetic_data,validate,evaluate
class ClassificationBatchTests(unittest.TestCase):
    def test_every_project(self):
        self.assertEqual(set(CONFIG),set(range(31,41)))
        for project in CONFIG:
            with self.subTest(project=project):
                a=synthetic_data(project)
                b=synthetic_data(project)
                self.assertTrue(a.equals(b))
                validate(project,a)
                result=evaluate(project,a)
                self.assertEqual((result["train_rows"],result["calibration_rows"],result["test_rows"]),(360,120,120))
                self.assertEqual(np.array(result["confusion_matrix"]).sum(),120)
                for metric in ("dummy_roc_auc","logistic_roc_auc","gradient_boosting_roc_auc","average_precision","precision","recall","f1","brier_score"):
                    self.assertTrue(0<=result[metric]<=1)
                self.assertIn("synthetic",result["limitation"])
    def test_input_guards(self):
        x=synthetic_data(31)
        with self.assertRaises(ValueError):validate(31,x.assign(sample_id="duplicate"))
        with self.assertRaises(ValueError):validate(31,x.assign(target_flag=2))
        with self.assertRaises(ValueError):validate(31,x.drop(columns=["monthly_orders"]))
        with self.assertRaises(ValueError):validate(31,x.assign(monthly_orders=np.nan))
if __name__=="__main__":unittest.main()
