# Milestone 6 preregistration v1: Intent-Aware Breakdown Guidance with Abstention

Implementation and CPU validation only at preregistration. No held-out RIFE outputs
have been inspected. This is a procedural ideal-breakdown diagnostic, not an
artist study, calibrated confidence system, prediction of RIFE failure, or final
research contribution. The simple temporal mapping tests explicit timing input.

## Frozen scope and inputs

Base: main and peeled milestone-5-position-study tag both resolve to
1e2f25e849aecf8d8349353f4f765dfd98b4646e. The Milestone 5 heuristic, ranking,
metrics, cases and UI remain unchanged. Only curved_arc, hold_then_fast,
exaggeration and occlusion may inform development choices. Their known GPU
results motivated the question; they are not Milestone 6 evaluation cases.

N=6, eight frames sampled at t=i/7, i=0..7. Candidate time is t=k/(N+1).
Early: t < 1/3; middle: 1/3 <= t <= 2/3; late: t > 2/3.
Fixed representatives: early -> k=2, middle -> k=3, late -> k=5.
Do not snap geometric event times to these representative slots.

Intent is a list of one or two equally important records with exactly two keys:
`event` in {path_turn, timing_change, pose_extremum, visibility_change};
`phase` in {early, middle, late, unspecified}. Events describe salient motion,
not the oracle-optimal breakdown. Event types define annotation semantics; the
minimal policy uses phase only. These records are authored from equations before
rendering or inspecting predictions. No free-text inference or case-name rules.

Each known phase admits its representative. Unspecified admits {2,3,5}.
Union admitted positions across events: one position answers; more than one
abstains. Reasons are unspecified_phase or conflicting_event_phases (unspecified
takes precedence). Missing/empty intent abstains as missing_intent; malformed,
unsupported or >2 events abstain as unsupported_intent. No endpoint images,
ground truth, D, scores, case identifiers or learned thresholds enter this policy.
This is deterministic ambiguity handling. Manual k remains authoritative.

The separately labelled forced_choice_intent_ablation chooses the smallest
admitted position; missing/invalid intent uses k=3. It is never substituted for
abstention. Abstention has null k, rank and regret.

## Ten held-out constructions, fixed before GPU evaluation

Every case is deterministic: seed=null, no randomness. RGB white canvas 256x256,
3x supersampling, LANCZOS downsampling, ink=(20,25,35), nominal stroke=4 px.
Coordinates below are in final-resolution pixels. `P(c,w)=max(0,1-|t-c|/w)`;
angles use radians. Rendering primitives round scaled coordinates to integers.
Polygons have white fill and closed ink outlines; ellipses have ink outlines,
transparent interiors unless explicitly white-filled. Full primitive definitions
in intent_cases.py are normative and source-hashed before inference. No case is
a transformed/reskinned Milestone 5 stick figure.

| Case | Frozen motion and geometry | Intent | Pre-registered method outputs |
| --- | --- | --- | --- |
| hinged_gate | a=.15+1.15 min(t/.24,1)-.12 max(0,(t-.24)/.76); x=55+130 cos(a), y=90+45 sin(a). Panel vertices (55,65),(x,y-25),(x,y+85),(55,175); post (48,45)-(48,210). | timing_change early | k=2 |
| obstacle_reach | Tip (95+115t,125-62P(.26,.26)); elbow (65+55t,162-40 sin(pi t)), anchor (35,205), elbow radius 7; obstacle rectangle (130,145)-(160,210). | path_turn early | k=2 |
| landing_ball | p=P(.46,.22); center (55+140t,70+105p+28t); radii (15+10p,18-9p); floor (25,198)-(230,198). | pose_extremum middle | k=3 |
| folding_panel | q=P(.56,.44), x=145-55q+18t,y=72+85q. Fixed panel (45,60),(110,65),(110,190),(45,180); moving panel (110,65),(x,y),(x+15,y+85),(110,190). | pose_extremum middle | k=3 |
| pendulum | a=-.8+1.7 min(t/.77,1)-.7 max(0,(t-.77)/.23); center (128+105 sin(a),40+105 cos(a)); radius 18; pivot (128,40), support (95,35)-(160,35). | path_turn late | k=5 |
| screen_cart | x=35+185t; body (x-23,145)-(x+23,178); wheels (x+-14,184), radius 8; foreground screen (65,60),(166,90),(166,210),(65,210). Salient event is full emergence, not first appearance. | visibility_change late | k=5 |
| depth_exchange | Disk center (55+140t,115+12t), radius 25, white fill; square x=200-130t, rectangle (x-24,105)-(x+24,153). Square foreground before .52, disk afterward. | visibility_change unspecified | abstain |
| waving_hand | a=-.6+sin(2pi t)+.3t; wrist (125+55 sin(a),140-55 cos(a)); chain (80,215)-(125,140)-wrist; hand radii (13,17); three fingers from (x+o,y-10) to (x+o+4,y-32), o=-10,0,10. | pose_extremum unspecified | abstain |
| s_ribbon | Center (35+185t,125+50 sin(2pi t)); open chevron offsets (-22,-12),(0,0),(-22,12), with tail (-22,-12),(-32,-8),(-22,12). Two equally important turns. | path_turn early + path_turn late | abstain |
| bounce_barrier | p=P(.23,.23), center (35+190t,90+90p+35t), radii (12+7p,16-7p); floor (20,215)-(235,215); foreground barrier (181,65)-(240,210). | pose_extremum early + visibility_change late | abstain |

Landmarks: moving tip/center/wrist for every case except gate ((55+x)/2,
(150+y)/2) and panel (110,y+45). These are centroid-proxy diagnostics, not
physical tracking guarantees; static geometry and occlusion bias them. Retain
Milestone 5 trajectory-coverage rules without repairing this known limitation.

Reject any individual A or B pixel hash collision with another held-out endpoint
or any of the four development cases. Hash mode, dimensions and pixel bytes.
Distinct hashes alone do not establish distinct geometry: the above independent
object constructions are the geometric audit. Do not add decorative marks merely
to pass hashes. Do not remove cases or change equations after RIFE inspection.
Coverage is constructed as 6/10, not an estimate of real artist coverage.

## Evaluation, ranking and reports

Use existing local pinned float32 RIFE through InterpolationBackend; no cloud,
training, downloads, new pretrained models or new dependencies. RTX 4050 only for
RIFE evaluation. One endpoint-only generation per case; six independent candidates
k=1..6, each with exactly one ground-truth D. A/D/B in saved PNGs must be exact;
D occurs once. Exhaustive evaluation is not extra policy input or artist budget.
Backend failures surface without crossfade fallback. CPU crossfade/fake runs
validate implementation only, never RIFE effectiveness.

Reuse rank_candidates from the frozen Milestone 5 position_study.py. Both methods
exclude k, evaluating the same five generated positions for each candidate.
Larger Edge F1 gain and Chamfer reduction are better. Include trajectory reduction
only if all six candidates have all five paired measurable indices; otherwise omit
it for all candidates. Descending midranks, unweighted mean rank, smaller-k oracle
tie break. Regret = chosen mean rank - oracle-best mean rank. Missing any candidate
invalidates all oracle ranks/regrets for that case. PSNR/SSIM are secondary;
perfect PSNR is null with explicit flags/counts, never silently dropped.
Different candidates exclude different indices; these remain intervention-benefit
estimates, not an identical-common-frame absolute-quality comparison.

Policies: intent, midpoint=3, frozen heuristic, oracle best, separately labelled
forced-choice intent ablation. Frozen heuristic sees only endpoint-only images,
and runs before any oracle candidate. Intent decisions also precede candidates.

Report strict JSON (no NaN/Infinity), CSV and Markdown containing:
- Each decision, admitted positions, abstention reason and intent record.
- Coverage answered/all attempted; evaluation completeness rankable answered/
  answered; rankable total/all attempted. Failures remain in denominators.
- Selective answered-subset aggregates for all five policies on their shared
  evaluable case intersection, with explicit requested/evaluated counts and IDs.
- Full-suite aggregates for midpoint, frozen heuristic, oracle and forced-choice
  ablation on their shared evaluable intersection. No full-suite intent mean.
- Per-case k, rank, regret, raw gains, candidate failures and exact-pixel checks;
  per-frame metrics and authoritative-k metrics separately in JSON.
- Paired win/tie/loss and mean regret differences against both baselines for
  selective intent and full-suite forced-choice, always on identical subsets.
- Forced-choice quality on answered and abstained strata separately. This is a
  descriptive stratification of different cases, not a paired causal comparison.
- Source/protocol hashes, all truth-frame hashes, manifests/model provenance,
  runtime and VRAM diagnostics. Write preregistration.json before inference.

Fresh output directories only. No result-dependent retries or case replacement.
An infrastructure correction requires a documented deviation and fresh full run;
retain the failed report. No GPU-quality conclusions from incomplete evaluation.

## Frozen success criteria and limitations

Placement supported descriptively only if answered-subset mean regret is strictly
lower than BOTH midpoint and frozen heuristic. Selective-quality criterion:
forced-choice mean regret strictly lower on answered than abstained cases.
Ties do not satisfy either criterion. Criteria are unavailable when the shared
full-suite evaluation is incomplete, answered set is empty, or required strata
are empty. Complete reporting and invariants, not positive quality, determine
implementation acceptance. Null abstention regret never becomes zero.

Ten cases do not support population significance, calibrated selective risk,
artist preference, usability or generalization claims. Timing labels explicitly
supply useful information; this is elicitation, not inferred intent. The same
researcher authors generators and labels, and missing annotations construct
abstention coverage. Oracle D is an ideal intervention. Benchmark construction,
renderer familiarity, correlated edge metrics, centroid bias and candidate-specific
exclusions constrain interpretation. CPU rendering may catch implementation
errors but must not be used to optimize held-out quality. Any later mapping,
threshold, vocabulary or equation tuning requires a new holdout.

## Commands (separate CPU validation and normal-WSL GPU evaluation)

CPU validation:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m inbetween.sample
.venv/bin/python -m inbetween.intent_study --backend crossfade --output outputs/intent-guidance-cpu-v1
```

Only in normal WSL with RTX 4050 CUDA available and existing pinned assets:

```bash
.venv/bin/python -m inbetween.intent_study --backend rife --output outputs/intent-guidance-rife-v1
```

No GPU run is part of the preregistered implementation commit. UI unchanged;
manual k stays authoritative. Preserve existing Milestone 1-5 behavior and tests.
