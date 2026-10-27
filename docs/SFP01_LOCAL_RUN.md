# SFP-01 local exploratory runner

Current status (2026-10-27): approval and GPU execution subsequently completed. See `SFP01_CHECKPOINT_20261027.md` and the execution report addendum. Earlier readiness/pending statements below describe their original time.

From a normal WSL terminal with CUDA access:

```bash
cd /home/ananya_anand/projects/animation-inbetweening
.venv/bin/python scripts/run_sfp01.py
```

Each invocation creates a unique `outputs/sfp01-<UTC>-<id>` directory and prints its path. An optional `--output PATH` must name a directory that does not exist. No installation, model download, CPU RIFE fallback, or previous-evidence replacement occurs.

The runner verifies the three pinned approved file hashes (frames 0, 4, corrected 7), checks the existing pinned RIFE assets and CUDA, then uses `GuidedBackend` for both conditions. Six interior timeline slots include the supplied frame 4: five frames are generated, giving eight total at 8 fps. Saved PNG slots 0, 4 and 7 must match the prepared inputs pixel for pixel. MP4 is lossy and GIF is palette quantized; these viewing exports are not pixel-preservation evidence. GIF delays alternate 120/130 ms because GIF cannot represent 125 ms exactly, giving eight frames per one-second cycle.

Each condition has eight PNGs, an MP4 and a GIF. `side_by_side` contains labelled comparison frames and animations; `labelled_contact_sheet.png` shows all eight paired frames at native size. `results.json` records status, input paths/hashes, settings, generation and total wall times, backend segment diagnostics, CUDA/GPU details when accessible, saved-pixel checks, and output hashes. `archive.sha256` also covers the result record. Partial failure artifacts remain in their own directory and the process exits nonzero.

The researcher reported CUDA available on an NVIDIA GeForce RTX 4050 Laptop GPU with 6141 MiB. The runner records this separately from its own diagnostics. The earlier `exploratory_execution_r001` evidence remains unchanged. This process's new CUDA-gate failure is recorded at `outputs/sfp01-20261027T033419Z-77a2154d/results.json`.

Share the printed output directory and `results.json` after running. The preliminary feasibility report remains pending actual GPU output inspection: review hand/arm contours, identity and shading drift, ghosting, temporal transitions around frame 4, and the accepted downward settle at frame 7. Do not infer artist-intent validation, independent-reference accuracy, or novelty from this synthetic exploratory demo. Guided and segmented RIFE with these settings are the same procedure. Runtime is an operational diagnostic, not a controlled speed comparison.
