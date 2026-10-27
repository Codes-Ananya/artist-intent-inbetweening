# SFP-01 preliminary feasibility report — completed GPU run

Review date: 2026-10-27. Run: `sfp01-20261027T033651Z-462f2bc4`.

Local GPU execution and export are feasible for this specific eight-frame, 512×512 synthetic example. Visual quality is mixed: segmented RIFE produces a cleaner downward settle than cross-dissolve, but the initial reach has severe fading, smearing and hand-contour defects. This is an operational feasibility demonstration, not production-quality animation, a novel algorithm, or artist-intent validation.

This report completes the previously pending review using the existing results and artifacts. No inference was rerun. The earlier CUDA-gate failure report remains valid evidence of that earlier attempt and has not been overwritten. The completed run's archived `results.json` retains `completed_pending_visual_review`; this separate report records the review without changing that historical record.

## Verified outputs and preservation

Read `results.json`, recomputed all 31 recorded output SHA-256 hashes, and checked all 32 entries in `archive.sha256` (including results.json): all passed. Independently checked all three current input file hashes and compared decoded input pixels with saved condition PNGs at slots 0, 4 and 7: all six comparisons passed. Inputs are 512×512 RGB; corrected frame 7 uses revision r002.

| Artifact set | PNG frames | MP4 | GIF |
| --- | ---: | --- | --- |
| Segmented cross-dissolve | 8 | 512×512, 8 fps, 1.000 s, 8 decoded frames | 8 frames, 1,000 ms |
| Segmented RIFE | 8 | 512×512, 8 fps, 1.000 s, 8 decoded frames | 8 frames, 1,000 ms |
| Labelled side-by-side | 8 | 1024×544, 8 fps, 1.000 s, 8 decoded frames | 8 frames, 1,000 ms |

Each condition contains three supplied frames and five generated frames (slots 1, 2, 3, 5, 6). The requested six interior slots include supplied frame 4; they do not mean six inferred frames. There are 24 sequence PNGs, three MP4s, three GIFs and one 1024×4352 contact sheet. GIF delays alternate 120/130 ms; average playback is 8 fps. Exact pixel preservation applies to PNGs, not lossy MP4 or palette-quantized GIF.

The 152 files in the earlier `exploratory_execution_r001/preservation_before.json` snapshot still match their recorded hashes. Existing evidence and Track A/D were not edited. No master freeze, input regeneration, paper change, dependency installation, download or commit occurred.

## Recorded CUDA, runtime and memory

These are historical run diagnostics, not measurements from a new inference or a current GPU probe.

| Quantity | Recorded result |
| --- | --- |
| CUDA | Available; both RIFE segments report `cuda:0`, float32; fallback disabled |
| GPU | NVIDIA GeForce RTX 4050 Laptop GPU |
| Total GPU memory | 6,438,780,928 bytes = 6,140.5 MiB; nvidia-smi rounds to 6,141 MiB |
| Free/available VRAM at execution | Not recorded; cannot be established from total capacity |
| Peak PyTorch allocated CUDA memory | 201,652,736 bytes = 192.31 MiB (maximum of segment peaks) |
| RIFE generation wall time | 3.226254 s |
| RIFE inference time, summed segments | 0.731305 s (0.658833 + 0.072472 s) |
| RIFE model-load time, segment records | 2.179536 s and 0.216909 s; sum 2.396445 s |
| Cross-dissolve generation wall time | 0.019220 s |
| Cross-dissolve summed backend time | 0.015472 s |
| Total recorded wall time | 9.169987 s |

The run records PyTorch 2.14.0+cu126, Python 3.10.12, WSL2 Linux and driver 566.26. RIFE source commit is `5d8adbdd40e12c2c8f91930eff838aebe561c086`; checkpoint SHA-256 is `9f9e2e8b5c3fef311c9a782aa17a30f87c388ce6dc9c00e4993eba3d3941d3cb`. Both segments used native 512×512 dimensions without resize or padding.

The aggregate model-load field is null, but the two segment records contain timings; null must not be interpreted as zero. The adapter synchronizes CUDA around inference timing and reports `torch.cuda.max_memory_allocated()`. That counter is not total device/process usage, reserved memory, or free VRAM. Subtracting it from capacity would not establish available headroom. Successful completion supports that sufficient memory was available for this run only. Total wall time includes setup, generation and exports but is captured before final result/archive writing. These single-run, load-inclusive measurements are operational diagnostics, not a controlled speed benchmark.

## Visual observations

Inspected the original contact sheet and all eight decoded side-by-side frames from each of the MP4 and GIF, including enlarged arm/hand details. Frame ordering and durations were checked from the media files. Review was frame-by-frame with timing metadata, not a real-time playback or human perceptual study; temporal judgments below are qualitative interpretations of that sequence.

- **Cross-dissolve, frames 1–3:** bent and extended arm silhouettes overlap transparently. The hand/forearm ghosts into the destination instead of tracing a solid articulated reach. At frames 5–6, two hand/arm positions remain visible during the settle.
- **RIFE, frames 1–2:** the bent arm and orange vest boundary smear, while a very faint extended forearm/hand appears against the background. Frame 2 still lacks a solid, well-defined reaching limb. This is a substantial visibility and contour failure.
- **RIFE, frame 3 into supplied frame 4:** the extended arm becomes more solid but remains blurred, with ragged/doubled finger edges and disturbed shoulder/vest contours. Frame 4 abruptly restores crisp supplied linework. The sequence suggests a delayed reach followed by a rapid resolution, rather than consistently clean movement through the first segment.
- **RIFE, frames 4–7:** frames 5 and 6 show a mostly single, coherent arm moving downward toward the accepted frame-7 settle. Hand edges are softer than the inputs, with small shoulder/vest contour changes, but the doubled silhouettes of cross-dissolve are substantially reduced here. This segment looks more continuous in frame progression; it does not rescue the defective first segment.
- **Identity and shading:** face, head silhouette, clothing palette, tail and feet remain broadly recognizable and stable at the inspected scale. Local color/contour instability is concentrated around the moving arm, shoulder and vest. This does not establish exact identity consistency or eliminate subtler drift. The supplied stylized anatomy and pronounced final settle are accepted input characteristics, not generated-output corrections.
- **Exports:** both decoded viewing formats retain the same major artifacts visible in the PNG contact sheet, so the initial-reach defects are not merely MP4 compression artifacts. Minor palette/compression differences limit fine color judgments. The looping GIF returns directly from frame 7 to frame 0; that reset is not an interpolated return motion and should not be mistaken for a within-segment failure.

## Interpretation and limitations

The workflow successfully preserves all authoritative PNG pixels, generates five intermediate images per condition on the intended timeline, executes existing RIFE on CUDA and exports reviewable media. Visual feasibility is only partial: the smaller settle is encouraging, while the larger initial reach fails to maintain a solid arm and clean linework. This example does not justify an overall RIFE quality win or production-readiness claim.

Both conditions split at supplied frame 4 and use the same three authoritative inputs. Guided RIFE and segmented RIFE under these settings are the same procedure, not independent algorithms. This work applies an existing pretrained interpolation backend; it makes no algorithmic novelty claim.

There is one short synthetic sequence, no independent ground-truth intermediate sequence, no blinded or repeated quality evaluation, and no artist-intent study. Input approval establishes permission to use these poses for exploration, not that generated motion realizes an artist's intent. No reference-dependent accuracy scores, generalization, causal benefit of breakdown guidance, or production performance conclusions are supported. Broader evaluation would require separately authorized examples and appropriate independent references or artist review; none were generated for this review.

## Exact artifact paths

- Side-by-side MP4: `/home/ananya_anand/projects/animation-inbetweening/outputs/sfp01-20261027T033651Z-462f2bc4/side_by_side/animation.mp4`
- Side-by-side GIF: `/home/ananya_anand/projects/animation-inbetweening/outputs/sfp01-20261027T033651Z-462f2bc4/side_by_side/animation.gif`
- Contact sheet: `/home/ananya_anand/projects/animation-inbetweening/outputs/sfp01-20261027T033651Z-462f2bc4/labelled_contact_sheet.png`
- This report: `/home/ananya_anand/projects/animation-inbetweening/docs/SFP01_PRELIMINARY_FEASIBILITY_REPORT.md`
- Results: `/home/ananya_anand/projects/animation-inbetweening/outputs/sfp01-20261027T033651Z-462f2bc4/results.json`
- Preserved earlier failure report: `/home/ananya_anand/projects/animation-inbetweening/.local/real_input_pilot/synthetic_pilot/sfp_01/exploratory_execution_r001/PRELIMINARY_FEASIBILITY_REPORT.md`
