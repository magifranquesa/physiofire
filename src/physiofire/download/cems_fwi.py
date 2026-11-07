"""CEMS fire danger indices historical reanalysis (EWDS dataset cems-fire-historical-v1; ERA5-based, EFFIS
operational reference) for the study region, one NetCDF per month.

The EWDS uses the same personal access token as the CDS: the key is read from ~/.cdsapirc and the URL from
fwi.cems.url (the URL in ~/.cdsapirc points to the CDS). The dataset licence must have been accepted once on the
EWDS web page with the same account.

Usage: python -m physiofire.download.cems_fwi --year 2025 --months 8
Output: {fwi.cems.raw_dir}/cems_fwi_YYYYMM.nc
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import cdsapi

from physiofire.config import REPO_ROOT, load_config

log = logging.getLogger("cems_fwi")


def _key() -> str:
    rc = Path.home() / ".cdsapirc"
    for line in rc.read_text().splitlines():
        if line.strip().startswith("key:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("no 'key:' line in ~/.cdsapirc")


def run(cfg: dict, year: int, months: list[int], variables: list[str]) -> None:
    c = cfg["fwi"]["cems"]
    r = cfg["region"]
    out_dir = REPO_ROOT / c["raw_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    client = cdsapi.Client(url=c["url"], key=_key(), quiet=True)
    area = [r["lat_max"] + 0.25, r["lon_min"] - 0.25, r["lat_min"] - 0.25, r["lon_max"] + 0.25]  # N, W, S, E
    for m in months:
        f = out_dir / f"cems_fwi_{year}{m:02d}.nc"
        if f.exists():
            log.info("%s exists, skipped", f.name)
            continue
        last = None
        for dtype in c["dataset_type"]:
            req = {"product_type": [c["product_type"]], "variable": variables, "dataset_type": dtype,
                   "system_version": [c["system_version"]], "year": [str(year)], "month": [f"{m:02d}"],
                   "day": [f"{d:02d}" for d in range(1, 32)], "grid": c["grid"], "data_format": "netcdf",
                   "area": area}
            try:
                client.retrieve(c["dataset"], req, str(f))
                log.info("wrote %s (%s)", f.relative_to(REPO_ROOT), dtype)
                break
            except Exception as e:  # noqa: BLE001 - try the next dataset type
                last = e
                log.warning("%s %d-%02d failed: %s", dtype, year, m, str(e)[:300])
        else:
            raise RuntimeError(f"CEMS FWI {year}-{m:02d} not retrieved") from last


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--months", type=int, nargs="+", required=True)
    p.add_argument("--variables", nargs="+", default=["fire_weather_index", "fine_fuel_moisture_code",
                                                      "duff_moisture_code", "drought_code"])
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(load_config(), args.year, args.months, args.variables)


if __name__ == "__main__":
    main()
