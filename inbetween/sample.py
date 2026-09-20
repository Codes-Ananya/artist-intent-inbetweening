"""Generate small synthetic keyframes and a complete local sample run."""
from pathlib import Path
from PIL import Image, ImageDraw
from .run import create_run


def make_samples(folder: str | Path = "samples") -> tuple[Path, Path]:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    paths = (folder / "keyframe_start.png", folder / "keyframe_end.png")
    for index, path in enumerate(paths):
        image = Image.new("RGBA", (256, 144), (245, 243, 235, 255))
        draw = ImageDraw.Draw(image)
        x = 25 + 145 * index
        draw.ellipse((x, 42, x + 62, 104), fill=(52, 112, 218, 255), outline=(25, 40, 70, 255), width=3)
        draw.line((0, 119, 255, 119), fill=(75, 76, 78, 255), width=3)
        image.save(path)
    return paths


if __name__ == "__main__":
    a, b = make_samples()
    print(create_run(a, b, 6)["run_id"])
