# Milestone 1 acceptance criteria

- [x] Two matching PNG keyframes upload and validate type, size, mode, and alpha presence.
- [x] 0–120 deterministic intermediate frames; first/last PNG pixels equal source pixels.
- [x] Ordered timeline, selected frame, and GIF playback in Gradio.
- [x] PNG sequence, GIF, MP4, manifest, and JSONL events in a unique run folder.
- [x] Local CUDA/system diagnostics available in UI and manifest.
- [x] Tests cover validation, count/order, determinism, endpoint pixels, manifest, and exports.
- [x] Synthetic sample run and startup smoke check executed.

## Milestone 2 branch criteria

- [x] Official MIT source, exact commit, author checkpoint revision, size, and hashes documented.
- [x] Rerunnable checksum-verified local setup; source and weights ignored by Git.
- [x] RIFE backend selection with no silent fallback; arbitrary count maps to ordered timestamps.
- [x] Endpoint pixels, backend metadata, preprocessing, timing, and peak memory paths covered by tests.
- [x] Crossfade integration tests continue to pass; UI startup and crossfade sample checked.
- [x] Normal-shell CUDA smoke test on RTX 4050 6GB: CUDA available true, official RIFE source at commit `5d8adbdd40e12c2c8f91930eff838aebe561c086`, checkpoint SHA-256 `9f9e2e8b5c3fef311c9a782aa17a30f87c388ce6dc9c00e4993eba3d3941d3cb`, four total frames with two generated intermediates, inference time 0.528s, peak CUDA memory 66.1 MiB, endpoints pixel-exact, Gradio UI generation successful, no cloud compute used. These measurements apply only to the synthetic smoke-test images and are not general performance claims.
