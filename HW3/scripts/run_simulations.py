import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MAX_WORKERS = 8
WARMUP_INST = 5_000_000
SIM_INST = 25_000_000

BASE_DIR = Path(__file__).parents[2]
TRACE_DIR = BASE_DIR.parent / "traces"

HW_DIR = Path(__file__).parents[1]
RES_DIR =  HW_DIR / "raw_output"

BINARIES = [
    BASE_DIR / "bin" / "champsim_lru",
    BASE_DIR / "bin" / "champsim_plru",
    BASE_DIR / "bin" / "champsim_lip",
    BASE_DIR / "bin" / "champsim_bip",
    BASE_DIR / "bin" / "champsim_srrip",
]

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
    print(f"Running with paths:\n{BASE_DIR=}\n{TRACE_DIR=}\n{RES_DIR=}")

    RES_DIR.mkdir(exist_ok=True, parents=True)

    for b in BINARIES:
        if not b.exists():
            raise FileNotFoundError(f"Binary {b} not found!")

    traces = list(TRACE_DIR.rglob("*.xz"))
    if not traces:
        raise FileNotFoundError("No traces found in 'traces' directory!")

    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for trace in traces:
            trace_base_name = trace.name.split("_s-")[0]
            for binary in BINARIES:
                version_name = binary.name.split("_")[-1]
                output_path = RES_DIR / f"{trace_base_name}_{version_name}.txt"

                tasks.append(
                    executor.submit(run_simulation, binary, trace, output_path)
                )

    for future in tasks:
        future.result()

if __name__ == "__main__":
    main()
