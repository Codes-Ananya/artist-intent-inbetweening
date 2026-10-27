# SFP-01 frame-1 flow-scale experiment

2026-10-27. Continues `SFP01_CHECKPOINT_20261027.md`. Current status: completed normal-WSL run reviewed as a negative result; scale 1 retained. Earlier CUDA-blocked attempt is preserved below.

## Inspection: observations versus hypotheses

Inspected native 512×512 PNGs 0, 2 and generated 1 from frozen `outputs/sfp01-extra-20261027T041321Z-539ba9c6/extra_breakdown/`. Frame 0 has a bent arm with the hand near the waist over the vest. Frame 2 has a forward-reaching forearm/hand, with different elbow geometry and vest exposure. Frame 1 visibly retains the bent-arm silhouette while showing a pale, almost disappearing extended limb; shoulder and orange vest edges smear. Head, legs and tail are comparatively stable. The inputs are opaque RGB, so visible translucency is not an input alpha-channel issue. Native-size inference previously used no image resizing or padding.

Hypotheses, not established causes: the large hand displacement and changing occlusion may defeat motion correspondence; predicted warps/blending may combine incompatible source regions or background. Accepted synthetic hand/vest inconsistencies may worsen correspondence. Stylized flat regions and thin outlines may provide insufficient matching cues. None is proven without inspecting internal flow/masks or independent motion references. No ground-truth frame 1 exists.

## Small fixed intervention

Expose optional `flow_scale` in existing `RifeBackend` (still an `InterpolationBackend`); allow only 1.0 (unchanged default invocation) or 0.5. The installed pinned `model/RIFE.py` multiplies its default internal flow scales `[4,2,1]` by `1/scale`, giving `[8,4,2]` at 0.5. This is an existing model control, not a new algorithm. It leaves full-resolution endpoint tensors/output dimensions intact; it changes internal flow estimation scales, not the approved source files.

Hypothesis tested: coarser estimation may handle the larger displacement more coherently. It may instead lose fine finger/outline detail or preserve the same artifact. One fixed candidate only: frame 1 at t=0.5 between exact approved 0 and 2, existing RIFE_m weights, CUDA float32. No sweep, new pose, crop, compositing, training, model download, dependency installation, TTA or fallback. Coarser flow is a modest local computation change suitable to try on the existing 6 GB RTX 4050, but actual memory/time are not established until the GPU run.

Compare against the archived extra-breakdown frame 1 (scale 1), not the original three-input experiment. Here both conditions use the same four supplied frames 0,2,4,7; frame 2 remains supplied. Reuse frames 3,5,6 and every supplied frame. Only frame 1 changes. Historical baseline is not recomputed, so timings are operational rather than a controlled benchmark. Compare limb opacity, single versus doubled silhouette, shoulder/vest continuity, hand integrity, and transitions 0→1→2 at 8 fps. Do not choose a winner solely from reduced pixel difference or greater opacity.

## Runner and artifacts

```bash
cd /home/ananya_anand/projects/animation-inbetweening
.venv/bin/python scripts/run_sfp01_frame1_scale.py
```

The command prints a fresh `outputs/sfp01-frame1-scale-<UTC>-<id>` path. Never reuse a prior output directory. Expected successful outputs:

- `candidate/frame_0000.png` through `frame_0007.png`, `animation.gif`, `animation.mp4`.
- `side_by_side/frame_0001.png` for detailed comparison, all eight paired PNGs, `animation.gif`, `animation.mp4` for full-motion comparison.
- `frames_0_1_2.png` for the local transition; `results.json` and `archive.sha256`.

Records include input hashes, pinned baseline manifest hash, runner/backend hashes, method, per-frame roles, GPU free/total memory, backend model/checkpoint/device/dtype/preprocessing/inference time/peak allocated memory, generation wall time and total wall time. Saved PNGs at all seven unchanged slots are compared exactly; baseline archive and input hashes are checked before and after. Exports use existing 8 fps helpers (GIF 120/130 ms alternating); viewing formats do not preserve exact pixels. Existing paths are refused. No model substitution on errors.

## Actual execution and preservation

Attempt: `outputs/sfp01-frame1-scale-20261027T170356Z-de19024c/results.json`. Status `failed`: CUDA unavailable to this process. Gate/setup wall time 3.362232 s, **not inference runtime**. No candidate PNG, comparison or animation was generated; no inference/memory/visual improvement result exists. Failure metadata and archive are preserved. Frozen baseline and inputs passed before/after verification. Prior preservation snapshots (152 and 194 entries) have zero mismatches; Track A/D and all historical runs remain untouched.

Tests cover default versus explicit scale dispatch, invalid scale, a real export with a labelled test-only backend, preservation of all seven unchanged frames, existing-path refusal, and archived CUDA failure without fallback. Test images are not pilot candidates. Full suite result is recorded below.

Next step: run the command in normal GPU-enabled WSL and inspect its printed run directory. Review candidate versus archived frame 1 and sequence continuity before accepting any improvement. No artistic-intent validation, novelty or production-readiness claim is supported. Current checkpoint commit remains the preserved baseline; this intervention is a local working-tree change and was not committed/pushed in this task.

Validation completed: `.venv/bin/python -m pytest -q` — **197 passed, 1 skipped in 43.99 s**, including the new sample PNG/GIF/MP4 export test. The skip is the existing CUDA-dependent test. `git diff --check` passed.

## Completed run review: negative result

Reviewed `outputs/sfp01-frame1-scale-20261027T170646Z-caeb63e7` without rerunning inference. This section supersedes the earlier pending next step; the failed Codex attempt remains historical evidence. The archived results retain `completed_pending_visual_review`; this separate report records the review without modifying the run.

Independent checks passed: 21 output hashes, 22 run archive entries including results.json, 22 frozen extra-breakdown archive entries, the pinned baseline manifest digest, two current code hashes and four approved input hashes. Decoded candidate PNGs match the baseline at every index except 1; supplied pixels also match original inputs. Frame 1 differs, confirming that the experiment actually changed its output. Both media sets fully decode to eight frames at 8 fps over one second; GIF delays alternate 120/130 ms. Earlier preservation snapshots of 152 and 194 files still match. See `SFP01_FRAME1_SCALE_VERIFICATION.json` for measured verification details.

Historical CUDA diagnostics: RTX 4050 Laptop GPU, `cuda:0`, float32, scale 0.5, one generated midpoint at t=0.5. Existing source/checkpoint identifiers match the prior run. Native 512×512 input/output, no resize/padding. Inference 0.715336 s; model load 1.771497 s; generation wall 2.547167 s; total recorded wall 7.992892 s. Peak allocated CUDA memory 193,264,128 bytes; free before generation 5,321,523,200 of 6,438,780,928 bytes. These are recorded operational measurements, not a fresh GPU probe or fair speed comparison with historical baseline timings.

Visual inspection of the paired 0/1/2 sheet shows **scale 0.5 did not visibly resolve fading/smearing**. The extended hand/forearm appears even paler and less defined than scale 1; the bent-arm trace and orange/green overlap around the vest remain. There are small differences in ghost position and contour softness, but no restored solid, coherent reaching arm. These qualitative observations do not establish a quantitative ranking. The jump into crisp supplied frame 2 remains; all later sequence frames are pixel-identical, so there is no downstream motion improvement. Review used ordered stills and media decoding/timing checks, not real-time playback or a perceptual study.

Decision: preserve this run as a negative result. **Scale 1 remains the default and baseline.** Keep the opt-in 0.5 control only for reproducibility; do not promote it or initiate a sweep. This does not rule out every scale or establish occlusion as the cause. Both conditions have the same four supplied frames (frame 2 is supplied), with only one new inference in this experiment. No novelty, artistic-intent or reference-based motion-accuracy claim follows.

## Proposed next experiment — no execution authorized by this proposal

Smallest practical next test: one independently drawn/supplied pose at the troublesome frame-1 time, explicitly showing a solid arm crossing in front of the vest. Preserve approved 0 and 2. First compare the three-pose sequence 0→supplied 1→2 with the current sequence, without new inference. This tests whether an explicit occlusion-consistent pose repairs the local workflow transition. Effort is one pose plus provenance, alignment and visual approval; no new model or code is initially needed. It is an extra-input/manual correction condition, **not** evidence that interpolation improved. A supplied frame 1 cannot also be scored as a generated frame or independent held-out reference. If interpolation around that pose is later desired, define a denser, matched timeline and evaluate newly generated half-slots separately; do not change timing silently. Independent means not copied/traced from the failed output; record actual authorship and generation provenance, without assuming approval establishes intent.

Alternative with more preparation: an arm-over-vest layered diagnostic using the same endpoint poses, manually reviewed foreground arm masks, correspondence/warp controls and a clean torso/vest plate for revealed areas. Generate only a candidate frame 1, retain the archived image outside a fixed reviewed region, and composite a separately warped arm with an explicit foreground order. Existing Pillow/OpenCV can support this locally; inference is not necessarily needed. This tests whether explicit region separation and occlusion ordering avoid the ghosting, but adds manual geometry/masks and possibly reconstructed hidden pixels. A rectangular crop alone would not remove arm/vest ambiguity. The current RGBA RIFE path linearly interpolates alpha, so passing masked inputs to it is not by itself an occlusion-aware solution. Effort exceeds one pose: masks at two endpoints, joint/correspondence choices, background reconstruction, boundary handling and new tests. Success would be a manually assisted compositing result, not proof of RIFE motion recovery.

Recommendation: obtain/review one independent pose first if the aim is a usable local correction. Choose the layered diagnostic instead if the aim is specifically testing an occlusion-handling mechanism and manual mask/plate effort is acceptable. Neither option has been started; no pose, mask or new parameter run was created.

Pre-commit review validation: full suite rerun **197 passed, 1 skipped in 47.36 s**, including `test_sample_export_only_frame1_changes` (real PNG/GIF/MP4 exports with a test-only backend). `git diff --check` passed. No experiment inference was rerun during review.
