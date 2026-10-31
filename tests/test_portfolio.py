"""Dependency-free regression tests: source inventory, frontend references and F1 model guardrails."""
import ast
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_BASE = "https://github.com/xlDuarte/portfolio/tree/main/projetos"

class TestPortfolioIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects=sorted((ROOT/'projetos').glob('**/main.py'))

    def test_project_count_and_documentation(self):
        self.assertEqual(len(self.projects),111)
        numbers=[int(m.group(1)) for p in self.projects if (m := re.match(r'(\d{3})-',p.parent.name))]
        self.assertEqual(sorted(numbers),list(range(1,112)))
        for p in self.projects:
            with self.subTest(path=p):
                self.assertTrue((p.parent/'README.md').is_file())

    def test_python_syntax(self):
        for p in self.projects+list((ROOT/'f1-predictive-intelligence').rglob('*.py')):
            with self.subTest(path=p):
                ast.parse(p.read_text(encoding='utf8'),filename=str(p))

    def test_project_execution(self):
        def execute(p):
            try:
                r=subprocess.run([sys.executable,str(p)],cwd=p.parent,capture_output=True,text=True,timeout=14)
                return p, r.returncode, r.stderr[:500]
            except subprocess.TimeoutExpired:
                return p, -999, 'Timed out after 14 seconds'
        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes=list(pool.map(execute,self.projects))
        for p,code,stderr in outcomes:
            with self.subTest(path=p):
                self.assertEqual(code,0,msg=stderr)

    def test_frontend_github_links(self):
        for rel in ('site/industry/arquivo.html','site/f1/index.html'):
            s=(ROOT/rel).read_text(encoding='utf8')
            with self.subTest(file=rel):
                self.assertIn(REPO_BASE,s)
                self.assertNotIn('gabrielrduarte/automotive-industrial-lab',s)
                self.assertNotIn('xlDuarte/automotive-industrial-lab',s)
                self.assertIn('Synthetic index (not validated)',s)
                self.assertIn('Generated example',s)
                self.assertIn('README.md ↗',s)
                self.assertNotIn('Score do Modelo (R² / F1)',s)

    def test_industry_catalog_source_links(self):
        directory = ROOT / 'site/industry'
        module = (directory / 'industrial.mjs').read_text()
        self.assertIn(REPO_BASE.rsplit('/', 1)[0] + "/'+p.code", module)
        self.assertIn('href="${code}"', module)
        paths = re.findall(r'"code":"(.*?)"', (directory / 'catalog.mjs').read_text())
        self.assertTrue(paths)
        for path in paths:
            self.assertTrue(path.startswith('projetos/') and (ROOT / path / 'README.md').is_file(), path)

    def test_f1_walk_forward_leakage_protection(self):
        src=ROOT/'f1-predictive-intelligence/main.py'
        spec=importlib.util.spec_from_file_location('f1_engine_for_test',src)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        engine=module.WalkForwardPredictionEngine
        past={'event_id':'prev','event_timestamp_utc':'2026-01-01T00:00:00Z','results':[{'driver_code':'AAA','constructor':'TEAM','finish_pos':4}]}
        target={'event_id':'target','snapshot_timestamp_utc':'2026-02-01T00:00:00Z','entries':[{'driver_code':'AAA','constructor':'TEAM','grid_pos':1},{'driver_code':'BBB','constructor':'TEAM','grid_pos':5}]}
        pred=engine.predict_event_walk_forward([past],target,'2026-02-02T00:00:00Z')
        self.assertEqual(len(pred['predictions']),2)
        self.assertAlmostEqual(sum(x['win_prob'] for x in pred['predictions']),1.0,places=3)
        for x in pred['predictions']:
            self.assertTrue(0<=x['win_prob']<=x['podium_prob']<=x['points_prob']<=1)
        with self.assertRaisesRegex(ValueError,'Look-ahead'):
            engine.predict_event_walk_forward([past],target,'2025-12-31T00:00:00Z')
        target_future={**target,'snapshot_timestamp_utc':'2026-03-01T00:00:00Z'}
        with self.assertRaisesRegex(ValueError,'snapshot'):
            engine.predict_event_walk_forward([past],target_future,'2026-02-02T00:00:00Z')

    def test_site_pages_and_ci_scope(self):
        self.assertTrue((ROOT/'site/industry/index.html').is_file())
        self.assertTrue((ROOT/'site/f1/index.html').is_file())
        yml=(ROOT/'.github/workflows/ci-and-pages.yml').read_text(encoding='utf8')
        self.assertIn('path: _site',yml)
        self.assertIn('unittest discover -s tests',yml)

if __name__=='__main__':unittest.main()