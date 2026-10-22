"""Ten actual, independently constrained industrial recommenders on fictional catalogs.

No SAP/Ariba integration, external route measurements, procurement execution, factual
market news, human workforce profiling, or observed business benefits are claimed.
"""
from __future__ import annotations
import argparse
import json
import math
import re
import unicodedata
from collections import Counter
from heapq import heappush, heappop
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

ROOT = Path(__file__).resolve().parent
SPECS = {int(k): v for k, v in json.loads((ROOT / "specs.json").read_text(encoding="utf-8")).items()}
FIXTURES = json.loads((ROOT / "fixtures.json").read_text(encoding="utf-8"))
VALID_MODES = set(s["mode"] for s in SPECS.values())

def words(s: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", s.lower())
    plain = "".join(c for c in normalized if not unicodedata.combining(c))
    return set(re.findall(r"[a-z0-9]+", plain))

def valid_query(query: str) -> str:
    if not isinstance(query, str) or not query.strip() or len(query) > 3000:
        raise ValueError("Query must be nonempty text at most 3000 characters")
    return query.strip()

def _positive_int(value, name: str, maximum: int = 1000) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= maximum:
        raise ValueError(f"{name} must be an integer between 1 and {maximum}")
    return value

def _rank_text(records: list[dict], query: str, top_k: int, *, status_key: str | None = None,
               text_key: str = "text", boost: dict[str, float] | None = None) -> list[dict]:
    if status_key:
        records = [r for r in records if r[status_key] in ("approved", "effective", "published")]
    if not records:
        return []
    df = pd.DataFrame(records)
    corpus = (df["title"].fillna("") + " " + df[text_key].fillna("")).tolist()
    vector = TfidfVectorizer(strip_accents="unicode", lowercase=True,
                             ngram_range=(1, 2), sublinear_tf=True)
    mat = vector.fit_transform(corpus + [query])
    similarities = cosine_similarity(mat[:-1], mat[-1]).reshape(-1)
    query_terms = words(query)
    results = []
    for i, item in enumerate(records):
        extra = (boost or {}).get(item["id"], 0.)
        intersection = sorted(query_terms & words(item["title"] + " " + item[text_key]))
        # Cosine measures user-to-item text relevance; supplemental boost is explicit.
        score = float(similarities[i]) + float(extra)
        results.append({
            "id": item["id"], "title": item["title"], "score": round(score, 6),
            "cosine_similarity": round(float(similarities[i]), 6),
            "matched_terms": intersection,
            "why": "relevância TF-IDF e regras de elegibilidade",
        })
    results.sort(key=lambda r: (-r["score"], r["id"]))
    return results[:top_k]

def _catalog(project: int, query: str, top_k: int, filters: dict) -> list[dict]:
    if project == 51:
        rows = [r for r in FIXTURES["media"]
                if r["status"] == "approved" and
                (filters.get("asset") is None or r["asset"] == filters["asset"]) and
                (filters.get("language") is None or r["language"] == filters["language"])]
        return _rank_text(rows, query, top_k)
    if project == 53:
        rows = [r for r in FIXTURES["docs"]
                if r["status"] == "effective" and r["authorized"] and
                (filters.get("domain") is None or r["domain"] == filters["domain"])]
        return _rank_text(rows, query, top_k)
    raise ValueError("Not a basic content recommender")

SIGNATURES = {
    "healthy": (22., 0.6, "healthy bearing reference"),
    "bearing_fault": (125., 2.2, "bearing fault - elevated high-frequency vibration"),
    "misalignment": (46., 1.8, "coupling/shaft misalignment"),
    "looseness": (72., 2.0, "mechanical looseness"),
    "gear_mesh": (205., 2.4, "gear tooth wear signature"),
}
def _wave(kind: str, seed: int = 2026) -> np.ndarray:
    if kind not in SIGNATURES:
        raise ValueError("Unknown reference acoustic class")
    hz, amp, _ = SIGNATURES[kind]
    sample_rate = 1024
    t = np.arange(2048) / sample_rate
    rng = np.random.default_rng(seed)
    return (amp * np.sin(2 * np.pi * hz * t)
            + .23 * np.sin(2 * np.pi * 2 * hz * t) + rng.normal(0, .13, len(t)))

def _features(wave: np.ndarray) -> np.ndarray:
    sample_rate = 1024
    spectrum = np.abs(np.fft.rfft(wave)) ** 2
    freqs = np.fft.rfftfreq(len(wave), 1 / sample_rate)
    dominant = float(freqs[np.argmax(spectrum[1:]) + 1])
    total = max(float(spectrum.sum()), 1e-12)
    return np.array([dominant / 250, float(np.sqrt(np.mean(wave**2))) / 3,
                     spectrum[(freqs >= 20) & (freqs < 90)].sum() / total,
                     spectrum[(freqs >= 90) & (freqs < 180)].sum() / total,
                     spectrum[(freqs >= 180) & (freqs < 320)].sum() / total])

def _acoustic(query: str, top_k: int, filters: dict) -> list[dict]:
    # The deterministic reference signals are a diagnostic simulation, NOT actual plant audio.
    if query not in SIGNATURES:
        raise ValueError("Acoustic query must be one of: " + ", ".join(SIGNATURES))
    references = list(SIGNATURES)
    training = np.stack([_features(_wave(kind)) for kind in references])
    # Query waveform is independently sampled noise, but same fictional fault process.
    observed = _features(_wave(query, seed=3031))
    neighbors = NearestNeighbors(n_neighbors=min(top_k, len(references)),
                                 metric="euclidean").fit(training)
    distances, indices = neighbors.kneighbors([observed])
    return [{"id": references[i], "title": SIGNATURES[references[i]][2],
             "distance": round(float(dist), 6),
             "why": "NearestNeighbors sobre FFT dominante, RMS e energia por banda",
             "fft_features": _features(_wave(references[i])).round(5).tolist()}
            for dist, i in zip(distances[0], indices[0])]

def _parts(query: str, top_k: int, filters: dict) -> list[dict]:
    asset = filters.get("asset", "pump")
    min_stock = int(filters.get("min_stock", 1))
    if min_stock < 0 or min_stock > 10000:
        raise ValueError("Invalid stock threshold")
    rows = [p for p in FIXTURES["parts"] if p["approved"] and
            p["asset"] == asset and p["stock"] >= min_stock]
    boost = {p["id"]: min(p["stock"], 20) / 1000 for p in rows}
    return _rank_text(rows, query, top_k, boost=boost)

def _learning(query: str, top_k: int, filters: dict) -> list[dict]:
    have = set(filters.get("known_skills", []))
    if not all(isinstance(x, str) for x in have):
        raise ValueError("Known skills must be strings")
    budget = _positive_int(filters.get("max_hours", 100), "max_hours", 500)
    terms = words(query)
    courses = FIXTURES["courses"]
    selected = []
    for _ in range(top_k):
        eligible = [c for c in courses if c["skill"] not in have and
                    c["id"] not in {x["id"] for x in selected} and
                    set(c["prerequisites"]) <= have and c["hours"] <= budget]
        if not eligible:
            break
        # Recommend learning goals and reachable prerequisites in order.
        def priority(c):
            desired = float(len(words(c["skill"] + " " + c["text"]) & terms))
            unlocks = sum(1 for t in courses if c["skill"] in t["prerequisites"] and
                          len(words(t["skill"] + " " + t["text"]) & terms) > 0)
            return (desired + .25 * unlocks, -c["hours"], c["id"])
        chosen = max(eligible, key=priority)
        selected.append({"id": chosen["id"], "title": chosen["title"],
                         "skill": chosen["skill"], "hours": chosen["hours"],
                         "prerequisites_met": True, "why": "lacuna de habilidade e pré-requisitos"})
        have.add(chosen["skill"])
        budget -= chosen["hours"]
    return selected

def _skill_matching(query: str, top_k: int, filters: dict) -> list[dict]:
    required = set(filters.get("required_skills", [])) or words(query)
    min_hours = _positive_int(filters.get("min_hours", 12), "min_hours", 500)
    candidates = []
    for person in FIXTURES["engineers"]:
        if not person["cleared"] or person["free_hours"] < min_hours:
            continue
        person_skills = set()
        for s in person["skills"]:
            person_skills |= words(s)
        coverage = len(required & person_skills) / max(1, len(required))
        candidates.append({"id": person["id"], "title": "Synthetic engineering profile",
                           "coverage": round(coverage, 5), "matched_skills": sorted(required & person_skills),
                           "available_hours": person["free_hours"],
                           "why": "simulated skills coverage; human staffing review required"})
    candidates.sort(key=lambda x: (-x["coverage"], -x["available_hours"], x["id"]))
    return candidates[:top_k]

def _feed(query: str, top_k: int, filters: dict) -> list[dict]:
    max_age = _positive_int(filters.get("max_age_days", 30), "max_age_days", 365)
    stories = [s for s in FIXTURES["stories"] if s["status"] == "published" and
               s["days_ago"] <= max_age]
    if not stories:
        return []
    relevance = {s["id"]: (max_age - s["days_ago"]) / (max_age * 10) for s in stories}
    result = _rank_text(stories, query, len(stories), boost=relevance)
    by_id = {s["id"]: s for s in stories}
    for row in result:
        row["age_days"] = by_id[row["id"]]["days_ago"]
        row["source"] = "SYNTHETIC news fixture, not a verified published article"
    return result[:top_k]

def _supplier(query: str, top_k: int, filters: dict) -> list[dict]:
    category = filters.get("category", query.lower().strip())
    quantity = _positive_int(filters.get("quantity", 100), "quantity", 100000)
    max_lead = _positive_int(filters.get("max_lead_days", 10), "max_lead_days", 365)
    min_otif = float(filters.get("min_otif", .90))
    if not 0 <= min_otif <= 1 or not math.isfinite(min_otif):
        raise ValueError("OTIF threshold must be a finite proportion")
    eligible = [r for r in FIXTURES["suppliers"] if r["category"] == category and
                r["approved"] and r["capacity"] >= quantity and
                r["lead_days"] <= max_lead and r["otif"] >= min_otif and
                "ISO9001" in r["certifications"]]
    if not eligible:
        return []
    max_price = max(r["unit_price_brl"] for r in eligible)
    ranked = []
    for r in eligible:
        # Transparent, deterministic commercial scenario, not authoritative sourcing.
        score = (.45 * (1 - r["unit_price_brl"] / max_price)
                 + .25 * r["otif"] + .2 * r["quality"]
                 + .1 * (1 - r["lead_days"] / max_lead))
        ranked.append({"id": r["id"], "title": "Synthetic approved supplier",
                       "score": round(score, 6), "unit_price_brl": r["unit_price_brl"],
                       "total_price_brl": round(quantity * r["unit_price_brl"], 2),
                       "lead_days": r["lead_days"], "otif": r["otif"],
                       "why": "approved + certificate + capacity + lead time, cost/quality ranking"})
    ranked.sort(key=lambda s: (-s["score"], s["id"]))
    return ranked[:top_k]

def _routing(query: str, top_k: int, filters: dict) -> list[dict]:
    if ">" not in query:
        raise ValueError("Route query must have 'origin>destination'")
    origin, destination = (s.strip() for s in query.split(">", 1))
    if not origin or not destination or origin == destination:
        raise ValueError("Choose different route endpoints")
    allowed = set(filters.get("modes", ["truck", "rail"]))
    if not allowed or not allowed <= {"truck", "rail"}:
        raise ValueError("Allowed modes must be truck and/or rail")
    legs = [r for r in FIXTURES["legs"] if r["carrier_approved"] and r["mode"] in allowed]
    graph = {}
    for leg in legs:
        graph.setdefault(leg["from"], []).append(leg)
    # Exhaustively enumerate SIMPLE paths up to five legs; no hidden network data.
    options = []
    def walk(node: str, visited: set[str], selected: list[dict]):
        if len(selected) > 5:
            return
        if node == destination:
            if selected:
                options.append(list(selected))
            return
        for leg in graph.get(node, []):
            nxt = leg["to"]
            if nxt not in visited and len(selected) < 5:
                walk(nxt, visited | {nxt}, selected + [leg])
    walk(origin, {origin}, [])
    if not options:
        return []
    max_cost = max(sum(x["cost_brl"] for x in p) for p in options)
    max_hours = max(sum(x["hours"] for x in p) for p in options)
    max_emissions = max(sum(x["co2_kg"] for x in p) for p in options)
    ranked = []
    for path in options:
        cost = sum(x["cost_brl"] for x in path)
        hours = sum(x["hours"] for x in path)
        co2 = sum(x["co2_kg"] for x in path)
        score = .50 * cost / max_cost + .35 * hours / max_hours + .15 * co2 / max_emissions
        ranked.append({"id": "ROUTE-" + "-".join(x["carrier"] for x in path),
                       "title": f"{origin} → {destination}", "nodes": [origin]+[p["to"] for p in path],
                       "legs": [{"from":x["from"],"to":x["to"],"carrier":x["carrier"],
                                 "mode":x["mode"]} for x in path],
                       "distance_km": sum(x["km"] for x in path),
                       "simulated_hours": round(hours, 3),
                       "simulated_cost_brl": round(cost, 2),
                       "simulated_co2_kg": round(co2, 3),
                       "weighted_objective": round(score, 6),
                       "why": "simple-path constrained search, approved carriers, weighted cost/time/CO2"})
    ranked.sort(key=lambda r: (r["weighted_objective"], r["nodes"]))
    return ranked[:top_k]

def _bom(query: str, top_k: int, filters: dict) -> list[dict]:
    # A BOM is NOT a ranked top-K list; it must never truncate required components.
    # top_k controls the unrelated UI setting and is deliberately ignored here.
    assembly = query.strip().upper()
    assemblies = FIXTURES["bom"]
    if assembly not in assemblies:
        raise ValueError("Unknown assembly: " + assembly)
    needed = Counter()
    def expand(node: str, multiplier: int, stack: set[str]):
        if node in stack:
            raise ValueError("Cyclic BOM")
        if node in assemblies:
            for row in assemblies[node]:
                qty = _positive_int(row["qty"], "BOM quantity")
                expand(row["component"], multiplier * qty, stack | {node})
        else:
            needed[node] += multiplier
    units = _positive_int(filters.get("units", 2), "units", 10000)
    expand(assembly, units, set())
    parts = {p["id"]: p for p in FIXTURES["parts"]}
    output = []
    for part_id, qty in sorted(needed.items()):
        if part_id not in parts:
            raise ValueError("Missing BOM part: " + part_id)
        p = parts[part_id]
        if not p["approved"]:
            raise ValueError("Non-approved BOM item: " + part_id)
        shortfall = max(0, qty - p["stock"])
        pack_size = _positive_int(filters.get("pack_size", 5), "pack_size", 1000)
        order_qty = int(math.ceil(shortfall / pack_size) * pack_size)
        output.append({"id": part_id, "title": p["title"], "required_qty": qty,
                       "stock_qty": p["stock"], "shortfall_qty": shortfall,
                       "suggested_purchase_qty": order_qty,
                       "estimated_purchase_brl": round(order_qty * p["unit_cost_brl"], 2),
                       "why": "recursive BOM explosion; stock and pack-size adjustment"})
    return output

def recommend(project: int, query: str | None = None, top_k: int = 5,
              filters: dict | None = None) -> dict:
    if project not in SPECS:
        raise ValueError("Unknown recommendation project")
    top_k = _positive_int(top_k, "top_k", 50)
    cfg = SPECS[project]
    query = valid_query(cfg["query"] if query is None else query)
    if filters is None:filters = {}
    if not isinstance(filters, dict):
        raise ValueError("Filters must be a JSON object")
    if project in (51, 53):
        rows = _catalog(project, query, top_k, filters)
    elif project == 52:
        rows = _acoustic(query, top_k, filters)
    elif project == 54:
        rows = _parts(query, top_k, filters)
    elif project == 55:
        rows = _learning(query, top_k, filters)
    elif project == 56:
        rows = _skill_matching(query, top_k, filters)
    elif project == 57:
        rows = _feed(query, top_k, filters)
    elif project == 58:
        rows = _supplier(query, top_k, filters)
    elif project == 59:
        rows = _routing(query, top_k, filters)
    elif project == 60:
        rows = _bom(query, top_k, filters)
    else:
        raise AssertionError("Unreachable")
    return {"project_id": project, "title": cfg["title"], "task": cfg["mode"],
            "query": query, "filters": filters, "result_count": len(rows),
            "recommendations": rows,
            "data_origin": "EXCLUSIVELY SYNTHETIC VERSIONED FIXTURES",
            "production_ready": False, "measured_business_impact": False,
            "limitations": "No SAP/Ariba connection or real industrial/market/traffic observations. Human review required."}

def cli(project: int | None = None):
    parser = argparse.ArgumentParser(description="Synthetic industrial recommendation benchmarks")
    if project is None:
        parser.add_argument("project", type=int, choices=sorted(SPECS))
    parser.add_argument("--query", type=str)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--filters-json", type=str, default="{}")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    selected = project if project is not None else args.project
    result = recommend(selected, args.query, args.top_k, json.loads(args.filters_json))
    if args.save:
        (ROOT / "reports").mkdir(exist_ok=True)
        (ROOT / "reports" / f"{selected:03d}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    cli()
