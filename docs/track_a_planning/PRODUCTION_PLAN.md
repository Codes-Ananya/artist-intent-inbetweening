# Track A production plan — researcher-approved planning decisions

Planning only, 2026-09-23. No production, dataset acceptance, freeze or inference
is authorized by this document. The researcher approved the planning package and
final decisions below. Numeric artistic tolerances are review guidance, not
automatic rejection criteria. Production evidence remains unpopulated. Base branch: `feature/real-input-pilot`,
`0581f5c23515c30a53e8cdb61712a144cb09c3cc`.

## Authority and scope

Ananya Anand is the sole artist of every authoritative Track A drawing, including
model sheets and all eight frames, artistic-intent authority and reference-landmark
creator. Samiksha Prasad is protocol-compliance reviewer, reference-landmark
verifier and primary model-output annotator using randomized, method-hidden
outputs. Ananya adjudicates only documented ambiguous landmark cases after
Samiksha’s initial annotation. Samiksha must not modify authoritative drawings. Synfig Studio supplies construction guides. Ananya manually
redraws and cleans every authoritative frame in Krita. Raw rig exports never
qualify as final artist-authored data. Preserve guides, editable sources and
flattened final PNGs. No AI-generated drawing belongs in Track A.

This plan specializes the provisional Track A character in the parent protocol:
Asha replaces the jacket/scarf/boots design for Track A only. It does not revise
Track D, its assets, provenance, approvals or inference status. The approved eight-landmark
Track A amendment below replaces scarf/boot/cuff wording for Track A only; it is
a protocol definition, not an implemented metric. Track D remains unchanged.

## Character and model-sheet controls

Use [CHARACTER_SPEC_TEMPLATE.md](CHARACTER_SPEC_TEMPLATE.md) to record the final
artist-approved choices. Required material: front, three-quarter front, side,
three-quarter back, back, neutral facial-expression sheet, simplified hand-shape
guide, and braid construction/length guide. Each view has its own 512×512 sheet;
retain editable sources and labeled measurement/review copies separately.
Use a neutral standing pose with arms approximately 10 degrees away from the
torso. The side view faces screen-right; three-quarter views are approximately
45 degrees. Orient the three-quarter back view to expose the anatomical left
side. The sheets must visibly establish the left braid, left bracelet and longer
left kurta hem; add an opposite-side detail only if these are not unambiguous.
Annotate anatomical left/right, never infer them from screen direction.
Do not add another expression sheet unless the trial demonstrates a need.

Approved identity: Asha, `track-a-asha-v1`, original modern Indian young woman;
braid over anatomical left shoulder; asymmetrical knee-length kurta, longer on
anatomical left by 0.2U, three-quarter sleeves, simple round neckline with short
center slit and two side slits; tapered trousers; sneakers; one plain anatomical
left-wrist bracelet with approximately 5 px total visible band thickness; minimal readable
eyes, eyebrows, nose and mouth. No scarf,
waistcoat, decorative pattern or additional jewelry. Deep brown/charcoal
line work, with distinct brown hair fill; muted teal kurta; charcoal trousers; warm cream sneakers; muted
rust bracelet; off-white background; minimal/no shading; approximately 5 px line.

Initial construction guidance uses neutral standing height H=358 px (69.9% of 512)
and exact head unit U=H/6 internally to avoid accumulated rounding errors. Measure
crown-to-sole excluding flyaway hair. Neutral model-sheet crown approximately
y=77, sole baseline approximately y=435, body midline x=256. These are model
sheet anchors, not per-frame alignment operations. Pixel origin is top-left,
x right and y down. Pose perspective can shorten projected lengths.

| Control | Initial target / review guidance |
| --- | --- |
| Neutral height | 358 ± 5 px in all standing turnaround views |
| Head height; frontal width | U; 0.72U, each ± 3% against approved sheet |
| Shoulder breadth; pelvis breadth (front) | 1.35U; 1.05U, each ± 5% |
| Shoulder, waist, hip, knee, ankle y | crown + 1.25U, 2.5U, 3.1U, 4.5U, 5.7U; ± 0.08U in neutral views |
| Upper arm; forearm; hand length | 1.05U; 0.90U; 0.60U, ± 5% in comparable unforeshortened poses |
| Sneaker sole length | 0.85U ± 5% in side view |
| Kurta low/high hem | crown + 4.5U / 4.3U; anatomical left is longer by 0.2U |
| Braid root-to-tip centerline length | 2.0U ± 5%; projected straight distance may vary |
| Facial neutral guides | eye line 0.48U, nose 0.67U, mouth 0.79U downward from crown, U=head height; ± 2 px in matching views, subject to approved perspective guidance |
| Stroke width | nominal 5 px; sample 10 ordinary contour locations, median 4–6 px; review joins/tapers separately |

These tolerances trigger inspection, not automatic artistic rejection. Approve a
coherent model sheet and derive final measurements from it; do not independently
force landmarks into incompatible positions. The visible braid may use five
simplified woven sections, independent of rig-control count. Record actual braid
attachment/tip construction, facial spacing and hand vocabulary in that sheet.
The hand sheet covers relaxed, anticipation, bent-wrist reach and extended reach,
with thumb side and a consistent simplified finger-group construction. The braid
sheet shows root, segment overlaps, tip and centerline measurement across bends.

Approved sRGB swatches: kurta #477F7A, trousers #3B3D40, sneakers #E9DDC6,
bracelet #A86347, line work and pupils #302B29, hair fill #59443B,
skin #B98262, background and eye whites #F5F1E8, mouth interior/lip accent
#A86347; sneaker soles may reuse #E9DDC6. Braid/hair construction lines use
#302B29 over #59443B so they remain visible.
Flat interior colors must equal the approved
8-bit RGB swatches; anti-aliased boundaries are exempt. No additional swatch may
be introduced during a01 production. Any palette change must be prospectively
documented and approved before a01 guide/frame production begins.
The bracelet is a single rust-colored band without a separate 5 px dark outline;
keep its silhouette and placement consistent.

## Synfig guide puppet specification

This is a conceptual local rig design, not an application installation or a
claim about a particular installed version. Record actual version and supported
control implementation when production is separately authorized.

Visual groups: background/reference grid; far sneaker, lower/upper leg; far hand,
forearm and upper arm/sleeve; rear braid; pelvis/trousers; kurta rear hem/body/front
hem; neck; head/ears/face/hair cap; near upper arm/sleeve, forearm/hand; near leg and
sneaker; left-wrist bracelet; optional front braid. Every visual part has separate fill and
outline guides. Hands/face may use pose-specific guide replacements.

Default back-to-front stack: background/grid → far leg/shoe → far arm/hand →
rear braid → near leg/shoe → pelvis → rear hem → torso/kurta/front hem → neck →
head/face/hair → near arm/hand → front braid. Attach the bracelet to the anatomical
left wrist in its actual occlusion group, not automatically to the near arm. Braid uses one visible
representation, not two copies. Record per-pose occlusion exceptions; anatomical
L/R names stay fixed when near/far visibility changes. Legs remain behind kurta.

```text
world (fixed canvas; no animated scale, rotation or translation)
├── foot_target_L (fixed ground contact)
├── foot_target_R (fixed ground contact)
└── pelvis_root (small body weight shift; constrained by planted feet)
    ├── hip_L → thigh_L → shin_L → foot_L
    ├── hip_R → thigh_R → shin_R → foot_R
    ├── spine → chest
    │   ├── clavicle_L → upper_arm_L → forearm_L → hand_L
    │   ├── clavicle_R → upper_arm_R → forearm_R → hand_R
    │   └── neck → head → braid_root → braid_01 → braid_02 → braid_tip
    └── kurta_waist → hem_L / hem_center / hem_R
```

World foot targets are constraints, not second parents. Solve leg placement
manually if the chosen local tooling cannot express constraints. Pivot points:
pelvis at hip midpoint, hips at femur sockets, knees at bend centers, ankles at
shoe articulation, shoulders at sleeve/arm sockets, elbows at bend centers,
wrists at hand base, neck at skull base, braid root at approved hair attachment,
hem controls at garment seams/free edge. Store each neutral pivot (x,y) against
the approved sheet, and record front/back order per frame.

Head drives braid root; successive braid controls supply pose-specific,
artist-authored lag, with approximately conserved centerline length. The visible
five-section weave is independent of the braid_root → braid_01 → braid_02 →
braid_tip controls. Hem controls follow waist with pose-specific, artist-authored
lag; 6 px relative to the body-following guide is a review indicator, not a hard
maximum. Preserve two side slits, side seams and left-longer hem asymmetry.
Do not impose a universal one-frame delay on braid or hem.
No automatic simulation is necessary. Root shift must not drag either foot.

Ananya redraws all final outlines and fills. In particular, do not treat deformed
guide eyes, mouth, hands/fingers, bent elbow/knee outlines, sleeve intersections,
braid overlaps, shoe contacts, bracelet ellipses or kurta folds/hem joins as
finished contours. Resolve occlusion and line thickness manually. The guide
puppet is never the authority for topology or artistic timing.

## Krita source and export workflow

Document settings: 512×512, RGB with alpha editing support, 8-bit integer
channels, sRGB profile; record exact profile name and application version. Use
one editable `.kra` per authoritative frame. Final export is RGB without alpha,
not RGBA with all alpha values opaque. No canvas resize, crop, rotation or
per-frame recentering. Layer stack, top to bottom:

```text
90_artist_notes                 Ananya-controlled; hidden on export
80_artist_landmark_overlay      Ananya-controlled; hidden on export
70_final_lines                  Ananya's clean strokes
60_final_colors                 Ananya's flat fills; named palette sublayers
40_artist_rough                 hidden on export; retained
20_synfig_guide                 locked, 20–30% opacity; hidden on export
10_registration_grid            locked; hidden on export
00_background_offwhite          opaque, locked
```

Keep final lines/colors at 100% layer opacity. Use nominal 5 px contour strokes
with clean joins, intentional taper and no accidental gaps, doubles or guide
remnants. Do not erase roughs or guides from the retained source. Record manual
changes per frame, not a blanket assertion that cleanup occurred.

Save a new numbered source revision, inspect at 100% and fit-to-canvas, hide all
nonfinal layers, verify the opaque background, and export a separate numbered
flattened PNG. Select an export path/settings that omit alpha and preserve sRGB
colors; independently inspect decoded mode, size and format. If the chosen
version exports RGBA, retain it as an intermediate and record any explicit
alpha removal/compositing conversion and hashes; never silently convert it into
an authoritative file. Reopen the export to check missing layers or color shifts.
Hash the closed/saved `.kra`, guide, Synfig source and exported PNG for the
immutable sidecar; hash canonical copies later in the accepted-version inventory.
Retain every accepted source revision and its dependency files. Never overwrite
an accepted revision; pre-exposure corrections create a new one with reason and review.

## a01 storyboard and timing intent

Approved: `curved_arm_reach`, eight authoritative frames 0–7, A=0, D=4, B=7,
k=4. Ananya selected frame 4 for the strongest intentional curved motion arc,
before model results. Equal sample times are t=i/7; motion spacing supplies
anticipation/acceleration/settling. Preview playback is 8 fps; optional endpoint
holds are review-only and cannot change formal timing, k or evaluation timestamps.
Right means anatomical right. Use a three-quarter front view, anatomical right
arm near/reaching, and a screen-right reach.

| Frame | t | Approved pose and timing intention |
| --- | --- | --- |
| 0 (A) | 0 | Neutral standing; right arm relaxed; gaze toward target; establish balance |
| 1 | 1/7 | Small anticipatory shift away; shoulder lowers slightly; delayed onset |
| 2 | 2/7 | Torso begins returning; shoulder initiates reach; proximal motion leads |
| 3 | 3/7 | Elbow rises on curved path; wrist/hand lag; develop curvature |
| 4 (D) | 4/7 | Strongest curved silhouette; bent elbow, trailing wrist and braid |
| 5 | 5/7 | Forearm extends; torso commits toward target; release extension |
| 6 | 6/7 | Hand approaches target; slight overshoot begins settling |
| 7 (B) | 1 | Stable final reach; readable hand and balanced stance |

Select and lock exact foot-contact coordinates from Ananya’s approved neutral
a01 layout; do not invent coordinates before that layout exists. Feet have zero
intended sliding; variation above 2 px is a review flag, not authorized movement.
Lock target coordinates before guide production. The target is invisible in
authoritative PNGs; its marker exists only on hidden guide/review layers.
No camera motion, canvas motion or per-frame recentering. Braid and kurta hem use
pose-specific artist-authored lag without changing topology. Hands remain
simplified and structurally consistent. Keep the left braid visible where naturally
possible, but do not alter the approved three-quarter view merely to maximize
landmark coverage. Authoritative-reference visibility governs eligibility; report
braid-tip coverage, including reference exclusions and output penalties.

For the D review, annotate elbow/wrist positions and compare frame 4 with the
endpoint chord at t=4/7, also viewing the geometric halfway pose at t=1/2. This
is a manual/geometric review, not an interpolated image or model result. Review
indicator: assess whether at least one right elbow/wrist landmark is ≥10 px
from its t=4/7 chord position, with readable curvature and wrist lag. This is a screening aid only:
a displacement alone cannot prove intent or good silhouette. Ananya must confirm
meaningful departure from a linear halfway pose and the intended curved arc.

## Trial gates and admission decision

Every gate records pass / rework / blocked / rejected, frame references, evidence, reviewer,
actual review timestamp and reason. Rework actions below apply only before model
exposure; afterward follow the no-repair policy. No weighted aggregate can hide a hard failure.

| Gate | Evidence and action |
| --- | --- |
| Identity/proportions | Fixed identity/design decisions are hard gates in all eight frames; approved views guide review; numeric proportion tolerances remain documented review guidance unless a separate hard gate explicitly says otherwise; record perspective exceptions and reasons |
| Topology | Stable limb count, anatomical sides, joints, braid attachment, garment seams/slits; impossible connections or unexplained swapping require rework |
| Lines/palette | Review contours at 100%; use stroke sampling and interior swatches above; accidental gaps, double lines, color drift or guide residue require rework |
| Face/hands | Required visible features, gaze, thumb orientation and simplified construction agree with sheets; hidden features explicitly occluded, not accidentally omitted |
| Braid/clothing | Constant design/length construction, readable lag, one bracelet, fixed hem asymmetry; no new ornamentation or changing topology |
| Motion arc | Storyboard poses, proximal-to-distal initiation, frame-4 curvature and final balance readable; human review plus geometric flag, no model comparison |
| Fixed framing | Exactly 512×512; world/camera transforms fixed; zero intended foot sliding; variation above 2 px from frame 0 per visible contact is a review flag; investigate antialias/annotation uncertainty without registration |
| Completeness | Exactly eight distinct canonical RGB PNGs indexed 0–7; no alpha, missing frame, copied hold or rig export substituted for drawing |
| Authorship/provenance | All final drawing edits by Ananya; complete source/guide links, revisions, actual times, verified hashes, manual-change descriptions and rights evidence; unknown required evidence blocks admission |
| Pre-results selection | k=4, frame identity/hash bound and signed before any model output; original prospective choice retained; exposure or post-result selection blocks primary admission |

Hard gates: fixed identity/design decisions; exactly eight frames indexed 0–7; a01 A=0, D=4, B=7, k=4;
512×512 RGB PNG without transparency; approved palette (antialiasing exempt);
Ananya-only authoritative drawing authorship; complete guide/source/export
provenance and hashes; D/k locked before model results; fixed camera and no
per-frame recentering; no clipping; required rights and approval records.

Review guidance only: proportion tolerances, median stroke range 4–6 px,
foot-contact variation flag above 2 px, canvas margin 12 px, curvature indicator
10 px, and hem-displacement indicator 6 px. A smaller intentional margin needs
recorded review. These are not automatic artistic rejection gates or permission
to normalize/recenter canonical pixels. Qualitative judgments remain attributed
human judgments; no numeric threshold claims perceptual validation.

Local drawing, palette, export or clipping defects require documented rework
before model exposure. Missing recoverable records block admission until supplied.
A changed creative premise requires a prospective documented amendment.
Prohibited authorship, post-result D/k selection or model-informed frame
replacement rejects the sequence from primary eligibility. There is no arbitrary
retry limit. Preserve complete revision history, including rejected revisions.

Admission procedure:
1. Planning decisions are approved; production remains a separate task. Complete
   the real model-sheet/layout measurements and records when they exist. Assets
   may be created only under separate production authorization.
2. Ananya completes model sheets and a01, records all revisions and self-reviews.
   Samiksha reviews compliance without drawing edits; separately log annotation.
3. Review all gates before model exposure. Rework only for documented production
   defects against this plan; keep the same a01 motion and k=4. Retain rejected
   revisions and reasons; no best-of-many model-based selection.
4. Bind the final frame-4 hash and eight-frame revision bundle, complete rights
   and provenance, and run future CPU-only checks. A failed/blocked gate prevents
   admission. A changed creative premise requires a prospective reviewed amendment,
   not silently relabeling a different trial a01.
5. Ananya signs artistic acceptance; Samiksha records compliance verification,
   and the admission approval/signatures are recorded when actually given. Record
   `accepted_for_track_a`, revision/hashes and rationale. Follow the one-way
   dependency contract in [records](RECORDS_AND_VALIDATION.md): immutable sidecars,
   gate review, selection binding, admission, then accepted-version inventory.
   Record canonical-copy hashes only in the downstream inventory.
   A passing trial occupies the final a01 slot once, not a seventh sequence.
6. a02–a06 require separately approved motion/selection records with the same
   character. a01 admission is neither a dataset freeze nor inference permission.
   Full six-sequence and existing complete-dataset gates remain mandatory.

## Track A landmarks and annotation roles

The eight primary landmarks are: nose tip; anatomical left elbow; anatomical
right elbow; anatomical left wrist/hand-base center; anatomical right wrist/hand-base
center; anatomical left sneaker toe; anatomical right sneaker toe; braid free tip.
This replaces scarf/boot/cuff-specific wording for Track A only. Track D is unchanged.

Ananya creates reference landmarks; Samiksha verifies them. Resolve reference
annotations and freeze them before inference. Samiksha is the primary model-output
annotator using randomized, method-hidden outputs. Ananya adjudicates only
recorded ambiguous cases after Samiksha’s initial annotation; retain initial and
adjudicated records with reasons. Samiksha does not modify authoritative drawings.
Paired landmark eligibility is determined only by the authoritative Track A
reference frame at that timeline index. Reference-invisible or genuinely
reference-occluded landmarks are excluded from both methods’ positional scores;
retain and report reference visibility and exclusions. Do not estimate hidden
reference positions. Reference-visible landmarks remain eligible for both methods:
use identifiable output coordinates normally; missing, malformed, merged, severed
or otherwise unidentifiable output landmarks receive the existing image-diagonal
penalty sqrt(512²+512²) pixels for that method. Output-only occlusion absent from
the reference is a generated-result failure/behavior: record its category and
apply the penalty, without changing either method’s evaluation mask.

Preserve raw reference and per-method visibility/status records. Report total
reference-visible eligible landmarks, valid-coordinate counts per method,
penalized missing/unidentifiable counts per method (including output-only
occlusion), reference-occluded/invisible exclusions, and per-landmark coverage and
error. A sequence/index with no reference-visible eligible landmarks contributes
no landmark score and must remain reported as a coverage failure in aggregate
reporting, never silently dropped or assigned zero error. Counts describe
landmark/index observations in the scored set E defined in the parent protocol.
Samiksha’s annotations remain randomized and method-hidden; the shared mask is
fixed from references, never chosen from perceived output quality or changed by
output adjudication. Finalize operational status/blinding rubrics and records
before execution. Metric implementation and executable annotation validation
remain pre-inference work; the reference-only mask rule itself is approved.

## Approved usage scope and remaining factual records

Permitted Track A uses: local research and evaluation, publication figures and
portfolio demonstration. Dataset redistribution is not currently authorized.
Authorship and usage authority do not assert a broader legal conclusion. Retain
the actual rights declaration, evidence, approval records and signatures when
created; these approved scope decisions are not fabricated production evidence.

Tool versions, exact profile/export settings, rig origin/dependencies, hashes,
timestamps, paths, revisions, measured model-sheet construction/pivots, actual
foot/target coordinates, annotation records, approvals and signatures remain
unpopulated until real events occur. Actual a01 foot/target coordinates are layout
facts to be locked before guide production, not open design-policy choices.
The a02–a06 motions/timing and remaining parent-protocol evaluation/freeze work
remain outside this a01 planning approval. No dataset is frozen by this document.

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
