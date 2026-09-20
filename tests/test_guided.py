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
    class Failing(Fake):
        def generate(self, *args):
            raise RuntimeError("boom")
    failed = run_guided_benchmark(tmp_path / "fail", ["curved_arc", "occlusion"], 2, "crossfade", backend_factory=Failing)
    assert len(failed) == 4 and all(r["status"] == "failed" for r in failed)


def test_cli_and_ui_failure(tmp_path, monkeypatch):
    root = str(__import__("pathlib").Path(__file__).resolve().parents[1])
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run([sys.executable, "-m", "inbetween.guided_benchmark", "--help"], cwd=root, env=env, capture_output=True, text=True)
    assert result.returncode == 0 and "--backend" in result.stdout
    smoke = subprocess.run([sys.executable, "scripts/guided_rife_smoke_test.py"], cwd=root, env=env, capture_output=True, text=True)
    assert "ModuleNotFoundError" not in smoke.stderr
    assert smoke.returncode in (0, 1)
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
