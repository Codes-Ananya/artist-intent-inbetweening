# Track A character specification template

Approved planning specification template — not a completed artist declaration
or production record.
Copy into the ignored source archive during separately authorized production. `TO_RECORD` means
unresolved; never substitute invented dates, hashes, approvals or measurements.

| Field | Approved value or item to complete |
| --- | --- |
| Character | Asha |
| character_id | track-a-asha-v1 |
| Design | Original modern Indian young woman |
| Sole authoritative artist | Ananya Anand |
| Compliance reviewer / annotation collaborators | Samiksha Prasad: compliance reviewer, reference-landmark verifier and primary randomized, method-hidden model-output annotator; no drawing edits |
| Artistic intent / reference landmarks | Ananya Anand; reference creator; adjudicates only documented ambiguous cases after Samiksha’s initial output annotation |
| Specification revision / actual recorded_at | TO_RECORD |
| Approval person / actual approved_at / evidence | TO_RECORD |
| Height/canvas | Approximately 70%; fixed 512×512 |
| Style | Approximately 5 px dark line, minimal/no shading, off-white background |
| Silhouette/clothes | Braid over anatomical left shoulder; asymmetrical knee-length kurta; tapered trousers; sneakers; one plain anatomical left-wrist bracelet |
| Face | Minimal readable eyes, eyebrows, nose and mouth |
| Excluded | Scarf, waistcoat, decorative pattern, additional jewelry |
| Palette families | Muted teal kurta; charcoal trousers; warm cream sneakers; muted rust bracelet; deep brown/charcoal hair and line |
| Exact sRGB swatches / skin / profile | Kurta #477F7A; trousers #3B3D40; sneakers #E9DDC6; bracelet #A86347; line work and pupils #302B29; hair fill #59443B; skin #B98262; background and eye whites #F5F1E8; mouth interior/lip accent #A86347; sneaker soles may reuse #E9DDC6; exact profile TO_RECORD; flat interiors exact, antialiasing exempt |
| Braid side / segment count / root / length / tip construction | Anatomical left shoulder; 2.0U ±5% review guidance; five simplified visible woven sections permitted, independent of braid_root → braid_01 → braid_02 → braid_tip controls; actual attachment/tip construction TO_RECORD |
| Bracelet anatomical wrist / width | Anatomical left; total visible band thickness approximately 5 px; single rust band, no separate 5 px dark outline; consistent silhouette/placement |
| Kurta long-hem side / hem difference / slit count / sleeve / neckline | Anatomical left longer by 0.2U; two side slits; three-quarter sleeves; round neckline with short center slit |
| Hand shape vocabulary and anatomical thumb rule | TO_RECORD |
| View angles / facial guides / perspective exceptions | Neutral standing, arms approximately 10° from torso; side faces screen-right; three-quarter approximately 45°; three-quarter back exposes anatomical left; visibly establish left braid/bracelet/longer hem, opposite-side detail only if ambiguous; eye/nose/mouth at 0.48U/0.67U/0.79U downward from crown (U=head height), subject to approved perspective guidance; anatomical L/R labels; actual facial measurements/perspective exceptions TO_RECORD |
| Neutral measured proportions / pivots / approved tolerances | Initial H=358 px, exact U=H/6; crown approximately y=77, soles approximately y=435, centerline x=256; derive final measurements/pivots from Ananya’s approved coherent sheet; detailed tolerances are review guidance, actual measurements TO_RECORD |
| Origin and rights declaration / evidence / permitted uses | Local research/evaluation, publication figures and portfolio demonstration permitted; redistribution not currently authorized; no broader legal conclusion; actual declaration, origin/references and evidence TO_RECORD |
| Synfig/Krita versions / rig creator and origin | TO_RECORD when actually used |

Required asset register (one row each): front, three-quarter front, side,
three-quarter back, back, neutral face sheet, hand guide, braid guide.
Each row records sheet ID, revision, editable path/SHA-256, flattened path/SHA-256,
artist, actual creation/edit times with timezone, measurements, review status,
approver/time/evidence. Retain prior revisions and record supersession reasons.
Face/hand/braid sheets may contain multiple labeled examples on their fixed
canvas; Ananya alone controls authoritative layers; Samiksha’s annotations belong to
separate review copies/sidecars, never the authoritative `.kra`.

Keep the eight listed sheets; do not add another expression sheet unless the trial
demonstrates a need. Approved a01 staging, hard gates and review-only numeric
guidance are in [PRODUCTION_PLAN.md](PRODUCTION_PLAN.md). All eight primary
landmarks and their visibility must be recorded; Ananya creates references and
Samiksha verifies them, with resolution and freeze before inference. Actual
landmarks, approvals, dates and signatures are not supplied by this template.

Paired scoring eligibility comes only from authoritative reference visibility at
each index: exclude reference-invisible/occluded points from both methods and
report exclusions. Reference-visible points remain eligible for both methods;
unidentifiable outputs, including output-only occlusion, receive the existing
image-diagonal penalty, never a mask exclusion. Preserve raw reference/output
statuses and report coverage failures as specified in the
[protocol](../REAL_INPUT_PILOT_PROTOCOL.md). Samiksha annotates randomized,
method-hidden outputs and cannot choose the mask from perceived method quality.
Metric implementation and executable annotation validation remain pre-inference
work; this template implements neither.

Braid/hair construction lines use #302B29 over #59443B. No additional swatch
may be introduced during a01 production; any palette change requires prospective
documentation and approval before a01 guide/frame production begins. Fixed
identity/design decisions and palette are hard gates; numeric proportion
tolerances remain review guidance unless a separate hard gate explicitly says
otherwise. Preserve the approved a01 three-quarter view; keep the left braid
visible where naturally possible and report braid-tip coverage under the
reference-only eligibility rule.

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
