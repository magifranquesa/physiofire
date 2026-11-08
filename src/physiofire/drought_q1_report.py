"""Question 1: summary tables of the pre-registered result and the post hoc diagnostics.

Reads the outputs of `python -m physiofire.drought_q1 analysis` (data/processed/drought_q1) and writes small CSV
tables next to them (versioned in git). It changes nothing in the analysis.

Pre-registered result (summaries of analysis1_cells.csv, analysis2_episodes.csv and hypotheses.csv):
  summary_significant.csv, summary_scale_lag.csv, summary_scale_share.csv, summary_aed.csv, summary_h2_lag_diff.csv,
  summary_spei_clip.csv
Post hoc (declared after seeing the result, 2026-11-08):
  posthoc_events.csv          responses per drought event and stratum (August events: SIF/APAR responds, NDVI/EVI not)
  posthoc_par_diagnostic.csv  lag-0 correlations of SIF/APAR with PAR, AED and SPEI-30 and partial correlations
                              given PAR, April-October, by stratum (per-cell values: posthoc_par_cells.csv, not in git)

Usage: python -m physiofire.drought_q1_report
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import xarray as xr

from . import drought_q1 as q1
from . import epoch
from .config import REPO_ROOT, load_config

log = logging.getLogger(__name__)
MAIN = ["sif_apar", "ndvi", "evi"]
SECONDARY = ["sif", "sif_par", "fpar"]


def _mode(x: pd.Series) -> float:
    x = x.dropna()
    return float(x.mode().iloc[0]) if len(x) else np.nan


def _strata(df: pd.DataFrame) -> pd.DataFrame:
    """Rows of df repeated for the strata plus wet heath alone (descriptive)."""
    wh = df[df["fuel_class"] == "wet_heath"].assign(stratum="wet_heath_only")
    return pd.concat([df, wh], ignore_index=True)


def scale_lag_tables(cells: pd.DataFrame, alpha: float) -> dict[str, pd.DataFrame]:
    s = _strata(cells[cells["explanatory"] == "spei"].copy())
    # main variables: cells with significant r* (permutation); secondary: all cells (no permutation, descriptive)
    s["used"] = np.where(s["variable"].isin(MAIN), s["p"] < alpha, s["r"].notna())
    sig = (s.groupby(["stratum", "variable"])
           .agg(n_cells=("cell", "size"), n_with_r=("r", lambda x: int(x.notna().sum())),
                n_significant=("p", lambda x: int((x < alpha).sum())),
                n_significant_h2=("p_h2", lambda x: int((x < alpha).sum())))
           .reset_index())
    sig.loc[~sig["variable"].isin(MAIN), ["n_significant", "n_significant_h2"]] = np.nan
    u = s[s["used"]]
    both = pd.concat([u, u.assign(aridity_class="all")], ignore_index=True)
    sl = (both.groupby(["stratum", "aridity_class", "variable"])
          .agg(n=("cell", "size"), r_median=("r", "median"), scale_median=("scale_days", "median"),
               scale_mode=("scale_days", _mode), lag_median=("lag_days", "median"), lag_mode=("lag_days", _mode),
               lag_spei090_median=("lag_h2", "median"), lag_spei090_mode=("lag_h2", _mode))
          .reset_index())
    sl["cells_used"] = np.where(sl["variable"].isin(MAIN), "significant", "all (descriptive)")
    share = (u.groupby(["stratum", "variable"])["scale_days"].value_counts(normalize=True)
             .rename("share").reset_index())
    a = _strata(cells[cells["explanatory"] == "aed"].copy())
    sp = s[["cell", "stratum", "variable", "r"]]
    a = a.merge(sp, on=["cell", "stratum", "variable"], suffixes=("", "_spei"))
    aed = (a.groupby(["stratum", "variable"])
           .agg(n_with_r=("r", lambda x: int(x.notna().sum())),
                n_significant=("p", lambda x: int((x < alpha).sum())), r_median=("r", "median"),
                lag_median=("lag_days", "median"), lag_mode=("lag_days", _mode),
                share_aed_stronger_than_spei=("r", lambda x: np.nan))
           .reset_index())
    stronger = (a.assign(st=a["r"].abs() > a["r_spei"]).groupby(["stratum", "variable"])["st"].mean())
    aed["share_aed_stronger_than_spei"] = aed.set_index(["stratum", "variable"]).index.map(stronger)
    aed.loc[~aed["variable"].isin(MAIN), "n_significant"] = np.nan
    w = s.pivot_table(index=["cell", "stratum"], columns="variable", values=["lag_h2", "p_h2"]).reset_index()
    rows = []
    for b in ("ndvi", "evi"):
        m = (w[("p_h2", "sif_apar")] < alpha) & (w[("p_h2", b)] < alpha)
        d = (w[("lag_h2", "sif_apar")] - w[("lag_h2", b)])[m]
        z = ((w[("lag_h2", "sif_apar")] == 0) & (w[("lag_h2", b)] == 0))[m]
        for st, g in pd.DataFrame({"d": d, "z": z, "st": w["stratum"][m]}).groupby("st"):
            rows.append({"stratum": st, "against": b, "n": len(g), "median_diff": g.d.median(),
                         "share_zero": (g.d == 0).mean(), "share_negative": (g.d < 0).mean(),
                         "share_positive": (g.d > 0).mean(), "share_both_lag0": g.z.mean()})
    return {"summary_significant": sig, "summary_scale_lag": sl, "summary_scale_share": share,
            "summary_aed": aed, "summary_h2_lag_diff": pd.DataFrame(rows)}


def event_table(ep: pd.DataFrame) -> pd.DataFrame:
    """Post hoc: per drought event (>= event_min_cells) and stratum, cells and responses of each variable."""
    e = ep[ep["event"] >= 0].copy()
    e["onset"] = pd.to_datetime(e["onset"])
    resp = [c for c in e if c.startswith("resp_")]
    g = e.groupby(["event", "stratum"])
    out = g.agg(n_cells=("cell", "size"), onset_first=("onset", "min"), onset_last=("onset", "max")).reset_index()
    for c in resp:
        out[f"n_{c}"] = g[c].apply(lambda x: int(x.notna().sum())).values
    for b in ("ndvi", "evi"):
        out[f"n_pairs_sif_apar_{b}"] = g.apply(lambda x: int((x["resp_sif_apar"].notna() & x[f"resp_{b}"].notna())
                                                            .sum()), include_groups=False).values
    out["onset_month"] = out["onset_first"].dt.month
    out["posthoc"] = True
    return out


def _corr(a: np.ndarray, b: np.ndarray, min_n: int) -> np.ndarray:
    """Pearson r per column over rows where both are finite (explicit sums)."""
    m = np.isfinite(a) & np.isfinite(b)
    n = m.sum(0)
    a0, b0 = np.where(m, a, 0.0), np.where(m, b, 0.0)
    with np.errstate(all="ignore"):
        ma, mb = a0.sum(0) / n, b0.sum(0) / n
        da, db = np.where(m, a - ma, 0.0), np.where(m, b - mb, 0.0)
        r = (da * db).sum(0) / np.sqrt((da * da).sum(0) * (db * db).sum(0))
    return np.where(n >= min_n, r, np.nan)


def _partial(rxy, rxz, ryz):
    with np.errstate(all="ignore"):
        return (rxy - rxz * ryz) / np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))


def par_diagnostic(cfg: dict, ds: xr.Dataset) -> pd.DataFrame:
    """Post hoc: is the SIF/APAR link to AED (and SPEI) carried by radiation? Lag 0, April-October, all years;
    anomalies as in the analysis (q1.standardised_anomaly); PAR read from the same input as the series."""
    q, acfg = cfg["drought_q1"], cfg["anomalies"]
    days = ds["time"].values.astype("datetime64[D]")
    inp = epoch.open_inputs(dict(cfg, epoch=dict(cfg["epoch"], optical_sensitivity=False)), q["cells"]["grid"])
    par = epoch._extract(inp["par"]["par"], inp["sif"]["sif"], ds["iy"].values, ds["ix"].values, days)
    win = int(acfg["clim_doy_window"])
    z = {k: q1.standardised_anomaly(v, days, q["anomalies"], win) for k, v in
         {"sif_apar": ds["sif_apar"].values.astype(float), "ndvi": ds["ndvi"].values.astype(float),
          "par": par, "aed": ds["aed"].values.astype(float)}.items()}
    mo = pd.DatetimeIndex(ds["time"].values).month
    season = np.isin(mo, [int(m) for m in q["analysis1"]["months"]])
    z = {k: v[season] for k, v in z.items()}
    spei30 = ds["spei_030"].values.astype(float)[season]
    mn = 30                                              # as q1.corr_from_sums
    r = {"r_sifapar_par": _corr(z["sif_apar"], z["par"], mn), "r_par_aed": _corr(z["par"], z["aed"], mn),
         "r_sifapar_aed": _corr(z["sif_apar"], z["aed"], mn), "r_sifapar_spei030": _corr(z["sif_apar"], spei30, mn),
         "r_par_spei030": _corr(z["par"], spei30, mn), "r_ndvi_par": _corr(z["ndvi"], z["par"], mn),
         "r_ndvi_aed": _corr(z["ndvi"], z["aed"], mn), "r_ndvi_spei030": _corr(z["ndvi"], spei30, mn)}
    r["r_sifapar_aed_given_par"] = _partial(r["r_sifapar_aed"], r["r_sifapar_par"], r["r_par_aed"])
    r["r_sifapar_spei030_given_par"] = _partial(r["r_sifapar_spei030"], r["r_sifapar_par"], r["r_par_spei030"])
    r["r_ndvi_aed_given_par"] = _partial(r["r_ndvi_aed"], r["r_ndvi_par"], r["r_par_aed"])
    r["r_ndvi_spei030_given_par"] = _partial(r["r_ndvi_spei030"], r["r_ndvi_par"], r["r_par_spei030"])
    return pd.DataFrame({"cell": ds["cell"].values, "stratum": ds["stratum"].values,
                         "fuel_class": ds["fuel_class"].values, "aridity_class": ds["aridity_class"].values, **r})


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    q = cfg["drought_q1"]
    od = REPO_ROOT / q["out_dir"]
    alpha = float(q["analysis1"]["alpha"])
    cells = pd.read_csv(od / "analysis1_cells.csv")
    for k, v in scale_lag_tables(cells, alpha).items():
        v.to_csv(od / f"{k}.csv", index=False)
    event_table(pd.read_csv(od / "analysis2_episodes.csv")).to_csv(od / "posthoc_events.csv", index=False)
    cl = pd.read_csv(REPO_ROOT / q["spei"]["out_dir"] / "spei_q1_clamped.csv")
    num = [c for c in cl if c.startswith("n_")]
    sc = cl.groupby("scale_days")[num].sum().reset_index()
    sc["cells_clipped_all"] = cl.assign(a=cl[[c for c in num if c.endswith("_all")]].sum(axis=1) > 0) \
        .groupby("scale_days")["a"].sum().values
    sc.to_csv(od / "summary_spei_clip.csv", index=False)
    ds = xr.open_dataset(od / "drought_q1_series.nc").load()
    pc = par_diagnostic(cfg, ds)
    pc.to_csv(od / "posthoc_par_cells.csv", index=False)
    rc = [c for c in pc if c.startswith("r_")]
    summ = _strata(pc).groupby("stratum")[rc].agg(["median", lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)])
    summ.columns = [f"{a}_{'median' if b == 'median' else ('q25' if b == '<lambda_0>' else 'q75')}"
                    for a, b in summ.columns]
    summ.reset_index().assign(posthoc=True).to_csv(od / "posthoc_par_diagnostic.csv", index=False)
    log.info("wrote summary and post hoc tables in %s", od)


if __name__ == "__main__":
    main()
