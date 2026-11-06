"""Resumable TROPOSIF L2B downloader: download each daily global file, subset to the region, delete the original.

Each day is processed independently and recorded in a manifest (CSV). Days already marked
``done`` are skipped, so the script can be stopped and relaunched at any time.

Usage:
    python -m physiofire.download.troposif --start 2022-07-01 --end 2022-07-31
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import logging
import time
from pathlib import Path

import netCDF4
import numpy as np
import requests

from physiofire.config import REPO_ROOT, load_config

log = logging.getLogger("troposif")

MANIFEST_FIELDS = ["date", "item_id", "status", "download_mb", "n_pixels_global", "n_pixels_region",
                   "output", "seconds", "processed_utc", "message"]


# --------------------------------------------------------------------------- STAC

def find_item(stac_url: str, collection: str, day: dt.date) -> dict | None:
    """Return the L2B item whose sensing start falls on `day` (UTC), or None if missing."""
    body = {
        "collections": [collection],
        "datetime": f"{day - dt.timedelta(days=1)}T12:00:00Z/{day + dt.timedelta(days=1)}T12:00:00Z",
        "limit": 10,
    }
    r = requests.post(f"{stac_url}/search", json=body, timeout=60)
    r.raise_for_status()
    items = [f for f in r.json().get("features", [])
             if (f["properties"].get("start_datetime") or "")[:10] == day.isoformat()]
    if len(items) > 1:
        # Several processings of the same day: keep the most recent processing time (last id field).
        items.sort(key=lambda f: f["id"].split("_")[-1])
    return items[-1] if items else None


def download(url: str, dest: Path, expected_size: int | None, retries: int) -> float:
    """Stream `url` to `dest`; return size in MB. Checks size against the STAC `file:size`."""
    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=(30, 300)) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                        f.write(chunk)
            size = dest.stat().st_size
            if expected_size and size != expected_size:
                raise IOError(f"size mismatch: {size} != {expected_size}")
            return size / 1e6
        except Exception as e:  # noqa: BLE001 - retry on any network/IO error
            log.warning("download attempt %d/%d failed: %s", attempt, retries, e)
            dest.unlink(missing_ok=True)
            if attempt == retries:
                raise
            time.sleep(10 * attempt)
    raise RuntimeError("unreachable")


# --------------------------------------------------------------------------- subset

def _iter_vars(group: netCDF4.Group, path: str = ""):
    """Yield (group_path, variable) for every variable in `group` and its subgroups."""
    for v in group.variables.values():
        yield path, v
    for name, sub in group.groups.items():
        yield from _iter_vars(sub, f"{path}/{name}")


def _copy_group_attrs(src: netCDF4.Group, dst: netCDF4.Dataset, prefix: str = "") -> None:
    for name in src.ncattrs():
        val = src.getncattr(name)
        key = f"{prefix}{name}".replace(" ", "_").replace("/", "_")
        try:
            dst.setncattr(key, val)
        except Exception:  # noqa: BLE001 - some attribute types cannot be written as-is
            dst.setncattr(key, str(val))
    for gname, sub in src.groups.items():
        _copy_group_attrs(sub, dst, f"{prefix}{gname}__")


def subset_l2b(src_path: Path, dst_path: Path, bbox: tuple[float, float, float, float]) -> tuple[int, int]:
    """Write the pixels of `src_path` whose centre lies in `bbox` (lon_min, lat_min, lon_max, lat_max)
    to a flat NetCDF4 file. All variables along `n_elem` are kept, with their original names and
    attributes; the source group is stored in the `source_group` attribute.
    Returns (n_pixels_global, n_pixels_region)."""
    lon_min, lat_min, lon_max, lat_max = bbox
    tmp = dst_path.with_suffix(".nc.part")
    with netCDF4.Dataset(src_path) as src:
        prod = src["PRODUCT"]
        lat = prod["latitude"][:]
        lon = prod["longitude"][:]
        sel = np.where((lat >= lat_min) & (lat <= lat_max) & (lon >= lon_min) & (lon <= lon_max))[0]
        n_global = lat.size

        with netCDF4.Dataset(tmp, "w", format="NETCDF4") as dst:
            _copy_group_attrs(src, dst)
            dst.setncattr("physiofire_source_file", src_path.name)
            dst.setncattr("physiofire_subset_bbox", np.array(bbox, dtype="f8"))
            dst.createDimension("n_elem", sel.size)
            for gpath, v in _iter_vars(src):
                if not v.dimensions or v.dimensions[0] != "n_elem":
                    # Variables not along n_elem (e.g. WVL_RFL): copy whole.
                    for d, n in zip(v.dimensions, v.shape):
                        if d not in dst.dimensions:
                            dst.createDimension(d, n)
                    data = v[:]
                else:
                    for d, n in zip(v.dimensions[1:], v.shape[1:]):
                        if d not in dst.dimensions:
                            dst.createDimension(d, n)
                    data = v[sel, ...] if sel.size else np.empty((0,) + v.shape[1:], v.dtype)
                if v.name in dst.variables:
                    raise ValueError(f"duplicate variable name across groups: {v.name}")
                fill = v.getncattr("_FillValue") if "_FillValue" in v.ncattrs() else None
                out = dst.createVariable(v.name, v.dtype, v.dimensions, zlib=True, complevel=4,
                                         fill_value=fill)
                for a in v.ncattrs():
                    if a != "_FillValue":
                        out.setncattr(a, v.getncattr(a))
                out.setncattr("source_group", gpath or "/")
                out[...] = data
    tmp.replace(dst_path)
    return n_global, int(sel.size)


# --------------------------------------------------------------------------- manifest

def read_manifest(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {row["date"]: row for row in csv.DictReader(f)}


def append_manifest(path: Path, row: dict) -> None:
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


# --------------------------------------------------------------------------- main

def process_day(day: dt.date, cfg: dict, tcfg: dict, bbox, out_dir: Path, tmp_dir: Path) -> dict:
    t0 = time.time()
    row = {"date": day.isoformat(), "processed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    item = find_item(tcfg["stac_url"], tcfg["collection"], day)
    if item is None:
        return row | {"status": "missing", "message": "no L2B item in STAC", "seconds": f"{time.time() - t0:.0f}"}
    asset = item["assets"]["product"]
    raw = tmp_dir / f"{item['id']}.nc"
    out = out_dir / f"{day.year}" / f"troposif_l2b_{cfg['region']['name']}_{day:%Y%m%d}.nc"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        mb = download(asset["href"], raw, asset.get("file:size"), int(tcfg["max_retries"]))
        n_glob, n_reg = subset_l2b(raw, out, bbox)
    finally:
        raw.unlink(missing_ok=True)  # never keep the global original
    return row | {"item_id": item["id"], "status": "done", "download_mb": f"{mb:.1f}",
                  "n_pixels_global": n_glob, "n_pixels_region": n_reg,
                  "output": out.relative_to(REPO_ROOT).as_posix(), "seconds": f"{time.time() - t0:.0f}",
                  "message": ""}


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", required=True, type=dt.date.fromisoformat)
    p.add_argument("--end", required=True, type=dt.date.fromisoformat)
    p.add_argument("--retry-missing", action="store_true", help="re-check days marked 'missing'")
    args = p.parse_args(argv)

    cfg = load_config()
    tcfg = cfg["troposif"]
    r, b = cfg["region"], float(tcfg["subset_buffer_deg"])
    bbox = (r["lon_min"] - b, r["lat_min"] - b, r["lon_max"] + b, r["lat_max"] + b)
    out_dir, tmp_dir, manifest = (REPO_ROOT / tcfg[k] for k in ("out_dir", "tmp_dir", "manifest"))
    for d in (out_dir, tmp_dir, manifest.parent):
        d.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(),
                                  logging.FileHandler(manifest.parent / "download.log", encoding="utf-8")])

    skip = {"done"} | (set() if args.retry_missing else {"missing"})
    day = args.start
    while day <= args.end:
        status = read_manifest(manifest).get(day.isoformat(), {}).get("status")
        if status in skip:
            log.info("%s already %s, skipping", day, status)
        else:
            try:
                row = process_day(day, cfg, tcfg, bbox, out_dir, tmp_dir)
            except Exception as e:  # noqa: BLE001 - record failure and continue with the next day
                log.exception("%s failed", day)
                row = {"date": day.isoformat(), "status": "failed", "message": str(e)[:300],
                       "processed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
            append_manifest(manifest, row)
            log.info("%s %s %s MB, %s/%s pixels, %s s", day, row.get("status"), row.get("download_mb"),
                     row.get("n_pixels_region"), row.get("n_pixels_global"), row.get("seconds"))
        day += dt.timedelta(days=1)


if __name__ == "__main__":
    main()
