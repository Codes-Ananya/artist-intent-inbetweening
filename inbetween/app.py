"""Gradio user interface."""
import os
from pathlib import Path
import gradio as gr
from .diagnostics import collect
from .run import create_run
from .core import CrossfadeBackend
from .rife import RifeBackend
from .comparison import compare
from .benchmark_cases import CATEGORIES


def select_backend(label: str):
    if label == "Crossfade baseline":
        return CrossfadeBackend()
    if label == "RIFE local AI baseline":
        return RifeBackend()
    raise ValueError(f"Unknown backend: {label}")


def generate(first, last, count, fps, backend_label="Crossfade baseline"):
    if not first or not last:
        raise gr.Error("Upload both PNG keyframes")
    try:
        manifest = create_run(first, last, int(count), int(fps), backend=select_backend(backend_label))
    except (ValueError, RuntimeError) as exc:
        raise gr.Error(str(exc)) from exc
    frames = manifest["frames"]
    gallery = [(path, f"Frame {index} / {len(frames)-1}") for index, path in enumerate(frames)]
    return gallery, gr.Slider(maximum=len(frames)-1, value=0), frames[0], manifest["exports"]["gif"], manifest["exports"]["mp4"], [str(path) for path in sorted(Path(manifest["exports"]["png_sequence"]).glob("*.png"))], str(Path(manifest["exports"]["png_sequence"]).parent / "manifest.json"), manifest


def show_frame(index, gallery):
    if not gallery:
        return None
    return gallery[int(index)][0]



def compare_ui(first,last,count,fps,ground_truth,benchmark_case):
    result=compare(first,last,int(count),int(fps),ground_truth,benchmark_case or None)
    outputs=[]
    for name in ('crossfade','rife'):
        record=result[name]
        if record['status']!='ok':
            outputs.extend([None,[],[],None,None,None,record['error']])
            continue
        manifest=record['manifest']
        frames=manifest['frames']
        details={key:manifest.get(key) for key in ('backend','backend_version','backend_wall_seconds','inference_seconds','model_load_seconds','peak_cuda_memory_bytes','checkpoint_id','source_commit')}
        if 'metrics' in record: details['synthetic_or_supplied_ground_truth_metrics']=record['metrics']
        outputs.extend([manifest['exports']['gif'],[(p,f'Frame {i}') for i,p in enumerate(frames)],frames,manifest['exports']['gif'],manifest['exports']['mp4'],str(Path(frames[0]).parent.parent/'manifest.json'),details])
    return outputs

def build_app():
    with gr.Blocks(title="Animation In-Betweening MVP") as app:
        gr.Markdown("# Animation In-Betweening MVP\nUpload two matching RGB or RGBA PNG keyframes. Choose a deterministic crossfade or optional local RIFE baseline. RIFE requires installed assets and CUDA.")
        with gr.Row():
            first = gr.File(label="First keyframe", file_types=[".png"], type="filepath")
            last = gr.File(label="Last keyframe", file_types=[".png"], type="filepath")
        backend_choice = gr.Radio(["Crossfade baseline", "RIFE local AI baseline"], value="Crossfade baseline", label="Interpolation backend")
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
        button.click(generate, [first, last, count, fps, backend_choice], [gallery, index, viewer, playback, mp4, pngs, manifest_file, manifest_json])
        index.change(show_frame, [index, gallery], viewer)
        with gr.Tab("Compare baselines"):
            gr.Markdown("Both backends use the same endpoints and timestamps. Metrics appear only with a complete ground truth sequence or a built-in synthetic case. No quality ranking is implied for uploads without ground truth.")
            with gr.Row():
                cfirst=gr.File(label="Start PNG",file_types=[".png"],type="filepath")
                clast=gr.File(label="End PNG",file_types=[".png"],type="filepath")
            ccase=gr.Dropdown(["",*CATEGORIES],value="",label="Built-in synthetic case (optional)")
            ctruth=gr.File(label="Complete ordered ground truth PNGs (optional)",file_types=[".png"],type="filepath",file_count="multiple")
            ccount=gr.Slider(1,120,value=6,step=1,label="Intermediate frames")
            cfps=gr.Slider(1,60,value=12,step=1,label="FPS")
            cbutton=gr.Button("Compare")
            comparison_outputs=[]
            with gr.Row():
                for title in ("Crossfade","RIFE"):
                    with gr.Column():
                        gr.Markdown(f"### {title}")
                        gif=gr.Image(label="Animation",interactive=False)
                        strip=gr.Gallery(label="Synchronized frame strip",columns=4,height=200)
                        png=gr.File(label="PNG sequence",file_count="multiple")
                        gif_file=gr.File(label="GIF")
                        mp4_file=gr.File(label="MP4")
                        manifest_file=gr.File(label="Manifest")
                        details=gr.JSON(label="Runtime, identity, VRAM, metrics or failure")
                        comparison_outputs.extend([gif,strip,png,gif_file,mp4_file,manifest_file,details])
            cbutton.click(compare_ui,[cfirst,clast,ccount,cfps,ctruth,ccase],comparison_outputs)
        gr.JSON(value=collect(), label="Current system diagnostics")
    return app


if __name__ == "__main__":
    build_app().launch(server_name="127.0.0.1", server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")))
