"""Q1b (docs/plan_q1b.md; config drought_q1b): post hoc follow-up of question 1, with its own criterion fixed in
git before running. Uses the series of question 1 (drought_q1_series.nc) and the same filters, climatology,
strata and inference; what changes:

  episodes    definitions valid for chained droughts (B rapid intensification, A intensification across category
              thresholds, C SPEI-30 onset), chosen in the fixed order B -> A -> C by counting events from SPEI only
  H3b         paired time-to-response with censoring at +90 days (cells without a response are kept, not excluded)
  analysis 1  backward 15-day mean, lags -15..+60 days, SIF/APAR corrected for PAR (slope fitted on days with
              SPEI-90 >= 0); H1 and H2b (cells with a lag at a boundary excluded); centred mean as sensitivity;
              partial correlation given PAR as sensitivity
  noise       NDVI/EVI degraded with white noise to the day-to-day noise fraction of SIF/APAR (5 replicates):
              robust H1
  decision    support / contrary / not conclusive (shrubland, against NDVI and against EVI)

Usage: python -m physiofire.drought_q1b {count,par,analysis1,analysis2,noise,decide} [--workers N]
"""
from __future__ import annotations

import argparse
import json
import logging

import numpy as np
import pandas as pd
import xarray as xr

from physiofire import anomalies, drought_q1 as q1, epoch
from physiofire.config import REPO_ROOT, load_config

log = logging.getLogger(__name__)
MAIN = ["sif_apar", "ndvi", "evi"]


# =============================================================================================== episodes

def run_length(b: np.ndarray) -> np.ndarray:
    """Number of consecutive True values starting at each index (0 where b is False)."""
    out = np.zeros(b.size, dtype=int)
    n = 0
    for i in range(b.size - 1, -1, -1):
        n = n + 1 if b[i] else 0
        out[i] = n
    return out


def separate(cands, min_sep: int) -> list[int]:
    """Keep the first of candidate onsets closer than min_sep days to the previous kept onset."""
    out = []
    for i in sorted(set(int(c) for c in cands)):
        if not out or i - out[-1] >= min_sep:
            out.append(i)
    return out


def window_ok(i: int, days: np.ndarray, a2: dict, valid: tuple) -> bool:
    """Onset month and response window inside the period with data (as question 1)."""
    w0, w1 = (int(x) for x in a2["response_window_days"])
    month = pd.Timestamp(days[i]).month
    return bool(month in a2["onset_months"] and days[i] + np.timedelta64(w0, "D") >= valid[0]
                and days[i] + np.timedelta64(w1 + int(a2["response_min_days"]), "D") <= valid[1])


def onsets_rapid(spei: np.ndarray, days: np.ndarray, p: dict, a2: dict, valid: tuple, min_sep: int) -> list[int]:
    """Definition B: first day i with SPEI[i] < threshold, staying below for >= min_duration days, and a fall of
    >= min_fall from the maximum of the previous fall_days days (whatever the starting level). Candidates closer
    than min_sep days keep the first; then the onset month and response window are checked."""
    thr, fall, fd, dur = (float(p["threshold"]), float(p["min_fall"]), int(p["fall_days"]),
                          int(p["min_duration_days"]))
    below = np.isfinite(spei) & (spei < thr)
    rl = run_length(below)
    cands = []
    for i in np.where(below & (rl >= dur))[0]:
        if i < fd:
            continue
        prev = spei[i - fd:i]
        if np.isfinite(prev).any() and np.nanmax(prev) - spei[i] >= fall:
            cands.append(i)
    return [i for i in separate(cands, min_sep) if window_ok(i, days, a2, valid)]


def onsets_intensification(spei: np.ndarray, days: np.ndarray, p: dict, a2: dict, valid: tuple,
                           min_sep: int) -> list[int]:
    """Definition A: downward crossing of a category threshold (-1, -1.5, -2), staying below it for >= min_duration
    days, with SPEI >= threshold + pre_margin on at least one of the previous pre_days days. Crossings of all
    thresholds are pooled; onsets closer than min_sep days keep the first; then month and window are checked."""
    dur, pre, mg = int(p["min_duration_days"]), int(p["pre_days"]), float(p["pre_margin"])
    cands = []
    for thr in p["thresholds"]:
        thr = float(thr)
        below = np.isfinite(spei) & (spei < thr)
        rl = run_length(below)
        start = below & np.concatenate([[True], ~below[:-1]])
        for i in np.where(start & (rl >= dur))[0]:
            if i < pre:
                continue
            prev = spei[i - pre:i]
            if np.isfinite(prev).any() and np.nanmax(prev) >= thr + mg:
                cands.append(i)
    return [i for i in separate(cands, min_sep) if window_ok(i, days, a2, valid)]


def onsets_short_scale(spei30: np.ndarray, days: np.ndarray, p: dict, a2: dict, valid: tuple) -> list[int]:
    """Definition C: the rule of question 1 (q1.find_onsets) on SPEI-30 with its own pre-period and duration."""
    a2c = dict(a2, onset_threshold=p["onset_threshold"], min_duration_days=p["min_duration_days"],
               pre_days=p["pre_days"], pre_threshold=p["pre_threshold"])
    return q1.find_onsets(spei30, days, a2c, valid)


def episode_onsets(defn: str, ds_c: dict, days: np.ndarray, cfg: dict) -> list[int]:
    """Onsets of one cell under definition 'A', 'B' or 'C'. ds_c: {'spei_090': ..., 'spei_030': ...} (time,)."""
    e = cfg["drought_q1b"]["episodes"]
    a2 = cfg["drought_q1"]["analysis2"]
    valid = (days[0], days[-1])
    if defn == "B":
        return onsets_rapid(ds_c["spei_090"], days, e["B"], a2, valid, int(e["min_separation_days"]))
    if defn == "A":
        return onsets_intensification(ds_c["spei_090"], days, e["A"], a2, valid, int(e["min_separation_days"]))
    if defn == "C":
        return onsets_short_scale(ds_c[f"spei_{int(e['C']['spei_scale_days']):03d}"], days, e["C"], a2, valid)
    raise ValueError(defn)


def episode_table(defn: str, ds: xr.Dataset, cfg: dict) -> pd.DataFrame:
    """Episodes of all cells (SPEI only) with their event id (question 1 event rule, all strata together)."""
    days = ds["time"].values.astype("datetime64[D]")
    a2 = cfg["drought_q1"]["analysis2"]
    sc = int(cfg["drought_q1b"]["episodes"]["C"]["spei_scale_days"])
    s90, s30 = ds["spei_090"].values.astype(float), ds[f"spei_{sc:03d}"].values.astype(float)
    rows = []
    for c in range(ds.sizes["cell"]):
        for o in episode_onsets(defn, {"spei_090": s90[:, c], f"spei_{sc:03d}": s30[:, c]}, days, cfg):
            rows.append({"cell": c, "onset": days[o], "onset_day": int((days[o] - days[0]).astype(int))})
    ep = pd.DataFrame(rows, columns=["cell", "onset", "onset_day"])
    meta = ds[["iy", "ix", "lon", "lat", "fuel_class", "stratum", "aridity_class"]].to_dataframe().reset_index()
    ep = ep.merge(meta, on="cell", how="left")
    ep["definition"] = defn
    ep["event"] = q1.build_events(ep, int(a2["event_max_onset_gap_days"]), int(a2["event_min_cells"])) \
        if len(ep) else pd.Series(dtype=int)
    return ep


def count_events(ep: pd.DataFrame, strata: list[str]) -> dict:
    """Events (>= event_min_cells cells, all strata) and how many contain cells of each stratum."""
    e = ep[ep["event"] >= 0]
    out = {"n_episodes": int(len(ep)), "n_cells_with_episode": int(ep["cell"].nunique()),
           "n_events": int(e["event"].nunique())}
    for st in strata:
        out[f"n_events_with_{st}"] = int(e.loc[e["stratum"] == st, "event"].nunique())
        out[f"n_{st}_cells_in_events"] = int(e.loc[e["stratum"] == st, "cell"].nunique())
    return out


def choose_definition(counts: dict, order: list[str], min_events: int, stratum: str = "shrubland") -> str | None:
    """First definition in `order` with >= min_events events containing cells of the deciding stratum."""
    for d in order:
        if counts[d][f"n_events_with_{stratum}"] >= min_events:
            return d
    return None


# =============================================================================================== anomalies

def backward_mean(x: np.ndarray, window: int, min_frac: float) -> np.ndarray:
    """Running mean over the `window` days ending at t (t - window + 1 .. t) along axis 0; NaN with fewer than
    min_frac * window valid days."""
    ok = np.isfinite(x)
    pad = np.zeros((1,) + x.shape[1:])
    cs = np.concatenate([pad, np.cumsum(np.where(ok, x, 0.0), axis=0)])
    cn = np.concatenate([pad, np.cumsum(ok, axis=0)])
    n = x.shape[0]
    hi = np.arange(1, n + 1)
    lo = np.clip(hi - window, 0, n)
    s, c = cs[hi] - cs[lo], cn[hi] - cn[lo]
    with np.errstate(invalid="ignore", divide="ignore"):
        m = s / c
    return np.where(c >= min_frac * window, m, np.nan)


def smooth_standardise(a: np.ndarray, qa: dict, mode: str) -> np.ndarray:
    """Daily anomaly -> running mean ('backward' or 'centred', smooth_days) -> / SD of each cell (whole period)."""
    w, mf = int(qa["smooth_days"]), float(qa["smooth_min_frac"])
    m = backward_mean(a, w, mf) if mode == "backward" else q1.centred_mean(a, w, mf)
    with np.errstate(invalid="ignore"):
        sd = np.nanstd(m, axis=0, keepdims=True)
    return m / np.where(sd > 0, sd, np.nan)


def _sd_scale(a: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore"):
        sd = np.nanstd(a, axis=0, keepdims=True)
    return a / np.where(sd > 0, sd, np.nan)


def par_correction(a_s: np.ndarray, a_p: np.ndarray, spei: np.ndarray, season: np.ndarray, min_spei: float,
                   min_days: int):
    """Daily SIF/APAR anomaly corrected for PAR. Both daily anomalies are scaled by their whole-period SD (z); the
    slope b of z_s on z_p (least squares with intercept) is fitted per cell only on season days with SPEI >= min_spei
    (outside drought), and z_s - b * z_p is returned for all days. Cells with fewer than min_days fit days: NaN.
    Returns (corrected (time, cell), b (cell), n_fit (cell))."""
    zs, zp = _sd_scale(a_s), _sd_scale(a_p)
    m = season[:, None] & np.isfinite(spei) & (spei >= min_spei) & np.isfinite(zs) & np.isfinite(zp)
    n = m.sum(0)
    x, y = np.where(m, zp, 0.0), np.where(m, zs, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        mx, my = x.sum(0) / n, y.sum(0) / n
        dx, dy = np.where(m, zp - mx, 0.0), np.where(m, zs - my, 0.0)
        b = (dx * dy).sum(0) / (dx * dx).sum(0)
    b = np.where(n >= min_days, b, np.nan)
    return zs - b[None, :] * zp, b, n


# =============================================================================================== noise

def noise_stats(a: np.ndarray):
    """Per cell: D = var(x[t+1] - x[t]) / 2 over consecutive calendar days both valid, V = var(x) over valid days,
    and the noise fraction f = D / V (white day-to-day part of the variance, assuming a slow signal)."""
    d = a[1:] - a[:-1]
    with np.errstate(invalid="ignore"):
        D = np.nanvar(d, axis=0) / 2
        V = np.nanvar(a, axis=0)
        f = D / V
    return D, V, f


def noise_variance(D, V, f_target, f_cap: float):
    """Variance of white noise to add so that the noise fraction becomes f_target: (D + s2) / (V + s2) = f_target.
    Zero when the series is already at least as noisy; targets above f_cap are capped."""
    ft = np.minimum(f_target, f_cap)
    with np.errstate(invalid="ignore", divide="ignore"):
        s2 = (ft * V - D) / (1 - ft)
    return np.where(np.isfinite(s2) & (s2 > 0), s2, 0.0)


def degrade(a: np.ndarray, s2: float, rng: np.random.Generator) -> np.ndarray:
    """Add white Gaussian noise of variance s2 on the valid days of a daily anomaly series (time,)."""
    return a + rng.normal(0.0, np.sqrt(s2), a.shape) if s2 > 0 else a.copy()


# =============================================================================================== analysis 1b

def lagged_season_signed(s: np.ndarray, days: np.ndarray, months: list[int], lags: np.ndarray) -> np.ndarray:
    """(n_lags, year, day-of-season) array of s(t - L) for the season days t; L < 0 reads s after t."""
    out = []
    for L in lags:
        sh = np.full_like(s, np.nan)
        if L > 0:
            sh[L:] = s[:-L]
        elif L < 0:
            sh[:L] = s[-L:]
        else:
            sh[:] = s
        out.append(q1.season_arrays(sh, days, months)[0])
    return np.stack(out)


def _partial_max(vs: np.ndarray, ps: np.ndarray, expl: np.ndarray) -> tuple[float, int, int]:
    """Max over (scale, lag) of the partial correlation of vegetation with the explanatory variable given PAR (same
    day t as vegetation). vs, ps: (year, day); expl: (scale, lag, year, day). Descriptive (no permutation)."""
    rxy = q1.pooled_corr(vs, expl)
    ryz = q1.pooled_corr(ps, expl)
    rxz = float(q1.pooled_corr(vs, ps))
    with np.errstate(invalid="ignore"):
        pr = (rxy - rxz * ryz) / np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    if not np.isfinite(pr).any():
        return np.nan, -1, -1
    i_s, i_l = np.unravel_index(np.nanargmax(pr), pr.shape)
    return float(pr[i_s, i_l]), int(i_s), int(i_l)


def _row(c, v, ex, r, scales, lags, with_p):
    return {"cell": c, "variable": v, "explanatory": ex, "r": r["r"], "p": r["p"] if with_p else np.nan,
            "scale_days": scales[r["i_scale"]] if (r["i_scale"] >= 0 and ex == "spei") else np.nan,
            "lag_days": lags[r["i_lag"]] if r["i_lag"] >= 0 else np.nan,
            "r_h2": r["r_h2"], "p_h2": r["p_h2"] if with_p else np.nan,
            "lag_h2": lags[r["i_lag_h2"]] if r["i_lag_h2"] >= 0 else np.nan}


def _cell_task_a1(args) -> list:
    """Analysis 1b for one cell: scale and lag of maximum correlation of the main variables (SIF/APAR corrected for
    PAR) with SPEI (and AED), lags -15..+60, permutation test as question 1; partial correlation given PAR."""
    (c, z_c, spei_c, days, scales, lags, months, h2_i, n_perm, seed, with_aed, partial) = args
    rng = np.random.default_rng([seed, c])
    expl = np.stack([lagged_season_signed(spei_c[s], days, months, lags) for s in scales])
    aed_l = lagged_season_signed(z_c["aed"], days, months, lags)[None] if with_aed else None
    rows = []
    for v in MAIN:
        vs = q1.season_arrays(z_c[v], days, months)[0]
        r = q1.max_corr_cell(vs, expl, +1, n_perm, rng, h2_i)
        rows.append(_row(c, v, "spei", r, scales, lags, True))
        if aed_l is not None:
            ra = q1.max_corr_cell(vs, aed_l, -1, n_perm, rng, None)
            rows.append(_row(c, v, "aed", ra, scales, lags, True))
    if partial:
        vs = q1.season_arrays(z_c["sif_apar_raw"], days, months)[0]
        ps = q1.season_arrays(z_c["par"], days, months)[0]
        pr, i_s, i_l = _partial_max(vs, ps, expl)
        rows.append({"cell": c, "variable": "sif_apar_raw", "explanatory": "spei_given_par", "r": pr, "p": np.nan,
                     "scale_days": scales[i_s] if i_s >= 0 else np.nan, "lag_days": lags[i_l] if i_l >= 0 else np.nan,
                     "r_h2": np.nan, "p_h2": np.nan, "lag_h2": np.nan})
    return rows


def _cell_task_noise(args) -> list:
    """Noise test for one cell: NDVI and EVI daily anomalies degraded to the noise fraction of SIF/APAR (corrected),
    then smoothed and standardised as the main run, and the analysis 1 maximum and permutation test recomputed."""
    (c, a_c, s2_c, spei_c, days, scales, lags, months, h2_i, n_perm, rep_seed, qa, mode) = args
    expl = np.stack([lagged_season_signed(spei_c[s], days, months, lags) for s in scales])
    rows = []
    for k, v in enumerate(("ndvi", "evi")):
        rng_n = np.random.default_rng([rep_seed, c, k])
        rng_p = np.random.default_rng([rep_seed, c, 100 + k])
        a = degrade(a_c[v], s2_c[v], rng_n)
        z = smooth_standardise(a[:, None], qa, mode)[:, 0]
        r = q1.max_corr_cell(q1.season_arrays(z, days, months)[0], expl, +1, n_perm, rng_p, h2_i)
        rows.append({**_row(c, v, "spei", r, scales, lags, True), "replicate_seed": rep_seed,
                     "noise_var": s2_c[v]})
    return rows


def _map(fn, tasks, workers):
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            return list(ex.map(fn, tasks, chunksize=16))
    return [fn(t) for t in tasks]


def daily_anomalies(cfg: dict, ds: xr.Dataset, par: np.ndarray | None) -> dict:
    """Daily (unsmoothed) median-by-DOY anomalies of the main variables, AED and PAR; SIF/APAR corrected for PAR."""
    q, qb = cfg["drought_q1"], cfg["drought_q1b"]
    win = int(cfg["anomalies"]["clim_doy_window"])
    days = ds["time"].values.astype("datetime64[D]")
    a = {v: anomalies.anomaly_median_doy(ds[v].values.astype(float), days, win) for v in MAIN + ["aed"]}
    out = {"raw": a}
    if par is not None:
        pc = qb["par_correction"]
        a["par"] = anomalies.anomaly_median_doy(par, days, win)
        mo = pd.DatetimeIndex(ds["time"].values).month
        season = np.isin(mo, [int(m) for m in q["analysis1"]["months"]])
        spei = ds[f"spei_{int(pc['fit_spei_scale_days']):03d}"].values.astype(float)
        corr, b, n = par_correction(a["sif_apar"], a["par"], spei, season, float(pc["fit_min_spei"]),
                                    int(pc["min_days"]))
        out.update({"sif_apar_corr": corr, "b": b, "n_fit": n})
    return out


def run_analysis1(cfg: dict, ds: xr.Dataset, par: np.ndarray, mode: str, workers: int, n_perm: int | None = None,
                  with_aed: bool = True, partial: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Analysis 1b on all cells. mode: 'backward' (main) or 'centred' (sensitivity). Returns (cells, par_fit)."""
    q, qb = cfg["drought_q1"], cfg["drought_q1b"]
    a1, a1b = q["analysis1"], qb["analysis1"]
    qa = q["anomalies"]
    days = ds["time"].values.astype("datetime64[D]")
    scales = [int(s) for s in q["spei"]["scales_days"]]
    lags = np.arange(int(a1b["lags_days"][0]), int(a1b["lags_days"][1]) + 1)
    months = [int(m) for m in a1["months"]]
    h2_i = scales.index(int(a1["h2_scale_days"]))
    n_perm = int(a1["permutations"]) if n_perm is None else n_perm
    da = daily_anomalies(cfg, ds, par)
    z = {"sif_apar": smooth_standardise(da["sif_apar_corr"], qa, mode),
         "ndvi": smooth_standardise(da["raw"]["ndvi"], qa, mode), "evi": smooth_standardise(da["raw"]["evi"], qa, mode),
         "aed": smooth_standardise(da["raw"]["aed"], qa, mode),
         "sif_apar_raw": smooth_standardise(da["raw"]["sif_apar"], qa, mode),
         "par": smooth_standardise(da["raw"]["par"], qa, mode)}
    sp = {s: ds[f"spei_{s:03d}"].values.astype(float) for s in scales}
    seed = int(cfg["random_seed"])
    tasks = [(c, {v: z[v][:, c] for v in z}, {s: sp[s][:, c] for s in scales}, days, scales, lags, months, h2_i,
              n_perm, seed, with_aed, partial) for c in range(ds.sizes["cell"])]
    res = pd.DataFrame([r for rc in _map(_cell_task_a1, tasks, workers) for r in rc])
    meta = ds[["iy", "ix", "lon", "lat", "fuel_class", "stratum", "aridity_class"]].to_dataframe().reset_index()
    res = res.merge(meta, on="cell", how="left")
    fit = meta.assign(b_par=da["b"], n_fit_days=da["n_fit"])
    return res, fit


def h2b_test(res: pd.DataFrame, a: str, b: str, alpha: float, max_diff: float, n_boot: int, deg: float, seed: int,
             lag_bounds: tuple[int, int]) -> dict:
    """H2b: H2 rule on cells significant at the fixed scale in both and with no lag at a boundary of the lag range.
    Also returns the number of cells excluded for a boundary lag."""
    s = res[res["explanatory"] == "spei"]
    w = s.pivot_table(index=["cell", "lon", "lat"], columns="variable", values=["lag_h2", "p_h2"]).dropna()
    if w.empty or ("p_h2", a) not in w or ("p_h2", b) not in w:
        return {"n_cells": 0, "n_boundary_excluded": 0, "median_diff": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
                "met": False}
    w = w[(w[("p_h2", a)] < alpha) & (w[("p_h2", b)] < alpha)]
    edge = w[("lag_h2", a)].isin(lag_bounds) | w[("lag_h2", b)].isin(lag_bounds)
    n_edge = int(edge.sum())
    w = w[~edge]
    if w.empty:
        return {"n_cells": 0, "n_boundary_excluded": n_edge, "median_diff": np.nan, "ci_lo": np.nan,
                "ci_hi": np.nan, "met": False}
    sub = w.copy()
    sub.columns = [f"{x}_{y}" for x, y in sub.columns]
    flat = pd.DataFrame({"cell": sub.index.get_level_values("cell"), "lon": sub.index.get_level_values("lon"),
                         "lat": sub.index.get_level_values("lat"), "variable": a, "lag_h2": sub[f"lag_h2_{a}"].values,
                         "p_h2": sub[f"p_h2_{a}"].values})
    flat = pd.concat([flat, flat.assign(variable=b, lag_h2=sub[f"lag_h2_{b}"].values, p_h2=sub[f"p_h2_{b}"].values)])
    out = q1.h2_test(flat, a, b, alpha, max_diff, n_boot, deg, seed)
    out["n_boundary_excluded"] = n_edge
    return out


def boundary_share(res: pd.DataFrame, alpha: float, lag_bounds: tuple[int, int]) -> pd.DataFrame:
    """Share of cells significant at the fixed scale whose lag at that scale is at each boundary, by stratum."""
    s = res[(res["explanatory"] == "spei") & (res["p_h2"] < alpha) & res["variable"].isin(MAIN)]
    g = s.groupby(["stratum", "variable"])["lag_h2"]
    return pd.DataFrame({"n_cells": g.size(), "share_lower": g.apply(lambda x: (x == lag_bounds[0]).mean()),
                         "share_upper": g.apply(lambda x: (x == lag_bounds[1]).mean())}).reset_index()


# =============================================================================================== analysis 2b (H3b)

def observed(z: np.ndarray, onset: int, a2: dict, min_frac: float) -> bool:
    """A variable is observed in an episode if its smoothed anomaly is finite on >= min_frac of the days of the
    response window extended by the run length (onset - 30 .. onset + 90 + response_min_days - 1)."""
    w0, w1 = (int(x) for x in a2["response_window_days"])
    i0, i1 = max(onset + w0, 0), min(onset + w1 + int(a2["response_min_days"]), len(z))
    seg = z[i0:i1]
    return bool(seg.size and np.isfinite(seg).mean() >= min_frac)


def episode_responses(ep: pd.DataFrame, z: dict, days: np.ndarray, a2: dict, min_frac: float,
                      prefix: str = "") -> pd.DataFrame:
    """Add response day (q1.response_day; NaN = no response in the window) and observed flag per variable."""
    ep = ep.copy()
    t0 = days[0]
    for v in MAIN:
        rs, ob = [], []
        for c, od in zip(ep["cell"], ep["onset_day"]):
            o = int(od)
            assert days[o] - t0 == np.timedelta64(o, "D")
            ob.append(observed(z[v][:, c], o, a2, min_frac))
            rs.append(q1.response_day(z[v][:, c], o, a2))
        ep[f"{prefix}resp_{v}"] = rs
        ep[f"{prefix}obs_{v}"] = ob
    return ep


def pair_scores(ep: pd.DataFrame, a: str, b: str, censor: int, prefix: str = "") -> pd.DataFrame:
    """Paired comparison per cell-episode in events (both variables observed): score -1 if `a` responds first or
    `b` is censored, +1 the reverse, 0 tie; d = Ta - Tb, or the bound Ta - censor / censor - Tb when one is
    censored. Doubly censored pairs are kept with informative = False."""
    e = ep[(ep["event"] >= 0) & ep[f"{prefix}obs_{a}"] & ep[f"{prefix}obs_{b}"]].copy()
    ta, tb = e[f"{prefix}resp_{a}"].to_numpy(float), e[f"{prefix}resp_{b}"].to_numpy(float)
    fa, fb = np.isfinite(ta), np.isfinite(tb)
    score = np.full(len(e), np.nan)
    d = np.full(len(e), np.nan)
    both = fa & fb
    score[both], d[both] = np.sign(ta[both] - tb[both]), ta[both] - tb[both]
    oa = fa & ~fb
    score[oa], d[oa] = -1.0, ta[oa] - censor
    ob = ~fa & fb
    score[ob], d[ob] = 1.0, censor - tb[ob]
    e["score"], e["d"], e["informative"] = score, d, fa | fb
    return e


def h3b_test(ep: pd.DataFrame, a: str, b: str, censor: int, max_diff: float, min_events: int, n_boot: int,
             seed: int, prefix: str = "") -> dict:
    """H3b: (a) mean over events of the event mean score < 0 with the bootstrap CI over events entirely below 0, and
    (b) median over events of the event median d <= max_diff. Evaluable only with >= min_events events having an
    informative cell."""
    e = pair_scores(ep, a, b, censor, prefix) if len(ep) else pd.DataFrame()
    base = {"n_events": 0, "n_pairs_informative": 0, "n_pairs_doubly_censored": 0, "n_pairs_unobserved": 0,
            "mean_score": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "median_d": np.nan,
            "share_sif_first": np.nan, "evaluable": False, "met": False}
    if e.empty:
        return base
    inf = e[e["informative"]]
    in_ev = ep[ep["event"] >= 0]
    base["n_pairs_unobserved"] = int(len(in_ev) - len(e))
    base["n_pairs_doubly_censored"] = int((~e["informative"]).sum())
    base["n_pairs_informative"] = int(len(inf))
    if inf.empty:
        return base
    g = inf.groupby("event")
    ms, md = g["score"].mean().to_numpy(), g["d"].median().to_numpy()
    rng = np.random.default_rng(seed)
    boots = [np.mean(rng.choice(ms, ms.size, replace=True)) for _ in range(n_boot)]
    lo, hi = np.quantile(boots, [0.025, 0.975])
    ok = ms.size >= min_events
    est, mdd = float(np.mean(ms)), float(np.median(md))
    base.update({"n_events": int(ms.size), "mean_score": est, "ci_lo": float(lo), "ci_hi": float(hi),
                 "median_d": mdd, "share_sif_first": float((inf["score"] < 0).mean()), "evaluable": bool(ok),
                 "met": bool(ok and est < 0 and hi < 0 and mdd <= max_diff)})
    return base


def event_season(ep: pd.DataFrame, seasons: dict) -> pd.Series:
    """Season of each event from the median onset month of its cells (descriptive stratum)."""
    e = ep[ep["event"] >= 0]
    m = pd.to_datetime(e["onset"]).dt.month.groupby(e["event"]).median().round().astype(int)
    lab = {mm: s for s, ms in seasons.items() for mm in ms}
    return m.map(lab)


# =============================================================================================== decision

def outcome(h3b_evaluable: bool, h3b_met: bool, h1_corr: bool, h1_robust: bool, h2b: bool) -> str:
    """Per reference: not conclusive if H3b is not evaluable; contrary if evaluable and not met; support if H3b and
    ((H1 corrected and robust) or H2b); otherwise (H3b met without analysis 1 support) not conclusive."""
    if not h3b_evaluable:
        return "not_conclusive"
    if not h3b_met:
        return "contrary"
    if (h1_corr and h1_robust) or h2b:
        return "support"
    return "not_conclusive"


def overall(outcomes: list[str]) -> str:
    """Shrubland decision over the two references: support if support against both; contrary if contrary against
    any; otherwise not conclusive."""
    if all(o == "support" for o in outcomes):
        return "support"
    if any(o == "contrary" for o in outcomes):
        return "contrary"
    return "not_conclusive"


def robust_h1(rows: pd.DataFrame) -> dict:
    """H1 robust from the per-replicate H1 results (columns fraction, ci_lo, ci_hi, met, replicate_seed): H1 in the
    replicate with the median fraction (odd number of replicates)."""
    r = rows.sort_values(["fraction", "replicate_seed"]).reset_index(drop=True)
    m = r.iloc[len(r) // 2]
    return {"fraction": m["fraction"], "ci_lo": m["ci_lo"], "ci_hi": m["ci_hi"], "met": bool(m["met"]),
            "median_replicate_seed": int(m["replicate_seed"]), "n_replicates_met": int(r["met"].sum())}


# =============================================================================================== driver

def decide(cfg: dict, res_m: pd.DataFrame, res_c: pd.DataFrame | None, noise: pd.DataFrame | None,
           ep: pd.DataFrame):
    """All Q1b tests by stratum and reference, and the outcome (support / contrary / not conclusive).
    res_m: analysis 1b cells (main smoothing); res_c: centred sensitivity or None; noise: noise_cells or None;
    ep: analysis 2b episodes (may be empty). Returns (tests, decision, per-replicate robust H1)."""
    q, qb = cfg["drought_q1"], cfg["drought_q1b"]
    strata = list(q["strata"])
    a1 = q["analysis1"]
    alpha, seed, nb, deg = float(a1["alpha"]), int(cfg["random_seed"]), int(q["bootstrap_n"]), \
        float(a1["bootstrap_block_deg"])
    lb = (int(qb["analysis1"]["lags_days"][0]), int(qb["analysis1"]["lags_days"][1]))
    hb = qb["h3b"]
    rows, robust_rows = [], []
    mx = float(a1["h2_max_median_lag_diff_days"])
    for st in strata + ["wet_heath_only"]:
        rs = _strata_rows(res_m, st)
        es = _strata_rows(ep, st) if len(ep) else ep
        for b in ("ndvi", "evi"):
            spei_rs = rs[rs["explanatory"] == "spei"]
            h1 = q1.h1_test(spei_rs, "sif_apar", b, alpha, float(a1["h1_min_fraction"]), nb, deg, seed)
            h2 = h2b_test(rs, "sif_apar", b, alpha, mx, nb, deg, seed, lb)
            rows += [{"stratum": st, "against": b, "test": "H1_par_corrected", **h1},
                     {"stratum": st, "against": b, "test": "H2b", **h2}]
            if noise is not None:
                reps = []
                for r_seed, g in noise.groupby("replicate_seed"):
                    gs = _strata_rows(g, st)
                    deg_b = gs[gs["variable"] == b]
                    sif = spei_rs[spei_rs["variable"] == "sif_apar"]
                    h = q1.h1_test(pd.concat([sif, deg_b]), "sif_apar", b, alpha, float(a1["h1_min_fraction"]), nb,
                                   deg, seed)
                    reps.append({"replicate_seed": r_seed, **h})
                    robust_rows.append({"stratum": st, "against": b, "replicate_seed": r_seed, **h})
                rows.append({"stratum": st, "against": b, "test": "H1_robust_noise", **robust_h1(pd.DataFrame(reps))})
            if res_c is not None:
                rc = _strata_rows(res_c, st)
                rows += [{"stratum": st, "against": b, "test": "H1_centred_sens", **q1.h1_test(
                             rc[rc["explanatory"] == "spei"], "sif_apar", b, alpha, float(a1["h1_min_fraction"]), nb,
                             deg, seed)},
                         {"stratum": st, "against": b, "test": "H2b_centred_sens",
                          **h2b_test(rc, "sif_apar", b, alpha, mx, nb, deg, seed, lb)}]
            # partial-correlation sensitivity: scale of max partial r of raw SIF/APAR vs scale of the reference
            pr = rs[rs["explanatory"] == "spei_given_par"][["cell", "lon", "lat", "scale_days"]] \
                .assign(variable="sif_apar", p=0.0)
            sig_sif = set(spei_rs.loc[(spei_rs["variable"] == "sif_apar") & (spei_rs["p"] < alpha), "cell"])
            pr = pr[pr["cell"].isin(sig_sif)]
            rows.append({"stratum": st, "against": b, "test": "H1_partial_sens",
                         **q1.h1_test(pd.concat([pr, spei_rs[spei_rs["variable"] == b]]), "sif_apar", b, alpha,
                                      float(a1["h1_min_fraction"]), nb, deg, seed)})
            for pref, name in (("", "H3b"), ("bwcorr_", "H3b_backward_par_corrected_sens")):
                if len(es) and f"{pref}obs_{b}" in es:
                    h3 = h3b_test(es, "sif_apar", b, int(hb["censor_day"]), float(hb["max_median_diff_days"]),
                                  int(hb["min_events"]), nb, seed, pref)
                else:
                    h3 = {"evaluable": False, "met": False, "n_events": 0}
                rows.append({"stratum": st, "against": b, "test": name, **h3})
            if len(es):
                for sn in hb["seasons"]:
                    ss = es[es["event_season"] == sn]
                    h3 = h3b_test(ss, "sif_apar", b, int(hb["censor_day"]), float(hb["max_median_diff_days"]),
                                  int(hb["min_events"]), nb, seed) if len(ss) else {"evaluable": False, "met": False,
                                                                                     "n_events": 0}
                    rows.append({"stratum": st, "against": b, "test": f"H3b_season_{sn}_descriptive", **h3})
    d = pd.DataFrame(rows)
    get = d.set_index(["stratum", "against", "test"])
    dec = []
    for st in strata + ["wet_heath_only"]:
        outs = []
        for b in ("ndvi", "evi"):
            def g(t, col="met", st=st, b=b):
                return bool(get.loc[(st, b, t), col]) if (st, b, t) in get.index else False
            o = outcome(g("H3b", "evaluable"), g("H3b"), g("H1_par_corrected"), g("H1_robust_noise"), g("H2b"))
            outs.append(o)
            dec.append({"stratum": st, "against": b, "outcome": o})
        dec.append({"stratum": st, "against": "both", "outcome": overall(outs)})
    return d, pd.DataFrame(dec), pd.DataFrame(robust_rows)


def _strata_rows(df: pd.DataFrame, st: str) -> pd.DataFrame:
    return df[df["fuel_class"] == "wet_heath"] if st == "wet_heath_only" else df[df["stratum"] == st]


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("step", choices=["count", "par", "analysis1", "analysis2", "noise", "decide"])
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--mode", choices=["backward", "centred"], default="backward")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    q, qb = cfg["drought_q1"], cfg["drought_q1b"]
    od = REPO_ROOT / qb["out_dir"]
    od.mkdir(parents=True, exist_ok=True)
    ds = xr.open_dataset(REPO_ROOT / q["out_dir"] / "drought_q1_series.nc").load()
    days = ds["time"].values.astype("datetime64[D]")
    strata = list(q["strata"])
    a1, a2 = q["analysis1"], q["analysis2"]
    alpha, seed, nb, deg = float(a1["alpha"]), int(cfg["random_seed"]), int(q["bootstrap_n"]), \
        float(a1["bootstrap_block_deg"])
    e = qb["episodes"]

    if args.step == "count":                                    # SPEI only: no vegetation variable is read
        counts = {}
        for d in e["order"]:
            ep = episode_table(d, ds[["spei_090", f"spei_{int(e['C']['spei_scale_days']):03d}", "iy", "ix", "lon",
                                      "lat", "fuel_class", "stratum", "aridity_class"]], cfg)
            ep.to_csv(od / f"episodes_{d}.csv", index=False)
            counts[d] = count_events(ep, strata)
        ch = choose_definition(counts, e["order"], int(e["min_events"]))
        pd.DataFrame(counts).T.rename_axis("definition").reset_index().to_csv(od / "event_count.csv", index=False)
        (od / "definition.json").write_text(json.dumps({"chosen": ch, "counts": counts}, indent=1))
        log.info("counts %s; chosen definition %s", counts, ch)
        return

    if args.step == "par":
        inp = epoch.open_inputs(dict(cfg, epoch=dict(cfg["epoch"], optical_sensitivity=False)), q["cells"]["grid"])
        par = epoch._extract(inp["par"]["par"], inp["sif"]["sif"], ds["iy"].values, ds["ix"].values, days)
        xr.Dataset({"par": (("time", "cell"), par.astype("f4"))}, coords={"time": ds["time"], "cell": ds["cell"]}) \
            .to_netcdf(od / "par_series.nc", encoding={"par": {"zlib": True, "complevel": 4}})
        log.info("wrote PAR series")
        return

    par = xr.open_dataset(od / "par_series.nc")["par"].values.astype(float)
    lb = (int(qb["analysis1"]["lags_days"][0]), int(qb["analysis1"]["lags_days"][1]))

    if args.step == "analysis1":
        main_run = args.mode == qb["analysis1"]["smoothing"]
        res, fit = run_analysis1(cfg, ds, par, args.mode, args.workers, with_aed=main_run, partial=main_run)
        res.to_csv(od / f"analysis1b_cells_{args.mode}.csv", index=False)
        fit.to_csv(od / "par_fit.csv", index=False)
        log.info("analysis 1b (%s) done", args.mode)
        return

    if args.step == "analysis2":
        ch = json.loads((od / "definition.json").read_text())["chosen"]
        if ch is None:
            log.info("no definition reaches the minimum: H3b not evaluable")
            pd.DataFrame().to_csv(od / "analysis2b_episodes.csv", index=False)
            return
        ep = pd.read_csv(od / f"episodes_{ch}.csv")
        qa, win, mf = q["anomalies"], int(cfg["anomalies"]["clim_doy_window"]), float(qb["h3b"]["min_observed_frac"])
        z_main = {v: q1.standardised_anomaly(ds[v].values.astype(float), days, qa, win) for v in MAIN}
        ep = episode_responses(ep, z_main, days, a2, mf)
        da = daily_anomalies(cfg, ds, par)
        z_s = {"sif_apar": smooth_standardise(da["sif_apar_corr"], qa, "backward"),
               "ndvi": smooth_standardise(da["raw"]["ndvi"], qa, "backward"),
               "evi": smooth_standardise(da["raw"]["evi"], qa, "backward")}
        ep = episode_responses(ep, z_s, days, a2, mf, prefix="bwcorr_")
        ev_season = event_season(ep, qb["h3b"]["seasons"])
        ep["event_season"] = ep["event"].map(ev_season)
        ep.to_csv(od / "analysis2b_episodes.csv", index=False)
        log.info("analysis 2b: %d episodes", len(ep))
        return

    if args.step == "noise":
        res = pd.read_csv(od / f"analysis1b_cells_{qb['analysis1']['smoothing']}.csv")
        s = res[(res["explanatory"] == "spei") & (res["variable"] == "sif_apar")]
        cells = s.loc[s["p"] < alpha, "cell"].astype(int).to_numpy()   # H1 uses only cells significant in both
        da = daily_anomalies(cfg, ds, par)
        D_s, V_s, f_s = noise_stats(da["sif_apar_corr"])
        nz = qb["noise"]
        stats, s2 = [], {}
        for v in ("ndvi", "evi"):
            D, V, f = noise_stats(da["raw"][v])
            s2[v] = noise_variance(D, V, f_s, float(nz["f_cap"]))
            stats.append(pd.DataFrame({"cell": ds["cell"].values, "variable": v, "f": f, "f_sif_apar": f_s,
                                       "noise_var": s2[v], "V": V}))
        pd.concat(stats).merge(ds[["stratum", "fuel_class"]].to_dataframe().reset_index(), on="cell") \
            .to_csv(od / "noise_fraction.csv", index=False)
        scales = [int(x) for x in q["spei"]["scales_days"]]
        lags = np.arange(lb[0], lb[1] + 1)
        months = [int(m) for m in a1["months"]]
        h2_i = scales.index(int(a1["h2_scale_days"]))
        sp = {x: ds[f"spei_{x:03d}"].values.astype(float) for x in scales}
        out = []
        for rs in nz["replicate_seeds"]:
            tasks = [(int(c), {v: da["raw"][v][:, c] for v in ("ndvi", "evi")}, {v: float(s2[v][c]) for v in s2},
                      {x: sp[x][:, c] for x in scales}, days, scales, lags, months, h2_i, int(a1["permutations"]),
                      int(rs), q["anomalies"], qb["analysis1"]["smoothing"]) for c in cells]
            out += [r for rc in _map(_cell_task_noise, tasks, args.workers) for r in rc]
            log.info("noise replicate %s done (%d cells)", rs, len(cells))
        meta = ds[["iy", "ix", "lon", "lat", "fuel_class", "stratum", "aridity_class"]].to_dataframe().reset_index()
        pd.DataFrame(out).merge(meta, on="cell", how="left").to_csv(od / "noise_cells.csv", index=False)
        return

    # decide --------------------------------------------------------------------------------------------------------
    res_m = pd.read_csv(od / f"analysis1b_cells_{qb['analysis1']['smoothing']}.csv")
    sens_f = od / "analysis1b_cells_centred.csv"
    res_c = pd.read_csv(sens_f) if sens_f.exists() else None
    nf = od / "noise_cells.csv"
    noise = pd.read_csv(nf) if nf.exists() else None
    epf = od / "analysis2b_episodes.csv"
    ep = pd.read_csv(epf) if epf.exists() and epf.stat().st_size > 2 else pd.DataFrame()
    d, dec, robust_rows = decide(cfg, res_m, res_c, noise, ep)
    d.to_csv(od / "hypotheses_q1b.csv", index=False)
    robust_rows.to_csv(od / "noise_h1_replicates.csv", index=False)
    dec.to_csv(od / "decision_q1b.csv", index=False)
    sh = dec.loc[(dec["stratum"] == "shrubland") & (dec["against"] == "both"), "outcome"].iloc[0]
    (od / "decision_q1b.json").write_text(json.dumps({"shrubland": sh}, indent=1))
    log.info("Q1b decision (shrubland): %s", sh)


if __name__ == "__main__":
    main()
