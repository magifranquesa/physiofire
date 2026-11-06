"""Aggregate MODIS products in Google Earth Engine to the project grid and fetch them as NetCDF.

GEE reduces the 500 m data to the fetch grid (0.05 deg by default) with an area-weighted mean of the
valid pixels and their count; coarser grids (0.25 deg) are built locally by count-weighted block
averaging (`block_mean`), so both scales are consistent.

Products:
    fpar        MCD15A3H Fpar, main-algorithm retrievals only (4-day composites)
    nbar        MCD43A4 red/NIR/blue NBAR, mandatory quality <= max (daily); NDVI/EVI computed later
    landcover   MCD12C1 IGBP (Type 1) class percentages, majority class (yearly, native 0.05 deg)
    mask        fraction of each cell inside mainland Spain + Portugal (LSIB boundaries)

Authentication: gcloud application-default credentials with the Earth Engine scope (see README).

Usage:
    python -m physiofire.download.gee fpar --start 2025-06-01 --end 2025-09-07
    python -m physiofire.download.gee nbar --start 2025-06-01 --end 2025-09-07
    python -m physiofire.download.gee landcover --year 2024
    python -m physiofire.download.gee mask
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import time

import ee
import numpy as np
import xarray as xr

from physiofire.config import REPO_ROOT, load_config
from physiofire.preprocess.grid import Grid, grid_from_config

log = logging.getLogger("gee")

SCOPES = ["https://www.googleapis.com/auth/earthengine", "https://www.googleapis.com/auth/cloud-platform"]


def initialize(project: str) -> None:
    """Initialise Earth Engine with gcloud application-default credentials."""
    import google.auth

    creds, _ = google.auth.default(scopes=SCOPES)
    ee.Initialize(credentials=creds, project=project)


def _grid_spec(grid: Grid) -> dict:
    return {
        "dimensions": {"width": grid.nx, "height": grid.ny},
        "affineTransform": {"scaleX": grid.res, "shearX": 0, "translateX": grid.lon_min,
                            "shearY": 0, "scaleY": -grid.res, "translateY": grid.lat_max},
        "crsCode": "EPSG:4326",
    }


def _to_grid(img: ee.Image, grid: Grid, max_pixels: int) -> ee.Image:
    """Area-weighted mean and count of valid (unmasked) pixels per grid cell, for every band."""
    reducer = ee.Reducer.mean().combine(ee.Reducer.count(), sharedInputs=True)
    return (img.reduceResolution(reducer, bestEffort=False, maxPixels=max_pixels)
               .reproject(crs="EPSG:4326", crsTransform=[grid.res, 0, grid.lon_min, 0, -grid.res, grid.lat_max]))


def fetch(img: ee.Image, grid: Grid, retries: int = 4) -> dict[str, np.ndarray]:
    """Fetch an image on `grid` as a dict of 2-D float arrays oriented south to north (like Grid.lat)."""
    for attempt in range(1, retries + 1):
        try:
            arr = ee.data.computePixels({"expression": img, "fileFormat": "NUMPY_NDARRAY", "grid": _grid_spec(grid)})
            break
        except Exception as e:  # noqa: BLE001 - transient EE errors (quota, timeouts)
            if attempt == retries:
                raise
            log.warning("computePixels attempt %d failed: %s", attempt, str(e)[:200])
            time.sleep(15 * attempt)
    return {name: np.flipud(arr[name].astype("f8")) for name in arr.dtype.names}


def block_mean(mean: np.ndarray, count: np.ndarray, factor: int) -> tuple[np.ndarray, np.ndarray]:
    """Count-weighted block average of a (..., ny, nx) array by an integer factor (fine -> coarse grid)."""
    m = np.where(count > 0, mean, 0.0)
    shp = mean.shape[:-2] + (mean.shape[-2] // factor, factor, mean.shape[-1] // factor, factor)
    wsum = (m * count).reshape(shp).sum(axis=(-3, -1))
    csum = count.reshape(shp).sum(axis=(-3, -1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(csum > 0, wsum / csum, np.nan), csum


# --------------------------------------------------------------------------- products

def fpar_images(gcfg: dict, start: dt.date, end: dt.date) -> ee.ImageCollection:
    f = gcfg["fpar"]

    def prep(img):
        qc = img.select("FparLai_QC")
        scf = qc.rightShift(5).bitwiseAnd(7)
        fpar = img.select("Fpar")
        ok = scf.lte(int(f["scf_qc_max"])).And(fpar.lte(100))
        return fpar.multiply(0.01).updateMask(ok).rename("fpar").copyProperties(img, ["system:time_start"])

    return ee.ImageCollection(f["collection"]).filterDate(str(start), str(end + dt.timedelta(days=1))).map(prep)


def nbar_images(gcfg: dict, start: dt.date, end: dt.date) -> ee.ImageCollection:
    n = gcfg["nbar"]
    qmax = int(n["max_mandatory_quality"])

    def prep(img):
        out = []
        for key, band in n["bands"].items():
            qband = band.replace("Nadir_Reflectance_", "BRDF_Albedo_Band_Mandatory_Quality_")
            out.append(img.select(band).multiply(0.0001)
                          .updateMask(img.select(qband).lte(qmax)).rename(key))
        return ee.Image(out).copyProperties(img, ["system:time_start"])

    return ee.ImageCollection(n["collection"]).filterDate(str(start), str(end + dt.timedelta(days=1))).map(prep)


def _collection_dates(col: ee.ImageCollection) -> list[int]:
    return col.aggregate_array("system:time_start").getInfo()


def run_timeseries(product: str, cfg: dict, start: dt.date, end: dt.date) -> None:
    gcfg = cfg["gee"]
    fine = grid_from_config(cfg, gcfg["fetch_grid"])
    col = fpar_images(gcfg, start, end) if product == "fpar" else nbar_images(gcfg, start, end)
    times = _collection_dates(col)
    imgs = col.toList(len(times))
    log.info("%s: %d images", product, len(times))

    layers: dict[str, list] = {}
    for i, t in enumerate(times):
        img = _to_grid(ee.Image(imgs.get(i)), fine, int(gcfg["max_pixels"]))
        a = fetch(img, fine)
        for k, v in a.items():
            layers.setdefault(k, []).append(v)
        log.info("%s %s fetched (%d/%d)", product, dt.datetime.utcfromtimestamp(t / 1000).date(), i + 1, len(times))

    time_coord = np.array(times, dtype="datetime64[ms]").astype("datetime64[ns]")
    if product == "fpar":
        center = time_coord + np.timedelta64(int(float(gcfg["fpar"]["composite_center_days"]) * 86400), "s")
    base_vars = sorted({k.rsplit("_", 1)[0] for k in layers})
    write_grids(product, cfg, base_vars, layers, time_coord, start, end,
                extra_coords={"time_center": ("time", center)} if product == "fpar" else None)


def write_grids(product, cfg, base_vars, layers, time_coord, start, end, extra_coords=None) -> None:
    """Write the fetch-grid data and every coarser grid in cfg['grids'] (block means)."""
    gcfg = cfg["gee"]
    fine_name = gcfg["fetch_grid"]
    fine = grid_from_config(cfg, fine_name)
    out_dir = REPO_ROOT / gcfg["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    for gname in cfg["grids"]:
        grid = grid_from_config(cfg, gname)
        factor = int(round(grid.res / fine.res))
        data = {}
        for v in base_vars:
            mean = np.stack(layers[f"{v}_mean"])
            count = np.stack(layers[f"{v}_count"])
            if factor > 1:
                mean, count = block_mean(mean, count, factor)
            data[v] = (("time", "lat", "lon"), mean.astype("f4"))
            data[f"{v}_count"] = (("time", "lat", "lon"), count.astype("f4"))
        coords = {"time": time_coord, "lat": grid.lat, "lon": grid.lon}
        if extra_coords:
            coords.update(extra_coords)
        ds = xr.Dataset(data, coords=coords)
        for v in base_vars:
            ds[f"{v}_count"].attrs["long_name"] = f"number of valid 500 m pixels (area-weighted) behind {v}"
        ds.attrs = {"source": gcfg[product]["collection"], "aggregated_in": "Google Earth Engine",
                    "fetch_grid_deg": fine.res, "resolution_deg": grid.res, "Conventions": "CF-1.8"}
        out = out_dir / f"{product}_{gname}_{start:%Y%m%d}_{end:%Y%m%d}.nc"
        ds.to_netcdf(out, encoding={v: {"zlib": True, "complevel": 4} for v in ds.data_vars})
        log.info("wrote %s", out.relative_to(REPO_ROOT))


def run_landcover(cfg: dict, year: int) -> None:
    gcfg = cfg["gee"]
    fine = grid_from_config(cfg, gcfg["fetch_grid"])
    img = (ee.ImageCollection(gcfg["landcover"]["collection"])
           .filterDate(f"{year}-01-01", f"{year + 1}-01-01").first())
    bands = ["Majority_Land_Cover_Type_1"] + [f"Land_Cover_Type_1_Percent_Class_{i}" for i in range(17)]
    # MCD12C1 is natively on the 0.05 deg CMG grid: fetch directly (nearest), no reduction.
    a = fetch(img.select(bands).reproject(crs="EPSG:4326",
                                          crsTransform=[fine.res, 0, fine.lon_min, 0, -fine.res, fine.lat_max]), fine)
    out_dir = REPO_ROOT / gcfg["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    pct = np.stack([a[f"Land_Cover_Type_1_Percent_Class_{i}"] for i in range(17)])
    for gname in cfg["grids"]:
        grid = grid_from_config(cfg, gname)
        factor = int(round(grid.res / fine.res))
        p = pct if factor == 1 else pct.reshape(17, grid.ny, factor, grid.nx, factor).mean(axis=(2, 4))
        ds = xr.Dataset({"percent": (("igbp_class", "lat", "lon"), p.astype("f4")),
                         "majority": (("lat", "lon"), np.argmax(p, axis=0).astype("i1"))},
                        coords={"igbp_class": np.arange(17), "lat": grid.lat, "lon": grid.lon})
        ds["percent"].attrs = {"long_name": "MCD12C1 IGBP (Type 1) class percentage of cell", "units": "%"}
        ds["majority"].attrs = {"long_name": "class with largest percentage (recomputed at this resolution)"}
        ds.attrs = {"source": gcfg["landcover"]["collection"], "year": year, "resolution_deg": grid.res}
        out = out_dir / f"landcover_mcd12c1_{year}_{gname}.nc"
        ds.to_netcdf(out)
        log.info("wrote %s", out.relative_to(REPO_ROOT))


def run_mask(cfg: dict) -> None:
    gcfg = cfg["gee"]
    fine = grid_from_config(cfg, gcfg["fetch_grid"])
    b = gcfg["boundaries"]
    fc = ee.FeatureCollection(b["collection"]).filter(ee.Filter.inList("country_na", b["countries"]))

    def mainland(feat):
        parts = ee.FeatureCollection(feat.geometry().geometries().map(
            lambda g: ee.Feature(ee.Geometry(g), {"area": ee.Geometry(g).area(1000)})))
        return ee.Feature(parts.sort("area", False).first().geometry())

    geom = ee.FeatureCollection(fc.map(mainland)).union(1000).geometry()
    # Rasterise at 1/20 of the fetch grid and average -> fraction of each cell inside the mainland.
    sub = fine.res / 20
    inside = ee.Image.constant(0).paint(ee.FeatureCollection([ee.Feature(geom)]), 1).rename("inside") \
        .reproject(crs="EPSG:4326", crsTransform=[sub, 0, fine.lon_min, 0, -sub, fine.lat_max])
    frac = inside.reduceResolution(ee.Reducer.mean(), maxPixels=int(gcfg["max_pixels"])) \
        .reproject(crs="EPSG:4326", crsTransform=[fine.res, 0, fine.lon_min, 0, -fine.res, fine.lat_max])
    a = fetch(frac, fine)["inside"]
    out_dir = REPO_ROOT / gcfg["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    for gname in cfg["grids"]:
        grid = grid_from_config(cfg, gname)
        factor = int(round(grid.res / fine.res))
        f = a if factor == 1 else a.reshape(grid.ny, factor, grid.nx, factor).mean(axis=(1, 3))
        ds = xr.Dataset({"land_fraction": (("lat", "lon"), f.astype("f4"))},
                        coords={"lat": grid.lat, "lon": grid.lon})
        ds["land_fraction"].attrs = {"long_name": "fraction of cell in mainland Spain + Portugal",
                                     "source": f"{b['collection']} {b['countries']}"}
        out = out_dir / f"mask_peninsula_{gname}.nc"
        ds.to_netcdf(out)
        log.info("wrote %s", out.relative_to(REPO_ROOT))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("product", choices=["fpar", "nbar", "landcover", "mask"])
    p.add_argument("--start", type=dt.date.fromisoformat)
    p.add_argument("--end", type=dt.date.fromisoformat)
    p.add_argument("--year", type=int)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    initialize(cfg["gee"]["project"])
    if args.product in ("fpar", "nbar"):
        run_timeseries(args.product, cfg, args.start, args.end)
    elif args.product == "landcover":
        run_landcover(cfg, args.year)
    else:
        run_mask(cfg)


if __name__ == "__main__":
    main()
