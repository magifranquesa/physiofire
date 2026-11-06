"""Footprint-weighted gridding of TROPOSIF L2B pixels to daily regular grids.

Each TROPOMI pixel is split into k x k sub-points, placed by bilinear interpolation between its four
corners (`latitude_bounds`, `longitude_bounds`, assumed in cyclic order; checked by
`corner_order_is_cyclic`). Each sub-point carries weight 1/k^2 of the pixel to the cell it falls in, so
a pixel straddling several cells contributes to each in proportion to its overlap (approximately).

Per cell and day:
    sif        = sum(w_i * s_i) / sum(w_i)
    sif_sem    = sqrt(sum(w_i^2 * e_i^2)) / sum(w_i)     (propagated 1-sigma retrieval error)
    weight_sum = sum(w_i)                                 (equivalent number of full pixels)
    n_pixels   = number of distinct pixels touching the cell

Usage:
    python -m physiofire.preprocess.troposif_grid --start 2025-06-01 --end 2025-09-07
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging

import numpy as np
import xarray as xr

from physiofire.config import REPO_ROOT, load_config
from physiofire.preprocess.grid import Grid, grid_from_config

log = logging.getLogger("troposif_grid")

FILL_THRESHOLD = 1e30  # L2B 735 nm variables carry 9.97e36 without a declared _FillValue


def subsample_footprints(lon_b: np.ndarray, lat_b: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (lon, lat) of k*k sub-points per pixel, shape (n, k*k). Corners shape (n, 4), cyclic order."""
    u = (np.arange(k) + 0.5) / k
    uu, vv = np.meshgrid(u, u, indexing="xy")
    uu, vv = uu.ravel(), vv.ravel()                      # (k*k,)
    w = np.stack([(1 - uu) * (1 - vv), uu * (1 - vv), uu * vv, (1 - uu) * vv])  # (4, k*k)
    return lon_b @ w, lat_b @ w


def corner_order_is_cyclic(lon_b: np.ndarray, lat_b: np.ndarray) -> np.ndarray:
    """True where corners 0-1-2-3 form a simple (non self-intersecting) quadrilateral.
    Checked by the sign of the cross products at each vertex: all equal for a convex cyclic polygon."""
    x, y = lon_b, lat_b
    signs = []
    for i in range(4):
        a, b, c = i, (i + 1) % 4, (i + 2) % 4
        cross = (x[:, b] - x[:, a]) * (y[:, c] - y[:, b]) - (y[:, b] - y[:, a]) * (x[:, c] - x[:, b])
        signs.append(np.sign(cross))
    s = np.stack(signs, axis=1)
    return np.all(s == s[:, :1], axis=1) & (s[:, 0] != 0)


def grid_day(sif, err, lon_b, lat_b, grid: Grid, k: int) -> dict[str, np.ndarray]:
    """Grid one day of (already filtered) pixels. Returns 2-D arrays (ny, nx)."""
    ncell = grid.nx * grid.ny
    out = {"sif": np.full(ncell, np.nan), "sif_sem": np.full(ncell, np.nan),
           "weight_sum": np.zeros(ncell), "n_pixels": np.zeros(ncell, dtype=np.int32)}
    if sif.size:
        slon, slat = subsample_footprints(lon_b, lat_b, k)          # (n, k*k)
        cell = grid.cell_index(slon, slat)                          # (n, k*k)
        pix = np.repeat(np.arange(sif.size), k * k).reshape(cell.shape)
        ok = cell >= 0
        cell, pix = cell[ok], pix[ok]
        # Aggregate sub-points to (pixel, cell) pairs: weight = fraction of the pixel in the cell.
        pair, w_counts = np.unique(pix * ncell + cell, return_counts=True)
        p_idx, c_idx = pair // ncell, pair % ncell
        w = w_counts / (k * k)
        wsum = np.bincount(c_idx, weights=w, minlength=ncell)
        ws = np.bincount(c_idx, weights=w * sif[p_idx], minlength=ncell)
        we2 = np.bincount(c_idx, weights=(w * err[p_idx]) ** 2, minlength=ncell)
        npix = np.bincount(c_idx, minlength=ncell)
        has = wsum > 0
        out["sif"][has] = ws[has] / wsum[has]
        out["sif_sem"][has] = np.sqrt(we2[has]) / wsum[has]
        out["weight_sum"] = wsum
        out["n_pixels"] = npix.astype(np.int32)
    return {key: v.reshape(grid.ny, grid.nx) for key, v in out.items()}


def load_filtered(path, scfg: dict) -> dict[str, np.ndarray]:
    """Read a regional L2B subset and apply the QC filters. Returns arrays for the kept pixels."""
    with xr.open_dataset(path, decode_times=False, mask_and_scale=False) as ds:
        sif = ds[scfg["variable"]].values.astype("f8")
        err = ds[scfg["error_variable"]].values.astype("f8")
        cf = ds["cloud_fraction_L2"].values.astype("f8")
        lc = ds["LC_MASK"].values
        lon_b = ds["longitude_bounds"].values.astype("f8")
        lat_b = ds["latitude_bounds"].values.astype("f8")
    finite = (np.isfinite(sif) & (np.abs(sif) < FILL_THRESHOLD) & np.isfinite(err) & (np.abs(err) < FILL_THRESHOLD)
              & np.all(np.isfinite(lon_b), axis=1) & np.all(np.isfinite(lat_b), axis=1))
    keep = (finite & np.isfinite(cf) & (cf <= float(scfg["max_cloud_fraction"]))
            & (lc > 0) & ~np.isin(lc, scfg["exclude_lc_classes"]))
    cyclic = corner_order_is_cyclic(lon_b, lat_b)
    return {"sif": sif[keep], "err": err[keep], "lon_b": lon_b[keep], "lat_b": lat_b[keep],
            "n_read": sif.size, "n_kept": int(keep.sum()), "n_noncyclic": int((~cyclic & keep).sum())}


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", required=True, type=dt.date.fromisoformat)
    p.add_argument("--end", required=True, type=dt.date.fromisoformat)
    p.add_argument("--grids", nargs="+", default=["base", "fine"])
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    cfg = load_config()
    scfg, tcfg = cfg["sif"], cfg["troposif"]
    grids = {g: grid_from_config(cfg, g) for g in args.grids}
    k = int(scfg["footprint_subsamples"])
    in_dir = REPO_ROOT / tcfg["out_dir"]
    out_dir = REPO_ROOT / scfg["grid_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    days = [args.start + dt.timedelta(days=i) for i in range((args.end - args.start).days + 1)]
    stacks = {g: {v: [] for v in ("sif", "sif_sem", "weight_sum", "n_pixels")} for g in grids}
    qc = []
    for day in days:
        f = in_dir / f"{day.year}" / f"troposif_l2b_{cfg['region']['name']}_{day:%Y%m%d}.nc"
        if f.exists():
            d = load_filtered(f, scfg)
            if d["n_noncyclic"]:
                log.warning("%s: %d kept pixels with non-cyclic corners", day, d["n_noncyclic"])
        else:
            log.warning("%s: no input file, writing empty day", day)
            d = {"sif": np.empty(0), "err": np.empty(0), "lon_b": np.empty((0, 4)), "lat_b": np.empty((0, 4)),
                 "n_read": 0, "n_kept": 0, "n_noncyclic": 0}
        qc.append((d["n_read"], d["n_kept"], d["n_noncyclic"]))
        for g, grid in grids.items():
            res = grid_day(d["sif"], d["err"], d["lon_b"], d["lat_b"], grid, k)
            for v in res:
                stacks[g][v].append(res[v])
        log.info("%s read %d kept %d", day, d["n_read"], d["n_kept"])

    time = np.array(days, dtype="datetime64[ns]")
    for g, grid in grids.items():
        ds = xr.Dataset(
            {v: (("time", "lat", "lon"), np.stack(stacks[g][v])) for v in stacks[g]},
            coords={"time": time, "lat": grid.lat, "lon": grid.lon},
        )
        ds["n_read"] = ("time", np.array([q[0] for q in qc]))
        ds["n_kept"] = ("time", np.array([q[1] for q in qc]))
        ds["sif"].attrs = {"long_name": f"daily mean {scfg['variable']} (footprint-weighted)", "units": "mW m-2 sr-1 nm-1"}
        ds["sif_sem"].attrs = {"long_name": "propagated 1-sigma error of the daily mean", "units": "mW m-2 sr-1 nm-1"}
        ds["weight_sum"].attrs = {"long_name": "sum of pixel fractions in cell (equivalent full pixels)"}
        ds["n_pixels"].attrs = {"long_name": "number of distinct TROPOMI pixels touching the cell"}
        ds["lat"].attrs = {"units": "degrees_north", "standard_name": "latitude"}
        ds["lon"].attrs = {"units": "degrees_east", "standard_name": "longitude"}
        ds.attrs = {"source": "TROPOSIF L2B (S5P-PAL), regional subset", "resolution_deg": grid.res,
                    "max_cloud_fraction": scfg["max_cloud_fraction"],
                    "excluded_lc_classes": np.array(scfg["exclude_lc_classes"]),
                    "footprint_subsamples": k, "Conventions": "CF-1.8"}
        enc = {v: {"zlib": True, "complevel": 4} for v in ds.data_vars}
        out = out_dir / f"troposif_sif_{g}_{args.start:%Y%m%d}_{args.end:%Y%m%d}.nc"
        ds.to_netcdf(out, encoding=enc)
        log.info("wrote %s", out.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
