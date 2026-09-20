# Architecture

`core.py` owns image validation and the `InterpolationBackend` interface. `CrossfadeBackend` is the Milestone 1 implementation; a later RIFE adapter can implement the same `generate(first, last, intermediate_count)` method. `run.py` orchestrates frame generation, exports, structured events, and manifests. `diagnostics.py` collects local CUDA/system facts. `app.py` is only the Gradio presentation layer. `sample.py` builds synthetic fixtures.

Frames are retained as PIL RGB/RGBA images. Source endpoint pixel arrays are copied into positions 0 and N+1. PNG sequence export is the pixel-exact artifact. GIF palette conversion and MP4 YUV encoding are lossy or color-limited and may discard alpha. FFmpeg exports MP4 from the saved PNG sequence.
