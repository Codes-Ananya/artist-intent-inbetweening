# SFP-01 extra-breakdown comparison — execution status

The user approved the prepared frame-2 candidate on 2026-10-27. Approval is bound to SHA-256 `b55d945b5575f8b8d26688722029100b95d25299531d94616558349dfd66ce9f` in `.local/real_input_pilot/synthetic_pilot/sfp_01/extra_breakdown_approval_r001/approval.json`. Minor hand shape/proportion and vest contour differences are accepted input limitations; possible resulting motion discontinuities remain to be evaluated.

Attempt `outputs/sfp01-extra-20261027T040056Z-7fd2e88d` stopped at the CUDA gate: `RifeError: CUDA is unavailable to this process. Run the GPU smoke test in a normal WSL shell with RTX 4050 access.` No RIFE inference, backend substitution or viewing exports occurred. No comparative quality, runtime or memory result is available. The failure and approval are preserved separately from all prior evidence.

| Condition | Supplied frames | New inference | Historical generated frames |
| --- | --- | --- | --- |
| Archived three-input RIFE | 0, 4, 7 | None | 1, 2, 3, 5, 6 |
| Planned four-input condition | 0, 2, 4, 7 | Only 1, 3 | Reuse baseline 5, 6 |

Both retain eight frames at 8 fps. Frame 2 is generated in the baseline and supplied in the treatment. Compare generated slots 1 and 3 and sequence continuity; improved appearance of supplied frame 2 is not an interpolation-quality result. The comparison tests an unequal-input exploratory workflow, not a novel algorithm or artist-intent validation. Independent motion accuracy cannot be established without references, nor artist intent without artist review.

The runner verified baseline archive integrity and unchanged input hashes. All 194 preexisting files in the candidate's preservation snapshot still match, including pilot/Track A/D evidence, baseline outputs and Track A planning documents. Saved treatment pixel preservation remains untested because no treatment was generated.

Run this exact command in the normal WSL terminal:

```bash
cd /home/ananya_anand/projects/animation-inbetweening
.venv/bin/python scripts/run_sfp01_extra_breakdown.py \
  --frame2 .local/real_input_pilot/synthetic_pilot/sfp_01/extra_breakdown_f002_r001/frame2_prepared.png \
  --approval .local/real_input_pilot/synthetic_pilot/sfp_01/extra_breakdown_approval_r001/approval.json
```

Omitting `--output` creates a new timestamped UUID directory and prints its exact path on success. Do not reuse the failed directory. Expected files beneath that new directory are `side_by_side/animation.mp4`, `side_by_side/animation.gif`, `labelled_contact_sheet.png` and `results.json`. These files do not yet exist for this experiment. The completed output must be inspected before reporting comparative visual findings.

Exact current evidence paths:

- Failed results: `/home/ananya_anand/projects/animation-inbetweening/outputs/sfp01-extra-20261027T040056Z-7fd2e88d/results.json`
- Failed archive manifest: `/home/ananya_anand/projects/animation-inbetweening/outputs/sfp01-extra-20261027T040056Z-7fd2e88d/archive.sha256`
- Approval: `/home/ananya_anand/projects/animation-inbetweening/.local/real_input_pilot/synthetic_pilot/sfp_01/extra_breakdown_approval_r001/approval.json`
- This report: `/home/ananya_anand/projects/animation-inbetweening/docs/SFP01_EXTRA_BREAKDOWN_EXECUTION_REPORT.md`

## Completed normal-WSL run review — 2026-10-27

This addendum supersedes the pending execution statements above; the earlier failed attempt remains historical evidence. Inspected exactly `outputs/sfp01-extra-20261027T041321Z-539ba9c6` without rerunning inference. Its immutable results status remains `completed_pending_visual_review`; this separate addendum records assistant review, not user acceptance.

Independent verification passed: all 21 output hashes, 22 archive entries including results.json, four input hashes, approval hash, four recorded code hashes, and all 32 baseline archive entries. Decoded PNG pixels at supplied 0,2,4,7 and reused 5,6 exactly match sources. Earlier preservation snapshots (152 and 194 files) have zero mismatches. Machine-readable details: `docs/SFP01_VERIFICATION_20261027.json`.

Both treatment and comparison have eight PNGs, eight-frame GIFs with alternating 120/130 ms delays (1,000 ms total), and fully decodable eight-frame MP4s at 8 fps for 1.000 seconds. Dimensions are 512×512 and 1024×560 respectively. PNGs are authoritative; viewing formats are quantized/lossy.

Historical diagnostics report RTX 4050 Laptop GPU, CUDA device `cuda:0`, float32 for both midpoint calls, native 512×512 with no resize/padding. Only frames 1 and 3 were inferred. Free VRAM before generation: 5,321,523,200 bytes; total: 6,438,780,928 bytes. Peak allocated PyTorch CUDA memory: 194,312,704 bytes (not total device usage). Summed inference 0.601373 s; new-generation wall 2.580614 s; total recorded wall 8.326731 s. Source commit `5d8adbdd40e12c2c8f91930eff838aebe561c086`, checkpoint SHA-256 `9f9e2e8b5c3fef311c9a782aa17a30f87c388ce6dc9c00e4993eba3d3941d3cb`. These are recorded execution facts, not a fresh CUDA probe or controlled speed comparison.

Visual review used the full eight-frame PNG comparison sheet plus native-size paired frames 1 and 3, with export decoding/timing checks. It was not real-time playback or a human perceptual study.

- Frame 1 remains defective: a translucent extended forearm/hand overlaps the bent arm, and orange vest/shoulder contours smear. The treatment hand is more visible than baseline's very faint ghost, but neither is a clean solid articulated intermediate; no convincing overall frame-1 improvement.
- Frame 3 improves visibly: treatment has a solid green forearm, much clearer fingers and shoulder/vest contours. Baseline remains translucent, ragged and smeared. Treatment hand outlines are still softer than supplied poses.
- Across the full motion, treatment resolves to a crisp reach sooner at supplied frame 2, making the transition from defective frame 1 to frame 2 conspicuous. Frames 2→3→4 form a more coherent extension, with residual outline softness. Frames 4→7 are identical to baseline and retain its relatively coherent downward settle; there is no new improvement in that segment. Head, torso, tail and feet appear broadly stable at inspected scale. GIF wrap 7→0 is a reset, not an interpolated return.

Budgets are unequal: baseline supplies 0,4,7 and historically generates five frames; treatment supplies 0,2,4,7, newly generates 1,3 and reuses 5,6. Frame 2 is supplied, never a generated quality win. Its accepted hand/proportion and vest differences may influence motion. This single synthetic case supports partial workflow feasibility, not production readiness, algorithm novelty, independent motion accuracy, artist intent, or a controlled causal/generalization claim. Decision: retain both runs and failed attempts; do not regenerate or promote the pilot to Track A/D evidence.
