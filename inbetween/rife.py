"""Optional official RIFE_m arbitrary-timestep inference adapter."""
from __future__ import annotations
import importlib
import math
from pathlib import Path
import sys
import subprocess
import time
import numpy as np
from PIL import Image
from .core import InterpolationBackend, ValidationError
from scripts.setup_rife import CHECKPOINT_ID, CHECKPOINT_SHA256, DEFAULT_ROOT, SOURCE_COMMIT, sha256


class RifeError(RuntimeError):
    pass


def timestamps_for_count(count: int) -> list[float]:
    if not isinstance(count, int) or not 0 <= count <= 120:
        raise ValidationError("Intermediate frame count must be an integer from 0 to 120")
    return [index / (count + 1) for index in range(1, count + 1)]


class RifeBackend(InterpolationBackend):
    name = "rife_local_ai"
    version = "RIFE_m arbitrary-timestep @ " + SOURCE_COMMIT[:12]
    max_working_pixels = 512 * 512

    def __init__(self, asset_root: str | Path = DEFAULT_ROOT):
        self.asset_root = Path(asset_root)
        self.last_run_metadata: dict = {}

    def _require_assets_and_cuda(self):
        source = self.asset_root / "source"
        checkpoint = self.asset_root / CHECKPOINT_ID
        if not source.is_dir() or not (source / "model" / "RIFE.py").is_file() or not checkpoint.is_file():
            raise RifeError("RIFE assets are missing. Run .venv/bin/python scripts/setup_rife.py first.")
        try:
            actual_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RifeError("RIFE source checkout is invalid. Rerun scripts/setup_rife.py.") from exc
        if actual_commit != SOURCE_COMMIT:
            raise RifeError(f"RIFE source commit mismatch: expected {SOURCE_COMMIT}, got {actual_commit}")
        if sha256(checkpoint) != CHECKPOINT_SHA256:
            raise RifeError("RIFE checkpoint checksum mismatch. Remove .local/rife and rerun setup.")
        try:
            import torch
        except ImportError as exc:
            raise RifeError("PyTorch is unavailable. Install requirements-gpu-cu126.txt in the existing virtual environment.") from exc
        if not torch.cuda.is_available():
            raise RifeError("CUDA is unavailable to this process. Run the GPU smoke test in a normal WSL shell with RTX 4050 access.")
        return torch, source

    def _infer_rgb(self, first: Image.Image, last: Image.Image, times: list[float], torch, source: Path):
        width, height = first.size
        scale = min(1.0, math.sqrt(self.max_working_pixels / (width * height)))
        work_size = (max(1, round(width * scale)), max(1, round(height * scale)))
        if work_size != first.size:
            first = first.resize(work_size, Image.Resampling.BICUBIC)
            last = last.resize(work_size, Image.Resampling.BICUBIC)
        work_width, work_height = work_size
        pad_right = (-work_width) % 32
        pad_bottom = (-work_height) % 32
        preprocessing = {"original_size": [width, height], "working_size": list(work_size), "resize_method": "bicubic" if work_size != (width, height) else "none", "padding": {"left": 0, "top": 0, "right": pad_right, "bottom": pad_bottom, "mode": "replicate"}, "output_restore": "bicubic" if work_size != (width, height) else "crop"}
        source_path = str(source.resolve())
        if source_path not in sys.path:
            sys.path.insert(0, source_path)
        try:
            model_load_started = time.perf_counter()
            Model = importlib.import_module("model.RIFE").Model
            model = Model(arbitrary=True)
            state = torch.load(self.asset_root / CHECKPOINT_ID, map_location="cpu", weights_only=True)
            state = {key.removeprefix("module."): value for key, value in state.items()}
            model.flownet.load_state_dict(state, strict=True)
            model.device()
            model.eval()
            torch.cuda.synchronize()
            self.last_model_load_seconds = time.perf_counter() - model_load_started
            def tensor(image):
                array = np.asarray(image, dtype=np.float32).copy() / 255.0
                value = torch.from_numpy(array.transpose(2, 0, 1)).unsqueeze(0).to("cuda:0")
                return torch.nn.functional.pad(value, (0, pad_right, 0, pad_bottom), mode="replicate")
            a, b = tensor(first), tensor(last)
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()
            started = time.perf_counter()
            images = []
            with torch.inference_mode():
                for timestamp in times:
                    result = model.inference(a, b, timestep=timestamp)
                    rgb = result[0, :, :work_height, :work_width].clamp(0, 1).mul(255).round().byte().cpu().permute(1, 2, 0).numpy()
                    image = Image.fromarray(rgb, mode="RGB")
                    if work_size != (width, height):
                        image = image.resize((width, height), Image.Resampling.BICUBIC)
                    images.append(image)
            torch.cuda.synchronize()
            seconds = time.perf_counter() - started
            peak = torch.cuda.max_memory_allocated()
            return images, preprocessing, seconds, peak
        except torch.cuda.OutOfMemoryError as exc:
            raise RifeError("RIFE ran out of GPU memory. Reduce input resolution or intermediate frame count; 512×512 and up to 8 frames are recommended for 6GB VRAM.") from exc
        except RuntimeError as exc:
            if "out of memory" in str(exc).lower():
                raise RifeError("RIFE ran out of GPU memory. Reduce input resolution; 512×512 is recommended for 6GB VRAM.") from exc
            raise RifeError(f"RIFE inference failed: {exc}") from exc

    def generate(self, first: Image.Image, last: Image.Image, intermediate_count: int) -> list[Image.Image]:
        self.last_model_load_seconds = None
        times = timestamps_for_count(intermediate_count)
        if first.size != last.size or first.mode != last.mode or first.mode not in ("RGB", "RGBA"):
            raise ValidationError("Keyframes must have matching size and RGB/RGBA mode")
        torch, source = self._require_assets_and_cuda()
        if first.mode == "RGBA":
            background = Image.new("RGBA", first.size, (255, 255, 255, 255))
            a_rgb = Image.alpha_composite(background, first).convert("RGB")
            b_rgb = Image.alpha_composite(background, last).convert("RGB")
            alpha_a = np.asarray(first.getchannel("A"), dtype=np.uint16)
            alpha_b = np.asarray(last.getchannel("A"), dtype=np.uint16)
        else:
            a_rgb, b_rgb = first, last
        images, preprocessing, seconds, peak = self._infer_rgb(a_rgb, b_rgb, times, torch, source)
        if len(images) != intermediate_count:
            raise RifeError(f"RIFE returned {len(images)} frames; expected {intermediate_count}")
        if first.mode == "RGBA":
            denominator = intermediate_count + 1
            for index, image in enumerate(images, 1):
                alpha = ((alpha_a * (denominator - index) + alpha_b * index + denominator // 2) // denominator).astype(np.uint8)
                image.putalpha(Image.fromarray(alpha, mode="L"))
            preprocessing["alpha"] = "RGB composited over white for inference; alpha channels linearly interpolated"
        else:
            preprocessing["alpha"] = "none"
        self.last_run_metadata = {"backend_version": self.version, "source_commit": SOURCE_COMMIT, "checkpoint_id": CHECKPOINT_ID, "checkpoint_sha256": CHECKPOINT_SHA256, "device": "cuda:0", "dtype": "float32", "requested_intermediate_count": intermediate_count, "generated_intermediate_count": len(images), "timestamps": times, "preprocessing": preprocessing, "inference_seconds": seconds, "peak_cuda_memory_bytes": peak}
        if self.last_model_load_seconds is not None:
            self.last_run_metadata["model_load_seconds"] = self.last_model_load_seconds
        return [first.copy(), *images, last.copy()]
