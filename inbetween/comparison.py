"""Independent two-baseline comparison runs."""
from pathlib import Path
import re
from PIL import Image
from .benchmark_cases import CATEGORIES, generate_assets
from .benchmark_metrics import metrics, endpoint_equal
from .core import CrossfadeBackend
from .rife import RifeBackend
from .run import create_run


def compare(first=None,last=None,count=6,fps=12,ground_truth=None,benchmark_case=None,output='outputs/comparison',backend_factories=None):
    count=int(count);fps=int(fps)
    if benchmark_case:
        if benchmark_case not in CATEGORIES: raise ValueError('Unknown benchmark case')
        case=generate_assets(Path(output)/'ground_truth',[benchmark_case],count)[0]
        first=Path(output)/'ground_truth'/benchmark_case/'frame_0000.png'
        last=Path(output)/'ground_truth'/benchmark_case/f'frame_{count+1:04d}.png'
        truth=case.frames
    elif ground_truth:
        if len(ground_truth)<3 or len(ground_truth)!=count+2:
            raise ValueError('Ground truth requires at least three frames and exactly count + 2 frames')
        paths=[Path(p) for p in ground_truth]
        names=[p.name for p in paths]
        if len(set(names))!=len(names): raise ValueError('Ground truth filenames must be unique')
        matches=[re.fullmatch(r'(.*?)(\d+)(\.[Pp][Nn][Gg])',name) for name in names]
        if any(m is None for m in matches) or len({(m.group(1),m.group(3).lower()) for m in matches})!=1:
            raise ValueError('Ground truth ordering is ambiguous; use one filename prefix and numeric frame suffix')
        numbers=[int(m.group(2)) for m in matches]
        if len(set(numbers))!=len(numbers): raise ValueError('Ground truth frame numbers must be unique')
        paths=[p for _,p in sorted(zip(numbers,paths))]
        truth=[Image.open(p).copy() for p in paths]
        if any(im.size!=truth[0].size for im in truth): raise ValueError('Ground truth sizes differ')
        with Image.open(first) as first_image, Image.open(last) as last_image:
            if not endpoint_equal(first_image,truth[0]) or not endpoint_equal(last_image,truth[-1]):
                raise ValueError('Ground truth endpoints differ from uploaded keyframes')
    else: truth=None
    if not first or not last: raise ValueError('Provide both keyframes or select a benchmark case')
    factories=backend_factories or {'crossfade':CrossfadeBackend,'rife':RifeBackend}
    result={}
    for name in ('crossfade','rife'):
        try:
            manifest=create_run(first,last,count,fps,Path(output)/name,backend=factories[name]())
            record={'status':'ok','manifest':manifest}
            if truth:
                frames=[Image.open(p).copy() for p in manifest['frames']]
                record['metrics']={k:sum(metrics(a,b)[k] for a,b in zip(truth[1:-1],frames[1:-1]))/count for k in ('psnr_db','ssim','edge_f1','chamfer_px')} if count else {}
            result[name]=record
        except Exception as exc:
            result[name]={'status':'failed','error':f'{type(exc).__name__}: {exc}'}
    return result
