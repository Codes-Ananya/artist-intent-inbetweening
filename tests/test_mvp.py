import json
from pathlib import Path
import numpy as np
import pytest
from PIL import Image
from inbetween.core import CrossfadeBackend, ValidationError, load_keyframes
from inbetween.run import create_run


def keyframes(tmp_path, mode="RGBA", size=(16, 12)):
    a = Image.new(mode, size, (10, 30, 80, 0) if mode == "RGBA" else (10, 30, 80))
    b = Image.new(mode, size, (240, 200, 20, 255) if mode == "RGBA" else (240, 200, 20))
    paths = [tmp_path / "a.png", tmp_path / "b.png"]
    a.save(paths[0]); b.save(paths[1])
    return paths


def test_endpoint_order_count_and_determinism(tmp_path):
    paths = keyframes(tmp_path)
    a, b = load_keyframes(*paths)
    backend = CrossfadeBackend()
    frames = backend.generate(a, b, 3)
    assert len(frames) == 5
    assert np.array_equal(np.asarray(frames[0]), np.asarray(a))
    assert np.array_equal(np.asarray(frames[-1]), np.asarray(b))
    assert [frame.getpixel((0, 0))[0] for frame in frames] == sorted(frame.getpixel((0, 0))[0] for frame in frames)
    again = backend.generate(a, b, 3)
    assert all(np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(frames, again))


@pytest.mark.parametrize("change", ["size", "mode", "format", "corrupt"])
def test_image_validation(tmp_path, change):
    paths = keyframes(tmp_path)
    if change == "size":
        Image.new("RGBA", (4, 4)).save(paths[1])
    elif change == "mode":
        Image.new("RGB", (16, 12)).save(paths[1])
    elif change == "format":
        paths[1] = tmp_path / "b.jpg"
        Image.new("RGB", (16, 12)).save(paths[1])
    else:
        paths[1].write_bytes(b"broken")
    with pytest.raises(ValidationError):
        load_keyframes(*paths)


def test_run_manifest_exports_and_pixel_exact_endpoints(tmp_path):
    paths = keyframes(tmp_path)
    manifest = create_run(*paths, 3, fps=12, output_root=tmp_path / "outputs")
    assert manifest["frame_count"] == 5
    assert len(manifest["frames"]) == 5
    assert all(Path(path).is_file() for path in manifest["frames"])
    assert all(Path(path).exists() for path in manifest["exports"].values())
    folder = Path(manifest["exports"]["png_sequence"]).parent
    assert json.loads((folder / "manifest.json").read_text())["run_id"] == manifest["run_id"]
    assert [json.loads(line)["event"] for line in (folder / "events.jsonl").read_text().splitlines()] == ["run_started", "run_completed"]
    for source, output in zip(paths, (manifest["frames"][0], manifest["frames"][-1])):
        assert np.array_equal(np.asarray(Image.open(source)), np.asarray(Image.open(output)))
    assert Path(manifest["exports"]["gif"]).stat().st_size > 0
    assert Path(manifest["exports"]["mp4"]).stat().st_size > 0
