"""ERA5-Land hourly inputs of the Canadian Fire Weather Index System from Google Earth Engine, on the native
ERA5-Land 0.1 deg grid of the study region (cell centres at multiples of 0.1 deg; no resampling).

For each day d: temperature, dew point and 10 m wind components at fwi.noon_utc_hour (UTC), and the 24 h
precipitation ending at that hour (sum of the `_hourly` images from noon+1 of day d-1 to noon of day d).
One request per month (all days stacked as bands); one NetCDF per month, so the download can be resumed.

Usage: python -m physiofire.download.era5land_fwi --start 2025-01-01 --end 2025-08-31
Output: {fwi.inputs_dir}/fwi_inputs_YYYYMM.nc (tas_K, tdew_K, u10, v10, pr_m; time, lat, lon)
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging

import ee
import numpy as np
import xarray as xr

from physiofire.config import REPO_ROOT, load_config
from physiofire.download.gee import NODATA, fetch, initialize
from physiofire.preprocess.grid import Grid

log = logging.getLogger("era5land_fwi")
VARS = ["tas", "tdew", "u10", "v10", "pr"]


def native_grid(cfg: dict) -> Grid:
    """ERA5-Land cells whose centres lie in the region (edges half a cell outside the region bounds)."""
    r, res = cfg["region"], float(cfg["fwi"]["native_res_deg"])
    h = res / 2
    return Grid(r["lon_min"] - h, r["lat_min"] - h, r["lon_max"] + h, r["lat_max"] + h, res)


def day_image(fcfg: dict, day: dt.date) -> ee.Image:
    b = fcfg["bands"]
    hh = int(fcfg["noon_utc_hour"])
    col = ee.ImageCollection(fcfg["collection"])
    t_noon = dt.datetime(day.year, day.month, day.day, hh)
    noon = col.filterDate(t_noon.isoformat(), (t_noon + dt.timedelta(hours=1)).isoformat()).first()
    # hourly images T(hh+1) of day-1 .. T(hh) of day: time_start in (t_noon - 24 h, t_noon]
    pr = (col.filterDate((t_noon - dt.timedelta(hours=23)).isoformat(), (t_noon + dt.timedelta(hours=1)).isoformat())
          .select(b["pr_hourly"]))
    n = pr.size()
    pr_sum = ee.Image(ee.Algorithms.If(n.eq(24), pr.sum(), ee.Image.constant(NODATA))).rename("pr")
    return ee.Image(noon).select([b["tas"], b["tdew"], b["u10"], b["v10"]], VARS[:4]).addBands(pr_sum)


def month_days(m0: dt.date, start: dt.date, end: dt.date) -> list[dt.date]:
    m1 = dt.date(m0.year + (m0.month == 12), m0.month % 12 + 1, 1)
    d0, d1 = max(m0, start), min(m1 - dt.timedelta(days=1), end)
    return [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days + 1)]


def run(cfg: dict, start: dt.date, end: dt.date, overwrite: bool = False) -> None:
    fcfg = cfg["fwi"]
    grid = native_grid(cfg)
    out_dir = REPO_ROOT / fcfg["inputs_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    m = dt.date(start.year, start.month, 1)
    while m <= end:
        days = month_days(m, start, end)
        f = out_dir / f"fwi_inputs_{m:%Y%m}.nc"
        full = len(days) == len(month_days(m, m, dt.date(2100, 1, 1)))
        if f.exists() and not overwrite:
            with xr.open_dataset(f) as old:
                if old.sizes["time"] >= len(days):
                    log.info("%s exists, skipped", f.name)
                    m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
                    continue
        imgs = [day_image(fcfg, d).rename([f"{v}_{i}" for v in VARS]) for i, d in enumerate(days)]
        stack = ee.Image.cat(imgs).unmask(NODATA)
        a = fetch(stack, grid)
        data = {}
        for v in VARS:
            x = np.stack([a[f"{v}_{i}"] for i in range(len(days))])
            x[x <= NODATA + 1] = np.nan
            data[v] = x
        if not np.isfinite(data["pr"]).any():
            raise RuntimeError(f"{m:%Y-%m}: no complete 24 h precipitation (hourly images missing?)")
        ds = xr.Dataset({"tas_K": (("time", "lat", "lon"), data["tas"].astype("f4")),
                         "tdew_K": (("time", "lat", "lon"), data["tdew"].astype("f4")),
                         "u10": (("time", "lat", "lon"), data["u10"].astype("f4")),
                         "v10": (("time", "lat", "lon"), data["v10"].astype("f4")),
                         "pr_m": (("time", "lat", "lon"), data["pr"].astype("f4"))},
                        coords={"time": np.array(days, dtype="datetime64[ns]"), "lat": grid.lat, "lon": grid.lon})
        ds["tas_K"].attrs = {"long_name": f"2 m temperature at {fcfg['noon_utc_hour']}:00 UTC", "units": "K"}
        ds["tdew_K"].attrs = {"long_name": f"2 m dew point at {fcfg['noon_utc_hour']}:00 UTC", "units": "K"}
        ds["u10"].attrs = {"long_name": "10 m u wind at noon UTC", "units": "m s-1"}
        ds["v10"].attrs = {"long_name": "10 m v wind at noon UTC", "units": "m s-1"}
        ds["pr_m"].attrs = {"long_name": "precipitation in the 24 h ending at noon UTC", "units": "m"}
        ds.attrs = {"source": fcfg["collection"], "grid": "native ERA5-Land 0.1 deg (centres at multiples of 0.1)",
                    "complete_month": int(full), "Conventions": "CF-1.8"}
        ds.to_netcdf(f, encoding={k: {"zlib": True, "complevel": 4} for k in ds.data_vars})
        log.info("wrote %s (%d days; land cells %d)", f.relative_to(REPO_ROOT), len(days),
                 int(np.isfinite(data["tas"][0]).sum()))
        m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", type=dt.date.fromisoformat, required=True)
    p.add_argument("--end", type=dt.date.fromisoformat, required=True)
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    initialize(cfg["gee"]["project"])
    run(cfg, args.start, args.end, args.overwrite)


if __name__ == "__main__":
    main()
