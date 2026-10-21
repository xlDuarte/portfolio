#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project #008: Plant Shift Utilities & Facility Analysis (Consumo de Utilidades e Operações de Turno)
Category: Industrial Data Analysis (/projetos/dados)
Original Benchmark: 08 Restaurant Sales Analysis
Author: Gabriel Reis Duarte (@gabrielrduarte)
Stack: Pandas, NumPy, Matplotlib, Jupyter, Power BI
"""

import math
import random
import statistics
from datetime import datetime, timezone


class IndustrialProjectPipeline:
    def __init__(self):
        self.project_id = 8
        self.title_pt = 'Consumo de Utilidades e Operações de Turno'
        self.title_en = 'Plant Shift Utilities & Facility Analysis'
        self.category = 'dados'
        self.tools = ['Pandas', 'NumPy', 'Matplotlib', 'Jupyter', 'Power BI']
        self.seed = 1096

    def generate_telemetry_dataset(self, n_samples=120):
        if not isinstance(n_samples, int) or not 2 <= n_samples <= 100_000:
            raise ValueError("n_samples must be an integer between 2 and 100000")
        random.seed(self.seed)
        records = []
        for i in range(n_samples):
            load_factor = 0.55 + 0.35 * math.sin(i * 0.15) + random.uniform(-0.05, 0.05)
            thermal_c = 72.0 + load_factor * 24.5 + random.uniform(-1.5, 1.5)
            oee_score = max(0.50, min(0.99, 0.92 - (thermal_c - 85.0) * 0.004 + random.uniform(-0.02, 0.02)))
            records.append({
                "cycle_id": i + 1,
                "load_factor": round(load_factor, 4),
                "thermal_c": round(thermal_c, 2),
                "oee_kpi": round(oee_score * 100, 2),
                "anomaly_flag": 1 if thermal_c > 94.0 or oee_score < 0.78 else 0
            })
        return records

    def run_pipeline(self):
        data = self.generate_telemetry_dataset()
        oee_vals = [r["oee_kpi"] for r in data]
        therm_vals = [r["thermal_c"] for r in data]
        anomalies = sum(r["anomaly_flag"] for r in data)

        return {
            "project_id": f"#{self.project_id:03d}",
            "route": f"/projetos/{self.category}/008-plant-shift-utilities-facility-analysis",
            "mean_oee_pct": round(statistics.mean(oee_vals), 2),
            "std_oee_pct": round(statistics.stdev(oee_vals), 2),
            "max_thermal_c": round(max(therm_vals), 2),
            "anomaly_rate_pct": round((anomalies / len(data)) * 100, 2),
            "model_validation_status": "not evaluated (synthetic demonstration)",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


if __name__ == "__main__":
    pipeline = IndustrialProjectPipeline()
    result = pipeline.run_pipeline()
    print("=" * 72)
    print(f"[AUTOMOTIVE & INDUSTRIAL LAB] Project {result['project_id']}: Plant Shift Utilities & Facility Analysis")
    for k, v in result.items():
        print(f"  -> {k:<20}: {v}")
    print("=" * 72)
