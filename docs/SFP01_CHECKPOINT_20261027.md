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
