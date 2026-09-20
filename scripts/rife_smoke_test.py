#!/usr/bin/env python3
"""Normal-shell CUDA acceptance test for the optional RIFE baseline."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inbetween.run import create_run
from inbetween.rife import RifeBackend
from inbetween.sample import make_samples


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    try:
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is unavailable; run this test in the normal WSL shell with GPU access")
        first, last = make_samples(ROOT / "samples")
        manifest = create_run(first, last, 2, fps=12, output_root=args.output_root, backend=RifeBackend())
        for source, generated in ((first, manifest["frames"][0]), (last, manifest["frames"][-1])):
            with Image.open(source) as original, Image.open(generated) as saved:
                if not np.array_equal(np.asarray(original), np.asarray(saved)):
                    raise RuntimeError(f"Endpoint pixels changed: {source}")
        if manifest["frame_count"] != 4:
            raise RuntimeError(f"Expected 4 frames, got {manifest['frame_count']}")
        print(f"Model: {manifest['backend_version']} | {manifest['checkpoint_id']} | {manifest['checkpoint_sha256']}")
        print(f"Frames: {manifest['frame_count']} (2 intermediates)")
        print(f"Inference: {manifest['inference_seconds']:.3f} s")
        print(f"Peak CUDA memory: {manifest['peak_cuda_memory_bytes'] / 1048576:.1f} MiB")
        print(f"Output: {Path(manifest['exports']['png_sequence']).parent}")
        print("Endpoint pixel comparison: exact")
        return 0
    except Exception as exc:
        print(f"RIFE smoke test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
