"""Static quality gates for the real five-scene Motorsport animation system."""
from pathlib import Path
import shutil
import subprocess
import unittest

SITE=Path(__file__).resolve().parents[1]/"site"/"motorsport"

class TestMotorsportEffects(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(SITE/"index.html").read_text(encoding="utf-8")
        cls.css=(SITE/"effects.css").read_text(encoding="utf-8")
        cls.js=(SITE/"effects.js").read_text(encoding="utf-8")
        cls.asset=(SITE/"asset-scene.js").read_text(encoding="utf-8")

    def test_five_acts_and_all_entrypoints(self):
        h=self.html
        for token in ('id="hero"','id="systems"','id="projects"','id="method"','id="contact"',
                      'id="loading-veil"','id="hero-scene"','id="track-trace"','id="reticle"',
                      'href="./f1-pip/"','href="../industry/"','href="../"'):
            with self.subTest(token=token):self.assertIn(token,h)
        self.assertEqual(h.count('class="history"'),7)
        self.assertEqual(h.count('data-checker='),3)

    def test_shaders_tier_and_reference_motion(self):
        for token in ('new THREE.WebGLRenderer','ShaderMaterial','function spring(',
                      'function marchingContours()','function setupTimeline()','function setupCircuit()',
                      'function setupMap()','function setupSignoff()','function setupLenis()',
                      'settings.freeze','uTrail[72]','uTrailCount',
                      'mobile?28:tablet?44:72','total=6000','nx=92,ny=87',
                      "params.has('referenceScene')"):
            with self.subTest(token=token):self.assertIn(token,self.js)
        self.assertIn('prefers-reduced-motion',self.css)

    def test_draco_hdr_personal_portrait_and_fallbacks(self):
        for token in ('GLTFLoader','DRACOLoader','RGBELoader','PMREMGenerator',
                      'studio-light.hdr','helmet3.glb','gabriel-racing.webp','noise.webp'):
            with self.subTest(token=token):self.assertIn(token,self.asset)
        self.assertTrue((SITE/"assets/gabriel-racing.webp").is_file())
        self.assertIn('gabriel-racing.webp',self.html)
        self.assertNotIn('id="concept-helmet"',self.html)
        self.assertIn('root.dataset.sceneReady="true"',self.js)
        self.assertIn('clearTimeout(watchdog)',self.js)
        self.assertIn('is-visible',self.css)
        self.assertIn("showError('WebGL",self.js)
        self.assertTrue((SITE/"assets/README.md").is_file())
        self.assertNotIn("Kimi Antonelli",self.html)
        self.assertNotIn("Mercedes-AMG F1 Team",self.html)

    @unittest.skipUnless(shutil.which("node"),"Node.js unavailable: JS parser check skipped")
    def test_ecmascript_modules_are_syntactically_valid(self):
        for name in ('effects.js','asset-scene.js'):
            with self.subTest(name=name):
                text=(SITE/name).read_text(encoding="utf-8")
                proc=subprocess.run(['node','--check','--input-type=module'],input=text,
                        capture_output=True,text=True,timeout=12)
                self.assertEqual(proc.returncode,0,proc.stderr)

if __name__=="__main__":unittest.main()

