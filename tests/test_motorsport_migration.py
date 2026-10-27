from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
class MotorsportMigration(unittest.TestCase):
    def test_industry_redirects_without_mounting_hub(self):
        text = (ROOT / 'site/industry/index.html').read_text()
        self.assertIn("new URL('../motorsport/racing/'", text)
        self.assertNotIn('id="page-f1-racing"', text)
        self.assertNotIn('function renderF1RacingPage()', text)
    def test_motorsport_owns_hub_and_links(self):
        text = (ROOT / 'site/motorsport/racing/index.html').read_text()
        self.assertIn("const defaultRoute = '#/f1-racing'", text)
        self.assertIn('id="f1-racing-container"', text)
        self.assertIn('racing.css', text)
        self.assertIn('href="racing/"', (ROOT / 'site/motorsport/index.html').read_text())
        for project in (109, 110, 111):
            self.assertIn(f'#/projetos/motorsport-f1/{project}', text)
