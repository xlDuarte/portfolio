"""GitHub Pages mirror: every page forwards to the canonical Vercel site."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.prepare_pages import build, public_path, ROOT
from scripts import site_data as D


class TestPagesRedirectBuild(unittest.TestCase):
    def test_public_paths_follow_clean_urls(self):
        self.assertEqual(public_path("index.html"), "/")
        self.assertEqual(public_path("industrial/index.html"), "/industrial/")
        self.assertEqual(public_path("cases/011/interactive.html"), "/cases/011/interactive")
        self.assertEqual(public_path("404.html"), "/404")

    def test_stubs_canonical_noindex_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source"
            (src / "industrial").mkdir(parents=True)
            (src / "index.html").write_text("<html><body>home</body></html>")
            (src / "industrial" / "index.html").write_text("<html><body>ind</body></html>")
            dist = Path(tmp) / "built"
            result = build(src, dist, "/portfolio", "https://example.vercel.app")
            self.assertEqual(result["pages"], 2)
            page = (dist / "industrial" / "index.html").read_text()
            self.assertIn('rel="canonical" href="https://example.vercel.app/industrial/"', page)
            self.assertIn('name="robots" content="noindex"', page)
            self.assertIn("location.hash", page)
            self.assertIn('http-equiv="refresh"', page)
            self.assertTrue((dist / ".nojekyll").is_file())
            self.assertIn("p.slice(10)", (dist / "404.html").read_text())
            for old, new in D.REDIRECTS.items():
                folder = dist / old.strip("/")
                target = folder / "index.html" if not old.endswith(".html") else dist / old.lstrip("/")
                self.assertIn("https://example.vercel.app" + new, target.read_text(), old)

    def test_refuses_to_write_into_source(self):
        with self.assertRaises(ValueError):
            build(ROOT / "site", ROOT / "site" / "_out")

    def test_real_site_builds(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build(ROOT / "site", Path(tmp) / "out")
            self.assertGreater(result["pages"], 100)
            home = (Path(tmp) / "out" / "index.html").read_text()
            self.assertIn(D.SITE_URL + "/", home)


if __name__ == "__main__":
    unittest.main()
