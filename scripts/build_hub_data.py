"""Compact data for the hub scenes, read from the case studies (all synthetic, seeded).

Output: site/assets/hubs/hub-data.json (deterministic). The industrial digital twin animates
these numbers; nothing in it is invented.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "case_studies" / "reports" / "metrics.json"
DEMAND = ROOT / "case_studies" / "data" / "demand_daily.csv"
OUT = ROOT / "site" / "assets" / "hubs" / "hub-data.json"
DAYS = 140


def demand_series() -> list[int]:
    with DEMAND.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    first = rows[0]["material"]
    series = [float(r["demand_units"]) for r in rows if r["material"] == first]
    return [int(round(v)) for v in series[-DAYS:]]


def main() -> None:
    m = json.loads(METRICS.read_text(encoding="utf-8"))
    series = demand_series()
    payload = {
        "schema_version": 1, "origin": "synthetic", "source": "case_studies/reports/metrics.json",
        "oee": {"oee_weighted_pct": m["oee"]["oee_weighted_pct"]},
        "supply": {k: m["supply"][k] for k in ("otif_pct", "on_time_pct", "late_mean_days")},
        "capex": {k: m["capex"][k] for k in ("mae_brl", "baseline_mae_brl")},
        "forecast": {"wape_pct": m["forecast"]["wape_pct"], "method": m["forecast"]["method"],
                     "demand_last_days": series},
        "churn": {k: m["churn"][k] for k in ("positive_rate_train", "roc_auc")},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT), OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
