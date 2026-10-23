"""Basic acceptance checks for three independently navigable portfolio entrances."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

class TestPortfolioPortalSplit(unittest.TestCase):
    def test_entrances_exist(self):
        for rel in ("index.html", "industry/index.html", "motorsport/index.html"):
            with self.subTest(path=rel):
                self.assertTrue((SITE/rel).is_file())

    def test_homepage_has_exactly_two_main_choices(self):
        home=(SITE/"index.html").read_text(encoding="utf-8")
        self.assertEqual(home.count('class="choice industry"'),1)
        self.assertEqual(home.count('class="choice racing"'),1)
        self.assertIn('href="./industry/"', home)
        self.assertIn('href="./motorsport/"', home)
        self.assertIn('id="sobre"', home)
        self.assertIn('Gabriel', home)

    def test_industry_retains_original_routes(self):
        industry=(SITE/"industry/index.html").read_text(encoding="utf-8")
        for token in ('function renderAll()', '#/f1-racing', '#/home', 'githubRepoBase'):
            self.assertIn(token,industry)
        self.assertIn('href="../"',industry)

    def test_motorsport_has_content_and_valid_paths(self):
        html=(SITE/"motorsport/index.html").read_text(encoding="utf-8")
        for token in ('id="systems"','id="projects"','id="method"','../f1-models/','../cases/motorsport/','href="../"'):
            self.assertIn(token,html)
        self.assertNotIn('Mercedes-AMG F1 Team',html)
        self.assertNotIn('Kimi Antonelli',html)
        self.assertIn('effects.css',html)
        self.assertIn('effects.js',html)
        css=(SITE/"motorsport/effects.css").read_text(encoding="utf-8")
        js=(SITE/"motorsport/effects.js").read_text(encoding="utf-8")
        self.assertIn('prefers-reduced-motion',css+js)
        self.assertIn('WebGLRenderer',js)
        self.assertIn('helmet-racing-lab.svg',html)
        self.assertIn('if(reduced||settings.mobile)uniforms.uIntro.value=0;',js)
        self.assertIn('raceBlue',js)
        self.assertTrue((SITE/'motorsport/assets/helmet-racing-lab.svg').is_file())
        self.assertIn('ShaderMaterial',js)
        self.assertIn('strokeDashoffset',js)
        self.assertIn('function checker()',js)
        self.assertIn('function marchingContours()',js)
        self.assertIn('function setupTimeline()',js)
        self.assertIn('function setupLenis()',js)
        self.assertIn('function spring(',js)
        self.assertEqual(html.count('class="history"'),7)

    def test_internal_portal_targets_exist(self):
        targets=('f1-models/index.html','cases/motorsport/index.html','cases/index.html')
        for target in targets:
            with self.subTest(target=target):
                self.assertTrue((SITE/target).is_file())

if __name__=='__main__':
    unittest.main()
