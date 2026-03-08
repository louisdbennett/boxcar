import os
import numpy as np
import pandas as pd
from scipy import stats


def test_all_configs(
    csv_path: str = "outputs/results.csv",
    baseline_cfg: str = "cr=closest, ms=None, bl=None",
    out_csv: str = "outputs/hypothesis_tests_all_vs_baseline.csv",
    alpha: float = 0.05,
    bins: int = 4,
):
    df = pd.read_csv(csv_path)

    skip = {"run_name", "cfg", "Highest earning taxi id", "Lowest earning taxi id"}
    metrics = [c for c in df.columns if c not in skip]

    base = df[df["cfg"] == baseline_cfg].copy()

    cfgs = [c for c in df["cfg"].unique() if c != baseline_cfg]
    rows = []

    for cfg in cfgs:
        test = df[df["cfg"] == cfg].copy()

        for m in metrics:
            x = base[m].dropna().to_numpy(dtype=float)
            y = test[m].dropna().to_numpy(dtype=float)
            ks_stat, ks_p = stats.ks_2samp(x, y)

            reject_null = ks_p < alpha
            
            rows.append({
                "config": cfg,
                "metric": m,
                "ks_stat": ks_stat,
                "p_value": ks_p,
                "alpha": alpha,
                "reject_null": reject_null,
                "conclusion": "Different Distribution" if reject_null else "Same Distribution",
                "baseline_mean": np.mean(x),
                "test_mean": np.mean(y),
                "diff_percent": ((np.mean(y) - np.mean(x)) / np.mean(x)) * 100
            })

    out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    out.to_csv(out_csv, index=False)