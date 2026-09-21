# Synthetic metric definitions (v1)

All frames are 256×256 RGB in the built-in suite. Metrics evaluate intermediate frames only. Input RGB is converted to 8-bit gray with OpenCV `COLOR_RGB2GRAY` (integer BT.601 coefficients). PSNR uses mean squared 8-bit gray error and peak 255: `10 log10(255²/MSE)` dB; exact equality is mathematically infinite and is reported as null. SSIM is the mean of the per-pixel standard formula with an 11×11 Gaussian window, sigma 1.5, population moments, C1=6.5025 and C2=58.5225. Border handling is OpenCV's default reflect-101.

Edges are OpenCV Canny on that gray image with thresholds 100 and 200, default 3×3 aperture, no L2 gradient. Precision is the fraction of generated edge pixels within Euclidean distance ≤2 pixels of a reference edge. Recall reverses the roles. F1 is their harmonic mean. Symmetric Chamfer is the mean of reference-to-generated and generated-to-reference nearest-edge Euclidean distances, divided by two, using `DIST_L2` with `DIST_MASK_PRECISE`. Empty/empty edges score F1=1, Chamfer=0; one empty edge map scores F1=0 and Chamfer=image diagonal. Pixel equality compares endpoint mode, dimensions, and every channel value.

Trajectory error is mean Euclidean pixel distance between annotated body center and the dark-pixel centroid estimated from each output frame using a fixed gray threshold below 80. This centroid is only a diagnostic proxy: limbs, occlusion, and line width can move it without moving the body center. When no pixel qualifies, the frame measurement is null in JSON and empty in CSV. The sequence mean uses only finite measurements and is null when none exist. `trajectory_measured_frames` and `trajectory_missing_frames` count intermediate frames; summary coverage shows measured/total. Other nonfinite metrics are also null in JSON and empty in CSV. No global ranking is computed. Failed sequences have no metric values, retain an error record, and do not stop other cases.

`backend_wall_seconds` measures the entire `backend.generate` call, including model loading, preprocessing, inference, and output preparation. `inference_seconds` is the backend-reported inference loop where available; for crossfade it equals wall time because there is no separate loop measurement. `model_load_seconds` records RIFE model initialization and checkpoint load when measured. These are durations, not mutually exclusive components. Peak CUDA allocation is reported when available.

For the guided oracle diagnostic, primary `means` and `generated_only_means` use the same frame indices for both methods: `1..N` excluding breakdown index `k`. `evaluated_frame_indices`, `excluded_frame_indices`, and `evaluated_frame_count` make the pairing explicit. Both methods' index-k metrics appear in `breakdown_index_metrics`; `is_authoritative_breakdown` marks guided D. Per-frame and aggregate perfect PSNR use a null numeric value plus `psnr_perfect_match` or `generated_only_psnr_perfect_match_count`. If any evaluated PSNR is infinite, its mean is null and `generated_only_psnr_mean_undefined_due_to_perfect_match` is true; infinity is never silently averaged or dropped. Guided backend wall time covers two calls and can differ in model loading from endpoint-only's one call. These durations are operational diagnostics, not a fair speed comparison; `guided_breakdown.segments` gives authoritative segment diagnostics.

Milestone 5 adds a preregistered within-case position ranking, defined precisely
in `BREAKDOWN_POSITION_PROTOCOL.md`. Gains are matched on indices excluding k;
trajectory gains use the intersection of measurable indices, and ranking uses
trajectory only when that intersection covers all five indices for every k.
Raw trajectory means retain their own measurable coverage through per-frame
records; do not subtract independently covered means for the primary gain.

Milestone 5 is closed as an initial procedural negative result; see
[verified results and limitations](BREAKDOWN_POSITION_PROTOCOL.md#milestone-5-closure-initial-procedural-negative-result).
Flat improvements use `psnr_db_gain`, `ssim_gain`, `edge_f1_gain`,
`chamfer_px_reduction`, and `trajectory_error_px_reduction`; absolute metrics
retain their names. The UI requires manual k and cannot adopt the diagnostic.
