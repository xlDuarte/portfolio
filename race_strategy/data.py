"""Lap table of the 2024 Bahrain GP from the OpenF1 extract stored in the site.

Each row is one timed lap with driver, team, compound, tyre age, stint, race lap and flags for
laps that do not represent green-flag race pace (lap 1, pit in-laps, pit out-laps).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "site" / "motorsport" / "data" / "bahrain-2024-race.json"
RACE_LAPS = 57


@dataclass
class LapTable:
    driver: np.ndarray          # acronym
    team: np.ndarray
    lap: np.ndarray             # race lap number (1..57)
    time: np.ndarray            # s
    compound: np.ndarray        # 'SOFT' | 'HARD'
    age: np.ndarray             # tyre age in laps at the start of this lap (laps already done on the set)
    stint: np.ndarray           # stint number per driver
    pit_in: np.ndarray          # bool: car entered the pit lane at the end of this lap
    pit_out: np.ndarray         # bool
    clean: np.ndarray           # bool: usable as green-flag pace

    def subset(self, mask) -> "LapTable":
        return LapTable(**{k: getattr(self, k)[mask] for k in self.__dataclass_fields__})

    def __len__(self) -> int:
        return len(self.lap)


def load(path: Path = DATA) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def lap_table(data: dict, max_time: float = 110.0) -> LapTable:
    drv = {d["driver_number"]: d for d in data["drivers"]}
    stints = {}
    for s in data["stints"]:
        stints.setdefault(s["driver_number"], []).append(s)
    pit_laps = {(p["driver_number"], p["lap_number"]) for p in data["pit"]}
    rows = []
    for lap in data["laps"]:
        n, who, t = lap["lap_number"], lap["driver_number"], lap.get("lap_duration")
        if not t:
            continue
        st = next((s for s in stints.get(who, []) if s["lap_start"] <= n <= s["lap_end"]), None)
        if st is None:
            continue
        age = st.get("tyre_age_at_start", 0) + (n - st["lap_start"])
        pin = (who, n) in pit_laps
        pout = bool(lap.get("is_pit_out_lap"))
        clean = n > 1 and not pin and not pout and t < max_time
        rows.append((drv[who]["name_acronym"], drv[who]["team_name"], n, float(t), st["compound"], age,
                     st["stint_number"], pin, pout, clean))
    cols = list(zip(*rows))
    return LapTable(*(np.array(c) for c in cols))


def pit_losses(t: LapTable, mean_pace) -> list[dict]:
    """Time lost to each pit stop: (in-lap − expected) + (out-lap − expected).

    ``mean_pace(driver, lap, compound, age)`` gives the model's green-flag lap time. The in-lap uses
    the old set, the out-lap the new set at age 0. Stops on lap 1 or followed by retirement are skipped.
    """
    out = []
    key = {(d, n): i for i, (d, n) in enumerate(zip(t.driver, t.lap))}
    for i in np.where(t.pit_in)[0]:
        d, n = t.driver[i], int(t.lap[i])
        j = key.get((d, n + 1))
        if n <= 1 or j is None or not t.pit_out[j]:
            continue
        exp_in = mean_pace(d, n, t.compound[i], int(t.age[i]))
        exp_out = mean_pace(d, n + 1, t.compound[j], int(t.age[j]))
        out.append({"driver": str(d), "lap": n, "loss_s": float(t.time[i] - exp_in + t.time[j] - exp_out),
                    "in_lap_s": float(t.time[i]), "out_lap_s": float(t.time[j])})
    return out
