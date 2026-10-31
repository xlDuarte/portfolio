import unittest
from scripts.prepare_pages import style_industrial_report, rewrite_html

class IndustrialReportThemeTests(unittest.TestCase):
 def test_scope_and_reproduction(self):
  s='<html><head></head><body><main><pre>python -m pip install -r requirements.txt</pre><table><tr><td>12</td></tr></table></main></body></html>'
  for p in ['index.html','industry/index.html','cases/motorsport/109/index.html','cases/eda/index.html','f1-models/index.html']:
   self.assertEqual(style_industrial_report(p,s),s)
  p='cases/advanced/096/index.html';v=style_industrial_report(p,s)
  self.assertEqual(style_industrial_report(p,v),v);self.assertIn('<table><tr><td>12</td></tr></table>',v);self.assertIn('<summary>Ver comandos de reprodução</summary><pre>',v)
  self.assertIn('href="/portfolio/industry/#/projetos/96"',rewrite_html(v,'/portfolio'))
