"""Canadian Fire Weather Index System from the ERA5-Land noon inputs (physiofire.download.era5land_fwi), with
xclim (xclim.compute.fire.cffwis_indices; follows the official CFS R code).

Relative humidity from the 2 m dew point and temperature (Magnus formula over water, Alduchov & Eskridge 1996);
wind speed from the 10 m components. Continuous calculation from the first day of the inputs with the standard
start-up codes (FFMC 85, DMC 6, DC 15), no fire-season start-up/shutdown and no overwintering (fwi in config.yaml).

Usage: python -m physiofire.preprocess.fwi --start 2025-01-01 --end 2025-08-31
Output: {fwi.out_dir}/fwi_era5land_{start}_{end}.nc (FFMC, DMC, DC, ISI, BUI, FWI and the inputs; native 0.1 deg)
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging

import numpy as np
import xarray as xr
from xclim.compute.fire import cffwis_indices

from physiofire.config import REPO_ROOT, load_config

log = logging.getLogger(__name__)


def relative_humidity(tas_c: xr.DataArray, tdew_c: xr.DataArray) -> xr.DataArray:
    """Relative humidity (%) from temperature and dew point (degC), Magnus over water; capped at 100."""
    def es(t):
        return 6.1094 * np.exp(17.625 * t / (t + 243.04))
    return (100 * es(tdew_c) / es(tas_c)).clip(max=100.0)


def noon_inputs(ds: xr.Dataset) -> dict[str, xr.DataArray]:
    """FWI inputs with units, from a dataset with tas_K, tdew_K, u10, v10 (m s-1) and pr_m (24 h, m)."""
    tas = (ds["tas_K"] - 273.15).assign_attrs(units="degC")
    hurs = relative_humidity(tas, ds["tdew_K"] - 273.15).assign_attrs(units="%")
    ws = (np.hypot(ds["u10"], ds["v10"]) * 3.6).assign_attrs(units="km/h")
    pr = (ds["pr_m"] * 1000).clip(min=0).assign_attrs(units="mm/d")
    return {"tas": tas, "hurs": hurs, "sfcWind": ws, "pr": pr}


def compute(ds: xr.Dataset) -> xr.Dataset:
    x = noon_inputs(ds)
    lat = ds["lat"].broadcast_like(ds["tas_K"].isel(time=0)).assign_attrs(units="degrees_north")
    dc, dmc, ffmc, isi, bui, fwi = cffwis_indices(tas=x["tas"], pr=x["pr"], sfcWind=x["sfcWind"], hurs=x["hurs"],
                                                  lat=lat, season_method=None, overwintering=False)
    out = xr.Dataset({"FFMC": ffmc, "DMC": dmc, "DC": dc, "ISI": isi, "BUI": bui, "FWI": fwi,
                      "tas": x["tas"], "hurs": x["hurs"], "sfcWind": x["sfcWind"], "pr": x["pr"]})
    return out.astype("f4")


def run(cfg: dict, start: dt.date, end: dt.date) -> None:
    fcfg = cfg["fwi"]
    in_dir = REPO_ROOT / fcfg["inputs_dir"]
    files = sorted(in_dir.glob("fwi_inputs_*.nc"))
    ds = xr.open_mfdataset(files, combine="by_coords").sel(time=slice(str(start), str(end))).load()
    days = (end - start).days + 1
    if ds.sizes["time"] != days or ds["time"][0].dt.date != start:
        raise ValueError(f"inputs cover {ds.sizes['time']} of {days} days from {start}: download them first")
    land = ds["tas_K"].notnull().all("time")
    gaps = int((ds["pr_m"].isnull() & land).sum())
    if gaps:
        raise ValueError(f"{gaps} missing land cell-days of precipitation: incomplete hourly data")
    out = compute(ds).where(land)
    out.attrs = {"source": "ERA5-Land hourly (GEE ECMWF/ERA5_LAND/HOURLY), noon UTC inputs",
                 "method": "Canadian FWI System, xclim.compute.fire.cffwis_indices (continuous from the first day, "
                           "standard start-up codes, no overwintering)",
                 "noon_utc_hour": int(fcfg["noon_utc_hour"]), "start_of_calculation": str(start),
                 "Conventions": "CF-1.8"}
    f = REPO_ROOT / fcfg["out_dir"] / f"fwi_era5land_{start:%Y%m%d}_{end:%Y%m%d}.nc"
    out.to_netcdf(f, encoding={k: {"zlib": True, "complevel": 4} for k in out.data_vars})
    v = out["FWI"].isel(time=-1).values
    log.info("wrote %s; FWI on the last day p10/p50/p90 = %.1f/%.1f/%.1f", f.relative_to(REPO_ROOT),
             *np.nanpercentile(v, [10, 50, 90]))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", type=dt.date.fromisoformat, required=True)
    p.add_argument("--end", type=dt.date.fromisoformat, required=True)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(load_config(), args.start, args.end)


if __name__ == "__main__":
    main()
