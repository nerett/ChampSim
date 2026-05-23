import re
from pathlib import Path
from statistics import geometric_mean
import matplotlib.pyplot as plt
import numpy as np

RES_DIR = Path(__file__).parents[1] / "raw_output"
POLICIES: list[str] = ["lru", "plru", "srrip", "lip", "bip"]

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
    ipc = float(ipc_matches[-1]) if ipc_matches else 0.0

    l2_matches = re.findall(r"cpu0_L2C\s+TOTAL\s+ACCESS:\s+(\d+)\s+HIT:\s+(\d+)\s+MISS:\s+(\d+)", text)

    miss_rate = 0.0
    if l2_matches:
        accesses = int(l2_matches[-1][0])
        misses = int(l2_matches[-1][2])
        if accesses > 0:
            miss_rate = (misses / accesses) * 100.0

    return ipc, miss_rate

def plot_bar_chart(
    data: dict[str, list[float]],
    labels: list[str],
    ylabel: str,
    title: str,
    filename: str
) -> None:
    x = np.arange(len(labels))
    width = 0.15

    fig, ax = plt.subplots(figsize=(18, 7))

    for i, policy in enumerate(POLICIES):
        offset = (i - len(POLICIES) / 2) * width + width / 2
        ax.bar(x + offset, data[policy], width, label=policy.upper())

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout()
    fig.savefig(filename, dpi=300)
    plt.close(fig)

def main() -> None:
    print(f"Starting with {RES_DIR=}")
    ipc_data: dict[str, list[float]] = {p: [] for p in POLICIES}
    miss_rate_data: dict[str, list[float]] = {p: [] for p in POLICIES}

    for trace in TRACES:
        for policy in POLICIES:
            log_path = RES_DIR / f"{trace}_{policy}.txt"
            ipc, miss_rate = parse_log(log_path)
            ipc_data[policy].append(ipc)
            miss_rate_data[policy].append(miss_rate)

    for policy in POLICIES:
        valid_ipc = [val for val in ipc_data[policy] if val > 0.0]
        valid_mr = [val for val in miss_rate_data[policy] if val > 0.0]

        gmean_ipc = geometric_mean(valid_ipc) if valid_ipc else 0.0
        gmean_mr = geometric_mean(valid_mr) if valid_mr else 0.0

        ipc_data[policy].append(gmean_ipc)
        miss_rate_data[policy].append(gmean_mr)

    plot_labels = TRACES + ["GMEAN"]

    plot_bar_chart(
        data=ipc_data,
        labels=plot_labels,
        ylabel="IPC (Higher is Better)",
        title="L2 Cache Replacement: IPC Comparison",
        filename="hw3_ipc_comparison.png"
    )

    plot_bar_chart(
        data=miss_rate_data,
        labels=plot_labels,
        ylabel="L2 Miss Rate % (Lower is Better)",
        title="L2 Cache Replacement: Miss Rate Comparison",
        filename="hw3_miss_rate_comparison.png"
    )

if __name__ == "__main__":
    main()
