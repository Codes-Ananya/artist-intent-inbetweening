# SFP-01 extra-breakdown runner readiness

Current status (2026-10-27): approval and GPU execution subsequently completed. See `SFP01_CHECKPOINT_20261027.md` and the execution report addendum. Earlier readiness/pending statements below describe their original time.

Prepared 2026-10-27. No experiment inference has been run. Frame 2 requires user visual approval before use. This is an exploratory workflow comparison with unequal supplied information, not a novel algorithm or artist-intent validation.

The separate runner `scripts/run_sfp01_extra_breakdown.py` imports existing export/input validation helpers and uses `GuidedBackend` over 0→4 with frame 2 supplied. It makes two backend calls, each requesting one local midpoint (frames 1 and 3). It appends archived RIFE frames 5–6 unchanged and approved frame 7. Frames 0, 4 and 7 retain their approved hashes. The baseline runner and archive are unchanged.

| Condition | Supplied | Newly inferred in this experiment | Historical generated |
|---|---|---|---|
| Archived baseline | 0, 4, 7 (3) | None | 1, 2, 3, 5, 6 (5) |
| Extra breakdown | 0, 2, 4, 7 (4) | 1, 3 (2) | 5, 6 reused (2) |

Both conditions retain eight frames at 8 fps. The comparison header shows input budgets; each frame is labelled supplied, historical generated, newly generated, or reused historical generated. Frame 2 is conditioning data in the treatment, not a matched generated-frame quality measurement. Evaluate frames 1 and 3 for ghosting, opacity, contour integrity and body distortion, and the sequence for motion continuity and popping. No independent motion correctness, artist intent, generalization or production readiness follows from this one case.

## Approval and invocation

Do not execute the command until the user explicitly approves the displayed frame-2 candidate. After that approval only, record an approval JSON containing `status: "approved_for_inference"`, the exact prepared PNG's `frame2_sha256`, `reviewer`, `approved_at`, and verbatim `user_approval_text`. No production approval record is supplied by this runner. Pending, incomplete or hash-mismatched records fail before CUDA/model initialization or output creation.

```bash
.venv/bin/python scripts/run_sfp01_extra_breakdown.py \
  --frame2 /absolute/path/to/approved_frame2_prepared.png \
  --approval /absolute/path/to/actual_user_approval.json \
  --output outputs/sfp01-extra-NEW-UNUSED-RUN-ID
```

Omitting `--output` selects a timestamped UUID directory. Existing output paths and paths inside the baseline are refused. The baseline defaults to `outputs/sfp01-20261027T033651Z-462f2bc4`. Its archive manifest hash is pinned and every archived file is verified before and after execution. Model source commit, checkpoint, float32 and CUDA device must match the archived baseline. No download or CPU fallback is added.

Future outputs include `extra_breakdown/frame_0000.png` through `frame_0007.png`, treatment MP4/GIF, `side_by_side/animation.mp4`, `side_by_side/animation.gif`, `labelled_contact_sheet.png`, `results.json`, and `archive.sha256`. Metadata records source paths/hashes, per-frame provenance, budgets, approval, runner/backend code hashes, model diagnostics, actual free/total VRAM before generation, separate new-generation timing, and exact saved PNG checks. GIF/MP4 are viewing derivatives; PNGs are authoritative for pixel checks. Timing includes only the new treatment work, not a recomputation of baseline. Failures leave their evidence in the fresh run directory.

## Local tests

`tests/test_sfp01_extra_breakdown.py` verifies midpoint placement/counts and exact preservation using an `InterpolationBackend` test double; approval rejection and hash binding; full PNG/GIF/MP4/contact-sheet export using a fake backend; refusal to overwrite an existing output directory. Test approval records and solid-color test poses exist only in temporary pytest paths and are explicitly marked TEST ONLY. They do not approve the real candidate. The export test verifies the real archived baseline read-only, with CUDA and RIFE replaced by a test double.

The current candidate is `.local/real_input_pilot/synthetic_pilot/sfp_01/extra_breakdown_f002_r001/frame2_prepared.png`, SHA-256 `b55d945b5575f8b8d26688722029100b95d25299531d94616558349dfd66ce9f`. Its sibling provenance and original-generation artifacts must be retained with it. This digest identifies the candidate for review; it is not approval. No actual user approval JSON has been created.
