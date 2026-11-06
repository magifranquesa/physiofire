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


def nirv(red, nir):
    """NIRv as in Tang et al. (2026), Eq. 2: (NDVI - 0.08) x NIR (0.08 removes the soil background)."""
    return (ndvi(red, nir) - 0.08) * nir


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
    (assigned to midday). Gaps up to `max_gap_days` between valid composites are bridged.
    DESCRIPTIVE use only: it uses composites after each day (see `composites_to_daily_cut`)."""
    x = da.assign_coords(time=centers)
    x = x.interpolate_na("time", method="linear", max_gap=np.timedelta64(int(max_gap_days * 86400), "s"))
    out = x.interp(time=days + np.timedelta64(12, "h"))
    return out.assign_coords(time=days)


def composites_to_daily_cut(da: xr.DataArray, starts: np.ndarray, centers: np.ndarray, days: np.ndarray,
                            cutoff: np.ndarray, period_days: int, max_gap_days: float,
                            persist_days: float | None) -> xr.DataArray:
    """Daily values from composites with a per-cell cut-off date, for the epoch analysis (no post-fire leakage).

    da       composites, dims (time, lat, lon)
    starts   composite start dates (time); a composite covers start .. start + period_days - 1
    centers  composite centre times (time)
    cutoff   datetime64[D] array (lat, lon): masking date of each cell (NaT = never masked)
    1. Composites whose period ends on or after the cell's cut-off are removed.
    2. Remaining composites are interpolated linearly (gaps <= max_gap_days), as in `composites_to_daily`.
    3. Where that leaves no value (after the last valid composite, or in longer gaps), the last valid
       composite is carried forward for at most `persist_days` (None = no persistence).
    4. All days on or after the cut-off are set to missing.
    """
    starts = np.asarray(starts, dtype="datetime64[D]")
    ends = starts + np.timedelta64(period_days - 1, "D")
    cut = np.asarray(cutoff, dtype="datetime64[D]")
    cut = np.where(np.isnat(cut), np.datetime64("2262-01-01"), cut)
    keep = ends[:, None, None] < cut[None, :, :]
    comp = da.copy(data=np.where(keep, da.values, np.nan))
    daily = composites_to_daily(comp, centers, days, max_gap_days)

    if persist_days is not None:
        vals = comp.values
        valid = np.isfinite(vals)
        idx = np.where(valid, np.arange(vals.shape[0])[:, None, None], -1)
        last_valid = np.maximum.accumulate(idx, axis=0)                      # latest valid composite index
        tmid = days.astype("datetime64[ns]") + np.timedelta64(12, "h")
        k = np.searchsorted(np.asarray(centers, dtype="datetime64[ns]"), tmid, side="right") - 1
        lv = np.where(k[:, None, None] >= 0, last_valid[np.clip(k, 0, None)], -1)      # (day, lat, lon)
        lv_safe = np.clip(lv, 0, None)
        last_val = np.take_along_axis(vals, lv_safe, axis=0)
        age = (tmid[:, None, None] - np.asarray(centers, dtype="datetime64[ns]")[lv_safe]) / np.timedelta64(1, "D")
        fill = (lv >= 0) & np.isnan(daily.values) & (age <= persist_days)
        daily = daily.copy(data=np.where(fill, last_val, daily.values))

    after = days.astype("datetime64[D]")[:, None, None] >= cut[None, :, :]
    return daily.copy(data=np.where(after, np.nan, daily.values))


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
    nirv_f = nirv(nb.red, nb.nir).where(nb_valid)
    nirv_f = nirv_f.where((nirv_f >= 0) & (nirv_f <= 1))      # Tang et al.: keep NIRv in [0, 1]
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

        idx = {}
        for name, x in [("ndvi", ndvi_f), ("evi", evi_f), ("nirv", nirv_f)]:
            if factor == 1:
                idx[name] = x
            else:
                m, _ = block_mean(x.values, w_f.where(x.notnull(), 0.0).values, factor)
                idx[name] = xr.DataArray(m, coords={"time": days, "lat": grid.lat, "lon": grid.lon},
                                         dims=("time", "lat", "lon"))

        coords = {"time": days, "lat": grid.lat, "lon": grid.lon}
        s = sif.sif.where(mask)
        p = par.assign_coords(coords).where(mask)
        f = fpar_d.assign_coords(coords).where(mask)
        nv = idx["nirv"].assign_coords(coords).where(mask)

        # Ratios are stored UNFILTERED: outlier screening (validity thresholds + per-cell robust filter)
        # is applied in the anomaly stage, after post-fire masking (CLAUDE.md, epoch rule 4).
        ds = xr.Dataset({
            "sif": s, "sif_sem": sif.sif_sem.where(mask), "sif_weight": sif.weight_sum.where(mask),
            "par": p, "fpar": f, "apar": p * f,
            "sif_apar": sif_apar(s, p, f), "sif_par": sif_par(s, p),
            "sif_apar_nirv": s / (p * nv), "sif_nirv": s / nv,
            "ndvi": idx["ndvi"].assign_coords(coords).where(mask), "evi": idx["evi"].assign_coords(coords).where(mask),
            "nirv": nv,
            "land_fraction": _open(gee_dir / f"mask_peninsula_{gname}.nc").land_fraction,
        })
        units = {"sif": "mW m-2 sr-1 nm-1", "sif_sem": "mW m-2 sr-1 nm-1", "par": "W m-2", "apar": "W m-2",
                 "fpar": "1", "sif_apar": "mW m-2 sr-1 nm-1 / (W m-2)", "sif_par": "mW m-2 sr-1 nm-1 / (W m-2)",
                 "sif_apar_nirv": "mW m-2 sr-1 nm-1 / (W m-2)", "sif_nirv": "mW m-2 sr-1 nm-1",
                 "ndvi": "1", "evi": "1", "nirv": "1"}
        for v, u in units.items():
            ds[v].attrs["units"] = u
        ds["par"].attrs.update(long_name="PAR (PROVISIONAL: par_fraction x ERA5-Land downward shortwave)",
                               par_fraction=float(pcfg["par_fraction"]), provisional=1)
        ds["fpar"].attrs.update(long_name="daily fPAR, centred interpolation of composites (DESCRIPTIVE ONLY; "
                                          "epoch analysis rebuilds it with composites_to_daily_cut)")
        ds["sif_apar"].attrs.update(long_name="SIF / (PAR x fPAR), unfiltered")
        ds["sif_par"].attrs.update(long_name="SIF / PAR, unfiltered")
        ds["sif_apar_nirv"].attrs.update(long_name="SIF / (PAR x NIRv), unfiltered (sensitivity)")
        ds["sif_nirv"].attrs.update(long_name="SIF / NIRv, unfiltered (sensitivity)")
        ds.attrs = {"title": "PHYSIOFIRE SIF/APAR chain (sample period)", "resolution_deg": grid.res,
                    "par_source": pcfg["source"], "par_provisional": int(bool(pcfg["provisional"])),
                    "sif_source": "TROPOSIF L2B SIF_Corr_743, footprint-weighted",
                    "fpar_source": cfg["gee"]["fpar"]["collection"], "nbar_source": cfg["gee"]["nbar"]["collection"],
                    "Conventions": "CF-1.8"}
        out = out_dir / f"sif_apar_{gname}_{tag}.nc"
        ds.to_netcdf(out, encoding={v: {"zlib": True, "complevel": 4} for v in ds.data_vars})
        log.info("wrote %s", out.relative_to(REPO_ROOT))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", required=True, type=dt.date.fromisoformat)
    p.add_argument("--end", required=True, type=dt.date.fromisoformat)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    build(load_config(), args.start, args.end)


if __name__ == "__main__":
    main()
