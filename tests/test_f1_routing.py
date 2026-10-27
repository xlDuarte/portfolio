"""Regression tests for F1 route mounting in every distributed HTML entrypoint."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (
    "index.html",
    "site/motorsport/racing/index.html",
    "site/f1/index.html",
    "gabriel_duarte_automotive_lab.html",
    "f1-predictive-intelligence/apps/web/index.html",
)

class TestF1Routing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {f: (ROOT / f).read_text(encoding="utf-8") for f in HTML}

    def test_f1_render_is_invoked_in_global_render(self):
        for name, html in self.pages.items():
            with self.subTest(page=name):
                render = html.split("function renderAll() {", 1)[1].split("\n        }", 1)[0]
                self.assertIn("currentRoute === '#/f1-racing'", render)
                self.assertIn("renderF1RacingPage();", render)

    def test_f1_container_is_unmounted_elsewhere(self):
        for name, html in self.pages.items():
            with self.subTest(page=name):
                render = html.split("function renderAll() {", 1)[1].split("\n        }", 1)[0]
                self.assertIn("f1Container.replaceChildren()", render)

    def test_automotive_controls_do_not_render_f1(self):
        for name, html in self.pages.items():
            with self.subTest(page=name):
                lab = html.split("function renderAutoLabPage() {", 1)[1].split("function updateLabMetricsOnly()", 1)[0]
                self.assertNotIn("renderF1RacingPage();", lab)

    def test_direct_f1_entrypoint(self):
        for name, html in self.pages.items():
            with self.subTest(page=name):
                self.assertIn("const defaultRoute =", html)
                self.assertIn("navigateTo(window.location.hash || defaultRoute)", html)

    def test_f1_hub_contains_modules(self):
        for name, html in self.pages.items():
            with self.subTest(page=name):
                self.assertIn("id=\"f1-racing-container\"", html)
                self.assertIn("function buildF1PipCommandCenterHTML", html)
                self.assertIn("function wireF1PipEvents", html)

if __name__ == "__main__":
    unittest.main()

