"""CLI evaluation of fixed synthetic line-art stress cases."""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
from .benchmark_cases import CATEGORIES, generate_assets
from .benchmark_metrics import metrics, endpoint_equal, edges, trajectory_error
from .core import CrossfadeBackend
from .rife import RifeBackend
from .run import create_run

BACKENDS={'crossfade':CrossfadeBackend,'rife':RifeBackend}


def _landmark(image):
    # Dark-pixel centroid, diagnostic proxy for body motion (not an annotated joint).
    a=np.asarray(image.convert('L'))<80
    ys,xs=np.nonzero(a)
    return (float(xs.mean()),float(ys.mean())) if len(xs) else None


def _finite_or_none(value):
    return float(value) if value is not None and math.isfinite(value) else None


def _visuals(folder, truth, frames, fps=12):
    width,height=truth[0].size
    sheet=Image.new('RGB',(width*3,height*len(truth)),'white')
    comparisons=[]
    for i,(gt,pred) in enumerate(zip(truth,frames)):
        diff=Image.fromarray(np.abs(np.asarray(gt,dtype=np.int16)-np.asarray(pred,dtype=np.int16)).astype(np.uint8))
        for j,image in enumerate((gt,pred,diff)):
            sheet.paste(image,(j*width,i*height))
        panel=Image.new('RGB',(width*2,height),'white')
        panel.paste(gt,(0,0));panel.paste(pred,(width,0))
        comparisons.append(panel)
    sheet.save(folder/'contact_sheet.png')
    comparisons[0].save(folder/'comparison.gif',save_all=True,append_images=comparisons[1:],duration=round(1000/fps),loop=0)


def run_benchmark(output='outputs/benchmark', categories=CATEGORIES, backends=('crossfade','rife'), count=6):
    root=Path(output); root.mkdir(parents=True,exist_ok=True)
    cases=generate_assets(root/'ground_truth',categories,count)
    rows=[]; sequences=[]
    for case in cases:
        first=root/'ground_truth'/case.identifier/'frame_0000.png'
        last=root/'ground_truth'/case.identifier/f'frame_{count+1:04d}.png'
        for backend_name in backends:
            record={'case_id':case.identifier,'backend':backend_name,'status':'failed','error':None}
            try:
                backend=BACKENDS[backend_name]()
                manifest=create_run(first,last,count,output_root=root/'runs'/case.identifier/backend_name,backend=backend)
                frames=[Image.open(p).copy() for p in manifest['frames']]
                if len(frames)!=len(case.frames):
                    raise ValueError('Incorrect frame count')
                endpoint_ok=endpoint_equal(case.frames[0],frames[0]) and endpoint_equal(case.frames[-1],frames[-1])
                if not endpoint_ok:
                    raise ValueError('Endpoint pixel mismatch')
                frame_rows=[]
                for i in range(1,len(frames)-1):
                    values={key:_finite_or_none(value) for key,value in metrics(case.frames[i],frames[i]).items()}
                    observed=_landmark(frames[i])
                    trajectory=_finite_or_none(trajectory_error([case.landmarks[i]],[observed])) if observed is not None else None
                    values.update(case_id=case.identifier,backend=backend_name,frame_index=i,timestamp=i/(count+1),endpoint_equal=endpoint_ok,
                                  trajectory_error_px=trajectory)
                    frame_rows.append(values)
                rows.extend(frame_rows)
                visual=root/'visuals'/case.identifier/backend_name;visual.mkdir(parents=True,exist_ok=True)
                _visuals(visual,case.frames,frames)
                measured=[r['trajectory_error_px'] for r in frame_rows if r['trajectory_error_px'] is not None]
                means={key:(float(np.mean(finite)) if (finite:=[r[key] for r in frame_rows if r[key] is not None]) else None) for key in ('psnr_db','ssim','edge_f1','chamfer_px')}
                means['trajectory_error_px']=float(np.mean(measured)) if measured else None
                record.update(status='ok',endpoint_equal=True,frame_count=len(frames),
                              backend_wall_seconds=manifest['backend_wall_seconds'],inference_seconds=manifest['inference_seconds'],model_load_seconds=manifest.get('model_load_seconds'),peak_cuda_memory_bytes=manifest['peak_cuda_memory_bytes'],
                              backend_version=manifest['backend_version'],source_commit=manifest['source_commit'],
                              checkpoint_id=manifest['checkpoint_id'],checkpoint_sha256=manifest['checkpoint_sha256'],
                              manifest=str(Path(manifest['frames'][0]).parent.parent/'manifest.json'),
                              trajectory_measured_frames=len(measured),trajectory_missing_frames=len(frame_rows)-len(measured),means=means)
            except Exception as exc:
                record['error']=f'{type(exc).__name__}: {exc}'
            sequences.append(record)
    fields=('case_id','backend','frame_index','timestamp','endpoint_equal','psnr_db','ssim','edge_f1','chamfer_px','trajectory_error_px')
    with (root/'frames.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows([{k:'' if v is None else v for k,v in row.items()} for row in rows])
    (root/'results.json').write_text(json.dumps({'protocol':'synthetic diagnostic v1','sequences':sequences,'frames':rows},indent=2,allow_nan=False)+'\n')
    lines=['# Synthetic diagnostic benchmark','', 'Procedural stress cases only; not evidence of artist performance.','', 'Trajectory coverage counts intermediate frames with a finite dark-pixel centroid measurement. Missing values are shown as —.','', '| Case | Backend | Status | PSNR dB | SSIM | Edge F1 | Chamfer px | Trajectory error px | Trajectory coverage (measured/total) | Backend wall s | Inference loop s | Peak VRAM bytes |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in sequences:
        m=r.get('means',{})
        fmt=lambda value: round(value,3) if value is not None else '—'
        coverage=f"{r['trajectory_measured_frames']}/{r['trajectory_measured_frames']+r['trajectory_missing_frames']}" if m else '—'
        lines.append('| '+ ' | '.join(str(x) for x in (r['case_id'],r['backend'],r['status'],fmt(m.get('psnr_db')),fmt(m.get('ssim')),fmt(m.get('edge_f1')),fmt(m.get('chamfer_px')),fmt(m.get('trajectory_error_px')),coverage,fmt(r.get('backend_wall_seconds')),fmt(r.get('inference_seconds')),r.get('peak_cuda_memory_bytes') or '—'))+' |')
        if r['error']: lines.append(f"\nFailure: {r['case_id']} / {r['backend']}: {r['error']}\n")
    (root/'summary.md').write_text('\n'.join(lines)+'\n')
    return sequences


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',default='outputs/benchmark')
    p.add_argument('--cases',nargs='+',choices=CATEGORIES,default=list(CATEGORIES))
    p.add_argument('--backends',nargs='+',choices=BACKENDS,default=list(BACKENDS))
    p.add_argument('--count',type=int,default=6)
    p.add_argument('--quick',action='store_true')
    args=p.parse_args()
    if args.quick:
        args.cases=args.cases[:2];args.count=min(args.count,2)
    print(json.dumps(run_benchmark(args.output,args.cases,args.backends,args.count),indent=2))

if __name__=='__main__':main()
