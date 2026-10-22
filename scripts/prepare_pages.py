#!/usr/bin/env python3
"""Build the static portfolio for GitHub Pages project subpaths.

Important: GitHub Pages for user/repo is served at /repo/ by default.
Absolute /cases/... links must be rewritten to /repo/cases/... without
changing external URLs, #anchors, query parameters or local file names.
This builds into a *separate* output tree; source site/ is never modified.

Usage:
 python scripts/prepare_pages.py --repo xlDuarte/portfolio --output _site
 python scripts/prepare_pages.py --base-path '' --site-url https://example.com --output _site
"""
from __future__ import annotations
import argparse
import html
import re
import shutil
from pathlib import Path
from urllib.parse import quote, urlsplit
from xml.etree.ElementTree import Element, SubElement, ElementTree

ROOT=Path(__file__).resolve().parents[1]
_LINK_ATTR=re.compile(
    r'(?P<attribute>\b(?:href|src|action|poster|data-src)\s*=\s*)'
    r'(?P<quote>["\x27])(?P<value>[^"\x27]*)(?P=quote)',re.I)
_CSS_URL=re.compile(r'url\(\s*(?P<quote>["\x27]?)(?P<url>/[^)"\x27]*)(?P=quote)\s*\)',re.I)
_JS_ROUTES=re.compile(r'(?P<quote>["\x27])(?P<path>/(?:cases|assets|f1)(?:/[^"\x27\s]*)?)(?P=quote)')
_TITLE=re.compile(r"<title>(.*?)</title>",re.I|re.S)
_HEAD_END=re.compile(r"</head\s*>",re.I)
_CNAME_RE=re.compile(r"^[a-z0-9][a-z0-9.-]*$",re.I)

def clean_base_path(base_path:str)->str:
    if base_path in ("","/"):return ""
    if not re.fullmatch(r"/[a-zA-Z0-9_-]+/?",base_path):
        raise ValueError("base-path must be one safe, optional repository segment")
    return base_path.rstrip("/")

def rewrite_url(url:str,base_path:str)->str:
    """Change only root-relative URLs, preserving external/protocol-relative."""
    if not url.startswith("/") or url.startswith("//") or not base_path:return url
    if url==base_path or url.startswith(base_path+"/"):return url
    return base_path+url

def rewrite_html(markup:str,base_path:str,canonical_url:str|None=None)->str:
    base=clean_base_path(base_path)
    def attr(match):
        raw=match.group("value")
        return (match.group("attribute")+match.group("quote")+
                rewrite_url(raw,base)+match.group("quote"))
    markup=_LINK_ATTR.sub(attr,markup)
    markup=_CSS_URL.sub(lambda m:'url('+m.group("quote")+
                        rewrite_url(m.group("url"),base)+m.group("quote")+')',markup)
    # Existing inline navigation JS uses string literal paths.
    markup=_JS_ROUTES.sub(lambda m:m.group("quote")+
                          rewrite_url(m.group("path"),base)+m.group("quote"),markup)
    if canonical_url and _HEAD_END.search(markup):
        if not re.search(r'<link\b[^>]*rel=["\x27]canonical["\x27]',markup,re.I):
            title_match=_TITLE.search(markup)
            title=html.unescape(re.sub("<[^>]+>","",title_match.group(1))).strip() if title_match else "Industrial Analytics Portfolio"
            safe=html.escape(title,quote=True)
            snippet=('\n    <link rel="canonical" href="'+html.escape(canonical_url,quote=True)+'">'
                     '\n    <meta property="og:type" content="website">'
                     '\n    <meta property="og:title" content="'+safe+'">'
                     '\n    <meta property="og:url" content="'+html.escape(canonical_url,quote=True)+'">'
                     '\n')
            markup=_HEAD_END.sub(lambda m:snippet+m.group(0),markup,count=1)
    return markup

def build(src:Path,dst:Path,base_path:str="/portfolio",
          site_url:str="https://xlduarte.github.io")->dict:
    base=clean_base_path(base_path)
    src=Path(src).resolve();dst=Path(dst).resolve()
    if not src.is_dir() or not (src/"index.html").is_file():
        raise ValueError("site/ with index.html must exist")
    if src==dst or src in dst.parents and dst.name=="site":
        raise ValueError("Refusing to overwrite source site")
    if dst.exists():shutil.rmtree(dst)
    shutil.copytree(src,dst)
    cname=dst/"CNAME"
    if cname.is_file():
        domain=cname.read_text(encoding="utf-8").strip()
        if not _CNAME_RE.fullmatch(domain):raise ValueError("Invalid Pages custom domain")
        base=""
        site_url="https://"+domain
    site_url=site_url.rstrip("/")
    files=sorted(dst.rglob("*.html"))
    urls=[]
    for path in files:
        relative=path.relative_to(dst).as_posix()
        public_path=relative.replace("index.html","") if relative.endswith("index.html") else relative
        public_url=site_url+base+"/"+quote(public_path,safe="/-._~")
        if relative=="index.html":public_url=site_url+base+"/"
        raw=path.read_text(encoding="utf-8")
        path.write_text(rewrite_html(raw,base,public_url),encoding="utf-8")
        if relative!="404.html":urls.append(public_url)
    (dst/".nojekyll").touch()
    root=Element("urlset",{"xmlns":"http://www.sitemaps.org/schemas/sitemap/0.9"})
    for address in urls:
        node=SubElement(root,"url")
        SubElement(node,"loc").text=address
    ElementTree(root).write(dst/"sitemap.xml",encoding="utf-8",xml_declaration=True)
    (dst/"robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: "+site_url+base+"/sitemap.xml\n",
        encoding="utf-8")
    if not (dst/"404.html").exists():
        (dst/"404.html").write_text(
            '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Página não encontrada · Automotive & Industrial Lab</title></head>'
            '<body style="font:16px system-ui;background:#101923;color:white;padding:3rem">'
            '<h1>Página não encontrada</h1><p>Esta rota não existe.</p>'
            '<a style="color:#8be4d5" href="'+(base or "")+'/">'
            'Voltar ao portfólio</a></body></html>',encoding="utf-8")
    return {"pages":len(files),"sitemap_entries":len(urls),
            "url":site_url+base+"/","output":str(dst)}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=ROOT/"site")
    parser.add_argument("--output",type=Path,default=ROOT/"_site")
    parser.add_argument("--repo",default="xlDuarte/portfolio")
    parser.add_argument("--base-path",default=None)
    parser.add_argument("--site-url",default=None)
    p=parser.parse_args()
    owner,name=p.repo.split("/",1)
    path=("/"+name if name.lower()!=owner.lower()+".github.io" else "")
    report=build(p.source,p.output,p.base_path if p.base_path is not None else path,
                 p.site_url or "https://"+owner.lower()+".github.io")
    print(report)
if __name__=="__main__":
    main()
