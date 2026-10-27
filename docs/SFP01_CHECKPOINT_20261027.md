# SFP-01 project checkpoint — 2026-10-27

## State and verified result

Repository root: `/home/ananya_anand/projects/animation-inbetweening`.
Branch: `feature/real-input-pilot`; starting HEAD `b3f8714` (Track A production planning). Starting working tree had seven untracked SFP-01 runner/test/report files and no tracked modifications. Those files were inspected before staging. No inference, installation, model download, or change to interpolation implementation occurred in this checkpoint batch.

Completed treatment: `outputs/sfp01-extra-20261027T041321Z-539ba9c6`.
Frozen baseline: `outputs/sfp01-20261027T033651Z-462f2bc4`.
Both historical result records retain `completed_pending_visual_review`; assistant review is separate in `docs/SFP01_EXTRA_BREAKDOWN_EXECUTION_REPORT.md` and baseline review in `docs/SFP01_PRELIMINARY_FEASIBILITY_REPORT.md`.

All 22 treatment and 32 baseline archive entries passed. All 21 treatment output hashes, four inputs, four code files and approval digest passed. Supplied 0,2,4,7 and reused 5,6 are pixel-exact. Both export sets decode to eight frames/one second/8 fps; GIF uses 120/130 ms alternating delays. Earlier 152-file and 194-file preservation snapshots remain unchanged, including Track A/D. Details: `docs/SFP01_VERIFICATION_20261027.json`.

CUDA execution is established by historical segment diagnostics, not rerun: RTX 4050, cuda:0, float32, two midpoint calls for 1 and 3; 0.601373 s inference, 2.580614 s generation wall, 194,312,704 bytes peak allocated CUDA memory. This is not a controlled speed benchmark.

Visual decision: frame 3 is substantially clearer; frame 1 still ghosts and smears. The first transition remains visibly problematic. Supplied frame 2 restores crisp linework and can cause an abrupt resolution; it is not an interpolated improvement. The 4→7 settle is unchanged. Review was of the full ordered PNG sequence and detailed paired frames, not real-time playback. Unequal budgets (three supplied versus four), synthetic input inconsistencies, no independent references, and no artist study prevent accuracy, novelty, artist-intent or production claims. No further generation is necessary to preserve this result.

## Preserved evidence and essential ignored assets

- Entire `.local/real_input_pilot/`: Track A setup/planning evidence, Track D source/provenance/dataset/review, SFP-01 native/canonical/prepared assets, generation records, candidate reviews and prior execution evidence.
- Approved SFP poses: `.local/real_input_pilot/synthetic_pilot/sfp_01/assets/synthetic_input/r001/` frames 000 and 004; `r002/` corrected frame 007. Exact names/hashes are in treatment results and `scripts/run_sfp01.py`.
- Additional supplied pose and original provenance: `.local/real_input_pilot/synthetic_pilot/sfp_01/extra_breakdown_f002_r001/`; approval: sibling `extra_breakdown_approval_r001/approval.json`. Frame-2 SHA-256: `b55d945b5575f8b8d26688722029100b95d25299531d94616558349dfd66ce9f`.
- Completed runs above, including authoritative PNGs, comparison PNGs/contact sheets, GIF/MP4, results and hash manifests.
- Earlier failures: `outputs/sfp01-20261027T033419Z-77a2154d`, `outputs/sfp01-extra-20261027T040056Z-7fd2e88d`, and SFP `exploratory_execution_r001/`. Never overwrite these with successful results.
- Existing `.local/rife/` contains the locally installed source/checkpoint required for future inference, but is deliberately outside the asset archive and Git. Required source commit `5d8adbdd40e12c2c8f91930eff838aebe561c086`; checkpoint SHA-256 `9f9e2e8b5c3fef311c9a782aa17a30f87c388ce6dc9c00e4993eba3d3941d3cb`. Preserve that installation separately if migrating machines; no automatic model download is authorized.

## Backup and Git

Separate ignored archive: `.local/backups/sfp01-20261027/pilot-assets-and-outputs.tar.gz`; per-file hashes: sibling `contents.sha256`; verification: sibling `verification.json` and tracked `docs/SFP01_ASSET_BACKUP_20261027.json`. This covers regular pilot files and outputs, excluding `pytest-temp` fixtures/symlinks; no weights, credentials or virtual environment. Every archive member is read back and checked against source SHA-256. This is a same-filesystem local backup, not off-device protection.

Configured origin: `https://github.com/Codes-Ananya/artist-intent-inbetweening.git`. Authenticated `gh repo view --json isPrivate,nameWithOwner` returned `isPrivate: false`. The user subsequently explicitly authorized continuing with this same repository even though public. Push to this existing origin is authorized; no visibility change or asset publication is intended. Local commit will include only reviewed SFP scripts, test, reports and this checkpoint. Its final hash is available through `git log -1` and the handoff. A post-commit Git bundle beside the asset archive preserves committed code/history locally.

## Validation and restart

Existing `.venv`: full `python -m pytest -q` completed with 194 passed, 1 skipped in 36.10 s. Dedicated `tests/test_sfp01_extra_breakdown.py::test_fake_backend_sample_export` passed (1.41 s), exercising real PNG/GIF/MP4/contact-sheet export with a test double, without RIFE inference. The test's temporary output is not pilot evidence.

1. Start in the repository root; read this checkpoint, the execution report addendum and both verification JSON files. Run `git status --short` and `git log -1 --oneline`.
2. Review existing `outputs/sfp01-extra-20261027T041321Z-539ba9c6/side_by_side/animation.mp4`, `animation.gif`, and the run's `labelled_contact_sheet.png`. No inference is needed.
3. Verify each run read-only with `(cd outputs/RUN-ID && sha256sum -c archive.sha256)`. Approved input and code digests are in results.json. Preserve historical status records.
4. To restore ignored evidence, first inspect `tar -tzf .local/backups/sfp01-20261027/pilot-assets-and-outputs.tar.gz`; extract into a NEW empty recovery directory, not over current evidence. From that recovery root verify `sha256sum -c /absolute/path/to/contents.sha256`. Paths in recorded results are absolute to the original workspace; relocation requires deliberate mapping, not editing frozen originals.
5. Future inference, only if newly requested, uses existing `.venv` and installed RIFE in normal GPU-accessible WSL: see `docs/SFP01_EXTRA_BREAKDOWN_RUNNER.md`. Omit `--output` to create a new unique run. Existing approval is bound to the exact frame-2 digest; do not reuse it for changed pixels.

## Remaining work

Push the checkpoint branch to the user-authorized existing public origin and verify remote HEAD matches local commit; final handoff records the actual outcome. Copy the verified asset archive and Git bundle to durable separate storage when a destination is available; same-disk redundancy does not protect against disk loss. User motion review remains separate from assistant review. Further experiment design/reference collection or input refinement requires a new task; do not silently turn this exploratory example into Track A/D data or regenerate approved poses.


## Frame-1 scale experiment checkpoint addendum

Completed run: `outputs/sfp01-frame1-scale-20261027T170646Z-caeb63e7`; earlier failed attempt: `outputs/sfp01-frame1-scale-20261027T170356Z-de19024c`. Both preserved, no inference rerun for review. Results retain their historical status; separate review: `docs/SFP01_FRAME1_SCALE_EXPERIMENT.md`. Verification: `docs/SFP01_FRAME1_SCALE_VERIFICATION.json`.

Negative result: scale 0.5 did not visibly resolve the fading/smearing. Extended hand/arm looks paler; vest overlap remains. Only frame 1 differs from the extra-breakdown baseline; all seven other PNGs and four supplied inputs match exactly. All 21 output hashes, 22 archive entries, two code hashes and baseline archive checks passed. RTX 4050 cuda:0 float32 generated one midpoint; inference 0.715336 s, generation wall 2.547167 s, peak allocated memory 193,264,128 bytes. Exports decode correctly at eight frames/one second. Prior 152/194-file preservation snapshots match, including Track A/D.

Scale 1 stays the default and baseline. The optional scale control, isolated runner, tests and report are being committed after review; no outputs, weights or credentials are staged. Previous checkpoint commit `3268bad32ad78d877eb1d3c097a2d0e5bd9b1544` was successfully pushed to the user-authorized public origin (verified then); this addendum does not claim a new push. Use `git log -1` for the new review commit. Earlier local backup predates these new runs: they remain in outputs and are not claimed to be in that archive.

Restart by reading the completed-review section, inspecting `outputs/sfp01-frame1-scale-20261027T170646Z-caeb63e7/frames_0_1_2.png` and `side_by_side/animation.mp4`, and verifying `archive.sha256` from that run directory. Do not rerun inference to review evidence. Remaining work is a choice of next experiment, not a sweep: one independently supplied occlusion-consistent frame-1 pose (smallest manual workflow test, unequal input budget), or a more involved arm/vest mask-and-clean-plate compositing diagnostic. Neither has begun. No new pose is approved or generated.

Review validation: full pytest suite 197 passed, 1 skipped in 47.36 s, including sample export; diff whitespace checks passed. Commit scope is six files: backend, frame-1 runner/test, experiment report, verification JSON and this checkpoint. Generated evidence remains ignored.

## Layered CPU prototype addendum

Run `outputs/sfp01-layered-20261027T171613Z-e7e5f278` completed using explicit CPU compositing (no RIFE fallback). See `docs/SFP01_LAYERED_PROTOTYPE.md` and `docs/SFP01_LAYERED_VERIFICATION.json`. Implements one manual-mask/cutout/plate experiment for frame 1 through `LayeredPilotBackend`; all other frames and pixels outside the fixed frame-1 ROI are unchanged. Approximate masks, observed-pixel fills, inpainted unknown region, transformed arm alpha and reconstructed plate are saved in `layers/`.

Result: opaque arm and reduced vest smear, but conspicuous shoulder seam, shortened arm/hand and residual edge debris. Not accepted as corrected motion or a new baseline. Unknown reconstruction: 916 pixels; 356 not fully covered by the transformed arm. CPU processing 0.030379 s; total recorded 1.785934 s. All 31 output hashes/32 archive entries and exports verified; 5,813 preexisting files unchanged, including negative scale experiment and Track A/D. Scale 1 remains baseline.

Next step would require an explicitly reviewed shoulder/vest patch and articulated arm pose, or simply one independently supplied frame-1 pose. No further artwork or tuning started. Inspect existing `frames_0_1_2.png`, `layers/reconstructed_plate.png` and `side_by_side/animation.mp4`; no inference rerun needed. CPU runner: `.venv/bin/python scripts/run_sfp01_layered.py`. New code/tests/docs remain local working-tree changes in this task, not committed/pushed. Prior backup predates this run.

## One bounded layered refinement

Run `outputs/sfp01-layered-refined-20261027T172313Z-f78a5da1` compares RIFE, first layer and one fixed refinement. See `docs/SFP01_LAYERED_REFINEMENT.md` and `docs/SFP01_LAYERED_REFINEMENT_VERIFICATION.json`. Restores observed shoulder pixels, cleans the isolated mark with observed background, and replaces scaled arm placement with two unscaled manually rotated pieces. Masks/patches/remaining estimated plate pixels are archived. 255 reconstructed pixels remain, 47 not fully covered by the arm.

Review: shoulder break reduced, stray mark absent, obvious arm shrink removed; blocky/soft elbow and abrupt frame-0 transition remain. Not ground truth or automatic intent preservation. Only frame 1 changed; all approved inputs and 5,846 preexisting files preserved, including Track A/D. 41 output hashes and 42 archive entries verified; three-way eight-frame/8-fps previews decode correctly. Processing 0.053476 s CPU. Scale 1 remains baseline, scale 0.5 remains negative. Stop after this single refinement; no sweep or further artwork undertaken. Inspect `frames_0_1_2.png`, `side_by_side/animation.mp4` and `layers/refined_plate.png` in that run. Local changes are uncommitted; existing backup predates this run.

## Accepted exploratory demonstration and research handoff

The user accepts `outputs/sfp01-layered-refined-20261027T172313Z-f78a5da1` as an exploratory demonstration, with manual masks/patches/articulation and remaining elbow/transition limitations disclosed. Acceptance is hash-bound in `docs/SFP01_EXPLORATORY_ACCEPTANCE.json`. It does not replace scale 1 as baseline or establish artist-intent preservation. Original layered run `outputs/sfp01-layered-20261027T171613Z-e7e5f278` remains a separate diagnostic. No poses generated, no frame tuning, and no experiment inference in this acceptance batch. Archived run results and Track A/D are unchanged.

Supplementary backup: `.local/backups/sfp01-layered-accepted-20261027/pilot-evidence.tar.gz`, with `contents.sha256` and `verification.json`. Includes all local real-input pilot assets (Track A/D included), both layered runs and every mask/reconstruction artifact, scale completed/failed evidence, extra-breakdown completed/failed evidence, baseline completed/failed evidence, and the acceptance record. `docs/SFP01_ACCEPTED_BACKUP.json` reports actual archive hash/size/count and verification. Every tar member is read back and hashed, then originals rechecked. This is same-filesystem protection only; earlier backups remain intact. No weights, credentials or virtual environment included. Restore into a fresh empty directory and check `contents.sha256` there; never overwrite existing evidence. Recorded absolute paths need deliberate mapping after relocation.

Research assessment: `docs/SFP01_RESEARCH_ASSESSMENT.md`. Present contribution is a transparent single-case workflow/failure analysis, not a validated novel method. Small next step proposed: three independently sourced, held-out transitions under a frozen procedure/manual budget with all failures reported, not more tuning of SFP-01. No new cases selected. Demonstrator packaging is modest; a publication needs literature positioning, diverse controlled evidence, matched effort/baselines, ablations and independent full-motion review.

This batch stages only reviewed code, tests, reports, acceptance and backup metadata; outputs remain ignored. Branch `feature/real-input-pilot`, origin `https://github.com/Codes-Ananya/artist-intent-inbetweening.git` (public, previously explicitly authorized). Prior HEAD `977edcb931ff67de078651e1ebc4b992f5ba4f22`. Final commit/push outcome is reported in the handoff and local backup receipt; use `git log -1` / `git status --short` to resume. A post-commit Git bundle is stored beside the supplementary archive. Earlier statements that layered work was uncommitted are historical and superseded by the final handoff.

Acceptance-batch validation: full `.venv` pytest **200 passed, 1 skipped in 35.02 s**. Sample PNG/GIF/MP4 export from already saved refined frames passed in a temporary directory; no candidate generation. Original/refined archive entries and current code hashes rechecked. Supplementary archive verified 337 files, 58,965,994 bytes; SHA-256 `13201a149877f203590d40c7930d18fa72f2f6633670f222cb82e33ee218d544`.
