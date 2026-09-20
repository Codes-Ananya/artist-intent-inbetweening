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
    return (float(xs.mean()),float(ys.mean())) if len(xs) else (float('nan'),float('nan'))


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
                    values=metrics(case.frames[i],frames[i])
                    values.update(case_id=case.identifier,backend=backend_name,frame_index=i,timestamp=i/(count+1),endpoint_equal=endpoint_ok,
                                  trajectory_error_px=trajectory_error([case.landmarks[i]],[_landmark(frames[i])]))
                    frame_rows.append(values)
                rows.extend(frame_rows)
                visual=root/'visuals'/case.identifier/backend_name;visual.mkdir(parents=True,exist_ok=True)
                _visuals(visual,case.frames,frames)
                record.update(status='ok',endpoint_equal=True,frame_count=len(frames),
                              inference_seconds=manifest['inference_seconds'],peak_cuda_memory_bytes=manifest['peak_cuda_memory_bytes'],
                              backend_version=manifest['backend_version'],source_commit=manifest['source_commit'],
                              checkpoint_id=manifest['checkpoint_id'],checkpoint_sha256=manifest['checkpoint_sha256'],
                              manifest=str(Path(manifest['frames'][0]).parent.parent/'manifest.json'),
                              means={key:float(np.mean([r[key] for r in frame_rows])) for key in ('psnr_db','ssim','edge_f1','chamfer_px','trajectory_error_px')})
            except Exception as exc:
                record['error']=f'{type(exc).__name__}: {exc}'
            sequences.append(record)
    fields=('case_id','backend','frame_index','timestamp','endpoint_equal','psnr_db','ssim','edge_f1','chamfer_px','trajectory_error_px')
    with (root/'frames.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    def safe(value):
        if isinstance(value,float) and not math.isfinite(value): return 'Infinity' if value>0 else 'NaN'
        if isinstance(value,dict):return {k:safe(v) for k,v in value.items()}
        if isinstance(value,list):return [safe(v) for v in value]
        return value
    (root/'results.json').write_text(json.dumps(safe({'protocol':'synthetic diagnostic v1','sequences':sequences,'frames':rows}),indent=2,allow_nan=False)+'\n')
    lines=['# Synthetic diagnostic benchmark','', 'Procedural stress cases only; not evidence of artist performance.','', '| Case | Backend | Status | PSNR dB | SSIM | Edge F1 | Chamfer px | Runtime s | Peak VRAM bytes |','|---|---|---|---:|---:|---:|---:|---:|---:|']
    for r in sequences:
        m=r.get('means',{})
        lines.append('| '+ ' | '.join(str(x) for x in (r['case_id'],r['backend'],r['status'],round(m['psnr_db'],3) if m else '—',round(m['ssim'],3) if m else '—',round(m['edge_f1'],3) if m else '—',round(m['chamfer_px'],3) if m else '—',round(r['inference_seconds'],3) if m else '—',r.get('peak_cuda_memory_bytes') or '—'))+' |')
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
