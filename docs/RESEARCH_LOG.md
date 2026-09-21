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

## 2026-09-21: Milestone 5 initial implementation (historical)

Initial checks confirmed a clean `feature/breakdown-position-study` branch and
`main` exactly at tagged `milestone-4-guided-breakdown`, commit
`3f5ed1604567325bd648f8add39fdb806d19ca34`. No merge or tag was performed.

Pre-registered `BREAKDOWN_POSITION_PROTOCOL.md` before examining any Milestone 5
GPU results. The primary criterion is mean descending rank of matched Edge F1
gain and Chamfer reduction, with trajectory reduction included only when all
six candidates have complete paired coverage. Lower mean rank is better;
rank ties use smaller k. Regret is the difference from oracle-best mean rank.
Incomplete candidate coverage produces no oracle ranking or regret.

The study generates endpoint-only once per case and evaluates all k=1..6 for
the four existing cases. Primary aggregates exclude the same k in both methods;
k metrics are separate. These matched leave-one-position-out estimates exclude
different frames across candidates. The transparent experimental recommender
sees only endpoint-only images, never ground truth, D or case identity. The UI
adopts or overrides its suggestion within the existing one-breakdown workflow.

Final local validation: `pip check`, offline application-lock dry run and
installed GPU requirement consistency passed (torch 2.14.0+cu126, torchvision
0.29.0+cu126). Compilation passed. Complete pytest: **55 passed, 1 skipped**
(existing CUDA-dependent mocked OOM test); Milestone 1–4 test files are unchanged.
A new test guard prohibits real RIFE model imports; fake backends validate all
positions, pairing, exact pixels, deterministic/missing-risk behavior, ranks,
regret, failure isolation, UI success/error and module CLI imports without
PYTHONPATH. CPU crossfade study completed **24/24 candidates**, with exact A/D/B,
under ignored `outputs/breakdown-position-study-cpu-v2/`. Fake-backend studies
also completed in pytest temporary directories. Strict JSON validation covers
all study JSON files. The sample exported run `20260921T161243-990d1f8b` and
quick crossfade benchmark (`outputs/benchmark-m5-quick/`) passed. Gradio returned
HTTP 200 on loopback port 7861. Diff whitespace and output/asset/venv ignore
checks passed. No outputs, pinned RIFE assets or dependencies were modified
for inclusion in Git.

At initial implementation CUDA was unavailable in the sandbox. The subsequent
normal-WSL results below supersede that pending status.

This remains a procedural oracle-position study: oracle breakdowns estimate
an upper bound; no real-artist usability conclusion is supported. The heuristic
is experimental, not yet a learned contribution. Runtime remains diagnostic.
No cloud compute was used. Superseded Milestone 4 v1 aggregates remain excluded.

## Milestone 5 closure: initial procedural negative result

Independent review findings and the saved normal-WSL GPU report verify that
24/24 RIFE candidates completed. All authoritative A/D/B checks passed.
Strict JSON passed. The heuristic selected k=1 for every case; heuristic oracle
selections: 0/4. Lower mean rank and regret are better.

| Policy | Mean rank | Mean regret |
| --- | --- | --- |
| heuristic | 5.67 | 4.50 |
| midpoint | 2.25 | 1.08 |
| seeded random | 4.33 | 3.17 |
| oracle best | 1.17 | 0.00 |

| Intended motion sequence | Heuristic k | Oracle k | Heuristic outcome |
| --- | --- | --- | --- |
| curved_arc | 1 | 3 | tied oracle-worst |
| hold_then_fast | 1 | 4 | tied oracle-worst |
| exaggeration | 1 | 4 | ranked 5/6 |
| occlusion | 1 | 5 | tied oracle-worst |

This is an initial procedural negative result, not a statistical population
claim. “Worse than seeded random” refers to this one deterministic seeded-random
baseline, not proof of being worse than random chance generally. Runtime is
diagnostic only. No cloud compute was used.

### Identifiability and boundary artifact

curved_arc, hold_then_fast and exaggeration have byte-identical A/B endpoint
frames. An endpoint-only deterministic recommender must therefore produce the
same output for all three, despite different intended intermediate motions and
oracle positions. There are two distinct endpoint-input configurations and
four intended motion sequences, not four independent endpoint-input trials.
Three sequences form an intentional/accidental same-endpoint ambiguity group.
This demonstrates underdetermination by construction for that ambiguity group;
occlusion supplies one additional distinct negative case.

The observed k=1 scores received large endpoint-adjacent temporal-difference
and centroid/area signals. Min-max normalization amplified these boundary
outliers. k=N was handled symmetrically in code but showed a smaller empirical
spike. This is a limitation of heuristic v1; no post-hoc correction is evaluated
in this milestone.

### Closure and reporting corrections

Milestone 5 is closed as a negative result. The normal UI exposes research
scores and an “experimental highest-risk position”, requires manual k entry,
and never adopts the diagnostic position. Manual k remains authoritative for
the existing guided workflow. The v1 diagnostic implementation is retained for
reproducibility without redesign or tuning. Existing procedural cases remain
unchanged: changing them after seeing results would invalidate the pre-registered
run. Any redesigned heuristic must be evaluated later on newly created held-out
cases with distinct endpoints.

Flat CSV/report and policy-table improvement fields are `psnr_db_gain`,
`ssim_gain`, `edge_f1_gain`, `chamfer_px_reduction`, and
`trajectory_error_px_reduction`; larger is better. Absolute per-frame,
aggregate-means and breakdown-index metrics keep their existing names. Nested
`improvement` and `metric_ranks` retain v1 keys with their explicit context.
Perfect PSNR remains null with perfect-match flags/counts; strict JSON forbids
NaN/Infinity. Historical artifacts in `outputs/breakdown-position-study` retain
the original schema and are preserved unchanged. No new GPU effectiveness
study was run for this correction; CPU runs validate implementation only.

Closure validation (local existing `.venv`): Python compilation passed; complete
pytest **61 passed, 1 skipped** (existing CUDA-dependent mocked OOM test).
Tests inspect Gradio event wiring to prove no callback writes manual k, verify
manual k reaches guided generation, distinguish flat gains from absolute metrics,
check the documented results and same-endpoint deterministic diagnostics, and
prove the real inference adapter is blocked by the pytest model-import guard.
The CPU crossfade study completed **24/24** candidates with exact A/D/B checks
in `outputs/breakdown-position-study-cpu-closure`. Strict JSON validation passed
for all 33 original GPU JSON files, 33 CPU JSON files and 5 quick-regression JSON
files. SHA-256 comparison confirmed all **444** original GPU artifact files
unchanged. Sample export `20260921T163512-69ec4bfa`, the existing quick crossfade
benchmark, `pip check`, and offline lock-file dry run passed. Gradio returned
HTTP 200 on loopback port 7861 (startup required execution outside the sandbox).
`git diff --check` and output/weights/credentials/venv ignore checks passed.
Milestone 1–4 tests, procedural cases, diagnostic v1 and ranking are unchanged.
No new models, dependencies, datasets, GPU study, merge or tag were introduced.

## 2026-09-21: Milestone 6 preregistered implementation and CPU validation

Before changes, main was clean and HEAD/main resolved to
`1e2f25e849aecf8d8349353f4f765dfd98b4646e`. The annotated
`milestone-5-position-study` tag peeled to the same commit. Created
`feature/intent-guidance-abstention`; no merge or tag is part of this milestone.

Preregistered `INTENT_GUIDANCE_PROTOCOL.md` freezes normalized time, temporal
bins, representatives, vocabulary, deterministic ambiguity handling, forced-choice
ablation, ten new procedural constructions/equations, null seeds, intent records,
ranking and descriptive success criteria before any Milestone 6 GPU evaluation.
A CPU ground-truth preview caught a folding-panel edge extending outside the
canvas; its extent was corrected before the final CPU validation and freeze.
No held-out RIFE output was inspected or used to tune these constructions.

The separate runner records source/truth hashes and decisions before inference,
rejects endpoint hash collisions, generates endpoint-only once per case and
independently evaluates k=1..6 with one ideal D. It reuses the frozen Milestone 5
ranking. Selective answered-subset and full-suite policy comparisons use explicit
shared case intersections. Abstention remains null, never zero regret or a silent
midpoint fallback. Coverage is designed at 6/10, not estimated artist coverage.
The simple mapping is not claimed as the final research contribution. UI and
manual k authority are unchanged.

Validation in the existing local `.venv`: **71 passed, 1 skipped** (existing
CUDA-dependent mocked OOM test); normal pytest retains the real-model import
guard. Compilation and `pip check` passed. The CPU crossfade study at ignored
`outputs/intent-guidance-cpu-v1` completed **60/60 candidates** with exact saved
A/D/B. All **82 JSON files** passed strict nonfinite rejection; CSV and Markdown
reports include coverage, completeness, reasons, candidate outcomes, explicit
subset IDs, baseline comparisons and forced-choice analysis. Source hashes in
the run match the preregistered implementation. Four frozen Milestone 5 source
hashes were checked against the required base commit (heuristic, study/ranking,
procedural cases and metrics). Sample export `20260921T170954-c6e7bb2e` passed.
Diff whitespace and output/weights/virtual-environment ignore checks passed.

These CPU results validate implementation only. No Milestone 6 GPU inference,
RIFE effectiveness measurement, model download, cloud service, new dependency,
or artist study was performed. The separate normal-WSL RTX 4050 command is in
`INTENT_GUIDANCE_PROTOCOL.md`; that evaluation remains pending.


## 2026-09-21: Milestone 6 GPU closure — negative/mixed preregistered result

Closure began on clean `feature/intent-guidance-abstention` at
`bb12375871bde179d2147b61e35a7d5dee9569c9`. Read-only verification of completed
`outputs/intent-guidance-rife-v1` confirmed `execution_kind: local_rife_evaluation`,
60/60 successful candidates, coverage 6/10, all 10 cases rankable, and exact
recorded authoritative endpoint A/B and candidate A/D/B checks. All 82 JSON files
passed strict parsing with nonfinite constants rejected. All 939 output files
were hashed before closure edits for an unchanged-output check.

Both preregistered descriptive criteria failed. On the six answered cases,
intent mean rank/regret was **3.4444/1.6111**, midpoint **2.7778/0.9444**, and the
frozen heuristic **4.0556/2.2222**. Intent beat the frozen heuristic but lost to
midpoint, recording **1 win, 2 ties and 3 losses** against midpoint. Answered
forced-choice regret **1.6111** was not lower than abstained-case forced-choice
regret **1.5417**. Abstention therefore did not isolate harder forced-choice
cases. This is a negative/mixed preregistered result, with no claim of calibrated
abstention, generalization, artist usability or successful intent-based
recommendation. Coverage is still designed coverage on procedural cases.

The saved GPU summary incorrectly says “CPU values are validation only”. That
historical artifact is preserved. A reporting-only correction now labels local
RIFE runs as GPU experimental results and CPU/injected runs as validation-only,
using execution provenance rather than the requested backend name. Regression
coverage uses synthetic criterion values and injected crossfade data only.
`INTENT_GUIDANCE_PROTOCOL.md` remains byte-for-byte frozen, as do cases, intent
mappings, abstention rules, candidate data and metrics. No GPU inference or
metric recalculation was performed during closure.

Closure validation in the existing `.venv`: **75 passed, 1 skipped** (existing
CUDA-dependent mocked OOM test); the real-model import guard remained active.
`pip check`, compilation of `inbetween`, `tests` and `scripts`, and
`git diff --check` passed. CPU sample export `20260921T172838-86518899` completed.
Read-only pixel verification independently confirmed all 200 saved authoritative
frame comparisons against saved ground truth; all 70 run manifests record
`cuda:0`. Preregistered source hashes matched the original HEAD above. All 939
GPU output files remained byte-for-byte unchanged. No merge or tag is part of
this closure.
