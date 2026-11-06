"""Vegetation indices and the SIF/APAR chain.

SIF/APAR = SIF / (PAR x fPAR) (apparent fluorescence yield) and SIF/PAR, following Tang et al. (2026),
plus NDVI and EVI from MCD43 NBAR. Builds one daily dataset per grid.

PAR is PROVISIONAL (config `par.source`): par_fraction x ERA5-Land daily downward shortwave, until
CERES SYN1deg Ed4B is available and tested.

Usage:
    python -m physiofire.indices --start 2025-06-01 --end 2025-09-07
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging

import numpy as np
import xarray as xr

from physiofire.config import REPO_ROOT, load_config
from physiofire.download.gee import block_mean
from physiofire.preprocess.grid import grid_from_config

log = logging.getLogger("indices")


# --------------------------------------------------------------------------- formulas

def ndvi(red, nir):
    return (nir - red) / (nir + red)


def evi(red, nir, blue):
    """EVI as in Tang et al. (2026), Eq. 1: 2.5 (NIR - R) / (NIR + 6R - 7.5B + 1)."""
    return 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)


def sif_apar(sif, par, fpar):
    """Apparent fluorescence yield, Tang et al. (2026), Eq. 6."""
    return sif / (par * fpar)


def sif_par(sif, par):
    return sif / par


def clip_percentiles(da: xr.DataArray, lo: float, hi: float) -> tuple[xr.DataArray, float, float]:
    """Mask values outside the [lo, hi] percentiles computed over all valid values."""
    q_lo, q_hi = np.nanpercentile(da.values, [lo, hi])
    return da.where((da >= q_lo) & (da <= q_hi)), float(q_lo), float(q_hi)


def composites_to_daily(da: xr.DataArray, centers: np.ndarray, days: np.ndarray, max_gap_days: float) -> xr.DataArray:
    """Linear interpolation of composites (dim `time`, centred at `centers`) to daily values at `days`
    (assigned to midday). Gaps up to `max_gap_days` between valid composites are bridged."""
    x = da.assign_coords(time=centers)
    x = x.interpolate_na("time", method="linear", max_gap=np.timedelta64(int(max_gap_days * 86400), "s"))
    out = x.interp(time=days + np.timedelta64(12, "h"))
    return out.assign_coords(time=days)


# --------------------------------------------------------------------------- chain

def _open(path):
    return xr.open_dataset(path).load()


def build(cfg: dict, start: dt.date, end: dt.date) -> None:
    gee_dir = REPO_ROOT / cfg["gee"]["out_dir"]
    sif_dir = REPO_ROOT / cfg["sif"]["grid_dir"]
    out_dir = REPO_ROOT / cfg["sif_apar"]["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    pcfg, acfg = cfg["par"], cfg["sif_apar"]
    tag = f"{start:%Y%m%d}_{end:%Y%m%d}"
    days = np.array([np.datetime64(start) + np.timedelta64(i, "D") for i in range((end - start).days + 1)],
                    dtype="datetime64[ns]")
    fine_name = cfg["gee"]["fetch_grid"]
    fine = grid_from_config(cfg, fine_name)

    # NDVI/EVI on the fetch (fine) grid from mean reflectances, as with MCD43C4 at 0.05 deg.
    nb = _open(gee_dir / f"nbar_{fine_name}_{tag}.nc").sel(time=days)
    nb_valid = (nb.red_count > 0) & (nb.nir_count > 0) & (nb.blue_count > 0)
    ndvi_f = ndvi(nb.red, nb.nir).where(nb_valid)
    evi_f = evi(nb.red, nb.nir, nb.blue).where(nb_valid)
    evi_f = evi_f.where((evi_f >= 0) & (evi_f <= 1))          # Tang et al.: keep EVI in [0, 1]
    w_f = nb.red_count.where(nb_valid, 0.0)

    for gname in cfg["grids"]:
        grid = grid_from_config(cfg, gname)
        factor = int(round(grid.res / fine.res))

        sif = _open(sif_dir / f"troposif_sif_{gname}_{tag}.nc").sel(time=days)
        mask = _open(gee_dir / f"mask_peninsula_{gname}.nc").land_fraction >= float(acfg["min_land_fraction"])

        # PAR (PROVISIONAL): fraction of ERA5-Land downward shortwave.
        sw = _open(gee_dir / f"shortwave_{gname}_{tag}.nc").sw.sel(time=days)
        par = (float(pcfg["par_fraction"]) * sw).where(sw > 0)

        # fPAR composites -> daily
        fp = _open(next(p for p in sorted(gee_dir.glob(f"fpar_{gname}_*.nc"))))
        fpar_d = composites_to_daily(fp.fpar.where(fp.fpar_count > 0), fp.time_center.values, days,
                                     float(acfg["fpar_max_gap_days"]))

        if factor == 1:
            ndvi_g, evi_g = ndvi_f, evi_f
        else:
            m, _ = block_mean(ndvi_f.values, w_f.values, factor)
            ndvi_g = xr.DataArray(m, coords={"time": days, "lat": grid.lat, "lon": grid.lon}, dims=("time", "lat", "lon"))
            m, _ = block_mean(evi_f.values, w_f.where(evi_f.notnull(), 0.0).values, factor)
            evi_g = xr.DataArray(m, coords=ndvi_g.coords, dims=ndvi_g.dims)

        coords = {"time": days, "lat": grid.lat, "lon": grid.lon}
        s = sif.sif.where(mask)
        p = par.assign_coords(coords).where(mask)
        f = fpar_d.assign_coords(coords).where(mask)
        ratio_apar, a_lo, a_hi = clip_percentiles(sif_apar(s, p, f), *acfg["clip_percentiles"])
        ratio_par, p_lo, p_hi = clip_percentiles(sif_par(s, p), *acfg["clip_percentiles"])

        ds = xr.Dataset({
            "sif": s, "sif_sem": sif.sif_sem.where(mask), "sif_weight": sif.weight_sum.where(mask),
            "par": p, "fpar": f, "apar": p * f,
            "sif_apar": ratio_apar, "sif_par": ratio_par,
            "ndvi": ndvi_g.assign_coords(coords).where(mask), "evi": evi_g.assign_coords(coords).where(mask),
            "land_fraction": _open(gee_dir / f"mask_peninsula_{gname}.nc").land_fraction,
        })
        units = {"sif": "mW m-2 sr-1 nm-1", "sif_sem": "mW m-2 sr-1 nm-1", "par": "W m-2", "apar": "W m-2",
                 "fpar": "1", "sif_apar": "mW m-2 sr-1 nm-1 / (W m-2)", "sif_par": "mW m-2 sr-1 nm-1 / (W m-2)",
                 "ndvi": "1", "evi": "1"}
        for v, u in units.items():
            ds[v].attrs["units"] = u
        ds["par"].attrs.update(long_name="PAR (PROVISIONAL: par_fraction x ERA5-Land downward shortwave)",
                               par_fraction=float(pcfg["par_fraction"]), provisional=1)
        ds["sif_apar"].attrs.update(long_name="SIF / (PAR x fPAR), clipped to percentiles",
                                    clip_low=a_lo, clip_high=a_hi, clip_percentiles=np.array(acfg["clip_percentiles"]))
        ds["sif_par"].attrs.update(long_name="SIF / PAR, clipped to percentiles", clip_low=p_lo, clip_high=p_hi)
        ds.attrs = {"title": "PHYSIOFIRE SIF/APAR chain (sample period)", "resolution_deg": grid.res,
                    "par_source": pcfg["source"], "par_provisional": int(bool(pcfg["provisional"])),
                    "sif_source": "TROPOSIF L2B SIF_Corr_743, footprint-weighted",
                    "fpar_source": cfg["gee"]["fpar"]["collection"], "nbar_source": cfg["gee"]["nbar"]["collection"],
                    "Conventions": "CF-1.8"}
        out = out_dir / f"sif_apar_{gname}_{tag}.nc"
        ds.to_netcdf(out, encoding={v: {"zlib": True, "complevel": 4} for v in ds.data_vars})
        log.info("wrote %s (SIF/APAR clip %.4g-%.4g)", out.relative_to(REPO_ROOT), a_lo, a_hi)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", required=True, type=dt.date.fromisoformat)
    p.add_argument("--end", required=True, type=dt.date.fromisoformat)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    build(load_config(), args.start, args.end)


if __name__ == "__main__":
    main()
