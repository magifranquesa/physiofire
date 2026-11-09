"""Q1b: summary tables of the result (criterion fixed in docs/plan_q1b.md) and post hoc diagnostics.

Reads the outputs of `python -m physiofire.drought_q1b` (data/processed/drought_q1b) and writes small CSV tables next
to them (versioned in git). It changes nothing in the analysis.

  summary_responses.csv        per variable, stratum and season: share observed, responding, at the window start
  summary_time_to_response.csv cumulative share responded by day (Kaplan-Meier with censoring at +90 only = empirical
                               cumulative share among observed cell-episodes in events)
  summary_lag_boundary.csv     share of cells with the SPEI-90 lag at -15 or +60 (main and centred runs)
  summary_scale_share.csv      share of cells by optimal SPEI scale (main run; SIF/APAR corrected)
  summary_par_fit.csv          PAR slope b by stratum
  summary_noise_fraction.csv   noise fraction f of SIF/APAR (corrected), NDVI and EVI by stratum
Post hoc (declared after seeing the H3b result, 2026-11-08):
  summary_posthoc_h3b_left_censored.csv  H3b without pairs where either variable "responds" at the window start
                                         (already <= -0.5 SD 30 days before onset), by season

Usage: python -m physiofire.drought_q1b_report
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from . import drought_q1b as qb
from .config import REPO_ROOT, load_config

log = logging.getLogger(__name__)
MAIN = ["sif_apar", "ndvi", "evi"]


def _strata(df: pd.DataFrame) -> pd.DataFrame:
    wh = df[df["fuel_class"] == "wet_heath"].assign(stratum="wet_heath_only")
    return pd.concat([df, wh], ignore_index=True)


def response_tables(ep: pd.DataFrame, w0: int, censor: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    e = _strata(ep[ep["event"] >= 0])
    e = pd.concat([e, e.assign(event_season="all")], ignore_index=True)
    rows, km = [], []
    for (st, sn), g in e.groupby(["stratum", "event_season"]):
        for v in MAIN:
            o = g[f"obs_{v}"].astype(bool)
            r = g.loc[o, f"resp_{v}"]
            rows.append({"stratum": st, "season": sn, "variable": v, "n_cell_episodes": len(g),
                         "share_observed": o.mean(), "share_responding": r.notna().mean(),
                         "share_at_window_start": (r == w0).mean(), "median_response_day": r.median()})
            for t in range(w0, censor + 1):
                km.append({"stratum": st, "season": sn, "variable": v, "day": t, "n": len(r),
                           "cum_share_responded": (r <= t).mean() if len(r) else np.nan})
    return pd.DataFrame(rows), pd.DataFrame(km)


def posthoc_left_censored(ep: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    hb, q = cfg["drought_q1b"]["h3b"], cfg["drought_q1"]
    w0 = int(q["analysis2"]["response_window_days"][0])
    rows = []
    for st in list(q["strata"]):
        es = ep[ep["stratum"] == st]
        for b in ("ndvi", "evi"):
            lc = (es["resp_sif_apar"] == w0) | (es[f"resp_{b}"] == w0)
            for name, sub in (("all_pairs", es), ("without_left_censored", es[~lc])):
                for sn in ["all"] + list(hb["seasons"]):
                    s = sub if sn == "all" else sub[sub["event_season"] == sn]
                    h = qb.h3b_test(s, "sif_apar", b, int(hb["censor_day"]), float(hb["max_median_diff_days"]),
                                    int(hb["min_events"]), int(q["bootstrap_n"]), int(cfg["random_seed"]))
                    rows.append({"stratum": st, "against": b, "pairs": name, "season": sn, **h, "posthoc": True})
    return pd.DataFrame(rows)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    q, qbc = cfg["drought_q1"], cfg["drought_q1b"]
    od = REPO_ROOT / qbc["out_dir"]
    alpha = float(q["analysis1"]["alpha"])
    lb = tuple(int(x) for x in qbc["analysis1"]["lags_days"])
    w0 = int(q["analysis2"]["response_window_days"][0])
    ep = pd.read_csv(od / "analysis2b_episodes.csv")
    resp, km = response_tables(ep, w0, int(qbc["h3b"]["censor_day"]))
    resp.to_csv(od / "summary_responses.csv", index=False)
    km.to_csv(od / "summary_time_to_response.csv", index=False)
    posthoc_left_censored(ep, cfg).to_csv(od / "summary_posthoc_h3b_left_censored.csv", index=False)
    bnd = []
    for mode in ("backward", "centred"):
        f = od / f"analysis1b_cells_{mode}.csv"
        if f.exists():
            res = pd.read_csv(f)
            bnd.append(qb.boundary_share(_strata(res), alpha, lb).assign(run=mode))
            if mode == qbc["analysis1"]["smoothing"]:
                s = _strata(res[(res["explanatory"] == "spei") & res["variable"].isin(MAIN) & (res["p"] < alpha)])
                (s.groupby(["stratum", "variable"])["scale_days"].value_counts(normalize=True).rename("share")
                 .reset_index().to_csv(od / "summary_scale_share.csv", index=False))
    if bnd:
        pd.concat(bnd).to_csv(od / "summary_lag_boundary.csv", index=False)
    fit = _strata(pd.read_csv(od / "par_fit.csv"))
    fit.groupby("stratum")["b_par"].describe(percentiles=[0.25, 0.5, 0.75]).reset_index() \
        .to_csv(od / "summary_par_fit.csv", index=False)
    nf = od / "noise_fraction.csv"
    if nf.exists():
        n = _strata(pd.read_csv(nf))
        a = n.groupby(["stratum", "variable"]).agg(f_median=("f", "median"), f_sif_apar_median=("f_sif_apar", "median"),
                                                   share_noise_added=("noise_var", lambda x: (x > 0).mean()))
        a.reset_index().to_csv(od / "summary_noise_fraction.csv", index=False)
    log.info("wrote Q1b summary tables in %s", od)


if __name__ == "__main__":
    main()
