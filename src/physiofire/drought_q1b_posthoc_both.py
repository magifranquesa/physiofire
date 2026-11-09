"""Q1b, POST HOC sensitivity (declared 2026-11-09, after the H3b result; external manuscript review, close-out check 5).

H3b statistics (mean over events of the event mean sign score with bootstrap CI by event; median over events of the
event median d) recomputed only with the cell-episodes in which BOTH SIF/APAR and the reference responded within the
window (no censored pair), by reference index and season of onset, shrubland stratum. Same function, parameters and
seed as the criterion (drought_q1b.h3b_test); the only change is the pair subset. Not part of any criterion.

Output: data/processed/drought_q1b/summary_posthoc_h3b_both_responded.csv
Usage: python -m physiofire.drought_q1b_posthoc_both
"""
from __future__ import annotations

import pandas as pd

from . import drought_q1b as qb
from .config import REPO_ROOT, load_config


def main() -> None:
    cfg = load_config()
    hb, q = cfg["drought_q1b"]["h3b"], cfg["drought_q1"]
    od = REPO_ROOT / cfg["drought_q1b"]["out_dir"]
    ep = pd.read_csv(od / "analysis2b_episodes.csv")
    rows = []
    for st in ["shrubland"]:
        es = ep[ep["stratum"] == st]
        for b in ("ndvi", "evi"):
            for subset in ("all_pairs", "both_responded"):
                s0 = es if subset == "all_pairs" else es[es["resp_sif_apar"].notna() & es[f"resp_{b}"].notna()]
                for sn in ["all"] + list(hb["seasons"]):
                    s = s0 if sn == "all" else s0[s0["event_season"] == sn]
                    h = qb.h3b_test(s, "sif_apar", b, int(hb["censor_day"]), float(hb["max_median_diff_days"]),
                                    int(hb["min_events"]), int(q["bootstrap_n"]), int(cfg["random_seed"]))
                    rows.append({"stratum": st, "against": b, "pairs": subset, "season": sn, **h, "posthoc": True})
    out = pd.DataFrame(rows)
    out.to_csv(od / "summary_posthoc_h3b_both_responded.csv", index=False)
    cols = ["against", "pairs", "season", "n_events", "n_pairs_informative", "mean_score", "ci_lo", "ci_hi", "median_d",
            "share_sif_first", "evaluable", "met"]
    print(out[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
