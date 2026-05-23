import re
from pathlib import Path
from statistics import geometric_mean

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HW_DIR = Path(__file__).resolve().parents[1]
RAW_OUTPUT_DIR = HW_DIR / "raw_output"

CSV_OUTPUT = HW_DIR / "metrics.csv"
MD_OUTPUT = HW_DIR / "metrics.md"
IPC_PLOT_OUTPUT = HW_DIR / "ipc_comparison.png"
MISS_PLOT_OUTPUT = HW_DIR / "miss_rate_comparison.png"

TARGETS = ["lru", "plru", "srrip", "lip", "bip"]

def get_traces() -> list[str]:
    traces = set()
    for file in RAW_OUTPUT_DIR.glob("*.txt"):
        name_parts = file.stem.split("_")
        if len(name_parts) > 1 and name_parts[-1] in TARGETS:
            trace_name = "_".join(name_parts[:-1])
            traces.add(trace_name)

    return sorted(list(traces))

def parse_log(filepath: Path) -> tuple[float, float]:
    if not filepath.exists():
        return 0.0, 0.0

    text = filepath.read_text(encoding="utf-8")
    ipc_matches = re.findall(r"cumulative IPC:\s*([0-9.]+)", text)
    l2_matches = re.findall(r"cpu0_L2C\s+TOTAL\s+ACCESS:\s+(\d+)\s+HIT:\s+(\d+)\s+MISS:\s+(\d+)", text)

    ipc = float(ipc_matches[-1]) if ipc_matches else 0.0
    miss_rate = 0.0

    if l2_matches:
        accesses = int(l2_matches[-1][0])
        misses = int(l2_matches[-1][2])
        if accesses > 0:
            miss_rate = (misses / accesses) * 100.0

    return ipc, miss_rate

def generate_plot(df: pd.DataFrame, metric: str, ylabel: str, title: str, filename: Path) -> None:
    x = np.arange(len(df.index))
    width = 0.8 / len(TARGETS)

    fig, ax = plt.subplots(figsize=(18, 7))

    for i, target in enumerate(TARGETS):
        offset = (i - len(TARGETS) / 2) * width + width / 2
        col_name = f"{target.upper()}_{metric}"
        ax.bar(x + offset, df[col_name], width, label=target.upper())

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout()
    fig.savefig(filename, dpi=300)
    plt.close(fig)

def main() -> None:
    traces = get_traces()
    if not traces:
        return

    data: dict[str, list[float]] = {f"{t.upper()}_{m}": [] for t in TARGETS for m in ("IPC", "MISS")}

    for trace in traces:
        for target in TARGETS:
            log_path = RAW_OUTPUT_DIR / f"{trace}_{target}.txt"
            ipc, miss_rate = parse_log(log_path)

            data[f"{target.upper()}_IPC"].append(ipc)
            data[f"{target.upper()}_MISS"].append(miss_rate)

    df = pd.DataFrame(data, index=traces)

    gmean_row = {}
    for col in df.columns:
        valid_data = [v for v in df[col] if v > 0.0]
        gmean_row[col] = geometric_mean(valid_data) if valid_data else 0.0

    df.loc["GMEAN"] = gmean_row

    df.to_csv(CSV_OUTPUT)
    MD_OUTPUT.write_text(df.to_markdown(floatfmt=".4f"), encoding="utf-8")

    generate_plot(df, "IPC", "IPC (Higher is Better)", "L2 Cache Replacement: IPC Comparison", IPC_PLOT_OUTPUT)
    generate_plot(df, "MISS", "L2 Miss Rate % (Lower is Better)", "L2 Cache Replacement: Miss Rate Comparison", MISS_PLOT_OUTPUT)

if __name__ == "__main__":
    main()
