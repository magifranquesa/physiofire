"""Atmospheric evaporative demand as FAO-56 Penman-Monteith reference evapotranspiration (ET0, mm day-1; Allen et
al., 1998) from the ERA5-Land daily inputs (physiofire.download.era5land_aed), native 0.1 deg grid.

    ET0 = [0.408 D (Rn - G) + g 900/(T + 273) u2 (es - ea)] / [D + g (1 + 0.34 u2)]

T = (Tmax + Tmin)/2; es = mean of e0(Tmax) and e0(Tmin) (Eq. 12); ea = e0(Tdew) from the daily mean dew point
(Eq. 14); u2 = u10 x 4.87 / ln(67.8 x 10 - 5.42) (Eq. 47); g from the daily mean surface pressure (Eq. 8);
Rn = (1 - albedo) Rs - Rnl, with Rnl from Tmax, Tmin, ea and Rs/Rso (Eq. 39), Rso = (0.75 + 2e-5 z) Ra (Eq. 37),
Ra from latitude and day of year (Eq. 21) and z from the surface pressure (Eq. 7 inverted); G = 0 (daily).

Usage: python -m physiofire.preprocess.aed --start 2017-01-01 --end 2026-10-31
Output: {aed.out_dir}/aed_era5land_{start}_{end}.nc (aed = ET0, mm day-1; native 0.1 deg)
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging

import numpy as np
import xarray as xr

from physiofire.config import REPO_ROOT, load_config

log = logging.getLogger(__name__)
SIGMA = 4.903e-9  # MJ K-4 m-2 day-1


def e0(t_c):
    """Saturation vapour pressure (kPa) at temperature t (degC), FAO-56 Eq. 11."""
    return 0.6108 * np.exp(17.27 * t_c / (t_c + 237.3))


def extraterrestrial_radiation(lat_deg, doy):
    """Ra (MJ m-2 day-1), FAO-56 Eqs. 21-25."""
    phi = np.deg2rad(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    delta = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(delta), -1, 1))
    return 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws))


def et0_fao56(tmax_c, tmin_c, tdew_c, rs_mj, ps_kpa, u10, lat_deg, doy, albedo=0.23):
    """Daily FAO-56 Penman-Monteith ET0 (mm day-1). Arrays broadcast; lat in degrees, doy day of year."""
    t = (tmax_c + tmin_c) / 2
    es = (e0(tmax_c) + e0(tmin_c)) / 2
    ea = e0(tdew_c)
    delta = 4098 * e0(t) / (t + 237.3) ** 2
    gamma = 0.000665 * ps_kpa
    u2 = u10 * 4.87 / np.log(67.8 * 10 - 5.42)
    z = 293 / 0.0065 * (1 - (ps_kpa / 101.3) ** (1 / 5.26))
    ra = extraterrestrial_radiation(lat_deg, doy)
    rso = (0.75 + 2e-5 * z) * ra
    rel = np.clip(np.where(rso > 0, rs_mj / rso, 1.0), 0.25, 1.0)  # Rs/Rso limited to [0.25, 1] (FAO-56, Eq. 39)
    rnl = SIGMA * ((tmax_c + 273.16) ** 4 + (tmin_c + 273.16) ** 4) / 2 * (0.34 - 0.14 * np.sqrt(np.maximum(ea, 0))) \
        * (1.35 * rel - 0.35)
    rn = (1 - albedo) * rs_mj - rnl
    et0 = (0.408 * delta * rn + gamma * 900 / (t + 273) * u2 * (es - ea)) / (delta + gamma * (1 + 0.34 * u2))
    return np.maximum(et0, 0.0)


def compute(ds: xr.Dataset, albedo: float = 0.23) -> xr.DataArray:
    doy = ds["time"].dt.dayofyear
    lat = ds["lat"]
    out = xr.apply_ufunc(et0_fao56, ds["tmax_K"] - 273.15, ds["tmin_K"] - 273.15, ds["tdew_K"] - 273.15,
                         ds["rs_J"] / 1e6, ds["ps_Pa"] / 1e3, ds["ws10"], lat, doy,
                         kwargs={"albedo": albedo})
    return out.transpose("time", "lat", "lon").rename("aed").assign_attrs(
        long_name="FAO-56 Penman-Monteith reference evapotranspiration (AED)", units="mm day-1")


def run(cfg: dict, start: dt.date, end: dt.date) -> None:
    acfg = cfg["aed"]
    files = sorted((REPO_ROOT / acfg["inputs_dir"]).glob("aed_inputs_*.nc"))
    ds = xr.open_mfdataset(files, combine="by_coords").sel(time=slice(str(start), str(end))).load()
    days = (end - start).days + 1
    if ds.sizes["time"] != days:
        raise ValueError(f"inputs cover {ds.sizes['time']} of {days} days: download them first")
    land = ds["tmax_K"].notnull().all("time")
    gaps = int((ds["ws10"].isnull() & land).sum())
    if gaps:
        raise ValueError(f"{gaps} missing land cell-days of wind speed: incomplete hourly data")
    aed = compute(ds, float(acfg["albedo"])).where(land).astype("f4")
    out = aed.to_dataset()
    out.attrs = {"source": "ERA5-Land daily (GEE ECMWF/ERA5_LAND/DAILY_AGGR; wind from HOURLY)",
                 "method": "FAO-56 Penman-Monteith (Allen et al., 1998), G = 0, Rn from Rs (albedo 0.23) and FAO-56 Rnl",
                 "Conventions": "CF-1.8"}
    f = REPO_ROOT / acfg["out_dir"] / f"aed_era5land_{start:%Y%m%d}_{end:%Y%m%d}.nc"
    out.to_netcdf(f, encoding={"aed": {"zlib": True, "complevel": 4}})
    jja = aed.sel(time=aed["time"].dt.month.isin([6, 7, 8])).mean("time").values
    log.info("wrote %s; JJA mean ET0 p10/p50/p90 = %.1f/%.1f/%.1f mm/day", f.relative_to(REPO_ROOT),
             *np.nanpercentile(jja, [10, 50, 90]))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", type=dt.date.fromisoformat, required=True)
    p.add_argument("--end", type=dt.date.fromisoformat, required=True)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(load_config(), args.start, args.end)


if __name__ == "__main__":
    main()
