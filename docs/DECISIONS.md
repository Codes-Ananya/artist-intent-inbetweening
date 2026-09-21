# Decisions

1. PNG is the accepted input to make channel and alpha validation explicit and keep endpoints pixel-exact.
2. Integer channel crossfade is a deterministic placeholder. It does not estimate motion or preserve line structure.
3. PNG sequence is authoritative for endpoint fidelity. GIF and MP4 are viewing formats with color/alpha limitations.
4. The app listens on loopback only and stores local run folders under ignored `outputs/`.
5. The backend interface permits a future RIFE implementation without changing run orchestration or UI.

6. Uploaded file paths are trusted only under the loopback-only Gradio deployment assumption. The API also accepts programmatic sample paths and valid Gradio temporary paths. Do not expose this app as a public service without revisiting path trust.
7. RIFE_m from the official MIT-licensed ECCV2022-RIFE source is the local AI comparison baseline. Source and checkpoint are pinned and downloaded under `.local/rife/`, not committed.
8. Arbitrary requested counts map directly to timestamps `i/(N+1)`; no recursive bisection or frame duplication is needed.
9. RIFE inference uses float32 and CUDA. FP16 is postponed pending normal-shell stability testing. A 512×512 working area budget limits memory; preprocessing is recorded in manifests.
10. RIFE sees RGB composited over white for RGBA uploads. Alpha is interpolated linearly and original endpoints remain untouched.

## Milestone 3 decisions

- Use 256×256 deterministic RGB procedural line art to bound local CPU/GPU cost; no external dataset or new model.
- Retain RIFE and crossfade implementations unchanged. Reuse run manifests for model identity, runtime, and peak VRAM.
- Use OpenCV's precise Euclidean distance transform and fixed Canny thresholds for reproducible contour diagnostics.
- Report trajectory through an annotated body-center versus output dark-pixel centroid proxy; it can be biased by pose and occlusion.
- Keep benchmark outputs under ignored `outputs/`; do not rank user uploads without complete ground truth.

## Milestone 4 decisions

- Treat the supplied breakdown D as an authoritative drawing at index k, alongside A and B. The guided output has N+2 frames and one copy of D.
- Orchestrate two calls through `InterpolationBackend`; keep RIFE internals and endpoint-only behavior unchanged. Never fall back to crossfade after failure.
- Use ground-truth-derived D for a controlled oracle diagnostic, not as evidence from artists. Splitting around D is not a novel algorithm claim; measuring intervention benefit and placement is the research goal.
- Keep all execution and assets local, without cloud services or training.

## Milestone 5 decisions

- Pre-register the primary mean-rank calculation in `BREAKDOWN_POSITION_PROTOCOL.md`
  before any Milestone 5 GPU results. Rank Edge F1 gain and Chamfer reduction;
  include trajectory reduction only with complete paired coverage in all six
  candidates. PSNR/SSIM are secondary. Incomplete candidates invalidate oracle
  ranks and regrets for that case.
- Use matched leave-one-position-out intervention-benefit estimates, acknowledging
  that candidates omit different frames. Preserve the authoritative A/D/B path.
- Keep the experimental ground-truth-free heuristic separate from procedural
  evaluation; use transparent equal normalized component contributions, no tuning,
  case-specific rule, training, cloud service, model download or new dependency.
- Midpoint is earlier middle slot k=3; seeded random is case/order independent.
  Oracle best/worst and rank-unit regret are descriptive procedural diagnostics.
- Oracle drawings estimate an upper bound, not real-artist usability. Superseded
  Milestone 4 v1 aggregates remain excluded. No cloud compute was used.

Milestone 5 is closed as an initial procedural negative result; see
[verified results and limitations](BREAKDOWN_POSITION_PROTOCOL.md#milestone-5-closure-initial-procedural-negative-result).
Flat improvements use `psnr_db_gain`, `ssim_gain`, `edge_f1_gain`,
`chamfer_px_reduction`, and `trajectory_error_px_reduction`; absolute metrics
retain their names. The UI requires manual k and cannot adopt the diagnostic.

## Milestone 6 preregistration

- Preserve Milestone 5's negative baseline byte-for-byte; use its corrected
  generated-only ranking and paired trajectory coverage unchanged.
- Freeze ten new object/motion constructions and explicit intent records in
  [INTENT_GUIDANCE_PROTOCOL.md](INTENT_GUIDANCE_PROTOCOL.md) before GPU evaluation.
- Use normalized candidate time k/(N+1), fixed early/middle/late phase boundaries,
  representatives 2/3/5 at N=6, and deterministic ambiguity abstention.
- Abstention is not calibrated confidence, predicted RIFE failure or midpoint
  fallback. Forced-choice intent is a separate ablation. Compare policies on
  identical evaluable cases within each explicitly labelled subset.
- Keep the UI unchanged and manual k authoritative. Use a separate local study
  runner, no training/new model/dependency, and CPU-safe tests. Source hashes and
  intent decisions are saved before inference; reject endpoint collisions.
- Simple mapping is an elicitation diagnostic, not the final research contribution.
