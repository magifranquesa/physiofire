"""Valid daily SIF/APAR values in the epoch window, per fire and cell group (report of the 2025 case).

Uses the same chain as physiofire.epoch.run (cut at ignition, fPAR composites cut before interpolation, validity
screening, spike filter) and counts the cell-days with a valid SIF/APAR value (before the trailing mean) on days
-window .. -1. Also counts the days with a valid trailing-mean anomaly (main series). Changes no parameter.

Usage: python -m physiofire.report_valid_days [--variable sif_apar_nopersist]
Output: {epoch.out_dir}/report2025_valid_days.csv
"""
from __future__ import annotations

import argparse
import logging

import numpy as np
import pandas as pd

from physiofire import anomalies, epoch
from physiofire.config import REPO_ROOT, load_config

log = logging.getLogger(__name__)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--grid", default="fine")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    ecfg, acfg, scfg = cfg["epoch"], cfg["anomalies"], cfg["sif_apar"]
    od = REPO_ROOT / ecfg["out_dir"]
    fires = pd.read_csv(REPO_ROOT / ecfg["selected_fires"], parse_dates=["ignition_date"], dtype={"fire_id": str})
    fires = fires[~fires["exclude"].astype(str).str.upper().eq("TRUE")]
    cells = pd.read_csv(od / "epoch_cells.csv", dtype={"fire_id": str})
    cells = cells[cells["grid"] == args.grid]
    inp = epoch.open_inputs(dict(cfg, epoch=dict(ecfg, optical_sensitivity=False)), args.grid)
    ref = inp["sif"]["sif"]
    days = ref.time.values.astype("datetime64[D]")
    w = int(ecfg["window_days"])
    rows = []
    for _, f in fires.iterrows():
        c = cells[cells["fire_id"] == f["fire_id"]].reset_index(drop=True)
        iy, ix = c["iy"].to_numpy(), c["ix"].to_numpy()
        ign = np.datetime64(f["ignition_date"].date(), "D")
        sif = epoch._extract(ref, ref, iy, ix, days)
        par = epoch._extract(inp["par"]["par"], ref, iy, ix, days)
        wt = epoch._extract(inp["sif"]["weight_sum"], ref, iy, ix, days)
        fp = inp["fpar"]
        comp = epoch._extract(fp["fpar"], ref, iy, ix, None)
        sel = (days >= ign - np.timedelta64(w, "D")) & (days < ign)
        for name, persist in (("sif_apar_nopersist", None), ("sif_apar", ecfg.get("fpar_persist_days"))):
            ratio, fpar_d = epoch.sif_apar_causal(sif, par, comp, fp.time.values, fp.time_center.values, days, ign,
                                                  int(scfg["fpar_composite_days"]), float(scfg["fpar_max_gap_days"]),
                                                  persist)
            m = epoch.screening_mask(scfg, fpar_d, par, wt)
            res = anomalies.compute(ratio, days, acfg, cutoff=np.full(len(c), ign), valid=m)
            x = res["x"][sel]
            tr = res[ecfg["main_series"]][sel]
            for grp in ("burned", "control"):
                k = (c["group"] == grp).to_numpy()
                rows.append({"fire_id": f["fire_id"], "variable": name, "group": grp, "n_cells": int(k.sum()),
                             "sif_retrieved": int(np.isfinite(sif[sel][:, k]).sum()),
                             "valid_cell_days": int(np.isfinite(x[:, k]).sum()),
                             "possible_cell_days": int(k.sum() * w),
                             "valid_trailing_days": int(np.isfinite(tr[:, k]).sum())})
    df = pd.DataFrame(rows)
    df["valid_frac"] = df["valid_cell_days"] / df["possible_cell_days"]
    df = df.merge(fires[["fire_id", "name", "country", "fuel_class"]], on="fire_id", how="left")
    df.to_csv(od / "report2025_valid_days.csv", index=False)
    pd.set_option("display.width", 220)
    v = df[df.variable == "sif_apar_nopersist"].pivot_table(
        index=["fire_id", "name", "fuel_class"], columns="group",
        values=["n_cells", "valid_cell_days", "valid_frac"]).round(2)
    print(v.to_string())
    print(df.groupby(["variable", "group"])[["sif_retrieved", "valid_cell_days", "possible_cell_days"]].sum())


if __name__ == "__main__":
    main()
