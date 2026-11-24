"""Home hero prototype: the payload must stay faithful to the repository data."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERO = ROOT / "site" / "assets" / "hero"


class TestHeroData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = (HERO / "hero-data.json").read_bytes()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_hero_data.py")], check=True, capture_output=True)
        cls.data = json.loads((HERO / "hero-data.json").read_text(encoding="utf-8"))

    def test_regeneration_is_deterministic(self):
        self.assertEqual(self.before, (HERO / "hero-data.json").read_bytes())

    def test_oee_matches_case_study(self):
        metrics = json.loads((ROOT / "case_studies" / "reports" / "metrics.json").read_text(encoding="utf-8"))
        self.assertAlmostEqual(self.data["industrial"]["oee_weighted"] * 100, metrics["oee"]["oee_weighted_pct"], places=1)
        self.assertEqual(self.data["industrial"]["origin"], "synthetic")

    def test_f1_replay_is_observed_and_complete(self):
        f1 = self.data["f1"]
        self.assertEqual(f1["origin"], "observed")
        self.assertEqual([c["code"] for c in f1["cars"]], ["VER", "PER", "SAI"])
        for car in f1["cars"]:
            self.assertEqual(len(car["samples"]), 240 * f1["sample_hz"])
        self.assertEqual(len(f1["track"]["points"]), 360)

    def test_home_carries_the_hero_and_the_prototype_is_retired(self):
        for name in ("hero.js", "hero.css", "hero-fallback.svg"):
            self.assertTrue((HERO / name).is_file(), name)
        home = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn('import("/assets/hero/hero.js")', home)
        self.assertIn('class="stage"', home)
        self.assertFalse((ROOT / "site" / "prototipos" / "heroi" / "index.html").exists())
        vercel = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
        self.assertIn({"source": "/prototipos/heroi/", "destination": "/", "permanent": True}, vercel["redirects"])

    def test_home_numbers_come_from_the_payload(self):
        home = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        oee = f'{self.data["industrial"]["oee_weighted"] * 100:.1f}%'.replace(".", ",")
        self.assertIn(f"<strong data-oee>{oee}</strong>", home)
        self.assertIn(f'de {self.data["f1"]["race_laps"]}</strong>', home)

    def test_caption_states_the_display_exaggeration_used_in_code(self):
        import re
        code = (ROOT / "frontend" / "hero" / "f1.js").read_text(encoding="utf-8")
        factor = re.search(r"elevation:\s*(\d+),", code).group(1)
        home = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn(f"exagerado <span data-elevation>{factor}</span> vezes", home)

    def test_derived_physics_is_plausible(self):
        """Accelerations and disc temperatures must sit inside physically plausible bands for an F1 car."""
        for car in self.data["f1"]["cars"]:
            s = car["summary"]
            self.assertTrue(2.5 <= s["a_lat_g_max"] <= 6.5, (car["code"], s))
            self.assertTrue(-6.5 <= s["a_long_g_min"] <= -2.0, (car["code"], s))
            self.assertTrue(0.8 <= s["a_long_g_max"] <= 2.2, (car["code"], s))
            lo, hi = s["brake_disc_c_range"]
            self.assertTrue(150 <= lo < hi <= 1200, (car["code"], s))


if __name__ == "__main__":
    unittest.main()
