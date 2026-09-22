# Milestone 7: Real-Input Artist-Controlled Pilot

Status: protocol and dataset infrastructure only, 2026-09-22. No pilot assets,
model execution, pilot metrics or results exist in this change. Base: Milestone 6
commit `bc09d3b84e4e6b105f209afb57e38fe048764eb5`. Existing experiments remain
frozen. This protocol proposes a small descriptive pilot, not a population study.

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
| d01 | Curved arm reach |
| d02 | Jump with anticipation and landing |
| d03 | Head turn with facial-feature movement |
| d04 | Body crossing behind an object |

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

## Provisional character and asset contract

An original simple full-body humanoid with a distinctive hair silhouette, visible
facial features, jacket and cuffs, asymmetrical scarf, trousers and boots. Dark
approximately 5-pixel line, off-white background, minimal shading, fixed camera.
Canonical evaluation assets are single-frame **512×512 RGB PNG**, without alpha.
RGB is a provisional explicit choice to avoid implicit compositing at evaluation.
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
placeholders are errors. Empty edit/operation lists explicitly mean none.

| Section | Required fields |
| --- | --- |
| Sequence | version=1, track, sequence_id, purpose, character_id, motion |
| Sequence provenance | creator, created_at, method, tools, authorship_status, source_files |
| Frame provenance | index, path, sha256, creator, created_at, method, edits, ai_generation, preprocessing |
| AI disclosure | model, model_version, prompt, generated_at, seed (integer or null), seed_note, edits, authorship_status, usage_basis; null at sequence and frame levels in A |
| Artist D/k selection | kind, k, D_path, D_sha256, selected_by, selected_at, before_model_results=true, rationale; D uses exploratory_curator rather than artist |
| Preprocessing | source_path, source_sha256, output_sha256, operations, original_preserved=true, recorded_by, recorded_at |
| Rights/consent | holder, usage_basis, consent_status (confirmed or not_required), consent_basis, confirmed_by, confirmed_at |

All timestamps use ISO 8601 with timezone, all file hashes lowercase SHA-256.
Rights scope must cover local evaluation and separately state whether portfolio
publication and dataset sharing are allowed. Record creator and any depicted
person's consent when applicable; for a wholly fictional original character,
`not_required` needs a reason. Include license/terms version/date and retained
evidence references; the validator checks completeness, not legal validity.
Source paths are archive references, not paths opened by the validator. Reviewers
must verify originals, source hashes and evidence manually before freeze. Do not
put private consent documents or credentials in Git or public exports.

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
checks, evidence and outstanding issues. Changes require a new version with a
reason and explicit exclusion of the old version; never select a revision using
model performance. This task implements ingestion only, not an evaluation runner,
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
3. **Landmark trajectory error:** mean Euclidean position error in pixels over E
   and reference-visible landmarks; also show trajectories and per-landmark
   errors. Freeze artist reference points before inference: nose tip, left/right
   wrist (cuff center), left/right boot toe, and scarf free tip. Coordinates use
   image x right/y down, origin at top-left pixel center, range [0,511]. Freeze
   visibility and anatomical identity per frame; do not infer hidden points.
   Independently annotate outputs in randomized, method-blinded order using the
   same rubric. A reference-visible but missing/unidentifiable output point gets
   image-diagonal penalty, never omission. Reference-invisible points are excluded
   symmetrically with counts. A sequence with no eligible points fails coverage.
   This is sampled trajectory-position error, not optical flow or inferred intent.
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
landmark name, visibility, x/y or null for hidden points, annotator, timestamp and
reference image hash. Candidate records additionally identify output hash and
blinded code. Fix the mapping and adjudication process before inference, retain
original annotations, and report disagreement; do not tune landmarks to outputs.
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

- Artist/reviewer identity, six motions, timing rationale, rig/tool choice and
  original character design approval; confirm the provisional RGB/line styling.
- Source archive, authorship, usage/publication permissions and consent evidence.
- Actual D/k choices, declared model non-exposure and timestamped freeze review.
- Landmark annotation staffing, blinding/adjudication logistics and repeatability
  review; implement and test landmark/temporal evaluation before any pilot run.
- Confirm or prospectively amend the proposed descriptive target; deliberate held
  frames need a versioned duplicate policy before freezing assets.
- Track D generation model/terms and prompts (not selected or executed here),
  optional existing-local LPIPS availability, and the future run environment.

These are preparation gates, not permission to begin generation or evaluation.
