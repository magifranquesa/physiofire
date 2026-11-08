"""Synthetic tests of question 1 (physiofire.drought_q1): anomalies, correlation by pair sums, recovery of a known
scale and lag, permutation test (size under the null), H1/H2/H3 functions, drought onsets, response day and events."""
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from physiofire import drought_q1 as q1
from physiofire.config import load_config

CFG = load_config()
Q = CFG["drought_q1"]
DAYS = np.arange(np.datetime64("2018-05-01"), np.datetime64("2026-01-01"), dtype="datetime64[D]")
MONTHS = [4, 5, 6, 7, 8, 9, 10]


def _rolling(x, n):
    c = np.cumsum(np.concatenate([[0.0], x]))
    out = np.full(x.size, np.nan)
    out[n - 1:] = (c[n:] - c[:-n]) / np.sqrt(n)
    return out


def _spei_family(rng, scales, n_extra=400):
    """Synthetic standardised 'SPEI' at several scales from one daily water-balance series (with spin-up)."""
    d = rng.normal(size=DAYS.size + n_extra)
    out = {}
    for s in scales:
        r = _rolling(d, s)[n_extra:]
        out[s] = (r - np.nanmean(r)) / np.nanstd(r)
    return out


def test_centred_mean_and_min_frac():
    x = np.arange(20, dtype=float)[:, None]
    m = q1.centred_mean(x, 5, 0.5)
    assert m[10, 0] == 10.0                      # centred: no shift
    x[8:13] = np.nan
    m = q1.centred_mean(x, 5, 0.5)
    assert np.isnan(m[10, 0]) and np.isfinite(m[7, 0])   # day 7: 3 of 5 valid days


def test_pair_sums_equal_direct_correlation():
    rng = np.random.default_rng(1)
    v = rng.normal(size=(8, 214))
    e = rng.normal(size=(3, 4, 8, 214)) + 0.5 * v[None, None]
    v[0, :20] = np.nan
    e[1, 2, 3, 50:60] = np.nan
    ps = q1.pair_sums(v, e)
    r = q1.permuted_corr(ps, np.arange(8))
    np.testing.assert_allclose(r, q1.pooled_corr(v, e), rtol=1e-10)
    perm = rng.permutation(8)
    np.testing.assert_allclose(q1.permuted_corr(ps, perm), q1.pooled_corr(v[perm], e), rtol=1e-10)


def test_recovers_scale_and_lag():
    rng = np.random.default_rng(2)
    scales = [15, 30, 60, 90, 180, 365]
    sp = _spei_family(rng, scales)
    lags = np.arange(0, 61)
    true_s, true_l = 60, 12
    veg = np.full(DAYS.size, np.nan)
    veg[true_l:] = sp[true_s][:-true_l]
    veg = veg + rng.normal(0, 0.5, DAYS.size)
    expl = np.stack([q1.lagged_season(sp[s], DAYS, MONTHS, lags) for s in scales])
    vs = q1.season_arrays(veg, DAYS, MONTHS)[0]
    r = q1.max_corr_cell(vs, expl, +1, 49, np.random.default_rng(0), h2_index=scales.index(90))
    assert scales[r["i_scale"]] == true_s and abs(lags[r["i_lag"]] - true_l) <= 2, r
    assert r["p"] <= 0.05 and r["r"] > 0.5


def test_aed_sign():
    rng = np.random.default_rng(3)
    a = rng.normal(size=DAYS.size)
    a = q1.centred_mean(a[:, None], 15, 0.5)[:, 0]
    veg = np.full(DAYS.size, np.nan)
    veg[5:] = -a[:-5]
    veg += rng.normal(0, 0.2, DAYS.size)
    lags = np.arange(0, 61)
    al = q1.lagged_season(a, DAYS, MONTHS, lags)[None]
    r = q1.max_corr_cell(q1.season_arrays(veg, DAYS, MONTHS)[0], al, -1, 19, np.random.default_rng(0))
    assert r["r"] < -0.5 and abs(lags[r["i_lag"]] - 5) <= 1


def test_permutation_test_size_under_null():
    """Without any relation, the max-statistic test rejects in about alpha of the cells (not far more)."""
    rng = np.random.default_rng(4)
    scales = [15, 30, 90, 365]
    lags = np.arange(0, 61, 5)
    rej = []
    for k in range(60):
        sp = _spei_family(rng, scales)
        veg = q1.centred_mean(rng.normal(size=(DAYS.size, 1)), 15, 0.5)[:, 0]   # autocorrelated noise
        expl = np.stack([q1.lagged_season(sp[s], DAYS, MONTHS, lags) for s in scales])
        r = q1.max_corr_cell(q1.season_arrays(veg, DAYS, MONTHS)[0], expl, +1, 39, np.random.default_rng(k))
        rej.append(r["p"] < 0.05)
    assert np.mean(rej) <= 0.15, np.mean(rej)


def _res_table(n, a_scale, b_scale, a_lag, b_lag, p=0.01):
    rows = []
    for c in range(n):
        for v, s, lg in (("sif_apar", a_scale[c], a_lag[c]), ("ndvi", b_scale[c], b_lag[c])):
            rows.append({"cell": c, "lon": -5 + 0.3 * c, "lat": 40 + 0.1 * (c % 7), "variable": v,
                         "scale_days": s, "p": p, "lag_h2": lg, "p_h2": p})
    return pd.DataFrame(rows)


def test_h1_h2():
    n = 60
    res = _res_table(n, [30] * n, [90] * n, [5] * n, [15] * n)
    h1 = q1.h1_test(res, "sif_apar", "ndvi", 0.05, 0.6, 200, 1.0, 0)
    h2 = q1.h2_test(res, "sif_apar", "ndvi", 0.05, -5, 200, 1.0, 0)
    assert h1["fraction"] == 1.0 and h1["met"] and h2["median_diff"] == -10 and h2["met"]
    res = _res_table(n, [90] * n, [90] * n, [15] * n, [15] * n)   # ties: not shorter
    assert q1.h1_test(res, "sif_apar", "ndvi", 0.05, 0.6, 200, 1.0, 0)["fraction"] == 0.0
    assert not q1.h2_test(res, "sif_apar", "ndvi", 0.05, -5, 200, 1.0, 0)["met"]
    res = _res_table(n, [30] * n, [90] * n, [5] * n, [15] * n, p=0.5)   # not significant: excluded
    assert q1.h1_test(res, "sif_apar", "ndvi", 0.05, 0.6, 200, 1.0, 0)["n_cells"] == 0


def test_onsets_and_response():
    a2 = Q["analysis2"]
    s = np.full(DAYS.size, 0.5)
    o = int(np.where(DAYS == np.datetime64("2022-06-01"))[0][0])
    s[o:o + 40] = -1.5                                   # 40-day episode
    s[o + 200:o + 210] = -1.5                            # too short
    on = q1.find_onsets(s, DAYS, a2, (DAYS[0], DAYS[-1]))
    assert on == [o]
    s2 = s.copy(); s2[o - 30:o] = -0.7                   # pre-period not clean
    assert q1.find_onsets(s2, DAYS, a2, (DAYS[0], DAYS[-1])) == []
    z = np.zeros(DAYS.size)
    z[o - 10:o + 60] = -1.0                              # responds 10 days BEFORE the SPEI-90 crossing
    assert q1.response_day(z, o, a2) == -10
    z2 = z.copy(); z2[o - 3:o + 2] = np.nan               # gaps neither break nor count (10 of 15 valid)
    assert q1.response_day(z2, o, a2) == -10
    assert np.isnan(q1.response_day(np.zeros(DAYS.size), o, a2))


def test_events():
    rows = []
    for i in range(4):
        for j in range(3):
            rows.append({"cell": i * 3 + j, "iy": i, "ix": j, "onset_day": 100 + i})   # 12 contiguous cells
    rows.append({"cell": 99, "iy": 50, "ix": 50, "onset_day": 100})                    # isolated
    rows.append({"cell": 98, "iy": 0, "ix": 1, "onset_day": 300})                      # same place, later
    ep = pd.DataFrame(rows)
    ev = q1.build_events(ep, 15, 10)
    big = ev.iloc[:12]
    assert big.nunique() == 1 and big.iloc[0] >= 0
    assert ev.iloc[12] == -1 and ev.iloc[13] == -1


def test_h3():
    ev = pd.DataFrame({"event": np.repeat(np.arange(8), 5), "resp_sif_apar": 0.0, "resp_ndvi": 12.0})
    h = q1.h3_test(ev, "sif_apar", "ndvi", -5, 500, 0)
    assert h["n_events"] == 8 and h["median_diff"] == -12 and h["met"]
    ev["resp_ndvi"] = 2.0
    assert not q1.h3_test(ev, "sif_apar", "ndvi", -5, 500, 0)["met"]


def test_analysis_end_to_end_small():
    """Full analysis on 6 synthetic cells: SIF/APAR follows SPEI-30 with lag 3; NDVI follows SPEI-180 with lag 20."""
    rng = np.random.default_rng(5)
    scales = [int(s) for s in Q["spei"]["scales_days"]]
    n = 6
    data = {f"spei_{s:03d}": np.empty((DAYS.size, n)) for s in scales}
    sif_apar = np.empty((DAYS.size, n)); ndvi = np.empty((DAYS.size, n))
    for c in range(n):
        sp = _spei_family(rng, scales)
        for s in scales:
            data[f"spei_{s:03d}"][:, c] = sp[s]
        sif_apar[:, c] = np.r_[np.full(3, np.nan), sp[30][:-3]] + rng.normal(0, 0.4, DAYS.size)
        ndvi[:, c] = np.r_[np.full(20, np.nan), sp[180][:-20]] + rng.normal(0, 0.4, DAYS.size)
    doy = pd.DatetimeIndex(DAYS).day_of_year.to_numpy()[:, None]
    seas = np.sin(2 * np.pi * doy / 365)
    ds = xr.Dataset({"sif_apar": (("time", "cell"), sif_apar + seas), "ndvi": (("time", "cell"), ndvi + seas),
                     "evi": (("time", "cell"), ndvi + seas), "aed": (("time", "cell"), rng.normal(size=(DAYS.size, n))),
                     **{k: (("time", "cell"), v) for k, v in data.items()}},
                    coords={"time": DAYS.astype("datetime64[ns]"), "cell": np.arange(n)})
    for k, v in {"iy": np.arange(n), "ix": np.zeros(n, int), "lon": -5.0 + 0.05 * np.arange(n),
                 "lat": np.full(n, 40.0), "fuel_class": ["shrubland"] * n, "stratum": ["shrubland"] * n,
                 "aridity_class": ["semiarid"] * n}.items():
        ds[k] = ("cell", np.asarray(v))
    out = q1.analysis(CFG, ds, n_perm=19)
    r = out["cells"]
    sa = r[(r.variable == "sif_apar") & (r.explanatory == "spei")]
    nd = r[(r.variable == "ndvi") & (r.explanatory == "spei")]
    assert (sa.scale_days == 30).mean() >= 0.8 and (nd.scale_days == 180).mean() >= 0.8
    assert (sa.lag_days.between(0, 8)).mean() >= 0.8
    assert {"spei", "aed"} == set(r.explanatory)
    d = q1.decide(CFG, out)
    assert set(d.hypothesis) == {"H1", "H2", "H3"} and "decision_positive" in d.attrs


def test_parallel_equals_serial():
    """Parallel processes give exactly the serial result (one random stream per cell)."""
    rng = np.random.default_rng(6)
    scales = [int(s) for s in Q["spei"]["scales_days"]]
    n = 3
    ds = xr.Dataset({k: (("time", "cell"), rng.normal(size=(DAYS.size, n))) for k in
                     ["sif_apar", "ndvi", "evi"] + [f"spei_{s:03d}" for s in scales]},
                    coords={"time": DAYS.astype("datetime64[ns]"), "cell": np.arange(n)})
    for k, v in {"iy": np.arange(n), "ix": np.zeros(n, int), "lon": np.full(n, -5.0), "lat": np.full(n, 40.0),
                 "fuel_class": ["shrubland"] * n, "stratum": ["shrubland"] * n,
                 "aridity_class": ["semiarid"] * n}.items():
        ds[k] = ("cell", np.asarray(v))
    a = q1.analysis(CFG, ds, n_perm=9, workers=1)["cells"]
    b = q1.analysis(CFG, ds, n_perm=9, workers=2)["cells"]
    pd.testing.assert_frame_equal(a, b)
