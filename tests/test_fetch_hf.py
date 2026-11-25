"""Offline checks of the Hugging Face fetcher: manifests, hashing, selection and token handling."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fetch_hf", ROOT / "scripts" / "fetch_hf.py")
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)


class Manifests(unittest.TestCase):
    def test_all_manifests_are_valid(self):
        paths = sorted((ROOT / "data" / "hf").glob("*.json"))
        self.assertGreater(len(paths), 0)
        for p in paths:
            with self.subTest(manifest=p.name):
                m = json.loads(p.read_text(encoding="utf-8"))
                H.validate_manifest(m, p.stem)
                self.assertRegex(m["repo_id"], r"^[\w.-]+/[\w.-]+$")
                self.assertIn("citation", m["source"])

    def test_non_redistributable_data_is_never_committed(self):
        tracked = subprocess.run(["git", "ls-files", "data/external"], cwd=ROOT, capture_output=True, text=True).stdout
        self.assertEqual(tracked.strip(), "")

    def test_rejects_bad_manifests(self):
        base = {"repo_id": "a/b", "license": "x", "include": ["*"], "redistribute": False, "projects": [1], "source": {}}
        H.validate_manifest(base)
        for bad in ({**base, "include": []}, {**base, "redistribute": "no"}, {**base, "revision": "main"},
                    {**base, "revision": "a" * 40}):
            with self.assertRaises(ValueError):
                H.validate_manifest(bad)


class Hashing(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "f.bin"
        self.data = b"steel surface\n" * 1000
        self.path.write_bytes(self.data)

    def tearDown(self):
        self.tmp.cleanup()

    def test_git_blob_oid_matches_git(self):
        git = subprocess.run(["git", "hash-object", str(self.path)], capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(H.git_blob_oid(self.path), git)

    def test_verify_plain_and_lfs_entries(self):
        size = len(self.data)
        H.verify_file(self.path, {"path": "f.bin", "size": size, "oid": H.git_blob_oid(self.path)})
        H.verify_file(self.path, {"path": "f.bin", "size": size, "oid": "x", "lfs": {"oid": hashlib.sha256(self.data).hexdigest()}})
        with self.assertRaises(H.IntegrityError):
            H.verify_file(self.path, {"path": "f.bin", "size": size, "oid": "0" * 40})
        with self.assertRaises(H.IntegrityError):
            H.verify_file(self.path, {"path": "f.bin", "size": size + 1, "oid": H.git_blob_oid(self.path)})

    def test_tree_digest_is_order_free_and_content_sensitive(self):
        a = {"path": "a.jpg", "oid": "1" * 40, "size": 3, "lfs": {"oid": "f" * 64}}
        b = {"path": "b.json", "oid": "2" * 40, "size": 5}
        self.assertEqual(H.tree_digest([a, b]), H.tree_digest([b, a]))
        self.assertNotEqual(H.tree_digest([a, b]), H.tree_digest([a, {**b, "size": 6}]))


class Selection(unittest.TestCase):
    def test_globs_and_directories(self):
        tree = [{"type": "directory", "path": "train"}, {"type": "file", "path": "train/x.jpg"},
                {"type": "file", "path": "train/_annotations.coco.json"}, {"type": "file", "path": ".gitattributes"},
                {"type": "file", "path": "data/test-00000-of-00001.parquet"}]
        got = [e["path"] for e in H.select(tree, ["train/*", "data/test-*.parquet"])]
        self.assertEqual(got, ["train/x.jpg", "train/_annotations.coco.json", "data/test-00000-of-00001.parquet"])


class Token(unittest.TestCase):
    def test_authorization_is_not_forwarded_to_storage(self):
        handler = H._NoAuthRedirect()
        req = urllib.request.Request("https://huggingface.co/datasets/a/b/resolve/x/f")
        req.add_unredirected_header("Authorization", "Bearer secret")
        new = handler.redirect_request(req, None, 302, "Found", {}, "https://cas-bridge.xethub.hf.co/f?sig=1")
        self.assertNotIn("Authorization", new.headers)
        self.assertNotIn("Authorization", new.unredirected_hdrs)


if __name__ == "__main__":
    unittest.main()
