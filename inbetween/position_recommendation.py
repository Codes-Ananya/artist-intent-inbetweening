"""Ground-truth-free, deterministic endpoint-sequence risk diagnostic."""
import numpy as np
from .benchmark_metrics import gray, edges


def normalize(values):
    finite = [v for v in values if v is not None and np.isfinite(v)]
    low, high = (min(finite), max(finite)) if finite else (0, 0)
    return [None if v is None or not np.isfinite(v) else
            (float((v - low) / (high - low)) if high > low else 0.0) for v in values]


def recommend_position(frames):
    """Accept only A, endpoint-generated intermediates, B. No case or D input."""
    if not 3 <= len(frames) <= 122 or len({im.size for im in frames}) != 1:
        raise ValueError("Provide matching A, 1–120 generated positions, and B")
    gs = [gray(im).astype(float) for im in frames]
    es = [edges(im) for im in frames]
    masks = [g < 80 for g in gs]
    areas = [float(m.mean()) for m in masks]
    centers = [np.array(np.nonzero(m)).mean(axis=1) if m.any() else None for m in masks]
    differences = [float(np.mean(np.abs(a-b))) for a, b in zip(gs, gs[1:])]
    rows = []
    for k in range(1, len(frames)-1):
        centers_valid = all(c is not None for c in centers[k-1:k+2])
        raw = {
            "edge_change": float((np.mean(es[k-1] != es[k]) + np.mean(es[k] != es[k+1])) / 2),
            "difference_imbalance": abs(differences[k-1] - differences[k]),
            "area_change": abs(areas[k]-areas[k-1]) + abs(areas[k+1]-areas[k]),
            "centroid_acceleration": float(np.linalg.norm(centers[k+1]-2*centers[k]+centers[k-1])) if centers_valid else None,
        }
        rows.append({"k": k, "raw": raw, "normalized": {}, "missing": [key for key, v in raw.items() if v is None]})
    # A common component set prevents missing centroids changing relative weights.
    active = [key for key in rows[0]["raw"] if all(r["raw"][key] is not None for r in rows)]
    for key in rows[0]["raw"]:
        for row, value in zip(rows, normalize([r["raw"][key] for r in rows])):
            row["normalized"][key] = value
    for row in rows:
        row["score"] = float(np.mean([row["normalized"][key] for key in active])) if active else 0.0
        row["valid"] = bool(active)
    valid = [r for r in rows if r["valid"]]
    return {"recommended_k": min(valid, key=lambda r: (-r["score"], r["k"]))["k"] if valid else None,
            "active_components": active, "positions": rows, "experimental": True}
