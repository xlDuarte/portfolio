#!/usr/bin/env python3
"""Build the GitHub Pages mirror as a set of redirects to the canonical site.

The portfolio is served from Vercel (see ``scripts/site_data.SITE_URL``). GitHub
Pages keeps working for old links, but every page it serves is a tiny stub that
points search engines (``rel=canonical`` + ``noindex``) and visitors
(``meta refresh`` + ``location.replace`` keeping the #hash) to the same path on
the canonical domain. Retired paths from ``site_data.REDIRECTS`` go straight to
their new destination. The source ``site/`` tree is never modified.

Usage:
  python scripts/prepare_pages.py --repo xlDuarte/portfolio --output _site
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_data as D  # noqa: E402


def clean_base_path(base_path: str) -> str:
    if base_path in ("", "/"):
        return ""
    if not re.fullmatch(r"/[a-zA-Z0-9_-]+/?", base_path):
        raise ValueError("base-path must be one safe, optional repository segment")
    return base_path.rstrip("/")


def public_path(relative: str) -> str:
    """site/ file path → canonical URL path (clean URLs, trailing slash for folders)."""
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return "/" + relative[: -len("index.html")]
    if relative.endswith(".html"):
        return "/" + relative[: -len(".html")]
    return "/" + relative


def stub(target_url: str, base: str) -> str:
    """HTML that forwards to ``target_url``; the inline script keeps the #fragment."""
    t = html.escape(target_url, quote=True)
    js_target = target_url.replace("\\", "\\\\").replace("'", "\\'")
    return (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex">'
        f'<link rel="canonical" href="{t}">'
        f'<meta http-equiv="refresh" content="0; url={t}">'
        "<title>Portfólio de Gabriel Reis Duarte</title>"
        f"<script>location.replace('{js_target}'+(location.hash||''))</script>"
        "</head><body>"
        f'<p>Este portfólio mudou de endereço: <a href="{t}">{t}</a></p>'
        "</body></html>"
    )


def not_found_stub(site_url: str, base: str) -> str:
    """404 page: forward any unknown /portfolio/... path to the same path on the canonical site."""
    b = base.replace("'", "")
    return (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
        "<title>Portfólio de Gabriel Reis Duarte</title>"
        f"<script>var p=location.pathname;if('{b}'&&p.indexOf('{b}')===0)p=p.slice({len(b)})||'/';"
        f"location.replace('{site_url}'+p+location.search+location.hash)</script></head>"
        f'<body><p>Este portfólio mudou de endereço: <a href="{html.escape(site_url)}">{html.escape(site_url)}</a></p></body></html>'
    )


def build(src: Path, dst: Path, base_path: str = "/portfolio", site_url: str = D.SITE_URL) -> dict:
    base = clean_base_path(base_path)
    src = Path(src).resolve()
    dst = Path(dst).resolve()
    if not src.is_dir() or not (src / "index.html").is_file():
        raise ValueError("site/ with index.html must exist")
    if src == dst or src in dst.parents:
        raise ValueError("Refusing to write inside the source site")
    site_url = site_url.rstrip("/")
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    pages = 0
    for path in sorted(src.rglob("*.html")):
        relative = path.relative_to(src).as_posix()
        if relative == "404.html":
            continue
        out = dst / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(stub(site_url + public_path(relative), base), encoding="utf-8")
        pages += 1
    redirects = 0
    for old, new in D.REDIRECTS.items():
        folder = dst / old.strip("/")
        target = folder / "index.html" if not old.endswith(".html") else dst / old.lstrip("/")
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(stub(site_url + new, base), encoding="utf-8")
        redirects += 1
    (dst / "404.html").write_text(not_found_stub(site_url, base), encoding="utf-8")
    (dst / ".nojekyll").touch()
    (dst / "robots.txt").write_text(f"User-agent: *\nDisallow:\nSitemap: {site_url}/sitemap.xml\n", encoding="utf-8")
    return {"pages": pages, "redirects": redirects, "canonical": site_url + "/", "output": str(dst)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "site")
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    parser.add_argument("--repo", default="xlDuarte/portfolio")
    parser.add_argument("--base-path", default=None)
    parser.add_argument("--site-url", default=D.SITE_URL)
    p = parser.parse_args()
    owner, name = p.repo.split("/", 1)
    path = "/" + name if name.lower() != owner.lower() + ".github.io" else ""
    print(build(p.source, p.output, p.base_path if p.base_path is not None else path, p.site_url))


if __name__ == "__main__":
    main()
