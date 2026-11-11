"""Diagnostic (not part of any analysis or figure): EVI/NDVI from daily MOD09GA/MYD09GA versus MCD43A4 NBAR in the
18 fire cells of Fig. 3 and S3_1-S3_5 (data/interim/explore/explore_cells.csv), June-July 2025.

Same 0.05 deg yearly series as the analyses (data/interim/gee/series: mod09ga, myd09ga, nbar; bands red, nir, blue
= MODIS bands 1, 2, 3), same index code (epoch._optical: EVI outside [0, 1] discarded), Terra + Aqua combined as in
the analyses, same spike filter on the indices, burned cell masked from the ignition (NBAR from ignition - 8 days,
as epoch.cutoff_offset_days), median-by-DOY climatology 2018-2025 (+-15 days) and SD of the backward 15-day mean of
the anomaly over 2018-2025 (as explore_timeseries).

Outputs (next to this script):
  evi_nbar_fig3_cells.csv      per cell, product (daily, nbar), variable and month (6, 7): raw mean, climatology mean,
                               anomaly (raw units), anomaly / SD, n valid days
  evi_nbar_fig3_nir_june.csv   June NIR anomaly per year 2018-2025, per product (terra, aqua, combined, nbar):
                               mean over the 18 cells, and n valid cell-days

Usage (from the repository root): python docs/diagnostics/evi_nbar_fig3.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

from physiofire import anomalies, drought_q1b as qb, epoch
from physiofire.config import REPO_ROOT, load_config

OUT = Path(__file__).resolve().parent
cfg = load_config()
q, acfg = cfg["drought_q1"], cfg["anomalies"]
cells = pd.read_csv(REPO_ROOT / "data/interim/explore/explore_cells.csv")
cells = cells[cells["case_type"] == "fire"].reset_index(drop=True)
inp = epoch.open_inputs(dict(cfg, epoch=dict(cfg["epoch"], optical_sensitivity=True)), q["cells"]["grid"])
ref = inp["sif"]["sif"]
d0, d1 = (np.datetime64(x) for x in q["period"])
days = np.arange(d0, d1 + np.timedelta64(1, "D"), dtype="datetime64[D]")
iy, ix = cells["iy"].to_numpy(), cells["ix"].to_numpy()

bands, idx = {}, {}
for key, tag in (("sr_terra", "terra"), ("sr_aqua", "aqua"), ("nbar", "nbar")):
    names = [b for b in inp[key].data_vars if b.split("_")[0] in ("red", "nir", "blue")]
    sr = {b: epoch._extract(inp[key][b], ref, iy, ix, days) for b in names}
    ok = np.ones(sr["red"].shape, dtype=bool)
    for b in ("red", "nir", "blue"):
        if f"{b}_count" in sr:
            ok &= sr[f"{b}_count"] > 0
    bands[tag] = {b: np.where(ok, sr[b], np.nan) for b in ("red", "nir", "blue")}
    idx[tag] = epoch._optical(sr)
series = {
    "daily": {"ndvi": epoch.combine_platforms(idx["terra"][0], idx["aqua"][0]),
              "evi": epoch.combine_platforms(idx["terra"][1], idx["aqua"][1]),
              **{b: epoch.combine_platforms(bands["terra"][b], bands["aqua"][b]) for b in ("red", "nir", "blue")}},
    "nbar": {"ndvi": idx["nbar"][0], "evi": idx["nbar"][1], **bands["nbar"]},
}
for prod in series:
    for v in ("ndvi", "evi"):
        series[prod][v], _ = anomalies.spike_filter(series[prod][v], int(acfg["spike_half_window"]),
                                                    float(acfg["spike_k"]), int(acfg["spike_min_neighbours"]))

ign = cells["marker_date"].to_numpy().astype("datetime64[D]")
burned = (cells["role"] == "burned").to_numpy()
win, qa = int(acfg["clim_doy_window"]), q["anomalies"]
t = pd.DatetimeIndex(days)


def anom(x, offset):
    cut = ign + np.timedelta64(offset, "D")
    x = np.where(burned[None, :] & (days[:, None] >= cut[None, :]), np.nan, x)
    a = anomalies.anomaly_median_doy(x, days, win)
    m = qb.backward_mean(a, int(qa["smooth_days"]), float(qa["smooth_min_frac"]))
    with np.errstate(invalid="ignore"):
        sd = np.nanstd(m, axis=0)
    return x, x - a, a, np.where(sd > 0, sd, np.nan)


rows = []
for prod, ss in series.items():
    off = -8 if prod == "nbar" else 0
    for v, x in ss.items():
        xm, clim, a, sd = anom(x, off)
        for j in range(len(cells)):
            for mo in (6, 7):
                k = (t.year == 2025) & (t.month == mo) & np.isfinite(xm[:, j])
                rows.append({"case": cells.loc[j, "case"], "name": cells.loc[j, "name"], "role": cells.loc[j, "role"],
                             "product": prod, "variable": v, "month": mo, "n_days": int(k.sum()),
                             "raw": np.nanmean(xm[k, j]) if k.any() else np.nan,
                             "clim": np.nanmean(clim[k, j]) if k.any() else np.nan,
                             "anom": np.nanmean(a[k, j]) if k.any() else np.nan,
                             "sd": sd[j], "anom_sd": np.nanmean(a[k, j]) / sd[j] if k.any() else np.nan})
pd.DataFrame(rows).to_csv(OUT / "evi_nbar_fig3_cells.csv", index=False)

rows = []
nir = {"terra": bands["terra"]["nir"], "aqua": bands["aqua"]["nir"], "combined": series["daily"]["nir"],
       "nbar": series["nbar"]["nir"]}
for prod, x in nir.items():
    xm, clim, a, sd = anom(x, -8 if prod == "nbar" else 0)
    for y in range(2018, 2026):
        k = (t.year == y) & (t.month == 6)
        rows.append({"product": prod, "year": y, "nir_anom_mean": np.nanmean(a[k]),
                     "nir_raw_mean": np.nanmean(xm[k]), "n_cell_days": int(np.isfinite(a[k]).sum())})
pd.DataFrame(rows).to_csv(OUT / "evi_nbar_fig3_nir_june.csv", index=False)
print("wrote", OUT)
