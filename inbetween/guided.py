"""Split a timeline at an authoritative artist-supplied breakdown."""
from __future__ import annotations

import json
from pathlib import Path
import time
import numpy as np
from PIL import Image

from .core import InterpolationBackend, ValidationError, load_keyframes
from .run import create_run, _sha


def _equal(a: Image.Image, b: Image.Image) -> bool:
    return a.mode == b.mode and a.size == b.size and np.array_equal(np.asarray(a), np.asarray(b))


def _validate(first, breakdown, last, count, position):
    if any(image is None for image in (first, breakdown, last)):
        raise ValidationError("Keyframes A and B and breakdown D are all required")
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 120:
        raise ValidationError("Guided intermediate frame count must be an integer from 1 to 120")
    if not isinstance(position, int) or isinstance(position, bool) or not 1 <= position <= count:
        raise ValidationError("Breakdown position must be an integer from 1 to the intermediate frame count")
    if any(image.mode not in ("RGB", "RGBA") for image in (first, breakdown, last)) or len({image.mode for image in (first, breakdown, last)}) != 1:
        raise ValidationError("A, D and B must have identical RGB or RGBA modes")
    if len({image.size for image in (first, breakdown, last)}) != 1 or min(first.size) < 1:
        raise ValidationError("A, D and B must have identical nonzero dimensions")


class GuidedBackend(InterpolationBackend):
    def __init__(self, backend: InterpolationBackend, breakdown: Image.Image, position: int):
        if breakdown is None:
            raise ValidationError("Keyframes A and B and breakdown D are all required")
        self.backend = backend
        self.breakdown = breakdown.copy()
        self.position = position
        self.name = backend.name
        self.version = getattr(backend, "version", "unknown")
        self.last_run_metadata = {}

    def generate(self, first, last, intermediate_count):
        _validate(first, self.breakdown, last, intermediate_count, self.position)
        originals = (first.copy(), self.breakdown.copy(), last.copy())
        segments = []
        generated = []
        for start, end, count in ((first, self.breakdown, self.position - 1),
                                  (self.breakdown, last, intermediate_count - self.position)):
            began = time.perf_counter()
            frames = self.backend.generate(start.copy(), end.copy(), count)
            wall = time.perf_counter() - began
            if len(frames) != count + 2:
                raise RuntimeError(f"Backend returned {len(frames)} frames; expected {count + 2}")
            if not _equal(frames[0], start) or not _equal(frames[-1], end):
                raise RuntimeError("Backend changed an authoritative segment endpoint")
            segments.append({"generated_intermediate_count": count, "backend_wall_seconds": wall,
                             "diagnostics": dict(getattr(self.backend, "last_run_metadata", {}))})
            generated.append(frames)
        result = [originals[0], *generated[0][1:-1], originals[1], *generated[1][1:-1], originals[2]]
        indices = [0, self.position, intermediate_count + 1]
        checks = {label: _equal(original, result[index]) for label, original, index in zip(("A", "D", "B"), originals, indices)}
        if not all(checks.values()):
            raise RuntimeError("Authoritative frame pixel validation failed")
        metadata = dict(getattr(self.backend, "last_run_metadata", {}))
        # These describe only the final segment; retain them in segments instead.
        metadata.pop("preprocessing", None)
        metadata.pop("model_load_seconds", None)
        metadata.update({"requested_intermediate_count": intermediate_count,
                         "generated_intermediate_count": intermediate_count - 1,
                         "inferred_frame_count": intermediate_count - 1,
                         "preprocessing": None,
                         "model_load_seconds": None,
                         "inference_seconds": sum(s["diagnostics"].get("inference_seconds", s["backend_wall_seconds"]) for s in segments),
                         "peak_cuda_memory_bytes": max((s["diagnostics"].get("peak_cuda_memory_bytes") or 0 for s in segments), default=0) or None,
                         "guided_breakdown": {"position": self.position, "authoritative_frame_indices": indices,
                                              "requested_intermediate_count": intermediate_count,
                                              "inferred_frame_count": intermediate_count - 1,
                                              "backend_invocation_count": 2,
                                              "exact_pixel_checks": checks, "segments": segments}})
        self.last_run_metadata = metadata
        return result


def generate_with_breakdown(backend, first, breakdown, last, intermediate_count, breakdown_position):
    """Return N+2 frames with D at index k and exact A, D, B pixels."""
    return GuidedBackend(backend, breakdown, breakdown_position).generate(first, last, intermediate_count)


def create_guided_run(first, breakdown, last, intermediate_count, breakdown_position, fps=12,
                      output_root="outputs/guided", backend=None):
    if not first or not breakdown or not last:
        raise ValidationError("Keyframes A and B and breakdown D are all required")
    a, d = load_keyframes(first, breakdown)
    _, b = load_keyframes(breakdown, last)
    _validate(a, d, b, intermediate_count, breakdown_position)
    if backend is None:
        from .rife import RifeBackend
        backend = RifeBackend()
    guided = GuidedBackend(backend, d, breakdown_position)
    manifest = create_run(first, last, intermediate_count, fps, output_root, guided)
    manifest["guided_breakdown"]["input_sha256"] = {"A": _sha(Path(first)), "D": _sha(Path(breakdown)), "B": _sha(Path(last))}
    for label, index, source in (("A", 0, a), ("D", breakdown_position, d), ("B", intermediate_count + 1, b)):
        with Image.open(manifest["frames"][index]) as saved:
            manifest["guided_breakdown"]["exact_pixel_checks"][label] = _equal(source, saved)
    if not all(manifest["guided_breakdown"]["exact_pixel_checks"].values()):
        raise RuntimeError("Saved authoritative PNG pixel validation failed")
    path = Path(manifest["exports"]["png_sequence"]).parent / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return manifest
