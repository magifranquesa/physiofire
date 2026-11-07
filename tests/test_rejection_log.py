import datetime as dt

import pandas as pd
import pytest

from physiofire.download.gee import ImplausibleValues, RejectionLog


def _err(day):
    return ImplausibleValues(f"mod09ga {day}: median blue = 0.004 outside plausible range", "blue", 0.004, 1000)


def _day(i):
    return dt.date(2025, 3, 1) + dt.timedelta(days=i)


def test_isolated_rejections_continue_and_are_logged(tmp_path):
    path = tmp_path / "rejected_images.csv"
    r = RejectionLog(path, max_consecutive=3, max_per_year=5)
    for i in range(5):   # 5 isolated rejections in one year: allowed
        r.reject("mod09ga", _day(2 * i), _err(_day(2 * i)))
        r.accept()
    df = pd.read_csv(path)
    assert len(df) == 5 and set(df.variable) == {"blue"}


def test_stop_on_consecutive(tmp_path):
    r = RejectionLog(tmp_path / "r.csv", max_consecutive=3, max_per_year=5)
    r.reject("mod09ga", _day(0), _err(_day(0)))
    r.reject("mod09ga", _day(1), _err(_day(1)))
    with pytest.raises(ImplausibleValues):
        r.reject("mod09ga", _day(2), _err(_day(2)))


def test_stop_on_more_than_per_year_and_reset(tmp_path):
    r = RejectionLog(tmp_path / "r.csv", max_consecutive=3, max_per_year=5)
    for i in range(5):
        r.reject("mod09ga", _day(2 * i), _err(_day(2 * i)))
        r.accept()
    r.start_year()   # new product-year: counters reset
    r.reject("mod09ga", _day(20), _err(_day(20)))
    r.accept()
    r2 = RejectionLog(None, max_consecutive=3, max_per_year=5)
    for i in range(5):
        r2.reject("mod09ga", _day(2 * i), _err(_day(2 * i)))
        r2.accept()
    with pytest.raises(ImplausibleValues):
        r2.reject("mod09ga", _day(30), _err(_day(30)))


def test_rerun_replaces_same_product_date(tmp_path):
    path = tmp_path / "r.csv"
    RejectionLog(path).reject("mod09ga", _day(0), _err(_day(0)))
    RejectionLog(path).reject("mod09ga", _day(0), _err(_day(0)))
    RejectionLog(path).reject("myd09ga", _day(0), _err(_day(0)))
    assert len(pd.read_csv(path)) == 2


def test_negative_fraction_check():
    import numpy as np

    from physiofire.download.gee import check_negative_fraction
    means = {"neg": np.array([0.3, 0.2, np.nan])}
    counts = {"neg": np.array([10000.0, 10000.0, 0.0])}
    with pytest.raises(ImplausibleValues):
        check_negative_fraction("mod09ga", "2025-03-29", means, counts, 0.10, 10000)
    assert check_negative_fraction("mod09ga", "d", means, counts, 0.10, 50000) is None   # too few pixels
    ok = check_negative_fraction("mod09ga", "d", {"neg": np.array([0.01, 0.0])}, {"neg": np.array([5e3, 5e3])},
                                 0.10, 10000)
    assert ok == pytest.approx(0.005)
