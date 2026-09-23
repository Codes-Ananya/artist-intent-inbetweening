# Track A records and CPU validation plan

Researcher-approved documentation contract only, not executable JSON Schema, generated
provenance or a validator change. No directories or records below are instantiated
by this protocol. Companion: [production plan](PRODUCTION_PLAN.md).

## Local paths and revision convention

All actual material remains under Git-ignored `.local/real_input_pilot/`.
Paths below are relative to that root. Use zero-padded indices and revisions;
never overwrite accepted revisions. All references use root-relative paths with
no `..`, external absolute paths or symlink traversal.

```text
sources/track_a/track-a-asha-v1/
  character_spec_r001.md
  model_sheets/<sheet-id>/asha_<sheet-id>_r001.kra
  model_sheets/<sheet-id>/asha_<sheet-id>_r001.png
  rig/asha_rig_r001.sif
  rig/dependencies/<retained-dependency>
  a01/synfig/a01_guides_r001.sif
  a01/guides/r001/frame_000_guide.png        # through frame_007_guide.png
  a01/krita/frame_000_r001.kra              # through frame_007_r001.kra
  a01/exports/r001/frame_000.png            # through frame_007.png
  a01/provenance/frame_000_r001.json        # through frame_007_r001.json
  a01/provenance/selection_intent_r001.json
  a01/provenance/selection_binding_r001.json
  a01/provenance/revision_events/revision_event_0001.json
  a01/provenance/revision_events/revision_event_0002.json
  a01/provenance/accepted_versions/accepted_version_0001.json
  rights/track_a_rights_r001.md
review/track_a/a01/review_r001/
  gate_review.json
  annotations.json
  copies/frame_000_review_r001.kra           # separate reviewer copy only
  overlays/frame_000_landmarks_review_r001.json
  admission.json
  validation_report.json
  contact_sheet.png                        # future review only
  playback.gif                            # future review only
dataset/track_a/a01/
  manifest.json
  frames/frame_000.png                     # exactly 0–7 when admitted
```

Sheet IDs: `front`, `three_quarter_front`, `side`, `three_quarter_back`, `back`,
`neutral_face`, `hands`, `braid`. `.sifz` is an alternative if actually used;
record exact format and dependencies. Final dataset filenames have no revision
suffix; their source export revision is resolved in the accepted-version inventory. Dataset copies are
byte-identical to accepted exports. Do not create duplicate D.png. Drafts stay
outside `dataset/`; no review/source sidecars enter that strict root. Review
previews are never authoritative pixels. a02–a06 follow the same convention.

A sequence-level production batch uses `r001`, `r002`, etc. A local correction
creates a new immutable revision for that frame; unchanged frames retain their
earlier revisions. Review records use independent IDs such as `review_r001` and
`review_r002`, which do not imply that every source frame changed. Each immutable
revision-event record records actor, actual time, reason, changed artifacts,
prior/new revision references and hashes. Never overwrite a revision event after
hashing or review. Subsequent events may reference earlier events, never the reverse.

The separate accepted-version inventory at
`sources/track_a/track-a-asha-v1/a01/provenance/accepted_versions/accepted_version_0001.json`
resolves the exact accepted guide, Krita source, export and sidecar revision and
path/hash for every frame, including unchanged earlier revisions. It references
the admission record and canonical dataset copies with their paths, hashes and
copy timestamps. Later accepted versions get new immutable inventory filenames.

## One-way record dependencies

```text
selection_intent + source/guide/Krita/final-export artifacts
  → immutable per-frame provenance sidecars
  → gate_review
  → selection_binding
  → admission
  → accepted-version inventory
```

Per-frame sidecars become immutable when submitted for gate review. They must
not contain canonical dataset-copy hashes, gate-review hashes, selection-binding
hashes, admission hashes or inventory hashes. `gate_review` references/hashes the
exact sidecars reviewed and uses its own review revision ID. `selection_binding`
references the prospective `selection_intent`, accepted D frame hash and applicable
`gate_review` path/hash. `admission` references/hashes `gate_review` and
`selection_binding`. The accepted-version inventory references/hashes admission
and the canonical dataset copies. No downstream record is hashed by an upstream
record, and no record embeds its own hash. This avoids circular/self-referential
dependencies. Corrections require new records and downstream review/binding/
admission/inventory records as applicable; never mutate a submitted sidecar.

## Locked pre-results selection: two records

The researcher's approved prospective intent is:

| Field | Value |
| --- | --- |
| sequence_id / character_id | a01 / track-a-asha-v1 |
| motion | curved_arm_reach |
| frame_count / A / D / B / k | 8 / 0 / 4 / 7 / 4 |
| selected_by | Ananya Anand |
| selection_basis | strongest intentional curved motion arc |
| selected_before_model_results | true |
| evidence | Current researcher instruction; preserve an actual reference when recorded |

`selection_intent` additionally requires record version, immutable intent revision,
actual `recorded_at`, `recorded_by`, evidence reference, storyboard/specification
references and hashes, exposure attestation/scope and amendment history. The exact
historical choice timestamp was not supplied; mark it unknown with reason in the
sidecar, never infer midnight or authoring time. No actual intent record or
attestation may be manufactured from planning approval. On authorized recording,
retain the approved text, hash the record, obtain Ananya's confirmation, and keep
immutable revision-event records. This locks the approved intent, not nonexistent
frame bytes. Amendments need pre-results review and may not conceal old choices.

After production but before any model output, `selection_binding` requires:
intent path/hash, applicable gate-review path/hash and review revision ID,
production batch revision, k=4, D_path=`frames/frame_004.png`, actual
D_sha256, all eight accepted source-export paths/hashes, actual `bound_at` with timezone, Ananya's
confirmation, no-results attestation and evidence, reviewer/time, and record hash
in a separate inventory. Never embed a record's own hash inside its hashed bytes.
If frame 4 changes during permitted pre-exposure rework, retain the old binding and create a
new binding to the revised bytes without changing the approved k/rationale.

Map binding confirmation time to manifest v1 `selection.selected_at`; it means
selection confirmation of the actual final drawing, not the earlier conceptual
choice. Preserve the distinction explicitly in `selection.rationale` with intent
and binding references. Manifest `before_model_results=true` maps from the
approved `selected_before_model_results=true` plus actual pre-exposure attestation.
The existing validator requires selection after sequence creation and actual
D hashes; therefore the prospective choice cannot yet be a valid manifest.
Chronology must be real, with selection binding after final export and before
future freeze and inference. Missing exact production/binding times block
admission; do not backdate or relax the Track A v1 contract.

## Per-frame provenance sidecar field contract

| Fields | Type / meaning / completion rule |
| --- | --- |
| record_version, track, character_id, sequence_id, frame_index, revision | Integer version/index; A, track-a-asha-v1, a01, 0–7; revision identifier |
| artist | Exact `Ananya Anand`; authoritative drawing author |
| contributors | Array of person, role, task, evidence, timestamp; nonartist roles cannot include authoritative drawing edits |
| guide | Path/hash of actual Synfig export; source project path/hash, rig path/hash, dependency inventory; guide export timestamp and operator |
| krita_source | Path/hash, source revision, exact tool version, color profile, canvas/mode; source created_at and last_saved_at |
| final_export | Path/hash, exported_at, exported_by, format, width/height, decoded mode; source revision and export settings |
| creation_edit_history | Nonempty ordered event array: actor, role, timezone timestamp, operation, input/output revision references and hashes, reason; distinguish guide creation, manual drawing, cleanup and export |
| manual_changes | Nonempty frame-specific descriptions, affected parts, artist, edit event references; explicitly document redraw and guide deviations/occlusion repairs |
| preprocessing | Pre-submission export/conversion operations with parameters, source-artifact input/output hashes and actor/time; empty if none; excludes downstream canonical copying |
| rights | Declaration path/hash, declarant, actual declared_at, original authorship/design basis, rig/reference origin, permitted use scopes and restrictions, consent status/basis, retained evidence |
| selection_intent | Prospective intent path/hash; no downstream review or acceptance links |
| recorded_by, recorded_at, supersedes, change_reason | Record author and actual timezone timestamp; prior revision reference or null for first record; explicit change reason |

All hashes are lowercase SHA-256 of file bytes. Optionally record decoded RGB
pixel digest with a documented byte serialization, separate from file SHA-256.
Timestamps are actual timezone-aware ISO 8601 events; filesystem mtime is not
proof of authorship or creation time. Unknown required evidence stays unresolved
and blocks admission. Revision inventories bind exact bytes of guides, `.sif`,
`.kra`, flattened images and declarations. Changes require a new immutable revision and rereview; the old approved
bytes and review remain retained without overwriting. Verify hashes against the retained files,
not merely against another string in a manifest.

Ananya's declaration must separately address original drawing/design authorship,
rig origin, external references, local research/evaluation, publication figures,
portfolio demonstration. Those uses are approved; dataset redistribution is not
currently authorized. Authorship and usage authority do not assert a broader
legal conclusion. Retain actual declarations, signatures and evidence when they
exist; do not fabricate them from this planning approval. Record the fictional
character consent basis; do not copy Track D's
usage declaration or researcher identities as Track A ownership evidence.

## Compatibility with the existing Track A manifest

Keep `docs/real_input_templates/track_a.json` and `validate_manifest` unchanged.
That generic template's k=3 is illustrative; the future a01 copy must use k=4.
Manifest version remains 1, method `rig_assisted_manual_cleanup` at sequence and
frame levels, `ai_generation=null` at both levels, and all creators Ananya Anand.
Set character/motion to approved IDs, canonical frames to 0–7, D path/hash to
frame 4. Sequence `created_at` records actual sequence creation, not planning.
Frame `created_at` records actual authoritative drawing creation; edits and
sidecars distinguish later saves/exports. `tools` records actual local versions
and rig origin; `source_files` lists retained sources and sidecar references.

Track A v1 `rights.usage_basis` must explicitly contain all four statements:
“local research/evaluation permitted”; “publication figures permitted”; “portfolio
demonstration permitted”; “dataset redistribution not authorized”. These are
text in the existing field; separate executable `permitted_uses` fields do not
exist in the v1 manifest. Retain the declaration/evidence reference in that text.

Use each frame's `edits` string list for factual manual-change summaries and
sidecar references. Retain the richer structured history outside the manifest.
For byte-identical final export→dataset copy, `preprocessing.source_path` points
to the preserved flattened PNG, source/output hashes agree and operations are
empty. The guide→Krita redraw is authorship history, not a byte-preserving PNG
preprocessing operation. Any genuine conversion gets ordered preprocessing
records with its actual preserved input and output hashes.

Current ingestion checks structure, canonical PNGs and some hash links, but does
not validate source sidecar schemas, source archive hashes, tool projects,
sole-artist identity, truthful manual redraw, or absence of model exposure. These
are future CPU audit checks plus human gates, not capabilities added by this plan.

## Annotation records and approved roles

Ananya is sole artist, artistic-intent authority and reference-landmark creator.
Samiksha is protocol-compliance reviewer, reference-landmark verifier and primary
model-output annotator using randomized, method-hidden outputs. Ananya adjudicates
only documented ambiguous cases after Samiksha’s initial annotation. Samiksha
must not modify authoritative drawings. Resolve and freeze references before
inference; retain initial annotations, verification and adjudication evidence.

The Track A primary set is nose tip, anatomical L/R elbows, anatomical L/R
wrist/hand-base centers, anatomical L/R sneaker toes and braid free tip: eight
landmarks, replacing scarf/boot/cuff wording for Track A only. Preserve raw
reference and per-method visibility/status for every landmark/index, coordinates
or null when unavailable, frame/hash, annotator/time, verifier/time and ambiguity/
adjudication history. Output records also need randomized method-hidden IDs,
output hashes and failure categories: missing, malformed, merged, severed,
otherwise unidentifiable, or output-only occlusion absent from the reference.

The shared eligibility mask depends only on visibility in the authoritative
Track A reference frame at that timeline index. Exclude reference-invisible or
genuinely reference-occluded observations from both methods, retaining/reporting
reference visibility and exclusions. Never estimate hidden reference positions.
Reference-visible observations remain eligible for both methods: use valid output
coordinates when identifiable; otherwise apply the existing image-diagonal
penalty sqrt(512²+512²) pixels for that method, including output-only occlusion.
Record the penalty separately from coordinates; null coordinates/output failure
statuses never remove reference-visible observations from either method’s mask.
Samiksha cannot select the shared mask based on perceived method quality; output
annotation and adjudication cannot change reference-derived eligibility.

Report total reference-visible eligible landmarks, valid-coordinate count per
method, penalized missing/unidentifiable count per method (including output-only
occlusion), reference-occluded/invisible exclusions, and per-landmark coverage and
error. Counts are landmark/index observations over the scored set E in the
parent protocol. A sequence/index with no reference-visible eligible landmarks
has no landmark score and must be reported as a coverage failure, including in
aggregate reporting, never silently omitted or assigned zero error.
These records, randomization, dates and signatures remain factual future work.
Metric implementation and executable annotation validation remain pre-inference
work; no executable annotation schema or scoring implementation is added here.

Hard gates and rework/rejection policy are defined in the
[production plan](PRODUCTION_PLAN.md). Numeric artistic indicators (proportion,
stroke, foot variation, margin, curvature and hem displacement) must not become
automatic rejection checks in future validators. Complete source/export hashes,
rights/approval records, approved palette and fixed frame contract remain required.
Retain the full revision history, with no arbitrary retry limit.

## CPU-safe regression and future production validation plan

Repository policy requires the complete CPU-safe pytest suite in the existing
`.venv` and a synthetic sample export before any commit. Disable CUDA with
`CUDA_VISIBLE_DEVICES=""`. Use only committed synthetic fixtures in `samples/`
for the sample export, with the local crossfade backend; never use Track A or
Track D assets. Temporary test fixtures and exports are test-only, never artist
drawings or provenance evidence. Keep exports outside tracked files. Validation
grants no authority to install applications, produce Track A assets, run RIFE,
freeze or publish data. Use local files and CPU only, no network, downloads or
new packages. Existing tests may import backend wrappers and use mocks; the test
guard prohibits real RIFE model import/inference.

Executable landmark metrics, annotation validation, sidecar validation and
accepted-version inventory validation remain future pre-inference work.
The following supplementary validation is future work, not implemented here:

1. Static document/template review: required eight sheet IDs, storyboard 0–7,
   a01/k=4, role restrictions, unresolved fields clearly marked; ensure proposed
   sidecars do not enter strict manifests. Implement any future schema tests
   using text/JSON only, with duplicate keys, nonfinite values, unknown fields,
   wrong actor, invalid indices, naive timestamps and bad hashes rejected.
2. On real artist assets, read-only file audit: RGB PNG 512×512 without alpha,
   exactly eight numerically ordered frames, distinct bytes and decoded pixels,
   all final/source/guide/declaration hashes and safe paths; unchanged originals.
   Inspect editable sources/dependencies and layer visibility manually in the
   installed tools only after authorization. Do not treat file existence as
   proof of redrawing.
3. Test provenance link failures, swapped guide/source revisions, mismatched D
   hash/path/k, missing rights scope, post-selection edits, absent manual-change
   history, timestamp inversions, symlinks and missing source files. Use in-memory
   record mutations for schema tests; any future image-level tests require an
   authorized real fixture and temporary copies, never fake primary drawings.
4. Run the existing read-only ingest CLI on available real assets with `--partial`;
   its `partial_ingest_only` result is not readiness. Full ingest is reserved for
   the complete six-A/four-D dataset. Neither mode grants freeze/inference.
5. Human review measures neutral proportions, sampled stroke widths, interior
   colors, foot anchors and elbow/wrist chord deviations. Report measurement
   method, uncertainty and exceptions. Check identity, face, hands, topology,
   lag, arc and authorship with evidence; software cannot certify these judgments.
6. Future validation report records CPU-only command/tool versions, code commit,
   input hashes, checks, failures, reviewer/time and scope. Preserve all failures;
   do not repair assets in a validator or resample/recenter to pass.

No current implementation enforces the supplementary record contract.
Any future implementation needs its own scoped review and tests before reliance.

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
