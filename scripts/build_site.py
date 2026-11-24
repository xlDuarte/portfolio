#!/usr/bin/env python3
"""Build the static portfolio site in ``site/`` with one shared design system.

What it does (idempotent — safe to run again after any engine regenerates pages):
  1. Renders the hub pages (home, Industrial, Automotivo, F1, Porsche,
     Laboratório, Sobre, 404) from ``scripts/site_data.py`` and the industrial
     catalogue.
  2. Normalises every project page under ``site/cases/`` into one template:
     global header, breadcrumbs, readable metric labels, pt-BR numbers and a
     project sidebar with code links.
  3. Wraps the raw Plotly exports (``interactive.html``) in the same shell.
  4. Injects the global header/footer and stylesheet into the interactive labs.
  5. Writes sitemap.xml, robots.txt and vercel.json (redirects + headers) and
     removes the retired pages listed in ``site_data.REDIRECTS``.

Usage:  python scripts/build_site.py
Requires: beautifulsoup4 (see requirements/site.txt).
"""
from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_data as D  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CATALOG_SRC = ROOT / "site" / "data" / "industrial-catalog.json"
STUDY_FOR_ID = {10: "/cases/supply/"}  # catalogue entries whose page is a full case study

esc = lambda s: html.escape(str(s), quote=True)  # noqa: E731


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------
@dataclass
class Page:
    path: str                      # URL path, e.g. "/industrial/" or "/cases/001/"
    title: str
    description: str
    section: str | None = None     # nav key for current section
    niche: str | None = None       # industrial | automotivo | laboratorio
    crumbs: list[tuple[str, str]] = field(default_factory=list)
    og_image: str = "/assets/og/default.png"
    extra_head: str = ""

    @property
    def file(self) -> Path:
        if self.path.endswith("/"):
            return SITE / self.path.lstrip("/") / "index.html"
        return SITE / self.path.lstrip("/")


OG_FOR_NICHE = {"industrial": "/assets/og/industrial.png", "automotivo": "/assets/og/automotivo.png",
                "laboratorio": "/assets/og/laboratorio.png"}


def head_html(p: Page) -> str:
    og = p.og_image if p.og_image != "/assets/og/default.png" else OG_FOR_NICHE.get(p.niche or "", p.og_image)
    canonical = D.SITE_URL + p.path
    full_title = p.title if D.AUTHOR in p.title else f"{p.title} · {D.AUTHOR}"
    return (
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{esc(full_title)}</title>\n"
        f'<meta name="description" content="{esc(p.description)}">\n'
        f'<link rel="canonical" href="{esc(canonical)}">\n'
        '<meta property="og:type" content="website">\n'
        f'<meta property="og:title" content="{esc(full_title)}">\n'
        f'<meta property="og:description" content="{esc(p.description)}">\n'
        f'<meta property="og:url" content="{esc(canonical)}">\n'
        f'<meta property="og:image" content="{esc(D.SITE_URL + og)}">\n'
        '<meta property="og:locale" content="pt_BR">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="theme-color" content="#ffffff">\n'
        '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">\n'
        '<link rel="preload" href="/assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
        '<link rel="stylesheet" href="/assets/ds.css">\n'
        + p.extra_head
    )


def header_html(p: Page) -> str:
    links = []
    for key, label, href in D.NAV:
        cls = {"industrial": ' class="nav-ind"', "automotivo": ' class="nav-auto"'}.get(key, "")
        current = ""
        if p.path == href:
            current = ' aria-current="page" data-section-current'
        elif p.section == key:
            current = " data-section-current"
        links.append(f'<a href="{href}"{cls}{current}>{label}</a>')
    return (
        "<!-- ds:header -->"
        '<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>'
        '<header class="site-header"><div class="wrap">'
        f'<a class="brand" href="/">{D.AUTHOR}</a>'
        f'<nav class="nav" aria-label="Principal">{"".join(links)}</nav>'
        "</div></header>"
        + crumbs_html(p)
        + "<!-- /ds:header -->"
    )


def crumbs_html(p: Page) -> str:
    if not p.crumbs:
        return ""
    items = [f'<li><a href="{esc(h)}">{esc(t)}</a></li>' for t, h in p.crumbs[:-1]]
    items.append(f'<li aria-current="page">{esc(p.crumbs[-1][0])}</li>')
    return f'<nav class="crumbs wrap" aria-label="Você está em"><ol>{"".join(items)}</ol></nav>'


def footer_html() -> str:
    return (
        "<!-- ds:footer -->"
        '<footer class="site-footer"><div class="wrap">'
        f"<p>{D.AUTHOR} · Dados e engenharia para a indústria e o automobilismo de desempenho.<br>"
        "Cada projeto informa se usa dados reais ou sintéticos.</p>"
        '<nav aria-label="Rodapé">'
        '<a href="/industrial/">Industrial</a><a href="/automotivo/">Automotivo</a>'
        '<a href="/laboratorio/">Laboratório</a><a href="/sobre/">Sobre</a>'
        f'<a href="{D.REPO_URL}">GitHub</a><a href="{D.LINKEDIN_URL}">LinkedIn</a>'
        "</nav></div></footer>"
        "<!-- /ds:footer -->"
    )


def render(p: Page, main: str, body_extra: str = "") -> str:
    niche = f' data-niche="{p.niche}"' if p.niche else ""
    return (
        '<!doctype html>\n<html lang="pt-BR">\n<head>\n' + head_html(p) + "</head>\n"
        f"<body{niche}>\n" + header_html(p) + f'\n<main id="conteudo">\n{main}\n</main>\n'
        + footer_html() + body_extra + "\n</body>\n</html>\n"
    )


def write(p: Page, main: str, body_extra: str = "") -> None:
    p.file.parent.mkdir(parents=True, exist_ok=True)
    p.file.write_text(render(p, main, body_extra), encoding="utf-8")
    PAGES.append(p)


PAGES: list[Page] = []


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def load_catalog() -> list[dict]:
    """Industrial catalogue (#001–#100) grouped by domain."""
    if not CATALOG_SRC.is_file():  # first run: migrate from the retired archive module
        legacy = (SITE / "industry" / "catalog.mjs").read_text(encoding="utf-8")
        data, _ = json.JSONDecoder().raw_decode(legacy[legacy.index("["):])
        groups = []
        for g in data:
            groups.append({"slug": g["slug"], "projects": [
                {"id": pr["id"], "name": pr["name"][0], "desc": pr["desc"][0], "code": pr["code"],
                 "page": ("/" + pr["view"].replace("../", "").strip("/") + "/") if pr.get("view") else STUDY_FOR_ID[pr["id"]]}
                for pr in g["projects"]]})
        CATALOG_SRC.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_SRC.write_text(json.dumps(groups, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return json.loads(CATALOG_SRC.read_text(encoding="utf-8"))


def project_index(groups: list[dict]) -> dict[str, dict]:
    """Map project page path → project record with its domain slug."""
    out = {}
    for g in groups:
        for i, pr in enumerate(g["projects"]):
            out[pr["page"]] = {**pr, "domain": g["slug"], "pos": i, "siblings": g["projects"]}
    return out


# ---------------------------------------------------------------------------
# Number and label formatting
# ---------------------------------------------------------------------------
_NUM = re.compile(r"^-?\d+(?:\.\d+)?$")


def fmt_ptbr(value: float, decimals: int) -> str:
    s = f"{value:,.{decimals}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def fmt_num(text: str) -> str:
    """Readable pt-BR numbers: 39257.0871 → 39.257; 0.9369 → 0,937; keeps ints/years."""
    t = text.strip()
    if not _NUM.match(t):
        return text
    if "." not in t:
        n = int(t)
        return fmt_ptbr(n, 0) if abs(n) >= 10000 else t
    v = float(t)
    a = abs(v)
    if a >= 1000:
        return fmt_ptbr(v, 0)
    if a >= 100:
        return fmt_ptbr(v, 1)
    if a >= 1:
        return fmt_ptbr(v, 2)
    return fmt_ptbr(v, 3)


LABELS = {
    "dataset": "Base de dados", "project": "Projeto", "mae": "MAE", "rmse": "RMSE", "r2": "R²",
    "roc_auc": "ROC-AUC", "f1": "F1", "smape": "sMAPE", "mape": "MAPE", "wape": "WAPE",
    "brier_score": "Brier", "average_precision": "Precisão média",
}


def humanize(key: str) -> str:
    k = key.strip()
    if k.lower() in LABELS:
        return LABELS[k.lower()]
    if "_" not in k and not (k.islower() and " " in k):
        return k
    words = k.replace("_", " ").split()
    acr = {"mae", "rmse", "r2", "auc", "roc", "f1", "kpi", "oee", "otif", "ltv", "capex", "sku", "id", "brl", "usd", "co2", "mw", "kwh", "pct"}
    out = [w.upper() if w.lower() in acr else w for w in words]
    out[0] = out[0][:1].upper() + out[0][1:]
    return " ".join(out).replace("PCT", "%")


# ---------------------------------------------------------------------------
# Hub pages
# ---------------------------------------------------------------------------
def tags_html(tags) -> str:
    return "".join(f'<span class="tag">{esc(t)}</span>' for t in tags)


def row_html(pid, title, desc, href, tags) -> str:
    pid_txt = f"#{pid:03d}" if isinstance(pid, int) else (pid or "")
    return (f'<li><a class="row" href="{esc(href)}"><span class="id">{esc(pid_txt)}</span>'
            f'<span class="title">{esc(title)}</span><span class="desc">{esc(desc)}</span>'
            f'<span class="tags">{tags}</span></a></li>')


HERO_DATA = SITE / "assets" / "hero" / "hero-data.json"
PORTRAIT = ('<img class="{cls}" src="/assets/gabriel-retrato-480.webp" '
            'srcset="/assets/gabriel-retrato-480.webp 480w, /assets/gabriel-retrato-960.webp 960w" '
            'sizes="{sizes}" width="480" height="600" alt="Gabriel Reis Duarte de óculos escuros e camiseta branca, '
            'num deck de madeira à beira de um lago" loading="{loading}" decoding="async">')
HERO_SCRIPT = """<script type="module">
const root = document.querySelector(".stage");
const hasGL = (() => { try { const c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); } catch { return false; } })();
if (hasGL && root) {
  const start = () => import("/assets/js/hero.js").then((m) => m.mountHero(root)).catch(() => { root.dataset.state = "fallback"; });
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 1));
  if (document.readyState === "complete") idle(start); else addEventListener("load", () => idle(start), { once: true });
} else if (root) {
  root.dataset.state = "fallback";
}
</script>"""


def hub_script(entry: str) -> str:
    """Load a hub scene only with WebGL, after the page has rendered; otherwise keep static content."""
    return f"""<script type="module">
const root = document.querySelector("[data-hub]");
const gl = (() => {{ try {{ const c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); }} catch {{ return false; }} }})();
const needsGL = root && root.dataset.hub !== "sobre";
if (root && (gl || !needsGL)) {{
  const start = () => import("/assets/js/hub-{entry}.js").then((m) => m.mount(root)).catch(() => {{ root.dataset.state = "fallback"; }});
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 1));
  if (document.readyState === "complete") idle(start); else addEventListener("load", () => idle(start), {{ once: true }});
}} else if (root) {{
  root.dataset.state = "fallback";
}}
</script>"""


HUB_HEAD = '<link rel="stylesheet" href="/assets/hero/hero.css"><link rel="stylesheet" href="/assets/hubs/hubs.css">'


def hub_stage(entry: str, inner: str = "", cls: str = "", label: str = "") -> str:
    return (f'<section class="hub-stage {cls}" data-hub="{entry}" data-state="static" aria-label="{esc(label)}">'
            f'<div class="hub-view"><canvas aria-hidden="true"></canvas></div>{inner}</section>')


def pct_br(v: float) -> str:
    return f"{v * 100:.1f}%".replace(".", ",")


def hero_html(n_ind: int) -> str:
    """Home hero. Static numbers come from hero-data.json so text and scene never disagree."""
    data = json.loads(HERO_DATA.read_text(encoding="utf-8"))
    ind, f1 = data["industrial"], data["f1"]
    names = {c["code"]: c["name"] for c in f1["cars"]}
    laps = sorted({s[7] for c in f1["cars"] for s in c["samples"] if s[7]})
    rows = "".join(
        f'<tr><th scope="row">{esc(l["line"].split("-")[-1])}</th><td>{pct_br(l["availability"])}</td>'
        f'<td>{pct_br(l["performance"])}</td><td>{pct_br(l["quality"])}</td></tr>' for l in ind["lines"])
    status = "".join(f'<p>Linha {esc(l["line"].split("-")[-1])} <span class="status" data-status="{i}" data-state="run">em operação</span></p>'
                     for i, l in enumerate(ind["lines"]))
    cars = "".join(f'<p data-car="{esc(c["code"])}"><b>{esc(c["code"])}</b><span data-v>—</span><span data-g></span></p>'
                   for c in f1["cars"])
    lead = f1["cars"][0]
    who = ", ".join(names[c["code"]] for c in f1["cars"][:-1]) + " e " + names[f1["cars"][-1]["code"]]
    return f"""
<section class="hero" aria-labelledby="hero-title">
  <div class="wrap hero-head">
    <h1 class="hero-name" id="hero-title">{esc(D.AUTHOR)}</h1>
    <p class="lede">Dados, software e engenharia para dois nichos: a operação industrial e o automobilismo de desempenho.</p>
  </div>
  <div class="stage" data-state="static">
    <div class="stage-under" aria-hidden="true"><span></span><span></span></div>
    <div class="stage-view">
      <img class="stage-fallback" src="/assets/hero/hero-fallback.svg" width="1200" height="560" alt="">
      <canvas aria-hidden="true"></canvas>
    </div>
    <div class="hud hud-ind" aria-hidden="true">
      <p class="hud-title">OEE ponderado <strong data-oee>{pct_br(ind["oee_weighted"])}</strong></p>
      {status}
    </div>
    <div class="hud hud-auto" aria-hidden="true">
      <div class="hud-cols">
        <div>
          <p class="hud-title">Sakhir {esc(f1["session"][7:11])} <strong data-lap>Volta {laps[0]} de {f1["race_laps"]}</strong></p>
          {cars}
          <p class="hud-sub">Disco dianteiro de {esc(lead["code"])} (modelo) <strong data-disc>—</strong></p>
        </div>
        <figure class="gg-wrap">
          <canvas class="gg" width="104" height="104"></canvas>
          <figcaption><span>lateral <strong data-glat>—</strong></span><span data-glong>—</span></figcaption>
        </figure>
      </div>
    </div>
    <div class="halves">
      <div class="half ind">
        <div class="view-dim" aria-hidden="true"></div>
        <div class="cap">
          <h2><a class="half-link" href="/industrial/">Industrial</a></h2>
          <p class="origin">Dados sintéticos, semente fixa</p>
          <p>Operação fabril, custos e cadeia de suprimentos: {len(D.INDUSTRIAL_FEATURED)} estudos de caso completos e {n_ind} projetos de dados. Na maquete, a esteira para pela disponibilidade, corre pelo desempenho, solda cada peça e descarta as reprovadas pela qualidade.</p>
          <table class="readout">
            <caption>OEE ponderado pelo tempo programado: <strong>{pct_br(ind["oee_weighted"])}</strong></caption>
            <thead><tr><th scope="col">Linha</th><th scope="col">Disponib.</th><th scope="col">Desemp.</th><th scope="col">Qualidade</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
      </div>
      <div class="half auto">
        <div class="view-dim" aria-hidden="true"></div>
        <div class="cap">
          <h2><a class="half-link" href="/automotivo/">Automotivo de desempenho</a></h2>
          <p class="origin">Dados reais, OpenF1</p>
          <p>Fórmula 1 ({len(D.F1_TOOLS)} ferramentas, {len(D.F1_PROJECTS)} projetos) e Porsche Cup. A maquete reproduz quatro minutos do GP do Bahrein de 2024 com {esc(who)}, relevo de Sakhir exagerado <span data-elevation>4</span> vezes.</p>
          <p class="legend">Cor da pista: velocidade de {esc(lead["name"].split()[-1])} na volta<span class="ramp" aria-hidden="true"></span><span data-speed-range>—</span></p>
          <p class="legend">Forças g estimadas da telemetria pública (picos subestimados pela amostragem de ~3,7 Hz); temperatura do disco por modelo térmico. Inclinação dos carros exagerada para leitura.</p>
        </div>
      </div>
    </div>
    <span class="seam" aria-hidden="true"></span>
    <a class="bridge" href="/laboratorio/"><strong>Laboratório comum</strong><span>{len(D.SHARED_PROJECTS)} projetos para os dois nichos</span></a>
  </div>
</section>"""


def build_home(groups) -> None:
    n_ind = sum(len(g["projects"]) for g in groups)
    p = Page("/", f"{D.AUTHOR} · Dados para indústria e automobilismo",
             "Portfólio de Gabriel Reis Duarte: dados, software e engenharia aplicados a operações industriais e ao automobilismo de desempenho (Fórmula 1 e Porsche Cup).",
             og_image="/assets/og/default.png")
    portrait = PORTRAIT.format(cls="home-portrait", sizes="(max-width: 720px) 40vw, 240px", loading="lazy")
    main = hero_html(n_ind) + f"""
<section class="wrap section home-about">
  {portrait}
  <div>
    <h2>Quem faz</h2>
    <p>Sou analista de dados com formação em Direito, Análise e Desenvolvimento de Sistemas e Ciência da Computação (2026). Trabalhei com supply chain, logística e controladoria na indústria e estudo telemetria e física de pista no automobilismo.</p>
    <p><a href="/sobre/">Experiência, formação e método</a></p>
  </div>
</section>
<section class="wrap section">
  <h2>Como ler este portfólio</h2>
  <div class="cols-2">
    <p>Cada projeto diz de onde vêm os dados. Os projetos de Fórmula 1 usam sessões reais públicas (OpenF1 e FastF1). Os projetos industriais usam bases sintéticas geradas com semente fixa, porque dados de fábrica são confidenciais.</p>
    <p>O código está aberto no GitHub, com testes automatizados rodando a cada alteração. Os resultados mostram que o método funciona como descrito; não são ganho medido em uma empresa.</p>
  </div>
</section>"""
    p.extra_head = ('<link rel="stylesheet" href="/assets/hero/hero.css">'
                    "<style>.home-about{display:grid;grid-template-columns:240px 1fr;gap:40px;align-items:center}"
                    ".home-portrait{width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;border-radius:10px}"
                    ".cols-2{display:grid;grid-template-columns:1fr 1fr;gap:32px}"
                    "@media(max-width:720px){.home-about{grid-template-columns:1fr;gap:20px}.home-portrait{max-width:280px}.cols-2{grid-template-columns:1fr;gap:0}}</style>")
    write(p, main, body_extra=HERO_SCRIPT)


def build_industrial(groups) -> None:
    p = Page("/industrial/", "Industrial",
             "Projetos de dados para operações industriais: OEE, supply chain, CAPEX, previsão de demanda, qualidade e 100 projetos de análise e machine learning.",
             section="industrial", niche="industrial", crumbs=[("Início", "/"), ("Industrial", "/industrial/")])
    feats = "".join(
        f'<article class="feature"><h3><a href="/cases/{f["slug"]}/">{esc(f["title"])}</a></h3>'
        f'<p>{esc(f["desc"])}</p>{tags_html(f["tags"] + ["Estudo completo"])}</article>'
        for f in D.INDUSTRIAL_FEATURED)
    nav = "".join(f'<a href="#{g["slug"]}">{esc(D.DOMAINS[g["slug"]][0])}</a>' for g in groups)
    blocks = []
    for g in groups:
        name, blurb = D.DOMAINS[g["slug"]]
        rows = "".join(
            row_html(pr["id"], pr["name"], pr["desc"], pr["page"],
                     '<span class="tag feature">Mais completo</span>' if pr["id"] in D.INDUSTRIAL_STRONG else "")
            for pr in g["projects"])
        first, last = g["projects"][0]["id"], g["projects"][-1]["id"]
        head = f'<a href="/cases/{g["slug"]}/">{esc(name)}</a>' if g["slug"] in DOMAIN_PAGES else esc(name)
        blocks.append(
            f'<div class="group" id="{g["slug"]}"><div class="group-head"><h3>{head}</h3>'
            f'<p>#{first:03d}–#{last:03d} · {esc(blurb)}</p></div><ul class="index">{rows}</ul></div>')
    total = sum(len(g["projects"]) for g in groups)
    main = f"""
<section class="wrap page-head">
  <h1>Industrial</h1>
  <p class="lede">Dados de operação, custos e cadeia de suprimentos, tratados com o mesmo rigor de uma análise que vai para a diretoria.</p>
</section>
{hub_stage("industrial", '<p class="hub-hint wrap">Gêmeo digital: cada estação é um estudo de caso e se move com os números dele (dados sintéticos). Clique numa estação para abrir o estudo.</p>', label="Gêmeo digital dos cinco estudos de caso")}
<section class="wrap section" aria-labelledby="destaques">
  <h2 id="destaques">Estudos de caso completos</h2>
  <p class="muted">Cinco estudos com problema, método, base de dados versionada, gráfico, métricas e código. São o melhor ponto de partida.</p>
  <div class="features">{feats}</div>
</section>
<section class="wrap section" aria-labelledby="catalogo" id="catalogo">
  <h2>Catálogo de projetos</h2>
  <div class="note"><p>Os {total} projetos abaixo são exercícios técnicos curtos, organizados por técnica. Cada um roda de verdade sobre uma base sintética e tem teste automatizado, mas compartilha o motor de cálculo com os demais do mesmo grupo. Os marcados como <strong>mais completo</strong> têm implementação própria mais extensa.</p></div>
  <nav class="jump" aria-label="Grupos do catálogo">{nav}</nav>
  {''.join(blocks)}
</section>"""
    p.extra_head = ("<style>.jump{display:flex;flex-wrap:wrap;gap:6px;margin:24px 0 40px}"
                    ".jump a{font-size:.875rem;text-decoration:none;padding:6px 10px;border:1px solid var(--rule);border-radius:999px;color:var(--slate)}"
                    ".jump a:hover{border-color:var(--accent);color:var(--accent)}</style>" + HUB_HEAD)
    write(p, main, body_extra=hub_script("industrial"))


DOMAIN_PAGES = {"eda", "regression", "classification", "nlp", "recommendation", "timeseries", "vision", "business", "advanced"}


def build_domain_pages(groups) -> None:
    """One listing page per technique (/cases/<domain>/), used as breadcrumb target."""
    for g in groups:
        if g["slug"] not in DOMAIN_PAGES:
            continue
        name, blurb = D.DOMAINS[g["slug"]]
        first, last = g["projects"][0]["id"], g["projects"][-1]["id"]
        rows = "".join(
            row_html(pr["id"], pr["name"], pr["desc"], pr["page"],
                     '<span class="tag feature">Mais completo</span>' if pr["id"] in D.INDUSTRIAL_STRONG else "")
            for pr in g["projects"])
        p = Page(f"/cases/{g['slug']}/", f"{name} · projetos #{first:03d}–#{last:03d}",
                 f"{name}: {len(g['projects'])} projetos industriais (#{first:03d}–#{last:03d}). {blurb}",
                 section="industrial", niche="industrial",
                 crumbs=[("Início", "/"), ("Industrial", "/industrial/"), (name, f"/cases/{g['slug']}/")])
        main = f"""
<section class="wrap page-head">
  <p class="kicker">Industrial · #{first:03d}–#{last:03d}</p>
  <h1>{esc(name)}</h1>
  <p class="lede">{esc(blurb)}</p>
  <div class="note"><p>Exercícios técnicos sobre bases sintéticas com semente fixa. Cada projeto roda de verdade e tem teste automatizado; não representam resultado medido em empresa.</p></div>
</section>
<section class="wrap section"><ul class="index">{rows}</ul></section>"""
        write(p, main)


def build_motorsport_index() -> None:
    """Listing of #101–#110 split by category, kept at the historical /cases/motorsport/ URL."""
    def rows(items, extra=lambda x: ""):
        return "".join(row_html(x["id"], x["title"], x["desc"], x["path"], extra(x)) for x in items)
    p = Page("/cases/motorsport/", "Projetos automotivos #101–#111",
             "Projetos de automobilismo e MLOps #101–#111, separados em Fórmula 1, Porsche Cup e laboratório comum.",
             section="automotivo", niche="automotivo",
             crumbs=[("Início", "/"), ("Automotivo", "/automotivo/"), ("Projetos #101–#111", "/cases/motorsport/")])
    pip = {"id": 111, "title": "Modelos e probabilidades de corrida", "desc": D.F1_TOOLS[0]["desc"], "path": "/motorsport/f1-pip/"}
    main = f"""
<section class="wrap page-head">
  <p class="kicker">Automotivo de desempenho</p>
  <h1>Projetos #101–#111</h1>
  <p class="lede">Todos os projetos numerados de automobilismo e MLOps, organizados pelo lugar onde se aplicam.</p>
</section>
<section class="wrap section">
  <div class="group"><div class="group-head"><h3><a href="/automotivo/f1/">Fórmula 1</a></h3><p>Dados reais OpenF1 e FastF1</p></div>
    <ul class="index">{rows(D.F1_PROJECTS + [pip])}</ul></div>
  <div class="group"><div class="group-head"><h3><a href="/automotivo/porsche/">Porsche Cup</a></h3><p>Aquisição importada</p></div>
    <ul class="index">{rows([D.PORSCHE_PROJECT])}</ul></div>
  <div class="group"><div class="group-head"><h3><a href="/laboratorio/">Laboratório comum</a></h3><p>Serve à indústria e ao automobilismo</p></div>
    <ul class="index">{rows(D.SHARED_PROJECTS)}</ul></div>
</section>"""
    write(p, main)


def build_automotivo() -> None:
    p = Page("/automotivo/", "Automotivo de desempenho",
             "Projetos de engenharia de corrida: Fórmula 1 com dados reais OpenF1/FastF1 e laboratório de engenharia Porsche Cup.",
             section="automotivo", niche="automotivo", crumbs=[("Início", "/"), ("Automotivo", "/automotivo/")])
    garages = hub_stage("automotivo", f"""<div class="halves">
  <div class="half auto" data-half="0"><div class="view-dim" aria-hidden="true"></div>
    <div class="cap"><h2><a class="half-link" href="/automotivo/f1/"><img class="brand-mark" src="/assets/brands/formula-1.svg" alt="" width="30" height="30">Fórmula 1</a></h2><p>{len(D.F1_TOOLS)} ferramentas e {len(D.F1_PROJECTS)} projetos com sessões reais.</p></div></div>
  <div class="half auto" data-half="1"><div class="view-dim" aria-hidden="true"></div>
    <div class="cap"><h2><a class="half-link" href="/automotivo/porsche/"><img class="brand-mark" src="/assets/brands/porsche.svg" alt="" width="30" height="30">Porsche Cup</a></h2><p>Laboratório de engenharia: carga por roda, pneus e dinâmica.</p></div></div>
</div><span class="seam" aria-hidden="true"></span><p class="hub-hint wrap">Carros genéricos, não réplicas. Arraste para girar a plataforma.</p>""", cls="is-split", label="Garagens de Fórmula 1 e Porsche Cup")
    main = f"""
<section class="wrap page-head">
  <h1>Automotivo de desempenho</h1>
  <p class="lede">Engenharia de corrida com dados: telemetria, estratégia, física de pista e dinâmica veicular.</p>
</section>
{garages}
<section class="wrap" aria-label="Categorias">
  <div class="tiles">
    <a class="tile" href="/automotivo/f1/"><h3>Fórmula 1</h3>
      <p>Probabilidades de corrida, estratégia de pneus, replay e laboratórios de aerodinâmica, energia e tempo de volta.</p>
      <span class="meta">{len(D.F1_TOOLS)} ferramentas interativas · {len(D.F1_PROJECTS)} projetos · dados reais de 2022–2024</span></a>
    <a class="tile" href="/automotivo/porsche/"><h3>Porsche Cup</h3>
      <p>Carga por roda, temperatura de pneus e dinâmica veicular a partir de uma aquisição importada do carro.</p>
      <span class="meta">Laboratório de engenharia · {len(D.PORSCHE_MODULES)} módulos</span></a>
  </div>
  <a class="shared" href="/laboratorio/">
    <span class="swatch" aria-hidden="true"></span>
    <span><strong>Também usado aqui: laboratório comum</strong><span class="muted small">Vibração, visão computacional, MLOps e explicabilidade servem tanto ao carro quanto à fábrica.</span></span>
    <span class="go small">Abrir laboratório</span>
  </a>
</section>
<section class="wrap section">
  <h2>De onde vêm os dados</h2>
  <p>As ferramentas de Fórmula 1 carregam sessões públicas do OpenF1 (corrida do Bahrein 2024) e resultados de 2022 a 2024 via FastF1 e Jolpica. Não é live timing e não há dado de equipe. O laboratório Porsche trabalha sobre a aquisição que você importar; sem arquivo, nada é preenchido com valores inventados.</p>
  <p><a href="/cases/motorsport/">Ver a lista completa dos projetos #101–#111</a></p>
  <p class="small muted">Projeto independente, sem vínculo com a Fórmula 1, a FIA, a Porsche ou equipes. Marcas citadas pertencem aos seus titulares.</p>
</section>"""
    p.extra_head = HUB_HEAD
    write(p, main, body_extra=hub_script("automotivo"))


def build_f1() -> None:
    p = Page("/automotivo/f1/", "Fórmula 1",
             "Ferramentas e projetos de Fórmula 1 com dados reais: probabilidades de corrida, estratégia de pneus, replay, aerodinâmica ativa, recuperação de energia e tempo de volta.",
             section="automotivo", niche="automotivo",
             crumbs=[("Início", "/"), ("Automotivo", "/automotivo/"), ("Fórmula 1", "/automotivo/f1/")])
    tools = "".join(
        f'<article class="feature"><h3><a href="{t["path"]}">{esc(t["title"])}</a></h3><p>{esc(t["desc"])}</p>{tags_html(t["tags"])}</article>'
        for t in D.F1_TOOLS)
    rows = "".join(row_html(x["id"], x["title"], x["desc"], x["path"], tags_html(x["tags"])) for x in D.F1_PROJECTS)
    main = f"""
<section class="wrap page-head">
  <p class="kicker">Automotivo de desempenho</p>
  <h1><img class="brand-mark" src="/assets/brands/formula-1.svg" alt="" width="40" height="40">Fórmula 1</h1>
  <p class="lede">Probabilidades, estratégia e física de pista calculadas sobre sessões reais públicas.</p>
  <nav class="subnav" aria-label="Categorias automotivas"><a href="/automotivo/f1/" aria-current="page">Fórmula 1</a><a href="/automotivo/porsche/">Porsche Cup</a></nav>
</section>
{hub_stage("f1", f1_hud(), label="Replay de quatro minutos do GP do Bahrein de 2024")}
<p class="wrap small muted">Marcas e logotipos pertencem aos seus titulares. Projeto independente, sem vínculo com a Fórmula 1, a FIA ou as equipes.</p>
<section class="wrap section" aria-labelledby="ferramentas">
  <h2 id="ferramentas">Ferramentas interativas</h2>
  <p class="muted">Rodam no navegador. Carregue o recorte real do Bahrein 2024 ou importe um CSV exportado pelo FastF1.</p>
  <div class="features">{tools}</div>
</section>
<section class="wrap section" aria-labelledby="projetos">
  <h2 id="projetos">Projetos</h2>
  <ul class="index">{rows}</ul>
</section>"""
    p.extra_head = SUBNAV_CSS + HUB_HEAD
    write(p, main, body_extra=hub_script("f1"))


def f1_hud() -> str:
    data = json.loads(HERO_DATA.read_text(encoding="utf-8"))["f1"]
    rows = "".join(f'<tr data-car="{esc(c["code"])}"><th scope="row">{esc(c["code"])}</th><td data-v>—</td><td data-g>—</td>'
                   f'<td data-lat>—</td><td data-lon>—</td><td data-disc>—</td></tr>' for c in data["cars"])
    return f"""<div class="hud hud-f1" aria-hidden="true">
  <p class="hud-title">Sakhir 2024 <strong data-lap>Volta 2 de {data["race_laps"]}</strong></p>
  <div class="hud-cols">
    <table class="hud-table"><thead><tr><th></th><th>Veloc.</th><th>Marcha</th><th>Lateral</th><th>Longit.</th><th>Disco*</th></tr></thead><tbody>{rows}</tbody></table>
    <canvas class="gg" width="104" height="104"></canvas>
  </div>
  <p class="hud-sub">*Disco dianteiro por modelo térmico. Forças g estimadas da telemetria pública.</p>
</div>"""


SUBNAV_CSS = ("<style>.subnav{display:flex;gap:4px;margin-top:20px;border-bottom:1px solid var(--rule)}"
              ".subnav a{text-decoration:none;padding:10px 14px;margin-bottom:-1px;border-bottom:2px solid transparent;color:var(--slate);font-weight:600}"
              ".subnav a[aria-current]{color:var(--accent);border-color:var(--accent)}"
              ".subnav a:hover{color:var(--graphite)}</style>")


def build_porsche() -> None:
    pp = D.PORSCHE_PROJECT
    p = Page("/automotivo/porsche/", "Porsche Cup",
             "Laboratório de engenharia inspirado na Porsche Cup: carga por roda, temperatura de pneus e dinâmica veicular a partir de aquisição importada.",
             section="automotivo", niche="automotivo",
             crumbs=[("Início", "/"), ("Automotivo", "/automotivo/"), ("Porsche Cup", "/automotivo/porsche/")])
    mods = "".join(
        f'<article class="feature"><h3><a href="{pp["path"]}{m["anchor"]}">{esc(m["title"])}</a></h3><p>{esc(m["desc"])}</p></article>'
        for m in D.PORSCHE_MODULES)
    main = f"""
<section class="wrap page-head">
  <p class="kicker">Automotivo de desempenho</p>
  <h1><img class="brand-mark" src="/assets/brands/porsche.svg" alt="" width="40" height="40">Porsche Cup</h1>
  <p class="lede">Engenharia de pista para um carro de turismo de competição: o que cada roda está fazendo, a cada instante.</p>
  <nav class="subnav" aria-label="Categorias automotivas"><a href="/automotivo/f1/">Fórmula 1</a><a href="/automotivo/porsche/" aria-current="page">Porsche Cup</a></nav>
</section>
{gt3_photo()}
{hub_stage("porsche", porsche_panel(), cls="with-panel", label="Carro GT com modelo de carga por roda")}
<section class="wrap section">
  <div class="cols">
    <div>
      <h2>{esc(pp["title"])}</h2>
      <p>{esc(pp["desc"])} O laboratório foi pensado para o fluxo de um engenheiro de pista: importar, checar canais, comparar voltas e exportar.</p>
      <div class="actions"><a class="btn" href="{pp["path"]}">Abrir o laboratório</a><a class="btn secondary" href="{D.REPO_URL}/tree/main/{pp["code"]}">Ver o código</a></div>
      <h3 style="margin-top:40px">Módulos</h3>
      <div class="features">{mods}</div>
    </div>
    <aside class="aside">
      <h2>Ficha</h2>
      <ul><li>Projeto #{pp["id"]}</li><li>Dados: aquisição importada pelo usuário</li><li>Sem dados do fabricante</li><li>Roda no navegador</li></ul>
      <p class="small muted">Projeto independente, sem vínculo com a Porsche AG. O nome identifica a categoria estudada.</p>
    </aside>
  </div>
</section>"""
    p.extra_head = SUBNAV_CSS + HUB_HEAD
    write(p, main, body_extra=hub_script("porsche"))


BRAND_SOURCES = SITE / "assets" / "brands" / "SOURCES.json"


def gt3_photo() -> str:
    """Category photo. Credit text comes from SOURCES.json so provenance and caption never diverge."""
    src = {e["file"]: e for e in json.loads(BRAND_SOURCES.read_text(encoding="utf-8"))["files"]}
    entry = src["assets/photos/911-gt3-cup-1600.webp"]
    credit = "" if entry["status"] == "pending" else f' {esc(entry["credit"])}, não é fotografia.'
    return f"""<figure class="gt3-photo">
  <img src="/assets/photos/911-gt3-cup-1600.webp" srcset="/assets/photos/911-gt3-cup-800.webp 800w, /assets/photos/911-gt3-cup-1600.webp 1600w"
       sizes="(max-width: 1240px) 100vw, 1160px" width="1600" height="900" alt="Imagem gerada por IA de um Porsche 911 GT3 Cup prata, vermelho e grafite contornando uma curva" decoding="async" fetchpriority="high">
  <figcaption>O 911 GT3 Cup, carro da categoria estudada no laboratório.{credit} Marcas pertencem aos seus titulares. Projeto independente, sem vínculo com a Porsche AG.</figcaption>
</figure>"""


def porsche_panel() -> str:
    """Controls for the load-transfer model (ranges = LIMITS in site/motorsport/porsche/model.mjs)."""
    def slider(id_, label, lo, hi, step, val, unit):
        return (f'<div class="ctl"><label for="{id_}">{label}</label><input type="range" id="{id_}" min="{lo}" max="{hi}" step="{step}" value="{val}">'
                f'<output for="{id_}">{val} {unit}</output></div>')
    cells = "".join(f'<td data-w="{w}">—</td>' for w in ("FL", "FR", "RL", "RR"))
    return f"""<div class="pc-panel wrap">
  <div class="pc-controls">
    <p class="pc-title">Cenário</p>
    {slider("pc-speed", "Velocidade", 60, 240, 1, 160, "km/h")}
    {slider("pc-ay", "Aceleração lateral", -1.2, 1.2, 0.01, 0.8, "g")}
    {slider("pc-ax", "Aceleração longitudinal", -0.8, 0.5, 0.01, 0, "g")}
    <button type="button" class="btn secondary" data-auto hidden>Voltar ao ciclo automático</button>
  </div>
  <div class="pc-out" data-loads>
    <table class="readout"><caption>Carga vertical por roda (modelo do laboratório)</caption>
      <thead><tr><th scope="col">Diant. esq.</th><th scope="col">Diant. dir.</th><th scope="col">Tras. esq.</th><th scope="col">Tras. dir.</th></tr></thead>
      <tbody><tr>{cells}</tr></tbody></table>
    <dl class="pc-kpis"><div><dt>Carga no eixo dianteiro</dt><dd data-front>—</dd></div><div><dt>Downforce</dt><dd data-down>—</dd></div><div><dt>Uso da aderência</dt><dd data-util>—</dd></div></dl>
    <p class="small muted">Transferência de carga longitudinal e lateral, downforce e distribuição de rolagem do modelo #110. Carro genérico, não réplica; inclinação exagerada cerca de 2× para leitura.</p>
  </div>
</div>"""


def build_lab() -> None:
    p = Page("/laboratorio/", "Laboratório comum",
             "Projetos que servem à indústria e ao automobilismo: visão computacional, detecção de anomalias em vibração, inspeção radiográfica, MLOps e explicabilidade, além da qualidade do código.",
             section="laboratorio", niche="laboratorio", crumbs=[("Início", "/"), ("Laboratório", "/laboratorio/")])
    rows = "".join(
        f'<li><a class="row" href="{x["path"]}"><span class="id">#{x["id"]:03d}</span><span class="title">{esc(x["title"])}</span>'
        f'<span class="desc">{esc(x["desc"])}</span><span class="tags"><span class="tag">{esc(x["both"])}</span></span></a></li>'
        for x in D.SHARED_PROJECTS)
    main = f"""
<section class="wrap page-head">
  <p class="kicker">Para os dois nichos</p>
  <h1>Laboratório comum</h1>
  <p class="lede">Técnicas que funcionam igual na fábrica e na pista. Um sensor de vibração num mancal e num câmbio pede o mesmo método.</p>
</section>
{hub_stage("lab", LAB_PANEL, cls="with-panel", label="Nuvem de pontos que muda entre três técnicas")}
<section class="wrap section" aria-labelledby="projetos">
  <h2 id="projetos">Projetos</h2>
  <ul class="index">{rows}</ul>
</section>
<section class="wrap section" aria-labelledby="qualidade">
  <h2 id="qualidade">Testes e qualidade</h2>
  <div class="cols-2">
    <div><h3>O que é verificado</h3><p>Cada alteração no repositório roda a suíte automatizada no GitHub Actions: catálogo dos 111 projetos, execução dos algoritmos sobre as bases de teste, contratos de API e SQL, treinos curtos e as páginas deste site.</p>
      <div class="actions"><a class="btn secondary" href="{D.REPO_URL}/actions">Ver execuções</a><a class="btn secondary" href="{D.REPO_URL}/tree/main/tests">Ver testes</a></div></div>
    <div><h3>O que não é afirmado</h3><p>Os testes mostram que o código faz o que diz. Não mostram desempenho em dados de uma empresa, operação segura de equipamentos ou ganho financeiro. A matriz de evidências separa, projeto a projeto, o que foi feito do que não foi.</p>
      <div class="actions"><a class="btn secondary" href="{D.REPO_URL}/blob/main/TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv">Matriz de evidências</a></div></div>
  </div>
</section>"""
    p.extra_head = "<style>.cols-2{display:grid;grid-template-columns:1fr 1fr;gap:40px}@media(max-width:720px){.cols-2{grid-template-columns:1fr;gap:16px}}</style>" + HUB_HEAD
    write(p, main, body_extra=hub_script("lab"))


LAB_PANEL = """<div class="lab-panel wrap">
  <div class="lab-tabs" role="group" aria-label="Técnica mostrada">
    <button type="button" data-shape aria-pressed="true">Vibração</button>
    <button type="button" data-shape aria-pressed="false">Raio-X</button>
    <button type="button" data-shape aria-pressed="false">Fluxo óptico</button>
  </div>
  <div data-panel="vibracao"><p>Modos de vibração de uma placa apoiada, superpostos. O mesmo sinal aparece num mancal de fábrica e numa suspensão. <a href="/cases/motorsport/104/">Projeto #104: anomalias em vibração</a></p></div>
  <div data-panel="raiox" hidden><p>Uma engrenagem inspecionada por pontos; em vermelho, a trinca na raiz do dente que o modelo destaca. <a href="/cases/motorsport/105/">Projeto #105: raio-X com CNN e Grad-CAM</a></p></div>
  <div data-panel="fluxo" hidden><p>Vórtice de Rankine: núcleo girando como corpo rígido, velocidade caindo com 1/r fora dele. É o tipo de campo que o fluxo óptico mede em vídeo. <a href="/cases/motorsport/103/">Projeto #103: visão computacional em vídeo</a></p></div>
</div>"""


def build_sobre() -> None:
    p = Page("/sobre/", "Sobre",
             "Gabriel Reis Duarte: formação em sistemas, ciência da computação, direito e finanças; experiência em análise de dados industrial, backend e redação técnica.",
             section="sobre", crumbs=[("Início", "/"), ("Sobre", "/sobre/")])
    exp = "".join(
        f'<li><span class="when">{esc(w)}</span><h3>{esc(r)}</h3><p class="muted small">{esc(o)}</p><p>{esc(d)}</p></li>'
        for w, o, r, d in reversed(D.EXPERIENCE))
    edu = "".join(f"<li>{esc(e)}</li>" for e in D.EDUCATION)
    main = f"""
<section class="wrap page-head">
  <h1>Sobre</h1>
  <p class="lede">Trabalho na fronteira entre dados, software e engenharia. Venho do direito empresarial, passei pelo desenvolvimento backend e hoje construo análises e modelos para operação industrial e para o automobilismo.</p>
</section>
<section class="section tl" data-hub="sobre" data-state="static" aria-labelledby="exp-title">
  <div class="wrap tl-head"><h2 id="exp-title">Experiência</h2>
    <div class="tl-nav"><button type="button" class="btn secondary" data-tl-prev aria-label="Etapa anterior">Anterior</button><button type="button" class="btn secondary" data-tl-next aria-label="Próxima etapa">Próxima</button></div></div>
  <div class="tl-progress" aria-hidden="true"><span></span></div>
  <div class="tl-scroller" tabindex="0" role="region" aria-label="Linha do tempo, da mais antiga para a mais recente"><ol class="tl-track">{exp}</ol></div>
</section>
<section class="wrap section">
  <div class="cols">
    <div>
      <h2>Formação</h2>
      <ul class="plain">{edu}</ul>
    </div>
    <aside class="aside">
      {PORTRAIT.format(cls="about-photo", sizes="300px", loading="eager")}
      <h2>Contato</h2>
      <ul><li><a href="{D.LINKEDIN_URL}">LinkedIn</a></li><li><a href="{D.REPO_URL}">GitHub</a></li><li>Vale do Paraíba, SP</li></ul>
    </aside>
  </div>
</section>
<section class="wrap section" id="metodo">
  <h2>Método e transparência</h2>
  <p>Cada projeto separa o que foi calculado do que seria preciso para uma validação real. Bases sintéticas são geradas com semente fixa e identificadas na página. Nenhum projeto usa dado confidencial de empresas onde trabalhei.</p>
  <p>Os números do catálogo industrial vêm de exercícios por técnica; os estudos de caso completos e os projetos de Fórmula 1 são os trabalhos mais profundos.</p>
</section>
<section class="wrap section" id="versoes">
  <h2>Versões e pacotes</h2>
  <p>O repositório publica pré-releases técnicas e duas imagens de demonstração no GitHub Container Registry: uma API de eventos industriais fictícios e uma API de inferência para os experimentos com MLflow. Não são produtos certificados.</p>
  <div class="actions"><a class="btn secondary" href="{D.REPO_URL}/releases">Releases</a><a class="btn secondary" href="https://github.com/xlDuarte?tab=packages&repo_name=portfolio">Pacotes</a></div>
</section>"""
    p.extra_head = ("<style>.timeline{list-style:none;margin:0;padding:0;border-top:1px solid var(--rule-strong)}"
                    ".timeline li{display:grid;grid-template-columns:8rem 1fr;gap:20px;padding:20px 0;border-bottom:1px solid var(--rule)}"
                    ".timeline .when{color:var(--slate);font-variant-numeric:tabular-nums;font-size:.9375rem}"
                    ".timeline h3{margin:0 0 2px}.timeline p{margin:0 0 6px}"
                    ".plain{padding-left:1.1em}.plain li{margin:.4em 0}"
                    ".about-photo{width:100%;max-width:300px;height:auto;aspect-ratio:4/5;object-fit:cover;border-radius:10px;margin-bottom:24px}"
                    "@media(max-width:560px){.timeline li{grid-template-columns:1fr;gap:4px}}</style>" + HUB_HEAD)
    write(p, main, body_extra=hub_script("sobre"))


def build_404() -> None:
    p = Page("/404.html", "Página não encontrada", "Esta página não existe ou mudou de endereço.")
    main = """
<section class="wrap page-head">
  <h1>Página não encontrada</h1>
  <p class="lede">O endereço pode ter mudado na reorganização do portfólio. Escolha um dos nichos para continuar.</p>
  <div class="actions"><a class="btn" href="/industrial/">Industrial</a><a class="btn" href="/automotivo/">Automotivo</a><a class="btn secondary" href="/">Início</a></div>
</section>"""
    p.file.write_text(render(p, main), encoding="utf-8")


# ---------------------------------------------------------------------------
# Project page normalisation (#001–#100, the five case studies, #103–#108)
# ---------------------------------------------------------------------------
NOTE_CLASSES = {"notice", "note", "alert", "warn", "warning", "disclaimer"}
BACK_LINK = re.compile(r"^\s*(←|Voltar)", re.I)
META_LINE = re.compile(r"(projeto\s*#?\d+|estudo de caso|·\s*#?\d{2,3}\s*$|/\s*\d{3}\s*/|^\s*#\d{3}\b)", re.I)


def extract_case(soup: BeautifulSoup) -> tuple[str, str | None, list, list[tuple[str, str]], str | None]:
    """Return (title, note_html, content_nodes, external_links, subtitle) from raw or normalised markup."""
    body = soup.find("article", class_="case-body")
    if body is not None:  # already normalised
        h1 = soup.select_one(".page-head h1").get_text(" ", strip=True)
        note = soup.select_one(".page-head .note")
        sub = soup.select_one(".page-head .lede")
        links = [(a.get_text(strip=True), a["href"]) for a in soup.select(".aside .ext a")]
        return h1, (note.decode_contents() if note else None), list(body.contents), links, (sub.get_text(" ", strip=True) if sub else None)

    root = soup.find("main") or soup.body
    for bad in root.find_all("style"):
        bad.decompose()
    h1 = root.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else (soup.title.get_text(strip=True) if soup.title else "Projeto")
    title = re.sub(r"^(Project|Projeto)\s*#?\d+\s*[—–-]\s*", "", title)
    title = re.sub(r"^#\d+\s*[—–-]\s*", "", title)
    note_html = None
    links: list[tuple[str, str]] = []
    # Collect external code links and drop navigation-only lines.
    for a in list(root.find_all("a")):
        href = a.get("href", "")
        text = a.get_text(" ", strip=True)
        if href.startswith("https://github.com/"):
            links.append((text.replace("↗", "").strip() or "Código", href))
            parent = a.parent
            a.decompose()
            if parent and parent.name == "p" and not parent.get_text(strip=True).strip("·| "):
                parent.decompose()
        elif BACK_LINK.match(text) or (href in ("/", "../../index.html", "../", "../../") and len(text) < 30):
            a.decompose()
    for tag in list(root.find_all(["nav", "header"])):
        tag.decompose()
    seen_h1 = False
    subtitle = None
    nodes = []
    for node in list(root.children):
        if isinstance(node, Comment):
            continue
        if isinstance(node, NavigableString):
            if node.strip().strip("·|"):
                nodes.append(node)
            continue
        if not isinstance(node, Tag):
            continue
        cls = set(node.get("class", []))
        if node.name == "h1":
            seen_h1 = True
            continue
        if note_html is None and cls & NOTE_CLASSES:
            note_html = node.decode_contents()
            continue
        text = node.get_text(" ", strip=True)
        if node.name == "p" and not text:
            continue
        if not seen_h1 and node.name == "p":
            continue  # kicker lines such as "ANÁLISE DE DADOS / PROJETO #001"
        if node.name == "p" and (cls & {"tag", "meta", "eyebrow"} or (len(text) < 60 and META_LINE.search(text))):
            continue
        if seen_h1 and subtitle is None and node.name == "p" and not cls and len(nodes) == 0 and len(text) < 260:
            subtitle = text
            continue
        nodes.append(node)
    return title, note_html, nodes, links, subtitle


def tidy_content(nodes: list, soup: BeautifulSoup) -> str:
    """Normalise metric grids, tables and numbers inside the case body."""
    wrapper = soup.new_tag("div")
    for n in nodes:
        wrapper.append(n.extract() if isinstance(n, Tag) else NavigableString(str(n)))
    # Stat grids → <dl class="metrics">
    for grid in wrapper.select(".grid, .cards, .kpis, .stats, div.metrics"):
        items = grid.select(".card, .stat, .kpi, .metric, article, div")
        pairs = []
        for it in items:
            label = it.find(["small", "span", "dt"])
            value = it.find(["strong", "b", "dd"])
            if label and value:
                pairs.append((label.get_text(" ", strip=True), value.get_text(" ", strip=True)))
        if pairs:
            dl = soup.new_tag("dl", attrs={"class": "metrics"})
            for k, v in pairs:
                d = soup.new_tag("div")
                dt = soup.new_tag("dt"); dt.string = humanize(k)
                dd = soup.new_tag("dd"); dd.string = fmt_num(v)
                d.append(dt); d.append(dd); dl.append(d)
            grid.replace_with(dl)
    for el in wrapper.select(".card strong, .stat strong"):
        el.string = fmt_num(el.get_text())
    for table in wrapper.find_all("table"):
        for cell in table.find_all(["td", "th"]):
            txt = cell.get_text()
            if cell.find(True) is None:
                if cell.name == "th":
                    cell.string = humanize(txt)
                else:
                    new = fmt_num(txt)
                    if new != txt:
                        cell.string = new
                        cell["class"] = "r num"
        if not (table.parent and "table-wrap" in (table.parent.get("class") or [])):
            w = soup.new_tag("div", attrs={"class": "table-wrap"})
            table.wrap(w)
    for pre in wrapper.find_all("pre"):
        pre["tabindex"] = "0"  # scrollable code must be keyboard-reachable (WCAG 2.1.1)
    for img in wrapper.find_all("img"):
        img["loading"] = "lazy"
        img.attrs.pop("style", None)
    for el in wrapper.find_all(True):
        el.attrs.pop("style", None)
        if el.name not in ("div", "dl", "table", "td", "th", "code", "pre", "tabindex", "span", "img", "a", "section", "figure", "canvas", "select", "input", "button", "label", "output", "details", "summary"):
            if el.get("class"):
                el.attrs.pop("class", None)
    return wrapper.decode_contents()


EVIDENCE_TEXT = {"source": "Origem dos dados", "leakage_control": "Controle de vazamento", "limitation": "Limitação",
                 "limitations": "Limitações", "threshold_selected_on_calibration": "Limiar escolhido na calibração"}


def _scalars(d: dict, prefix: str = "") -> list[tuple[str, object]]:
    out = []
    for k, v in d.items():
        if isinstance(v, bool) or k in ("project_id", "name", "title"):
            continue
        if isinstance(v, (int, float)):
            out.append((prefix + k, v))
        elif isinstance(v, dict):
            out.extend(_scalars(v, prefix=""))
    return out


def evidence_html(folder: Path) -> str:
    """Results block rendered from the project's own metrics.json (and input.png)."""
    mfile = folder / "metrics.json"
    if not mfile.is_file():
        return ""
    data = json.loads(mfile.read_text(encoding="utf-8"))
    nums = _scalars(data)[:9]
    dl = "".join(f"<div><dt>{esc(humanize(k))}</dt><dd>{esc(fmt_num(str(v)))}</dd></div>" for k, v in nums)
    parts = ['<section data-evidence><h2>Resultados calculados</h2>',
             '<p class="small muted">Gerado pelo próprio código do projeto e salvo em <code>metrics.json</code> ao lado desta página.</p>']
    if (folder / "input.png").is_file():
        parts.append('<figure class="scene"><img src="input.png" alt="Imagem sintética de entrada gerada pelo projeto" width="240" height="240">'
                     '<figcaption class="small muted">Imagem de entrada gerada pelo código (sintética).</figcaption></figure>')
    if dl:
        parts.append(f'<dl class="metrics">{dl}</dl>')
    cm = data.get("confusion_matrix")
    if isinstance(cm, list) and len(cm) == 2:
        parts.append('<h3>Matriz de confusão no teste</h3><div class="table-wrap"><table><tr><th></th><th class="r">Previsto 0</th><th class="r">Previsto 1</th></tr>'
                     f'<tr><th>Real 0</th><td class="r num">{cm[0][0]}</td><td class="r num">{cm[0][1]}</td></tr>'
                     f'<tr><th>Real 1</th><td class="r num">{cm[1][0]}</td><td class="r num">{cm[1][1]}</td></tr></table></div>')
    notes = [(EVIDENCE_TEXT[k], v) for k, v in data.items() if k in EVIDENCE_TEXT and isinstance(v, str)]
    res = data.get("result")
    if isinstance(res, dict):
        notes += [(humanize(k), v) for k, v in res.items() if isinstance(v, str)]
    if notes:
        parts.append("<ul>" + "".join(f"<li><strong>{esc(k)}:</strong> {esc(v)}</li>" for k, v in notes) + "</ul>")
    parts.append("</section>")
    return "".join(parts)


def case_page(file: Path, rec: dict | None, special: dict | None, kind: str) -> None:
    raw = file.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")
    title, note, nodes, links, subtitle = extract_case(soup)
    url = "/" + str(file.parent.relative_to(SITE)).replace("\\", "/") + "/"
    scripts = [s for s in soup.find_all("script") if s.get("src") or (s.string and s.string.strip())]
    # Module scripts used by #104/#106 must keep their relative paths.
    extra_links = [l for l in soup.find_all("link", rel="stylesheet") if "strategy.css" not in l.get("href", "")]
    nodes = [n for n in nodes if not (isinstance(n, Tag) and n.has_attr("data-evidence"))]
    content = tidy_content(nodes, soup)
    if kind == "industrial" and rec["domain"] in ("classification", "vision"):
        content = evidence_html(file.parent) + content

    if kind == "industrial":
        domain_name = D.DOMAINS[rec["domain"]][0]
        dom_href = f"/cases/{rec['domain']}/" if rec["domain"] in DOMAIN_PAGES else f"/industrial/#{rec['domain']}"
        crumbs = [("Início", "/"), ("Industrial", "/industrial/"), (domain_name, dom_href), (f"#{rec['id']:03d}", url)]
        kicker = f"Industrial · {domain_name} · Projeto #{rec['id']:03d}"
        desc = rec["desc"]
        subtitle = rec["desc"]
        code = f"{D.REPO_URL}/tree/main/{rec['code']}"
        sib = rec["siblings"]
        prev_ = sib[rec["pos"] - 1] if rec["pos"] > 0 else None
        next_ = sib[rec["pos"] + 1] if rec["pos"] + 1 < len(sib) else None
        facts = [f"Projeto #{rec['id']:03d}", domain_name,
                 "Mais completo do grupo" if rec["id"] in D.INDUSTRIAL_STRONG else "Exercício técnico",
                 "Dados sintéticos com semente fixa"]
        section, niche = "industrial", "industrial"
        title = rec["name"]
    elif kind == "study":
        crumbs = [("Início", "/"), ("Industrial", "/industrial/"), (special["title"], url)]
        kicker = "Industrial · Estudo de caso completo" + (f" · Projeto #{rec['id']:03d}" if rec else "")
        desc = special["desc"]
        code = f"{D.REPO_URL}/tree/main/{rec['code']}" if rec else f"{D.REPO_URL}/tree/main/case_studies"
        prev_ = next_ = None
        facts = (["Projeto #%03d" % rec["id"]] if rec else []) + ["Estudo de caso completo", "Dados sintéticos com semente fixa", ", ".join(special["tags"])]
        section, niche = "industrial", "industrial"
        title = special["title"]
    else:  # shared lab project
        crumbs = [("Início", "/"), ("Laboratório", "/laboratorio/"), (f"#{special['id']}", url)]
        kicker = f"Laboratório comum · Projeto #{special['id']}"
        desc = special["desc"]
        code = f"{D.REPO_URL}/tree/main/{special['code']}"
        prev_ = next_ = None
        facts = [f"Projeto #{special['id']}", f"Aplicação: {special['both']}"]
        section, niche = "laboratorio", "laboratorio"
        title = special["title"]
        if not subtitle:
            subtitle = special["desc"]

    ext = [(t, h) for t, h in links if h != code]
    ext_html = "".join(f'<li><a href="{esc(h)}">{esc(t[:60])}</a></li>' for t, h in ext[:4])
    pager = ""
    if prev_ or next_:
        pager = '<nav class="pager" aria-label="Projetos do mesmo grupo">'
        if prev_:
            pager += f'<a href="{prev_["page"]}"><span class="small muted">Anterior</span>#{prev_["id"]:03d} {esc(prev_["name"])}</a>'
        else:
            pager += "<span></span>"
        if next_:
            pager += f'<a class="next" href="{next_["page"]}"><span class="small muted">Próximo</span>#{next_["id"]:03d} {esc(next_["name"])}</a>'
        pager += "</nav>"
    note_block = f'<div class="note">{note}</div>' if note else ""
    facts_html = "".join(f"<li>{esc(f)}</li>" for f in facts)
    main = f"""
<section class="wrap page-head">
  <p class="kicker">{esc(kicker)}</p>
  <h1>{esc(title)}</h1>
  {f'<p class="lede">{esc(subtitle)}</p>' if subtitle else ''}
  {note_block}
</section>
<div class="wrap cols">
  <article class="case-body prose">{content}</article>
  <aside class="aside">
    <h2>Ficha</h2>
    <ul>{facts_html}</ul>
    <h2>Código</h2>
    <ul class="ext"><li><a href="{esc(code)}">Pasta do projeto no GitHub</a></li>{ext_html}</ul>
  </aside>
</div>
<div class="wrap">{pager}</div>"""
    keep_links = "".join(str(l) for l in extra_links if l.get("href", "").startswith(("../", "./")) and "ds.css" not in l.get("href", ""))
    p = Page(url, f"#{rec['id']:03d} {title}" if rec and kind == "industrial" else title, desc, section=section, niche=niche, crumbs=crumbs,
             extra_head=PAGER_CSS + keep_links)
    body_extra = "".join(str(s) for s in scripts if "plotly" not in (s.get("src") or ""))
    write(p, main, body_extra)


PAGER_CSS = ("<style>.pager{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:48px;border-top:1px solid var(--rule);padding-top:20px}"
             ".pager a{display:flex;flex-direction:column;gap:2px;text-decoration:none;font-weight:600}"
             ".pager a.next{text-align:right}.case-body img{border:1px solid var(--rule);border-radius:6px;background:#fff}"
             ".case-body>h2:first-child,.case-body>section:first-child>h2{margin-top:0}.page-head .note{margin-top:20px}"
             ".scene{margin:0 0 20px}.scene img{width:240px;image-rendering:pixelated}</style>")


# ---------------------------------------------------------------------------
# Plotly EDA exports
# ---------------------------------------------------------------------------
PLOTLY_THEME = """<script>
(function(){
  var el=document.querySelector('.plotly-graph-div'); if(!el||!window.Plotly) return;
  var colors=['#1d4e9e','#b8122b','#3b4652','#6d8fc7','#d9707f','#8b939c'];
  Plotly.relayout(el,{paper_bgcolor:'#ffffff',plot_bgcolor:'#ffffff',colorway:colors,
    font:{family:'Archivo, system-ui, sans-serif',color:'#1c2128',size:13},
    'xaxis.gridcolor':'#e3e6ea','yaxis.gridcolor':'#e3e6ea','xaxis.linecolor':'#c9ced5','yaxis.linecolor':'#c9ced5',
    margin:{t:24,r:16,b:48,l:56},title:{text:''}});
  var data=el.data||[]; data.forEach(function(t,i){Plotly.restyle(el,{'line.color':colors[i%colors.length],'marker.color':colors[i%colors.length]},[i]);});
  window.addEventListener('resize',function(){Plotly.Plots.resize(el)});
})();
</script>"""


def eda_page(file: Path, rec: dict) -> None:
    soup = BeautifulSoup(file.read_text(encoding="utf-8"), "html.parser")
    div = soup.select_one(".plotly-graph-div")
    if div is None:
        return
    scripts = soup.find_all("script")
    fig_script = next(s for s in scripts if s.string and "Plotly.newPlot" in s.string)
    plotly_src = next((s["src"] for s in scripts if s.get("src") and "plotly" in s["src"]), "https://cdn.plot.ly/plotly-3.3.1.min.js")
    div.attrs["style"] = "height:520px;width:100%;"
    url = "/" + str(file.relative_to(SITE)).replace("\\", "/")
    page_dir = "/" + str(file.parent.relative_to(SITE)) + "/"
    domain = D.DOMAINS[rec["domain"]][0]
    p = Page(url, f"Gráfico interativo · #{rec['id']:03d} {rec['name']}",
             f"Gráfico interativo do projeto #{rec['id']:03d}: {rec['desc']}", section="industrial", niche="industrial",
             crumbs=[("Início", "/"), ("Industrial", "/industrial/"), (domain, f"/cases/{rec['domain']}/"),
                     (f"#{rec['id']:03d}", page_dir), ("Gráfico interativo", url)])
    main = f"""
<section class="wrap page-head">
  <p class="kicker">Industrial · {esc(domain)} · Projeto #{rec['id']:03d}</p>
  <h1>{esc(rec['name'])}</h1>
  <p class="lede">{esc(rec['desc'])}</p>
  <div class="note"><p>Gráfico gerado com Plotly a partir da base sintética do projeto. Passe o cursor para ver os valores; clique na legenda para isolar séries.</p></div>
</section>
<section class="wrap"><div class="chart-frame">{div}</div>
<p class="actions"><a class="btn secondary" href="{page_dir}">Voltar ao projeto</a></p></section>"""
    p.extra_head = "<style>.chart-frame{border:1px solid var(--rule);border-radius:10px;padding:12px;overflow:hidden}</style>"
    body_extra = f'<script src="{esc(plotly_src)}"></script>\n{fig_script}\n{PLOTLY_THEME}'
    write(p, main, body_extra)


# ---------------------------------------------------------------------------
# Interactive labs: inject the shell, keep the app markup.
# ---------------------------------------------------------------------------
APPS = {  # file → (page title, category hub)
    "motorsport/insights/index.html": ("Análise de corrida", "/automotivo/f1/"),
    "motorsport/active-aero/index.html": ("Aerodinâmica ativa", "/automotivo/f1/"),
    "motorsport/energy-recovery/index.html": ("Recuperação de energia", "/automotivo/f1/"),
    "motorsport/lap-simulator/index.html": ("Simulador de tempo de volta", "/automotivo/f1/"),
    "motorsport/f1-pip/index.html": ("Modelos e probabilidades de corrida", "/automotivo/f1/"),
    "cases/motorsport/101/index.html": ("Estratégia de pneus", "/automotivo/f1/"),
    "cases/motorsport/102/index.html": ("Telemetria e filtro de Kalman", "/automotivo/f1/"),
    "cases/motorsport/107/index.html": ("Arquivo da direção de prova", "/automotivo/f1/"),
    "cases/motorsport/109/index.html": ("Replay de corrida", "/automotivo/f1/"),
    "cases/motorsport/110/index.html": ("Laboratório de engenharia Porsche Cup", "/automotivo/porsche/"),
}
GOOGLE_FONTS = re.compile(r'<link[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>\s*', re.I)
HEADER_BLOCK = re.compile(r"<!-- ds:header -->.*?<!-- /ds:header -->", re.S)
FOOTER_BLOCK = re.compile(r"<!-- ds:footer -->.*?<!-- /ds:footer -->", re.S)


def _head(kicker: str, title: str, lede: str, extra: str = "") -> str:
    return (f'<!-- ds:hero --><div class="page-head app-head"><p class="kicker">{esc(kicker)}</p>'
            f'<h1>{esc(title)}</h1><p class="lede">{esc(lede)}</p>{extra}</div><!-- /ds:hero -->')


LAB_SWITCH = ('<nav class="subnav" aria-label="Laboratórios de física">'
              '<a href="/motorsport/active-aero/"{a}>Aerodinâmica ativa</a>'
              '<a href="/motorsport/energy-recovery/"{e}>Recuperação de energia</a>'
              '<a href="/motorsport/lap-simulator/"{l}>Tempo de volta</a></nav>')


def _lab_head(which: str):
    cur = {k: (' aria-current="page"' if k == which else "") for k in "ael"}
    def build(m):
        return _head("Fórmula 1 · Laboratório de física", m.group(1).strip(),
                     re.sub(r"<[^>]+>", "", m.group(2)).strip() + " " + re.sub(r"<[^>]+>", "", m.group(3)).strip(),
                     LAB_SWITCH.format(**cur))
    return (r'<p class="eyebrow">[^<]*</p><h1>(.*?)</h1><h2>(.*?)</h2><p class="intro">(.*?)</p>', build)


PIP_STATS = ('<dl class="metrics app-stats"><div><dt>Modelos avaliados</dt><dd>8</dd></div>'
             '<div><dt>Pilotos reais</dt><dd>20</dd></div><div><dt>Simulações por cenário</dt><dd>até 10 mil</dd></div></dl>')

APP_HEROES = {
    "motorsport/active-aero/index.html": _lab_head("a"),
    "motorsport/energy-recovery/index.html": _lab_head("e"),
    "motorsport/lap-simulator/index.html": _lab_head("l"),
    "motorsport/insights/index.html": (r'<div class="hero">.*?</div>', lambda m: _head(
        "Fórmula 1", "Análise de corrida em cinco ferramentas",
        "Comparação de curvas, probabilidade de pódio, cenários de campeonato, ritmo de corrida e trajetória, com dados rastreáveis do OpenF1, FastF1 e Jolpica.")),
    "motorsport/f1-pip/index.html": (r'<section class="hero">.*?</section>\s*<section class="paddock".*?</section>', lambda m: _head(
        "Fórmula 1 · Projeto #111", "Modelos e probabilidades de corrida",
        "Oito modelos ajustados em resultados reais de 2022 a 2024 e simulação Monte Carlo. Veja a distribuição dos resultados, não só o mais provável. Estudo retrospectivo do GP do Bahrein 2024.",
        PIP_STATS)),
    "cases/motorsport/101/index.html": (r'<div class="breadcrumb">.*?</div>\s*<section class="intro">.*?</section>', lambda m: _head(
        "Fórmula 1 · Projeto #101", "Estratégia de pneus e janela de pit-stop",
        "Compare planos de parada com o ritmo estimado a partir de voltas observadas no GP do Bahrein 2024. Pista seca, dois compostos por plano, sem tráfego.")),
    "cases/motorsport/102/index.html": (r'<div class="breadcrumb">.*?</div>\s*<section class="intro">.*?</section>', lambda m: _head(
        "Fórmula 1 · Projeto #102", "Telemetria e filtro de Kalman",
        "Observe o sinal, estime o estado e inspecione os resíduos. Velocidade, RPM, acelerador e freio medidos via OpenF1 no GP do Bahrein 2024.")),
    "cases/motorsport/109/index.html": (r'<div class="breadcrumb">.*?</div>\s*<section class="intro">.*?</section>', lambda m: _head(
        "Fórmula 1 · Projeto #109", "Replay de corrida",
        "Escolha um piloto, explore a pista e conecte cada movimento aos dados. GP do Bahrein 2024, três pilotos, recorte de quatro minutos (OpenF1).")),
    "cases/motorsport/107/index.html": (r'<a href="[^"]*">← Projetos</a>\s*<p class="eyebrow">[^<]*</p>\s*<h1>[^<]*</h1>', lambda m: _head(
        "Fórmula 1 · Projeto #107", "Arquivo da direção de prova",
        "Mensagens oficiais da direção de prova no GP do Bahrein 2024 (OpenF1, sessão 9472). Pesquise no texto original, em inglês.")),
    "cases/motorsport/110/index.html": (r'<section class="hero">.*?</section>\s*<nav class="porsche-sections".*?</nav>', lambda m: _head(
        "Porsche Cup · Projeto #110", "Laboratório de engenharia Porsche Cup",
        "Explore o equilíbrio entre carga, contato e comportamento do carro. Importe uma aquisição autorizada para analisar os canais; nada é preenchido com valores inventados.",
        '<div class="actions"><a class="btn" href="#demo">Aquisição e quatro rodas</a><a class="btn secondary" href="#seminar">Análises de engenharia</a></div>')),
}

ACRONYMS = {"F1": "F1", "OPENF1": "OpenF1", "FASTF1": "FastF1", "JOLPICA": "Jolpica", "EKF": "EKF", "RPM": "RPM",
            "DRS": "DRS", "JSON": "JSON", "CSV": "CSV", "API": "API", "GT3": "GT3", "SOC": "SoC", "CFD": "CFD",
            "FIA": "FIA", "UTC": "UTC", "CAD": "CAD", "RMS": "RMS", "MAE": "MAE", "ERS": "ERS", "2D": "2D", "3D": "3D",
            "A/B": "A/B", "BAHRAIN": "Bahrain", "BAHREIN": "Bahrein", "SAKHIR": "Sakhir", "PORSCHE": "Porsche",
            "CUP": "Cup", "FASTF1/OPENF1": "FastF1/OpenF1", "VER": "VER", "PER": "PER", "SAI": "SAI", "L1": "L1",
            "MGU-K": "MGU-K", "PIP": "PIP", "F1-PIP": "F1-PIP", "KM/H": "km/h", "S": "s", "M": "M", "H": "H", "GP": "GP"}
_CAPS_WORD = re.compile(r"[A-ZÀ-Ý0-9][A-ZÀ-Ý0-9/\-]*")


def sentence_case(text: str) -> str:
    """Turn shouted labels ("MELHOR PLANO AVALIADO") into sentence case, keeping acronyms."""
    letters = [c for c in text if c.isalpha()]
    if len(letters) < 4 or any(c.islower() for c in letters):
        return text
    def word(m):
        w = m.group(0)
        return ACRONYMS.get(w, w.lower())
    out = _CAPS_WORD.sub(word, text)
    for i, c in enumerate(out):
        if c.isalpha():
            return out[:i] + c.upper() + out[i + 1:]
    return out


def polish_app(s: str, rel: str) -> str:
    hero = APP_HEROES.get(rel)
    if hero and "<!-- ds:hero -->" not in s:
        pattern, build = hero
        s, n = re.subn(pattern, build, s, count=1, flags=re.S)
        if not n:
            print(f"warning: hero pattern not found in {rel}", file=sys.stderr)
    s = s.replace('href="../../../f1-models/"', 'href="/motorsport/f1-pip/"')
    if rel == "motorsport/insights/index.html" and 'id="export-report"' not in s:
        s = s.replace("</main>", '<div class="report-actions"><button id="export-report" class="secondary">Exportar resultados em JSON</button>'
                      '<p class="small muted">Dados observados e resultados calculados são identificados separadamente. '
                      '<a href="./README.md">Metodologia e fontes</a></p></div></main>', 1)
    # Sentence-case shouted text nodes in the app body (scripts, styles and code untouched).
    start = s.find("<!-- /ds:header -->")
    end = s.find("<!-- ds:footer -->")
    if start < 0 or end < 0:
        return s
    body = s[start:end]
    keep = []
    def mask(m):
        keep.append(m.group(0))
        return f"\x00{len(keep) - 1}\x00"
    body = re.sub(r"<(script|style|code|pre)\b.*?</\1>", mask, body, flags=re.S)
    body = re.sub(r">([^<>]+)<", lambda m: ">" + sentence_case(m.group(1)) + "<", body)
    body = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], body)
    return s[:start] + body + s[end:]


def inject_app(rel: str, label: str, parent: str) -> None:
    file = SITE / rel
    s = file.read_text(encoding="utf-8")
    soup_head = BeautifulSoup(s, "html.parser")
    title = label
    desc_tag = soup_head.find("meta", attrs={"name": "description"})
    desc = desc_tag["content"] if desc_tag else ""
    if len(desc) < 40:
        known = {x["path"]: x["desc"] for x in D.F1_PROJECTS + D.F1_TOOLS + [D.PORSCHE_PROJECT]}
        desc = known.get("/" + rel.replace("index.html", ""), label)
    url = "/" + rel.replace("index.html", "")
    cat = "Porsche Cup" if "porsche" in parent else "Fórmula 1"
    p = Page(url, title, desc, section="automotivo", niche="automotivo",
             crumbs=[("Início", "/"), ("Automotivo", "/automotivo/"), (cat, parent), (title, url)])
    first_run = "<!-- ds:header -->" not in s
    s = GOOGLE_FONTS.sub("", s)
    if first_run:
        # Remove the app's own top header/skip link and its closing footer: the shell replaces them.
        body_start = s.index("<body")
        head_part, body_part = s[:body_start], s[body_start:]
        body_part = re.sub(r'<a class="skip"[^>]*>.*?</a>', "", body_part, count=1, flags=re.S)
        body_part = re.sub(r"(<body[^>]*>\s*)<header\b.*?</header>", r"\1", body_part, count=1, flags=re.S)
        body_part = re.sub(r"<footer\b(?![^>]*site-footer).*?</footer>(?=(?:(?!<footer).)*$)", "", body_part, count=1, flags=re.S)
        s = head_part + body_part
    # Head: replace everything up to the app's own stylesheets with the shell head.
    m = re.search(r"<head>(.*?)</head>", s, re.S)
    head_inner = m.group(1)
    own = [x for x in re.findall(r"<link[^>]+stylesheet[^>]*>|<style\b.*?</style>|<script\b[^>]*>.*?</script>", head_inner, re.S)
           if "ds.css" not in x and "apps.css" not in x and "data-ds" not in x]
    new_head = head_html(p) + "".join(own) + '<link rel="stylesheet" href="/assets/apps.css">\n'
    s = s[:m.start(1)] + "\n" + new_head + s[m.end(1):]
    # Body: niche attribute, header and footer.
    s = re.sub(r"<body([^>]*)>", lambda b: "<body" + re.sub(r'\sdata-niche="[^"]*"', "", b.group(1)) + ' data-niche="automotivo">', s, count=1)
    hdr = header_html(p)
    if HEADER_BLOCK.search(s):
        s = HEADER_BLOCK.sub(lambda _m: hdr, s, count=1)
    else:
        s = re.sub(r"(<body[^>]*>)", lambda b: b.group(1) + hdr, s, count=1)
    if FOOTER_BLOCK.search(s):
        s = FOOTER_BLOCK.sub(lambda _m: footer_html(), s, count=1)
    else:
        s = s.replace("</body>", footer_html() + "</body>", 1)
    # Landmark id for the skip link.
    if 'id="conteudo"' not in s:
        s = re.sub(r"<main\b([^>]*)>", lambda mm: "<main" + re.sub(r'\sid="[^"]*"', "", mm.group(1)) + ' id="conteudo">', s, count=1)
    s = polish_app(s, rel)
    file.write_text(s, encoding="utf-8")
    PAGES.append(p)


# ---------------------------------------------------------------------------
# Site files
# ---------------------------------------------------------------------------
def write_sitemap() -> None:
    urls = sorted({p.path for p in PAGES if not p.path.endswith("404.html")})
    body = "".join(f"<url><loc>{esc(D.SITE_URL + u)}</loc></url>" for u in urls)
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + body + "</urlset>\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {D.SITE_URL}/sitemap.xml\n", encoding="utf-8")


def write_vercel() -> None:
    redirects = []
    for src, dst in D.REDIRECTS.items():
        # trailingSlash:true turns "/industry" into "/industry/" before matching, and
        # cleanUrls turns "/x.html" into "/x/": emit every spelling Vercel may match.
        base = src.rstrip("/")
        if base.endswith(".html"):
            base = base[:-5]
        for s in dict.fromkeys([base, base + "/", src]):
            if all(r["source"] != s for r in redirects):
                redirects.append({"source": s, "destination": dst, "permanent": True})
    csp = ("default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.plot.ly https://cdn.jsdelivr.net; "
           "style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; "
           "connect-src 'self' https://api.openf1.org https://api.jolpi.ca; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
    cfg = {
        "version": 2,
        "buildCommand": None,
        "outputDirectory": "site",
        "cleanUrls": True,
        "trailingSlash": True,
        "redirects": redirects,
        "headers": [
            {"source": "/(.*)", "headers": [
                {"key": "Content-Security-Policy", "value": csp},
                {"key": "X-Content-Type-Options", "value": "nosniff"},
                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"},
                {"key": "X-Frame-Options", "value": "DENY"},
            ]},
            {"source": "/assets/fonts/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
        ],
    }
    (ROOT / "vercel.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


RETIRED = [
    "prototipos/heroi/index.html", "assets/gabriel-racing-640.webp",
    "industry/arquivo.html", "industry/index.html", "industry/industrial.mjs", "industry/catalog.mjs",
    "industry/industrial.css", "industry/report.css", "motorsport/index.html", "motorsport/effects.js", "motorsport/effects.css",
    "motorsport/asset-scene.js", "motorsport/racing/index.html", "motorsport/racing/racing.css",
    "f1/index.html", "f1-models/index.html", "about/index.html", "docs/index.html", "releases/index.html",
    "packages/index.html", "cases/index.html",
    "motorsport/assets/red-bull.svg", "motorsport/assets/helmet-racing-lab.svg", "motorsport/assets/concept-helmet.webp",
    "motorsport/porsche/assets/porsche-motorsport.svg", "motorsport/porsche/assets/gt3-cup.webp",
    "motorsport/models/assets/f1.svg", "assets/gabriel-portrait.webp", "motorsport/models/teams.mjs",
    "motorsport/models/assets/sources.json",
]


def retire() -> None:
    for n in range(41, 51):  # unlinked duplicates of the NLP pages (#041–#050)
        dup = SITE / "cases" / "nlp" / str(n) / "index.html"
        if dup.is_file():
            dup.unlink()
            dup.parent.rmdir()
    for rel in RETIRED:
        f = SITE / rel
        if f.is_file():
            f.unlink()
    for f in (SITE / "motorsport" / "models" / "assets").glob("*.webp"):
        f.unlink()
    for d in sorted({(SITE / r).parent for r in RETIRED}, key=lambda x: len(str(x)), reverse=True):
        if d.is_dir() and d != SITE and not any(d.iterdir()):
            d.rmdir()


REPO_LINK = re.compile(r"https://github\.com/xlDuarte/portfolio/(blob|tree)/([^/\"'#?]+)/([^\"'#?<\s]*)")


RETIRED_HREFS = [(re.compile(r'href="(?:\.\./)*f1-models/"'), 'href="/motorsport/f1-pip/"'),
                 (re.compile(r'href="(?:\.\./)*motorsport/racing/"'), 'href="/automotivo/f1/"'),
                 (re.compile(r'href="(?:\.\./)+motorsport/"'), 'href="/automotivo/"'),
                 (re.compile(r'href="(?:\.\./)*industry/[^"]*"'), 'href="/industrial/"')]


def fix_internal_links() -> None:
    """Rewrite links that still point at retired hubs to their new home."""
    for f in SITE.rglob("*.html"):
        s = f.read_text(encoding="utf-8")
        new = s
        for rx, repl in RETIRED_HREFS:
            new = rx.sub(repl, new)
        if new != s:
            f.write_text(new, encoding="utf-8")


def fix_repo_links() -> list[str]:
    """Point every repository link at main and report links whose path does not exist."""
    missing = []
    for f in SITE.rglob("*.html"):
        s = f.read_text(encoding="utf-8")
        def repl(m):
            kind, _branch, path = m.groups()
            clean = path.rstrip("/")
            if clean and not (ROOT / clean).exists():
                padded = re.sub(r"(^|/)(\d{1,2})(\.\w+)$", lambda d: f"{d.group(1)}{int(d.group(2)):03d}{d.group(3)}", clean)
                if (ROOT / padded).exists():
                    path, clean = padded, padded
            if clean and not (ROOT / clean).exists():
                missing.append(f"{f.relative_to(SITE)} -> {clean}")
            return f"https://github.com/xlDuarte/portfolio/{kind}/main/{path}"
        new = REPO_LINK.sub(repl, s)
        if new != s:
            f.write_text(new, encoding="utf-8")
    return missing


# ---------------------------------------------------------------------------
def main() -> None:
    groups = load_catalog()
    idx = project_index(groups)
    build_home(groups)
    build_industrial(groups)
    build_domain_pages(groups)
    build_motorsport_index()
    build_automotivo()
    build_f1()
    build_porsche()
    build_lab()
    build_sobre()
    build_404()
    study_pages = {f"/cases/{st['slug']}/" for st in D.INDUSTRIAL_FEATURED}
    for pr in idx.values():
        f = SITE / pr["page"].lstrip("/") / "index.html"
        if f.is_file() and pr["page"] not in study_pages:
            case_page(f, pr, None, "industrial")
        inter = f.parent / "interactive.html"
        if inter.is_file():
            eda_page(inter, pr)
    for st in D.INDUSTRIAL_FEATURED:
        f = SITE / "cases" / st["slug"] / "index.html"
        if f.is_file():
            case_page(f, idx.get(f"/cases/{st['slug']}/"), st, "study")
    for sp in D.SHARED_PROJECTS:
        f = SITE / sp["path"].lstrip("/") / "index.html"
        if f.is_file():
            case_page(f, None, sp, "shared")
    for rel, (label, parent) in APPS.items():
        if (SITE / rel).is_file():
            inject_app(rel, label, parent)
    retire()
    fix_internal_links()
    for bad in fix_repo_links():
        print("missing repo path:", bad, file=sys.stderr)
    write_sitemap()
    write_vercel()
    print(f"built {len(PAGES)} pages", file=sys.stderr)


if __name__ == "__main__":
    main()
