"""Real Brazilian energy and weather data used in phase 5 (projects #008, #063, #064).

* ONS hourly load by subsystem (curva de carga, MWmed), 2019–2025, committed gzip-compressed with
  the SHA-256 of the original files in data/ons/manifest.json.
* INMET daily data of four automatic stations (BDMEP export), committed the same way in
  data/inmet. Only the original BDMEP columns (marked "(AUT)") are read.

Brazilian national holidays are computed, not downloaded: fixed dates (plus 20 November from 2024,
Lei 14.759/2023) and the movable ones from the Gregorian Easter (anonymous algorithm, Meeus).
Carnival Monday/Tuesday and Corpus Christi are "pontos facultativos", not legal holidays, but the
load drops on them, so they are flagged separately.
"""
from __future__ import annotations

import gzip
import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ONS = ROOT / "data" / "ons"
INMET = ROOT / "data" / "inmet"
COLS = {"TEMPERATURA MEDIA, DIARIA (AUT)(°C)": "tmean", "TEMPERATURA MAXIMA, DIARIA (AUT)(°C)": "tmax",
        "TEMPERATURA MINIMA, DIARIA (AUT)(°C)": "tmin", "UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)": "rh",
        "PRECIPITACAO TOTAL, DIARIO (AUT)(mm)": "rain", "VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)": "wind",
        "TEMPERATURA DO PONTO DE ORVALHO MEDIA DIARIA (AUT)(°C)": "dew"}
LOAD_CITIES = ("A701", "A652", "A521")          # São Paulo, Rio de Janeiro, Belo Horizonte


def manifest(kind: str) -> dict:
    return json.loads(((ONS if kind == "ons" else INMET) / "manifest.json").read_text(encoding="utf-8"))


def ons_hourly(subsystem: str = "SE") -> pd.Series:
    """Hourly load (MWmed) of one subsystem, indexed by local time as published."""
    parts = []
    for name in manifest("ons")["files"]:
        with gzip.open(ONS / f"{name}.gz", "rt", encoding="utf-8") as f:
            parts.append(pd.read_csv(f, sep=";"))
    d = pd.concat(parts)
    d = d[d.id_subsistema == subsystem]
    s = pd.Series(d.val_cargaenergiahomwmed.to_numpy(float), index=pd.to_datetime(d.din_instante), name=f"load_{subsystem}")
    return s.sort_index()


def inmet_daily(station: str) -> pd.DataFrame:
    """Daily BDMEP data with basic consistency checks: rows where Tmin > Tmean or Tmean > Tmax are
    set to missing (they are recording errors), and so are temperatures outside −10…45 °C."""
    with gzip.open(INMET / f"dados_{station}.csv.gz", "rt", encoding="utf-8") as f:
        w = pd.read_csv(f)
    w = w.rename(columns=COLS)
    w["date"] = pd.to_datetime(w["Datas"])
    w = w.set_index("date")[list(COLS.values())].astype(float)
    bad = (w.tmin > w.tmean) | (w.tmean > w.tmax) | (w.tmean < -10) | (w.tmax > 45)
    w.loc[bad, ["tmean", "tmax", "tmin"]] = np.nan
    w.attrs["flagged"] = int(bad.sum())
    return w


def easter(year: int) -> date:
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def holidays(years) -> pd.DataFrame:
    """National holidays and the two load-relevant pontos facultativos."""
    rows = []
    for y in years:
        fixed = [(1, 1, "Confraternização Universal"), (4, 21, "Tiradentes"), (5, 1, "Dia do Trabalho"),
                 (9, 7, "Independência"), (10, 12, "Nossa Senhora Aparecida"), (11, 2, "Finados"),
                 (11, 15, "Proclamação da República"), (12, 25, "Natal")]
        if y >= 2024:
            fixed.append((11, 20, "Consciência Negra"))
        rows += [(date(y, m, d), n, "feriado") for m, d, n in fixed]
        e = easter(y)
        rows += [(e - timedelta(days=48), "Carnaval (segunda)", "ponto facultativo"),
                 (e - timedelta(days=47), "Carnaval (terça)", "ponto facultativo"),
                 (e - timedelta(days=2), "Sexta-feira Santa", "feriado"),
                 (e + timedelta(days=60), "Corpus Christi", "ponto facultativo")]
    h = pd.DataFrame(rows, columns=["date", "name", "kind"])
    h["date"] = pd.to_datetime(h["date"])
    return h.sort_values("date").reset_index(drop=True)


def daily_panel(subsystem: str = "SE", cities=LOAD_CITIES) -> pd.DataFrame:
    """Daily mean load (MWmed), daily peak (max hourly MW) and the hour of the peak, joined with the
    mean temperature of the three largest metropolitan areas of the subsystem (simple mean of the
    stations available that day; missing if fewer than two report)."""
    h = ons_hourly(subsystem)
    day = h.groupby(h.index.normalize())
    df = pd.DataFrame({"load": day.mean(), "peak": day.max(), "peak_hour": day.apply(lambda s: s.idxmax().hour)})
    temps = pd.concat({c: inmet_daily(c)[["tmean", "tmax"]] for c in cities}, axis=1)
    tm = temps.xs("tmean", axis=1, level=1)
    tx = temps.xs("tmax", axis=1, level=1)
    n = tm.notna().sum(axis=1)
    df["temp"] = tm.mean(axis=1).where(n >= 2)
    df["tmax"] = tx.mean(axis=1).where(tx.notna().sum(axis=1) >= 2)
    hol = holidays(range(df.index.year.min(), df.index.year.max() + 1))
    df["holiday"] = df.index.isin(hol.loc[hol.kind == "feriado", "date"])
    df["bridge"] = df.index.isin(hol.loc[hol.kind == "ponto facultativo", "date"])
    df["dow"] = df.index.day_of_week
    return df
