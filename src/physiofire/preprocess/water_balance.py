"""Daily climatic water balance D = P - ET0 (mm day-1) on the native ERA5-Land 0.1 deg grid, one file per year, for
the daily SPEI of question 1 (docs/plan_q1_drought.md).

P: daily precipitation of the UTC day (physiofire.download.era5land_precip). ET0: FAO-56 Penman-Monteith from the
daily inputs (physiofire.download.era5land_aed; physiofire.preprocess.aed.compute), the same code as the AED.
Days with a missing input are left missing over land (and reported).

Usage: python -m physiofire.preprocess.water_balance --years 1991 2025
Output: {drought_q1.spei.out_dir}/water_balance_YYYY.nc (pr, et0, d)
"""
from __future__ import annotations

import argparse
import logging

import numpy as np
import xarray as xr

from physiofire.config import REPO_ROOT, load_config
from physiofire.preprocess.aed import compute as et0_compute

log = logging.getLogger(__name__)


def year_balance(pr: xr.Dataset, aed_in: xr.Dataset, albedo: float) -> xr.Dataset:
    """D = P - ET0 for one year from the precipitation and ET0-input datasets (same grid and days)."""
    if not (np.array_equal(pr["time"].values, aed_in["time"].values) and np.allclose(pr["lat"], aed_in["lat"])
            and np.allclose(pr["lon"], aed_in["lon"])):
        raise ValueError("precipitation and ET0 inputs are not on the same days and grid")
    et0 = et0_compute(aed_in, albedo)
    p = pr["pr_mm"].clip(min=0)
    ds = xr.Dataset({"pr": p.astype("f4"), "et0": et0.astype("f4"), "d": (p - et0).astype("f4")})
    ds["pr"].attrs = {"long_name": "precipitation (UTC day)", "units": "mm day-1"}
    ds["et0"].attrs = {"long_name": "FAO-56 Penman-Monteith reference evapotranspiration", "units": "mm day-1"}
    ds["d"].attrs = {"long_name": "climatic water balance P - ET0", "units": "mm day-1"}
    return ds


def run(cfg: dict, y0: int, y1: int) -> None:
    q = cfg["drought_q1"]["spei"]
    pdir = REPO_ROOT / q["precip_dir"]
    adir = REPO_ROOT / cfg["aed"]["inputs_dir"]
    out = REPO_ROOT / q["out_dir"]
    out.mkdir(parents=True, exist_ok=True)
    for y in range(y0, y1 + 1):
        pf = sorted(pdir.glob(f"precip_{y}[01][0-9].nc"))
        af = sorted(adir.glob(f"aed_inputs_{y}[01][0-9].nc"))
        if len(pf) != 12 or len(af) != 12:
            raise FileNotFoundError(f"{y}: {len(pf)} precipitation and {len(af)} ET0-input monthly files (need 12)")
        pr = xr.open_mfdataset(pf, combine="by_coords").load()
        ai = xr.open_mfdataset(af, combine="by_coords").load()
        ds = year_balance(pr, ai, float(cfg["aed"]["albedo"]))
        land = ai["tmax_K"].notnull().any("time")
        miss = int((ds["d"].isnull() & land).sum())
        if miss:
            log.warning("%d: %d missing land cell-days", y, miss)
        ds.attrs = {"source": "ERA5-Land (GEE): hourly precipitation, daily aggregates and hourly wind",
                    "grid": "native ERA5-Land 0.1 deg", "Conventions": "CF-1.8"}
        f = out / f"water_balance_{y}.nc"
        ds.to_netcdf(f, encoding={v: {"zlib": True, "complevel": 4} for v in ds.data_vars})
        log.info("wrote %s (mean P %.2f, ET0 %.2f mm/day over land)", f.relative_to(REPO_ROOT),
                 float(ds["pr"].where(land).mean()), float(ds["et0"].where(land).mean()))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--years", type=int, nargs=2, required=True)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(load_config(), *args.years)


if __name__ == "__main__":
    main()
