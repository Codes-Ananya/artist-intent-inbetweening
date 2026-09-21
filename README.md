# Preserving Artistic Intent in 2D Animation In-Betweening

Milestone 1 is a local, deterministic Gradio prototype. It creates a crossfade between two PNG keyframes and exports an ordered PNG sequence, GIF, MP4, and JSON manifest. It does not use a trained motion model.

## Setup and launch

Use Python 3.10 and the existing `.venv`. The verified GPU environment uses CUDA 12.6 PyTorch wheels on an RTX 4050 6GB. Install the GPU requirements first:

```bash
.venv/bin/python -m pip install -r requirements-gpu-cu126.txt
```

Then install the application requirements:

```bash
.venv/bin/python -m pip install -r requirements.txt
./launch.sh
```

`requirements-lock.txt` pins the verified application dependency environment for reproducibility; install it instead of `requirements.txt` when exact application versions are needed. PyTorch and CUDA are controlled separately by `requirements-gpu-cu126.txt`. The placeholder backend can run without PyTorch, but the GPU installation prepares later model integration.

Open `http://127.0.0.1:7860`. To use another port: `GRADIO_SERVER_PORT=7861 ./launch.sh`. The app binds to loopback only. FFmpeg must be on `PATH`.

Upload two RGB or RGBA PNGs with identical dimensions and mode. Select 0–120 intermediate frames and 1–60 FPS. Use the timeline, frame slider, and animated GIF preview, then download the PNG frames, MP4, or manifest. Each run is saved under ignored `outputs/<run-id>/` with a GIF and JSONL log too. The original endpoint pixels are retained exactly in the PNG sequence.

## Verify

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m inbetween.sample
```

Synthetic keyframes are in `samples/`. See `docs/` for specification, architecture, acceptance criteria, decisions, and research results.

## Optional local RIFE baseline (Milestone 2)

RIFE is a comparison baseline, not the proposed research contribution. It uses the official MIT-licensed [ECCV2022-RIFE](https://github.com/hzwer/ECCV2022-RIFE) implementation and the author's RIFE_m arbitrary-timestep checkpoint. The exact source commit, checkpoint revision, sizes, and SHA-256 hashes are in [RIFE provenance](docs/RIFE_PROVENANCE.md).

After installing the CUDA PyTorch requirements above, download the pinned local assets without changing the virtual environment:

```bash
.venv/bin/python scripts/setup_rife.py
```

The checkpoint archive is 39,819,850 bytes (38.0 MiB), and the extracted weight file is 42,884,324 bytes. The script verifies both hashes, can be rerun, and reports errors on failure. It places source and weights under ignored `.local/rife/`. To remove them, run `rm -r .local/rife`.

Launch the app and select **RIFE local AI baseline**. RIFE requires CUDA; a missing checkpoint, CUDA failure, or inference error is shown directly and never causes a crossfade fallback. For an RTX 4050 6GB, start with keyframes at or below **512×512** and **2–8 intermediate frames**. Larger inputs are reduced to a 512×512 pixel area budget for inference, then generated frames are restored to the input dimensions. Padding, resizing, alpha treatment, inference time, and peak GPU memory appear in the run manifest. Uploaded first and last PNG pixels remain exact. The RIFE adapter uses float32; FP16 awaits GPU validation.

Run the GPU acceptance check in a normal WSL shell with GPU passthrough:

```bash
.venv/bin/python scripts/rife_smoke_test.py
```

The restricted Codex sandbox may not expose `/dev/dxg`; its CUDA failure does not imply that the normal WSL shell lacks CUDA. The smoke script must pass there before treating RIFE inference as GPU-verified.

## Milestone 3: controlled baseline benchmark

The local synthetic diagnostic suite generates ten deterministic 256×256 line-art motion cases with known intermediate frames. It compares the existing crossfade and RIFE baselines. This does not measure natural artist performance or preference. See [benchmark protocol](docs/BENCHMARK_PROTOCOL.md) and [metric definitions](docs/METRICS.md).

```bash
.venv/bin/python -m inbetween.benchmark --output outputs/benchmark --backends crossfade
.venv/bin/python -m inbetween.benchmark --quick --backends crossfade --output outputs/benchmark-quick
.venv/bin/python -m inbetween.benchmark --backends crossfade rife --output outputs/benchmark-full
.venv/bin/python scripts/benchmark_smoke_test.py
./launch.sh
```

The Gradio **Compare baselines** tab accepts two PNGs or a built-in benchmark case and runs both backends at matching timestamps. It offers both animations, frame strips, PNG sequences, GIFs, MP4s, manifests, complete backend generation wall time, inference-loop time, and VRAM. Upload a complete ground-truth PNG sequence, including endpoints, with a shared filename prefix and numeric frame suffix to show metrics for your own sequence. A failed RIFE run is shown as failed. Reports and contact sheets are under the selected ignored `outputs/benchmark*/` directory.

## Milestone 4: artist-guided breakdown experiment

The **Artist-guided breakdown** tab compares endpoint-only RIFE with RIFE split around an uploaded breakdown D. For N intermediate positions, set `k` from 1 to N: A is frame 0, D is frame k, and B is frame N+1. The output has N+2 frames; A, D and B are authoritative and pixel-exact in the PNG sequence. The tab provides paired playback, frame galleries, PNG sequences, GIF and MP4 downloads, manifests, runtime details and exact-frame status. Both methods require the local RIFE assets and CUDA; a failure is shown without substituting crossfade.

The controlled oracle-breakdown diagnostic uses four existing synthetic cases and ground-truth-derived D. It is not an artist study. See [guided protocol](docs/GUIDED_BREAKDOWN_PROTOCOL.md).

Its primary generated-only metrics compare indices 1..N excluding D at k for both methods. Index-k metrics are separate and guided D is labeled authoritative. Guided generation calls the backend twice; endpoint-only calls it once, so wall-clock values are operational diagnostics rather than a fair speed comparison. The guided manifest records N requested positions, N-1 inferred frames, and authoritative indices [0, k, N+1]; segment diagnostics are authoritative for preprocessing and model load.

```bash
.venv/bin/python -m inbetween.guided_benchmark --backend rife --output outputs/guided-breakdown-benchmark-corrected
```

In a normal WSL shell with CUDA and the pinned local RIFE assets, run `.venv/bin/python scripts/guided_rife_smoke_test.py` for a small GPU acceptance check.

## Milestone 5: closed as a negative experimental result

The **Artist-guided breakdown** tab offers **Analyze experimental position risk**,
per-position scores and an **experimental highest-risk position**. Research
diagnostic only: in the initial procedural study this heuristic performed worse
than midpoint and seeded random and should not be treated as a recommendation.
Manually enter k and upload D before guided comparison; analysis never fills k.

The [protocol and verified results](docs/BREAKDOWN_POSITION_PROTOCOL.md) record
24/24 successful RIFE candidates and 0/4 heuristic oracle selections. Four
intended motion sequences contain only two distinct endpoint-input configurations;
three share identical endpoints. This is an initial procedural negative result,
not a population claim. Seeded random means one deterministic baseline, not
random chance generally. Runtime is diagnostic only. No cloud compute was used.

Preserve the original GPU artifacts. A CPU implementation check can use:

```bash
.venv/bin/python -m inbetween.position_study --backend crossfade --output outputs/breakdown-position-study-cpu-closure
```

Flat improvements have explicit gain/reduction field names; absolute frame
metrics remain separate. No heuristic tuning or post-hoc correction was evaluated.

## Milestone 6: preregistered intent guidance with abstention

The separate [Milestone 6 protocol](docs/INTENT_GUIDANCE_PROTOCOL.md) freezes ten
new procedural cases and a small explicit temporal-intent mapping. Abstention
handles ambiguous intent deterministically; it is not calibrated confidence.
Selective answered-subset comparisons and full-suite forced-choice ablation
results are reported separately. The Milestone 5 heuristic and UI are unchanged;
manual k remains authoritative. This is not a final research contribution.

CPU implementation validation (use a fresh output directory):

```bash
.venv/bin/python -m inbetween.intent_study --backend crossfade --output outputs/intent-guidance-cpu-v1
```

Milestone 6 is closed as a **negative/mixed preregistered GPU result** from
`outputs/intent-guidance-rife-v1` (`execution_kind: local_rife_evaluation`).
All 60/60 candidates succeeded, coverage was 6/10, all 10 cases were rankable,
and all authoritative A/D/B checks were exact. All 82 JSON files parsed strictly.

On the six answered cases (lower is better):

| Policy | Mean rank | Mean regret |
|---|---:|---:|
| Intent | 3.4444 | 1.6111 |
| Midpoint | 2.7778 | 0.9444 |
| Frozen heuristic | 4.0556 | 2.2222 |

**Both preregistered descriptive criteria failed.** Intent beat the frozen
heuristic but lost to midpoint, with 1 win, 2 ties and 3 losses against midpoint.
Answered forced-choice regret (1.6111) was not lower than abstained-case
forced-choice regret (1.5417): abstention did not isolate harder forced-choice
cases. These results do not establish calibrated abstention, generalization,
artist usability, or successful intent-based recommendation.

The original GPU output is preserved, including its erroneous “CPU values are
validation only” summary label. The reporting code now labels CPU/injected runs
as validation-only and local RIFE runs as GPU experimental results. No experiment,
metric or frozen protocol was revised; see the [closure record](docs/RESEARCH_LOG.md).
