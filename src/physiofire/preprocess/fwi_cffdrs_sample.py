"""Sample for the cross-check of the FWI System (xclim) against cffdrs (R/check_fwi_cffdrs.R; supplementary S1.10).

Reconstructs data/interim/era5land_fwi/cffdrs_check_sample.csv, first written ad hoc on 2026-11-07 (code recovered
from the session log and versioned here unchanged in substance):

1. xclim run of the FWI System from the ERA5-Land noon inputs (physiofire.preprocess.fwi.compute) for
   1 January - 31 August 2025, STARTING ON 1 JANUARY 2025 with the standard start-up codes (FFMC 85, DMC 6, DC 15),
   so that cffdrs can be started on the same day with the same codes. (The main analysis uses the continuous run
   from 1 January 2017; this short run exists only for the implementation check.)
2. Cells: 30 random land cells of the native 0.1 deg grid (land = temperature available on every day;
   numpy.random.default_rng(42).choice over the land cells in row-major order) plus the ERA5-Land cells nearest
   to four fire centres of 2025 (approximate): Benuza (42.4 N, 6.4 W), A Rua (42.3 N, 7.0 W),
   Navaconcejo (40.1 N, 5.9 W) and Carvicais (41.3 N, 6.9 W). 34 cells x 243 days = 8,262 cell-days.

Usage: python -m physiofire.preprocess.fwi_cffdrs_sample [--out PATH] [--compare-with PATH]
Then:  Rscript R/check_fwi_cffdrs.R [PATH]
"""
from __future__ import annotations

import argparse
import logging

import numpy as np
import pandas as pd
import xarray as xr

from physiofire.config import REPO_ROOT, load_config
from physiofire.preprocess.fwi import compute

log = logging.getLogger(__name__)
START, END = "2025-01-01", "2025-08-31"
SEED, N_RANDOM = 42, 30
FIRE_POINTS = [(42.4, -6.4), (42.3, -7.0), (40.1, -5.9), (41.3, -6.9)]   # Benuza, A Rua, Navaconcejo, Carvicais
COLS = ["tas", "hurs", "sfcWind", "pr", "FFMC", "DMC", "DC", "ISI", "BUI", "FWI"]


def xclim_run(cfg: dict) -> xr.Dataset:
    """FWI System with xclim from the first day of the period (start-up codes on 1 January 2025)."""
    files = sorted((REPO_ROOT / cfg["fwi"]["inputs_dir"]).glob("fwi_inputs_2025*.nc"))
    ds = xr.open_mfdataset(files, combine="by_coords").sel(time=slice(START, END)).load()
    land = ds["tas_K"].notnull().all("time")
    return compute(ds).where(land)


def sample(ds: xr.Dataset) -> pd.DataFrame:
    land = ds["tas"].notnull().all("time")
    rng = np.random.default_rng(SEED)
    iy, ix = np.where(land.values)
    k = rng.choice(iy.size, N_RANDOM, replace=False)
    pts = [(float(ds.lat[iy[i]]), float(ds.lon[ix[i]])) for i in k] + FIRE_POINTS
    rows = []
    for j, (la, lo) in enumerate(pts):
        df = ds.sel(lat=la, lon=lo, method="nearest")[COLS].to_dataframe().reset_index()
        df["id"] = j
        rows.append(df)
    return pd.concat(rows, ignore_index=True)


def main(argv=None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=None, help="output CSV (default: the sample file used by R/check_fwi_cffdrs.R)")
    p.add_argument("--compare-with", default=None, help="existing sample CSV to compare with (max abs difference)")
    a = p.parse_args(argv)
    cfg = load_config()
    out = sample(xclim_run(cfg))
    f = a.out or REPO_ROOT / cfg["fwi"]["out_dir"] / "cffdrs_check_sample.csv"
    out.to_csv(f, index=False)
    log.info("wrote %s: %d cell-days, %d cells", f, len(out), out["id"].nunique())
    if a.compare_with:
        old = pd.read_csv(a.compare_with)
        new = pd.read_csv(f)
        same_cells = old[["id", "lat", "lon"]].drop_duplicates().reset_index(drop=True).equals(
            new[["id", "lat", "lon"]].drop_duplicates().reset_index(drop=True))
        diff = max(float(np.nanmax(np.abs(old[c].to_numpy() - new[c].to_numpy()))) for c in COLS)
        log.info("same cells and order: %s; max abs difference over %s: %.3g", same_cells, COLS, diff)


if __name__ == "__main__":
    main()
