"""Synthetic tests of the epoch series: post-ignition leakage (daily series and fPAR composites) and recovery of
an injected pre-fire signal in burned cells against controls."""
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from physiofire import epoch
from physiofire.config import load_config

CFG = load_config()
ACFG, ECFG, SCFG = CFG["anomalies"], dict(CFG["epoch"]), CFG["sif_apar"]
DAYS = np.arange(np.datetime64("2019-01-01"), np.datetime64("2025-10-01"), dtype="datetime64[D]")
IGN = np.datetime64("2025-08-10")
NB, NC = 20, 20   # burned, control cells (enough to average out noise in the trailing means)


def _synthetic(seed=0, post=None, signal=3.0, onset=20):
    """Daily series (time, cell): seasonal cycle + noise (SD 1); burned cells drop linearly by `signal` SD over the
    `onset` days before ignition. `post` replaces all values from ignition on (leakage probe)."""
    rng = np.random.default_rng(seed)
    t = (DAYS - DAYS[0]).astype(int)
    x = 5 + 2 * np.sin(2 * np.pi * t / 365.25)[:, None] + rng.normal(0, 1, (len(DAYS), NB + NC))
    rel = (DAYS - IGN).astype(int)
    ramp = np.clip((rel + onset) / onset, 0, 1)
    x[:, :NB] -= signal * np.where(rel < 0, ramp, 1)[:, None]
    if post is not None:
        x[DAYS >= IGN] = post(rng, (int((DAYS >= IGN).sum()), NB + NC))
    return x


def _run(x):
    return epoch.fire_series({"v": x}, DAYS, IGN, ACFG, ECFG)["v"]


def test_no_leakage_from_post_ignition_values():
    a = _run(_synthetic(post=lambda r, s: np.full(s, 1e6)))
    b = _run(_synthetic(post=lambda r, s: r.normal(-50, 30, s)))
    for k in ECFG["series"]:
        assert np.allclose(a[k], b[k], equal_nan=True)


def test_injected_signal_recovered_and_controls_flat():
    s = _run(_synthetic())
    for k in ECFG["series"]:
        z = s[k]                                     # (60, ncell), day -60 .. -1
        burned_late = np.nanmean(z[-7:, :NB])
        control_late = np.nanmean(z[-7:, NB:])
        burned_early = np.nanmean(z[:20, :NB])       # days -60 .. -41: before the onset (-20)
        assert burned_late < -1.0, (k, burned_late)
        assert abs(control_late) < 0.8, (k, control_late)
        assert abs(burned_early) < 0.8, (k, burned_early)
        assert burned_late - control_late < -1.0


def test_fpar_composites_after_ignition_do_not_leak():
    starts = np.arange(DAYS[0], DAYS[-1], np.timedelta64(4, "D")).astype("datetime64[ns]")
    centers = starts + np.timedelta64(36, "h")
    rng = np.random.default_rng(1)
    ncell = NB + NC
    comp = 0.4 + 0.05 * rng.normal(size=(len(starts), ncell))
    comp2 = comp.copy()
    ends = starts.astype("datetime64[D]") + np.timedelta64(3, "D")
    comp2[ends >= IGN] = 0.01                         # post-ignition (and straddling) composites: absurd fPAR
    sif = 1 + 0.1 * rng.normal(size=(len(DAYS), ncell))
    par = np.full((len(DAYS), ncell), 300.0)
    for persist in (SCFG["fpar_persist_days"], None):
        r1, f1 = epoch.sif_apar_causal(sif, par, comp, starts, centers, DAYS, IGN, 4, 12, persist)
        r2, f2 = epoch.sif_apar_causal(sif, par, comp2, starts, centers, DAYS, IGN, 4, 12, persist)
        pre = DAYS < IGN
        assert np.allclose(f1[pre], f2[pre], equal_nan=True)
        assert np.all(np.isnan(f1[~pre]))
        if persist is None:   # no persistence: days after the last composite fully before ignition are missing
            assert np.isnan(f1[DAYS == IGN - np.timedelta64(1, "D")]).all()


def test_to_long_shape():
    s = _run(_synthetic())
    cells = pd.DataFrame({"cell_id": range(NB + NC), "group": ["burned"] * NB + ["control"] * NC,
                          "weight": [0.7] * NB + [1.0] * NC})
    df = epoch.to_long("f1", cells, {"v": s}, int(ECFG["window_days"]))
    assert len(df) == len(ECFG["series"]) * 60 * (NB + NC)
    assert df.day_rel.min() == -60 and df.day_rel.max() == -1
    assert set(df.group) == {"burned", "control"}


def test_window_must_be_covered():
    with pytest.raises(ValueError):
        epoch.fire_series({"v": _synthetic()[:100]}, DAYS[:100], IGN, ACFG, ECFG)


def synthetic_inputs(n_fires=8, seed=3):
    """Gridded synthetic inputs (lat 2 x lon 2*n_fires cells; per fire one burned and one control cell) whose
    burned-cell SIF drops by 3 SD over the 20 days before ignition; NDVI/EVI without signal."""
    rng = np.random.default_rng(seed)
    days = DAYS.astype("datetime64[ns]")
    nlat, nlon = 2, 2 * n_fires
    t = (DAYS - DAYS[0]).astype(int)
    seas = np.sin(2 * np.pi * t / 365.25)[:, None, None]
    sif = 1.0 + 0.3 * seas + 0.1 * rng.normal(size=(len(DAYS), nlat, nlon))
    rel = (DAYS - IGN).astype(int)
    ramp = np.where(rel < 0, np.clip((rel + 20) / 20, 0, 1), 1)[:, None]
    sif[:, 0, 0::2] -= 0.3 * ramp                    # burned cells: row 0, even columns
    coords = {"time": days, "lat": [40.0, 40.25], "lon": 0.25 * np.arange(nlon)}
    starts = np.arange(DAYS[0], DAYS[-1], np.timedelta64(4, "D")).astype("datetime64[ns]")
    fpar = 0.4 + 0.02 * rng.normal(size=(len(starts), nlat, nlon))
    red = 0.08 + 0.01 * rng.normal(size=sif.shape)
    nir = 0.30 + 0.02 * rng.normal(size=sif.shape) + 0.03 * seas
    inputs = {
        "sif": xr.Dataset({"sif": (("time", "lat", "lon"), sif)}, coords=coords),
        "par": xr.Dataset({"par": (("time", "lat", "lon"), np.full(sif.shape, 300.0))}, coords=coords),
        "fpar": xr.Dataset({"fpar": (("time", "lat", "lon"), fpar)},
                           coords={"time": starts, "lat": coords["lat"], "lon": coords["lon"],
                                   "time_center": ("time", starts + np.timedelta64(36, "h"))}),
        "sr": xr.Dataset({"red": (("time", "lat", "lon"), red), "nir": (("time", "lat", "lon"), nir),
                          "blue": (("time", "lat", "lon"), np.full(sif.shape, 0.04))}, coords=coords),
    }
    fires = pd.DataFrame({"fire_id": [f"f{i}" for i in range(n_fires)], "country": ["ES", "PT"] * (n_fires // 2),
                          "ignition_date": str(IGN)})
    cells = pd.concat([pd.DataFrame({"fire_id": f"f{i}", "grid": "base", "fire_veg": "shrubland",
                                     "group": ["burned", "control"], "iy": [0, 1], "ix": [2 * i, 2 * i + 1],
                                     "burned_fraction": [0.8, 0.0]}) for i in range(n_fires)], ignore_index=True)
    cells["cell_id"] = cells.fire_id + "_" + cells.group
    return inputs, fires, cells


def test_run_end_to_end(tmp_path):
    inputs, fires, cells = synthetic_inputs()
    fires.to_csv(tmp_path / "fires.csv", index=False)
    cells.to_csv(tmp_path / "cells.csv", index=False)
    df = epoch.run(CFG, "base", str(tmp_path / "fires.csv"), str(tmp_path / "cells.csv"), inputs,
                   str(tmp_path / "anom.csv"))
    assert set(df.variable) == {"sif_apar", "ndvi", "evi"}
    late = df[(df.day_rel >= -5) & (df.series == ECFG["series"][0]) & (df.variable == "sif_apar")]
    b = late[late.group == "burned"].z.mean()
    c = late[late.group == "control"].z.mean()
    assert b - c < -1.0, (b, c)
    nd = df[(df.day_rel >= -5) & (df.variable == "ndvi")]
    assert abs(nd[nd.group == "burned"].z.mean() - nd[nd.group == "control"].z.mean()) < 1.0


def test_loess_trend_end_limits_signal_absorption():
    """With the trend fitted only before day -60, the LOESS anomaly of burned cells early in the window stays near
    0 and the late signal is not damped compared with the trend fitted on all pre-ignition data."""
    x = _synthetic(signal=3.0, onset=20)
    e_cut = dict(ECFG, series=["loess_trail15"])
    e_all = dict(e_cut, loess_trend_end_day=None)
    cut = epoch.fire_series({"v": x}, DAYS, IGN, ACFG, e_cut)["v"]["loess_trail15"]
    full = epoch.fire_series({"v": x}, DAYS, IGN, ACFG, e_all)["v"]["loess_trail15"]
    early_cut, early_full = np.nanmean(cut[:20, :NB]), np.nanmean(full[:20, :NB])
    assert abs(early_cut) < 0.3, early_cut
    assert abs(early_cut) <= abs(early_full) + 0.05, (early_cut, early_full)
    assert np.nanmean(cut[-7:, :NB]) <= np.nanmean(full[-7:, :NB]) + 0.05
