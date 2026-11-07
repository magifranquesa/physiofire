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
    offsets = ecfg.get("cutoff_offset_days") or {}      # e.g. NBAR: masked from day -8 (16-day retrieval window)
    spike_vars = ecfg.get("spike_filter_variables")     # None = all variables (previous behaviour)
    out = {}
    for name, x in variables.items():
        cutoff = np.full(x.shape[1], ign + np.timedelta64(int(offsets.get(name, 0)), "D"))
        trend_end = None if te is None else np.full(x.shape[1], ign + np.timedelta64(int(te), "D"))
        spike = spike_vars is None or any(name == v or name.startswith(v + "_") for v in spike_vars)
        res = anomalies.compute(x, d, acfg, cutoff=cutoff, valid=None if valid is None else valid.get(name),
                                trend_end=trend_end, spike=spike)
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

OPTICAL_INPUTS = {"sr_terra": "terra", "sr_aqua": "aqua", "nbar": "nbar"}


def _extract(da: xr.DataArray, ref: xr.DataArray, iy: np.ndarray, ix: np.ndarray, days: np.ndarray | None) -> np.ndarray:
    """(time, ncell) values of `da` at the cells (iy, ix) of the reference grid `ref` (iy south-to-north index).
    Inputs on the reference grid are read by index; coarser inputs (FWI, AED on the native 0.1 deg ERA5-Land
    grid) by the nearest cell centre, i.e. the coarse cell that contains the reference cell centre.
    Daily inputs are aligned to `days` (missing days -> NaN); composite inputs (days=None) are returned as is."""
    rlat = np.sort(ref["lat"].values)
    rlon = ref["lon"].values
    da = da.sortby("lat")
    if da.sizes["lat"] == rlat.size and da.sizes["lon"] == rlon.size and np.allclose(da["lat"], rlat):
        x = da.isel(lat=xr.DataArray(iy, dims="cell"), lon=xr.DataArray(ix, dims="cell"))
    else:
        steps = np.concatenate([np.abs(np.diff(da["lat"].values)), np.abs(np.diff(da["lon"].values))])
        res = float(steps.max())
        x = da.sel(lat=xr.DataArray(rlat[iy], dims="cell"), lon=xr.DataArray(rlon[ix], dims="cell"),
                   method="nearest", tolerance=res / 2 + 1e-6)
    if days is not None:
        x = x.reindex(time=days.astype("datetime64[ns]"))
    return x.transpose("time", "cell").values.astype("f8")


def _optical(sr: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """NDVI and EVI from red/nir/blue (time, ncell); invalid where a band count is 0 (if counts are given) and EVI
    outside [0, 1] (as in the descriptive chain)."""
    ok = np.ones(sr["red"].shape, dtype=bool)
    for b in ("red", "nir", "blue"):
        if f"{b}_count" in sr:
            ok &= sr[f"{b}_count"] > 0
    with np.errstate(all="ignore"):
        nd = np.where(ok, indices.ndvi(sr["red"], sr["nir"]), np.nan)
        ev = np.where(ok, indices.evi(sr["red"], sr["nir"], sr["blue"]), np.nan)
    ev = np.where((ev >= 0) & (ev <= 1), ev, np.nan)
    return nd, ev


def combine_platforms(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Terra + Aqua combined index: mean when both are valid, the valid one otherwise (main optical competitor)."""
    s = np.where(np.isfinite(a), a, 0.0) + np.where(np.isfinite(b), b, 0.0)
    n = np.isfinite(a).astype(int) + np.isfinite(b).astype(int)
    return np.where(n > 0, s / np.maximum(n, 1), np.nan)


def screening_mask(scfg: dict, fpar: np.ndarray, par: np.ndarray, sif_weight: np.ndarray | None) -> np.ndarray | None:
    """Input-validity mask of SIF/APAR from sif_apar.screening (null thresholds are not applied)."""
    sc = scfg.get("screening") or {}
    m = np.ones(fpar.shape, dtype=bool)
    used = False
    with np.errstate(invalid="ignore"):
        if sc.get("fpar_min") is not None:
            m &= fpar >= float(sc["fpar_min"])
            used = True
        if sc.get("par_min") is not None:
            m &= par >= float(sc["par_min"])
            used = True
        if sc.get("sif_weight_min") is not None and sif_weight is not None:
            m &= sif_weight >= float(sc["sif_weight_min"])
            used = True
    return m if used else None


def run(cfg: dict, grid: str, fires_csv: str, cells_csv: str, inputs: dict[str, xr.Dataset],
        out_csv: str) -> pd.DataFrame:
    """Epoch series for all selected fires on one grid.

    inputs: datasets over the needed period (may be lazily opened; only the fire and control cells are read):
      'sif'  (sif; optional weight_sum), 'par' (par, W m-2), 'fpar' (fpar composites, time = start, time_center),
      optical: 'sr_terra' and/or 'sr_aqua' (red, nir, blue[, *_count]) -> MAIN NDVI/EVI = Terra + Aqua combined
               (mean if both, else the one available); with epoch.optical_sensitivity also each platform and
               'nbar' separately (ndvi_terra, ..., ndvi_nbar; NBAR masked from day -8 via epoch.cutoff_offset_days).
               A single 'sr' input (synthetic tests) is used as the main optical input.
      optional 'fwi' (fwi) and 'aed' (aed), on any coarser regular grid (nearest containing cell).
    Fires with exclude = TRUE in the fires table are skipped. SIF/APAR is computed with the main fPAR persistence
    (epoch.fpar_persist_days) and, as 'sif_apar_nopersist', without persistence (reference run R1)."""
    ecfg, acfg, scfg = cfg["epoch"], cfg["anomalies"], cfg["sif_apar"]
    fires = pd.read_csv(fires_csv, parse_dates=["ignition_date"], dtype={"fire_id": str})
    if "exclude" in fires:
        ex = fires["exclude"].astype(str).str.upper().eq("TRUE")
        if ex.any():
            log.info("skipping %d excluded fires: %s", int(ex.sum()), ", ".join(fires.loc[ex, "fire_id"]))
        fires = fires[~ex]
    cells = pd.read_csv(cells_csv, dtype={"fire_id": str})
    cells = cells[(cells["grid"] == grid) & cells["fire_id"].isin(fires["fire_id"])].reset_index(drop=True)
    cells = cells.assign(weight=np.where(cells["group"] == "burned", cells["burned_fraction"], 1.0))
    ref = inputs["sif"]["sif"]
    days = ref.time.values.astype("datetime64[D]")

    # read every needed cell once
    u = cells[["iy", "ix"]].drop_duplicates().reset_index(drop=True)
    u["k"] = np.arange(len(u))
    cells = cells.merge(u, on=["iy", "ix"], how="left")
    iy, ix = u["iy"].to_numpy(), u["ix"].to_numpy()
    log.info("%d fires, %d distinct cells", fires["fire_id"].nunique(), len(u))
    data: dict[str, np.ndarray] = {
        "sif": _extract(ref, ref, iy, ix, days),
        "par": _extract(inputs["par"]["par"], ref, iy, ix, days)}
    if "weight_sum" in inputs["sif"]:
        data["sif_weight"] = _extract(inputs["sif"]["weight_sum"], ref, iy, ix, days)
    fp = inputs["fpar"]
    fpar_comp = _extract(fp["fpar"], ref, iy, ix, None)
    opt: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for key in [k for k in ("sr", *OPTICAL_INPUTS) if k in inputs]:
        bands = [b for b in inputs[key].data_vars if b.split("_")[0] in ("red", "nir", "blue")]
        opt[key] = _optical({b: _extract(inputs[key][b], ref, iy, ix, days) for b in bands})
    if "sr" in opt:
        data["ndvi"], data["evi"] = opt["sr"]
    elif "sr_terra" in opt or "sr_aqua" in opt:
        pl = [opt[k] for k in ("sr_terra", "sr_aqua") if k in opt]
        data["ndvi"] = pl[0][0] if len(pl) == 1 else combine_platforms(pl[0][0], pl[1][0])
        data["evi"] = pl[0][1] if len(pl) == 1 else combine_platforms(pl[0][1], pl[1][1])
    if ecfg.get("optical_sensitivity"):
        for key, tag in OPTICAL_INPUTS.items():
            if key in opt:
                data[f"ndvi_{tag}"], data[f"evi_{tag}"] = opt[key]
    for v in ("fwi", "aed"):
        if v in inputs:
            data[v] = _extract(inputs[v][v], ref, iy, ix, days)
        else:
            log.warning("%s not available: skipped", v)

    out = []
    for _, f in fires.iterrows():
        c = cells[cells["fire_id"] == f["fire_id"]].reset_index(drop=True)
        if c.empty:
            log.warning("fire %s: no cells on grid %s", f["fire_id"], grid)
            continue
        k = c["k"].to_numpy()
        ign = np.datetime64(f["ignition_date"].date(), "D")
        variables, valid = {}, {}
        for name, persist in (("sif_apar", ecfg.get("fpar_persist_days")), ("sif_apar_nopersist", None)):
            ratio, fpar_d = sif_apar_causal(data["sif"][:, k], data["par"][:, k], fpar_comp[:, k], fp.time.values,
                                            fp.time_center.values, days, ign, int(scfg["fpar_composite_days"]),
                                            float(scfg["fpar_max_gap_days"]), persist)
            variables[name] = ratio
            m = screening_mask(scfg, fpar_d, data["par"][:, k],
                               data["sif_weight"][:, k] if "sif_weight" in data else None)
            if m is not None:
                valid[name] = m
        for name in data:
            if name not in ("sif", "par", "sif_weight"):
                variables[name] = data[name][:, k]
        series = fire_series(variables, days, ign, acfg, ecfg, valid or None)
        out.append(to_long(f["fire_id"], c, series, int(ecfg["window_days"])))
    df = pd.concat(out, ignore_index=True)
    df.insert(1, "grid", grid)
    df.to_csv(out_csv, index=False)
    log.info("wrote %s (%d rows)", out_csv, len(df))
    return df


# --------------------------------------------------------------------------- input files

def _yearly(directory, prefix: str, grid: str) -> list:
    files = sorted(directory.glob(f"{prefix}_{grid}_[0-9][0-9][0-9][0-9].nc"))
    if not files:
        raise FileNotFoundError(f"no yearly files {prefix}_{grid}_YYYY.nc in {directory}")
    return files


def _open_years(files) -> xr.Dataset:
    ds = xr.open_mfdataset(files, combine="nested", concat_dim="time", data_vars="minimal", coords="minimal",
                           compat="override")
    _, i = np.unique(ds["time"].values, return_index=True)
    return ds.isel(time=np.sort(i))


def sif_year_files(sif_dir, grid: str) -> list:
    """Yearly gridded SIF files (troposif_sif_{grid}_YYYY0101_YYYY1231.nc; the first year starts on 1 May 2018 and
    the last one ends with the record); sample-period files are ignored."""
    import re
    pat = re.compile(rf"troposif_sif_{grid}_(\d{{4}})(\d{{4}})_(\d{{4}})(\d{{4}})\.nc$")
    out = []
    for f in sorted(sif_dir.glob(f"troposif_sif_{grid}_*.nc")):
        m = pat.search(f.name)
        if m and m.group(1) == m.group(3) and m.group(2) in ("0101", "0501") \
                and (m.group(4) == "1231" or int(m.group(3)) >= 2026):
            out.append(f)
    return out


def open_inputs(cfg: dict, grid: str) -> dict[str, xr.Dataset]:
    """Lazily open the full-period inputs of the epoch analysis on `grid` (yearly files)."""
    from physiofire.config import REPO_ROOT
    series = REPO_ROOT / cfg["gee"]["out_dir"] / "series"
    sif_files = sif_year_files(REPO_ROOT / cfg["sif"]["grid_dir"], grid)
    if not sif_files:
        raise FileNotFoundError("no yearly gridded SIF files")
    inputs = {"sif": _open_years(sif_files)[["sif", "weight_sum"]]}
    sw = _open_years(_yearly(series, "shortwave", grid))["sw"]
    inputs["par"] = (float(cfg["par"]["par_fraction"]) * sw).where(sw > 0).rename("par").to_dataset()
    fp = _open_years(_yearly(series, "fpar", grid))
    if "time_center" in fp.data_vars:
        fp = fp.set_coords("time_center")
    inputs["fpar"] = fp.assign(fpar=fp["fpar"].where(fp["fpar_count"] > 0))[["fpar"]]
    inputs["sr_terra"] = _open_years(_yearly(series, "mod09ga", grid))
    inputs["sr_aqua"] = _open_years(_yearly(series, "myd09ga", grid))
    if cfg["epoch"].get("optical_sensitivity"):
        inputs["nbar"] = _open_years(_yearly(series, "nbar", grid))
    for key, var, pref in (("fwi", "FWI", "fwi_era5land"), ("aed", "aed", "aed_era5land")):
        fs = sorted((REPO_ROOT / cfg[key]["out_dir"]).glob(f"{pref}_*.nc"))
        if fs:
            best = max(fs, key=lambda f: xr.open_dataset(f).sizes["time"])
            inputs[key] = xr.open_dataset(best)[[var]].rename({var: key})
        else:
            log.warning("no %s file: the epoch analysis will skip it", key)
    return inputs


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--grid", choices=["base", "fine"], default="fine")
    p.add_argument("--fires", help="fires table (default epoch.selected_fires)")
    p.add_argument("--cells", help="cells table (default {epoch.out_dir}/epoch_cells.csv)")
    p.add_argument("--out", help="output CSV (default {epoch.out_dir}/epoch_series_{grid}.csv)")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    from physiofire.config import REPO_ROOT, load_config
    cfg = load_config()
    od = REPO_ROOT / cfg["epoch"]["out_dir"]
    run(cfg, args.grid, args.fires or str(REPO_ROOT / cfg["epoch"]["selected_fires"]),
        args.cells or str(od / "epoch_cells.csv"), open_inputs(cfg, args.grid),
        args.out or str(od / f"epoch_series_{args.grid}.csv"))


if __name__ == "__main__":
    main()
