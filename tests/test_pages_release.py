"""Pages project-subpath, metadata and site build smoke tests."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from scripts.prepare_pages import rewrite_url,rewrite_html,build,ROOT

class TestPagesReleaseBuild(unittest.TestCase):
    def test_links_rewrite_without_double_prefix(self):
        self.assertEqual(rewrite_url("/cases/nlp/","/portfolio"),"/portfolio/cases/nlp/")
        self.assertEqual(rewrite_url("/portfolio/cases/nlp/","/portfolio"),"/portfolio/cases/nlp/")
        self.assertEqual(rewrite_url("/","/portfolio"),"/portfolio/")
        self.assertEqual(rewrite_url("//cdn.example.com/s.js","/portfolio"),"//cdn.example.com/s.js")
        self.assertEqual(rewrite_url("https://github.com/xlDuarte","/portfolio"),"https://github.com/xlDuarte")
        self.assertEqual(rewrite_url("#projects","/portfolio"),"#projects")
    def test_html_links_scripts_and_canonical(self):
        html='''<html><head><title>Engineering &amp; BI</title></head><body>
        <a href="/cases/advanced/">A</a><a href="//github.com/">B</a>
        <img src="/assets/logo.svg"><a href="/">Home</a>
        <script>const path='/cases/motorsport/';</script></body></html>'''
        out=rewrite_html(html,"/portfolio","https://xlduarte.github.io/portfolio/")
        self.assertIn('href="/portfolio/cases/advanced/"',out)
        self.assertIn('href="//github.com/"',out)
        self.assertIn('src="/portfolio/assets/logo.svg"',out)
        self.assertIn('href="/portfolio/"',out)
        self.assertIn("='/portfolio/cases/motorsport/'",out)
        self.assertIn('rel="canonical"',out)
        self.assertIn('content="Engineering &amp; BI"',out)
    def test_dist_tree_and_sitemap_are_separate_from_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/"source";src.mkdir()
            (src/"index.html").write_text('<html><head><title>Home</title></head><body><a href="/cases/">Catalog</a></body></html>')
            dest=src/"cases";dest.mkdir()
            (dest/"index.html").write_text('<html><head><title>Cases</title></head><body><a href="/">Home</a></body></html>')
            dist=Path(tmp)/"built"
            result=build(src,dist)
            self.assertEqual(result["pages"],2)
            self.assertEqual(result["sitemap_entries"],2)
            self.assertTrue((dist/".nojekyll").is_file())
            self.assertTrue((dist/"404.html").is_file())
            self.assertIn("/portfolio/cases/",(dist/"index.html").read_text())
            self.assertIn('href="/cases/"',(src/"index.html").read_text())
            ET.parse(dist/"sitemap.xml")
            self.assertIn("https://xlduarte.github.io/portfolio/sitemap.xml",(dist/"robots.txt").read_text())
    def test_real_site_index_and_routes(self):
        index=(ROOT/"site"/"industry"/"index.html").read_text(encoding="utf-8")
        self.assertIn('href="/docs/"',index)
        self.assertIn('href="/cases/"',index)
        self.assertIn('href="/about/"',index)
        self.assertIn('href="/releases/"',index)
        for folder in ("docs","about","releases","packages"):
            self.assertTrue((ROOT/"site"/folder/"index.html").is_file(),folder)
        self.assertTrue((ROOT/"site"/"index.html").exists())
        personal=(ROOT/"site"/"index.html").read_text(encoding="utf-8")
        self.assertIn('href="./industry/"',personal)
        self.assertIn('href="./motorsport/"',personal)
        for category in ("classification","nlp","recommendation","timeseries","vision","business","advanced","motorsport"):
            with self.subTest(category=category):
                self.assertTrue((ROOT/"site"/"cases"/category/"index.html").exists())
if __name__=="__main__":unittest.main()
