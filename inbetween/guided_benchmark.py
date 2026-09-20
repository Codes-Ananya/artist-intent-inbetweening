"""Controlled oracle-breakdown diagnostic for local interpolation backends."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from PIL import Image
from .benchmark import _finite_or_none, _landmark, _visuals
from .benchmark_cases import generate_assets
from .benchmark_metrics import endpoint_equal, metrics, trajectory_error
from .core import CrossfadeBackend
from .guided import create_guided_run
from .rife import RifeBackend
from .run import create_run

CATEGORIES = ("curved_arc", "hold_then_fast", "exaggeration", "occlusion")
BACKENDS = {"rife": RifeBackend, "crossfade": CrossfadeBackend}
METRIC_KEYS = ("psnr_db", "ssim", "edge_f1", "chamfer_px", "trajectory_error_px")


def _aggregate(frame_rows):
    result = {}
    for key in METRIC_KEYS:
        valid = [row[key] for row in frame_rows if row[key] is not None]
        perfect = sum(row["psnr_perfect_match"] for row in frame_rows) if key == "psnr_db" else 0
        # An infinite PSNR has no finite arithmetic mean with imperfect frames.
        result[key] = float(np.mean(valid)) if valid and not perfect else None
    return result


def run_guided_benchmark(output="outputs/guided-breakdown-benchmark", categories=CATEGORIES,
                         count=6, backend="rife", position=None, backend_factory=None):
    if count < 1 or count > 120:
        raise ValueError("Count must be from 1 to 120")
    k = position if position is not None else (count + 1) // 2
    if not 1 <= k <= count:
        raise ValueError("Breakdown position must be from 1 to count")
    root = Path(output)
    cases = generate_assets(root / "ground_truth", categories, count)
    factory = backend_factory or BACKENDS[backend]
    sequences, rows = [], []
    for case in cases:
        paths = [root / "ground_truth" / case.identifier / f"frame_{i:04d}.png" for i in range(count + 2)]
        for method in ("endpoint_only", "guided"):
            record = {"case_id": case.identifier, "method": method, "backend": backend,
                      "status": "failed", "error": None, "breakdown_position": k}
            try:
                model = factory()
                out = root / "runs" / case.identifier / method
                manifest = (create_guided_run(paths[0], paths[k], paths[-1], count, k, output_root=out, backend=model)
                            if method == "guided" else create_run(paths[0], paths[-1], count, output_root=out, backend=model))
                frames = [Image.open(path).copy() for path in manifest["frames"]]
                if len(frames) != len(case.frames):
                    raise ValueError("Output and ground truth frame counts differ")
                checks = {"A": endpoint_equal(frames[0], case.frames[0]),
                          "D": endpoint_equal(frames[k], case.frames[k]) if method == "guided" else None,
                          "B": endpoint_equal(frames[-1], case.frames[-1])}
                if checks["A"] is not True or checks["B"] is not True or (method == "guided" and checks["D"] is not True):
                    raise ValueError("Authoritative pixel mismatch")
                frame_rows = []
                for i in range(1, count + 1):
                    raw = metrics(case.frames[i], frames[i])
                    values = {key: _finite_or_none(value) for key, value in raw.items()}
                    observed = _landmark(frames[i])
                    values.update(case_id=case.identifier, method=method, frame_index=i,
                                  is_authoritative_breakdown=method == "guided" and i == k,
                                  psnr_perfect_match=bool(np.isposinf(raw["psnr_db"])),
                                  trajectory_error_px=_finite_or_none(trajectory_error([case.landmarks[i]], [observed])) if observed else None)
                    frame_rows.append(values)
                rows.extend(frame_rows)
                visual = root / "visuals" / case.identifier / method
                visual.mkdir(parents=True, exist_ok=True)
                _visuals(visual, case.frames, frames)
                evaluated = [r for r in frame_rows if r["frame_index"] != k]
                means = _aggregate(evaluated)
                measured = sum(r["trajectory_error_px"] is not None for r in evaluated)
                record.update(status="ok", frame_count=len(frames), exact_pixel_checks=checks,
                              means=means, generated_only_means=means,
                              generated_only_psnr_perfect_match_count=sum(r["psnr_perfect_match"] for r in evaluated),
                              generated_only_psnr_mean_undefined_due_to_perfect_match=any(r["psnr_perfect_match"] for r in evaluated),
                              breakdown_index_metrics=frame_rows[k - 1],
                              evaluated_frame_count=len(evaluated), evaluated_frame_indices=[r["frame_index"] for r in evaluated],
                              excluded_frame_indices=[k],
                              trajectory_measured_frames=measured, trajectory_total_frames=len(evaluated),
                              backend_wall_seconds=manifest["backend_wall_seconds"],
                              inference_seconds=manifest.get("inference_seconds"),
                              peak_cuda_memory_bytes=manifest.get("peak_cuda_memory_bytes"),
                              source_commit=manifest.get("source_commit"), checkpoint_id=manifest.get("checkpoint_id"),
                              manifest=str(Path(manifest["exports"]["png_sequence"]).parent / "manifest.json"))
            except Exception as exc:
                record["error"] = f"{type(exc).__name__}: {exc}"
            sequences.append(record)
    root.mkdir(parents=True, exist_ok=True)
    fields = ("case_id", "method", "frame_index", "is_authoritative_breakdown", "psnr_perfect_match", "psnr_db", "ssim", "edge_f1", "chamfer_px", "trajectory_error_px")
    with (root / "frames.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (root / "results.json").write_text(json.dumps({"protocol": "oracle breakdown diagnostic v1", "count": count,
        "breakdown_position": k, "sequences": sequences, "frames": rows}, indent=2, allow_nan=False) + "\n")
    lines = ["# Oracle breakdown diagnostic", "", "Ground-truth-derived D; no artist study or algorithm novelty claim.",
             f"Generated-only paired means evaluate indices 1..{count} excluding breakdown index {k} for both methods ({count - 1} frames). Index {k} is reported separately in results.json; guided D is authoritative/oracle, not generated output.",
             "PSNR mean is null when any evaluated frame is a perfect match (infinite PSNR); the perfect-match count is recorded in results.json.",
             "Runtime is an operational diagnostic, not a fair speed comparison: endpoint-only invokes the backend once; guided invokes it twice. Backend wall time may include different model-loading behavior. Guided per-segment diagnostics in guided_breakdown.segments are authoritative.", "",
             "| Case | Method | Status | Generated-only PSNR dB | Generated-only SSIM | Generated-only Edge F1 | Generated-only Chamfer px | Generated-only trajectory error px | Generated-only trajectory coverage | Backend wall s (diagnostic) | Inference s (diagnostic) | Peak CUDA bytes |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in sequences:
        m = r.get("means", {})
        fmt = lambda v: "—" if v is None else f"{v:.3f}"
        lines.append("| " + " | ".join(str(v) for v in (r["case_id"], r["method"], r["status"], *(fmt(m.get(key)) for key in ("psnr_db", "ssim", "edge_f1", "chamfer_px", "trajectory_error_px")),
            f"{r.get('trajectory_measured_frames', 0)}/{r.get('trajectory_total_frames', count)}" if m else "—",
            fmt(r.get("backend_wall_seconds")), fmt(r.get("inference_seconds")), r.get("peak_cuda_memory_bytes") or "—")) + " |")
        if r["error"]:
            lines.append(f"\nFailure: {r['case_id']} / {r['method']}: {r['error']}\n")
    (root / "summary.md").write_text("\n".join(lines) + "\n")
    return sequences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=BACKENDS, default="rife")
    parser.add_argument("--output", default="outputs/guided-breakdown-benchmark")
    parser.add_argument("--cases", nargs="+", choices=CATEGORIES, default=list(CATEGORIES))
    parser.add_argument("--count", type=int, default=6)
    parser.add_argument("--position", type=int)
    args = parser.parse_args()
    records = run_guided_benchmark(args.output, args.cases, args.count, args.backend, args.position)
    print(json.dumps(records, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
