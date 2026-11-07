"""Superposed-epoch series for the simplified 2025 analysis.

For each selected fire, the burned and control cells chosen in R (R/epoch_cells.R) are extracted from the daily
grids, every series is masked from the fire's ignition date (day 0, inclusive) BEFORE any statistic, anomalies are
computed with `anomalies.compute` (trend, seasonal cycle, spike filter and trailing windows on pre-ignition data
only) and standardised by each cell's own SD over the days before the epoch window. The result is a long table
(fire, cell, group, variable, series, day relative to ignition, standardised anomaly) for the statistics and figures
in R (R/epoch_analysis.R).

Rules enforced here (CLAUDE.md, epoch analysis):
- the same cut-off (ignition) for burned and control cells of a fire;
- SIF/APAR uses fPAR composites cut at the ignition date BEFORE daily interpolation (indices.composites_to_daily_cut),
  with at most `epoch.fpar_persist_days` of persistence (None = no persistence, the reference run);
- no fPAR smoothing, no spatial smoothing, backward (trailing) windows only.
"""

from __future__ import annotations

import argparse
import logging

import numpy as np
import pandas as pd
import xarray as xr

from physiofire import anomalies, indices

log = logging.getLogger(__name__)


def standardize(a: np.ndarray, days: np.ndarray, ref_end: np.datetime64) -> np.ndarray:
    """Divide each cell's anomaly series (time, ncell) by its SD over the days before `ref_end` (exclusive)."""
    ref = days.astype("datetime64[D]") < np.datetime64(ref_end, "D")
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            sd = np.nanstd(a[ref], axis=0)
    sd = np.where(sd > 0, sd, np.nan)
    return a / sd[None, :]


def sif_apar_causal(sif: np.ndarray, par: np.ndarray, fpar_comp: np.ndarray, starts: np.ndarray,
                    centers: np.ndarray, days: np.ndarray, cutoff: np.datetime64, period_days: int,
                    max_gap_days: float, persist_days: float | None) -> tuple[np.ndarray, np.ndarray]:
    """SIF/APAR for (time, ncell) cell series with fPAR composites (ncomp, ncell) cut at `cutoff` before the daily
    interpolation. Returns (sif_apar, daily fpar)."""
    ncell = sif.shape[1]
    da = xr.DataArray(fpar_comp[:, :, None], dims=("time", "cell", "one"))
    cut = np.full((ncell, 1), np.datetime64(cutoff, "D"))
    fpar = indices.composites_to_daily_cut(da, starts, centers, days.astype("datetime64[ns]"), cut, period_days,
                                           max_gap_days, persist_days).values[:, :, 0]
    with np.errstate(all="ignore"):
        ratio = indices.sif_apar(sif, par, fpar)
    return ratio, fpar


def fire_series(variables: dict[str, np.ndarray], days: np.ndarray, ignition: np.datetime64, acfg: dict,
                ecfg: dict, valid: dict[str, np.ndarray] | None = None) -> dict[str, dict[str, np.ndarray]]:
    """Anomaly series of each variable for the cells of one fire, masked from `ignition` (inclusive).
    variables: name -> (time, ncell) daily values (already causal, e.g. SIF/APAR from `sif_apar_causal`).
    Returns name -> series name -> (window_days, ncell) standardised anomalies for days -window .. -1."""
    ign = np.datetime64(ignition, "D")
    w = int(ecfg["window_days"])
    win_start = ign - np.timedelta64(w, "D")
    d = days.astype("datetime64[D]")
    sel = (d >= win_start) & (d < ign)
    if sel.sum() != w:
        raise ValueError(f"daily series do not cover the {w}-day window before {ign}")
    te = ecfg.get("loess_trend_end_day")
    out = {}
    for name, x in variables.items():
        cutoff = np.full(x.shape[1], ign)
        trend_end = None if te is None else np.full(x.shape[1], ign + np.timedelta64(int(te), "D"))
        res = anomalies.compute(x, d, acfg, cutoff=cutoff, valid=None if valid is None else valid.get(name),
                                trend_end=trend_end)
        out[name] = {s: standardize(res[s], d, win_start)[sel] for s in ecfg["series"]}
    return out


def to_long(fire_id, cells: pd.DataFrame, series: dict[str, dict[str, np.ndarray]], window_days: int) -> pd.DataFrame:
    """Long table: one row per fire, cell, variable, series and day relative to ignition (-window .. -1)."""
    day_rel = np.arange(-window_days, 0)
    rows = []
    for var, ss in series.items():
        for sname, a in ss.items():
            n = a.shape[1]
            rows.append(pd.DataFrame({
                "fire_id": fire_id,
                "cell_id": np.tile(cells["cell_id"].to_numpy(), window_days),
                "group": np.tile(cells["group"].to_numpy(), window_days),
                "weight": np.tile(cells["weight"].to_numpy(), window_days),
                "variable": var, "series": sname,
                "day_rel": np.repeat(day_rel, n),
                "z": a.reshape(-1)}))
    return pd.concat(rows, ignore_index=True)


# --------------------------------------------------------------------------- real data (per grid)

def _cell_values(da: xr.DataArray, iy: np.ndarray, ix: np.ndarray) -> np.ndarray:
    """(time, lat, lon) DataArray -> (time, ncell) at grid indices (iy south-to-north, ix west-to-east)."""
    da = da.sortby("lat")
    return da.values[:, iy, ix]


def run(cfg: dict, grid: str, fires_csv: str, cells_csv: str, inputs: dict[str, xr.Dataset],
        out_csv: str) -> pd.DataFrame:
    """Epoch series for all selected fires on one grid.

    inputs: datasets already opened over the needed period, keys:
      'sif'  (sif), 'par' (par, W m-2), 'fpar' (fpar composites with time = start and time_center),
      'sr'   (red, nir, blue daily surface reflectance), optional 'fwi' (fwi) and 'aed' (aed).
    Missing optional inputs are skipped with a warning."""
    ecfg, acfg, scfg = cfg["epoch"], cfg["anomalies"], cfg["sif_apar"]
    fires = pd.read_csv(fires_csv, parse_dates=["ignition_date"])
    cells = pd.read_csv(cells_csv)
    cells = cells[cells["grid"] == grid]
    cells = cells.assign(weight=np.where(cells["group"] == "burned", cells["burned_fraction"], 1.0))
    days = inputs["sif"].time.values.astype("datetime64[D]")
    out = []
    for _, f in fires.iterrows():
        c = cells[cells["fire_id"] == f["fire_id"]].reset_index(drop=True)
        if c.empty:
            log.warning("fire %s: no cells on grid %s", f["fire_id"], grid)
            continue
        iy, ix = c["iy"].to_numpy(), c["ix"].to_numpy()
        ign = np.datetime64(f["ignition_date"].date(), "D")
        fp = inputs["fpar"]
        ratio, _ = sif_apar_causal(
            _cell_values(inputs["sif"]["sif"], iy, ix), _cell_values(inputs["par"]["par"], iy, ix),
            _cell_values(fp["fpar"], iy, ix), fp.time.values, fp.time_center.values, days, ign,
            int(scfg["fpar_composite_days"]), float(scfg["fpar_max_gap_days"]), ecfg.get("fpar_persist_days"))
        sr = inputs["sr"]
        red, nir, blue = (_cell_values(sr[b], iy, ix) for b in ("red", "nir", "blue"))
        variables = {"sif_apar": ratio, "ndvi": indices.ndvi(red, nir), "evi": indices.evi(red, nir, blue)}
        for opt in ("fwi", "aed"):
            if opt in inputs:
                variables[opt] = _cell_values(inputs[opt][opt], iy, ix)
            else:
                log.warning("%s not available: skipped", opt)
        series = fire_series(variables, days, ign, acfg, ecfg)
        out.append(to_long(f["fire_id"], c, series, int(ecfg["window_days"])))
    df = pd.concat(out, ignore_index=True)
    df.insert(1, "grid", grid)
    df.to_csv(out_csv, index=False)
    log.info("wrote %s (%d rows)", out_csv, len(df))
    return df


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--grid", choices=["base", "fine"], required=True)
    p.parse_args(argv)
    raise SystemExit("The full-series input grids (SIF, PAR, fPAR, MOD09GA, FWI, AED) are not assembled yet; "
                     "call epoch.run() with opened datasets (see tests/test_epoch.py).")


if __name__ == "__main__":
    main()
