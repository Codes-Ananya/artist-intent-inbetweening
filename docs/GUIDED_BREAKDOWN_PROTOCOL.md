# Guided breakdown protocol

This is a local controlled **oracle-breakdown diagnostic**, not an artist study. For each of `curved_arc`, `hold_then_fast`, `exaggeration`, and `occlusion`, the breakdown D is copied from the known ground-truth sequence at index `k = (N+1)//2` by default. Its position can be set with `--position`. Both endpoint-only RIFE and guided RIFE produce `N+2` frames. Primary generated-only means compare the identical indices `1..N` excluding `k` for both methods. Index `k` metrics are reported separately; guided D is an authoritative oracle frame, not generated output. The report includes operational timing and peak CUDA memory diagnostics when available. A failed case or method is recorded and later cases continue.

For `N` intermediate timeline positions, choose integer `k` in `1..N`. A is index 0, D is index `k`, and B is index `N+1`. Generate `k-1` frames between A and D and `N-k` between D and B, then concatenate with D once. The guided manifest records `requested_intermediate_count=N`, `inferred_frame_count=N-1`, and `authoritative_frame_indices=[0,k,N+1]`. A, D and B source pixels are copied into the output and checked against saved PNGs. GIF and MP4 are playback formats and may change pixels. The manifest records source hashes, backend provenance, segment counts and diagnostics. `guided_breakdown.segments` is authoritative for segment-specific preprocessing, timing and model-load fields; top-level preprocessing and model-load fields are null for guided runs. Guided generation invokes the backend twice, while endpoint-only invokes it once. Backend wall times can include different model-loading behavior and are operational diagnostics, not a fair speed comparison. Errors never trigger crossfade substitution.

Run from the repository root:

```bash
.venv/bin/python -m inbetween.guided_benchmark --backend rife --output outputs/guided-breakdown-benchmark-corrected
```

For a CPU implementation check, use `--backend crossfade --count 2`; this does not estimate RIFE quality. Outputs are ignored by Git. The procedure uses only local files, the pinned local RIFE assets, and local CUDA; no cloud service is used.

The separate normal-WSL GPU smoke command is `.venv/bin/python scripts/guided_rife_smoke_test.py`. It tests both RIFE methods on a two-intermediate curved-arc case and exits nonzero on failure.

Splitting interpolation around a supplied drawing is not claimed as a novel algorithm. The research question is how much an intervention helps, where it helps most, and eventually when and where artist input is most useful. A ground-truth-derived D estimates the value of an ideal intervention. Artist-created breakdowns and artist judgments are needed before making claims about actual artist workflows.
