"""Daily anomalies for the epoch analysis, following the epoch rules in CLAUDE.md.

Order of operations for one variable, per cell (arrays shaped (time, ncell)):
  1. Masking: all values on or after the cell's cut-off date are removed (ignition date of the fire for its
     cells in the main analysis; burn date for cells burned above the climatology threshold). Done BEFORE any
     statistic, so post-fire data never enter trends, seasonal cycles, filters or smoothing.
  2. Input validity (optional thresholds on fPAR, PAR, TROPOMI pixel weight).
  3. Isolated-spike filter (Hampel type): residual to the running median of the cell's own series;
     persistent anomalies are kept because the running median follows them.
  4. Anomalies, two definitions with equal weight:
       loess       x - LOESS trend - mean seasonal cycle of the detrended series (Tang et al., 2026)
       median_doy  x - median over all years of the values within DOY +- window
  5. Trailing means (windows ending on the evaluated day) for the epoch analysis.
No step uses data on or after the cut-off date; `tests/test_anomalies.py` checks this explicitly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.nonparametric.smoothers_lowess import lowess

NEVER = np.datetime64("2262-01-01")


# --------------------------------------------------------------------------- masking and validity

def apply_cutoff(x: np.ndarray, days: np.ndarray, cutoff: np.ndarray | None) -> np.ndarray:
    """Set to NaN all values on or after each cell's cut-off date. cutoff: (ncell,) datetime64[D], NaT = never."""
    if cutoff is None:
        return x.copy()
    cut = np.asarray(cutoff, dtype="datetime64[D]")
    cut = np.where(np.isnat(cut), NEVER, cut)
    after = np.asarray(days, dtype="datetime64[D]")[:, None] >= cut[None, :]
    return np.where(after, np.nan, x)


def validity_mask(fpar=None, par=None, sif_weight=None, fpar_min=None, par_min=None, weight_min=None) -> np.ndarray | None:
    """True where inputs are usable for SIF/APAR. Thresholds set to None are not applied."""
    mask = None
    for arr, thr in [(fpar, fpar_min), (par, par_min), (sif_weight, weight_min)]:
        if arr is None or thr is None:
            continue
        m = np.asarray(arr) >= thr
        mask = m if mask is None else (mask & m)
    return mask


# --------------------------------------------------------------------------- helpers

def day_of_year(days: np.ndarray) -> np.ndarray:
    return pd.DatetimeIndex(np.asarray(days, dtype="datetime64[ns]")).day_of_year.values


def _doy_pooled(x: np.ndarray, doys: np.ndarray, window: int, func) -> np.ndarray:
    """func (nanmedian/nanmean) of values within circular DOY distance <= window, pooled across years.
    Returns (367, ncell) indexed by DOY (row 0 unused)."""
    out = np.full((367, x.shape[1]), np.nan)
    for d in np.unique(doys):
        dist = np.abs(doys - d)
        dist = np.minimum(dist, 366 - dist)
        sel = dist <= window
        with np.errstate(all="ignore"):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                out[d] = func(x[sel], axis=0)
    return out


# --------------------------------------------------------------------------- spike filter

def spike_filter(x: np.ndarray, half_window: int, k: float, min_neighbours: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Hampel-type filter on each cell's own series. Residual r_t = x_t - median(x_{t-h..t+h}) (masked values
    excluded); robust noise scale s = 1.4826 median|r| over the cell's record; values with |r| > k s are removed.
    Returns (filtered x, boolean array of removed values)."""
    w = 2 * half_window + 1
    df = pd.DataFrame(x)
    med = df.rolling(w, center=True, min_periods=min_neighbours).median().values
    r = x - med
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            s = 1.4826 * np.nanmedian(np.abs(r), axis=0)
    removed = np.isfinite(r) & (np.abs(r) > k * s[None, :]) & (s[None, :] > 0)
    return np.where(removed, np.nan, x), removed


# --------------------------------------------------------------------------- anomalies

def anomaly_median_doy(x: np.ndarray, days: np.ndarray, window: int) -> np.ndarray:
    """x minus the median over all years of the values within DOY +- window."""
    doys = day_of_year(days)
    clim = _doy_pooled(x, doys, window, np.nanmedian)
    return x - clim[doys]


def loess_trend(x: np.ndarray, days: np.ndarray, frac: float, delta_days: float, min_obs: int) -> np.ndarray:
    """LOESS trend per cell on its valid values, evaluated (linear interpolation) at every day within the range of
    valid values; NaN outside it and for cells with fewer than min_obs valid values."""
    t = (np.asarray(days, dtype="datetime64[D]") - np.asarray(days, dtype="datetime64[D]")[0]).astype(float)
    out = np.full(x.shape, np.nan)
    for j in range(x.shape[1]):
        ok = np.isfinite(x[:, j])
        if ok.sum() < min_obs:
            continue
        fit = lowess(x[ok, j], t[ok], frac=frac, it=0, delta=delta_days, return_sorted=True)
        lo, hi = fit[0, 0], fit[-1, 0]
        inside = (t >= lo) & (t <= hi)
        out[inside, j] = np.interp(t[inside], fit[:, 0], fit[:, 1])
    return out


def anomaly_loess(x: np.ndarray, days: np.ndarray, frac: float, delta_days: float, min_obs: int,
                  window: int) -> np.ndarray:
    """Tang et al. (2026): x - LOESS trend - mean daily seasonal cycle of the detrended series
    (pooled over DOY +- window across years)."""
    detr = x - loess_trend(x, days, frac, delta_days, min_obs)
    doys = day_of_year(days)
    cycle = _doy_pooled(detr, doys, window, np.nanmean)
    return detr - cycle[doys]


def trailing_mean(x: np.ndarray, window: int, min_frac: float) -> np.ndarray:
    """Mean over the `window` days ending on each day (inclusive); NaN if fewer than min_frac x window valid days."""
    minp = max(1, int(np.ceil(min_frac * window)))
    return pd.DataFrame(x).rolling(window, min_periods=minp).mean().values


# --------------------------------------------------------------------------- pipeline

def compute(x: np.ndarray, days: np.ndarray, acfg: dict, cutoff: np.ndarray | None = None,
            valid: np.ndarray | None = None) -> dict[str, np.ndarray]:
    """Full chain for one variable. x: (time, ncell). Returns the masked/filtered input, the spike mask, raw
    anomalies per method and their trailing means per window: keys 'x', 'spikes', '<method>',
    '<method>_trail<w>'."""
    x = apply_cutoff(np.asarray(x, dtype=float), days, cutoff)
    if valid is not None:
        x = np.where(valid, x, np.nan)
    x, spikes = spike_filter(x, int(acfg["spike_half_window"]), float(acfg["spike_k"]),
                             int(acfg["spike_min_neighbours"]))
    out = {"x": x, "spikes": spikes}
    for m in acfg["methods"]:
        if m == "loess":
            a = anomaly_loess(x, days, float(acfg["loess_frac"]), float(acfg["loess_delta_days"]),
                              int(acfg["loess_min_obs"]), int(acfg["clim_doy_window"]))
        elif m == "median_doy":
            a = anomaly_median_doy(x, days, int(acfg["clim_doy_window"]))
        else:
            raise ValueError(f"unknown anomaly method {m}")
        a = apply_cutoff(a, days, cutoff)       # defensive: nothing after the cut-off, ever
        out[m] = a
        for w in acfg["trailing_days"]:
            out[f"{m}_trail{w}"] = apply_cutoff(trailing_mean(a, int(w), float(acfg["trailing_min_frac"])), days, cutoff)
    return out
