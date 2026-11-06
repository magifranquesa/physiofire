"""Sensitivity to the fPAR sensor: VIIRS VNP15A2H (8-day) vs MODIS MCD15A3H (4-day), sample period.

At the generic QC points (figures/qc/qc_points.csv, chosen by the rule in config `qc_points`) and over all
peninsula cells: correlation, bias and RMSD of daily fPAR, and differences in SIF/APAR.
Quick-look figure only.

Usage:
    python notebooks/02_qc_fpar_viirs_vs_modis.py --start 2025-06-01 --end 2025-09-07
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

from physiofire.config import REPO_ROOT, load_config


def pair_stats(a: pd.Series, b: pd.Series) -> dict:
    d = pd.concat([a, b], axis=1).dropna()
    if len(d) < 5:
        return {"n": len(d)}
    x, y = d.iloc[:, 0], d.iloc[:, 1]
    return {"n": len(d), "r": x.corr(y), "bias": (y - x).mean(), "rel_bias_pct": 100 * (y - x).mean() / x.mean(),
            "rmsd": np.sqrt(((y - x) ** 2).mean())}


def main(argv=None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True, type=dt.date.fromisoformat)
    p.add_argument("--end", required=True, type=dt.date.fromisoformat)
    args = p.parse_args(argv)
    cfg = load_config()
    tag = f"{args.start:%Y%m%d}_{args.end:%Y%m%d}"
    proc = REPO_ROOT / cfg["sif_apar"]["out_dir"]
    qc_dir = REPO_ROOT / "figures" / "qc"
    pts = pd.read_csv(qc_dir / "qc_points.csv")
    roll = int(cfg["qc_points"]["rolling_days"])

    rows = []
    fig, axes = plt.subplots(2, len(pts), figsize=(3.3 * len(pts), 5.2), sharex=True, squeeze=False)
    for gname in ["base", "fine"]:
        ds = xr.open_dataset(proc / f"sif_apar_{gname}_{tag}.nc")
        for j, pt in pts.iterrows():
            c = ds.sel(lat=pt.lat, lon=pt.lon, method="nearest")
            fm, fv = c.fpar.to_series(), c.fpar_viirs.to_series()
            sm = c.sif_apar.to_series().rolling(roll, center=True, min_periods=roll // 3).mean()
            sv = c.sif_apar_viirs.to_series().rolling(roll, center=True, min_periods=roll // 3).mean()
            rows.append({"grid": gname, "point": pt.point, "variable": "fpar (daily)", **pair_stats(fm, fv)})
            rows.append({"grid": gname, "point": pt.point, "variable": f"sif_apar ({roll}-d mean)", **pair_stats(sm, sv)})
            if gname == "base":
                ax = axes[0, j]
                ax.plot(fm.index, fm, color="C0", label="MCD15A3H (4-d)")
                ax.plot(fv.index, fv, color="C1", label="VNP15A2H (8-d)")
                ax.set_title(f"{pt.point}", fontsize=9)
                axes[1, j].plot(sm.index, sm, color="C0")
                axes[1, j].plot(sv.index, sv, color="C1")
                if j == 0:
                    ax.set_ylabel("fPAR")
                    axes[1, j].set_ylabel(f"SIF/APAR ({roll}-d mean)")
                    ax.legend(fontsize=7)
        # Peninsula-wide: per-cell mean difference and correlation of daily fPAR
        land = ds.land_fraction >= cfg["sif_apar"]["min_land_fraction"]
        d = (ds.fpar_viirs - ds.fpar).where(land)
        cell_bias = d.mean("time")
        r = xr.corr(ds.fpar, ds.fpar_viirs, dim="time").where(land)
        rel = (100 * (ds.sif_apar_viirs - ds.sif_apar) / ds.sif_apar).where(land)
        rows.append({"grid": gname, "point": "ALL land cells", "variable": "fpar (daily)",
                     "n": int(land.sum()), "r": float(r.median()), "bias": float(cell_bias.median()),
                     "rel_bias_pct": float(100 * cell_bias.median() / ds.fpar.where(land).mean()),
                     "rmsd": float(np.sqrt((d ** 2).mean()))})
        rows.append({"grid": gname, "point": "ALL land cells", "variable": "sif_apar daily rel. diff (median %)",
                     "n": int(land.sum()), "rel_bias_pct": float(rel.median())})
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(qc_dir / "qc_fpar_viirs_vs_modis.png", dpi=80)
    out = pd.DataFrame(rows)
    out.to_csv(qc_dir / "qc_fpar_viirs_vs_modis.csv", index=False)
    with pd.option_context("display.width", 160):
        print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
