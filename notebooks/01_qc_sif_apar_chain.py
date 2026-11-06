"""QC of the SIF/APAR chain on the sample period (task 4): maps and series at generic points.

Quick-look figures (matplotlib), not publication figures. Points are chosen by the rule in
config `qc_points` (land cover purity, unburned in 2025, spatial separation), not at fire locations.

Usage:
    python notebooks/01_qc_sif_apar_chain.py --start 2025-06-01 --end 2025-09-07
"""

from __future__ import annotations

import argparse
import datetime as dt

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from scipy.ndimage import maximum_filter

from physiofire.config import REPO_ROOT, load_config

VARS = [("sif", "SIF (mW m-2 sr-1 nm-1)", "YlGn"), ("par", "PAR provisional (W m-2)", "magma"),
        ("fpar", "fPAR", "YlGn"), ("sif_apar", "SIF/APAR", "viridis"), ("sif_par", "SIF/PAR", "viridis"),
        ("ndvi", "NDVI", "YlGn"), ("evi", "EVI", "YlGn")]


def select_points(cfg: dict, tag_burned: str) -> pd.DataFrame:
    q = cfg["qc_points"]
    gee = REPO_ROOT / cfg["gee"]["out_dir"]
    g = q["grid"]
    lc = xr.open_dataset(gee / f"landcover_mcd12c1_{q['landcover_year']}_{g}.nc")
    land = xr.open_dataset(gee / f"mask_peninsula_{g}.nc").land_fraction
    burned = xr.open_dataset(gee / f"burned_{g}_{tag_burned}.nc").burned_fraction
    burned_nb = maximum_filter(burned.values, size=3, mode="nearest")   # cell + 8 neighbours
    ok = (land.values >= q["min_land_fraction"]) & (burned_nb == 0)
    lat2, lon2 = np.meshgrid(lc.lat.values, lc.lon.values, indexing="ij")
    rows = []
    for cname, c in q["classes"].items():
        purity = lc.percent.sel(igbp_class=c["igbp"]).sum("igbp_class").values
        cand = np.argwhere(ok & (purity >= c["min_percent"]))
        cand = cand[np.argsort(-purity[cand[:, 0], cand[:, 1]], kind="stable")]
        chosen = []
        for iy, ix in cand:
            if all(np.hypot(lat2[iy, ix] - lat2[a, b], lon2[iy, ix] - lon2[a, b]) >= q["min_separation_deg"]
                   for a, b in chosen):
                chosen.append((iy, ix))
            if len(chosen) == q["n_per_class"]:
                break
        for k, (iy, ix) in enumerate(chosen):
            rows.append({"point": f"{cname}_{k + 1}", "class": cname, "lat": lat2[iy, ix], "lon": lon2[iy, ix],
                         "purity_percent": purity[iy, ix], "n_candidates": len(cand)})
    return pd.DataFrame(rows)


def maps(ds: xr.Dataset, gname: str, out_dir, period: slice) -> None:
    m = ds.sel(time=period)
    fig, axes = plt.subplots(2, 4, figsize=(18, 7.5), constrained_layout=True)
    for ax, (v, lab, cmap) in zip(axes.flat, VARS):
        x = m[v].mean("time")
        lo, hi = np.nanpercentile(x, [2, 98])
        x.plot(ax=ax, cmap=cmap, vmin=lo, vmax=hi, cbar_kwargs={"label": lab, "shrink": 0.8})
        ax.set_title(f"{v} mean Jul-Aug 2025 ({gname})")
        ax.set_aspect(1 / 0.77)
    cov = m["sif_apar"].notnull().mean("time").where(m["land_fraction"] >= 0.5)
    cov.plot(ax=axes.flat[-1], cmap="cividis", vmin=0, vmax=1, cbar_kwargs={"label": "fraction of days", "shrink": 0.8})
    axes.flat[-1].set_title(f"days with valid SIF/APAR ({gname})")
    axes.flat[-1].set_aspect(1 / 0.77)
    fig.savefig(out_dir / f"qc_maps_{gname}.png", dpi=80)
    plt.close(fig)


def series(dsb: xr.Dataset, dsf: xr.Dataset, pts: pd.DataFrame, out_dir, roll: int) -> pd.DataFrame:
    stats = []
    panels = [("sif_apar", "SIF/APAR"), ("sif_par", "SIF/PAR"), ("sif", "SIF"), ("fpar", "fPAR"),
              ("ndvi", "NDVI"), ("evi", "EVI"), ("par", "PAR (prov.)")]
    fig, axes = plt.subplots(len(panels), len(pts), figsize=(3.2 * len(pts), 2.0 * len(panels)),
                             sharex=True, squeeze=False)
    for j, p in pts.iterrows():
        b = dsb.sel(lat=p.lat, lon=p.lon, method="nearest")
        f = dsf.sel(lat=slice(p.lat - 0.125, p.lat + 0.125), lon=slice(p.lon - 0.125, p.lon + 0.125))
        f_centre = dsf.sel(lat=p.lat, lon=p.lon, method="nearest")
        for i, (v, lab) in enumerate(panels):
            ax = axes[i, j]
            s = b[v].to_series()
            ax.plot(s.index, s.values, ".", ms=2.5, color="0.6", label="daily 0.25°")
            ax.plot(s.index, s.rolling(roll, center=True, min_periods=roll // 3).mean(), "-", color="C0",
                    lw=1.5, label=f"{roll}-d mean 0.25°")
            if v in ("sif_apar", "sif", "ndvi"):
                sf = f_centre[v].to_series()
                ax.plot(sf.index, sf.rolling(roll, center=True, min_periods=roll // 3).mean(), "-", color="C3",
                        lw=1, label=f"{roll}-d mean 0.05° (centre)")
            if j == 0:
                ax.set_ylabel(lab)
            if i == 0:
                ax.set_title(f"{p.point}\n{p.lat:.3f}N {p.lon:.3f}E ({p.purity_percent:.0f}%)", fontsize=9)
        sa = b["sif_apar"].to_series()
        stats.append({"point": p.point, "valid_days_base": int(sa.notnull().sum()),
                      "valid_days_fine_centre": int(f_centre["sif_apar"].notnull().sum()),
                      "sif_apar_median": float(sa.median()), "sif_apar_cv_daily": float(sa.std() / sa.mean()),
                      "sif_apar_fine_vs_base_r": float(pd.concat([f_centre["sif_apar"].to_series(), sa], axis=1)
                                                       .rolling(roll, min_periods=roll // 3).mean().corr().iloc[0, 1]),
                      "n_fine_cells": int(f["sif_apar"].notnull().any("time").sum())})
    axes[0, 0].legend(fontsize=6, loc="upper right")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_dir / "qc_series_points.png", dpi=80)
    plt.close(fig)
    return pd.DataFrame(stats)


def main(argv=None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True, type=dt.date.fromisoformat)
    p.add_argument("--end", required=True, type=dt.date.fromisoformat)
    args = p.parse_args(argv)
    cfg = load_config()
    tag = f"{args.start:%Y%m%d}_{args.end:%Y%m%d}"
    bp = cfg["qc_points"]["burned_period"]
    tag_burned = f"{bp[0].replace('-', '')}_{bp[1].replace('-', '')}"
    out_dir = REPO_ROOT / "figures" / "qc"
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = REPO_ROOT / cfg["sif_apar"]["out_dir"]
    dsb = xr.open_dataset(proc / f"sif_apar_base_{tag}.nc")
    dsf = xr.open_dataset(proc / f"sif_apar_fine_{tag}.nc")

    period = slice("2025-07-01", "2025-08-31")
    for gname, ds in [("base", dsb), ("fine", dsf)]:
        maps(ds, gname, out_dir, period)
        v = ds.sel(time=period)
        q = np.nanpercentile(v.sif_apar.values, [1, 99])
        print(f"{gname}: SIF/APAR valid fraction (land) {float(v.sif_apar.notnull().where(v.land_fraction >= 0.5).mean()):.2f}"
              f" | unfiltered p1-p99 {q[0]:.4g}-{q[1]:.4g} | median SIF/APAR {float(v.sif_apar.median()):.4g}")

    pts = select_points(cfg, tag_burned)
    pts.to_csv(out_dir / "qc_points.csv", index=False)
    print(pts.to_string(index=False))
    st = series(dsb, dsf, pts, out_dir, int(cfg["qc_points"]["rolling_days"]))
    st.to_csv(out_dir / "qc_points_stats.csv", index=False)
    print(st.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
