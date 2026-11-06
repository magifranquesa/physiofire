"""Effect of the FparExtra_QC cloud/cirrus/shadow filter on MCD15A3H and VNP15A2H fPAR (sample period).

Compares files fetched without (data/interim/gee/noextraqc/) and with the filter:
  1. fraction of valid 500 m pixels removed, by vegetation type (MCD12C1 2017) and month;
  2. fraction of retained pixels carrying the aerosol flag (what an aerosol mask would remove);
  3. frequency of valid composites and age of the last valid composite before each possible ignition day
     (relevant for the persistence limit: 5 d MODIS, 11 d VIIRS);
  4. composite-to-composite fPAR drops at the generic QC points.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from physiofire.config import REPO_ROOT, load_config

cfg = load_config()
G = REPO_ROOT / cfg["gee"]["out_dir"]
QC = REPO_ROOT / "figures" / "qc"
FILES = {"MCD15A3H": ("fpar_{g}_20250528_20250911.nc", 4, 1.5, cfg["sif_apar"]["fpar_persist_days"]),
         "VNP15A2H": ("fpar_viirs_{g}_20250525_20250906.nc", 8, 3.5, cfg["sif_apar"]["fpar_viirs_persist_days"])}
VEG = {"woodland (1-5)": [1, 2, 3, 4, 5], "shrubland (6-7)": [6, 7], "savannas (8-9)": [8, 9],
       "grassland (10)": [10], "cropland (12,14)": [12, 14]}
DAYS = pd.date_range("2025-06-01", "2025-09-07", freq="D")


def veg_class(g):
    lc = xr.open_dataset(G / f"landcover_mcd12c1_2017_{g}.nc").majority.values
    out = np.full(lc.shape, "other", dtype=object)
    for name, cls in VEG.items():
        out[np.isin(lc, cls)] = name
    return out


def age_last_valid(valid, starts, period, center):
    """For each possible ignition day d: age (days) at day d-1 of the latest valid composite whose period ends
    before d. valid: (time, ncell) bool. Returns (ndays, ncell) array (inf if none)."""
    ends = starts + pd.Timedelta(days=period - 1)
    centers = starts + pd.Timedelta(hours=24 * center)
    out = np.full((len(DAYS), valid.shape[1]), np.inf)
    for i, d in enumerate(DAYS):
        allowed = np.asarray(ends < d)
        if not allowed.any():
            continue
        v = valid[allowed]
        idx = np.where(v.any(axis=0), v.shape[0] - 1 - np.argmax(v[::-1], axis=0), -1)
        c = np.asarray(centers[allowed])
        age = ((d - pd.Timedelta(days=1) + pd.Timedelta(hours=12)) - pd.DatetimeIndex(c[np.clip(idx, 0, None)]))
        out[i] = np.where(idx >= 0, age / pd.Timedelta(days=1), np.inf)
    return out


rows_removed, rows_freq, rows_drop = [], [], []
pts = pd.read_csv(QC / "qc_points.csv")
fig, axes = plt.subplots(2, len(pts), figsize=(3.3 * len(pts), 5), sharex=True, squeeze=False)
for k, (prod, (pat, period, center, persist)) in enumerate(FILES.items()):
    for g in ["fine", "base"]:
        old = xr.open_dataset(G / "noextraqc" / pat.format(g=g))
        new = xr.open_dataset(G / pat.format(g=g))
        land = (xr.open_dataset(G / f"mask_peninsula_{g}.nc").land_fraction >= 0.5).values
        co, cn = old.fpar_count.values, new.fpar_count.values
        months = pd.DatetimeIndex(old.time.values).month
        veg = veg_class(g)
        if g == "fine":
            for vname in list(VEG) + ["other", "ALL"]:
                sel = land & ((veg == vname) if vname != "ALL" else True)
                for m in sorted(set(months)) + ["ALL"]:
                    t = (months == m) if m != "ALL" else np.ones(len(months), bool)
                    so, sn = co[t][:, sel].sum(), cn[t][:, sel].sum()
                    aer = np.nansum((new.aerosol.values * cn)[t][:, sel]) / sn if sn else np.nan
                    rows_removed.append({"product": prod, "vegetation": vname, "month": m,
                                         "removed_pct": 100 * (1 - sn / so) if so else np.nan,
                                         "aerosol_flag_pct_of_retained": 100 * aer})
        # composite frequency and age of last valid composite
        starts = pd.DatetimeIndex(old.time.values)
        for label, c in [("no cloud filter", co), ("cloud filter", cn)]:
            valid = (c > 0)[:, land]
            age = age_last_valid(valid, starts, period, center)
            fin = np.isfinite(age)
            rows_freq.append({"product": prod, "grid": g, "filter": label,
                              "valid_composites_pct": 100 * valid.mean(),
                              "age_median_d": float(np.median(age[fin])), "age_p90_d": float(np.percentile(age[fin], 90)),
                              "age_p99_d": float(np.percentile(age[fin], 99)),
                              f"pct_days_age_gt_persist({persist}d)": 100 * float((age > persist).mean())})
        # drops at generic points (base grid)
        if g == "base":
            for j, p in pts.iterrows():
                so = old.fpar.where(old.fpar_count > 0).sel(lat=p.lat, lon=p.lon, method="nearest").to_series()
                sn = new.fpar.where(new.fpar_count > 0).sel(lat=p.lat, lon=p.lon, method="nearest").to_series()
                for label, s in [("no cloud filter", so), ("cloud filter", sn)]:
                    d = s.dropna().diff().dropna()
                    rows_drop.append({"product": prod, "point": p.point, "filter": label,
                                      "n_valid": int(s.notna().sum()), "sd_diff": float(d.std()),
                                      "n_abs_diff_gt_0.1": int((d.abs() > 0.1).sum()), "min": float(s.min()),
                                      "mean": float(s.mean())})
                ax = axes[k, j]
                ax.plot(so.index, so, "o-", ms=2.5, lw=0.8, color="0.6", label="no cloud filter")
                ax.plot(sn.index, sn, "o-", ms=2.5, lw=1.2, color="C0" if k == 0 else "C1", label="cloud filter")
                ax.set_title(f"{prod} {p.point}", fontsize=8)
                if j == 0:
                    ax.set_ylabel("fPAR (composites)")
                    ax.legend(fontsize=6)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(QC / "qc_fpar_cloud_filter_points.png", dpi=80)

pd.set_option("display.width", 200)
rem = pd.DataFrame(rows_removed)
rem.to_csv(QC / "qc_fpar_cloud_filter_removed.csv", index=False)
for prod in FILES:
    r = rem[rem["product"] == prod]
    print(f"\n{prod}: % of valid 500 m pixels removed by the cloud/cirrus/shadow filter (rows: vegetation, cols: month)")
    print(r.pivot(index="vegetation", columns="month", values="removed_pct").round(1).to_string())
    print(f"{prod}: % of RETAINED pixels with aerosol flag (would be removed by an aerosol mask)")
    print(r.pivot(index="vegetation", columns="month", values="aerosol_flag_pct_of_retained").round(1).to_string())
fr = pd.DataFrame(rows_freq)
fr.to_csv(QC / "qc_fpar_cloud_filter_frequency.csv", index=False)
print("\nValid composites and age of last valid composite at day -1 (all land cells, ignition days Jun 1-Sep 7)")
print(fr.round(2).to_string(index=False))
dr = pd.DataFrame(rows_drop)
dr.to_csv(QC / "qc_fpar_cloud_filter_drops.csv", index=False)
print("\nComposite-to-composite changes at generic points (base grid)")
print(dr.round(3).to_string(index=False))
