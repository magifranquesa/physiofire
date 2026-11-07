import numpy as np

from physiofire.preprocess.fuel import type_fractions
from physiofire.preprocess.grid import Grid


def test_type_fractions_lonlat_identity():
    # categorical raster already in lon/lat: 0.01 deg pixels, two types split at lon 0.02
    res = 0.01
    x = np.arange(0.005, 0.1, res)
    y = np.arange(0.095, 0.0, -res)  # north to south, as in a GeoTIFF
    codes = np.where(x[None, :] < 0.02, 21.0, 41.0) * np.ones((y.size, 1))
    codes[0, 0] = np.nan  # no data pixel
    grid = Grid(0.0, 0.0, 0.1, 0.1, 0.05)
    frac, n = type_fractions(codes, x, y, res, "EPSG:4326", grid, [21, 41, 7], k=2)
    assert frac.shape == (3, 2, 2)
    np.testing.assert_allclose(np.nansum(frac, axis=0), 1.0)
    # western cells: lon 0-0.05 -> pixels at 0.005, 0.015 type 21 (2 of 5 columns)
    np.testing.assert_allclose(frac[0, 0, 0], 0.4)
    np.testing.assert_allclose(frac[1, 0, 0], 0.6)
    assert np.all(frac[2] == 0)
    # eastern cells: all type 41
    np.testing.assert_allclose(frac[1, :, 1], 1.0)
    # the no-data pixel (north-west corner) is excluded from the count of the north-west cell
    assert n[1, 0] == 25 * 4 - 4 and n[0, 0] == 25 * 4
    np.testing.assert_allclose(frac[0, 1, 0], 9 / 24)  # 10 type-21 pixels minus the no-data one, of 24
