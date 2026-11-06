import numpy as np
import xarray as xr

from physiofire.indices import (clip_percentiles, composites_to_daily, composites_to_daily_cut, evi, ndvi, nirv,
                                sif_apar, sif_par)


def _composites(values):
    starts = np.array([np.datetime64("2025-06-01") + np.timedelta64(4 * i, "D") for i in range(len(values))],
                      dtype="datetime64[ns]")
    centers = starts + np.timedelta64(36, "h")
    da = xr.DataArray(np.array(values, dtype=float)[:, None, None], dims=("time", "lat", "lon"),
                      coords={"time": starts})
    days = np.array([np.datetime64("2025-06-01") + np.timedelta64(i, "D") for i in range(20)], dtype="datetime64[ns]")
    return da, starts, centers, days


def _day(out, d):
    return float(out.sel(time=np.datetime64(d)).values.squeeze())


def test_cut_removes_post_cutoff_composites_and_persists():
    da, starts, centers, days = _composites([0.1, 0.2, 0.3, 0.4, 0.5])
    cut = np.array([[np.datetime64("2025-06-14")]])
    out = composites_to_daily_cut(da, starts, centers, days, cut, 4, 12, 5)
    assert np.isclose(_day(out, "2025-06-04"), 0.15)          # normal interpolation before the cut-off
    assert np.isclose(_day(out, "2025-06-11"), 0.3)           # composite of 06-13 (ends 06-16) removed -> persistence
    assert np.isclose(_day(out, "2025-06-13"), 0.3)
    assert np.isnan(_day(out, "2025-06-14"))                  # cut-off day itself masked
    assert np.isnan(_day(out, "2025-06-18"))


def test_cut_without_persistence_and_without_cutoff():
    da, starts, centers, days = _composites([0.1, 0.2, 0.3, 0.4, 0.5])
    cut = np.array([[np.datetime64("2025-06-14")]])
    assert np.isnan(_day(composites_to_daily_cut(da, starts, centers, days, cut, 4, 12, None), "2025-06-11"))
    nat = np.array([[np.datetime64("NaT")]], dtype="datetime64[D]")
    out = composites_to_daily_cut(da, starts, centers, days, nat, 4, 12, 5)
    assert np.isclose(_day(out, "2025-06-11"), 0.325)         # no cut-off: plain interpolation


def test_persistence_limited_in_days():
    da, starts, centers, days = _composites([0.1, 0.2, 0.3, np.nan, np.nan])
    nat = np.array([[np.datetime64("NaT")]], dtype="datetime64[D]")
    out = composites_to_daily_cut(da, starts, centers, days, nat, 4, 12, 5)
    assert np.isclose(_day(out, "2025-06-15"), 0.3)           # 5 days after the last centre (06-10 12:00)
    assert np.isnan(_day(out, "2025-06-16"))                  # 6 days: beyond persistence


def test_nirv():
    assert np.isclose(nirv(0.1, 0.3), (0.5 - 0.08) * 0.3)


def test_formulas():
    assert np.isclose(ndvi(0.1, 0.3), 0.5)
    assert np.isclose(evi(0.1, 0.3, 0.05), 2.5 * 0.2 / (0.3 + 0.6 - 0.375 + 1))
    assert np.isclose(sif_apar(0.4, 200.0, 0.5), 0.004)
    assert np.isclose(sif_par(0.4, 200.0), 0.002)


def test_clip_percentiles():
    da = xr.DataArray(np.arange(101, dtype=float))
    out, lo, hi = clip_percentiles(da, 1, 99)
    assert lo == 1 and hi == 99
    assert int(out.notnull().sum()) == 99


def test_composites_to_daily_linear():
    t0 = np.datetime64("2025-06-01T12:00")
    centers = np.array([t0, t0 + np.timedelta64(4, "D")], dtype="datetime64[ns]")
    da = xr.DataArray([[0.2], [0.6]], dims=("time", "x"), coords={"time": centers})
    days = np.array([np.datetime64("2025-06-01") + np.timedelta64(i, "D") for i in range(5)], dtype="datetime64[ns]")
    out = composites_to_daily(da, centers, days, 12)
    assert np.allclose(out.values[:, 0], [0.2, 0.3, 0.4, 0.5, 0.6])


def test_composites_gap_bridged_only_if_short():
    t0 = np.datetime64("2025-06-01T12:00")
    centers = np.array([t0 + np.timedelta64(4 * i, "D") for i in range(6)], dtype="datetime64[ns]")
    vals = np.array([0.2, np.nan, 0.4, np.nan, np.nan, np.nan])[:, None]
    da = xr.DataArray(vals, dims=("time", "x"), coords={"time": centers})
    days = np.array([np.datetime64("2025-06-03"), np.datetime64("2025-06-14")], dtype="datetime64[ns]")
    out = composites_to_daily(da, centers, days, 12)
    assert np.isclose(out.values[0, 0], 0.25)       # inside the bridged 8-day gap
    assert np.isnan(out.values[1, 0])               # after the last valid composite
