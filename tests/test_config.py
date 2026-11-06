from physiofire.config import load_config


def test_config_loads():
    cfg = load_config()
    r = cfg["region"]
    assert r["lon_min"] < r["lon_max"] and r["lat_min"] < r["lat_max"]
    assert cfg["epoch"]["window_days"] == 60
    assert cfg["paths"]["raw"].is_absolute()


def test_grids_aligned_with_region():
    cfg = load_config()
    r = cfg["region"]
    for grid in cfg["grids"].values():
        res = grid["resolution_deg"]
        for edge in (r["lon_min"], r["lon_max"], r["lat_min"], r["lat_max"]):
            assert abs(round(edge / res) * res - edge) < 1e-9
