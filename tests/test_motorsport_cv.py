"""OpenCV motor sport reproducible optical-flow tests."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

PATH = Path(__file__).resolve().parents[1] / 'motorsport' / 'optical_flow.py'
spec = importlib.util.spec_from_file_location('motorsport_cv', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestMotorsportVision(unittest.TestCase):
    def test_motion_is_measured_not_stubbed(self):
        for dx, dy in [(6, -3), (2.5, 4), (-8, 1.5)]:
            with self.subTest(dx=dx,dy=dy):
                a,b=module.synthetic_pair(shift_x=dx,shift_y=dy)
                out=module.track_features(a,b,expected_shift=(dx,dy))
                self.assertGreater(out['tracked_features'],30)
                self.assertLess(out['endpoint_error_px'],0.6)
    def test_no_feature_frame_is_rejected(self):
        blank=np.zeros((300,400),dtype=np.uint8)
        with self.assertRaisesRegex(ValueError,'insufficient'):
            module.track_features(blank,blank)
    def test_input_validation(self):
        a,b=module.synthetic_pair()
        with self.assertRaises(ValueError): module.track_features(a,b,focal_px=0)
        with self.assertRaises(ValueError): module.track_features(a,b[:20])
        with self.assertRaises(ValueError): module.synthetic_pair(shift_x=float('nan'))

if __name__=='__main__': unittest.main()
