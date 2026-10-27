# SFP-01 single layered refinement

Run: `outputs/sfp01-layered-refined-20261027T172313Z-f78a5da1`. One fixed refinement, one actual candidate run, no parameter sweep. CPU only, existing OpenCV/Pillow/NumPy/ffmpeg. Previous layered run `outputs/sfp01-layered-20261027T171613Z-e7e5f278` and RIFE scale-1 extra-breakdown baseline are preserved. Scale 0.5 remains a negative result; scale 1 remains the baseline.

## Manual changes and reconstruction

Implemented separately in `inbetween/layered_refinement.py` and `scripts/run_sfp01_layered_refinement.py`, retaining the first implementation unchanged. Interpolation remains behind `InterpolationBackend`. The new backend validates the same one-midpoint 512×512 RGB scope and starts from the first diagnostic's documented plate and arm masks.

- Restore an observed shoulder anchor from **frame 2** in an ellipse centered at (215,213), radii (15,19). This overwrites much of the defective inpaint seam with visible source artwork, including shoulder/arm pixels. It is not a recovered hidden clean vest plate or a newly approved pose.
- Replace rectangle `[334,234,363,255)` in the plate with **frame-0 background pixels** to remove the isolated mark missed by the original arm-removal mask. This small region was visually inspected as background in frame 0.
- Remove the original 0.75 scaling. Split the original arm mask into upper-arm and forearm pieces with complementary weights over x=244..256. Rotate the upper piece clockwise 40 degrees about (216,218), at scale 1. Rotate the forearm clockwise 10 degrees, also at scale 1, and translate its manually chosen elbow (252,240) to the transformed upper elbow (229.4363,257.9933). These are fixed assistant-selected joints/angles, not inferred motion. Source segments retain scale but the approximate elbow join can still distort perceived anatomy.
- Warp premultiplied colors and alpha with bilinear sampling. Normalize overlapping foreground colors by summed alpha and clip coverage at one; composite over the restored plate. Only replace the same frame-1 ROI `[160,190,370,295)`. No other frame changes.

The initial plate procedure attempted reconstruction in 916 pixels. After observed-pixel restoration/cleanup, **255 pixels still derive from that inpainting; 47 are not fully covered by the new arm** (coverage below 0.99). These counts follow approximate masks, not a guarantee that every uncertain hidden pixel is known or accounted for. The full original plate method remains nested in metadata; its original transform is provenance, not the new active arm transform. Inpainting remains an estimate. Observed patches may still carry endpoint appearance differences inappropriate to the actual midpoint.

All original masks are retained in `layers/`. Additional files: `shoulder_observed_restore_mask.png`, `background_cleanup_mask.png`, `upper_source_alpha.png`, `forearm_source_alpha.png`, `warped_upper_alpha.png`, `warped_forearm_alpha.png`, `refined_arm_alpha.png`, `refined_plate.png`, `remaining_reconstruction_mask.png`, `refined_exposed_reconstruction_mask.png`. `results.json` records both matrices, manual choices, source hashes, code hashes, timing and preservation checks.

## Comparison and limitations

Inspected the native-size three-way frame-1 comparison and ordered frames 0–2. Columns are archived RIFE scale 1, first manual layer, and this refinement. The shoulder's dark/white break is substantially reduced, the isolated background mark near the former hand is absent, and the hand/arm no longer looks uniformly shrunk by 25%. The arm stays opaque and vest remains clearer than the fading RIFE baseline.

There is still an overly rounded/blocky elbow transition with soft color/contour overlap, and the shoulder outline is not seamless. The visible arm length is not proof of anatomically correct articulation. Frame 0 still goes from a hand near the waist to a much more forward hand in one step; vest/shoulder silhouette also changes. Abruptness is therefore not resolved or quantitatively measured. Frame 1→2 is more readable as a bent-to-extended arm, but the trajectory and timing are manually imposed. Review is ordered stills plus media decoding/timing verification, not real-time perceptual evaluation. No motion-quality or artist-intent validation is established.

This is a manually guided local edit with extra annotation and patch choices, not an automatic model improvement, ground truth, or algorithmic novelty. Stop here after the requested one refinement. No follow-up parameter changes or artwork were made after inspection.

## Exact artifacts

Under `outputs/sfp01-layered-refined-20261027T172313Z-f78a5da1`:

- `frames_0_1_2.png`: three-way 0–2 comparison, 1536×1680.
- `side_by_side/frame_0001.png`: native-size three-way frame 1.
- `side_by_side/animation.mp4` and `animation.gif`: full eight-frame motion preview, 1536×560, 8 fps.
- `candidate/`: unchanged supplied frames and reused frames, refined frame 1, GIF and MP4.
- `layers/`: masks, cutout, original and refined plates, reconstruction provenance.
- `results.json` and `archive.sha256`: immutable execution evidence. Visual review recorded in this document, leaving historical status unchanged.

CPU processing **0.053476 s**; recorded total **2.423050 s**, including export and preservation recheck but excluding initial snapshot/preflight and final metadata writing. This is not a GPU benchmark. Existing-input/manual-edit budgets differ from automatic RIFE.

Verified all **41 output hashes / 42 archive entries**, code/input hashes, original supplied pixels and independent comparisons against both earlier timelines: **only frame 1 differs**. Frame 1 outside the ROI remains pixel-exact to RIFE. Both GIFs decode to eight frames / 1000 ms (120/130 ms alternating), both MP4s fully decode to eight frames at 8 fps / one second. Snapshot of **5,846 preexisting pilot/output files**, excluding pytest-temp and symlinks, has zero changes. Track A/D, first layered result, scale experiment and original inputs remain untouched. Details: `SFP01_LAYERED_REFINEMENT_VERIFICATION.json`.

No GPU command is needed. Reproduction, if explicitly desired later: `.venv/bin/python scripts/run_sfp01_layered_refinement.py` from the repository root creates another fresh directory. No rerun is needed to review the current result. New code/docs remain local and uncommitted in this task.

Validation: full pytest suite **200 passed, 1 skipped in 37.03 s**. Added test checks original/returned endpoint immutability, outside-ROI equality, unit-scale rotation matrices, exact observed-patch sources and reconstruction-mask exclusions. Actual sample exports and independent decoding checks passed. `git diff --check` passed.

## User acceptance and preservation

The user subsequently accepted this exact refined result as an **exploratory demonstration**, explicitly retaining disclosure of manual interventions and remaining elbow/transition limitations. Hash-bound record: `docs/SFP01_EXPLORATORY_ACCEPTANCE.json`. This does not upgrade it to ground truth, automatic intent preservation or the default baseline. Both layered archives, masks and reconstruction records are retained unchanged; their execution statuses remain historical. Verified supplementary local backup: `docs/SFP01_ACCEPTED_BACKUP.json`. The earlier uncommitted-state statement describes the pre-acceptance task; this acceptance batch commits the code/tests/reports and attempts the authorized branch push.
