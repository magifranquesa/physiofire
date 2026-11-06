import numpy as np
import pytest

from physiofire.download.gee import ImplausibleValues, check_plausible

RANGES = {"fpar": [0.05, 0.95], "red": [0.01, 0.40]}


def test_plausible_passes_and_returns_medians():
    m = {"fpar": np.array([[0.3, 0.5], [np.nan, 0.0]])}
    c = {"fpar": np.array([[10, 10], [0, 0]])}          # only counted cells enter the median
    med = check_plausible("fpar", "2025-07-01", m, c, RANGES)
    assert np.isclose(med["fpar"], 0.4)


def test_plausible_catches_scaling_error():
    m = {"fpar": np.full((2, 2), 0.004)}                  # VIIRS asset scaled twice
    c = {"fpar": np.ones((2, 2))}
    with pytest.raises(ImplausibleValues, match="fpar 2025-07-04: median fpar"):
        check_plausible("fpar", "2025-07-04", m, c, RANGES)


def test_plausible_skips_variables_without_range_or_data():
    m = {"sw": np.full((2, 2), 999.0), "red": np.full((2, 2), np.nan)}
    c = {"sw": np.ones((2, 2)), "red": np.zeros((2, 2))}
    assert check_plausible("x", "d", m, c, RANGES) == {}
