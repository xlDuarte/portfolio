from pathlib import Path
import subprocess
import unittest

class TelemetryTests(unittest.TestCase):
    def test_model_and_metrics(self):
        subprocess.run(['node', str(Path(__file__).with_name('telemetry_checks.mjs'))], check=True, timeout=30)
