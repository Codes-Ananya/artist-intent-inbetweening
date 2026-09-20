"""Run storage, manifests, logging and exports."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4
from PIL import Image
from .core import CrossfadeBackend, InterpolationBackend, load_keyframes
from .diagnostics import collect


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_run(first: str | Path, last: str | Path, intermediate_count: int, fps: int = 12, output_root: str | Path = "outputs", backend: InterpolationBackend | None = None) -> dict:
    if not isinstance(fps, int) or not 1 <= fps <= 60:
        raise ValueError("FPS must be an integer from 1 to 60")
    a, b = load_keyframes(first, last)
    backend = backend or CrossfadeBackend()
    frames = backend.generate(a, b, intermediate_count)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8]
    folder = Path(output_root) / run_id
    sequence = folder / "png_sequence"
    sequence.mkdir(parents=True)
    log_path = folder / "events.jsonl"
    def log(event: str, **fields):
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "event": event, **fields}) + "\n")
    log("run_started", backend=backend.name, frame_count=len(frames))
    for index, frame in enumerate(frames):
        frame.save(sequence / f"frame_{index:04d}.png")
    first_path = sequence / "frame_0000.png"
    last_path = sequence / f"frame_{len(frames)-1:04d}.png"
    # Pixel equality is verified in tests; copies retain the source mode and channel values.
    gif = folder / "animation.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=round(1000 / fps), loop=0, disposal=2)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required for MP4 export")
    mp4 = folder / "animation.mp4"
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-framerate", str(fps), "-i", str(sequence / "frame_%04d.png"), "-vf", "format=yuv420p", "-c:v", "libx264", "-movflags", "+faststart", str(mp4)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        log("export_failed", format="mp4", error=result.stderr)
        raise RuntimeError(f"FFmpeg export failed: {result.stderr}")
    manifest = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(), "backend": backend.name, "intermediate_count": intermediate_count, "frame_count": len(frames), "fps": fps, "size": list(a.size), "mode": a.mode, "input_sha256": [_sha(Path(first)), _sha(Path(last))], "frames": [str(path) for path in sorted(sequence.glob("*.png"))], "exports": {"png_sequence": str(sequence), "gif": str(gif), "mp4": str(mp4)}, "diagnostics": collect()}
    manifest_path = folder / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    log("run_completed", manifest=str(manifest_path), endpoint_frames=[str(first_path), str(last_path)])
    return manifest
