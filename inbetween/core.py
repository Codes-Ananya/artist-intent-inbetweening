"""Validation and pluggable frame generation."""
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import numpy as np
from PIL import Image, UnidentifiedImageError


class ValidationError(ValueError):
    pass


def load_keyframes(first: str | Path, last: str | Path) -> tuple[Image.Image, Image.Image]:
    images = []
    for path in (first, last):
        try:
            with Image.open(path) as source:
                if source.format != "PNG":
                    raise ValidationError("Keyframes must be PNG files")
                if source.mode not in ("RGB", "RGBA"):
                    raise ValidationError("Keyframes must use RGB or RGBA color mode")
                source.load()
                images.append(source.copy())
        except (OSError, UnidentifiedImageError) as exc:
            raise ValidationError(f"Cannot read keyframe: {path}") from exc
    a, b = images
    if a.size != b.size:
        raise ValidationError("Keyframes must have identical dimensions")
    if a.mode != b.mode:
        raise ValidationError("Keyframes must have identical color modes and alpha presence")
    if min(a.size) < 1:
        raise ValidationError("Keyframes must have nonzero dimensions")
    return a, b


class InterpolationBackend(ABC):
    name: str

    @abstractmethod
    def generate(self, first: Image.Image, last: Image.Image, intermediate_count: int) -> list[Image.Image]:
        """Return endpoints and ordered intermediate frames."""


class CrossfadeBackend(InterpolationBackend):
    name = "deterministic_crossfade"
    version = "1"

    def generate(self, first: Image.Image, last: Image.Image, intermediate_count: int) -> list[Image.Image]:
        if not isinstance(intermediate_count, int) or not 0 <= intermediate_count <= 120:
            raise ValidationError("Intermediate frame count must be an integer from 0 to 120")
        if first.size != last.size or first.mode != last.mode or first.mode not in ("RGB", "RGBA"):
            raise ValidationError("Keyframes must have matching size and RGB/RGBA mode")
        a = np.asarray(first, dtype=np.uint16)
        b = np.asarray(last, dtype=np.uint16)
        frames = [first.copy()]
        denominator = intermediate_count + 1
        for index in range(1, denominator):
            pixels = ((a * (denominator - index) + b * index + denominator // 2) // denominator).astype(np.uint8)
            frames.append(Image.fromarray(pixels, mode=first.mode))
        frames.append(last.copy())
        return frames
