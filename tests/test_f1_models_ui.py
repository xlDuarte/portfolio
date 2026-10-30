from pathlib import Path
import subprocess
import unittest

class F1ModelsUITests(unittest.TestCase):
    def test_simulation_and_report(self):
        subprocess.run(['node', str(Path(__file__).with_name('f1_models_checks.mjs'))], check=True, timeout=30)
