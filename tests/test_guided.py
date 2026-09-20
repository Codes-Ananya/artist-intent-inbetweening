import json
import os
import subprocess
import sys
import numpy as np
import pytest
import gradio as gr
from PIL import Image
from inbetween.core import CrossfadeBackend, ValidationError
from inbetween.guided import create_guided_run, generate_with_breakdown
from inbetween.guided_benchmark import run_guided_benchmark
from inbetween import guided_benchmark
from inbetween import app


class Fake(CrossfadeBackend):
    name = "fake"
    def __init__(self):
        self.counts = []
    def generate(self, first, last, count):
        self.counts.append(count)
        return super().generate(first, last, count)


def images():
    return [Image.new("RGB", (8, 8), (v, v, v)) for v in (0, 100, 255)]


@pytest.mark.parametrize("n,k", [(1, 1), (2, 1), (2, 2), (6, 3), (6, 6)])
def test_timeline_exactness_and_determinism(n, k):
    a, d, b = images()
    fake = Fake()
    frames = generate_with_breakdown(fake, a, d, b, n, k)
    assert len(frames) == n + 2
    assert fake.counts == [k - 1, n - k]
    assert [np.array_equal(np.asarray(frames[i]), np.asarray(x)) for i, x in ((0, a), (k, d), (n + 1, b))] == [True] * 3
    assert sum(np.array_equal(np.asarray(frame), np.asarray(d)) for frame in frames) == 1
    again = generate_with_breakdown(Fake(), a, d, b, n, k)
    assert all(np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(frames, again))
    assert len(CrossfadeBackend().generate(a, b, n)) == n + 2


@pytest.mark.parametrize("k", [0, 4, -1, 1.5, True])
def test_invalid_position(k):
    with pytest.raises(ValidationError, match="Breakdown position"):
        generate_with_breakdown(Fake(), *images(), 3, k)


def test_missing_dimension_mode_and_failure():
    a, d, b = images()
    with pytest.raises(ValidationError, match="required"):
        generate_with_breakdown(Fake(), a, None, b, 2, 1)
    with pytest.raises(ValidationError, match="dimensions"):
        generate_with_breakdown(Fake(), a, Image.new("RGB", (9, 8)), b, 2, 1)
    with pytest.raises(ValidationError, match="modes"):
        generate_with_breakdown(Fake(), a, Image.new("RGBA", a.size), b, 2, 1)
    class Failing(Fake):
        def generate(self, *args):
            raise RuntimeError("inference failed")
    with pytest.raises(RuntimeError, match="inference failed"):
        generate_with_breakdown(Failing(), a, d, b, 2, 1)


def test_manifest_and_saved_pixels(tmp_path):
    paths = [tmp_path / f"{x}.png" for x in "adb"]
    for image, path in zip(images(), paths):
        image.save(path)
    manifest = create_guided_run(paths[0], paths[1], paths[2], 3, 2, output_root=tmp_path / "out", backend=Fake())
    guided = manifest["guided_breakdown"]
    assert guided["authoritative_frame_indices"] == [0, 2, 4]
    assert guided["requested_intermediate_count"] == 3
    assert guided["inferred_frame_count"] == 2
    assert manifest["requested_intermediate_count"] == 3 and manifest["inferred_frame_count"] == 2
    assert manifest["preprocessing"] is None and manifest["model_load_seconds"] is None
    assert guided["exact_pixel_checks"] == {"A": True, "D": True, "B": True}
    assert [s["generated_intermediate_count"] for s in guided["segments"]] == [1, 1]
    assert len(guided["input_sha256"]) == 3
    assert json.loads((tmp_path / "out" / manifest["run_id"] / "manifest.json").read_text())["guided_breakdown"] == guided


def test_benchmark_counts_strict_json_and_failure_isolation(tmp_path):
    records = run_guided_benchmark(tmp_path / "ok", ["curved_arc"], 2, "crossfade", backend_factory=Fake)
    assert [r["status"] for r in records] == ["ok", "ok"]
    assert [r["frame_count"] for r in records] == [4, 4]
    raw = (tmp_path / "ok" / "results.json").read_text()
    json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    result = json.loads(raw)
    for record in records:
        assert record["evaluated_frame_indices"] == [2]
        assert record["excluded_frame_indices"] == [1]
        assert record["evaluated_frame_count"] == record["trajectory_total_frames"] == 1
        assert record["breakdown_index_metrics"]["frame_index"] == 1
    assert result["sequences"][1]["breakdown_index_metrics"]["is_authoritative_breakdown"]
    assert not result["sequences"][0]["breakdown_index_metrics"]["is_authoritative_breakdown"]
    assert "Generated-only paired means" in (tmp_path / "ok" / "summary.md").read_text()
    assert "not a fair speed comparison" in (tmp_path / "ok" / "summary.md").read_text()
    class Failing(Fake):
        def generate(self, *args):
            raise RuntimeError("boom")
    failed = run_guided_benchmark(tmp_path / "fail", ["curved_arc", "occlusion"], 2, "crossfade", backend_factory=Failing)
    assert len(failed) == 4 and all(r["status"] == "failed" for r in failed)


def test_oracle_cannot_inflate_primary_means_and_perfect_psnr(tmp_path, monkeypatch):
    values = iter([0.4, 0.4, 1.0, 0.2])
    def metric_stub(*args):
        score = next(values)
        return {"psnr_db": float("inf") if score == 1.0 else score,
                "ssim": score, "edge_f1": score, "chamfer_px": score}
    monkeypatch.setattr(guided_benchmark, "metrics", metric_stub)
    records = run_guided_benchmark(tmp_path / "benchmark", ["curved_arc"], 2, "crossfade", 1, Fake)
    assert [r["evaluated_frame_indices"] for r in records] == [[2], [2]]
    for key in ("psnr_db", "ssim", "edge_f1", "chamfer_px"):
        assert records[0]["means"][key] == pytest.approx(0.4)
        assert records[1]["means"][key] == pytest.approx(0.2)
    assert records[1]["means"]["trajectory_error_px"] == next(
        row["trajectory_error_px"] for row in json.loads((tmp_path / "benchmark" / "results.json").read_text())["frames"]
        if row["method"] == "guided" and row["frame_index"] == 2)
    assert records[1]["breakdown_index_metrics"]["psnr_db"] is None
    assert records[1]["breakdown_index_metrics"]["psnr_perfect_match"] is True
    raw = (tmp_path / "benchmark" / "results.json").read_text()
    json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def test_perfect_evaluated_psnr_has_explicit_undefined_mean(tmp_path, monkeypatch):
    monkeypatch.setattr(guided_benchmark, "metrics", lambda *args: {"psnr_db": float("inf"), "ssim": 1.0, "edge_f1": 1.0, "chamfer_px": 0.0})
    records = run_guided_benchmark(tmp_path / "perfect", ["curved_arc"], 2, "crossfade", 1, Fake)
    assert all(r["means"]["psnr_db"] is None for r in records)
    assert all(r["generated_only_psnr_perfect_match_count"] == 1 for r in records)
    assert all(r["generated_only_psnr_mean_undefined_due_to_perfect_match"] for r in records)
    json.loads((tmp_path / "perfect" / "results.json").read_text(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def test_cli_and_ui_failure(tmp_path, monkeypatch):
    root = str(__import__("pathlib").Path(__file__).resolve().parents[1])
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run([sys.executable, "-m", "inbetween.guided_benchmark", "--help"], cwd=root, env=env, capture_output=True, text=True)
    assert result.returncode == 0 and "--backend" in result.stdout
    from scripts import guided_rife_smoke_test
    monkeypatch.setattr(guided_rife_smoke_test, "run_guided_benchmark", lambda *a, **kw: [{"status": "ok"}] * 2)
    guided_rife_smoke_test.main()
    selected = []
    class Failing:
        def __init__(self):
            selected.append("rife")
    monkeypatch.setattr(app, "RifeBackend", Failing)
    monkeypatch.setattr(app, "create_run", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("RIFE failed")))
    paths = [tmp_path / f"{name}.png" for name in "adb"]
    for image, path in zip(images(), paths):
        image.save(path)
    with pytest.raises(gr.Error, match="RIFE failed"):
        app.guided_compare_ui(*paths, 2, 1, 12)
    assert selected == ["rife"]
