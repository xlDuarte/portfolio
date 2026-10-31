from pathlib import Path
import unittest,subprocess
class RealF1Tests(unittest.TestCase):
 def test_observed_data_and_causal_features(self):
  subprocess.run(['node',str(Path(__file__).with_name('real_f1_checks.mjs'))],check=True,timeout=30)
