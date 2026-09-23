# Milestone 7: Real-Input Artist-Controlled Pilot

Status: protocol and dataset infrastructure only, 2026-09-22. No pilot assets,
model execution, pilot metrics or results exist in this change. Base: Milestone 6
commit `bc09d3b84e4e6b105f209afb57e38fe048764eb5`. Existing experiments remain
frozen. This protocol proposes a small descriptive pilot, not a population study.

## Approved Track A planning addendum (2026-09-23)

The researcher approved the Track A planning package and final character,
staging, usage and role decisions in the
[Track A production plan](track_a_planning/PRODUCTION_PLAN.md),
[character specification template](track_a_planning/CHARACTER_SPEC_TEMPLATE.md)
and [records/validation plan](track_a_planning/RECORDS_AND_VALIDATION.md).
Asha (`track-a-asha-v1`) supersedes the provisional character description below
for Track A only. The eight-landmark definition in Primary metrics supersedes
scarf/boot/cuff-specific wording for Track A only. Track D's contract, assets,
approvals and status are unchanged. Numeric artistic tolerances are review
guidance; the production plan separately lists hard gates and rejection rules.
Ananya is sole artist, artistic-intent authority and reference-landmark creator;
Samiksha is compliance reviewer, reference verifier and primary model-output
annotator. Permitted uses are local research/evaluation, publication figures and
portfolio demonstration; dataset redistribution is not currently authorized.
Authorship and usage authority do not assert a broader legal conclusion.
Planning approval is not evidence of actual production events, signatures,
dataset acceptance, freeze or inference authorization. Prospective D/k intent
remains separate from later final-frame hash binding. Sidecar/annotation contracts
are prose specifications, not implemented executable validation. Executable
landmark metrics, annotation validation, sidecar validation and accepted-version
inventory validation remain future pre-inference work. The records plan defines
immutable revision events, independent review revision IDs, separate reviewer
copies/overlays and accepted-version inventory paths. Its one-way dependency
order is selection_intent plus source/guide/Krita/final-export artifacts → immutable
per-frame sidecars → gate_review → selection_binding → admission → accepted-version
inventory. No downstream record is hashed upstream; this avoids circular/self-
referential dependencies. Sidecars are immutable once submitted for gate review
and contain no canonical-copy, gate-review, binding, admission or inventory hashes.

## Strictly separate tracks

**Track A — primary evaluation:** six complete original sequences, eight
authoritative frames each, one recurring original character. An artist constructs
poses with a rig and manually cleans up every line-art frame. These are artist
reference drawings at eight discrete times, not evidence of a unique physically
correct continuous motion. No AI-generated drawing enters this track. Record the
rig's origin, tool versions, original editable files, creator and cleanup history.
The artist chooses D, its index k, and a motion-intent rationale before viewing any
interpolation result, including previews or failed trials. Automated placement,
post-result k selection and best-of-many model output selection are prohibited.

**Track D — exploratory stress tests:** four AI-generated A/D/B triplets:

| ID | Motion |
| --- | --- |
| d01 | Curved jump |
| d02 | Hold-then-fast reach |
| d03 | Exaggerated recoil |
| d04 | Body turn with self-occlusion |

The Track D roster was prospectively amended on 2026-09-22 to match the
researcher-approved source triptychs, before preprocessing approval or inference.
A, D and B were selected together by the researcher. Method: AI-generated
exploratory input; provider/tool: OpenAI image generation through ChatGPT.
The human role was motion specification, iterative visual review and approval.
D does not represent independently human-authored intent. Track D remains
excluded from primary Track A research claims. Track D is complete and
researcher-approved: `researcher_approved`,
`provenance_complete_with_disclosed_limitations`, and
`ready_for_complete_dataset_freeze_review`; `frozen=false` and
`inference_authorized=false`. Both Ananya Anand and Samiksha Prasad approved the
provenance/usage record. Usage permits research/evaluation, publication figures
and portfolio use; dataset redistribution is not currently authorized.
The combined six-Track-A/four-Track-D dataset freeze review remains pending.
Inference remains unauthorized until that complete-dataset freeze succeeds.
Track D provenance and usage decisions are complete and are not reopened.

Researcher visual review approved all 12 normalized Track D frames on
2026-09-22, with these qualifications:

- d01, d03 and d04 are accepted without adjustment.
- d02 is accepted as a difficult exploratory sequence. D and B are intentionally
  close but remain distinguishable through arm extension, torso commitment and
  stance.
- Existing source-level scarf, tassel and vest-detail variation is acknowledged
  and retained as real generative inconsistency.
- The relatively small character scale is accepted because sequence-wide
  framing preserves motion coordinates and avoids per-frame recentering.
- No additional cropping, scaling, retouching or generation is authorized.

Visual approval is distinct from provenance and usage confirmation. A subsequent
authorized researcher declaration supplies project usage authority, and the
Track D version 2 contract records date-only historical events, recovered
conversation excerpts, and explicitly unavailable internal generation metadata.
Complete generation history is not claimed. The corrected local manifests are
researcher-approved with disclosed limitations; no timestamps or ownership claims
are inferred from visual approval. Track A production and the combined complete-
dataset freeze review remain pending. RIFE must not run yet.

These serve engineering validation and portfolio demonstration only. They have
no authoritative intermediate animation and no claim of human artistic intent.
Exclude them from every primary quantitative average, success count and research
claim. Keep separate exports, captions and reports labelled **AI-generated
exploratory — not primary evaluation**. Do not compute reference-intermediate
quality scores from three images or treat D as a ground-truth trajectory.
Sequence-level generation disclosure summarizes the session; each frame also
records its actual model/version, full prompt (including negative prompt and
settings), date/time, seed or explicit unavailability reason, edits, authorship
status and license/usage evidence. For a jointly generated triplet, repeat the
shared record and document extraction in each frame's preprocessing. For multiple
calls, include the complete ordered generation history in prompt/edits text.
Generation is future, separately authorized work; this preparation performs none.

## Character and asset contract

Track A uses the approved Asha specification linked above, including its exact
palette and construction guidance. The following provisional description is
retained as historical context, not an instruction to redraw Track D or produce
Track A with scarf/boots:

An original simple full-body humanoid with a distinctive hair silhouette, visible
facial features, jacket and cuffs, asymmetrical scarf, trousers and boots. Dark
approximately 5-pixel line, off-white background, minimal shading, fixed camera.
Canonical evaluation assets are single-frame **512×512 RGB PNG**, without alpha.
RGB is required for Track A and retained unchanged for Track D, avoiding implicit
compositing at evaluation.
Artist review must confirm the recurring identity and visible design details;
file validation cannot establish authorship, pose quality or manual cleanup.

Preserve raw originals in a separate local source archive. Prefer constructing at
canonical size/mode. Any crop, resize, rotation, color conversion or alpha
composite happens before freezing, with ordered parameters, source and output
hashes, operator and timestamp recorded. Empty operations means byte-identical
source and output hashes. Never overwrite originals. After freeze, the canonical
uploaded A/D/B pixels are immutable: no repair, alignment or normalization of
those images. Internal RIFE padding must be removed without altering the saved
authoritative copies. PNG preservation is pixel equality, not PNG byte equality.

## Directory, filenames and manifest contract

Actual assets are local and ignored by Git; no empty drawings or fabricated
primary records are committed. The following is a convention, not existing data:

```text
.local/real_input_pilot/
  sources/                         # retained editable/raw originals and rights evidence
  dataset/
    track_a/
      a01/                         # a01 through a06
        manifest.json
        frames/frame_000.png       # A
        frames/frame_001.png       # through frame_006.png, including D at k
        frames/frame_007.png       # B
    track_d/
      d01/                         # d01 through d04, fixed motion roster above
        manifest.json
        frames/frame_000.png       # A
        frames/frame_00k.png       # notation only: e.g. frame_003.png for k=3
        frames/frame_007.png       # B; exactly three files
  freeze/                          # immutable manifest copies, hashes, signed review, annotations
outputs/real-input-pilot/<freeze-id>/
  track_a/<sequence-id>/{endpoint,guided}/
  track_d/<sequence-id>/{endpoint,guided}/
```

Indices are zero-based. Both tracks use eight output slots, t=i/7, N=6 and k in
1..6. Track D's other five slots are unobserved, never missing primary data.
D is a reference to the existing canonical frame k, not a duplicate D.png.
`a01`..`a06` are identity slots; artist-selected motion descriptions are frozen
before inference. Sequence/frame order is numerical; manifests list ascending
indices. Source archives and freeze records sit outside the validator's dataset
root. No extra sequence files or directories are accepted inside that root.

Copy [Track A template](real_input_templates/track_a.json) or
[Track D template](real_input_templates/track_d.json) outside the repository and
fill every `REPLACE_` value. The sample k=3 is illustrative, not an artist decision.
These are **validated manifest templates**, not JSON Schema documents or actual
provenance. Their executable contract is `validate_manifest` in
`inbetween/pilot_dataset.py`; unknown/missing fields, wrong types and unresolved
placeholders are errors. Empty edit/operation lists explicitly mean none within
their declared scope; incomplete AI correction history must be disclosed in
Track D's prompt provenance, never represented as a complete empty history.

The table below describes the original version 1 contract, still required for
Track A and readable for legacy Track D records. New Track D records use the
version 2 corrections described immediately below it.

| Section | Required fields |
| --- | --- |
| Sequence | version=1, track, sequence_id, purpose, character_id, motion |
| Sequence provenance | creator, created_at, method, tools, authorship_status, source_files |
| Frame provenance | index, path, sha256, creator, created_at, method, edits, ai_generation, preprocessing |
| AI disclosure | model, model_version, prompt, generated_at, seed (integer or null), seed_note, edits, authorship_status, usage_basis; null at sequence and frame levels in A |
| Artist D/k selection | kind, k, D_path, D_sha256, selected_by, selected_at, before_model_results=true, rationale; D uses exploratory_curator rather than artist |
| Preprocessing | source_path, source_sha256, output_sha256, operations, original_preserved=true, recorded_by, recorded_at |
| Rights/consent | holder, usage_basis, consent_status (confirmed or not_required), consent_basis, confirmed_by, confirmed_at |

For Track A, v1 `rights.usage_basis` must explicitly state: local
research/evaluation permitted; publication figures permitted; portfolio
demonstration permitted; dataset redistribution not authorized. These statements
use the existing text field, not separate executable `permitted_uses` fields.

Version 1 timestamps use ISO 8601 with timezone; all file hashes use lowercase SHA-256.
Rights scope must cover local evaluation and separately state whether portfolio
publication and dataset sharing are allowed. Record creator and any depicted
person's consent when applicable; for a wholly fictional original character,
`not_required` needs a reason. When citing license/terms as the usage basis,
include their version/date and retained evidence references. Version 2 also
supports an explicit researcher project-usage declaration as described below;
the validator checks completeness, not legal validity.
Source paths are archive references, not paths opened by the validator. Reviewers
must verify originals, source hashes and evidence manually before freeze. Do not
put private consent documents or credentials in Git or public exports.

### Track D version 2 provenance correction

Version 2 is restricted to exploratory Track D; it does not relax Track A.
The generic Track D template is the complete field contract. No personal rights
declaration or actual dataset manifest is tracked.

- Historical `provenance.created_at`, frame `created_at`, generation
  `generated_at`, `selection.selected_at` and `rights.confirmed_at` are objects
  with `precision`, `value`, `reason`, `source`. Precision is `exact`
  (timezone-aware ISO timestamp), `date_only` (YYYY-MM-DD, no invented timezone),
  or `unavailable` (null value and nonempty reason). Available event values have
  null reason. Evidence source is always required.
- Exact `provenance.recorded_at` records authorship of the current provenance
  record; `selection.recorded_at` preserves when the selection record was
  originally authored; `rights.recorded_at` records declaration authorship.
  `selection.selected_at` means the historical selection event, never authoring
  time. Original preprocessing fields remain unchanged. Frame source-creation
  events inherit the triptych generation event; normalization is separate.
- Chronology rejects provably reversed events using conservative possible-time
  bounds. Date-only events have no known timezone; overlapping bounds or
  unavailable events cannot establish order. No bounds are written as event
  timestamps. `before_model_results=true` and a nonempty
  `before_model_results_basis` are both required. Reviewers must assess evidence;
  a same-day date alone cannot prove pre-inference selection.
- Generation records separate `provider`, `interface`, `model_identifier`,
  `seed`, `inference_settings`, `generated_at`, `local_gpu_used`,
  `generation_compute`, `D_authorship`, `human_role`, `usage_basis` and
  `prompt_provenance`. Nullable metadata uses `{status, value, reason}`:
  unavailable requires null value and nonempty reason; available requires a
  typed value and null reason. Hosted generation cannot claim local GPU use.
- Prompt provenance separates `conversation_instructions` (kind, text, source,
  scope) from `internal_expanded_prompt`. Kinds distinguish researcher
  instructions, approvals and explicitly labelled approval summaries. A
  partial/complete `history_status` and explanatory `history_note` describe
  coverage. Recovered excerpts are not an assertion of full transcript,
  per-output message mapping or internal tool prompts. Pending markers and
  conversation text substituted for an internal prompt are rejected.
- Rights record multiple named `authorities` and matching `confirmed_by`,
  capacity, nullable organization, declared usage basis, permitted uses,
  dataset-redistribution scope, consent status/basis, event and recording times,
  and an evidence reference. `declaration_scope` must be
  `project_usage_authority_not_ownership`. This implements the authorized
  researcher decision to document project usage authority, not to guess legal
  ownership. Research/evaluation permissions are required; publication figures
  and portfolio uses are explicit. Dataset redistribution is not implied.
- Sequence/frame generation disclosures and creation events must agree for
  the triptych-derived frames. Source hashes, frame hashes and preprocessing
  checks remain mandatory. Evidence references are reviewed manually, not
  authenticated by the validator. Missing declarations cannot be waived by an
  unavailable-model flag.

Known unexposed model/settings/internal prompts are reproducibility limitations,
not values to invent. Partial conversation history can be honestly ingested;
its sufficiency for exploratory use requires researcher review, already completed
for the approved Track D records. A successful
version 2 validation certifies structural ingestion only, never a dataset freeze.

## Validation and freezing gates

Run locally in the existing environment:

```bash
.venv/bin/python -m inbetween.pilot_dataset .local/real_input_pilot/dataset --partial
.venv/bin/python -m inbetween.pilot_dataset .local/real_input_pilot/dataset
```

Partial mode validates available sequences and explicitly returns
`partial_ingest_only`; it never certifies readiness. Full mode requires exactly
six A sequences (48 frames) and four D triplets (12 frames), one A character ID,
canonical paths, dimensions, mode and PNG format. It verifies decoded images,
file hashes, preprocessing hash links, integer k, D path/hash identity with frame
k, provenance, consent declarations and track/directory/purpose consistency.
It rejects symlinked entries, unexpected files, duplicate JSON keys, nonfinite
JSON values, duplicate file bytes and duplicate decoded pixels within or across
tracks. Intentional held frames would currently be rejected: agree and version a
hold exception before data freeze rather than silently bypassing validation.
No validator invocation edits images or imports a backend.

A passing ingest report does **not** verify the truth of an artist declaration,
rights, archive hashes, or absence of earlier model exposure. Before inference,
a reviewer verifies these, reviews all 48 cleaned drawings and four disclosures,
records approval, and freezes copies plus SHA-256 hashes of manifests, images,
selection records, protocol, annotations, code commit and tool/backend versions.
Record freeze time before any model run; selections must predate it. Store
read-only provenance snapshots and a review record with reviewer, timestamp,
checks, evidence and outstanding issues. Before model exposure, changes require a new version with a
reason and explicit exclusion of the old version. After exposure, authoritative
primary frames cannot be repaired or replaced; disclose or exclude under the
approved rules. Never select a revision using model performance. The existing implementation provides ingestion only, not an evaluation runner,
annotation UI or automatic freeze-signing system.

## Frozen comparison

For each sequence, one endpoint-only RIFE A→B run and one artist-guided RIFE
A→D→B run through the existing `InterpolationBackend` and guided orchestration.
Use the same pinned RIFE source/checkpoint, device, precision, preprocessing,
canonical A/B, eight timestamps and export settings. Record their actual hashes
and settings, time, errors and execution provenance. The endpoint-only model
receives no D. Guided segment counts are k−1 and 6−k with D copied into slot k.
A/B must be exact in both methods; D must be exact in guided output. Endpoint-only
slot k is generated and is not required to equal D. Never overwrite it with D.

For primary image/landmark metrics use the identical generated-only set
**E={1,2,3,4,5,6} minus {k}** for both methods (five frames per sequence). Keep
index-k diagnostics separate and excluded from primary means. Temporal pairs are
**P={(i,i+1): i and i+1 are both in E}** for both methods; disclose the exact
pair indices/counts (three or four depending on k). Do not mix preservation
scores or authoritative-frame transitions into generated-only quality means.

No silent fallback to crossfade, alternate checkpoint, alternate k or revised
input. Record a failed method/sequence and reason; do not substitute, rerun for
quality or silently drop it. Any necessary technical retry retains the failure
record and its configuration/reason. Report planned versus complete coverage;
paired summaries name their common complete sequence IDs. Full pilot success
requires all six primary pairs. Separate Track D demonstrations have no weight.

## Primary metrics (definitions frozen here; implementation is future work)

Report per-frame/per-pair values, per-sequence means, then equal-weight means of
the six sequence means. Do not pool frames across sequences or combine these
metrics into a rank. Gains are guided minus endpoint for F1 and endpoint minus
guided for errors. Report absolute values, paired deltas and all six cases.

1. **Edge F1:** existing RGB→grayscale OpenCV Canny 100/200 edges and two-pixel
   Euclidean matching tolerance at 512×512. Precision is the fraction of predicted
   edges within tolerance of reference, recall reverses the roles; harmonic mean.
   Both edge maps empty gives F1=1, one empty gives 0.
2. **Symmetric Chamfer:** half the sum of the two directional mean nearest-edge
   Euclidean distances in pixels, matching existing `benchmark_metrics.py`.
   Both maps empty gives 0; one empty gives image diagonal sqrt(512²+512²).
3. **Landmark trajectory error (Track A):** mean Euclidean position error in
   pixels over E and eligible landmarks; show trajectories, per-landmark errors
   and coverage. The approved eight-point set is nose tip, anatomical left elbow,
   anatomical right elbow, anatomical left wrist/hand-base center, anatomical
   right wrist/hand-base center, anatomical left sneaker toe, anatomical right
   sneaker toe, and braid free tip. This replaces the old scarf/boot/cuff wording
   for Track A only; it changes no Track D record or exploratory contract.
   Coordinates use image x right/y down, origin at top-left pixel center, range
   [0,511]. Paired landmark eligibility is determined only by the authoritative
   Track A reference frame at that timeline index. If a landmark is invisible or
   genuinely occluded in the reference, exclude that landmark/index from both
   methods’ positional scores; retain and report the exclusion and reference
   visibility status. Never estimate hidden reference positions.
   If reference-visible, the landmark remains eligible for both methods. Annotate
   a coordinate normally when identifiable in an output. If missing, malformed,
   merged, severed or otherwise unidentifiable, assign the existing image-diagonal
   penalty sqrt(512²+512²) pixels to that method; do not remove the landmark/index
   from either method’s evaluation mask. An output-specific occlusion absent from
   the reference is generated-result failure/behavior, not an eligibility reason:
   record its output visibility/failure category and apply the same penalty.
   Preserve raw reference and per-method visibility/status records. Report total
   reference-visible eligible landmarks, valid-coordinate count per method,
   penalized missing/unidentifiable count per method (including output-only
   occlusion), reference-occluded/invisible exclusions, and per-landmark coverage
   and error. Counts refer to landmark/index observations over the scored set E.
   A sequence/index with no reference-visible eligible landmarks cannot contribute
   a landmark score and must be reported as a coverage failure, never silently
   dropped from aggregate reporting or represented as zero error.
   Ananya creates reference landmarks, Samiksha verifies them, and references
   must be resolved and frozen before inference. Samiksha annotates randomized,
   method-hidden model outputs; she cannot choose the shared evaluation mask
   based on perceived method quality. Ananya adjudicates only documented ambiguous
   cases after Samiksha’s initial annotation; preserve initial records and reasons.
   The shared mask is fixed from references, independent of output annotation or
   adjudication. This is sampled trajectory-position error, not optical flow or
   inferred intent. Operational status/blinding rubrics and executable metric
   implementation and annotation validation remain pre-inference work; reference-
   only eligibility is approved, not an unresolved mask choice.
4. **Temporal flicker/consistency:** mean over P of
   `mean_pixels(abs((Y[i+1]-Y[i])-(R[i+1]-R[i])))`, using grayscale intensities
   scaled to [0,1] and signed floating-point differences (Y output, R reference).
   Lower is better. This reference-relative temporal-change residual measures
   changes in reconstruction error; it is affected by motion/registration and is
   not a pure perceptual flicker measure. Report paired playback review separately.
   No flow warping, frame-specific registration or threshold tuning.
5. **Exact authoritative preservation:** decoded PNG mode, dimensions and pixel
   array equality for A/B in both methods and D in guided, checked individually
   with reference hashes. Required 30/30 primary checks (five per sequence);
   track D has a separate 20-check engineering report. Any mismatch is a failure,
   never averaged away. Encoded GIF/MP4 previews are not preservation evidence.

Landmark annotation files under `freeze/` must record sequence, frame index,
landmark name, raw reference visibility/status, x/y or null for hidden reference
points, annotator, timestamp and reference image hash. Candidate records retain
per-method visibility/failure status, valid x/y or null if unidentifiable, output
hash and blinded code. Store penalty/error separately from coordinates; a null
output coordinate never removes a reference-visible observation from the mask.
Use the approved Track A roles and eight-point mapping above;
finalize the operational visibility/blinding rubric before inference, retain original
annotations, and report disagreement; do not tune landmarks to outputs.
The ingest validator does not yet validate these future annotation records.

**Secondary only:** PSNR and SSIM using existing grayscale definitions; represent
infinite PSNR explicitly rather than emitting nonfinite JSON. Optional LPIPS may
be added only if its exact implementation, local existing weights, hash and
normalization are frozen before inference; no downloads in this preparation.
Its absence does not fail the primary pilot. Do not let secondary scores override
primary failure or blend Track D into quantitative evidence.

## Descriptive success criteria and limits

Operational completion: all six primary pairs, all five primary metric families
with explicit coverage, exact 30/30 preservation, complete provenance and no
fallback. Incomplete pairs or absent annotations mean the full pilot is incomplete;
show partial results with denominators rather than declaring success.

Proposed descriptive benefit target: at least four of six sequences improve both
mean edge F1 and mean Chamfer, with no worsening of the equal-sequence mean
landmark or temporal error. Strict improvement means positive unrounded delta;
zero is a tie. Report every metric's wins/ties/losses, failures and magnitude even
if this target fails. This target is not a validated perceptual threshold.
Artist review records fidelity to intended pose/timing, artifacts and preference
for each blinded pair, with verbatim rationale and ties permitted; it is
contextual evidence, not a replacement quantitative score or broad usability test.

Any finding is limited to these six sequences, one character and the contributing
artist(s), at this resolution and pipeline. No significance test, confidence
interval suggesting population inference, claim of generalization, calibrated
control, superiority across animation, or novel interpolation method. Track D
supports engineering demonstrations only. Negative/mixed outcomes are retained.

## Decisions still requiring pre-inference resolution

- a02–a06 motions, timing and D/k choices; a01 character, staging, formal t=i/7,
  preview 8 fps and A=0/D=4/B=7/k=4 are approved. A passing a01 occupies one of
  the final six slots, subject to actual acceptance records.
- Actual approved model-sheet measurements, a01 foot/target coordinates, local
  tool versions/profile/export settings, source archive and rig origin, hashes,
  timestamps, revisions, rights/consent evidence, approvals and signatures.
  Approved Track A use scopes and named roles are no longer open decisions.
- Actual final-frame D/k hash bindings, model non-exposure evidence and timestamped
  freeze review; preserve the earlier prospective intent separately.
- Operational visibility rubric, randomized method-hidden annotation logistics
  and repeatability review; staffing/adjudication roles are approved above.
  Implement and test landmark/temporal evaluation before any pilot run.
- Confirm or prospectively amend the proposed descriptive target; deliberate held
  frames need a versioned duplicate policy before freezing assets.
- Track D is complete and researcher-approved, including its provenance/usage
  record with disclosed date precision and partial conversation-history limits.
  The combined six-Track-A/four-Track-D dataset freeze review remains pending;
  inference remains unauthorized until that complete-dataset freeze succeeds.
- Optional existing-local LPIPS availability and the future run environment.

These are preparation gates, not permission to begin generation or evaluation.

## Track A review safeguards

Samiksha never edits or saves an authoritative `.kra`. Only Ananya may edit
these sources, including all hidden layers. Samiksha’s review notes and landmark
overlays live in separate review copies/sidecars.

For a01, the blinded model-output quality/landmark annotation pool contains only
E = {1, 2, 3, 5, 6} for both endpoint-only and guided methods. Do not include
A, D/k or B; evaluate authoritative-slot preservation diagnostics separately.
For later sequences, use the protocol’s generated-only E excluding their approved k.
Samiksha performs initial annotation using randomized, method-hidden codes.
Ananya receives only the same blinded codes during adjudication. The endpoint-only/
guided method key remains sealed until all initial annotations and adjudications
are complete. Record the original ambiguity flag, who raised it, initial
annotation, adjudication decision and reason; preserve both original and
adjudicated values. Output status cannot remove a reference-visible point from
paired eligibility; output-only missing/occluded/unidentifiable points receive
the image-diagonal penalty. Only authoritative-reference visibility determines
the shared mask.

After any sequence has been exposed to model output, do not repair or replace
its authoritative primary frames. Report defects and either retain with disclosure
or exclude the sequence from primary eligibility under the approved rules.
Never use model results to guide a corrected authoritative frame. Rework and
new source revisions are permitted only before model exposure.
