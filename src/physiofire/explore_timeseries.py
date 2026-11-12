"""Exploratory time-series figures (config explore_timeseries): descriptive only, no statistics.

Steps:
  cells   choose the cells by the fixed rules of the config (without looking at any vegetation series):
          burned cells of August 2025 fires (3 largest per country) with 2 controls each, and shrubland cells of the
          largest summer-2022 drought events (definition B of Q1b). Writes explore_cells.csv; the SPEI of their
          ERA5-Land cells is then computed with R/explore_spei.R (same method and reference as question 1).
  series  daily series with drought_q1.build_series (same screening, spike filter and SPEI as question 1); for the
          fire cells (burned and controls) SIF/APAR is recomputed as in the epoch analysis (fPAR composites cut at
          the ignition before interpolation, no persistence; causal_sif_apar); burned
          cells masked from the ignition date (included) before any anomaly; median-by-DOY anomalies
          (2018-2025), backward 15-day mean, both the smoothed and the daily anomaly divided by the SD of the
          smoothed anomaly of the cell (whole period). Writes explore_series.csv (long; case-year April-October).

Usage: python -m physiofire.explore_timeseries {cells,series}
"""
from __future__ import annotations

import argparse
import logging

import numpy as np
import pandas as pd

from physiofire import anomalies, drought_q1 as q1, drought_q1b as qb
from physiofire.config import REPO_ROOT, load_config

log = logging.getLogger(__name__)
MAIN = ["sif_apar", "ndvi", "evi"]


def era5_cell(x: pd.Series) -> pd.Series:
    """Centre of the containing ERA5-Land 0.1 deg cell (0.05 deg centres are never on a 0.1 boundary)."""
    return (np.round(x * 10) / 10).round(2)


def fire_cells(cfg: dict) -> pd.DataFrame:
    e = cfg["explore_timeseries"]["fires"]
    f = pd.read_csv(REPO_ROOT / "data/fires/selected_fires.csv")
    f = f[~f["exclude"].astype(bool) & f["ignition_date"].str.startswith(e["ignition_month"])]
    f = f.sort_values("burned_ha", ascending=False).groupby("country").head(int(e["per_country"]))
    c = pd.read_csv(REPO_ROOT / "data/processed/epoch/epoch_cells.csv")
    rows = []
    for _, fr in f.sort_values(["country", "burned_ha"], ascending=[True, False]).iterrows():
        cf = c[c["fire_id"] == fr["fire_id"]]
        b = cf[(cf["group"] == "burned") & cf["veg"].isin(e["burned_cell_veg"])]
        b = b.sort_values(["burned_fraction", "cell_id"], ascending=[False, True]).head(1)
        k = cf[cf["group"] == "control"].sort_values(["score", "dist_centre_km"]).head(int(e["controls_per_cell"]))
        case = f"fire_{fr['country']}_{fr['fire_id']}"
        for role, d in [("burned", b)] + [(f"control_{i + 1}", k.iloc[[i]]) for i in range(len(k))]:
            r = d.iloc[0]
            rows.append({"case": case, "case_type": "fire", "role": role, "cell_id": r["cell_id"], "iy": r["iy"],
                         "ix": r["ix"], "lon": r["lon"], "lat": r["lat"], "fuel_class": r["veg"],
                         "burned_fraction": r["burned_fraction"], "fire_id": fr["fire_id"],
                         "country": fr["country"], "name": fr["name"], "burned_ha": fr["burned_ha"],
                         "marker_date": fr["ignition_date"], "marker": "ignition"})
    return pd.DataFrame(rows)


def drought_cells(cfg: dict) -> pd.DataFrame:
    e = cfg["explore_timeseries"]["drought"]
    ep = pd.read_csv(REPO_ROOT / cfg["drought_q1b"]["out_dir"] / "episodes_B.csv")
    d0, d1 = e["onset_window"]
    ep = ep[(ep["event"] >= 0) & (ep["onset"] >= d0) & (ep["onset"] <= d1)]
    size = ep.groupby("event").size().rename("n_cells")
    has = ep[ep["fuel_class"] == e["fuel_class"]].groupby("event").size().index
    top = size[size.index.isin(has)].sort_values(ascending=False, kind="stable").head(int(e["n_events"]))
    rows = []
    for i, (ev, n) in enumerate(top.items()):
        g = ep[ep["event"] == ev]
        s = g[g["fuel_class"] == e["fuel_class"]].copy()
        s["d"] = np.hypot(s["lon"] - g["lon"].mean(), s["lat"] - g["lat"].mean())
        r = s.sort_values(["d", "cell"]).iloc[0]
        rows.append({"case": "drought_2022", "case_type": "drought", "role": f"event_{i + 1}",
                     "cell_id": f"q1_{int(r['cell'])}", "iy": r["iy"], "ix": r["ix"], "lon": r["lon"],
                     "lat": r["lat"], "fuel_class": r["fuel_class"], "event": int(ev), "event_cells": int(n),
                     "marker_date": r["onset"], "marker": "drought onset (SPEI-90, def. B)"})
    return pd.DataFrame(rows)


def select_cells(cfg: dict) -> pd.DataFrame:
    cells = pd.concat([fire_cells(cfg), drought_cells(cfg)], ignore_index=True)
    cells["lon01"], cells["lat01"] = era5_cell(cells["lon"]), era5_cell(cells["lat"])
    cells["stratum"] = np.where(cells["fuel_class"].isin(["shrubland", "wet_heath"]), "shrubland", "other")
    cells["aridity_class"] = ""
    return cells


def causal_sif_apar(cfg: dict, cells: pd.DataFrame, ds) -> None:
    """Replace SIF/APAR of the fire cells (burned and controls) in `ds` by the causal version of the epoch analysis
    (Fig. 2): fPAR composites ending on or after the fire's ignition removed BEFORE the daily interpolation, no
    persistence (epoch.sif_apar_causal with persist_days=None), so SIF/APAR is missing from the last valid composite
    centre onwards and from the ignition date on. Then the same screening and spike filter as build_series.
    Controls keep SIF/APAR after the ignition: from the ignition date on they take the question 1 series (fPAR
    interpolated without cut); the burned cell is masked from the ignition later anyway. Drought cells keep the
    question 1 series."""
    from physiofire import epoch
    q, scfg, acfg = cfg["drought_q1"], cfg["sif_apar"], cfg["anomalies"]
    j = np.where(cells["case_type"].to_numpy() == "fire")[0]
    if not j.size:
        return
    inp = epoch.open_inputs(dict(cfg, epoch=dict(cfg["epoch"], optical_sensitivity=False)), q["cells"]["grid"])
    ref = inp["sif"]["sif"]
    days = ds["time"].values.astype("datetime64[D]")
    iy, ix = cells["iy"].to_numpy()[j], cells["ix"].to_numpy()[j]
    sif = epoch._extract(ref, ref, iy, ix, days)
    w = epoch._extract(inp["sif"]["weight_sum"], ref, iy, ix, days)
    par = epoch._extract(inp["par"]["par"], ref, iy, ix, days)
    fp = inp["fpar"]
    comp = epoch._extract(fp["fpar"], ref, iy, ix, None)
    mark = cells["marker_date"].to_numpy()[j]
    new = np.full((days.size, j.size), np.nan)
    for ign in np.unique(mark):
        k = np.where(mark == ign)[0]
        ratio, fpar_d = epoch.sif_apar_causal(sif[:, k], par[:, k], comp[:, k], fp.time.values,
                                              fp.time_center.values, days, np.datetime64(ign, "D"),
                                              int(scfg["fpar_composite_days"]), float(scfg["fpar_max_gap_days"]),
                                              None)
        m = epoch.screening_mask(scfg, fpar_d, par[:, k], w[:, k])
        new[:, k] = ratio if m is None else np.where(m, ratio, np.nan)
    new, _ = anomalies.spike_filter(new, int(acfg["spike_half_window"]), float(acfg["spike_k"]),
                                    int(acfg["spike_min_neighbours"]))
    vals = ds["sif_apar"].values.astype(float)
    # controls: causal series up to the day before ignition, the question 1 series (no cut) from the ignition on
    after = days[:, None] >= mark.astype("datetime64[D]")[None, :]
    ctl = (cells["role"].to_numpy()[j] != "burned")[None, :]
    new = np.where(after & ctl, vals[:, j], new)
    vals[:, j] = new
    ds["sif_apar"] = (("time", "cell"), vals.astype("f4"))


def series_table(cfg: dict, cells: pd.DataFrame) -> pd.DataFrame:
    et, q = cfg["explore_timeseries"], cfg["drought_q1"]
    qa = q["anomalies"]
    c = dict(cfg, drought_q1=dict(q, spei=dict(q["spei"], out_dir=et["out_dir"], scales_days=[90])))
    ds = q1.build_series(c, cells)
    causal_sif_apar(cfg, cells, ds)
    days = ds["time"].values.astype("datetime64[D]")
    burned = (cells["role"] == "burned").to_numpy()
    mark = cells["marker_date"].to_numpy().astype("datetime64[D]")
    post = burned[None, :] & (days[:, None] >= mark[None, :])          # mask from the ignition date, included
    win = int(cfg["anomalies"]["clim_doy_window"])
    w, mf = int(qa["smooth_days"]), float(qa["smooth_min_frac"])
    if et["smoothing"] != "backward":
        raise ValueError("only the backward mean is implemented here")
    out = []
    t = pd.DatetimeIndex(days)
    m0, m1 = (int(x) for x in et["months"])
    for v in MAIN:
        x = np.where(post, np.nan, ds[v].values.astype(float))
        a = anomalies.anomaly_median_doy(x, days, win)
        m = qb.backward_mean(a, w, mf)
        with np.errstate(invalid="ignore"):
            sd = np.nanstd(m, axis=0)
        sd = np.where(sd > 0, sd, np.nan)
        for j, r in cells.reset_index(drop=True).iterrows():
            year = int(str(r["marker_date"])[:4])
            k = (t.year == year) & (t.month >= m0) & (t.month <= m1)
            out.append(pd.DataFrame({"case": r["case"], "role": r["role"], "cell_id": r["cell_id"],
                                     "date": t[k].strftime("%Y-%m-%d"), "variable": v,
                                     "daily_z": a[k, j] / sd[j], "smooth_z": m[k, j] / sd[j]}))
    sp = ds["spei_090"].values.astype(float)
    for j, r in cells.reset_index(drop=True).iterrows():
        year = int(str(r["marker_date"])[:4])
        k = (t.year == year) & (t.month >= m0) & (t.month <= m1)
        out.append(pd.DataFrame({"case": r["case"], "role": r["role"], "cell_id": r["cell_id"],
                                 "date": t[k].strftime("%Y-%m-%d"), "variable": "spei_090",
                                 "daily_z": np.nan, "smooth_z": sp[k, j]}))
    return pd.concat(out, ignore_index=True)


def main(argv=None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("step", choices=["cells", "series"])
    a = p.parse_args(argv)
    cfg = load_config()
    od = REPO_ROOT / cfg["explore_timeseries"]["out_dir"]
    od.mkdir(parents=True, exist_ok=True)
    if a.step == "cells":
        cells = select_cells(cfg)
        cells.to_csv(od / "explore_cells.csv", index=False)
        log.info("wrote %d cells (%d ERA5-Land cells)", len(cells), len(cells[["lon01", "lat01"]].drop_duplicates()))
    else:
        cells = pd.read_csv(od / "explore_cells.csv")
        series_table(cfg, cells).to_csv(od / "explore_series.csv", index=False)
        log.info("wrote %s", od / "explore_series.csv")


if __name__ == "__main__":
    main()
