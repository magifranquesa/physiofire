import numpy as np

from physiofire.preprocess.grid import Grid
from physiofire.preprocess.troposif_grid import corner_order_is_cyclic, grid_day

G = Grid(0.0, 0.0, 1.0, 1.0, 0.25)  # 4 x 4 cells


def square(lon0, lat0, size):
    """Corners in cyclic (counter-clockwise) order."""
    lon_b = np.array([[lon0, lon0 + size, lon0 + size, lon0]])
    lat_b = np.array([[lat0, lat0, lat0 + size, lat0 + size]])
    return lon_b, lat_b


def test_pixel_inside_one_cell():
    lon_b, lat_b = square(0.05, 0.05, 0.1)
    r = grid_day(np.array([2.0]), np.array([0.4]), lon_b, lat_b, G, 4)
    assert r["weight_sum"][0, 0] == 1.0 and r["sif"][0, 0] == 2.0
    assert np.isclose(r["sif_sem"][0, 0], 0.4)
    assert r["weight_sum"].sum() == 1.0 and r["n_pixels"].sum() == 1


def test_pixel_split_across_four_cells():
    # Pixel centred on the corner shared by cells (0,0), (0,1), (1,0), (1,1)
    lon_b, lat_b = square(0.125, 0.125, 0.25)
    r = grid_day(np.array([1.0]), np.array([0.2]), lon_b, lat_b, G, 4)
    assert np.allclose(r["weight_sum"][:2, :2], 0.25)
    assert np.isclose(r["weight_sum"].sum(), 1.0)
    assert np.allclose(r["sif"][:2, :2], 1.0)


def test_weighted_mean_of_two_pixels():
    a = square(0.0, 0.0, 0.25)           # fully in cell (0,0)
    b = square(0.125, 0.0, 0.25)          # half in cell (0,0), half in (0,1)
    lon_b = np.vstack([a[0], b[0]])
    lat_b = np.vstack([a[1], b[1]])
    r = grid_day(np.array([1.0, 3.0]), np.array([0.1, 0.1]), lon_b, lat_b, G, 4)
    assert np.isclose(r["weight_sum"][0, 0], 1.5)
    assert np.isclose(r["sif"][0, 0], (1.0 * 1 + 3.0 * 0.5) / 1.5)
    assert np.isclose(r["sif"][0, 1], 3.0)


def test_empty_day():
    r = grid_day(np.empty(0), np.empty(0), np.empty((0, 4)), np.empty((0, 4)), G, 4)
    assert np.all(np.isnan(r["sif"])) and r["weight_sum"].sum() == 0


def test_corner_order_check():
    lon_b, lat_b = square(0.0, 0.0, 1.0)
    assert corner_order_is_cyclic(lon_b, lat_b).all()
    bowtie = lon_b[:, [0, 1, 3, 2]], lat_b[:, [0, 1, 3, 2]]
    assert not corner_order_is_cyclic(*bowtie).any()
