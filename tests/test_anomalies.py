"""Synthetic tests for the anomaly chain, with emphasis on the absence of post-fire leakage."""

import numpy as np
import pytest

from physiofire.anomalies import (anomaly_loess, anomaly_median_doy, apply_cutoff, compute, spike_filter,
                                  trailing_mean, validity_mask)

ACFG = {"loess_frac": 0.4, "loess_delta_days": 10, "loess_min_obs": 365, "clim_doy_window": 15,
        "trailing_days": [15, 7], "trailing_min_frac": 0.5, "spike_half_window": 3, "spike_k": 6,
        "spike_min_neighbours": 3, "methods": ["loess", "median_doy"]}

DAYS = np.arange(np.datetime64("2018-05-01"), np.datetime64("2026-05-01"), dtype="datetime64[D]")
T = len(DAYS)
RNG = np.random.default_rng(42)


def seasonal(n_cells=3, trend=0.0, noise=0.02):
    t = np.arange(T)
    doy = (DAYS - DAYS.astype("datetime64[Y]")).astype(int)
    base = 0.5 + 0.2 * np.sin(2 * np.pi * doy / 365.25) + trend * t / 365.25
    return base[:, None] + noise * RNG.standard_normal((T, n_cells))


# --------------------------------------------------------------------------- masking

def test_apply_cutoff_with_nat():
    x = np.ones((T, 2))
    cut = np.array([np.datetime64("2025-08-10"), np.datetime64("NaT")], dtype="datetime64[D]")
    y = apply_cutoff(x, DAYS, cut)
    i = int(np.where(DAYS == np.datetime64("2025-08-10"))[0][0])
    assert np.all(np.isfinite(y[:i, 0])) and np.all(np.isnan(y[i:, 0]))   # cut-off day itself masked
    assert np.all(np.isfinite(y[:, 1]))


def test_validity_mask_skips_none_thresholds():
    f = np.array([0.05, 0.3])
    assert validity_mask(fpar=f, fpar_min=None) is None
    assert validity_mask(fpar=f, fpar_min=0.1).tolist() == [False, True]


# --------------------------------------------------------------------------- trailing windows

def test_trailing_mean_uses_only_past():
    x = RNG.standard_normal((100, 1))
    a = trailing_mean(x, 7, 0.5)
    x2 = x.copy()
    x2[50:] += 100                                  # change the future
    b = trailing_mean(x2, 7, 0.5)
    assert np.allclose(a[:50], b[:50], equal_nan=True)
    assert np.isclose(a[20, 0], x[14:21, 0].mean())


# --------------------------------------------------------------------------- spike filter

def test_spike_filter_removes_isolated_spike_keeps_persistent_drop():
    x = seasonal(1, noise=0.01)
    spike, drop0 = 400, 800
    x[spike] += 0.5                                 # one-day spike
    x[drop0:drop0 + 12] -= 0.3                      # 12-day stress-like drop (30 x noise)
    y, removed = spike_filter(x, 3, 6)
    assert removed[spike, 0]
    assert not removed[drop0 + 3:drop0 + 9, 0].any()  # interior of the persistent drop kept
    assert removed.mean() < 0.01


# --------------------------------------------------------------------------- anomalies

def test_median_doy_recovers_injected_anomaly():
    x = seasonal(2, noise=0.005)
    i0 = int(np.where(DAYS == np.datetime64("2022-07-10"))[0][0])
    x[i0:i0 + 20, 0] -= 0.2
    a = anomaly_median_doy(x, DAYS, 15)
    assert np.isclose(np.nanmean(a[i0 + 5:i0 + 15, 0]), -0.2, atol=0.03)
    assert abs(np.nanmean(a[:, 1])) < 0.02


def test_loess_removes_trend_and_recovers_anomaly():
    x = seasonal(1, trend=0.03, noise=0.005)
    i0 = int(np.where(DAYS == np.datetime64("2023-07-10"))[0][0])
    x[i0:i0 + 20, 0] -= 0.2
    a = anomaly_loess(x, DAYS, 0.4, 10, 365, 15)
    other = np.ones(T, bool)
    other[i0 - 30:i0 + 50] = False
    assert abs(np.nanmean(a[other, 0])) < 0.01                       # trend removed
    assert np.nanmean(a[i0 + 5:i0 + 15, 0]) < -0.15                  # anomaly recovered (~-0.2, minus 1/8 in cycle)


# --------------------------------------------------------------------------- no post-fire leakage (key test)

@pytest.mark.parametrize("perturb", ["shift", "nan", "noise"])
def test_no_post_cutoff_leakage(perturb):
    """Pre-cut-off outputs must not change when post-cut-off data change (burn scar, smoke, anything)."""
    x = seasonal(3, trend=0.01, noise=0.02)
    cut = np.array(["2025-08-10", "2021-07-01", "NaT"], dtype="datetime64[D]")
    a = compute(x, DAYS, ACFG, cutoff=cut)
    x2 = x.copy()
    after = DAYS[:, None] >= np.where(np.isnat(cut), np.datetime64("2262-01-01"), cut)[None, :]
    if perturb == "shift":
        x2[after] -= 0.4                            # post-fire collapse
    elif perturb == "nan":
        x2[after] = np.nan
    else:
        x2[after] += RNG.standard_normal(after.sum())
    b = compute(x2, DAYS, ACFG, cutoff=cut)
    for key in a:
        if key == "spikes":
            continue
        assert np.allclose(a[key], b[key], equal_nan=True), key
        assert np.all(np.isnan(a[key][after])), key  # and nothing is ever reported after the cut-off


def test_without_cutoff_post_data_would_leak():
    """Sanity check of the test design: without the cut-off, the same perturbation does change pre-fire outputs."""
    x = seasonal(1, trend=0.01, noise=0.02)
    i = int(np.where(DAYS == np.datetime64("2025-08-10"))[0][0])
    a = compute(x, DAYS, ACFG)
    x2 = x.copy()
    x2[i:] -= 0.4
    b = compute(x2, DAYS, ACFG)
    assert not np.allclose(a["loess"][:i], b["loess"][:i], equal_nan=True)
