"""Aridity index of the Global Aridity Index and Potential Evapotranspiration Database (Global-AI_PET),
version 3.1 (Zomer et al., figshare doi:10.6084/m9.figshare.7504448.v7), aggregated to the working grids.

Annual AI = P / ET0 (FAO-56 Penman-Monteith), 1970-2000, 30 arc-second GeoTIFF stored as uint16 x 10000.
v3.1 corrects the overestimated ET0 of v3 (air temperature in degC instead of K in the Stefan-Boltzmann term),
so v3 AI values are too dry; v3.1 is used. Used only to match control cells (epoch.controls).

The 30" grid (origin -180, 90) is aligned with the region bounds, so each 0.05 deg cell is the mean of 6 x 6
source pixels (no resampling). Source pixels with 0 (no data over sea in this file) or 65535 are excluded.

Usage: python -m physiofire.preprocess.aridity
Output: {epoch.static.aridity.out_dir}/aridity_gai_{grid}.nc (aridity_index, aridity_count)
"""
from __future__ import annotations

import logging

import numpy as np
import rioxarray  # noqa: F401 - registers .rio
import xarray as xr

from physiofire.config import REPO_ROOT, load_config
from physiofire.preprocess.grid import grid_from_config

log = logging.getLogger(__name__)
SRC_RES = 1.0 / 120.0


def aggregate(raw: np.ndarray, factor: int, scale: float, invalid: tuple[int, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Block mean of a (ny, nx) integer array, south-to-north rows; invalid source values excluded."""
    x = raw.astype("f8")
    bad = np.isin(raw, invalid)
    x[bad] = np.nan
    ny, nx = x.shape[0] // factor, x.shape[1] // factor
    b = x.reshape(ny, factor, nx, factor)
    n = np.isfinite(b).sum(axis=(1, 3))
    with np.errstate(invalid="ignore"):
        m = np.nansum(b, axis=(1, 3)) / n
    return np.where(n > 0, m * scale, np.nan), n


def run(cfg: dict) -> None:
    acfg = cfg["epoch"]["static"]["aridity"]
    r = cfg["region"]
    src = REPO_ROOT / acfg["file"]
    da = xr.open_dataarray(src, engine="rasterio").squeeze("band", drop=True)
    # exact crop on the 30" grid: pixel centres inside the region
    sub = da.sel(x=slice(r["lon_min"], r["lon_max"]), y=slice(r["lat_max"], r["lat_min"]))
    raw = np.flipud(sub.values)  # south to north
    exp = (int(round((r["lat_max"] - r["lat_min"]) / SRC_RES)), int(round((r["lon_max"] - r["lon_min"]) / SRC_RES)))
    if raw.shape != exp:
        raise ValueError(f"cropped AI array {raw.shape} != expected {exp}: grid not aligned")
    out_dir = REPO_ROOT / acfg["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    for gname in cfg["grids"]:
        grid = grid_from_config(cfg, gname)
        k = int(round(grid.res / SRC_RES))
        m, n = aggregate(raw, k, float(acfg["scale"]), tuple(int(v) for v in acfg["invalid_values"]))
        ds = xr.Dataset({"aridity_index": (("lat", "lon"), m.astype("f4")),
                         "aridity_count": (("lat", "lon"), n.astype("i2"))},
                        coords={"lat": grid.lat, "lon": grid.lon})
        ds["aridity_index"].attrs = {"long_name": "aridity index P / ET0, 1970-2000 (mean of 30 arc-second pixels)",
                                     "units": "1"}
        ds["aridity_count"].attrs = {"long_name": "number of valid 30 arc-second pixels in the cell"}
        ds.attrs = {"source": acfg["source"], "source_file": acfg["file"], "doi": acfg["doi"],
                    "scale_factor_applied": float(acfg["scale"]), "resolution_deg": grid.res, "Conventions": "CF-1.8"}
        f = out_dir / f"aridity_gai_{gname}.nc"
        ds.to_netcdf(f)
        v = m[np.isfinite(m)]
        log.info("wrote %s (cells %d, AI p5/p50/p95 = %.2f/%.2f/%.2f)", f.relative_to(REPO_ROOT), v.size,
                 *np.percentile(v, [5, 50, 95]))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(load_config())


if __name__ == "__main__":
    main()
