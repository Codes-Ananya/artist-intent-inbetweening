# Research log

## 2026-09-20: Milestone 1

Environment: Python 3.10.12 virtual environment, FFmpeg available. Initial `nvidia-smi` failed with “GPU access blocked by the operating system”; the placeholder needs no CUDA. Gradio, OpenCV, and pytest were installed into the existing virtual environment. Measured test and sample results are recorded below after verification.

Verification: `pytest -q` passed 6 tests in 2.56 seconds. A sample run with 256×144 RGBA keyframes, 6 intermediate frames, and 12 FPS produced 8 ordered PNGs plus GIF, MP4, manifest, and JSONL log. The Gradio application built and, when launched outside the restricted shell sandbox on loopback port 7861, returned HTTP 200 from `curl -I`. The sandbox itself denied socket access on ports 7860 and 7861. The restricted Codex command sandbox could not access GPU/NVML; this does not establish CUDA availability in the normal WSL shell. No GPU operations are required by this backend.

## 2026-09-20: Dependency and diagnostic correction

The normal WSL shell previously verified PyTorch 2.14.0+cu126 with CUDA available: true on an RTX 4050 Laptop GPU with 6GB VRAM. Codex’s restricted command sandbox may lack WSL `/dev/dxg` device passthrough even when CUDA works in the normal WSL shell. The application lockfile excludes PyTorch/CUDA; those wheels are pinned separately in `requirements-gpu-cu126.txt`. OpenCV was removed from application requirements because no current code imports it.

Correction verification: application and GPU requirement versions matched the installed environment; `pip check` found no broken requirements. The pinned application lock resolved with `pip install --dry-run --no-index`. Python compilation succeeded, `pytest -q` passed 10 tests in 1.11 seconds, and sample generation created `outputs/20260920T160141-0cf2ec2e/`. Gradio returned HTTP 200 on loopback port 7861. `git diff --check` passed, and `git check-ignore` confirmed generated outputs remain ignored.

## 2026-09-20: Milestone 2 RIFE integration

Reviewed the [official ECCV2022-RIFE repository](https://github.com/hzwer/ECCV2022-RIFE), its MIT license, `model/RIFE.py`, and `benchmark/HD_multi_4X.py`. The latter uses `Model(arbitrary=True)` with direct `timestep` values, so the adapter can request any count at `i/(N+1)`. The author-published `RIFE_m_train_log.zip` at pinned Hugging Face revision was downloaded locally: 39,819,850 bytes and SHA-256 `8cb49709fde0d53de8167273986458db1b15ff45b947a042026f1d383c99c8d7`. Its `flownet.pkl` is 42,884,324 bytes and SHA-256 `9f9e2e8b5c3fef311c9a782aa17a30f87c388ce6dc9c00e4993eba3d3941d3cb`. The state dictionary loaded strictly into the pinned RIFE_m architecture on CPU (10,710,780 parameters). Setup reran successfully using the verified local assets. The Codex sandbox reported `torch.cuda.is_available() == False`; `scripts/rife_smoke_test.py` therefore exited non-zero as designed. GPU inference time, VRAM, and visual quality remain unmeasured pending the normal WSL shell acceptance run.

Sandbox validation after implementation: `pip check` reported no broken requirements; Python compilation passed; `pytest -q` passed 17 tests in 4.05 seconds; crossfade sample generation created `outputs/20260920T161204-325c6838/`; Gradio returned HTTP 200 on loopback port 7861. Torch and torchvision remained at `2.14.0+cu126` and `0.29.0+cu126`. `git diff --check` passed. Git ignore checks covered RIFE source, weights, and generated output.

## 2026-09-20: Normal-WSL GPU acceptance run

Ran the RIFE smoke test and a Gradio UI generation in the normal WSL shell (outside the Codex sandbox) on the RTX 4050 Laptop GPU. `torch.cuda.is_available()` was `True`, GPU: "NVIDIA GeForce RTX 4050 Laptop GPU, 6GB". RIFE source verified against the official [hzwer/ECCV2022-RIFE](https://github.com/hzwer/ECCV2022-RIFE) repository at pinned commit `5d8adbdd40e12c2c8f91930eff838aebe561c086`; checkpoint SHA-256 `9f9e2e8b5c3fef311c9a782aa17a30f87c388ce6dc9c00e4993eba3d3941d3cb`. The run produced four total frames (the two uploaded endpoints plus two generated intermediates); inference took 0.528 seconds with peak CUDA memory of 66.1 MiB. Endpoint frames compared pixel-exact against the uploaded source PNGs. The Gradio UI completed a RIFE generation successfully. No cloud compute was used at any point.

These measurements apply only to the synthetic smoke-test images used for this run and are not general performance claims about typical animation frames, resolutions, or frame counts.

## Milestone 3 controlled diagnostic

Implemented a reproducible local procedural suite for ten motion stress categories. This is an implementation check, not a study of natural hand-drawn animation or artist preference. PSNR/SSIM may penalize valid alternative motion; edge scores depend on alignment and line width; smoothness is not inherently desirable. Publication claims require review and permissioned artist data. Benchmark commands and metric definitions are in `BENCHMARK_PROTOCOL.md` and `METRICS.md`.

### Codex validation, 2026-09-20

`pip check` and `compileall` passed. Pytest: 22 passed, 1 skipped (the existing mocked RIFE OOM test requires CUDA before reaching the mock). The full six-intermediate crossfade benchmark completed all 10 cases (60 intermediate comparisons) with exact endpoints, and produced reports and visuals under `outputs/benchmark-full/`. CUDA was unavailable in this sandbox (`torch.cuda.is_available() == False`). Gradio returned HTTP 200 on localhost port 7861. Ignore checks confirmed benchmark reports and images stay untracked.

The first normal-WSL GPU benchmark completed all 20 case/backend combinations with exact endpoints. RIFE inference-loop times were approximately 0.20–0.64 seconds, and peak VRAM was 86,549,504 bytes. This run was provisional: two trajectory sequence aggregates were missing and report handling required correction. Corrected results must be regenerated before Milestone 3 acceptance; the original report must not be treated as an accepted result.
