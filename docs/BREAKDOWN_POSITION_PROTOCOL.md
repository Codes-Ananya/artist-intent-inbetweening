# Breakdown position protocol (Milestone 5, preregistered v1)

This procedural oracle-position study uses only curved_arc, hold_then_fast,
exaggeration and occlusion, N=6, every k=1..6. Endpoint-only generation runs once
per case. Each candidate uses ground-truth frame k as authoritative D and the
existing two-segment backend. A/D/B must be pixel-exact in saved PNGs.

Primary metrics are a matched leave-one-position-out comparison: both methods
use the identical five indices 1..6 excluding k. Report index k separately.
Candidate k values exclude different positions: absolute candidate scores are
paired intervention-benefit estimates, not a perfectly identical common-frame
comparison across all k. Oracle breakdowns estimate an upper bound on ideal
input value; no real-artist usability conclusion is supported.

## Primary criterion, fixed before GPU results

For each candidate compute guided minus endpoint-only Edge F1, endpoint-only
minus guided Chamfer (pixels), and endpoint-only minus guided trajectory error
(pixels). Larger improvement is better for all three. Trajectory uses only
indices measurable in BOTH methods; record those indices. Include trajectory
in ranking only if EVERY candidate measures ALL five paired indices. Otherwise
omit trajectory for ALL candidates, avoiding advantage or penalty for missing
measurements. PSNR and SSIM are secondary descriptive metrics; perfect PSNR
is null with explicit perfect-match counts, never silently dropped from a mean.

Require all six candidates successful, each with five structural measurements.
If coverage is incomplete, oracle ranks and regrets are unavailable (null),
not ranks over the surviving subset. For each included metric, rank descending
improvement: rank = 1 + number strictly greater + (number equal - 1)/2.
The primary value is the unweighted arithmetic mean of these metric ranks
(lower is better). No tuning or metric weighting follows inspection of results.
Oracle best minimizes mean rank; oracle worst maximizes it; both break ties
by smaller k. Policy regret = policy mean rank minus oracle-best mean rank,
in rank units, with null regret when coverage or the selected candidate fails.

## Observable experimental diagnostic and baselines

The recommender accepts ONLY A, endpoint-only generated frames, B. It cannot
see ground truth, D, case names, or candidate evaluation. At each k measure:
mean adjacent binary Canny-edge disagreement; absolute imbalance between the
two adjacent mean absolute grayscale differences; sum of adjacent dark-pixel
area-fraction changes (gray <80); and centroid second-difference magnitude
when all three neighboring dark-pixel centroids exist. Gray/Canny use the
existing metric definitions. Normalize each component across positions by
min-max; constant signals become zero, missing signals remain null. Use only
components measurable at every position in the final unweighted mean, and
record raw, normalized, missing and active components. Highest score wins,
smaller k breaks ties. If no components exist, no recommendation is returned.
This is an experimental heuristic, not yet a learned contribution.

Fixed midpoint is floor((N+1)/2), the earlier central slot for even N (3 at N=6).
Random uses a fresh Python random.Random(20260921).randint(1,N) for each case;
it is independent of case identity, order, ground truth and oracle D. The same
seed deliberately selects the same slot across cases. Neither policy sees truth.

## Execution and interpretation

```bash
.venv/bin/python -m inbetween.position_study --backend rife --output outputs/breakdown-position-study-new-run
.venv/bin/python -m inbetween.position_study --backend crossfade --output outputs/breakdown-position-study-cpu
```

CPU runs validate implementation only. No cloud compute is used. Endpoint
wall time and candidate guided wall time are separate diagnostics, never the
primary result. Manifests retain backend provenance, hashes, segment diagnostics
and exact-pixel checks. Failures remain in reports and do not abort later
candidates/cases. Reports in a reused output directory are replaced; use a
fresh directory for independent runs. Milestone 4 v1 aggregates remain excluded.

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
