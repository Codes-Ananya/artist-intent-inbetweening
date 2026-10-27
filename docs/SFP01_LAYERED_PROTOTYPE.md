# SFP-01 bounded layered diagnostic

Run: `outputs/sfp01-layered-20261027T171613Z-e7e5f278`. Completed on CPU using existing NumPy, Pillow, OpenCV 5.0.0 and ffmpeg. No RIFE inference, GPU requirement, model change, downloaded dependency or silently substituted backend. Archived RIFE scale 1 remains the baseline; the completed scale-0.5 experiment remains a negative result.

## What was feasible

Inspection of approved frames 0 and 2 shows a bent arm overlapping the vest versus an extended arm across the torso. Neither gives a complete clean background plate: some shoulder/vest regions are covered in both. A small manually guided compositing diagnostic is feasible, but a defensible *anatomically correct interpolated pose* cannot be inferred from this cutout alone. This experiment tests whether explicitly putting opaque arm pixels in front of a separated torso avoids the characteristic fade. It does not test automatic recovery of motion or hidden artwork.

Implemented `LayeredPilotBackend` behind `InterpolationBackend`, deliberately restricted to one midpoint and 512×512 RGB input. `scripts/run_sfp01_layered.py` verifies the archived extra-breakdown baseline and approved input hashes, creates a fresh timestamped output directory, and replaces only frame 1. This is a diagnostic composite with additional manual information, not an equal-effort RIFE comparison. Four image inputs remain supplied (0,2,4,7); frames 3,5,6 are reused; frame 1 is manually composited.

## Exact processing and manual assumptions

1. Assistant manually traced approximate arm polygons in endpoint image coordinates. These are **not artist-approved masks** or automatic segmentation. Polygon vertices are recorded in source and `results.json`; raster masks are saved. Masks include outline/edge pixels and can miss fragments or include background.
2. Use frame 2 as the plate. Dilate its arm mask with a 5×5 kernel. Fill that removal area using frame-0 pixels only where outside the similarly dilated frame-0 arm mask. This uses 4,684 observed endpoint pixels. Their *visibility* does not establish that they are the correct hidden texture at the intermediate time; endpoint vest contours differ and registration is assumed.
3. Mark the remaining overlap as unknown: 916 pixels under these approximate masks. Fill using OpenCV Telea inpainting, radius 3. This is explicit estimated reconstruction, not recovered ground truth. It cannot reconstruct missing stylized boundaries reliably. The masks are not a guarantee that every hidden pixel has been identified.
4. Cut out the frame-2 arm and apply a fixed affine transform: pivot (216,218), OpenCV angle −15 degrees (clockwise in image appearance), scale 0.75. This assistant-selected placement is an exploratory proxy, not joint interpolation or an inferred midpoint. Scaling shortens the arm and hand; it does not conserve anatomy. There was one configuration, no sweep or iterative pose tuning.
5. Warp premultiplied RGB and alpha with bilinear sampling; composite over the plate. Use a hard rectangle `[160,190,370,295)` to replace the archived frame-1 region. Pixels outside this region are exactly the archived frame 1. Within it, stationary vest pixels also come from the constructed endpoint plate, so improvement cannot be attributed solely to the arm mask. Of the inpainted pixels, 356 are not fully covered by the transformed arm (alpha below 0.99).
6. Retain all other timeline frames and export eight-frame PNG/GIF/MP4 sequences at 8 fps. GIF delays alternate 120/130 ms. Endpoints are copied exactly, not reconstructed.

## Artifacts and results

All paths below are beneath the run directory:

- `frames_0_1_2.png`: paired input-transition comparison.
- `side_by_side/frame_0001.png`: full-size frame-1 comparison.
- `side_by_side/animation.mp4` and `animation.gif`: full sequence comparison.
- `candidate/`: all eight PNGs plus viewing exports.
- `layers/arm0_mask.png`, `arm2_mask.png`, `arm2_removal_mask.png`, `arm2_cutout.png`, `warped_arm_alpha.png`: segmentation and foreground evidence.
- `layers/observed_endpoint0_fill_mask.png`, `unknown_reconstruction_mask.png`, `exposed_reconstruction_mask.png`, `reconstructed_plate.png`, `roi_mask.png`: plate provenance and uncertainty.
- `results.json`: polygon vertices, transform matrix, settings, timing, input/code/output hashes, frame roles and preservation checks.
- `archive.sha256`: all artifacts and historical result record. Review is recorded here rather than modifying that record's `completed_pending_visual_review` status.

Observed from the ordered 0/1/2 comparison and reconstructed plate: the arm is solid and readable, and the large orange/green vest smear is largely absent. This is expected when a cutout is kept opaque; it does not demonstrate that interpolation was repaired. The prototype introduces a conspicuous white/dark shoulder seam, shoulder contour damage and a small residual speck near the old hand region. The plate visibly fails around the missing shoulder boundary. The arm/hand is shortened by the fixed scaling and does not establish an appropriate intermediate pose. The 0→1→2 sequence therefore still has pose/shape discontinuity; 2 onward is unchanged. Review was of still progression plus export decoding/timing, not real-time perceptual evaluation.

Processing time: **0.030379 s CPU**; recorded total **1.785934 s**, including export and preservation recheck, excluding initial snapshot/preflight and final metadata writing. Not comparable to GPU inference-only or historical run times. No artistic-intent preservation, algorithmic novelty, reference accuracy or production quality is established.

Verification passed: all 31 output hashes and 32 archive entries; input/code hashes; all supplied PNGs pixel-exact to inputs; only frame 1 differs; frame-1 pixels outside the ROI exact. Both GIF/MP4 sets decode to eight frames, one second, 8 fps. Snapshot of **5,813 preexisting regular files** in outputs and the local pilot (excluding pytest-temp and symlinks) has zero changes, including the scale negative result and Track A/D. See `SFP01_LAYERED_VERIFICATION.json`. This is preservation verification, not a new off-device backup.

## Decision and next step

Keep this as a limited diagnostic, not a replacement baseline. It demonstrates that manually separating and compositing an opaque arm can remove the fade in this region, while exposing the actual clean-plate and geometry problems. Do not hide those defects by repeated automatic inpainting/parameter adjustments.

Smallest useful next step is a manually reviewed shoulder/vest clean patch plus articulated arm placement, with edits stored separately and approved as exploratory artwork. A human-authored frame-1 pose may be simpler overall and avoids pretending that a single rigid cutout reproduces elbow motion. Neither refinement has been started. The concrete blocker to a convincing layered in-between is missing trustworthy shoulder/vest contours behind the arm together with an appropriate bent-arm intermediate shape; the current pixels and rigid transform do not supply either reliably.

Reproduction, only if another diagnostic run is wanted:

```bash
cd /home/ananya_anand/projects/animation-inbetweening
.venv/bin/python scripts/run_sfp01_layered.py
```

Runs on CPU; no special WSL GPU command needed. Every invocation creates a new directory and records its own evidence. Preserve the original run above when reviewing.

Validation: full existing-venv pytest suite **199 passed, 1 skipped in 34.98 s**. New tests cover endpoint immutability, exact outside-ROI preservation, explicit observed/unknown mask partition, no plate changes outside removal mask, deterministic output, and restricted input/count handling. Actual pilot PNG/GIF/MP4 exports completed and were independently decoded. `git diff --check` passed.

## Preservation at refined-result acceptance

The original layered run remains unchanged as the first diagnostic, including its shoulder seam, reduced-size arm, masks and reconstruction evidence. The user accepted the separately archived refinement only as an exploratory demonstration. Both are included in the verified supplementary backup described in `SFP01_ACCEPTED_BACKUP.json`; acceptance is bound to the refined output hashes in `SFP01_EXPLORATORY_ACCEPTANCE.json`. No new rendering or tuning occurred in the acceptance batch.
