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

The first normal-WSL GPU benchmark completed all 20 case/backend combinations with exact endpoints. RIFE inference-loop times were approximately 0.20–0.64 seconds, and peak VRAM was 86,549,504 bytes. This run was provisional: two trajectory sequence aggregates were missing and report handling required correction. The original report was not accepted; the corrected rerun is recorded below.

### Corrected normal-WSL GPU benchmark, 2026-09-20

The user ran the corrected benchmark in a normal WSL shell with `python -m inbetween.benchmark --backends crossfade rife --output outputs/benchmark-full-v2`. The local result directory `outputs/benchmark-full-v2` is ignored by Git. All ten procedural cases completed for both backends: 20 successful case/backend runs. Every sequence preserved both endpoint frames exactly. Cloud compute was not used.

RIFE peak CUDA allocation was 86,549,504 bytes in every case. After the first run, typical RIFE inference-loop time was approximately 0.35 seconds for six intermediate 256×256 frames. The first RIFE case took 2.100 seconds to load the model and 0.826 seconds for inference.

On these synthetic diagnostics, RIFE strongly outperformed crossfade for small translation, large translation, articulated limb, and crossing limb. Improvements were modest or mixed for rigid rotation and squash/stretch. RIFE did not reliably encode animation intent: it was weak on curved arcs, hold-then-fast timing, and exaggeration. In the occlusion case, RIFE trajectory measurements covered only 3 of 6 intermediate frames, so that trajectory score needs cautious interpretation. These results are not evidence of performance on artist-created animation.

## 2026-09-20: Milestone 4 guided breakdown diagnostic

Implemented local orchestration that splits an `InterpolationBackend` run at an authoritative D, with exact saved-PNG checks for A, D and B. The Gradio tab compares endpoint-only and guided RIFE. The controlled benchmark derives D from ground truth for curved arc, hold-then-fast, exaggeration and occlusion. It is an oracle diagnostic, not an artist study, and splitting at D is not claimed as a novel algorithm. The intended research value is measuring intervention benefit and placement, then learning when and where artist input helps most. No cloud services, training or new model were used.

Sandbox validation: application `pip check` and offline pinned-lock dry run passed; Python compilation passed; pytest passed 41 tests with 1 CUDA-dependent skip. The guided CPU crossfade diagnostic completed all four categories and both methods with exact authoritative frames and strict JSON. The existing crossfade sample and benchmark quick test passed. Gradio returned HTTP 200 on loopback port 7861; `git diff --check` and generated-output/weight ignore checks passed. CUDA was unavailable (`torch.cuda.is_available() == False`); the existing GPU benchmark smoke failed for that reason. No RIFE quality or GPU timing result is claimed for Milestone 4 until the separate normal-WSL smoke test runs.

### Methodology correction

Independent review found that the earlier guided benchmark aggregate included oracle index k for the guided method. The earlier v1 aggregates are superseded for quantitative interpretation; their values are not evidence for a paired comparison. The corrected primary means use indices 1..N excluding k for both methods, report k separately, and explicitly represent perfect PSNR. Runtime values remain operational diagnostics because guided invokes the backend twice and endpoint-only once, with potentially different model-loading behavior.

Correction validation: compilation passed; full pytest passed 43 tests with 1 CUDA-dependent skip. The CPU guided crossfade benchmark completed all four cases for both methods; its JSON parsed with strict nonfinite rejection and every record used the same generated-only frame index. The sample export and quick crossfade baseline benchmark passed. Gradio startup returned HTTP 200 on loopback port 7861. `git diff --check` passed, and ignore checks covered generated outputs, RIFE weights, and the virtual environment. The GPU benchmark was not rerun in the restricted shell.

### Corrected normal-WSL GPU benchmark, 2026-09-21

The corrected local RIFE run at `outputs/guided-breakdown-benchmark-v2` completed all four procedural cases with both endpoint-only and guided methods successful. Primary metrics compare the identical generated indices `[1, 2, 4, 5, 6]` for both methods; oracle breakdown index 3 is excluded from both primary aggregates and reported separately. A, D and B passed exact-pixel checks. Peak CUDA allocation was 86,549,504 bytes. Cloud compute was not used.

| Case | Guided PSNR gain | SSIM gain | Edge F1 gain | Chamfer reduction | Trajectory error reduction |
|---|---:|---:|---:|---:|---:|
| `curved_arc` | +0.83 dB | +0.012 | +0.246 | 68.9% | 81.1% |
| `hold_then_fast` | +17.05 dB | +0.028 | +0.305 | 61.0% | 44.7% |
| `exaggeration` | +1.81 dB | +0.020 | +0.394 | 71.4% | 73.7% |
| `occlusion` | +7.12 dB | +0.028 | +0.184 | 74.2% | 66.3% |

For `occlusion`, trajectory coverage improved from 3/5 endpoint-only frames to 5/5 guided frames; its trajectory error means therefore cover different numbers of measurable frames. These are procedural oracle-breakdown results. They do not establish performance with artist-created drawings or novelty. Runtime values are not used for method comparison because backend invocation and model-loading behavior differ. The earlier v1 aggregates are superseded by this corrected run.
