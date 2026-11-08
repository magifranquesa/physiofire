"""Question 1 (docs/plan_q1_drought.md; config drought_q1): response of SIF/APAR and NDVI/EVI to water stress.

Steps (each tested on synthetic data in tests/test_drought_q1.py):
  series      daily series of the selected cells (R/q1_cells.R): SIF/APAR, NDVI, EVI (Terra + Aqua), secondary SIF,
              SIF/PAR and fPAR, AED (ET0) and the daily SPEI (R/q1_spei.R) of the containing ERA5-Land cell
  anomalies   median by day of year (2018-2025), centred 15-day mean, standardised by the whole-period SD
  analysis 1  scale and lag of maximum correlation (April-October, lags 0-60 days) with a whole-year permutation
              test of the maximum; H1 (scale) and H2 (lag at SPEI-90) with 1-degree block bootstrap
  analysis 2  drought episodes from SPEI-90, response day of each variable in -30..+90 days, events (8-neighbour
              cells with onsets within +-15 days, >= 10 cells), H3 with bootstrap over events
  decision    H3 and (H1 or H2) in the shrubland stratum, each against NDVI and against EVI

Usage: python -m physiofire.drought_q1 {series,analysis}
"""
from __future__ import annotations

import argparse
import json
import logging

import numpy as np
import pandas as pd
import xarray as xr

from physiofire import anomalies, epoch, indices
from physiofire.config import REPO_ROOT, load_config

log = logging.getLogger(__name__)
MAIN = ["sif_apar", "ndvi", "evi"]
SECONDARY = ["sif", "sif_par", "fpar"]
SATELLITE_SPIKE = {"sif_apar", "ndvi", "evi", "sif", "sif_par"}   # retrievals with noise (fpar: interpolated composites)


# =============================================================================================== series

def build_series(cfg: dict, cells: pd.DataFrame) -> xr.Dataset:
    """Daily series (time, cell) of all variables for the selected cells over drought_q1.period.
    Validity screening (sif_apar.screening) and the spike filter (anomalies.spike_k) are applied here."""
    q, scfg, acfg = cfg["drought_q1"], cfg["sif_apar"], cfg["anomalies"]
    inp = epoch.open_inputs(dict(cfg, epoch=dict(cfg["epoch"], optical_sensitivity=False)), q["cells"]["grid"])
    ref = inp["sif"]["sif"]
    d0, d1 = (np.datetime64(x) for x in q["period"])
    days = np.arange(d0, d1 + np.timedelta64(1, "D"), dtype="datetime64[D]")
    iy, ix = cells["iy"].to_numpy(), cells["ix"].to_numpy()
    sif = epoch._extract(ref, ref, iy, ix, days)
    w = epoch._extract(inp["sif"]["weight_sum"], ref, iy, ix, days)
    par = epoch._extract(inp["par"]["par"], ref, iy, ix, days)
    fp = inp["fpar"]
    comp = epoch._extract(fp["fpar"], ref, iy, ix, None)
    fpar = indices.composites_to_daily(xr.DataArray(comp[:, :, None], dims=("time", "cell", "one")),
                                       fp.time_center.values, days.astype("datetime64[ns]"),
                                       float(scfg["fpar_max_gap_days"])).values[:, :, 0]
    with np.errstate(all="ignore"):
        out = {"sif_apar": indices.sif_apar(sif, par, fpar), "sif": sif.copy(), "sif_par": indices.sif_par(sif, par),
               "fpar": fpar}
    valid = epoch.screening_mask(scfg, fpar, par, w)
    if valid is not None:
        for v in ("sif_apar", "sif", "sif_par"):
            out[v] = np.where(valid, out[v], np.nan)
    opt = {}
    for key in ("sr_terra", "sr_aqua"):
        bands = [b for b in inp[key].data_vars if b.split("_")[0] in ("red", "nir", "blue")]
        opt[key] = epoch._optical({b: epoch._extract(inp[key][b], ref, iy, ix, days) for b in bands})
    out["ndvi"] = epoch.combine_platforms(opt["sr_terra"][0], opt["sr_aqua"][0])
    out["evi"] = epoch.combine_platforms(opt["sr_terra"][1], opt["sr_aqua"][1])
    for v in SATELLITE_SPIKE:
        out[v], _ = anomalies.spike_filter(out[v], int(acfg["spike_half_window"]), float(acfg["spike_k"]),
                                           int(acfg["spike_min_neighbours"]))
    out["aed"] = epoch._extract(inp["aed"]["aed"], ref, iy, ix, days)
    # SPEI (time, era5 cell) -> selected cells by the containing ERA5-Land cell
    sp = xr.open_dataset(REPO_ROOT / q["spei"]["out_dir"] / "spei_q1.nc")
    key = {(round(a, 3), round(b, 3)): k for k, (a, b) in enumerate(zip(sp["lon01"].values, sp["lat01"].values))}
    kk = np.array([key[(round(a, 3), round(b, 3))] for a, b in zip(cells["lon01"], cells["lat01"])])
    sp_days = pd.to_datetime(sp["time"].values).values.astype("datetime64[D]")
    pos = np.searchsorted(sp_days, days)
    if not np.array_equal(sp_days[pos], days):
        raise ValueError("SPEI does not cover the analysis period")
    for s in q["spei"]["scales_days"]:
        out[f"spei_{int(s):03d}"] = sp[f"spei_{int(s):03d}"].transpose("time", "cell").values[pos][:, kk]   # R writes (cell, time)
    ds = xr.Dataset({k: (("time", "cell"), v.astype("f4")) for k, v in out.items()},
                    coords={"time": days.astype("datetime64[ns]"), "cell": np.arange(len(cells))})
    for c in ("iy", "ix", "lon", "lat", "fuel_class", "stratum", "aridity_class", "lon01", "lat01"):
        ds[c] = ("cell", cells[c].to_numpy())
    return ds


# =============================================================================================== anomalies

def centred_mean(x: np.ndarray, window: int, min_frac: float) -> np.ndarray:
    """Centred running mean over `window` days (odd) along axis 0, NaN if fewer than min_frac valid days."""
    h = window // 2
    ok = np.isfinite(x)
    cs = np.cumsum(np.where(ok, x, 0.0), axis=0)
    cn = np.cumsum(ok, axis=0)
    cs = np.concatenate([np.zeros((1,) + x.shape[1:]), cs])
    cn = np.concatenate([np.zeros((1,) + x.shape[1:]), cn])
    n = x.shape[0]
    lo = np.clip(np.arange(n) - h, 0, n)
    hi = np.clip(np.arange(n) + h + 1, 0, n)
    s = cs[hi] - cs[lo]
    c = cn[hi] - cn[lo]
    with np.errstate(invalid="ignore", divide="ignore"):
        m = s / c
    return np.where(c >= min_frac * window, m, np.nan)


def standardised_anomaly(x: np.ndarray, days: np.ndarray, qa: dict, clim_window: int) -> np.ndarray:
    """Median-by-day-of-year anomaly, centred mean, divided by each cell's SD over the whole period."""
    a = anomalies.anomaly_median_doy(x, days, clim_window)
    a = centred_mean(a, int(qa["smooth_days"]), float(qa["smooth_min_frac"]))
    with np.errstate(invalid="ignore"):
        sd = np.nanstd(a, axis=0)
    return a / np.where(sd > 0, sd, np.nan)[None, :]


# =============================================================================================== analysis 1

def season_arrays(z: np.ndarray, days: np.ndarray, months: list[int]):
    """Reshape a (time,) series to (year, day-of-season) for the season months, aligned on calendar days.
    Returns (array, years, season month-days) with NaN where a day is outside the record."""
    d = pd.DatetimeIndex(days.astype("datetime64[ns]"))
    md = pd.date_range("2001-01-01", "2001-12-31")
    md = md[md.month.isin(months)].strftime("%m-%d")
    years = np.unique(d.year)
    out = np.full((years.size, md.size), np.nan)
    key = pd.Series(np.arange(len(d)), index=pd.MultiIndex.from_arrays([d.year, d.strftime("%m-%d")]))
    for i, y in enumerate(years):
        idx = key.reindex(pd.MultiIndex.from_product([[y], md])).to_numpy()
        ok = ~np.isnan(idx)
        out[i, ok] = z[idx[ok].astype(int)]
    return out, years, md


def lagged_season(s: np.ndarray, days: np.ndarray, months: list[int], lags: np.ndarray) -> np.ndarray:
    """(n_lags, year, day-of-season) array of s(t - L) for the season days t."""
    out = []
    for L in lags:
        sh = np.full_like(s, np.nan)
        if L == 0:
            sh[:] = s
        else:
            sh[L:] = s[:-L]
        out.append(season_arrays(sh, days, months)[0])
    return np.stack(out)


def pooled_corr(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Pearson correlation between x (year, day) and each y[..., year, day] over pairs valid in both (NaN-aware)."""
    m = np.isfinite(x) & np.isfinite(y)
    n = m.sum(axis=(-2, -1))
    xv = np.where(m, x, 0.0)
    yv = np.where(m, y, 0.0)
    sx, sy = xv.sum(axis=(-2, -1)), yv.sum(axis=(-2, -1))
    sxx, syy, sxy = (xv * xv).sum(axis=(-2, -1)), (yv * yv).sum(axis=(-2, -1)), (xv * yv).sum(axis=(-2, -1))
    with np.errstate(invalid="ignore", divide="ignore"):
        cov = sxy - sx * sy / n
        vx = sxx - sx * sx / n
        vy = syy - sy * sy / n
        r = cov / np.sqrt(vx * vy)
    return np.where(n >= 30, r, np.nan)


def pair_sums(v: np.ndarray, e: np.ndarray) -> np.ndarray:
    """Sums for the Pearson correlation between vegetation year a and explanatory year b, for every (a, b):
    returns (6, n_years_v, ..., n_years_e) with n, sum x, sum y, sum xy, sum xx, sum yy over the valid day pairs.
    v: (year, day); e: (..., year, day)."""
    out = []
    for a in range(v.shape[0]):
        m = np.isfinite(v[a]) & np.isfinite(e)
        x = np.where(m, v[a], 0.0)
        y = np.where(m, e, 0.0)
        out.append(np.stack([m.sum(-1), x.sum(-1), y.sum(-1), (x * y).sum(-1), (x * x).sum(-1), (y * y).sum(-1)]))
    return np.stack(out, axis=1)                                   # (6, Yv, ..., Ye)


def corr_from_sums(t: np.ndarray, min_n: int = 30) -> np.ndarray:
    """Pearson r from totals (6, ...) = n, sx, sy, sxy, sxx, syy."""
    n, sx, sy, sxy, sxx, syy = t
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (sxy - sx * sy / n) / np.sqrt((sxx - sx * sx / n) * (syy - sy * sy / n))
    return np.where(n >= min_n, r, np.nan)


def permuted_corr(ps: np.ndarray, perm: np.ndarray) -> np.ndarray:
    """Correlation when vegetation year perm[b] is paired with explanatory year b (perm = identity: observed)."""
    t = sum(ps[:, perm[b], ..., b] for b in range(perm.size))     # (6, ...)
    return corr_from_sums(t)


def max_corr_cell(v: np.ndarray, explanatory: np.ndarray, sign: int, n_perm: int, rng: np.random.Generator,
                  h2_index: int | None = None) -> dict:
    """Analysis 1 for one cell. v: (year, day) vegetation anomalies; explanatory: (scale, lag, year, day).
    sign = +1 (maximum correlation, SPEI) or -1 (most negative, AED). Returns r*, scale and lag indices, the
    permutation p-value of the maximum (whole-year permutations of v), and the same at the fixed scale h2_index.
    Sums are computed once per pair of years, so each permutation only adds blocks (pair_sums)."""
    ps = pair_sums(v, explanatory)
    ny = v.shape[0]
    r = sign * permuted_corr(ps, np.arange(ny))                    # (scale, lag)
    nan_out = {"r": np.nan, "i_scale": -1, "i_lag": -1, "p": np.nan, "r_h2": np.nan, "i_lag_h2": -1, "p_h2": np.nan}
    if not np.isfinite(r).any():
        return nan_out
    i_s, i_l = np.unravel_index(np.nanargmax(r), r.shape)
    rmax = r[i_s, i_l]
    r_h2 = np.nanmax(r[h2_index]) if h2_index is not None and np.isfinite(r[h2_index]).any() else np.nan
    exceed = exceed_h2 = 0
    for _ in range(n_perm):
        perm = rng.permutation(ny)
        while ny > 1 and np.array_equal(perm, np.arange(ny)):
            perm = rng.permutation(ny)
        rp = sign * permuted_corr(ps, perm)
        if np.isfinite(rp).any() and np.nanmax(rp) >= rmax:
            exceed += 1
        if h2_index is not None and np.isfinite(r_h2) and np.isfinite(rp[h2_index]).any() and \
                np.nanmax(rp[h2_index]) >= r_h2:
            exceed_h2 += 1
    out = {"r": sign * rmax, "i_scale": int(i_s), "i_lag": int(i_l), "p": (exceed + 1) / (n_perm + 1),
           "r_h2": np.nan, "i_lag_h2": -1, "p_h2": np.nan}
    if h2_index is not None and np.isfinite(r_h2):
        out.update({"r_h2": sign * r_h2, "i_lag_h2": int(np.nanargmax(r[h2_index])),
                    "p_h2": (exceed_h2 + 1) / (n_perm + 1)})
    return out


def block_bootstrap(values: np.ndarray, blocks: np.ndarray, stat, n: int, rng: np.random.Generator,
                    level: float = 0.95) -> tuple[float, float, float]:
    """Statistic and percentile CI resampling whole blocks (e.g. 1-degree squares) with replacement."""
    ub = np.unique(blocks)
    idx = {b: np.where(blocks == b)[0] for b in ub}
    est = stat(values)
    boots = []
    for _ in range(n):
        pick = rng.choice(ub, ub.size, replace=True)
        boots.append(stat(values[np.concatenate([idx[b] for b in pick])]))
    a = (1 - level) / 2
    return est, float(np.nanquantile(boots, a)), float(np.nanquantile(boots, 1 - a))


def one_degree_block(lon: np.ndarray, lat: np.ndarray, deg: float) -> np.ndarray:
    return (np.floor(lat / deg).astype(int) * 1000 + np.floor(lon / deg).astype(int))


def h1_test(res: pd.DataFrame, a: str, b: str, alpha: float, min_frac: float, n_boot: int, deg: float, seed: int):
    """H1: fraction of cells (significant in both) where the optimal scale of `a` is strictly shorter than `b`."""
    w = res.pivot_table(index=["cell", "lon", "lat"], columns="variable", values=["scale_days", "p"]).dropna()         if not res.empty else pd.DataFrame()
    if w.empty or ("p", a) not in w.columns or ("p", b) not in w.columns:
        return {"n_cells": 0, "fraction": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "met": False}
    w = w[(w[("p", a)] < alpha) & (w[("p", b)] < alpha)]
    if w.empty:
        return {"n_cells": 0, "fraction": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "met": False}
    shorter = (w[("scale_days", a)] < w[("scale_days", b)]).to_numpy().astype(float)
    blk = one_degree_block(w.index.get_level_values("lon").to_numpy(), w.index.get_level_values("lat").to_numpy(), deg)
    est, lo, hi = block_bootstrap(shorter, blk, np.mean, n_boot, np.random.default_rng(seed))
    return {"n_cells": int(len(w)), "fraction": est, "ci_lo": lo, "ci_hi": hi,
            "met": bool(est >= min_frac and lo > 0.5)}


def h2_test(res: pd.DataFrame, a: str, b: str, alpha: float, max_diff: float, n_boot: int, deg: float, seed: int):
    """H2: median lag difference L(a) - L(b) at the fixed scale, cells significant at that scale in both."""
    w = res.pivot_table(index=["cell", "lon", "lat"], columns="variable", values=["lag_h2", "p_h2"]).dropna()         if not res.empty else pd.DataFrame()
    if w.empty or ("p_h2", a) not in w.columns or ("p_h2", b) not in w.columns:
        return {"n_cells": 0, "median_diff": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "met": False}
    w = w[(w[("p_h2", a)] < alpha) & (w[("p_h2", b)] < alpha)]
    if w.empty:
        return {"n_cells": 0, "median_diff": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "met": False}
    d = (w[("lag_h2", a)] - w[("lag_h2", b)]).to_numpy().astype(float)
    blk = one_degree_block(w.index.get_level_values("lon").to_numpy(), w.index.get_level_values("lat").to_numpy(), deg)
    est, lo, hi = block_bootstrap(d, blk, np.median, n_boot, np.random.default_rng(seed))
    return {"n_cells": int(len(w)), "median_diff": est, "ci_lo": lo, "ci_hi": hi,
            "met": bool(est <= max_diff and hi < 0)}


# =============================================================================================== analysis 2

def find_onsets(spei: np.ndarray, days: np.ndarray, a2: dict, valid_window: tuple) -> list[int]:
    """Episode onsets (indices) in one SPEI series: below onset_threshold for >= min_duration days, the pre_days
    before all > pre_threshold, onset month in onset_months, onset + response window inside valid_window."""
    thr, dur, pre, pthr = (float(a2["onset_threshold"]), int(a2["min_duration_days"]), int(a2["pre_days"]),
                           float(a2["pre_threshold"]))
    w0, w1 = (int(x) for x in a2["response_window_days"])
    months = pd.DatetimeIndex(days.astype("datetime64[ns]")).month
    below = spei < thr
    out = []
    i = 0
    n = len(spei)
    while i < n:
        if below[i] and (i == 0 or not below[i - 1]):
            j = i
            while j < n and below[j]:
                j += 1
            if (j - i >= dur and i >= pre and np.all(spei[i - pre:i] > pthr) and months[i] in a2["onset_months"]
                    and days[i] + np.timedelta64(w0, "D") >= valid_window[0]
                    and days[i] + np.timedelta64(w1 + int(a2["response_min_days"]), "D") <= valid_window[1]):
                out.append(i)
            i = j
        else:
            i += 1
    return out


def response_day(z: np.ndarray, onset: int, a2: dict) -> float:
    """First day (relative to onset, in the response window) from which z stays <= response_threshold_sd for
    response_min_days consecutive calendar days. Missing days neither break nor count as a response: the run must
    start on a valid day, and all valid days in the run must be below the threshold, with at least half valid."""
    w0, w1 = (int(x) for x in a2["response_window_days"])
    thr, k = float(a2["response_threshold_sd"]), int(a2["response_min_days"])
    for d in range(w0, w1 + 1):
        i = onset + d
        if i < 0 or i + k > len(z) or not np.isfinite(z[i]) or z[i] > thr:
            continue
        seg = z[i:i + k]
        v = seg[np.isfinite(seg)]
        if v.size >= k / 2 and np.all(v <= thr):
            return float(d)
    return np.nan


def build_events(ep: pd.DataFrame, gap_days: int, min_cells: int) -> pd.Series:
    """Event id for each episode row (columns iy, ix, onset_day as integer days): connected components of episodes
    in 8-neighbour cells with onsets within +-gap_days; events with fewer than min_cells cells get -1."""
    n = len(ep)
    parent = np.arange(n)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    iy, ix, t = ep["iy"].to_numpy(), ep["ix"].to_numpy(), ep["onset_day"].to_numpy()
    order = np.argsort(t)
    for a_pos, a in enumerate(order):
        for b in order[a_pos + 1:]:
            if t[b] - t[a] > gap_days:
                break
            if abs(iy[a] - iy[b]) <= 1 and abs(ix[a] - ix[b]) <= 1 and a != b:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[rb] = ra
    roots = np.array([find(a) for a in range(n)])
    ids = pd.Series(roots, index=ep.index)
    size = ep.groupby(roots)["cell"].nunique()
    ok = size[size >= min_cells].index
    return ids.where(ids.isin(ok), -1)


def h3_test(ev: pd.DataFrame, a: str, b: str, max_diff: float, n_boot: int, seed: int):
    """H3: median over events of the event median of paired response-day differences a - b (cells responding in
    both); percentile CI resampling events."""
    if ev.empty or f"resp_{a}" not in ev or f"resp_{b}" not in ev:
        return {"n_events": 0, "n_cells": 0, "median_diff": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "met": False}
    d = ev.dropna(subset=[f"resp_{a}", f"resp_{b}"])
    d = d[d["event"] >= 0]
    if d.empty:
        return {"n_events": 0, "n_cells": 0, "median_diff": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "met": False}
    em = (d[f"resp_{a}"] - d[f"resp_{b}"]).groupby(d["event"]).median().to_numpy()
    rng = np.random.default_rng(seed)
    boots = [np.median(rng.choice(em, em.size, replace=True)) for _ in range(n_boot)]
    lo, hi = np.quantile(boots, [0.025, 0.975])
    est = float(np.median(em))
    return {"n_events": int(em.size), "n_cells": int(len(d)), "median_diff": est, "ci_lo": float(lo),
            "ci_hi": float(hi), "met": bool(est <= max_diff and hi < 0)}


# =============================================================================================== driver

def _cell_task(args) -> tuple[list, list]:
    """Analyses 1 and 2 for one cell (top-level function, so that it can run in worker processes)."""
    (c, z_c, spei_c, days, scales, lags, months, h2_i, n_perm, seed, a2, s90_key) = args
    rng = np.random.default_rng([seed, c])                       # per-cell stream: reproducible in any order
    expl = np.stack([lagged_season(spei_c[s], days, months, lags) for s in scales])   # (scale, lag, year, day)
    aed_l = lagged_season(z_c["aed"], days, months, lags)[None] if "aed" in z_c else None
    rows, ep_rows = [], []
    veg = [v for v in MAIN + SECONDARY if v in z_c]
    for v in veg:
        vs = season_arrays(z_c[v], days, months)[0]
        np_v = n_perm if v in MAIN else 0                        # secondary variables: descriptive only
        r = max_corr_cell(vs, expl, +1, np_v, rng, h2_i)
        rows.append({"cell": c, "variable": v, "explanatory": "spei", "r": r["r"], "p": r["p"] if np_v else np.nan,
                     "scale_days": scales[r["i_scale"]] if r["i_scale"] >= 0 else np.nan,
                     "lag_days": lags[r["i_lag"]] if r["i_lag"] >= 0 else np.nan,
                     "r_h2": r["r_h2"], "p_h2": r["p_h2"] if np_v else np.nan,
                     "lag_h2": lags[r["i_lag_h2"]] if r["i_lag_h2"] >= 0 else np.nan})
        if aed_l is not None:
            ra = max_corr_cell(vs, aed_l, -1, np_v, rng, None)
            rows.append({"cell": c, "variable": v, "explanatory": "aed", "r": ra["r"],
                         "p": ra["p"] if np_v else np.nan, "scale_days": np.nan,
                         "lag_days": lags[ra["i_lag"]] if ra["i_lag"] >= 0 else np.nan,
                         "r_h2": np.nan, "p_h2": np.nan, "lag_h2": np.nan})
    for o in find_onsets(spei_c[s90_key], days, a2, (days[0], days[-1])):
        r_ = {"cell": c, "onset": days[o], "onset_day": int((days[o] - days[0]).astype(int))}
        for v in veg:
            r_[f"resp_{v}"] = response_day(z_c[v], o, a2)
        ep_rows.append(r_)
    return rows, ep_rows


def analysis(cfg: dict, ds: xr.Dataset, n_perm: int | None = None, workers: int = 1) -> dict:
    """Run analyses 1 and 2 on a series dataset (from build_series or synthetic). Returns result tables.
    workers > 1 runs the cells in parallel processes (identical results: one random stream per cell)."""
    q, acfg = cfg["drought_q1"], cfg["anomalies"]
    a1, a2 = q["analysis1"], q["analysis2"]
    seed = int(cfg["random_seed"])
    n_perm = int(a1["permutations"]) if n_perm is None else n_perm
    days = ds["time"].values.astype("datetime64[D]")
    scales = [int(s) for s in q["spei"]["scales_days"]]
    lags = np.arange(int(a1["lags_days"][0]), int(a1["lags_days"][1]) + 1)
    months = [int(m) for m in a1["months"]]
    h2_i = scales.index(int(a1["h2_scale_days"]))
    veg = [v for v in MAIN + SECONDARY if v in ds]
    z = {v: standardised_anomaly(ds[v].values.astype(float), days, q["anomalies"], int(acfg["clim_doy_window"]))
         for v in veg + (["aed"] if q.get("aed_secondary") and "aed" in ds else [])}
    sp = {s: ds[f"spei_{s:03d}"].values.astype(float) for s in scales}
    s90 = int(a2["spei_scale_days"])
    tasks = [(c, {v: z[v][:, c] for v in z}, {s: sp[s][:, c] for s in scales}, days, scales, lags, months, h2_i,
              n_perm, seed, a2, s90) for c in range(ds.sizes["cell"])]
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(_cell_task, tasks, chunksize=16))
    else:
        results = [_cell_task(t) for t in tasks]
    rows = [r for res_c, _ in results for r in res_c]
    ep_rows = [r for _, ep_c in results for r in ep_c]
    res = pd.DataFrame(rows)
    meta = ds[["iy", "ix", "lon", "lat", "fuel_class", "stratum", "aridity_class"]].to_dataframe().reset_index()
    res = res.merge(meta, on="cell", how="left")
    ep = pd.DataFrame(ep_rows)
    if not ep.empty:
        ep = ep.merge(meta, on="cell", how="left")
        ep["event"] = build_events(ep, int(a2["event_max_onset_gap_days"]), int(a2["event_min_cells"]))
    return {"cells": res, "episodes": ep}


def decide(cfg: dict, out: dict) -> pd.DataFrame:
    """H1, H2 and H3 by stratum (against NDVI and against EVI) and the decision for the deciding stratum."""
    q = cfg["drought_q1"]
    a1, a2 = q["analysis1"], q["analysis2"]
    seed, nb, deg = int(cfg["random_seed"]), int(q["bootstrap_n"]), float(a1["bootstrap_block_deg"])
    res = out["cells"][out["cells"]["explanatory"] == "spei"]
    ep = out["episodes"]
    rows = []
    for st in list(q["strata"]) + ["wet_heath_only"]:
        rs = res[res["fuel_class"] == "wet_heath"] if st == "wet_heath_only" else res[res["stratum"] == st]
        es = (ep[ep["fuel_class"] == "wet_heath"] if st == "wet_heath_only" else ep[ep["stratum"] == st]) \
            if not ep.empty else ep
        for b in ("ndvi", "evi"):
            h1 = h1_test(rs, "sif_apar", b, float(a1["alpha"]), float(a1["h1_min_fraction"]), nb, deg, seed)
            h2 = h2_test(rs, "sif_apar", b, float(a1["alpha"]), float(a1["h2_max_median_lag_diff_days"]), nb, deg,
                         seed)
            h3 = h3_test(es, "sif_apar", b, float(a2["h3_max_median_diff_days"]), nb, seed) if not ep.empty else \
                {"n_events": 0, "met": False}
            for name, h in (("H1", h1), ("H2", h2), ("H3", h3)):
                rows.append({"stratum": st, "against": b, "hypothesis": name, **h})
    d = pd.DataFrame(rows)
    met = d.set_index(["stratum", "against", "hypothesis"])["met"]

    def ok(st):
        return all(met[(st, b, "H3")] and (met[(st, b, "H1")] or met[(st, b, "H2")]) for b in ("ndvi", "evi"))
    d.attrs["decision_positive"] = bool(ok("shrubland"))
    return d


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("step", choices=["series", "analysis"])
    p.add_argument("--workers", type=int, default=1)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    od = REPO_ROOT / cfg["drought_q1"]["out_dir"]
    if args.step == "series":
        cells = pd.read_csv(od / "drought_q1_cells.csv")
        ds = build_series(cfg, cells)
        ds.to_netcdf(od / "drought_q1_series.nc", encoding={v: {"zlib": True, "complevel": 4}
                                                             for v in ds.data_vars if ds[v].dtype.kind == "f"})
        log.info("wrote series for %d cells", ds.sizes["cell"])
    else:
        ds = xr.open_dataset(od / "drought_q1_series.nc").load()
        out = analysis(cfg, ds, workers=args.workers)
        out["cells"].to_csv(od / "analysis1_cells.csv", index=False)
        out["episodes"].to_csv(od / "analysis2_episodes.csv", index=False)
        d = decide(cfg, out)
        d.to_csv(od / "hypotheses.csv", index=False)
        (od / "decision.json").write_text(json.dumps({"decision_positive": d.attrs["decision_positive"]}, indent=1))
        log.info("decision positive: %s", d.attrs["decision_positive"])


if __name__ == "__main__":
    main()
