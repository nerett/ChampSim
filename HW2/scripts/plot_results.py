import re
from pathlib import Path
from statistics import geometric_mean

import matplotlib.pyplot as plt
import numpy as np

PREDICTORS: list[str] = ["bimodal", "gag", "gap", "pap"]

TRACES: list[str] = [
    "600.perlbench", "602.gcc", "603.bwaves", "605.mcf", "607.cactuBSSN", "619.lbm",
    "620.omnetpp", "621.wrf", "623.xalancbmk", "625.x264", "627.cam4", "628.pop2",
    "631.deepsjeng", "638.imagick", "641.leela", "644.nab", "648.exchange2",
    "649.fotonik3d", "654.roms", "657.xz"
]

def parse_log(filepath: Path) -> tuple[float, float]:
    if not filepath.exists():
        return 0.0, 0.0

    text = filepath.read_text(encoding="utf-8")
    ipc_matches = re.findall(r"cumulative IPC:\s*([0-9.]+)", text)
    mpki_matches = re.findall(r"MPKI:\s*([0-9.]+)", text)

    ipc = float(ipc_matches[-1]) if ipc_matches else 0.0
    mpki = float(mpki_matches[-1]) if mpki_matches else 0.0

    return ipc, mpki

def plot_bar_chart(
    data: dict[str, list[float]],
    labels: list[str],
    ylabel: str,
    title: str,
    filename: str
) -> None:
    x = np.arange(len(labels))
    width = 0.2

    fig, ax = plt.subplots(figsize=(16, 7))

    for i, pred in enumerate(PREDICTORS):
        ax.bar(x + i * width, data[pred], width, label=pred.upper())

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout()
    fig.savefig(filename, dpi=300)
    plt.close(fig)

def main() -> None:
    results_dir = Path("results")

    ipc_data: dict[str, list[float]] = {p: [] for p in PREDICTORS}
    mpki_data: dict[str, list[float]] = {p: [] for p in PREDICTORS}

    for trace in TRACES:
        for pred in PREDICTORS:
            log_path = results_dir / f"{trace}_{pred}.txt"
            ipc, mpki = parse_log(log_path)
            ipc_data[pred].append(ipc)
            mpki_data[pred].append(mpki)

    for pred in PREDICTORS:
        valid_ipc = [val for val in ipc_data[pred] if val > 0.0]
        valid_mpki = [val for val in mpki_data[pred] if val > 0.0]

        gmean_ipc = geometric_mean(valid_ipc) if valid_ipc else 0.0
        gmean_mpki = geometric_mean(valid_mpki) if valid_mpki else 0.0

        ipc_data[pred].append(gmean_ipc)
        mpki_data[pred].append(gmean_mpki)

    plot_labels = TRACES + ["GMEAN"]

    plot_bar_chart(
        data=ipc_data,
        labels=plot_labels,
        ylabel="IPC (Higher is Better)",
        title="IPC Comparison Across Branch Predictors",
        filename="ipc_comparison.png"
    )

    plot_bar_chart(
        data=mpki_data,
        labels=plot_labels,
        ylabel="MPKI (Lower is Better)",
        title="MPKI Comparison Across Branch Predictors",
        filename="mpki_comparison.png"
    )

if __name__ == "__main__":
    main()
