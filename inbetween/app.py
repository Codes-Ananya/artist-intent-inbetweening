"""Gradio user interface."""
import os
from pathlib import Path
import gradio as gr
from .diagnostics import collect
from .run import create_run


def generate(first, last, count, fps):
    if not first or not last:
        raise gr.Error("Upload both PNG keyframes")
    try:
        manifest = create_run(first, last, int(count), int(fps))
    except (ValueError, RuntimeError) as exc:
        raise gr.Error(str(exc)) from exc
    frames = manifest["frames"]
    gallery = [(path, f"Frame {index} / {len(frames)-1}") for index, path in enumerate(frames)]
    return gallery, gr.Slider(maximum=len(frames)-1, value=0), frames[0], manifest["exports"]["gif"], manifest["exports"]["mp4"], [str(path) for path in sorted(Path(manifest["exports"]["png_sequence"]).glob("*.png"))], str(Path(manifest["exports"]["png_sequence"]).parent / "manifest.json"), manifest


def show_frame(index, gallery):
    if not gallery:
        return None
    return gallery[int(index)][0]


def build_app():
    with gr.Blocks(title="Animation In-Betweening MVP") as app:
        gr.Markdown("# Animation In-Betweening MVP\nUpload two matching RGB or RGBA PNG keyframes. The placeholder backend produces a deterministic crossfade.")
        with gr.Row():
            first = gr.File(label="First keyframe", file_types=[".png"], type="filepath")
            last = gr.File(label="Last keyframe", file_types=[".png"], type="filepath")
        count = gr.Slider(0, 120, value=6, step=1, label="Intermediate frames")
        fps = gr.Slider(1, 60, value=12, step=1, label="Playback FPS")
        button = gr.Button("Generate")
        gallery = gr.Gallery(label="Timeline", columns=6, height=200)
        index = gr.Slider(0, 1, value=0, step=1, label="Frame-by-frame viewer")
        viewer = gr.Image(label="Selected frame", interactive=False)
        playback = gr.Image(label="Animation playback (GIF)", interactive=False)
        with gr.Row():
            mp4 = gr.File(label="MP4")
            pngs = gr.File(label="PNG sequence", file_count="multiple")
            manifest_file = gr.File(label="JSON manifest")
        manifest_json = gr.JSON(label="Run details and CUDA diagnostics")
        button.click(generate, [first, last, count, fps], [gallery, index, viewer, playback, mp4, pngs, manifest_file, manifest_json])
        index.change(show_frame, [index, gallery], viewer)
        gr.JSON(value=collect(), label="Current system diagnostics")
    return app


if __name__ == "__main__":
    build_app().launch(server_name="127.0.0.1", server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")))
