"""FirEUrisk European fuel map (Aragoneses et al., 2023, ESSD 15:1287-1315; data doi:10.21950/YABYCN, v2.0)
aggregated to the working grids as the area fraction of each first-level fuel type.

The source is a single-band categorical GeoTIFF, 1 km, ETRS89-LAEA (EPSG:3035), circa 2019 (inputs 2018-2020),
with 20 of the 24 first-level FirEUrisk fuel types (codes in epoch.fuel.types of config.yaml; sea is coded as 7,
nonfuel). The equal-area projection means every source pixel has the same area, so fractions are pixel counts.

Each 1 km pixel is split into k x k sub-points (epoch.fuel.subsamples); each sub-point is projected to lon/lat and
assigned to the grid cell that contains it. A 0.05 deg cell (~4.4 x 5.6 km at 40 N) receives ~25 pixels, so
sub-sampling is needed to avoid edge effects from assigning whole pixels by their centre.

Fractions are stored per fuel TYPE; grouping into classes (epoch.fuel.classes) is done when reading (R), so the
grouping can change without re-running this step.

Usage: python -m physiofire.preprocess.fuel
Output: {epoch.fuel.out_dir}/fuel_fireurisk_{grid}.nc (type_fraction(fuel_type, lat, lon), pixel_count)
"""
from __future__ import annotations

import logging

import numpy as np
import rioxarray  # noqa: F401 - registers .rio
import xarray as xr
from pyproj import Transformer

from physiofire.config import REPO_ROOT, load_config
from physiofire.preprocess.grid import Grid, grid_from_config

log = logging.getLogger(__name__)


def type_fractions(codes: np.ndarray, x: np.ndarray, y: np.ndarray, res: float, crs: str, grid: Grid,
                   types: list[int], k: int) -> tuple[np.ndarray, np.ndarray]:
    """Area fraction of each type per grid cell from a categorical raster.

    codes: (ny, nx) array of type codes (NaN = no data); x, y: pixel-centre coordinates in `crs`; res: pixel size.
    Returns (fraction (n_types, grid.ny, grid.nx), sub-point count (grid.ny, grid.nx)); fractions are over valid
    sub-points (codes outside `types` count as valid but belong to no type, so the type fractions may sum to < 1).
    """
    off = (np.arange(k) + 0.5) / k - 0.5
    tr = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    ncell = grid.ny * grid.nx
    count = np.zeros((len(types), ncell))
    total = np.zeros(ncell)
    xx, yy = np.meshgrid(x, y)
    valid = np.isfinite(codes)
    c = codes[valid].astype(np.int64)
    type_idx = np.full(c.shape, -1)
    for i, t in enumerate(types):
        type_idx[c == t] = i
    for dx in off:
        for dy in off:
            lon, lat = tr.transform(xx[valid] + dx * res, yy[valid] + dy * res)
            cell = grid.cell_index(lon, lat)
            ok = cell >= 0
            total += np.bincount(cell[ok], minlength=ncell)
            sel = ok & (type_idx >= 0)
            np.add.at(count, (type_idx[sel], cell[sel]), 1.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(total > 0, count / total, np.nan)
    return frac.reshape(len(types), grid.ny, grid.nx), total.reshape(grid.ny, grid.nx)


def run(cfg: dict) -> None:
    fcfg = cfg["epoch"]["fuel"]
    r = cfg["region"]
    types = [int(t) for t in fcfg["types"]]
    k = int(fcfg["subsamples"])
    da = xr.open_dataarray(REPO_ROOT / fcfg["file"], engine="rasterio").squeeze("band", drop=True)
    crs = da.rio.crs.to_string()
    res = abs(float(da.rio.resolution()[0]))
    pad = 0.1  # degrees: keep whole edge cells
    sub = da.rio.clip_box(r["lon_min"] - pad, r["lat_min"] - pad, r["lon_max"] + pad, r["lat_max"] + pad,
                          crs="EPSG:4326")
    codes = sub.values.astype("f8")
    found = set(np.unique(codes[np.isfinite(codes)]).astype(int))
    if found - set(types):
        raise ValueError(f"fuel codes not listed in epoch.fuel.types: {sorted(found - set(types))}")
    out_dir = REPO_ROOT / fcfg["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    for gname in cfg["grids"]:
        grid = grid_from_config(cfg, gname)
        frac, n = type_fractions(codes, sub.x.values, sub.y.values, res, crs, grid, types, k)
        ds = xr.Dataset({"type_fraction": (("fuel_type", "lat", "lon"), frac.astype("f4")),
                         "pixel_count": (("lat", "lon"), (n / k**2).astype("f4"))},
                        coords={"fuel_type": np.array(types, dtype="i4"), "lat": grid.lat, "lon": grid.lon})
        ds["type_fraction"].attrs = {"long_name": "area fraction of each FirEUrisk first-level fuel type",
                                     "units": "1"}
        ds["pixel_count"].attrs = {"long_name": "number of 1 km source pixels in the cell (from sub-points)"}
        ds.attrs = {"source": fcfg["source"], "source_file": fcfg["file"], "doi": fcfg["doi"],
                    "method": f"{k}x{k} sub-points per 1 km pixel, assigned to the containing cell",
                    "resolution_deg": grid.res, "Conventions": "CF-1.8"}
        f = out_dir / f"fuel_fireurisk_{gname}.nc"
        ds.to_netcdf(f)
        s = np.nansum(frac, axis=0)[n > 0]
        log.info("wrote %s (cells with data %d; type fractions sum to 1 in %.1f %%)", f.relative_to(REPO_ROOT),
                 s.size, 100 * np.mean(np.abs(s - 1) < 1e-6))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(load_config())


if __name__ == "__main__":
    main()
