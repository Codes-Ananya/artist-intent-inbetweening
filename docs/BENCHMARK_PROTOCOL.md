# Controlled baseline benchmark protocol

This is a **synthetic diagnostic**, not evidence of real artist performance. The generator produces ten deterministic 256×256 RGB white-background character-like line drawings, 4 px nominal strokes, 3× supersampling and LANCZOS reduction. Default sampling is six intermediate frames at uniform timestamps `i/(N+1)`; hold/fast changes motion timing within those timestamps. Metadata beside each generated sequence records category, trajectory/timing, expected difficulty, resolution, seed, and frame count. No external data or training is used.

From the repository root:

```bash
.venv/bin/python -m inbetween.benchmark --output outputs/benchmark --backends crossfade --cases small_translation
.venv/bin/python -m inbetween.benchmark --quick --backends crossfade --output outputs/benchmark-quick
.venv/bin/python -m inbetween.benchmark --backends crossfade rife --output outputs/benchmark-full
.venv/bin/python scripts/benchmark_smoke_test.py
./launch.sh
```

The first command also generates ground-truth assets; all commands generate them automatically. `--cases`, `--backends`, `--count`, `--output`, and `--quick` select the workload. The full GPU command requires installed pinned RIFE assets and a CUDA-enabled normal WSL shell. The smoke script runs two cases with two intermediates and exits nonzero if RIFE fails. No automatic crossfade fallback occurs.

Each output directory contains `ground_truth/<case>/`, `runs/<case>/<backend>/<run-id>/`, `visuals/<case>/<backend>/contact_sheet.png`, `comparison.gif`, `frames.csv`, `results.json`, and `summary.md`. Contact sheet columns are reference, prediction, and absolute RGB difference; GIF columns are reference and prediction. Run manifests carry model source commit and checkpoint identity. Endpoints are checked pixel-for-pixel; a mismatch fails that sequence. See [METRICS.md](METRICS.md).

These cases test implementation behavior and known motion stress cases. They do not represent natural hand-drawn animation, drawing style, or artist preference. PSNR and SSIM can penalize plausible alternative motion. Edge metrics depend on line width and alignment. Smoothness is not automatically desirable in animation. Results must not be described as publication evidence until reviewed and supplemented with permissioned artist data.
