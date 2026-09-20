"""Normal-WSL CUDA acceptance test using pinned local RIFE assets."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inbetween.guided_benchmark import run_guided_benchmark


def main():
    records = run_guided_benchmark("outputs/guided-rife-smoke", ["curved_arc"], 2, "rife", 1)
    if len(records) != 2 or any(record["status"] != "ok" for record in records):
        raise SystemExit(f"Guided RIFE smoke failed: {records}")
    print("Guided RIFE smoke passed:", Path("outputs/guided-rife-smoke/results.json"))


if __name__ == "__main__":
    main()
