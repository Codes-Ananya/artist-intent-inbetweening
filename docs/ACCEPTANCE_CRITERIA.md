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
- [ ] Normal-shell CUDA smoke test on RTX 4050 6GB (pending outside the Codex sandbox).
