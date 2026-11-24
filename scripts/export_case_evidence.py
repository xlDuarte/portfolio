#!/usr/bin/env python3
"""Run the classification (#031–#040) and vision (#071–#080) projects and save
their results next to each project page, so the site can show real numbers and
the synthetic input image instead of a one-line description.

Writes ``site/cases/<group>/<id>/metrics.json`` (and ``input.png`` for vision).
Usage: python scripts/export_case_evidence.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def export_classification() -> None:
    from classification_batch.engine import evaluate
    for pid in range(31, 41):
        out = ROOT / "site" / "cases" / "classification" / f"{pid:03d}"
        result = evaluate(pid)
        (out / "metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"#{pid:03d} classification ok", file=sys.stderr)


def export_vision() -> None:
    import cv2
    from vision_batch import engine
    scenes = {71: lambda: engine.render_ppe(True, 2026), 72: lambda: engine.render_gesture("open"),
              73: lambda: engine.parts_scene(5), 74: lambda: engine.eye_scene(True),
              75: lambda: engine.serial_scene("AB1234"), 76: lambda: engine.surface_scene("crack"),
              77: lambda: engine.sign_scene("stop"), 78: lambda: engine.scrap_scene("copper", 2026),
              79: lambda: engine.yard_frames(6)[-1], 80: lambda: engine.texture("pearlite", 2026)}
    for pid, scene in scenes.items():
        out = ROOT / "site" / "cases" / "vision" / f"{pid:03d}"
        report = engine.run(pid)  # OpenCV path; CNN training stays opt-in (--deep) and is not run here
        (out / "metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        cv2.imwrite(str(out / "input.png"), scene())
        print(f"#{pid:03d} vision ok", file=sys.stderr)


if __name__ == "__main__":
    export_classification()
    export_vision()
