# Architecture

`core.py` owns image validation and the `InterpolationBackend` interface. `CrossfadeBackend` is the Milestone 1 implementation; a later RIFE adapter can implement the same `generate(first, last, intermediate_count)` method. `run.py` orchestrates frame generation, exports, structured events, and manifests. `diagnostics.py` collects local CUDA/system facts. `app.py` is only the Gradio presentation layer. `sample.py` builds synthetic fixtures.

Frames are retained as PIL RGB/RGBA images. Source endpoint pixel arrays are copied into positions 0 and N+1. PNG sequence export is the pixel-exact artifact. GIF palette conversion and MP4 YUV encoding are lossy or color-limited and may discard alpha. FFmpeg exports MP4 from the saved PNG sequence.

## Milestone 2 RIFE adapter

`inbetween/rife.py` implements `InterpolationBackend` and loads the pinned official source and checkpoint from ignored `.local/rife/`. It sends equally spaced arbitrary timestamps directly to RIFE_m. The uploaded endpoints are copied into the returned sequence; only intermediate frames are model-generated. The adapter checks source commit and checkpoint hash, requires CUDA, uses `torch.inference_mode()` and float32, and reports memory and inference time. It does not call the crossfade backend on error. The run orchestrator merges backend metadata into each manifest. Setup and normal-shell GPU smoke scripts live in `scripts/`.

## Milestone 3 benchmark

`benchmark_cases.py` draws complete deterministic RGB character sequences. `benchmark_metrics.py` computes fixed grayscale and edge metrics. `benchmark.py` calls the unchanged backends through `create_run`, checks endpoints, isolates failures, and writes CSV, JSON, summary, contact sheets and GIFs. `comparison.py` runs independent backend manifests for the Gradio comparison tab. Generated assets live under ignored `outputs/`.

## Milestone 4 guided orchestration

`guided.py` wraps any `InterpolationBackend` with two segment calls. It copies A, D and B into indices 0, k and N+1 and checks their pixels. `create_guided_run` reuses `create_run` exports and adds breakdown source hash, segment diagnostics, authoritative indices and saved-PNG checks to the manifest. `guided_benchmark.py` evaluates four oracle-breakdown cases independently, recording failures without fallback. The existing endpoint-only path remains unchanged.

## Milestone 5 position study

`position_recommendation.py` accepts only endpoint-only image sequences. Its
observable component extraction, safe normalization and deterministic selection
are separate from procedural assets and oracle evaluation. `position_study.py`
generates each endpoint sequence once, runs six existing guided orchestrations,
computes paired generated-only gains and complete-coverage oracle ranks, and
writes strict JSON, CSV, tables and existing-format visuals. Per-candidate errors
are isolated; incomplete cases have no oracle rank or regret. The app's small
recommendation section uses uploaded A/B only and feeds an editable k into the
Milestone 4 workflow. Backend errors propagate without fallback. Tests prohibit
real RIFE model imports while retaining explicitly mocked backend tests.
