import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

MAX_WORKERS = 8
WARMUP_INST = 5_000_000
SIM_INST = 25_000_000

BASE_DIR = Path(".")

def run_simulation(binary_path: Path, trace_path: Path, output_path: Path) -> None:
    cmd = [
        str(binary_path),
        "-w", str(WARMUP_INST),
        "-i", str(SIM_INST),
        str(trace_path)
    ]

    with open(output_path, "w") as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=False)

def main() -> None:
    traces_dir = BASE_DIR / ".." / "traces"
    results_dir = BASE_DIR.parent / "results"
    results_dir.mkdir(exist_ok=True)

    binaries = [
        BASE_DIR / "bin" / "champsim_bimodal",
        BASE_DIR / "bin" / "champsim_gag",
        BASE_DIR / "bin" / "champsim_gap",
        BASE_DIR / "bin" / "champsim_pap",
    ]

    for b in binaries:
        if not b.exists():
            raise FileNotFoundError(f"Binary {b} not found!")

    traces = list(traces_dir.rglob("*.xz"))
    if not traces:
        raise FileNotFoundError("No traces found in 'traces' directory!")

    tasks = []
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for trace in traces:
            trace_base_name = trace.name.split("_s-")[0]
            for binary in binaries:
                pred_name = binary.name.split("_")[-1]
                output_path = results_dir / f"{trace_base_name}_{pred_name}.txt"

                tasks.append(
                    executor.submit(run_simulation, binary, trace, output_path)
                )

    for future in tasks:
        future.result()

if __name__ == "__main__":
    main()
