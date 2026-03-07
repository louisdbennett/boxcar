import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

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