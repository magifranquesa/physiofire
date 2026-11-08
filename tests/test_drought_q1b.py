"""Synthetic tests of Q1b (physiofire.drought_q1b): episode definitions, censoring and paired scores, H3b, backward
mean and signed lags, PAR correction, noise fraction and degradation, decision rules."""
import numpy as np
import pandas as pd

from physiofire import drought_q1 as q1
from physiofire import drought_q1b as qb
from physiofire.config import load_config

CFG = load_config()
E = CFG["drought_q1b"]["episodes"]
A2 = CFG["drought_q1"]["analysis2"]
DAYS = np.arange(np.datetime64("2018-05-01"), np.datetime64("2026-01-01"), dtype="datetime64[D]")
VALID = (DAYS[0], DAYS[-1])


def _day(s):
    return int((np.datetime64(s) - DAYS[0]).astype(int))


def test_run_length_and_separate():
    np.testing.assert_array_equal(qb.run_length(np.array([1, 1, 0, 1, 0, 1, 1, 1], bool)), [2, 1, 0, 1, 0, 3, 2, 1])
    assert qb.separate([5, 6, 200, 250, 400], 90) == [5, 200, 400]


def test_rapid_onset_from_normal_and_within_drought():
    s = np.zeros(DAYS.size)
    i1 = _day("2019-06-10")                      # fast fall from 0 to -2 in 10 days
    s[i1 - 10:i1] = np.linspace(0, -0.95, 10)
    s[i1:i1 + 80] = -2.0
    i2 = _day("2022-04-01")                      # chained: long at -1.2, then fall to -2.4 in 10 days
    s[i2 - 120:i2 - 10] = -1.2
    s[i2 - 10:i2] = np.linspace(-1.2, -2.1, 10)
    s[i2:i2 + 60] = -2.4
    on = qb.onsets_rapid(s, DAYS, E["B"], A2, VALID, 90)
    assert i1 in on                               # first day below -1 with a fall >= 1 in 30 days
    assert any(abs(o - (i2 - 1)) <= 1 for o in on)   # onset where the fall of >= 1.0 completes (already < -1)
    assert not any(i2 - 120 <= o < i2 - 10 for o in on)   # the slow entry at -1.2 is not a rapid onset
    slow = np.zeros(DAYS.size)
    j = _day("2020-07-01")
    slow[j - 90:j] = np.linspace(0, -0.99, 90)    # fall of < 1 in any 30 days
    slow[j:j + 60] = -1.2
    assert qb.onsets_rapid(slow, DAYS, E["B"], A2, VALID, 90) == []


def test_intensification_crossings():
    s = np.full(DAYS.size, -0.2)
    i = _day("2021-05-01")
    s[i:i + 40] = -1.2                            # crossing -1 from normal
    s[i + 40:i + 200] = -1.7                      # crossing -1.5: max of previous 60 days -1.2 < -1.0 -> no
    j = _day("2023-06-01")
    s[j - 30:j] = -0.9                            # crossing -1.5 directly after -0.9 (>= -1.0) -> yes
    s[j:j + 40] = -1.6
    on = qb.onsets_intensification(s, DAYS, E["A"], A2, VALID, 90)
    assert i in on and j in on
    assert i + 40 not in on
    s2 = s.copy()
    s2[i + 50:i + 60] = -0.3                      # brief recovery, new crossing 60 days after the first: < 90
    on2 = qb.onsets_intensification(s2, DAYS, E["A"], A2, VALID, 90)
    assert i in on2 and i + 60 not in on2


def test_short_scale_rule_and_months():
    s = np.zeros(DAYS.size)
    i = _day("2019-07-01")
    s[i:i + 25] = -1.3
    k = _day("2019-11-15")                        # November onset: outside onset months
    s[k:k + 25] = -1.3
    on = qb.onsets_short_scale(s, DAYS, E["C"], A2, VALID)
    assert on == [i]


def _ep(rows):
    ep = pd.DataFrame(rows, columns=["event", "resp_sif_apar", "resp_ndvi"])
    ep["obs_sif_apar"] = True
    ep["obs_ndvi"] = True
    return ep


def test_pair_scores_with_censoring():
    ep = _ep([[0, 10, 20], [0, 5, np.nan], [0, np.nan, 30], [0, np.nan, np.nan], [-1, 1, 50]])
    e = qb.pair_scores(ep, "sif_apar", "ndvi", 90)
    assert len(e) == 4                            # event -1 out
    np.testing.assert_array_equal(e["score"].to_numpy()[:3], [-1, -1, 1])
    np.testing.assert_array_equal(e["d"].to_numpy()[:3], [-10, -85, 60])
    assert e["informative"].tolist() == [True, True, True, False]


def test_h3b_direction_magnitude_and_minimum():
    rows = []
    for ev in range(12):                          # SIF/APAR first in every event by 10 days
        rows += [[ev, 0, 10], [ev, 5, np.nan], [ev, np.nan, np.nan]]
    h = qb.h3b_test(_ep(rows), "sif_apar", "ndvi", 90, -5, 10, 500, 42)
    assert h["evaluable"] and h["met"] and h["mean_score"] == -1 and h["n_pairs_doubly_censored"] == 12
    h = qb.h3b_test(_ep(rows[:27]), "sif_apar", "ndvi", 90, -5, 10, 500, 42)   # 9 events -> not evaluable
    assert not h["evaluable"] and not h["met"]
    rows = [[ev, 20, 10] for ev in range(12)]
    h = qb.h3b_test(_ep(rows), "sif_apar", "ndvi", 90, -5, 10, 500, 42)
    assert h["evaluable"] and not h["met"] and h["mean_score"] == 1
    ep = _ep([[ev, 10, 20] for ev in range(12)])
    ep.loc[0, "obs_ndvi"] = False                 # unobserved reference: pair not used, counted
    h = qb.h3b_test(ep, "sif_apar", "ndvi", 90, -5, 10, 500, 42)
    assert h["n_pairs_unobserved"] == 1 and h["n_events"] == 11


def test_observed_flag():
    z = np.full(400, np.nan)
    z[100:200] = 0.0
    assert qb.observed(z, 130, A2, 0.5)           # onset-30 .. onset+104: 70 of 135 days valid
    assert not qb.observed(z, 170, A2, 0.5)


def test_backward_mean_and_signed_lags():
    x = np.arange(30, dtype=float)[:, None]
    m = qb.backward_mean(x, 5, 0.5)
    assert m[10, 0] == 8.0 and np.isnan(m[1, 0]) and m[2, 0] == 1.0   # window ends at t; 3 of 5 needed
    s = np.arange(DAYS.size, dtype=float)
    lg = qb.lagged_season_signed(s, DAYS, [6], np.array([-3, 0, 4]))
    t0 = q1.season_arrays(s, DAYS, [6])[0]
    np.testing.assert_array_equal(lg[0], t0 + 3)  # L = -3: s(t + 3)
    np.testing.assert_array_equal(lg[2], t0 - 4)
    np.testing.assert_array_equal(qb.lagged_season_signed(s, DAYS, [6], np.arange(0, 3)),
                                  q1.lagged_season(s, DAYS, [6], np.arange(0, 3)))


def test_par_correction_fitted_outside_drought():
    rng = np.random.default_rng(3)
    n, nc = DAYS.size, 4
    par = rng.normal(size=(n, nc))
    spei = rng.normal(size=(n, nc))
    drought = spei < 0
    sif = 0.6 * par + 0.3 * rng.normal(size=(n, nc))
    sif[drought] -= 1.0                           # drought signal
    par[drought] += 0.8                           # dry days are sunny
    season = np.ones(n, bool)
    corr, b, nfit = qb.par_correction(sif, par, spei, season, 0.0, 30)
    zb = 0.6 * np.nanstd(par, axis=0) / np.nanstd(sif, axis=0)   # slope 0.6 on the raw scale, z scale here
    np.testing.assert_allclose(b, zb, rtol=0.1)
    assert (nfit > 1000).all()
    assert np.nanmean(corr[drought]) < np.nanmean(corr[~drought]) - 0.5   # the drought signal survives
    _, b_few, _ = qb.par_correction(sif, par, spei, np.zeros(n, bool), 0.0, 30)
    assert np.isnan(b_few).all()


def test_noise_fraction_and_degradation():
    rng = np.random.default_rng(4)
    n = 3000
    slow = np.convolve(rng.normal(size=n + 60), np.ones(60) / 60, "valid")[:n] * 8
    x = (slow + 0.3 * rng.normal(size=n))[:, None]
    x[rng.random(n) < 0.4] = np.nan             # gaps as in the optical series
    D, V, f = qb.noise_stats(x)
    target = np.array([0.6])
    s2 = qb.noise_variance(D, V, target, 0.99)
    assert s2[0] > 0
    fs = [qb.noise_stats(qb.degrade(x[:, 0], s2[0], np.random.default_rng(k))[:, None])[2][0] for k in range(20)]
    assert abs(np.mean(fs) - 0.6) < 0.03
    assert qb.noise_variance(D, V, np.array([f[0] / 2]), 0.99)[0] == 0      # already noisier: no noise added
    assert np.isnan(qb.degrade(x[:, 0], s2[0], rng)).sum() == np.isnan(x).sum()


def test_definition_choice_and_decision():
    c = {"B": {"n_events_with_shrubland": 7}, "A": {"n_events_with_shrubland": 12},
         "C": {"n_events_with_shrubland": 30}}
    assert qb.choose_definition(c, ["B", "A", "C"], 10) == "A"
    c["A"]["n_events_with_shrubland"] = 3
    assert qb.choose_definition(c, ["B", "A", "C"], 10) == "C"
    c["C"]["n_events_with_shrubland"] = 0
    assert qb.choose_definition(c, ["B", "A", "C"], 10) is None
    assert qb.outcome(False, False, True, True, True) == "not_conclusive"
    assert qb.outcome(True, False, True, True, True) == "contrary"
    assert qb.outcome(True, True, True, False, True) == "support"
    assert qb.outcome(True, True, True, False, False) == "not_conclusive"
    assert qb.overall(["support", "support"]) == "support"
    assert qb.overall(["support", "contrary"]) == "contrary"
    assert qb.overall(["support", "not_conclusive"]) == "not_conclusive"
    r = pd.DataFrame({"fraction": [0.7, 0.5, 0.65, 0.4, 0.62], "ci_lo": [0.6, 0.4, 0.55, 0.3, 0.52],
                      "ci_hi": 0.8, "met": [True, False, True, False, True], "replicate_seed": [42, 43, 44, 45, 46]})
    h = qb.robust_h1(r)
    assert h["fraction"] == 0.62 and h["met"] and h["n_replicates_met"] == 3


def _rolling(x, n):
    c = np.cumsum(np.concatenate([[0.0], x]))
    out = np.full(x.size, np.nan)
    out[n - 1:] = (c[n:] - c[:-n]) / np.sqrt(n)
    return out


def test_end_to_end_small():
    """Analysis 1b on synthetic cells: SIF/APAR follows SPEI-30 with lag 3 plus a PAR term; NDVI leads SPEI-90 by 10
    days (negative lag allowed); then the full decision on these cells with synthetic episodes."""
    import xarray as xr
    rng = np.random.default_rng(7)
    q = CFG["drought_q1"]
    scales = [int(s) for s in q["spei"]["scales_days"]]
    n = 4
    data = {f"spei_{s:03d}": np.empty((DAYS.size, n)) for s in scales}
    sif_apar, ndvi, par = (np.empty((DAYS.size, n)) for _ in range(3))
    for c in range(n):
        d = rng.normal(size=DAYS.size + 400)
        for s in scales:
            r = _rolling(d, s)[400:]
            data[f"spei_{s:03d}"][:, c] = (r - np.nanmean(r)) / np.nanstd(r)
        par[:, c] = 300 + 30 * rng.normal(size=DAYS.size)
        sp30, sp90 = data["spei_030"][:, c], data["spei_090"][:, c]
        sif_apar[:, c] = np.r_[np.full(3, np.nan), sp30[:-3]] + 0.02 * (par[:, c] - 300) + rng.normal(0, .4, DAYS.size)
        ndvi[:, c] = np.r_[sp90[10:], np.full(10, np.nan)] + rng.normal(0, 0.4, DAYS.size)
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
    res, fit = qb.run_analysis1(CFG, ds, par, "backward", workers=1, n_perm=9)
    assert (fit["b_par"] > 0.2).all()            # PAR slope found outside drought
    sa = res[(res.variable == "sif_apar") & (res.explanatory == "spei")]
    nd = res[(res.variable == "ndvi") & (res.explanatory == "spei")]
    assert (sa.scale_days == 30).mean() >= 0.75 and sa.lag_days.between(5, 15).all()   # 3 + ~7 (backward mean)
    assert nd.lag_h2.between(-8, 2).all()         # -10 + ~7: a negative true lag is not censored at 0
    assert {"spei", "aed", "spei_given_par"} == set(res.explanatory)
    ep = pd.DataFrame({"cell": np.tile(np.arange(n), 12), "event": np.repeat(np.arange(12), n),
                       "onset": "2020-06-01", "resp_sif_apar": 5.0, "resp_ndvi": 20.0, "resp_evi": np.nan,
                       "obs_sif_apar": True, "obs_ndvi": True, "obs_evi": True, "fuel_class": "shrubland",
                       "stratum": "shrubland", "event_season": "summer"})
    d, dec, _ = qb.decide(CFG, res, None, None, ep)
    h3 = d[(d.stratum == "shrubland") & (d.test == "H3b")].set_index("against")
    assert h3.loc["ndvi", "met"] and h3.loc["evi", "met"] and h3.loc["evi", "median_d"] == -85
    assert set(dec.outcome) <= {"support", "contrary", "not_conclusive"}
