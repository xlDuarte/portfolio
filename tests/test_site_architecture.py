"""Static site architecture: two niches, F1/Porsche split, shared lab, one design system.

These checks read the committed ``site/`` tree (built by scripts/build_site.py) and
``vercel.json``; they need no network and no browser.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "scripts"))
import site_data as D  # noqa: E402

PAGES = sorted(SITE.rglob("*.html"))


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if tag in ("a", "link", "img", "script") and a.get(key):
                self.links.append(a[key])


def read(rel: str) -> str:
    return (SITE / rel).read_text(encoding="utf-8")


def resolve(page: Path, href: str) -> Path | None:
    """Map an internal URL to the file Vercel would serve (cleanUrls + redirects)."""
    parts = urlsplit(href)
    if parts.scheme or href.startswith(("//", "#", "mailto:", "data:", "javascript:")) or "${" in href:
        return None
    path = parts.path
    if not path:
        return None
    if path.startswith("/"):
        url = path
    else:
        base = "/" + str(page.parent.relative_to(SITE)).replace("\\", "/") + "/"
        url = str(Path(base.replace("/./", "/")) / path) if base != "/./" else "/" + path
        url = re.sub(r"/+", "/", "/" + str(Path(url)).lstrip("/")) + ("/" if path.endswith("/") else "")
    for old, new in D.REDIRECTS.items():
        if url.rstrip("/") == old.rstrip("/"):
            url = urlsplit(new).path
    target = SITE / url.lstrip("/")
    for candidate in (target, Path(str(target) + ".html"), target / "index.html"):
        if candidate.is_file():
            return candidate
    return target  # missing


class TestNiches(unittest.TestCase):
    def test_home_presents_two_niches_and_shared_lab(self):
        home = read("index.html")
        self.assertEqual(home.count('class="half ind"'), 1)
        self.assertEqual(home.count('class="half auto"'), 1)
        self.assertIn('href="/industrial/"', home)
        self.assertIn('href="/automotivo/"', home)
        self.assertIn('href="/laboratorio/"', home)
        self.assertIn("Automotivo de desempenho", home)

    def test_automotive_splits_f1_and_porsche(self):
        hub = read("automotivo/index.html")
        self.assertIn('href="/automotivo/f1/"', hub)
        self.assertIn('href="/automotivo/porsche/"', hub)
        f1, porsche = read("automotivo/f1/index.html"), read("automotivo/porsche/index.html")
        for tool in D.F1_TOOLS:
            self.assertIn(f'href="{tool["path"]}"', f1)
        for proj in D.F1_PROJECTS:
            self.assertIn(proj["path"], f1)
            self.assertNotIn(proj["path"], porsche)
        self.assertIn(D.PORSCHE_PROJECT["path"], porsche)
        self.assertNotIn(D.PORSCHE_PROJECT["path"], f1)
        self.assertIn('aria-current="page">Fórmula 1', f1)
        self.assertIn('aria-current="page">Porsche Cup', porsche)

    def test_shared_lab_lists_cross_niche_projects(self):
        lab = read("laboratorio/index.html")
        for proj in D.SHARED_PROJECTS:
            self.assertIn(proj["path"], lab)
            page = read(proj["path"].lstrip("/") + "index.html")
            self.assertIn('data-niche="laboratorio"', page)

    def test_niche_colour_on_every_niche_page(self):
        expected = {"industrial/": "industrial", "automotivo/": "automotivo", "laboratorio/": "laboratorio",
                    "cases/022/": "industrial", "cases/motorsport/110/": "automotivo", "motorsport/f1-pip/": "automotivo"}
        for rel, niche in expected.items():
            self.assertIn(f'data-niche="{niche}"', read(rel + "index.html"), rel)

    def test_porsche_anchors_exist(self):
        page = read("cases/motorsport/110/index.html")
        for mod in D.PORSCHE_MODULES:
            self.assertIn(f'id="{mod["anchor"].lstrip("#")}"', page)


class TestDesignSystem(unittest.TestCase):
    def test_every_page_uses_the_shell(self):
        for page in PAGES:
            s = page.read_text(encoding="utf-8")
            with self.subTest(page=str(page.relative_to(SITE))):
                if True:
                    self.assertIn('href="/assets/ds.css"', s)
                    self.assertIn("<!-- ds:header -->", s)
                    self.assertIn('<html lang="pt-BR">', s.replace("<html lang=\"pt-BR\">\n", "<html lang=\"pt-BR\">"))
                    self.assertRegex(s, r'<meta name="description" content="[^"]{20,}"')
                    self.assertIn('<link rel="canonical" href="' + D.SITE_URL, s)
                    self.assertIn('property="og:image"', s)
                    self.assertEqual(s.count("<h1"), 1)
                self.assertNotIn("fonts.googleapis.com", s)

    def test_fonts_self_hosted_and_licensed(self):
        css = (SITE / "assets/ds.css").read_text()
        self.assertIn("/assets/fonts/archivo-latin.woff2", css)
        self.assertTrue((SITE / "assets/fonts/archivo-latin.woff2").is_file())
        self.assertTrue((SITE / "assets/fonts/OFL.txt").is_file())
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn(":focus-visible", css)

    def test_legacy_brand_artwork_stays_removed(self):
        banned = ["red-bull.svg", "porsche-motorsport.svg", "models/assets/f1.svg", "media.formula1.com", "concept-helmet"]
        for page in list(PAGES) + list(SITE.rglob("*.mjs")) + list(SITE.rglob("*.js")):
            s = page.read_text(encoding="utf-8", errors="ignore")
            for token in banned:
                self.assertNotIn(token, s, f"{page}: {token}")
        self.assertFalse(list((SITE / "motorsport/models").glob("assets/*.webp")))

    def test_every_third_party_image_has_provenance(self):
        """Each file in assets/photos and assets/brands needs origin, licence and credit in SOURCES.json;
        pages that show one carry the no-affiliation notice and, once confirmed, the credit."""
        sources = json.loads((SITE / "assets/brands/SOURCES.json").read_text(encoding="utf-8"))["files"]
        by_file = {e["file"]: e for e in sources}
        files = [p for d in ("photos", "brands") for p in (SITE / "assets" / d).glob("*") if p.name != "SOURCES.json"]
        self.assertTrue(files)
        for f in files:
            rel = f.relative_to(SITE).as_posix()
            self.assertIn(rel, by_file, rel)
            for key in ("origin", "license", "credit", "status", "added"):
                self.assertTrue(by_file[rel].get(key), (rel, key))
        for page in PAGES:
            html = page.read_text(encoding="utf-8")
            for rel, entry in by_file.items():
                if f"/{rel}" in html:
                    self.assertIn("sem vínculo", html, page)
                    if entry["status"] != "pending":
                        self.assertIn(entry["credit"], html, page)

    def test_og_images_present(self):
        for name in ("default", "industrial", "automotivo", "laboratorio"):
            f = SITE / "assets/og" / f"{name}.png"
            self.assertTrue(f.is_file())
            self.assertEqual(f.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


class TestLinksAndDeploy(unittest.TestCase):
    def test_internal_links_resolve(self):
        missing = []
        for page in PAGES:
            p = _Links()
            p.feed(page.read_text(encoding="utf-8"))
            for href in p.links:
                target = resolve(page, href)
                if target is not None and not target.is_file():
                    missing.append(f"{page.relative_to(SITE)} → {href}")
        self.assertEqual(missing, [])

    def test_repository_links_point_to_main(self):
        for page in PAGES:
            for m in re.finditer(r"github\.com/xlDuarte/portfolio/(?:blob|tree)/([^/\"']+)/", page.read_text(encoding="utf-8")):
                self.assertEqual(m.group(1), "main", str(page))

    def test_vercel_redirects_headers_and_seo_files(self):
        cfg = json.loads((ROOT / "vercel.json").read_text())
        self.assertEqual(cfg["outputDirectory"], "site")
        sources = {r["source"] for r in cfg["redirects"]}
        for old in ("/industry", "/motorsport", "/f1", "/about", "/motorsport/racing"):
            self.assertIn(old, sources)
            self.assertIn(old + "/", sources)  # trailingSlash:true matches the slash form
        self.assertIn("/industry/arquivo/", sources)  # cleanUrls form of arquivo.html
        keys = {h["key"] for block in cfg["headers"] for h in block["headers"]}
        for header in ("Content-Security-Policy", "X-Content-Type-Options", "Referrer-Policy"):
            self.assertIn(header, keys)
        self.assertTrue((SITE / "404.html").is_file())
        self.assertIn(D.SITE_URL + "/sitemap.xml", (SITE / "robots.txt").read_text())
        sitemap = (SITE / "sitemap.xml").read_text()
        for path in ("/", "/industrial/", "/automotivo/f1/", "/automotivo/porsche/", "/laboratorio/", "/sobre/"):
            self.assertIn(f"<loc>{D.SITE_URL}{path}</loc>", sitemap)

    def test_retired_pages_are_gone(self):
        for rel in ("industry/arquivo.html", "motorsport/racing/index.html", "f1/index.html", "motorsport/effects.js"):
            self.assertFalse((SITE / rel).exists(), rel)


class TestContentCredibility(unittest.TestCase):
    def test_no_outdated_or_contradictory_claims(self):
        for page in PAGES:
            s = page.read_text(encoding="utf-8")
            with self.subTest(page=str(page.relative_to(SITE))):
                self.assertNotIn("Cases Reais", s)
                self.assertNotRegex(s, r"Gerdau Summit[^<]{0,40}(ATUAL|PRESENT)")
                self.assertNotIn("SOP-GERDAU", s)

    def test_experience_uses_the_owner_wording(self):
        about = read("sobre/index.html")
        self.assertIn("Estágio em análise de dados", about)
        self.assertIn("2024 – 2026", about)


if __name__ == "__main__":
    unittest.main()
