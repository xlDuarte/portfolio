from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
class MotorsportMigration(unittest.TestCase):
    def test_industry_redirects_without_mounting_hub(self):
        text = (ROOT / 'site/industry/index.html').read_text()
        self.assertIn("new URL('../motorsport/f1-pip/'", text)
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
    def test_only_active_route_is_mounted(self):
        import subprocess
        html = (ROOT / 'site/motorsport/racing/index.html').read_text()
        body = html.split('function renderAll() {', 1)[1].split('\n        /*', 1)[0]
        script = """
const assert = require('node:assert/strict');
let calls=[], cleared=[];
const document={getElementById:id=>({replaceChildren:()=>cleared.push(id)})};
const renderHeaderNav=()=>calls.push('header');
const renderF1RacingPage=()=>calls.push('hub');
const renderProjetoDetalhePage=()=>calls.push('detail');
const renderProjetosPage=()=>calls.push('catalogue');
let currentRoute, currentProjectDetailId;
function renderAll(){BODY
for(const [route,id,expected] of [['#/f1-racing',null,'hub'],['#/projetos/motorsport-f1/111',111,'detail'],['#/projetos/motorsport-f1',null,'catalogue']]) {
 currentRoute=route;currentProjectDetailId=id;calls=[];cleared=[];renderAll();
 assert.deepEqual(calls,['header',expected]);assert.equal(new Set(cleared).size,3);
}
""".replace('BODY', body)
        subprocess.run(['node', '-e', script], check=True, capture_output=True)

    def test_pip_uses_motorsport_assets_and_navigation(self):
        from html.parser import HTMLParser
        page = ROOT / 'site/motorsport/f1-pip/index.html'
        class Links(HTMLParser):
            def handle_starttag(self, tag, attrs):
                for key, value in attrs:
                    if key in ('src', 'href') and value.startswith('../'):
                        target = (page.parent / value).resolve()
                        self_target = target / 'index.html' if value.endswith('/') else target
                        assert self_target.is_file(), str(self_target)
        text = page.read_text()
        Links().feed(text)
        self.assertIn('F1-PIP', text)
        self.assertIn('Space+Grotesk', text)
        self.assertIn('Oswald', text)
