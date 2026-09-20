# Decisions

1. PNG is the accepted input to make channel and alpha validation explicit and keep endpoints pixel-exact.
2. Integer channel crossfade is a deterministic placeholder. It does not estimate motion or preserve line structure.
3. PNG sequence is authoritative for endpoint fidelity. GIF and MP4 are viewing formats with color/alpha limitations.
4. The app listens on loopback only and stores local run folders under ignored `outputs/`.
5. The backend interface permits a future RIFE implementation without changing run orchestration or UI.

6. Uploaded file paths are trusted only under the loopback-only Gradio deployment assumption. The API also accepts programmatic sample paths and valid Gradio temporary paths. Do not expose this app as a public service without revisiting path trust.
7. RIFE_m from the official MIT-licensed ECCV2022-RIFE source is the local AI comparison baseline. Source and checkpoint are pinned and downloaded under `.local/rife/`, not committed.
8. Arbitrary requested counts map directly to timestamps `i/(N+1)`; no recursive bisection or frame duplication is needed.
9. RIFE inference uses float32 and CUDA. FP16 is postponed pending normal-shell stability testing. A 512×512 working area budget limits memory; preprocessing is recorded in manifests.
10. RIFE sees RGB composited over white for RGBA uploads. Alpha is interpolated linearly and original endpoints remain untouched.

## Milestone 3 decisions

- Use 256×256 deterministic RGB procedural line art to bound local CPU/GPU cost; no external dataset or new model.
- Retain RIFE and crossfade implementations unchanged. Reuse run manifests for model identity, runtime, and peak VRAM.
- Use OpenCV's precise Euclidean distance transform and fixed Canny thresholds for reproducible contour diagnostics.
- Report trajectory through an annotated body-center versus output dark-pixel centroid proxy; it can be biased by pose and occlusion.
- Keep benchmark outputs under ignored `outputs/`; do not rank user uploads without complete ground truth.
