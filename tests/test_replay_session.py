from pathlib import Path
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ReplaySessionTests(unittest.TestCase):
    def test_engine_parity_and_synchronized_data(self):
        subprocess.run(['node',str(ROOT/'tests/replay_session_checks.mjs')],check=True,timeout=30)
    def test_one_canonical_replay(self):
        hub=(ROOT/'site/motorsport/racing/index.html').read_text()
        self.assertIn("new URL('../../cases/motorsport/109/'",hub)
        page=(ROOT/'site/cases/motorsport/109/index.html').read_text()
        self.assertEqual(page.count('data-lab="109"'),1)
        self.assertIn('replay/replay.mjs',page)
        self.assertNotIn('src="../../../motorsport/lab/lab.mjs"',page)
