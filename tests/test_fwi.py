import numpy as np
import pandas as pd
import xarray as xr

from physiofire.preprocess.fwi import compute, relative_humidity


def test_relative_humidity():
    t = xr.DataArray([20.0, 30.0, 10.0])
    np.testing.assert_allclose(relative_humidity(t, t), 100.0)
    rh = relative_humidity(xr.DataArray([30.0]), xr.DataArray([10.0]))
    assert 27 < float(rh[0]) < 30  # ~28.5 % with the Magnus formula
    assert float(relative_humidity(xr.DataArray([10.0]), xr.DataArray([10.5]))[0]) == 100.0  # capped


def test_compute_dry_spell_increases_codes():
    n = 40
    time = pd.date_range("2025-07-01", periods=n)
    shape = (n, 1, 2)
    ds = xr.Dataset({"tas_K": (("time", "lat", "lon"), np.full(shape, 303.15)),
                     "tdew_K": (("time", "lat", "lon"), np.full(shape, 283.15)),
                     "u10": (("time", "lat", "lon"), np.full(shape, 3.0)),
                     "v10": (("time", "lat", "lon"), np.zeros(shape)),
                     "pr_m": (("time", "lat", "lon"), np.zeros(shape))},
                    coords={"time": time, "lat": [40.0], "lon": [-5.0, -4.9]})
    ds["pr_m"][20, :, 1] = 0.03  # 30 mm on day 20 in the second cell
    out = compute(ds)
    for v in ["FFMC", "DMC", "DC", "ISI", "BUI", "FWI"]:
        assert np.isfinite(out[v]).all()
    dc = out["DC"].isel(lat=0, lon=0).values
    assert np.all(np.diff(dc) > 0)  # no rain: the drought code rises every day
    # rain lowers the moisture codes on that day
    assert float(out["DMC"].isel(time=20, lat=0, lon=1)) < float(out["DMC"].isel(time=19, lat=0, lon=1))
    assert float(out["FWI"].isel(time=20, lat=0, lon=1)) < float(out["FWI"].isel(time=20, lat=0, lon=0))
