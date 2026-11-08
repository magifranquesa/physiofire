"""Daily precipitation of ERA5-Land (UTC day) from the hourly images in Google Earth Engine, on the native 0.1 deg
grid of the study region (same grid as the FWI and AED inputs), for the daily SPEI of question 1.

P(day d) = sum of the 24 `total_precipitation_hourly` images with time stamps d 01:00 .. d+1 00:00 (each image holds
the amount of the hour ENDING at its time stamp; checked on 5-6 March 2025). The GEE daily aggregate is not used
(it differed slightly from the hourly sum in a check). Days with fewer than 24 hourly images are set to missing.
One request per month; one NetCDF per month (resumable).

Usage: python -m physiofire.download.era5land_precip --start 1991-01-01 --end 2025-12-31
Output: {drought_q1.spei.precip_dir}/precip_YYYYMM.nc (pr_mm; time, lat, lon)
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging

import ee
import numpy as np
import xarray as xr

from physiofire.config import REPO_ROOT, load_config
from physiofire.download.era5land_fwi import month_days, native_grid
from physiofire.download.gee import NODATA, fetch, initialize

log = logging.getLogger("era5land_precip")
HOURLY = "ECMWF/ERA5_LAND/HOURLY"
BAND = "total_precipitation_hourly"


def day_image(day: dt.date) -> ee.Image:
    t0 = dt.datetime(day.year, day.month, day.day, 1)
    col = ee.ImageCollection(HOURLY).filterDate(t0.isoformat(), (t0 + dt.timedelta(hours=24)).isoformat()).select(BAND)
    n = col.size()
    return ee.Image(ee.Algorithms.If(n.eq(24), col.sum().multiply(1000), ee.Image.constant(NODATA))).rename("pr")


def run(cfg: dict, start: dt.date, end: dt.date, overwrite: bool = False) -> None:
    grid = native_grid(cfg)
    out_dir = REPO_ROOT / cfg["drought_q1"]["spei"]["precip_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    m = dt.date(start.year, start.month, 1)
    while m <= end:
        nxt = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
        days = month_days(m, start, end)
        f = out_dir / f"precip_{m:%Y%m}.nc"
        if f.exists() and not overwrite:
            with xr.open_dataset(f) as old:
                if old.sizes["time"] >= len(days):
                    log.info("%s exists, skipped", f.name)
                    m = nxt
                    continue
        imgs = [day_image(d).rename(f"pr_{i}") for i, d in enumerate(days)]
        a = fetch(ee.Image.cat(imgs).unmask(NODATA), grid)
        x = np.stack([a[f"pr_{i}"] for i in range(len(days))])
        x[x <= NODATA + 1] = np.nan
        ds = xr.Dataset({"pr_mm": (("time", "lat", "lon"), x.astype("f4"))},
                        coords={"time": np.array(days, dtype="datetime64[ns]"), "lat": grid.lat, "lon": grid.lon})
        ds["pr_mm"].attrs = {"long_name": "precipitation of the UTC day (sum of 24 hourly ERA5-Land amounts)",
                             "units": "mm day-1"}
        ds.attrs = {"source": f"{HOURLY} {BAND}", "grid": "native ERA5-Land 0.1 deg (centres at multiples of 0.1)",
                    "Conventions": "CF-1.8"}
        ds.to_netcdf(f, encoding={"pr_mm": {"zlib": True, "complevel": 4}})
        log.info("wrote %s (%d days)", f.relative_to(REPO_ROOT), len(days))
        m = nxt


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
