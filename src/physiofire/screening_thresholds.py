"""Derivation of the input-validity thresholds of SIF/APAR (sif_apar.screening) from cells NOT used in the epoch
analysis, before any fire or control series is extracted (decided 2026-11-07).

Sample: land cells (>= sif_apar.min_land_fraction) whose dominant FirEUrisk class is vegetated (not nonfuel), with
no burned area in 2013-2025 (MCD64A1 and VNP64A1 yearly burn history), not inside or within `buffer_km` of any EFFIS
perimeter of 2018-2026, and not among the burned or control cells of the short-listed fires; random subset
(seed = random_seed).

For every cell-day with SIF, PAR and fPAR, the relative noise of SIF/APAR is the absolute residual to the cell's
running median (+- spike_half_window days, as in the spike filter) divided by the cell's median SIF/APAR. The noise
is summarised (median) in bins of fPAR, PAR and TROPOSIF equivalent pixel weight (weight_sum). The proposed
threshold of each variable is the lower edge of the first bin from which the noise stays below `noise_factor` x the
noise of the best-conditioned half of the data (cell-days above the median of that variable).

Usage: python -m physiofire.screening_thresholds [--n-cells 1500]
Output: {sif_apar.out_dir}/screening/noise_by_bin.csv, proposed_thresholds.csv, sample_cells.csv
"""
from __future__ import annotations

import argparse
import logging

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import Point

from physiofire import anomalies, epoch, indices
from physiofire.config import REPO_ROOT, load_config
from physiofire.preprocess.grid import grid_from_config

log = logging.getLogger(__name__)
BINS = {"fpar": np.round(np.arange(0.0, 0.85, 0.05), 2),
        "par": np.arange(0, 360, 20.0),
        "sif_weight": np.array([0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0])}


def sample_cells(cfg: dict, n: int, buffer_km: float, classes: list[str] | None = None) -> pd.DataFrame:
    g = grid_from_config(cfg, "fine")
    gee = REPO_ROOT / cfg["gee"]["out_dir"]
    land = xr.open_dataset(gee / "mask_peninsula_fine.nc")["land_fraction"].sortby("lat").values
    burned = np.zeros_like(land, dtype=bool)
    for pref in ("burn_history", "burn_history_vnp64a1"):
        f = sorted(gee.glob(f"{pref}_fine_*.nc"))[0]
        b = xr.open_dataset(f)["burned_fraction"].sortby("lat")
        burned |= (b.fillna(0) > 0).any(b.dims[0]).values
    tf = xr.open_dataset(REPO_ROOT / cfg["epoch"]["fuel"]["out_dir"] / "fuel_fireurisk_fine.nc")
    types = [int(t) for t in cfg["epoch"]["fuel"]["types"]]
    cls = cfg["epoch"]["fuel"]["classes"]
    frac = np.stack([tf["type_fraction"].sel(fuel_type=[t for t in cls[k]]).sum("fuel_type").sortby("lat").values
                     for k in cls])
    dom = np.array(list(cls))[np.argmax(np.nan_to_num(frac, nan=-1), axis=0)]
    lat2, lon2 = np.meshgrid(g.lat, g.lon, indexing="ij")
    ok = (land >= float(cfg["sif_apar"]["min_land_fraction"])) & ~burned & (dom != "nonfuel")
    iy, ix = np.where(ok)
    df = pd.DataFrame({"iy": iy, "ix": ix, "lat": lat2[iy, ix], "lon": lon2[iy, ix], "fuel_class": dom[iy, ix]})
    # EFFIS perimeters 2018-2026 with a buffer
    gp = sorted((REPO_ROOT / cfg["effis"]["out_dir"]).glob("effis_iberia_*.gpkg"))[0]
    per = gpd.read_file(gp).to_crs(3035)
    pts = gpd.GeoDataFrame(df, geometry=[Point(x, y) for x, y in zip(df.lon, df.lat)], crs=4326).to_crs(3035)
    near = gpd.sjoin_nearest(pts, per[["geometry"]], how="left", distance_col="d_m", max_distance=buffer_km * 1000)
    near_ids = set(near.index[near["d_m"].notna()])
    df = df[~df.index.isin(near_ids)]
    # cells of the short-listed fires and their controls
    used = []
    for f in [REPO_ROOT / cfg["effis"]["out_dir"] / "shortlist_cells_2025" / "epoch_cells.csv",
              REPO_ROOT / cfg["epoch"]["out_dir"] / "epoch_cells.csv"]:
        if f.exists():
            used.append(pd.read_csv(f)[["iy", "ix"]])
    if used:
        u = pd.concat(used).drop_duplicates()
        df = df.merge(u.assign(_u=1), on=["iy", "ix"], how="left")
        df = df[df["_u"].isna()].drop(columns="_u")
    if classes:
        df = df[df["fuel_class"].isin(classes)]
    log.info("eligible cells: %d", len(df))
    rng = np.random.default_rng(int(cfg["random_seed"]))
    return df.iloc[np.sort(rng.choice(len(df), min(n, len(df)), replace=False))].reset_index(drop=True)


def noise(cfg: dict, cells: pd.DataFrame) -> pd.DataFrame:
    acfg, scfg = cfg["anomalies"], cfg["sif_apar"]
    inp = epoch.open_inputs(dict(cfg, epoch=dict(cfg["epoch"], optical_sensitivity=False)), "fine")
    ref = inp["sif"]["sif"]
    days = ref.time.values.astype("datetime64[D]")
    iy, ix = cells["iy"].to_numpy(), cells["ix"].to_numpy()
    sif = epoch._extract(ref, ref, iy, ix, days)
    w = epoch._extract(inp["sif"]["weight_sum"], ref, iy, ix, days)
    par = epoch._extract(inp["par"]["par"], ref, iy, ix, days)
    fp = inp["fpar"]
    comp = epoch._extract(fp["fpar"], ref, iy, ix, None)
    da = xr.DataArray(comp[:, :, None], dims=("time", "cell", "one"))
    fpar = indices.composites_to_daily(da, fp.time_center.values, days.astype("datetime64[ns]"),
                                       float(scfg["fpar_max_gap_days"])).values[:, :, 0]
    with np.errstate(all="ignore"):
        r = indices.sif_apar(sif, par, fpar)
    h = int(acfg["spike_half_window"])
    med = anomalies.running_median(r, h) if hasattr(anomalies, "running_median") else \
        pd.DataFrame(r).rolling(2 * h + 1, center=True, min_periods=int(acfg["spike_min_neighbours"])).median().values
    with np.errstate(all="ignore"):
        scale = np.nanmedian(np.where(r > 0, r, np.nan), axis=0)
        rel = np.abs(r - med) / scale[None, :]
    ok = np.isfinite(rel) & np.isfinite(fpar) & np.isfinite(par) & np.isfinite(w)
    return pd.DataFrame({"fpar": fpar[ok], "par": par[ok], "sif_weight": w[ok], "rel_noise": rel[ok],
                         "sif": sif[ok], "month": pd.DatetimeIndex(np.broadcast_to(days[:, None], r.shape)[ok]).month})


def propose(d: pd.DataFrame, factor: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, props = [], []
    for v, edges in BINS.items():
        b = pd.cut(d[v], np.append(edges, np.inf), right=False)
        s = d.groupby(b, observed=True)["rel_noise"].agg(["median", "count"]).reset_index()
        s["lower"] = [iv.left for iv in s[v]]
        s["variable"] = v
        ref_noise = d.loc[d[v] >= d[v].median(), "rel_noise"].median()
        s["ratio_to_ref"] = s["median"] / ref_noise
        good = s["ratio_to_ref"] <= factor
        # first bin from which all following bins (with data) are below the factor
        thr = np.nan
        for i in range(len(s)):
            if good.iloc[i:].all():
                thr = s["lower"].iloc[i]
                break
        removed = float((d[v] < thr).mean()) if np.isfinite(thr) else np.nan
        props.append({"variable": v, "proposed_min": thr, "reference_noise": ref_noise,
                      "fraction_removed": removed})
        rows.append(s.drop(columns=[v]))
    return pd.concat(rows, ignore_index=True), pd.DataFrame(props)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n-cells", type=int, default=1500)
    p.add_argument("--buffer-km", type=float, default=10.0)
    p.add_argument("--noise-factor", type=float, default=1.5)
    p.add_argument("--classes", nargs="+", help="fuel classes of the sample (default: all vegetated)")
    p.add_argument("--tag", default="all")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    out = REPO_ROOT / cfg["sif_apar"]["out_dir"] / "screening" / args.tag
    out.mkdir(parents=True, exist_ok=True)
    cells = sample_cells(cfg, args.n_cells, args.buffer_km, args.classes)
    cells.to_csv(out / "sample_cells.csv", index=False)
    log.info("sample: %d cells; classes %s", len(cells), cells.fuel_class.value_counts().to_dict())
    d = noise(cfg, cells)
    log.info("cell-days with SIF, PAR and fPAR: %d", len(d))
    bins, props = propose(d, args.noise_factor)
    bins.to_csv(out / "noise_by_bin.csv", index=False)
    props.to_csv(out / "proposed_thresholds.csv", index=False)
    pd.set_option("display.width", 200)
    print(bins.round(3).to_string(index=False))
    print(props.round(4).to_string(index=False))
    jj = d[d.month.isin([6, 7, 8])]
    print(f"JJA cell-days: {len(jj)}; median fPAR {jj.fpar.median():.3f}, PAR {jj.par.median():.0f}, "
          f"weight {jj.sif_weight.median():.2f}")
    cand = {"fpar": [0.05, 0.1, 0.15, 0.2, 0.25], "par": [20, 40], "sif_weight": [0.1, 0.2, 0.3, 0.5]}
    rows = []
    for v, ts in cand.items():
        for t in ts:
            rows.append({"variable": v, "threshold": t, "removed_all": float((d[v] < t).mean()),
                         "removed_JJA": float((jj[v] < t).mean()),
                         "noise_kept_JJA": float(jj.loc[jj[v] >= t, "rel_noise"].median()),
                         "noise_removed_JJA": float(jj.loc[jj[v] < t, "rel_noise"].median())})
    c = pd.DataFrame(rows)
    c.to_csv(out / "candidates.csv", index=False)
    print(c.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
