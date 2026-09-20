# Research log

## 2026-09-20: Milestone 1

Environment: Python 3.10.12 virtual environment, FFmpeg available. Initial `nvidia-smi` failed with “GPU access blocked by the operating system”; the placeholder needs no CUDA. Gradio, OpenCV, and pytest were installed into the existing virtual environment. Measured test and sample results are recorded below after verification.

Verification: `pytest -q` passed 6 tests in 2.56 seconds. A sample run with 256×144 RGBA keyframes, 6 intermediate frames, and 12 FPS produced 8 ordered PNGs plus GIF, MP4, manifest, and JSONL log. The Gradio application built and, when launched outside the restricted shell sandbox on loopback port 7861, returned HTTP 200 from `curl -I`. The sandbox itself denied socket access on ports 7860 and 7861. CUDA was unavailable because NVML access was blocked; no GPU operations are required by this backend.
