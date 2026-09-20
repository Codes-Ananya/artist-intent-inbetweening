"""Run a tiny RIFE benchmark in a normal WSL GPU shell."""
import sys
from inbetween.benchmark import run_benchmark

if __name__ == '__main__':
    results=run_benchmark('outputs/benchmark-gpu-smoke',('small_translation','large_translation'),('rife',),2)
    for result in results: print(result['case_id'],result['status'],result.get('error',''))
    sys.exit(0 if all(r['status']=='ok' for r in results) else 1)
