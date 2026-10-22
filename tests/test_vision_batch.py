"""Functional tests: independent synthetic image inputs, geometry, OCR and tracking."""
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
import cv2
import numpy as np
from vision_batch import engine as v

ROOT=Path(__file__).resolve().parents[1]

class VisionAcceptance(unittest.TestCase):
    def test_inventory_and_real_input_provenance(self):
        self.assertEqual(set(v.CONFIG),set(range(71,81)))
        self.assertEqual(len({c["slug"] for c in v.CONFIG.values()}),10)
        for i in range(71,81):
            with self.subTest(project=i):
                output=v.run(i)
                self.assertEqual(output["project_id"],i)
                self.assertEqual(output["source"],"SYNTHETIC OpenCV-rendered images")
                self.assertFalse(output["production_validated"])
                self.assertIn("result",output)
                self.assertEqual(output,v.run(i))

    def test_ppe_pixel_segmentation_and_synthetic_cnn_entrypoint(self):
        wearing=v.render_ppe(True)
        bare=v.render_ppe(False)
        self.assertTrue(np.any(wearing!=bare))
        hsv=lambda im:cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        mask=lambda im:cv2.inRange(hsv(im),(15,70,80),(45,255,255))
        self.assertGreater(int(cv2.countNonZero(mask(wearing))),int(cv2.countNonZero(mask(bare))))
        self.assertIn("Run --deep",v.run(71)["result"]["trained_cnn"])

    def test_gesture_shape_matching_does_not_execute_hmi(self):
        for gesture in ("open","fist","point"):
            with self.subTest(gesture=gesture):
                data=v.gestures(v.render_gesture(gesture))
                self.assertEqual(data["gesture"],gesture)
                self.assertFalse(data["action_executed"])
        self.assertEqual(v.gestures(v.canvas())["gesture"],"unknown")

    def test_part_contour_counts(self):
        for count in range(7):
            self.assertEqual(v.detect_parts(v.parts_scene(count))["count"],count)
        with self.assertRaises(ValueError):v.parts_scene(9)

    def test_vigilance_never_inferrs_verified_fatigue(self):
        r=v.vigilance_sequence([True,False,False,True])
        self.assertEqual(r["frames"],4)
        self.assertEqual(r["closed_frames"],2)
        self.assertAlmostEqual(r["perclos_demo"],.5)
        self.assertIn("NOT VALIDATED",r["fatigue_diagnosis"])
        with self.assertRaises(ValueError):v.vigilance_sequence([])

    def test_ocr_of_rendered_serial(self):
        predicted=v.recognize_serial(v.serial_scene("AB1234"))
        self.assertEqual(predicted["serial"],"AB1234")
        self.assertFalse(predicted["real_stamping_validation"])
        with self.assertRaises(ValueError):v.serial_scene("!!")

    def test_crack_porosity_oxidation_and_clean(self):
        for kind in ("clean","crack","porosity","oxidation"):
            with self.subTest(kind=kind):
                actual=v.analyze_surface(v.surface_scene(kind))
                self.assertEqual(actual["synthetic_label"],kind)
        self.assertGreater(v.analyze_surface(v.surface_scene("oxidation"))["oxidized_pixel_ratio"],.1)

    def test_road_sign_color_and_polygon_detection(self):
        for kind in ("stop","warning","mandatory"):
            out=v.recognize_sign(v.sign_scene(kind))
            self.assertEqual(out["sign"],kind)
            self.assertFalse(out["control_action_executed"])
            self.assertGreater(out["colored_area_px"],100)

    def test_material_histogram_similarity(self):
        for kind in v.COLORS:
            with self.subTest(kind=kind):
                self.assertEqual(v.classify_scrap(v.scrap_scene(kind))["category"],kind)
                self.assertGreater(v.classify_scrap(v.scrap_scene(kind))["cosine_histogram"],.9)

    def test_multi_target_tracking_contiguous_ids(self):
        r=v.track_yard(v.yard_frames(6))
        self.assertEqual(r["unique_tracks"],2)
        self.assertEqual(r["frames"],6)
        self.assertTrue(all(len(path)==6 for path in r["track_paths"].values()))
        self.assertFalse(r["real_vehicle_identity"])
        with self.assertRaises(ValueError):v.track_yard([])

    def test_validate_bad_images_and_save_real_artifacts(self):
        with self.assertRaises(ValueError):v.validate_image(np.zeros((96,96),dtype=np.uint8))
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(v,"ROOT",Path(tmp)):
                # config is loaded at import, only output folder is redirected
                for i in range(71,81):
                    output=v.run(i,save=True)
                    pic=Path(tmp)/"reports"/f"{i:03d}.png"
                    report=Path(tmp)/"reports"/f"{i:03d}.json"
                    self.assertTrue(pic.is_file())
                    self.assertTrue(report.is_file())
                    self.assertIsNotNone(cv2.imread(str(pic)))
                    self.assertEqual(json.loads(report.read_text()),output)

    def test_ten_canonical_entrypoints_documentation_site(self):
        for i,c in v.CONFIG.items():
            base=ROOT/"projetos"/"08-vision"/c["slug"]
            self.assertTrue((base/"main.py").is_file())
            self.assertTrue((base/"README.md").is_file())
            self.assertIn("vision_batch.engine",(base/"main.py").read_text())
            self.assertTrue((ROOT/"site"/"cases"/"vision"/f"{i:03d}"/"index.html").is_file())
        self.assertTrue((ROOT/"site"/"cases"/"vision"/"index.html").is_file())
        self.assertIn("/cases/vision/",(ROOT/"site"/"docs"/"index.html").read_text())

if __name__=="__main__":unittest.main()
