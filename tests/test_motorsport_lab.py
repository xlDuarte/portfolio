from pathlib import Path
import subprocess
import shutil
import unittest
ROOT=Path(__file__).resolve().parents[1]
class MotorsportLabTests(unittest.TestCase):
    def test_pages_and_real_captures(self):
        for id in ('101','102','103','104','106','109','111'):
            p=ROOT/'site'/('f1-models/index.html' if id=='111' else f'cases/motorsport/{id}/index.html')
            s=p.read_text()
            self.assertIn(f'data-lab="{id}"',s)
            self.assertIn(f'lab/screenshots/{id}.webp',s)
            self.assertGreater((ROOT/f'site/motorsport/lab/screenshots/{id}.webp').stat().st_size,1000)
    @unittest.skipUnless(shutil.which('node'),'Node.js required')
    def test_computational_engines(self):
        subprocess.run(['node',str(ROOT/'tests/motorsport_lab_checks.mjs')],check=True,timeout=30)
