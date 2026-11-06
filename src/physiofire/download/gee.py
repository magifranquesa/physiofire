"""Aggregate MODIS products in Google Earth Engine to the project grid and fetch them as NetCDF.

GEE reduces the 500 m data to the fetch grid (0.05 deg by default) with an area-weighted mean of the
valid pixels and their count; coarser grids (0.25 deg) are built locally by count-weighted block
averaging (`block_mean`), so both scales are consistent.

Products:
    fpar        MCD15A3H Fpar, main-algorithm retrievals only (4-day composites); MAIN fPAR
    fpar_viirs  VNP15A2H (S-NPP, collection 2) Fpar, main algorithm (8-day composites); SENSITIVITY fPAR.
                NOTE: SCF_QC bits and asset scaling differ from MCD15A3H (see config).
    check       re-check an existing file against the plausible median ranges
    nbar        MCD43A4 red/NIR/blue NBAR, mandatory quality <= max (daily); NDVI/EVI computed later
    landcover   MCD12C1 IGBP (Type 1) class percentages, majority class (yearly, native 0.05 deg)
    mask        fraction of each cell inside mainland Spain + Portugal (LSIB boundaries)
    shortwave   ERA5-Land daily downward shortwave (W m-2), bilinear; PROVISIONAL PAR source
    shortwave_monthly_1deg  monthly ERA5-Land shortwave on the 1 deg CERES grid (CERES jump test)
    burned      MCD64A1 burned fraction (only to keep generic QC points out of burned cells)
    burn_history  yearly MCD64A1 burned fraction and first burn day per cell (masks, 5-year criterion)
    mod09ga / myd09ga  daily Terra / Aqua surface reflectance (not BRDF-adjusted), screened; daily NDVI/EVI
                competitor (epoch rule 2)

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
NODATA = -9999.0  # explicit no-data flag (computePixels returns masked pixels as 0)


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

def fpar_images(gcfg: dict, start: dt.date, end: dt.date, product: str = "fpar") -> ee.ImageCollection:
    """fPAR, main-algorithm retrievals only. Bit position of SCF_QC and asset scaling differ between
    MCD15A3H (bits 5-7, integer 0-100) and NASA/VIIRS/002/VNP15A2H (bits 0-2, pre-scaled 0-1): see config."""
    f = gcfg[product]

    def prep(img):
        scf = img.select("FparLai_QC").rightShift(int(f["scf_bit_start"])).bitwiseAnd(7)
        fpar = img.select("Fpar")
        ok = scf.lte(int(f["scf_qc_max"])).And(fpar.lte(float(f["valid_max_raw"])))
        extra = img.select("FparExtra_QC")
        for q in f.get("extra_qc", []):                      # clouds, cirrus, cloud shadow
            ok = ok.And(_bits(extra, int(q["bit"]), int(q["nbits"])).lte(int(q["max"])))
        laiqc = img.select("FparLai_QC")
        for q in f.get("lai_qc_exclude", []):                # e.g. MOD09 cloud state (MODIS bits 3-4)
            field = _bits(laiqc, int(q["bit"]), int(q["nbits"]))
            for v in q["exclude"]:
                ok = ok.And(field.neq(int(v)))
        out = fpar.multiply(float(f["scale"])).updateMask(ok).rename("fpar")
        a = f.get("aerosol_flag")
        if a:   # per-pixel aerosol flag (0/1) on the retained pixels -> per-cell fraction (smoke indicator)
            aer = _bits(extra, int(a["bit"]), int(a["nbits"])).gte(int(a["min"])).updateMask(ok).rename("aerosol")
            out = out.addBands(aer)
        return out.copyProperties(img, ["system:time_start"])

    return ee.ImageCollection(f["collection"]).filterDate(str(start), str(end + dt.timedelta(days=1))).map(prep)


class ImplausibleValues(RuntimeError):
    """Raised when the median of a fetched image is outside the plausible range (likely a scaling error)."""


def check_plausible(product: str, date, means: dict[str, np.ndarray], counts: dict[str, np.ndarray],
                    ranges: dict) -> dict[str, float]:
    """Check the median over valid cells of every variable with a configured range. Returns the medians.
    Raises ImplausibleValues naming product, date and variable if a median falls outside its range."""
    medians = {}
    for var, (lo, hi) in ranges.items():
        if var not in means:
            continue
        ok = (counts[var] > 0) & np.isfinite(means[var])
        if not ok.any():
            log.warning("%s %s: no valid cells for %s, plausibility check skipped", product, date, var)
            continue
        med = float(np.median(means[var][ok]))
        medians[var] = med
        if not (lo <= med <= hi):
            raise ImplausibleValues(f"{product} {date}: median {var} = {med:.4g} outside plausible range "
                                    f"[{lo}, {hi}] (check asset scaling)")
    return medians


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


def _bits(img: ee.Image, start: int, n: int) -> ee.Image:
    return img.rightShift(start).bitwiseAnd((1 << n) - 1)


def sr_images(gcfg: dict, product: str, start: dt.date, end: dt.date) -> ee.ImageCollection:
    """Daily MOD09GA/MYD09GA red/NIR/blue surface reflectance (not BRDF-adjusted), screened for clouds,
    shadows, cirrus, adjacency, snow, high aerosol, water, poor quality and view zenith (see config)."""
    vza_max = float(gcfg["sr_max_sensor_zenith"])

    def prep(img):
        st = img.select("state_1km")
        clear = (_bits(st, 0, 2).eq(0).And(_bits(st, 2, 1).eq(0)).And(_bits(st, 3, 3).eq(1))
                 .And(_bits(st, 6, 2).neq(3)).And(_bits(st, 8, 2).eq(0)).And(_bits(st, 10, 1).eq(0))
                 .And(_bits(st, 13, 1).eq(0)).And(_bits(st, 15, 1).eq(0)))
        good = _bits(img.select("QC_500m"), 0, 2).lte(1)
        vza = img.select("SensorZenith").multiply(0.01).lte(vza_max)
        ok = clear.And(good).And(vza)
        bands = [img.select(b).multiply(0.0001).updateMask(ok).rename(k) for k, b in gcfg["sr_bands"].items()]
        return ee.Image(bands).copyProperties(img, ["system:time_start"])

    return (ee.ImageCollection(gcfg[product]["collection"])
            .filterDate(str(start), str(end + dt.timedelta(days=1))).map(prep))


def _collection_dates(col: ee.ImageCollection) -> list[int]:
    return col.aggregate_array("system:time_start").getInfo()


def run_timeseries(product: str, cfg: dict, start: dt.date, end: dt.date) -> None:
    gcfg = cfg["gee"]
    fine = grid_from_config(cfg, gcfg["fetch_grid"])
    if product in ("fpar", "fpar_viirs"):
        col = fpar_images(gcfg, start, end, product)
    elif product == "nbar":
        col = nbar_images(gcfg, start, end)
    else:
        col = sr_images(gcfg, product, start, end)
    times = _collection_dates(col)
    imgs = col.toList(len(times))
    log.info("%s: %d images", product, len(times))

    layers: dict[str, list] = {}
    ranges = gcfg.get("plausible_median", {})
    for i, t in enumerate(times):
        img = _to_grid(ee.Image(imgs.get(i)), fine, int(gcfg["max_pixels"]))
        a = fetch(img, fine)
        day = dt.datetime.utcfromtimestamp(t / 1000).date()
        base = {k.rsplit("_", 1)[0] for k in a}
        med = check_plausible(product, day, {v: a[f"{v}_mean"] for v in base}, {v: a[f"{v}_count"] for v in base},
                              ranges)
        for k, v in a.items():
            layers.setdefault(k, []).append(v)
        log.info("%s %s fetched (%d/%d) medians %s", product, day, i + 1, len(times),
                 {k: round(v, 3) for k, v in med.items()})

    time_coord = np.array(times, dtype="datetime64[ms]").astype("datetime64[ns]")
    extra = None
    if product in ("fpar", "fpar_viirs"):
        center = time_coord + np.timedelta64(int(float(gcfg[product]["composite_center_days"]) * 86400), "s")
        extra = {"time_center": ("time", center)}
    base_vars = sorted({k.rsplit("_", 1)[0] for k in layers})
    write_grids(product, cfg, base_vars, layers, time_coord, start, end, extra_coords=extra)


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
            count = np.nan_to_num(np.stack(layers[f"{v}_count"]), nan=0.0)
            mean = np.where(count > 0, mean, np.nan)   # masked cells come back as 0, not as no-data
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
        pc = gcfg[product]
        ds.attrs = {"source": pc["collection"], "gee_asset": pc["collection"], "aggregated_in": "Google Earth Engine",
                    "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                    "fetch_grid_deg": fine.res, "resolution_deg": grid.res, "Conventions": "CF-1.8"}
        if "scale" in pc:
            ds.attrs.update(scale_factor_applied=float(pc["scale"]), valid_max_asset_units=float(pc["valid_max_raw"]),
                            asset_prescaled=int(float(pc["scale"]) == 1.0),
                            scf_qc_bits=f"{pc['scf_bit_start']}-{int(pc['scf_bit_start']) + 2} <= {pc['scf_qc_max']}",
                            extra_qc="; ".join(f"{q['name']}: bits {q['bit']}+{q['nbits']} <= {q['max']}"
                                               for q in pc.get("extra_qc", [])) or "none",
                            lai_qc_exclude="; ".join(f"{q['name']}: bits {q['bit']}+{q['nbits']} not in {q['exclude']}"
                                                     for q in pc.get("lai_qc_exclude", [])) or "none")
            if "aerosol" in ds:
                a = pc["aerosol_flag"]
                ds["aerosol"].attrs = {"long_name": "fraction of retained pixels with aerosol flag "
                                       f"(FparExtra_QC bits {a['bit']}+{a['nbits']} >= {a['min']}); NOT used as mask",
                                       "units": "1"}
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


def _reproject_bilinear(img: ee.Image, grid: Grid) -> ee.Image:
    """Bilinear resampling to `grid` (for sources coarser than the grid, e.g. ERA5-Land 0.1 deg)."""
    return img.resample("bilinear").reproject(
        crs="EPSG:4326", crsTransform=[grid.res, 0, grid.lon_min, 0, -grid.res, grid.lat_max])


def run_shortwave(cfg: dict, start: dt.date, end: dt.date) -> None:
    """ERA5-Land daily downward shortwave (daily mean W m-2), bilinear to the fetch grid, block means coarser.
    PROVISIONAL PAR source: PAR = par_fraction x SW is applied later (indices step)."""
    gcfg = cfg["gee"]
    e = gcfg["era5land"]
    fine = grid_from_config(cfg, gcfg["fetch_grid"])
    col = (ee.ImageCollection(e["collection"]).filterDate(str(start), str(end + dt.timedelta(days=1)))
           .select(e["sw_band"]))
    times = _collection_dates(col)
    imgs = col.toList(len(times))
    layers: dict[str, list] = {"sw_mean": [], "sw_count": []}
    for i, t in enumerate(times):
        img = ee.Image(imgs.get(i)).divide(86400).rename("sw")  # J m-2 day-1 -> W m-2
        # Masked pixels come back as 0 from computePixels: flag them explicitly.
        a = fetch(_reproject_bilinear(img, fine).unmask(NODATA), fine)["sw"]
        a[a <= NODATA + 1] = np.nan
        layers["sw_mean"].append(a)
        layers["sw_count"].append(np.isfinite(a).astype("f8"))
        log.info("sw %s fetched (%d/%d)", dt.datetime.utcfromtimestamp(t / 1000).date(), i + 1, len(times))
    time_coord = np.array(times, dtype="datetime64[ms]").astype("datetime64[ns]")
    gcfg = dict(gcfg, shortwave={"collection": f"{e['collection']} {e['sw_band']}"})
    write_grids("shortwave", dict(cfg, gee=gcfg), ["sw"], layers, time_coord, start, end)


def run_shortwave_monthly_1deg(cfg: dict, start: dt.date, end: dt.date) -> None:
    """Monthly mean ERA5-Land downward shortwave (W m-2) on the 1 deg CERES grid, for the CERES
    discontinuity test. Area-weighted mean of the 0.1 deg ERA5-Land cells in each 1 deg cell."""
    gcfg = cfg["gee"]
    e = gcfg["era5land"]
    r = cfg["region"]
    res = float(cfg["par"]["ceres_jump_test_grid_deg"])
    g1 = Grid(np.floor(r["lon_min"]), np.floor(r["lat_min"]), np.ceil(r["lon_max"]), np.ceil(r["lat_max"]), res)
    months = []
    m = dt.date(start.year, start.month, 1)
    while m <= end:
        months.append(m)
        m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    out, cnt = [], []
    for i, m0 in enumerate(months):
        m1 = dt.date(m0.year + (m0.month == 12), m0.month % 12 + 1, 1)
        mcol = ee.ImageCollection(e["collection"]).filterDate(str(m0), str(m1)).select(e["sw_band"])
        native = mcol.first().projection()  # composites lose the default projection
        img = mcol.mean().divide(86400).rename("sw").setDefaultProjection(native)
        a = fetch(_to_grid(img, g1, int(gcfg["max_pixels"])), g1)
        out.append(np.where(a["sw_count"] > 0, a["sw_mean"], np.nan))
        cnt.append(a["sw_count"])
        log.info("sw monthly %s fetched (%d/%d)", m0, i + 1, len(months))
    ds = xr.Dataset({"sw": (("time", "lat", "lon"), np.stack(out).astype("f4")),
                     "sw_count": (("time", "lat", "lon"), np.stack(cnt).astype("f4"))},
                    coords={"time": np.array(months, dtype="datetime64[ns]"), "lat": g1.lat, "lon": g1.lon})
    ds["sw"].attrs = {"long_name": "monthly mean ERA5-Land surface downward shortwave", "units": "W m-2"}
    ds.attrs = {"source": f"{e['collection']} {e['sw_band']}", "resolution_deg": res,
                "purpose": "CERES SYN1deg Ed4B discontinuity test (April 2022)"}
    out_dir = REPO_ROOT / gcfg["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    f = out_dir / f"shortwave_monthly_1deg_{start:%Y%m}_{end:%Y%m}.nc"
    ds.to_netcdf(f)
    log.info("wrote %s", f.relative_to(REPO_ROOT))


def run_burned(cfg: dict, start: dt.date, end: dt.date) -> None:
    """Fraction of each cell burned between start and end (MCD64A1 BurnDate > 0)."""
    gcfg = cfg["gee"]
    fine = grid_from_config(cfg, gcfg["fetch_grid"])
    col = ee.ImageCollection(gcfg["burned"]["collection"]).filterDate(str(start), str(end + dt.timedelta(days=1)))
    native = col.first().projection()  # composites lose the default projection
    burned = col.select("BurnDate").max().gt(0).unmask(0).rename("burned").setDefaultProjection(native)
    a = fetch(_to_grid(burned, fine, int(gcfg["max_pixels"])), fine)["burned_mean"]
    a = np.nan_to_num(a, nan=0.0)
    out_dir = REPO_ROOT / gcfg["out_dir"]
    for gname in cfg["grids"]:
        grid = grid_from_config(cfg, gname)
        factor = int(round(grid.res / fine.res))
        f = a if factor == 1 else a.reshape(grid.ny, factor, grid.nx, factor).mean(axis=(1, 3))
        ds = xr.Dataset({"burned_fraction": (("lat", "lon"), f.astype("f4"))},
                        coords={"lat": grid.lat, "lon": grid.lon})
        ds.attrs = {"source": gcfg["burned"]["collection"], "start": str(start), "end": str(end),
                    "purpose": "exclude burned cells from generic QC points"}
        out = out_dir / f"burned_{gname}_{start:%Y%m%d}_{end:%Y%m%d}.nc"
        ds.to_netcdf(out)
        log.info("wrote %s", out.relative_to(REPO_ROOT))


def check_file(path: str, ranges: dict) -> None:
    """Re-run the plausibility check on every time step of an existing fetch-grid file."""
    ds = xr.open_dataset(path)
    product = ds.attrs.get("source", path)
    base = [v for v in ds.data_vars if f"{v}_count" in ds]
    for t in ds.time.values:
        s = ds.sel(time=t)
        check_plausible(product, str(t)[:10], {v: s[v].values for v in base},
                        {v: s[f"{v}_count"].values for v in base}, ranges)
    log.info("%s: all %d time steps within plausible ranges", path, ds.sizes["time"])


def run_burn_history(cfg: dict, y0: int, y1: int) -> None:
    """Yearly MCD64A1 burn history per cell: burned fraction and first burn date (day of year).
    Used for the climatology/control masks (burned fraction above a threshold) and for the
    'no burn in the previous 5 years' selection criterion."""
    gcfg = cfg["gee"]
    fine = grid_from_config(cfg, gcfg["fetch_grid"])
    mx = int(gcfg["max_pixels"])
    tr = [fine.res, 0, fine.lon_min, 0, -fine.res, fine.lat_max]
    years = list(range(y0, y1 + 1))
    frac, first = [], []
    for y in years:
        col = ee.ImageCollection(gcfg["burned"]["collection"]).filterDate(f"{y}-01-01", f"{y + 1}-01-01")
        native = col.first().projection()
        bd = col.select("BurnDate")
        burned = bd.max().gt(0).unmask(0).rename("burned").setDefaultProjection(native)
        doy = bd.map(lambda i: i.updateMask(i.gt(0))).min().rename("doy").setDefaultProjection(native)
        f = fetch(burned.reduceResolution(ee.Reducer.mean(), maxPixels=mx).reproject(crs="EPSG:4326", crsTransform=tr),
                  fine)["burned"]
        d = fetch(doy.reduceResolution(ee.Reducer.min(), maxPixels=mx).reproject(crs="EPSG:4326", crsTransform=tr)
                  .unmask(0), fine)["doy"]
        frac.append(np.nan_to_num(f, nan=0.0))
        first.append(np.where(d > 0, d, np.nan))
        log.info("burn history %d fetched", y)
    frac, first = np.stack(frac), np.stack(first)
    out_dir = REPO_ROOT / gcfg["out_dir"]
    for gname in cfg["grids"]:
        grid = grid_from_config(cfg, gname)
        k = int(round(grid.res / fine.res))
        if k == 1:
            fr, fd = frac, first
        else:
            shp = (len(years), grid.ny, k, grid.nx, k)
            fr = frac.reshape(shp).mean(axis=(2, 4))
            with np.errstate(all="ignore"):
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    fd = np.nanmin(first.reshape(shp), axis=(2, 4))
        ds = xr.Dataset({"burned_fraction": (("year", "lat", "lon"), fr.astype("f4")),
                         "first_burn_doy": (("year", "lat", "lon"), fd.astype("f4"))},
                        coords={"year": years, "lat": grid.lat, "lon": grid.lon})
        ds["burned_fraction"].attrs = {"long_name": "fraction of cell burned during the year (MCD64A1)"}
        ds["first_burn_doy"].attrs = {"long_name": "earliest MCD64A1 burn day of year in the cell (NaN = none)"}
        ds.attrs = {"source": gcfg["burned"]["collection"], "resolution_deg": grid.res}
        out = out_dir / f"burn_history_{gname}_{y0}_{y1}.nc"
        ds.to_netcdf(out)
        log.info("wrote %s", out.relative_to(REPO_ROOT))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("product", choices=["fpar", "fpar_viirs", "nbar", "mod09ga", "myd09ga", "landcover", "mask",
                                       "shortwave", "shortwave_monthly_1deg", "burned", "burn_history", "check"])
    p.add_argument("--file", help="for 'check': NetCDF written by this module to re-check against plausible ranges")
    p.add_argument("--start", type=dt.date.fromisoformat)
    p.add_argument("--end", type=dt.date.fromisoformat)
    p.add_argument("--year", type=int)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    if args.product == "check":
        check_file(args.file, cfg["gee"].get("plausible_median", {}))
        return
    initialize(cfg["gee"]["project"])
    if args.product in ("fpar", "fpar_viirs", "nbar", "mod09ga", "myd09ga"):
        run_timeseries(args.product, cfg, args.start, args.end)
    elif args.product == "burn_history":
        y0, y1 = cfg["gee"]["burn_history_years"]
        run_burn_history(cfg, int(y0), int(y1))
    elif args.product == "landcover":
        run_landcover(cfg, args.year)
    elif args.product == "shortwave":
        run_shortwave(cfg, args.start, args.end)
    elif args.product == "shortwave_monthly_1deg":
        run_shortwave_monthly_1deg(cfg, args.start, args.end)
    elif args.product == "burned":
        run_burned(cfg, args.start, args.end)
    else:
        run_mask(cfg)


if __name__ == "__main__":
    main()
