import io
from pathlib import Path
import numpy as np
import pytest
import gradio as gr
from PIL import Image
from inbetween import app as app_module
from inbetween.app import select_backend
from inbetween.core import CrossfadeBackend
from inbetween.rife import RifeBackend, RifeError, timestamps_for_count
from inbetween.run import create_run
from scripts import setup_rife


def test_selection():
    assert isinstance(select_backend("Crossfade baseline"), CrossfadeBackend)
    assert isinstance(select_backend("RIFE local AI baseline"), RifeBackend)
    with pytest.raises(ValueError, match="Unknown backend"):
        select_backend("other")


def test_arbitrary_timestamp_order():
    assert timestamps_for_count(0) == []
    assert timestamps_for_count(2) == [1 / 3, 2 / 3]
    assert timestamps_for_count(7) == [i / 8 for i in range(1, 8)]


def test_missing_checkpoint(tmp_path):
    backend = RifeBackend(tmp_path)
    with pytest.raises(RifeError, match="assets are missing"):
        backend.generate(Image.new("RGB", (8, 8)), Image.new("RGB", (8, 8)), 1)


def test_cuda_unavailable(tmp_path, monkeypatch):
    source = tmp_path / "source" / "model"
    source.mkdir(parents=True)
    (source / "RIFE.py").write_text("", encoding="utf-8")
    checkpoint = tmp_path / setup_rife.CHECKPOINT_ID
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_bytes(b"fake")
    monkeypatch.setattr("inbetween.rife.sha256", lambda path: setup_rife.CHECKPOINT_SHA256)
    monkeypatch.setattr("inbetween.rife.subprocess.check_output", lambda *a, **k: setup_rife.SOURCE_COMMIT)
    import torch
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    with pytest.raises(RifeError, match="CUDA is unavailable"):
        RifeBackend(tmp_path).generate(Image.new("RGB", (8, 8)), Image.new("RGB", (8, 8)), 1)


def test_endpoint_count_timestamps_and_manifest(tmp_path, monkeypatch):
    first, last = tmp_path / "a.png", tmp_path / "b.png"
    Image.new("RGBA", (16, 12), (10, 20, 30, 0)).save(first)
    Image.new("RGBA", (16, 12), (200, 210, 220, 255)).save(last)
    backend = RifeBackend(tmp_path)
    monkeypatch.setattr(backend, "_require_assets_and_cuda", lambda: (object(), tmp_path))
    captured = []
    def fake_infer(a, b, times, torch, source):
        captured.extend(times)
        return [Image.new("RGB", a.size, (70 + i, 80, 90)) for i in range(len(times))], {"working_size": list(a.size), "padding": {}}, 0.25, 123456
    monkeypatch.setattr(backend, "_infer_rgb", fake_infer)
    manifest = create_run(first, last, 4, output_root=tmp_path / "out", backend=backend)
    assert captured == [i / 5 for i in range(1, 5)]
    assert manifest["frame_count"] == 6
    assert manifest["requested_intermediate_count"] == manifest["generated_intermediate_count"] == 4
    assert manifest["source_commit"] == setup_rife.SOURCE_COMMIT
    assert manifest["checkpoint_sha256"] == setup_rife.CHECKPOINT_SHA256
    assert manifest["device"] == "cuda:0" and manifest["dtype"] == "float32"
    assert manifest["inference_seconds"] == 0.25 and manifest["peak_cuda_memory_bytes"] == 123456
    for source, saved in ((first, manifest["frames"][0]), (last, manifest["frames"][-1])):
        assert np.array_equal(np.asarray(Image.open(source)), np.asarray(Image.open(saved)))


def test_backend_failure_does_not_fallback(tmp_path, monkeypatch):
    first, last = tmp_path / "a.png", tmp_path / "b.png"
    Image.new("RGB", (8, 8)).save(first)
    Image.new("RGB", (8, 8)).save(last)
    backend = RifeBackend(tmp_path)
    monkeypatch.setattr(backend, "_require_assets_and_cuda", lambda: (object(), tmp_path))
    def fail(*args):
        raise RifeError("model failed")
    monkeypatch.setattr(backend, "_infer_rgb", fail)
    with pytest.raises(RifeError, match="model failed"):
        create_run(first, last, 1, output_root=tmp_path / "out", backend=backend)
    assert not (tmp_path / "out").exists()


def test_out_of_memory_raises_clear_rife_error(tmp_path, monkeypatch):
    import torch
    backend = RifeBackend(tmp_path)
    monkeypatch.setattr(backend, "_require_assets_and_cuda", lambda: (torch, tmp_path))

    class FakeFlownet:
        def load_state_dict(self, state, strict=True):
            pass

    class FakeModel:
        def __init__(self, arbitrary=True):
            self.flownet = FakeFlownet()

        def device(self):
            pass

        def eval(self):
            pass

        def inference(self, a, b, timestep):
            raise torch.cuda.OutOfMemoryError("CUDA out of memory: fake allocation failure")

    fake_module = type("FakeRifeModule", (), {"Model": FakeModel})
    monkeypatch.setattr("inbetween.rife.importlib.import_module", lambda name: fake_module)
    monkeypatch.setattr(torch, "load", lambda *a, **k: {})
    with pytest.raises(RifeError, match="ran out of GPU memory"):
        backend.generate(Image.new("RGB", (8, 8)), Image.new("RGB", (8, 8)), 1)


def test_ui_error_does_not_substitute_crossfade_backend(monkeypatch):
    def fail_create_run(*args, **kwargs):
        raise RifeError("model failed")

    monkeypatch.setattr(app_module, "create_run", fail_create_run)
    selected = []
    real_select_backend = select_backend

    def tracking_select_backend(label):
        backend = real_select_backend(label)
        selected.append(type(backend))
        return backend

    monkeypatch.setattr(app_module, "select_backend", tracking_select_backend)
    with pytest.raises(gr.Error):
        app_module.generate("first.png", "last.png", 1, 12, backend_label="RIFE local AI baseline")
    assert selected == [RifeBackend]


def test_setup_checksum_and_download(tmp_path, monkeypatch):
    payload = b"small fake archive"
    import hashlib
    expected = hashlib.sha256(payload).hexdigest()
    class Response(io.BytesIO):
        headers = {"Content-Length": str(len(payload))}
    monkeypatch.setattr(setup_rife.urllib.request, "urlopen", lambda *a, **k: Response(payload))
    path = tmp_path / "archive.zip"
    setup_rife.download("https://example.test/archive", path, expected, len(payload))
    setup_rife.download("https://example.test/archive", path, expected, len(payload))
    assert path.read_bytes() == payload
    with pytest.raises(RuntimeError, match="Checksum mismatch"):
        setup_rife.verify_checksum(path, "0" * 64)
    bad = tmp_path / "bad.zip"
    with pytest.raises(RuntimeError, match="Download size mismatch"):
        setup_rife.download("https://example.test/archive", bad, expected, len(payload) + 1)
    assert not bad.exists() and not bad.with_suffix(".zip.part").exists()
