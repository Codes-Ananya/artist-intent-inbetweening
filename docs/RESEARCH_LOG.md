# Research log

## 2026-09-20: Milestone 1

Environment: Python 3.10.12 virtual environment, FFmpeg available. Initial `nvidia-smi` failed with “GPU access blocked by the operating system”; the placeholder needs no CUDA. Gradio, OpenCV, and pytest were installed into the existing virtual environment. Measured test and sample results are recorded below after verification.

Verification: `pytest -q` passed 6 tests in 2.56 seconds. A sample run with 256×144 RGBA keyframes, 6 intermediate frames, and 12 FPS produced 8 ordered PNGs plus GIF, MP4, manifest, and JSONL log. The Gradio application built and, when launched outside the restricted shell sandbox on loopback port 7861, returned HTTP 200 from `curl -I`. The sandbox itself denied socket access on ports 7860 and 7861. The restricted Codex command sandbox could not access GPU/NVML; this does not establish CUDA availability in the normal WSL shell. No GPU operations are required by this backend.

## 2026-09-20: Dependency and diagnostic correction

The normal WSL shell previously verified PyTorch 2.14.0+cu126 with CUDA available: true on an RTX 4050 Laptop GPU with 6GB VRAM. Codex’s restricted command sandbox may lack WSL `/dev/dxg` device passthrough even when CUDA works in the normal WSL shell. The application lockfile excludes PyTorch/CUDA; those wheels are pinned separately in `requirements-gpu-cu126.txt`. OpenCV was removed from application requirements because no current code imports it.

Correction verification: application and GPU requirement versions matched the installed environment; `pip check` found no broken requirements. The pinned application lock resolved with `pip install --dry-run --no-index`. Python compilation succeeded, `pytest -q` passed 10 tests in 1.11 seconds, and sample generation created `outputs/20260920T160141-0cf2ec2e/`. Gradio returned HTTP 200 on loopback port 7861. `git diff --check` passed, and `git check-ignore` confirmed generated outputs remain ignored.
