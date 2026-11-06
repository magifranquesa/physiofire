import numpy as np
import xarray as xr

from physiofire.indices import clip_percentiles, composites_to_daily, evi, ndvi, sif_apar, sif_par


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
