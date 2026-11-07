"""Comparison of the FWI System computed from ERA5-Land at 0.1 deg (main analysis) with the operational CEMS fire
danger reanalysis (ERA5, 0.25 deg; sensitivity R17) for one month.

The 0.1 deg values are averaged within each 0.25 deg CEMS cell (cells centred at multiples of 0.25 deg; every
0.1 deg cell centre lies inside exactly one of them). Only CEMS cells with at least `min_land` of their 0.1 deg
sub-cells on land are compared.

Usage: python -m physiofire.preprocess.fwi_cems_compare --fwi data/interim/era5land_fwi/fwi_era5land_20170101_20261031.nc
           --cems data/raw/cems_fwi/cems_fwi_202508.nc
Output: printed table; {fwi.out_dir}/fwi_cems_compare_YYYYMM.csv (per index: n, r, bias, MAE, medians, spatial r of the
        monthly mean, median temporal r per cell)
"""
from __future__ import annotations

import argparse
import logging

import numpy as np
import pandas as pd
import xarray as xr

from physiofire.config import REPO_ROOT, load_config

log = logging.getLogger(__name__)
PAIRS = {"FWI": "fwinx", "FFMC": "ffmcode", "DMC": "dufmcode", "DC": "drtcode"}


def to_cems_grid(own: xr.Dataset, cems: xr.Dataset, min_land: float = 0.5) -> xr.Dataset:
    """Mean of the 0.1 deg cells inside each 0.25 deg cell; cells with < min_land valid sub-cells set to NaN."""
    iy = np.round(own["lat"].values / 0.25) * 0.25
    ix = np.round(own["lon"].values / 0.25) * 0.25
    o = own.assign_coords(lat25=("lat", iy), lon25=("lon", ix))
    land = o["FWI"].isel(time=0).notnull()
    frac = land.groupby("lat25").mean().groupby("lon25").mean()
    m = o.groupby("lat25").mean().groupby("lon25").mean()
    m = m.where(frac >= min_land).rename(lat25="latitude", lon25="longitude")
    return m.reindex(latitude=cems["latitude"], longitude=cems["longitude"], method="nearest", tolerance=1e-6)


def compare(own: xr.Dataset, cems: xr.Dataset) -> pd.DataFrame:
    cems = cems.rename(valid_time="time") if "valid_time" in cems.dims else cems
    days = np.intersect1d(own["time"].values.astype("datetime64[D]"), cems["time"].values.astype("datetime64[D]"))
    own = own.sel(time=days.astype("datetime64[ns]"))
    cems = cems.sel(time=days.astype("datetime64[ns]"))
    agg = to_cems_grid(own[list(PAIRS)], cems)
    rows = []
    for v, c in PAIRS.items():
        a = agg[v].transpose("time", "latitude", "longitude").values
        b = cems[c].transpose("time", "latitude", "longitude").values
        ok = np.isfinite(a) & np.isfinite(b)
        am, bm = np.nanmean(np.where(ok, a, np.nan), 0), np.nanmean(np.where(ok, b, np.nan), 0)
        okm = np.isfinite(am) & np.isfinite(bm)
        rt = []
        for j, k in zip(*np.where(okm)):
            s = ok[:, j, k]
            if s.sum() > 10 and np.std(a[s, j, k]) > 0 and np.std(b[s, j, k]) > 0:
                rt.append(np.corrcoef(a[s, j, k], b[s, j, k])[0, 1])
        rows.append({"index": v, "n_cell_days": int(ok.sum()), "n_cells": int(okm.sum()),
                     "r_pooled": np.corrcoef(a[ok], b[ok])[0, 1], "bias_own_minus_cems": float(np.mean(a[ok] - b[ok])),
                     "mae": float(np.mean(np.abs(a[ok] - b[ok]))), "median_own": float(np.median(a[ok])),
                     "median_cems": float(np.median(b[ok])), "r_spatial_monthly_mean": np.corrcoef(am[okm], bm[okm])[0, 1],
                     "median_r_temporal": float(np.median(rt))})
    return pd.DataFrame(rows)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fwi", required=True)
    p.add_argument("--cems", required=True)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    own = xr.open_dataset(REPO_ROOT / args.fwi)
    cems = xr.open_dataset(REPO_ROOT / args.cems)
    df = compare(own, cems)
    pd.set_option("display.width", 200)
    print(df.round(3).to_string(index=False))
    month = str(np.datetime_as_string(cems[[c for c in cems.dims if "time" in c][0]].values[0], unit="M")).replace("-", "")
    f = REPO_ROOT / cfg["fwi"]["out_dir"] / f"fwi_cems_compare_{month}.csv"
    df.to_csv(f, index=False)
    log.info("wrote %s", f.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
