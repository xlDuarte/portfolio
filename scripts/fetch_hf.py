"""Pin, verify and download datasets from the Hugging Face Hub.

    python scripts/fetch_hf.py list
    python scripts/fetch_hf.py pin   <slug> [--revision REV]   # resolve a commit, record the tree digest
    python scripts/fetch_hf.py fetch <slug> [--limit N]        # download into data/external/hf/<slug>/

Each dataset has a manifest in data/hf/<slug>.json with the repository, the license, the files to
use (glob patterns) and, once pinned, the commit SHA plus a digest of the file tree at that commit.

Integrity: a Hub commit is immutable, and the tree API gives every file's git blob id and, for LFS
or Xet files, its SHA-256. `pin` records sha256 over the sorted "path<TAB>oid<TAB>size" lines of the
selected files; `fetch` re-reads the tree at the pinned commit, checks that digest, then verifies
every downloaded file against its own SHA-256 (LFS) or git blob id (plain files). Nothing that fails
a check is kept.

Credentials: public datasets need none. For gated ones, HF_TOKEN is read from the environment, sent
only to huggingface.co (never forwarded to the storage redirect) and never printed.
Standard library only, so it runs anywhere CI can reach huggingface.co.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "hf"
CACHE = ROOT / "data" / "external" / "hf"
HUB = "https://huggingface.co"
REQUIRED = ("repo_id", "license", "include", "redistribute", "projects", "source")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class IntegrityError(RuntimeError):
    pass


# ------------------------------------------------------------------------------------------------
# manifests
# ------------------------------------------------------------------------------------------------
def load_manifest(slug: str) -> dict:
    path = MANIFESTS / f"{slug}.json"
    if not path.is_file():
        raise SystemExit(f"no manifest for '{slug}' in {MANIFESTS.relative_to(ROOT)}")
    m = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(m, slug)
    return m


def validate_manifest(m: dict, slug: str = "?") -> None:
    missing = [k for k in REQUIRED if k not in m]
    if missing:
        raise ValueError(f"{slug}: manifest lacks {missing}")
    if not isinstance(m["include"], list) or not m["include"]:
        raise ValueError(f"{slug}: 'include' must be a non-empty list of glob patterns")
    if not isinstance(m["redistribute"], bool):
        raise ValueError(f"{slug}: 'redistribute' must be true or false")
    if "revision" in m and not SHA_RE.match(m["revision"]):
        raise ValueError(f"{slug}: 'revision' must be a full 40-character commit SHA")
    if "revision" in m and not {"tree_sha256", "n_files", "bytes"} <= m.keys():
        raise ValueError(f"{slug}: a pinned manifest needs tree_sha256, n_files and bytes")


def save_manifest(slug: str, m: dict) -> None:
    (MANIFESTS / f"{slug}.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ------------------------------------------------------------------------------------------------
# hashing
# ------------------------------------------------------------------------------------------------
def git_blob_oid(path: Path) -> str:
    h = hashlib.sha1(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(entries: list[dict]) -> str:
    lines = sorted(f"{e['path']}\t{file_oid(e)}\t{e['size']}" for e in entries)
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def file_oid(e: dict) -> str:
    """SHA-256 for LFS/Xet files, git blob id otherwise."""
    return (e.get("lfs") or {}).get("oid") or e["oid"]


def verify_file(path: Path, entry: dict) -> None:
    if path.stat().st_size != entry["size"]:
        raise IntegrityError(f"{entry['path']}: size {path.stat().st_size} != {entry['size']}")
    lfs = entry.get("lfs")
    got, want = (sha256_file(path), lfs["oid"]) if lfs else (git_blob_oid(path), entry["oid"])
    if got != want:
        raise IntegrityError(f"{entry['path']}: hash {got} != {want}")


def select(entries: list[dict], include: list[str]) -> list[dict]:
    return [e for e in entries if e.get("type") == "file" and any(fnmatch.fnmatch(e["path"], p) for p in include)]


# ------------------------------------------------------------------------------------------------
# Hub API
# ------------------------------------------------------------------------------------------------
class _NoAuthRedirect(urllib.request.HTTPRedirectHandler):
    """Follow redirects (to the LFS/Xet storage) without carrying the Authorization header."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and urllib.parse.urlparse(newurl).hostname != "huggingface.co":
            new.headers.pop("Authorization", None)
            new.unredirected_hdrs.pop("Authorization", None)
        return new


_OPENER = urllib.request.build_opener(_NoAuthRedirect)


def _request(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "xlDuarte-portfolio-fetch/1"})
    token = os.environ.get("HF_TOKEN")
    if token and urllib.parse.urlparse(url).hostname == "huggingface.co":
        req.add_unredirected_header("Authorization", f"Bearer {token}")
    return _OPENER.open(req, timeout=120)


def api_json(url: str):
    with _request(url) as r:
        return json.load(r), r.headers.get("Link", "")


def resolve_revision(repo_id: str, revision: str = "main") -> str:
    data, _ = api_json(f"{HUB}/api/datasets/{repo_id}/revision/{urllib.parse.quote(revision, safe='')}")
    sha = data.get("sha", "")
    if not SHA_RE.match(sha):
        raise IntegrityError(f"{repo_id}@{revision}: the Hub returned no commit SHA")
    return sha


def list_tree(repo_id: str, revision: str) -> list[dict]:
    url = f"{HUB}/api/datasets/{repo_id}/tree/{revision}?recursive=true&expand=false"
    out = []
    while url:
        page, link = api_json(url)
        out += page
        nxt = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = nxt.group(1) if nxt else None
    return out


def download(repo_id: str, revision: str, entry: dict, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{HUB}/datasets/{repo_id}/resolve/{revision}/{urllib.parse.quote(entry['path'])}"
    fd, tmp = tempfile.mkstemp(dir=dest.parent, prefix=".part-")
    try:
        with os.fdopen(fd, "wb") as f, _request(url) as r:
            for chunk in iter(lambda: r.read(1 << 20), b""):
                f.write(chunk)
        verify_file(Path(tmp), entry)
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ------------------------------------------------------------------------------------------------
# commands
# ------------------------------------------------------------------------------------------------
def cmd_list(_args) -> None:
    for p in sorted(MANIFESTS.glob("*.json")):
        m = json.loads(p.read_text(encoding="utf-8"))
        pin = m.get("revision", "not pinned")[:12]
        print(f"{p.stem:24} {m['repo_id']:40} {m['license']:16} {pin:12} projects {', '.join(map(str, m['projects']))}")


def cmd_pin(args) -> None:
    m = load_manifest(args.slug)
    sha = resolve_revision(m["repo_id"], args.revision)
    files = select(list_tree(m["repo_id"], sha), m["include"])
    if not files:
        raise SystemExit(f"{args.slug}: no file at {sha[:12]} matches {m['include']}")
    m.update(revision=sha, tree_sha256=tree_digest(files), n_files=len(files), bytes=sum(e["size"] for e in files))
    save_manifest(args.slug, m)
    print(f"{args.slug}: pinned {m['repo_id']}@{sha} — {len(files)} files, {m['bytes'] / 1e6:.1f} MB")


def cmd_fetch(args) -> None:
    m = load_manifest(args.slug)
    if "revision" not in m:
        raise SystemExit(f"{args.slug}: run 'pin' first; downloads only come from a pinned commit")
    files = select(list_tree(m["repo_id"], m["revision"]), m["include"])
    if tree_digest(files) != m["tree_sha256"] or len(files) != m["n_files"]:
        raise IntegrityError(f"{args.slug}: the file tree at {m['revision'][:12]} differs from the manifest")
    files = sorted(files, key=lambda e: e["path"])[: args.limit or None]
    root = CACHE / args.slug
    done = 0
    for e in files:
        dest = root / e["path"]
        if dest.is_file():
            try:
                verify_file(dest, e)
                done += 1
                continue
            except IntegrityError:
                dest.unlink()
        download(m["repo_id"], m["revision"], e, dest)
        done += 1
    print(f"{args.slug}: {done} files verified in {root.relative_to(ROOT)}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    p = sub.add_parser("pin")
    p.add_argument("slug")
    p.add_argument("--revision", default="main")
    p.set_defaults(fn=cmd_pin)
    p = sub.add_parser("fetch")
    p.add_argument("slug")
    p.add_argument("--limit", type=int, default=0, help="download only the first N files (smoke test)")
    p.set_defaults(fn=cmd_fetch)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
