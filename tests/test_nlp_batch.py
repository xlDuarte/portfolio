"""End-to-end checks for ten genuine text tasks. No external downloads or personal data."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nlp_batch.engine import (
    CLASSIFIERS, SPECS, DEFAULT_ALERTS, DEFAULT_EVIDENCE, DEMO_DOCUMENT,
    make_dataset, validate_frame, train_classifier, verify_alert, scan_governance,
    summarize_document, run, valid_text,
)

class NLPBatchTests(unittest.TestCase):
    def test_full_taxonomy(self):
        self.assertEqual(set(SPECS), set(range(41,51)))
        self.assertEqual(CLASSIFIERS, {41,42,44,45,46,47,49})
        self.assertEqual(len({spec["slug"] for spec in SPECS.values()}),10)

    def test_supervised_tasks_train_and_holdout(self):
        for project in sorted(CLASSIFIERS):
            with self.subTest(project=project):
                frame = make_dataset(project)
                self.assertTrue(frame.equals(make_dataset(project)))
                validate_frame(project,frame)
                groups = {part:set(frame[frame.split==part].template_id) for part in
                          ("train","calibration","test")}
                for a,b in (("train","calibration"),("train","test"),("calibration","test")):
                    self.assertFalse(groups[a] & groups[b])
                model, report, data = train_classifier(project,frame)
                self.assertEqual(report["test_rows"], len(data[data.split=="test"]))
                self.assertGreater(report["train_rows"], report["test_rows"])
                self.assertTrue(0 <= report["test_macro_f1"] <= 1)
                self.assertTrue(0 <= report["test_accuracy"] <= 1)
                self.assertTrue(0 <= report["baseline_test_accuracy"] <= 1)
                self.assertEqual(set(report["classes"]),set(SPECS[project]["labels"]))
                self.assertIn(model.predict([data.text.iloc[0]])[0], report["classes"])

    def test_validation_rejects_template_leakage_and_bad_inputs(self):
        x = make_dataset(41)
        y = x.copy()
        y.loc[y.split=="test","template_id"] = x[x.split=="train"].template_id.iloc[0]
        with self.assertRaisesRegex(ValueError,"Template leakage"):
            validate_frame(41,y)
        z = x.copy()
        z.loc[0,"text"] = None
        with self.assertRaises(ValueError):
            validate_frame(41,z)
        z = x.copy()
        z.loc[0,"sample_id"] = z.loc[1,"sample_id"]
        with self.assertRaises(ValueError):
            validate_frame(41,z)
        with self.assertRaises(ValueError):
            valid_text("  ")

    def test_document_reference_consistency_verifier(self):
        ok = verify_alert(DEFAULT_ALERTS[0],DEFAULT_EVIDENCE)
        conflict = verify_alert(DEFAULT_ALERTS[1],DEFAULT_EVIDENCE)
        missing = verify_alert(DEFAULT_ALERTS[2],DEFAULT_EVIDENCE)
        self.assertEqual(ok["status"], "consistent_with_supplied_text")
        self.assertEqual(ok["source_ids"],["SOP-FX01"])
        self.assertEqual(conflict["status"],"conflicting_supplied_text")
        self.assertEqual(conflict["source_ids"],["LOG-17"])
        self.assertEqual(missing["status"],"insufficient_evidence")
        self.assertEqual(missing["source_ids"],[])
        self.assertEqual(verify_alert(DEFAULT_ALERTS[0],[])["status"],"insufficient_evidence")
        with self.assertRaises(ValueError): verify_alert("text",[{"text":"no id"}])

    def test_governance_scanner_cites_exact_spans(self):
        text = "Foi reportado compartilhamento de senha. É proibido conflito de interesses."
        out = scan_governance(text)
        self.assertGreaterEqual(out["count"],2)
        self.assertTrue(any(f["control"]=="ACCESS" and f["triage"]=="human_review"
                            for f in out["findings"]))
        self.assertTrue(any(f["control"]=="CONFLICT" and f["triage"]=="control_language_detected"
                            for f in out["findings"]))
        self.assertTrue(all(f["excerpt"] in text for f in out["findings"]))

    def test_extracted_summary_is_traceable_verbatim(self):
        result = summarize_document(DEMO_DOCUMENT,max_sentences=3)
        self.assertEqual(len(result["source_sentences"]),3)
        self.assertEqual(result["summary"]," ".join(x["text"] for x in result["source_sentences"]))
        self.assertTrue(all(x["text"] in DEMO_DOCUMENT for x in result["source_sentences"]))
        self.assertTrue(all(x["source_sentence_id"].startswith("S") for x in result["source_sentences"]))
        with self.assertRaises(ValueError):
            summarize_document(DEMO_DOCUMENT,max_sentences=0)

    def test_project_entrypoints_and_readmes_present(self):
        root=Path(__file__).resolve().parents[1]
        for p,cfg in SPECS.items():
            directory=root/"projetos"/"05-nlp"/cfg["slug"]
            for fname in ("main.py","README.md"):
                with self.subTest(project=p,file=fname):
                    self.assertTrue((directory/fname).is_file())
            self.assertIn("nlp_batch.engine",(directory/"main.py").read_text(encoding="utf-8"))
        self.assertTrue((root/"site"/"cases"/"nlp"/"index.html").is_file())

    def test_specialized_dispatch_and_save(self):
        for p in (43,48,50):
            with self.subTest(project=p):
                self.assertEqual(run(p)["project_id"],p)
        with tempfile.TemporaryDirectory() as temp:
            from nlp_batch import engine
            with patch.object(engine,"ROOT",Path(temp)):
                result=run(50,save=True)
                exported=json.loads((Path(temp)/"reports"/"050.json").read_text())
                self.assertEqual(exported,result)

if __name__ == "__main__":
    unittest.main()
