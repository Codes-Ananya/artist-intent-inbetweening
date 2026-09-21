# Milestone 1 acceptance criteria

- [x] Two matching PNG keyframes upload and validate type, size, mode, and alpha presence.
- [x] 0–120 deterministic intermediate frames; first/last PNG pixels equal source pixels.
- [x] Ordered timeline, selected frame, and GIF playback in Gradio.
- [x] PNG sequence, GIF, MP4, manifest, and JSONL events in a unique run folder.
- [x] Local CUDA/system diagnostics available in UI and manifest.
- [x] Tests cover validation, count/order, determinism, endpoint pixels, manifest, and exports.
- [x] Synthetic sample run and startup smoke check executed.

## Milestone 2 branch criteria

- [x] Official MIT source, exact commit, author checkpoint revision, size, and hashes documented.
- [x] Rerunnable checksum-verified local setup; source and weights ignored by Git.
- [x] RIFE backend selection with no silent fallback; arbitrary count maps to ordered timestamps.
- [x] Endpoint pixels, backend metadata, preprocessing, timing, and peak memory paths covered by tests.
- [x] Crossfade integration tests continue to pass; UI startup and crossfade sample checked.
- [x] Normal-shell CUDA smoke test on RTX 4050 6GB: CUDA available true, official RIFE source at commit `5d8adbdd40e12c2c8f91930eff838aebe561c086`, checkpoint SHA-256 `9f9e2e8b5c3fef311c9a782aa17a30f87c388ce6dc9c00e4993eba3d3941d3cb`, four total frames with two generated intermediates, inference time 0.528s, peak CUDA memory 66.1 MiB, endpoints pixel-exact, Gradio UI generation successful, no cloud compute used. These measurements apply only to the synthetic smoke-test images and are not general performance claims.

## Milestone 3

- Ten deterministic procedural stress cases at 256×256 with complete ground truth and metadata.
- Equal endpoint/timestamp inputs for crossfade and RIFE; no fallback on RIFE failure.
- Intermediate PSNR, SSIM, edge F1, symmetric Chamfer, trajectory diagnostic and endpoint equality, defined in `METRICS.md`.
- Per-frame CSV, JSON, Markdown summary, contact sheets and comparison GIFs; generated files ignored.
- Gradio comparison with independent exports and metrics only when complete ground truth is present.
- Run pip check, compileall, pytest, crossfade benchmark, conditional CUDA RIFE benchmark, HTTP startup, diff and ignore checks.

## Milestone 4

- Guided timeline: N+2 frames, D at k, segment counts k-1 and N-k, exact authoritative A/D/B PNG pixels.
- Paired Gradio endpoint-only and guided RIFE exports and manifest diagnostics; failures surface without fallback.
- Four controlled oracle-breakdown categories with identical frame counts, metric coverage, strict JSON and isolated failures.
- Primary generated-only paired metrics exclude k for both methods; index-k oracle metrics, perfect PSNR, evaluated counts, and runtime limitations are explicit.
- Normal pytest never launches real RIFE inference or writes persistent smoke outputs when CUDA is available.
- CPU fake-backend tests and normal-WSL CUDA smoke command. Generated assets remain ignored.

## Milestone 5

- Four existing cases, N=6, all positions; one endpoint generation per case.
- Matched exclusion of k, separate authoritative-k metrics, exact A/D/B PNGs.
- Observable-only deterministic risk components, constant/missing handling,
  midpoint/random/oracle policies and preregistered ranks/regret.
- Strict reports, per-case value/risk tables, previews, provenance and isolated failures.
- UI research diagnostic with manual k required; no adoption action or fallback.
- CPU fake-backend tests, unchanged Milestone 1–4 tests, local regressions and HTTP check.
- Closed negative normal-WSL result: 24/24 candidates, 0/4 heuristic oracle selections; CPU validation is not GPU quality evidence.

## Milestone 6 preregistered implementation

- [x] Clean main, HEAD and peeled Milestone 5 tag verified at required base commit;
  work isolated on feature/intent-guidance-abstention.
- [x] Ten distinct held-out constructions, equations/geometry/intent records and
  null seeds documented before GPU evaluation; endpoint hash collisions rejected.
- [x] Fixed N=6 phase mapping and deterministic ambiguity abstention; separately
  labelled forced-choice ablation; no silent midpoint substitution.
- [x] One endpoint run and six independent one-breakdown candidates per case;
  exact saved A/D/B and corrected frozen Milestone 5 rank/regret protocol.
- [x] Strict JSON/CSV/Markdown with explicit subset IDs, shared policy comparison
  subsets, coverage, completeness, reasons, per-case metrics and failure records.
- [x] CPU-safe fake-backend tests; existing real-model import guard retained;
  Milestone 1-5 behavior and manual UI authority unchanged.
- [ ] Separate normal-WSL RTX 4050 study. No Milestone 6 GPU result claimed.
