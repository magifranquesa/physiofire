"""Noise that each fPAR source passes on to SIF/APAR (sample period, descriptive interpolation of fPAR).

Sources: MODIS MCD15A3H with FparExtra_QC filter (data/interim/gee/extraqc/), MODIS with FparExtra_QC +
MOD09 cloud state (current main), VIIRS VNP15A2H with FparExtra_QC filter.
Metrics per cell (days where all three are valid):
  - sd of consecutive-day differences of daily SIF/APAR, relative to the cell median;
  - the same on a 7-day TRAILING mean (epoch rule), and number of large jumps (|diff| > 10% of the median);
  - sd of consecutive-day differences of log(fPAR) (noise injected by fPAR alone).
At the generic QC points and summarised by vegetation type (MCD12C1 2017) over all land cells.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from physiofire.config import REPO_ROOT, load_config
from physiofire.indices import composites_to_daily

cfg = load_config()
G = REPO_ROOT / cfg["gee"]["out_dir"]
P = REPO_ROOT / cfg["sif_apar"]["out_dir"]
QC = REPO_ROOT / "figures" / "qc"
TAG = "20250601_20250907"
SOURCES = {"MODIS FparExtra_QC": (G / "extraqc" / "fpar_{g}_20250528_20250911.nc", cfg["sif_apar"]["fpar_max_gap_days"]),
           "MODIS +MOD09 cloud state": (G / "fpar_{g}_20250528_20250911.nc", cfg["sif_apar"]["fpar_max_gap_days"]),
           "VIIRS FparExtra_QC": (G / "fpar_viirs_{g}_20250525_20250906.nc", cfg["sif_apar"]["fpar_viirs_max_gap_days"])}
VEG = {"woodland (1-5)": [1, 2, 3, 4, 5], "shrubland (6-7)": [6, 7], "savannas (8-9)": [8, 9],
       "grassland (10)": [10], "cropland (12,14)": [12, 14]}
ROLL, JUMP = 7, 0.10


def metrics(x: np.ndarray, flog: np.ndarray) -> dict:
    """x: (time, ncell) SIF/APAR; flog: (time, ncell) log fPAR. Per-cell metrics."""
    med = np.nanmedian(x, axis=0)
    d = np.diff(x, axis=0) / med
    tr = pd.DataFrame(x).rolling(ROLL, min_periods=ROLL // 2 + 1).mean().values     # trailing window
    dt_ = np.diff(tr, axis=0) / med
    return {"sd_daily_rel": np.nanstd(d, axis=0), "sd_trail7_rel": np.nanstd(dt_, axis=0),
            "n_jumps_trail7": np.sum(np.abs(dt_) > JUMP, axis=0).astype(float),
            "sd_dlog_fpar": np.nanstd(np.diff(flog, axis=0), axis=0)}


rows_pts, rows_veg = [], []
pts = pd.read_csv(QC / "qc_points.csv")
fig, axes = plt.subplots(1, len(pts), figsize=(3.3 * len(pts), 2.8), squeeze=False)
for g in ["base", "fine"]:
    ds = xr.open_dataset(P / f"sif_apar_{g}_{TAG}.nc")
    days = ds.time.values
    land = (ds.land_fraction >= cfg["sif_apar"]["min_land_fraction"]).values
    lc = xr.open_dataset(G / f"landcover_mcd12c1_2017_{g}.nc").majority.values
    ratios, flogs = {}, {}
    for name, (pat, gap) in SOURCES.items():
        fp = xr.open_dataset(str(pat).format(g=g))
        f = composites_to_daily(fp.fpar.where(fp.fpar_count > 0), fp.time_center.values, days, float(gap))
        f = f.assign_coords(lat=ds.lat, lon=ds.lon)
        ratios[name] = (ds.sif / (ds.par * f)).where(ds.land_fraction >= 0.5)
        flogs[name] = np.log(f.where(f > 0))
    common = np.logical_and.reduce([r.notnull().values for r in ratios.values()])
    met = {n: metrics(np.where(common, r.values, np.nan).reshape(len(days), -1),
                      flogs[n].values.reshape(len(days), -1)) for n, r in ratios.items()}
    # by vegetation type
    flat_land, flat_lc = land.ravel(), lc.ravel()
    for vname, cls in list(VEG.items()) + [("ALL", None)]:
        sel = flat_land & (np.isin(flat_lc, cls) if cls else True)
        for n in SOURCES:
            rows_veg.append({"grid": g, "vegetation": vname, "source": n, "n_cells": int(sel.sum()),
                             **{k: float(np.nanmedian(v[sel])) for k, v in met[n].items()}})
    # generic points
    for j, p in pts.iterrows():
        iy = int(np.abs(ds.lat.values - p.lat).argmin())
        ix = int(np.abs(ds.lon.values - p.lon).argmin())
        k = iy * ds.sizes["lon"] + ix
        for n in SOURCES:
            rows_pts.append({"grid": g, "point": p.point, "source": n, **{m: float(v[k]) for m, v in met[n].items()}})
            if g == "base":
                s = ratios[n].isel(lat=iy, lon=ix).to_series().rolling(ROLL, min_periods=ROLL // 2 + 1).mean()
                axes[0, j].plot(s.index, s, lw=1.2, label=n)
        if g == "base":
            axes[0, j].set_title(p.point, fontsize=9)
axes[0, 0].set_ylabel(f"SIF/APAR ({ROLL}-d trailing mean)")
axes[0, 0].legend(fontsize=6)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(QC / "qc_sif_apar_noise_by_fpar.png", dpi=80)

pd.set_option("display.width", 220)
rv = pd.DataFrame(rows_veg)
rp = pd.DataFrame(rows_pts)
rv.to_csv(QC / "qc_sif_apar_noise_by_fpar_veg.csv", index=False)
rp.to_csv(QC / "qc_sif_apar_noise_by_fpar_points.csv", index=False)
cols = ["sd_daily_rel", "sd_trail7_rel", "n_jumps_trail7", "sd_dlog_fpar"]
for g in ["base", "fine"]:
    print(f"\n=== {g}: median over cells, by vegetation type ===")
    print(rv[rv.grid == g].pivot(index="vegetation", columns="source", values=cols).round(3).to_string())
print("\n=== generic points ===")
print(rp.pivot_table(index=["grid", "point"], columns="source", values=["sd_trail7_rel", "n_jumps_trail7",
                                                                        "sd_dlog_fpar"]).round(3).to_string())
