import numpy as np
import pandas as pd
import pytest
import xarray as xr

from physiofire.preprocess.aed import compute
from physiofire.preprocess.water_balance import year_balance


def _inputs(days, lat=(40.0, 40.1), lon=(-5.0, -4.9)):
    shape = (len(days), len(lat), len(lon))
    c = {"time": days, "lat": list(lat), "lon": list(lon)}
    ai = xr.Dataset({"tmax_K": (("time", "lat", "lon"), np.full(shape, 303.15)),
                     "tmin_K": (("time", "lat", "lon"), np.full(shape, 288.15)),
                     "tdew_K": (("time", "lat", "lon"), np.full(shape, 283.15)),
                     "rs_J": (("time", "lat", "lon"), np.full(shape, 25e6)),
                     "ps_Pa": (("time", "lat", "lon"), np.full(shape, 95000.0)),
                     "ws10": (("time", "lat", "lon"), np.full(shape, 3.0))}, coords=c)
    pr = xr.Dataset({"pr_mm": (("time", "lat", "lon"), np.zeros(shape))}, coords=c)
    return pr, ai


def test_balance_is_p_minus_et0():
    days = pd.date_range("2020-07-01", periods=5)
    pr, ai = _inputs(days)
    pr["pr_mm"][2] = 10.0
    ds = year_balance(pr, ai, 0.23)
    et0 = compute(ai, 0.23)
    np.testing.assert_allclose(ds["d"].values, (pr["pr_mm"] - et0).values, rtol=1e-6)
    assert float(ds["et0"].min()) > 3        # summer ET0 of several mm/day
    assert float(ds["d"][2].min()) > 0       # rainy day: positive balance


def test_misaligned_inputs_rejected():
    pr, ai = _inputs(pd.date_range("2020-07-01", periods=5))
    with pytest.raises(ValueError):
        year_balance(pr.isel(time=slice(1, None)), ai.isel(time=slice(0, 4)), 0.23)
