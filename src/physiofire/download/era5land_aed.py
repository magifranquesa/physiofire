"""ERA5-Land daily inputs of the FAO-56 Penman-Monteith reference evapotranspiration (AED), from Google Earth
Engine, on the native ERA5-Land 0.1 deg grid (same grid as the FWI; physiofire.download.era5land_fwi.native_grid).

Per UTC day: maximum and minimum 2 m temperature, mean 2 m dew point, surface solar radiation downwards and mean
surface pressure (ECMWF/ERA5_LAND/DAILY_AGGR), and the mean 10 m wind SPEED from the 24 hourly u, v components
(ECMWF/ERA5_LAND/HOURLY; the daily mean components would underestimate the speed).
One request per month; one NetCDF per month (resumable).

Usage: python -m physiofire.download.era5land_aed --start 2018-01-01 --end 2026-10-31
Output: {aed.inputs_dir}/aed_inputs_YYYYMM.nc (tmax_K, tmin_K, tdew_K, rs_J, ps_Pa, ws10)
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

log = logging.getLogger("era5land_aed")
VARS = {"tmax_K": "K", "tmin_K": "K", "tdew_K": "K", "rs_J": "J m-2 day-1", "ps_Pa": "Pa", "ws10": "m s-1"}


def day_image(acfg: dict, day: dt.date) -> ee.Image:
    b = acfg["bands"]
    d0, d1 = day.isoformat(), (day + dt.timedelta(days=1)).isoformat()
    daily = ee.ImageCollection(acfg["daily_collection"]).filterDate(d0, d1).first()
    hourly = ee.ImageCollection(acfg["hourly_collection"]).filterDate(d0, d1)
    ws = hourly.map(lambda i: i.select(b["u10"]).hypot(i.select(b["v10"]))).mean()
    n = hourly.size()
    ws = ee.Image(ee.Algorithms.If(n.eq(24), ws, ee.Image.constant(NODATA))).rename("ws10")
    return (ee.Image(daily).select([b["tmax"], b["tmin"], b["tdew"], b["rs"], b["ps"]],
                                   ["tmax_K", "tmin_K", "tdew_K", "rs_J", "ps_Pa"]).addBands(ws))


def run(cfg: dict, start: dt.date, end: dt.date, overwrite: bool = False) -> None:
    acfg = cfg["aed"]
    grid = native_grid(cfg)
    out_dir = REPO_ROOT / acfg["inputs_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    m = dt.date(start.year, start.month, 1)
    while m <= end:
        days = month_days(m, start, end)
        f = out_dir / f"aed_inputs_{m:%Y%m}.nc"
        nxt = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
        if f.exists() and not overwrite:
            with xr.open_dataset(f) as old:
                if old.sizes["time"] >= len(days):
                    log.info("%s exists, skipped", f.name)
                    m = nxt
                    continue
        names = list(VARS)
        imgs = [day_image(acfg, d).rename([f"{v}_{i}" for v in names]) for i, d in enumerate(days)]
        a = fetch(ee.Image.cat(imgs).unmask(NODATA), grid)
        data = {}
        for v in names:
            x = np.stack([a[f"{v}_{i}"] for i in range(len(days))])
            x[x <= NODATA + 1] = np.nan
            data[v] = x
        ds = xr.Dataset({v: (("time", "lat", "lon"), data[v].astype("f4")) for v in names},
                        coords={"time": np.array(days, dtype="datetime64[ns]"), "lat": grid.lat, "lon": grid.lon})
        for v, u in VARS.items():
            ds[v].attrs["units"] = u
        ds["ws10"].attrs["long_name"] = "daily mean 10 m wind speed (mean of 24 hourly speeds)"
        ds.attrs = {"source": f"{acfg['daily_collection']} + {acfg['hourly_collection']} (wind)",
                    "grid": "native ERA5-Land 0.1 deg (centres at multiples of 0.1)", "day": "UTC",
                    "Conventions": "CF-1.8"}
        ds.to_netcdf(f, encoding={k: {"zlib": True, "complevel": 4} for k in ds.data_vars})
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
