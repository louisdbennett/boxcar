import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import pandas as pd
from plotnine import ggplot, aes, geom_histogram, geom_density, labs,theme_minimal, theme, element_text


def plot_taxi_path(taxi, outdir="outputs/figures", filename=None):
    path = taxi.path 

    segs = np.array([[s["start"], s["end"]] for s in path], dtype=float)
    occ  = np.array([s["has_rider"] for s in path], dtype=bool)

    os.makedirs(outdir, exist_ok=True)
    if filename is None:
        filename = f"taxi_{taxi.number}.png"
    outpath = os.path.join(outdir, filename)

    fig, ax = plt.subplots(figsize=(7, 6))

    lc = LineCollection(segs, colors=np.where(occ, "C1", "C0"), linewidths=2, alpha=0.95)
    ax.add_collection(lc)

    ax.scatter(*segs[0, 0], marker="o", s=40, label="start")
    ax.scatter(*segs[-1, 1], marker="X", s=55, label="end")

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x (miles)")
    ax.set_ylabel("y (miles)")
    ax.set_title(f"Taxi #{taxi.number} (money={taxi.money_made:.2f})")
    ax.autoscale()

    ax.plot([], [], color="C0", linewidth=2, label="empty / no rider")
    ax.plot([], [], color="C1", linewidth=2, label="occupied / rider onboard")
    ax.legend(loc="best")

    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)
    return outpath


def get_histos(
    csv_path: str = "outputs/results.csv",
    outdir: str = "outputs/histograms_by_config",
    bins: int = 20,
    dpi: int = 200,
):
    df = pd.read_csv(csv_path)

    skip = {"run_name", "cfg"}

    cols = [
        c for c in df.columns
        if c not in skip
    ]

    os.makedirs(outdir, exist_ok=True)

    cfgs = df["cfg"].unique()

    for cfg_val in cfgs:
        mask = df["cfg"] == cfg_val
        sub = df.loc[mask]

        cfg_tag = str(cfg_val).replace(" ", "").replace("{", "").replace("}", "").replace("'", "")
        cfg_tag = cfg_tag.replace(":", "_").replace(",", "__")
        if len(cfg_tag) > 120:
            cfg_tag = cfg_tag[:120]

        for col in cols:
            data = sub[[col]].dropna()
            if data.empty:
                continue

            p = (
                ggplot(data, aes(x=col))
                + geom_histogram(aes(y="..density.."), bins=bins, fill="#4C78A8", color="#2F2F2F", alpha=0.75)
                + geom_density(color="#F58518", size=1.1)
                + labs(title=f"{col} (cfg={cfg_val})", x=col, y="Density")
                + theme_minimal()
                + theme(
                    figure_size=(7, 5),
                    plot_title=element_text(size=11, weight="bold"),
                    axis_title=element_text(size=10),
                )
            )

            fname = f"{col.replace(' ', '_')}_{cfg_tag}.png"
            p.save(os.path.join(outdir, fname), dpi=dpi, verbose=False)