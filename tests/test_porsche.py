from pathlib import Path
import subprocess
import unittest

class PorscheTests(unittest.TestCase):
    def test_physics_invariants(self):
        subprocess.run(['node', str(Path(__file__).with_name('porsche_checks.mjs'))], check=True, timeout=30)
