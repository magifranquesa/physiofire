import numpy as np

from physiofire.preprocess.aed import et0_fao56, extraterrestrial_radiation


def test_extraterrestrial_radiation_fao56_example8():
    # FAO-56 Example 8: 20 S, 3 September (doy 246) -> Ra = 32.2 MJ m-2 day-1
    np.testing.assert_allclose(extraterrestrial_radiation(-20.0, 246), 32.2, atol=0.1)


def test_et0_fao56_example18():
    # FAO-56 Example 18 (Brussels, 50 deg 48' N, 100 m, 6 July): Tmax 21.5, Tmin 12.3 degC, ea 1.409 kPa,
    # wind 10 km/h at 10 m (2.78 m/s; u2 = 2.078 m/s), Rs 22.07 MJ m-2 day-1 -> ET0 = 3.9 mm/day
    ea = 1.409
    tdew = 237.3 * np.log(ea / 0.6108) / (17.27 - np.log(ea / 0.6108))
    ps = 101.3 * ((293 - 0.0065 * 100) / 293) ** 5.26
    et0 = et0_fao56(21.5, 12.3, tdew, 22.07, ps, 2.78, 50.8, 187)
    np.testing.assert_allclose(et0, 3.9, atol=0.1)
