from pathlib import Path
import subprocess
import unittest

class StrategyTests(unittest.TestCase):
    def test_model_totals(self):
        subprocess.run(['node', str(Path(__file__).with_name('strategy_checks.mjs'))], check=True, timeout=30)
