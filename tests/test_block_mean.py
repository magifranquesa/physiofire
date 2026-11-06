import numpy as np

from physiofire.download.gee import block_mean


def test_block_mean_count_weighted():
    mean = np.array([[1.0, 3.0], [np.nan, 5.0]])
    count = np.array([[1.0, 3.0], [0.0, 0.0]])
    m, c = block_mean(mean, count, 2)
    assert c.shape == (1, 1) and c[0, 0] == 4.0
    assert np.isclose(m[0, 0], (1 * 1 + 3 * 3) / 4)


def test_block_mean_empty_block_is_nan():
    m, c = block_mean(np.full((2, 4), np.nan), np.zeros((2, 4)), 2)
    assert np.all(np.isnan(m)) and np.all(c == 0)


def test_block_mean_keeps_leading_dims():
    mean = np.ones((3, 10, 10))
    count = np.ones((3, 10, 10))
    m, c = block_mean(mean, count, 5)
    assert m.shape == (3, 2, 2) and np.all(c == 25) and np.allclose(m, 1)
