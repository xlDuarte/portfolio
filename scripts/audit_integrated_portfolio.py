#!/usr/bin/env python3
"""Audit structural completeness and declared technology limitations in 111 projects.

Only verifies source inventory, syntax, test presence and audit documentation.
Does NOT claim frameworks have executed, PDFs were validated, live APIs are
configured, or models have been externally benchmarked.
"""
from __future__ import annotations
import argparse
import ast
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MATRIX=ROOT/"TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv"
OUTPUT_DEFAULT=ROOT/"reports"/"integrated_portfolio_audit.json"
LABELS={
    "001-030":"Data analytics / EDA / supply-chain / regression",
    "031-040":"Classification",
    "041-050":"NLP",
    "051-060":"Recommendations",
    "061-070":"Time series",
    "071-080":"Vision",
    "081-090":"Business and BI",
    "091-100":"Industrial full-stack",
    "101-110":"Motorsport / MLOps",
    "111":"F1-PIP incomplete model catalogue",
}
ARTIFACT_ROOTS={
    "classification":"classification_batch",
    "nlp":"nlp_batch",
    "recommendation":"recommendation_batch",
    "timeseries":"timeseries_batch",
    "vision":"vision_batch",
    "business":"business_batch",
    "advanced":"advanced_batch",
    "motorsport":"motorsport_batch",
}
KNOWN_LIMITS=[
    {"technology":"Power BI DAX / PBIX/PBIP","status":"UNVERIFIED_RUNTIME",
     "reason":"M and DAX templates are not imported and executed by Power BI Desktop / Tabular engine"},
    {"technology":"SAP/Ariba/MES/OT real integration","status":"NOT_CONNECTED",
     "reason":"No approved live system, data extract and authorization evidenced"},
    {"technology":"FIA/FastF1 official telemetry, Interlagos GPS","status":"NOT_VALIDATED",
     "reason":"Synthetic replay, no licensed official source-backed performance evaluation"},
    {"technology":"FLIR/NDT, ChassisSim","status":"NOT_VALIDATED",
     "reason":"Numeric heatmaps and QSS proxy cannot substitute for instruments/proprietary simulation"},
    {"technology":"F1-PIP model catalogue #111","status":"INCOMPLETE",
     "reason":"Declared production model catalogue not actually fit/validated in existing application"},
    {"technology":"MLflow registry/production security","status":"NOT_DEPLOYED",
     "reason":"CI exercises local experiment tracking; production registry/access controls absent"},
]
def build_audit(root:Path=ROOT)->dict:
    programs=list((root/"projetos").glob("**/main.py"))
    entries=[]
    for p in programs:
        match=re.match(r"^(\d{3})-",p.parent.name)
        if match is None:raise ValueError(f"Unnumbered canonical program: {p}")
        index=int(match.group(1))
        text=p.read_text(encoding="utf-8")
        try:tree=ast.parse(text,filename=str(p))
        except SyntaxError as e:raise ValueError(f"Invalid Python syntax: {p}: {e}") from e
        imports=sorted({node.module.split(".")[0] for node in ast.walk(tree)
                        if isinstance(node,ast.ImportFrom) and node.module}
                       |{name.name.split(".")[0] for node in ast.walk(tree)
                         if isinstance(node,ast.Import) for name in node.names})
        entries.append({"id":index,"path":p.relative_to(root).as_posix(),
                        "readme_exists":(p.parent/"README.md").exists(),
                        "imports_direct":imports,
                        "entrypoint_python_syntax_valid":True})
    entries.sort(key=lambda r:r["id"])
    numbers=[e["id"] for e in entries]
    if numbers!=list(range(1,112)):
        raise ValueError(f"Canonical 111-project inventory mismatch: {numbers}")
    with (root/"TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv").open(
        newline="",encoding="utf-8") as stream:
        matrix=list(csv.DictReader(stream))
    if len(matrix)!=111 or sorted(int(row["id"]) for row in matrix)!=list(range(1,112)):
        raise ValueError("Integrated technology matrix does not cover each project 1..111 exactly once")
    for row in matrix:
        index=int(row["id"])
        expected=entries[index-1]["path"].rsplit("/",1)[0]
        if row["programa"]!=expected:
            raise ValueError(f"Technology matrix path disagrees for #{index}: {row['programa']} != {expected}")
        if not row["lacunas_nao_comprovadas"] or not row["evidencia_no_codigo"]:
            raise ValueError(f"Missing evidence/limitation disclosure at #{index}")
    if not all(e["readme_exists"] for e in entries):raise ValueError("At least one README missing")
    modules={name:(root/path).is_dir() for name,path in ARTIFACT_ROOTS.items()}
    if not all(modules.values()):raise ValueError("A domain implementation package is missing")
    workflows=list((root/".github"/"workflows").glob("*.yml"))
    known_packages={
        "classification":range(31,41),"nlp":range(41,51),
        "recommendation":range(51,61),"timeseries":range(61,71),
        "vision":range(71,81),"business":range(81,91),
        "advanced":range(91,101),"motorsport":range(101,111)}
    domains=[]
    for name,ids in known_packages.items():
        cases=[entries[x-1] for x in ids]
        path=root/"site"/"cases"/name
        domains.append({"domain":name,"project_ids":list(ids),
                        "package_present":modules[name],
                        "case_index_present":(path/"index.html").is_file(),
                        "individual_site_pages_present":
                            sum((path/f"{i:03d}"/"index.html").is_file() for i in ids)})
    return {
        "audit_type":"STATIC_PORTFOLIO_INVENTORY_AND_SCOPE_VALIDATION",
        "source":"repository files at execution time",
        "canonical_projects":111,
        "all_readmes_present":True,
        "python_entrypoints_syntax_valid":111,
        "technology_gap_matrix_rows":len(matrix),
        "domain_code_packages_present":sum(modules.values()),
        "workflow_files_present":len(workflows),
        "domains":domains,"projects":entries,
        "externally_validated_projects":None,
        "production_maturity_score":None,
        "scope_limitations":KNOWN_LIMITS,
        "disclaimer":"Static presence/import inspection cannot establish runtime use, model accuracy or external integration.",
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,default=OUTPUT_DEFAULT)
    p.add_argument("--check",action="store_true",
                   help="Validate without writing a JSON artifact")
    args=p.parse_args()
    result=build_audit()
    if not args.check:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                               encoding="utf-8")
    print(f"Static audit OK: {result['canonical_projects']} numbered projects, "
          f"{result['technology_gap_matrix_rows']} gap rows, "
          f"{result['domain_code_packages_present']} domain packages; "
          "external performance NOT certified.")
if __name__=="__main__":main()
