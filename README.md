# Preserving Artistic Intent in 2D Animation In-Betweening

Milestone 1 is a local, deterministic Gradio prototype. It creates a crossfade between two PNG keyframes and exports an ordered PNG sequence, GIF, MP4, and JSON manifest. It does not use a trained motion model.

## Setup and launch

Use Python 3.10 and the existing `.venv`. The verified GPU environment uses CUDA 12.6 PyTorch wheels on an RTX 4050 6GB. Install the GPU requirements first:

```bash
.venv/bin/python -m pip install -r requirements-gpu-cu126.txt
```

Then install the application requirements:

```bash
.venv/bin/python -m pip install -r requirements.txt
./launch.sh
```

`requirements-lock.txt` pins the verified application dependency environment for reproducibility; install it instead of `requirements.txt` when exact application versions are needed. PyTorch and CUDA are controlled separately by `requirements-gpu-cu126.txt`. The placeholder backend can run without PyTorch, but the GPU installation prepares later model integration.

Open `http://127.0.0.1:7860`. To use another port: `GRADIO_SERVER_PORT=7861 ./launch.sh`. The app binds to loopback only. FFmpeg must be on `PATH`.

Upload two RGB or RGBA PNGs with identical dimensions and mode. Select 0–120 intermediate frames and 1–60 FPS. Use the timeline, frame slider, and animated GIF preview, then download the PNG frames, MP4, or manifest. Each run is saved under ignored `outputs/<run-id>/` with a GIF and JSONL log too. The original endpoint pixels are retained exactly in the PNG sequence.

## Verify

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m inbetween.sample
```

Synthetic keyframes are in `samples/`. See `docs/` for specification, architecture, acceptance criteria, decisions, and research results.

## Optional local RIFE baseline (Milestone 2)

RIFE is a comparison baseline, not the proposed research contribution. It uses the official MIT-licensed [ECCV2022-RIFE](https://github.com/hzwer/ECCV2022-RIFE) implementation and the author's RIFE_m arbitrary-timestep checkpoint. The exact source commit, checkpoint revision, sizes, and SHA-256 hashes are in [RIFE provenance](docs/RIFE_PROVENANCE.md).

After installing the CUDA PyTorch requirements above, download the pinned local assets without changing the virtual environment:

```bash
.venv/bin/python scripts/setup_rife.py
```

The checkpoint archive is 39,819,850 bytes (38.0 MiB), and the extracted weight file is 42,884,324 bytes. The script verifies both hashes, can be rerun, and reports errors on failure. It places source and weights under ignored `.local/rife/`. To remove them, run `rm -r .local/rife`.

Launch the app and select **RIFE local AI baseline**. RIFE requires CUDA; a missing checkpoint, CUDA failure, or inference error is shown directly and never causes a crossfade fallback. For an RTX 4050 6GB, start with keyframes at or below **512×512** and **2–8 intermediate frames**. Larger inputs are reduced to a 512×512 pixel area budget for inference, then generated frames are restored to the input dimensions. Padding, resizing, alpha treatment, inference time, and peak GPU memory appear in the run manifest. Uploaded first and last PNG pixels remain exact. The RIFE adapter uses float32; FP16 awaits GPU validation.

Run the GPU acceptance check in a normal WSL shell with GPU passthrough:

```bash
.venv/bin/python scripts/rife_smoke_test.py
```

The restricted Codex sandbox may not expose `/dev/dxg`; its CUDA failure does not imply that the normal WSL shell lacks CUDA. The smoke script must pass there before treating RIFE inference as GPU-verified.
