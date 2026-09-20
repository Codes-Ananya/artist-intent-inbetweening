# Preserving Artistic Intent in 2D Animation In-Betweening

Milestone 1 is a local, deterministic Gradio prototype. It creates a crossfade between two PNG keyframes and exports an ordered PNG sequence, GIF, MP4, and JSON manifest. It does not use a trained motion model.

## Setup and launch

Use Python 3.10 and the existing `.venv`:

```bash
.venv/bin/python -m pip install -r requirements.txt
./launch.sh
```

Open `http://127.0.0.1:7860`. To use another port: `GRADIO_SERVER_PORT=7861 ./launch.sh`. The app binds to loopback only. FFmpeg must be on `PATH`.

Upload two RGB or RGBA PNGs with identical dimensions and mode. Select 0–120 intermediate frames and 1–60 FPS. Use the timeline, frame slider, and animated GIF preview, then download the PNG frames, MP4, or manifest. Each run is saved under ignored `outputs/<run-id>/` with a GIF and JSONL log too. The original endpoint pixels are retained exactly in the PNG sequence.

## Verify

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m inbetween.sample
```

Synthetic keyframes are in `samples/`. See `docs/` for specification, architecture, acceptance criteria, decisions, and research results.
