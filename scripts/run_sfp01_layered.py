#!/usr/bin/env python3
"""Run one explicit CPU layered diagnostic; never calls RIFE or downloads."""
import json
from pathlib import Path
import sys
import time
from datetime import datetime,timezone
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PIL import Image,ImageDraw
import numpy as np
from inbetween.layered_pilot import LayeredPilotBackend,ROI
from inbetween.run import _sha
from scripts.run_sfp01 import export
from scripts.run_sfp01_frame1_scale import verify,BASE
from scripts.run_sfp01_extra_breakdown import load_rgb


def main():
    prior=verify()
    # Snapshot all existing run/pilot files (no mutation); includes scale negative result.
    before={p:_sha(p) for root in [ROOT/'outputs',ROOT/'.local/real_input_pilot'] for p in root.rglob('*') if p.is_file() and not p.is_symlink() and 'pytest-temp' not in p.parts}
    out=ROOT/'outputs'/('sfp01-layered-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid4().hex[:8])
    out.mkdir(exist_ok=False)
    report=dict(status='running',baseline=str(BASE),inputs=prior['inputs'],
        method='Explicit manually guided CPU layer diagnostic, not backend fallback',
        frame_roles={'supplied':[0,2,4,7],'manual_composite':[1],'reused_generated':[3,5,6]},
        code_sha256={p:_sha(ROOT/p) for p in ['inbetween/layered_pilot.py','scripts/run_sfp01_layered.py']})
    start=time.perf_counter()
    try:
        frames=[load_rgb(BASE/'extra_breakdown'/f'frame_{i:04d}.png') for i in range(8)]
        backend=LayeredPilotBackend(frames[1])
        began=time.perf_counter()
        result=backend.generate(frames[0],frames[2],1)
        report['processing_seconds']=time.perf_counter()-began
        report['settings']=backend.last_run_metadata
        (out/'layers').mkdir()
        for name,array in backend.artifacts.items():Image.fromarray(array).save(out/'layers'/f'{name}.png')
        candidate=[f.copy() for f in frames];candidate[1]=result[1]
        report['candidate_export']=export(candidate,out/'candidate')
        report['unchanged_saved_frames']={str(i):np.array_equal(np.array(frames[i]),np.array(load_rgb(out/'candidate'/f'frame_{i:04d}.png'))) for i in range(8) if i!=1}
        if not all(report['unchanged_saved_frames'].values()):raise RuntimeError('Unexpected timeline changes')
        outside=np.ones((512,512),bool);x0,y0,x1,y1=ROI;outside[y0:y1,x0:x1]=False
        report['outside_roi_exact']=bool(np.array_equal(np.array(frames[1])[outside],np.array(candidate[1])[outside]))
        if not report['outside_roi_exact']:raise RuntimeError('Outside ROI changed')
        paired=[]
        for i in range(8):
            canvas=Image.new('RGB',(1024,560),'white');draw=ImageDraw.Draw(canvas)
            for x,seq,label in [(0,frames,'Archived RIFE scale 1'),(512,candidate,'Manual CPU layer at frame 1; others reused')]:
                draw.text((x+8,8),f'{label} | frame {i}',fill='black');canvas.paste(seq[i],(x,48))
            paired.append(canvas)
        report['comparison_export']=export(paired,out/'side_by_side')
        sheet=Image.new('RGB',(1024,1680),'white')
        for i in range(3):sheet.paste(paired[i],(0,560*i))
        sheet.save(out/'frames_0_1_2.png')
        report['status']='completed_pending_visual_review'
    except Exception as exc:report.update(status='failed',error=f'{type(exc).__name__}: {exc}')
    finally:
        changed=[str(p) for p,h in before.items() if not p.exists() or _sha(p)!=h]
        report['preservation']={'checked_files':len(before),'changed':changed}
        if changed:report['status']='failed'
        report['total_wall_seconds']=time.perf_counter()-start
        report['output_sha256']={str(p.relative_to(out)):_sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
        (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
        (out/'archive.sha256').write_text(''.join(f'{_sha(p)}  {p.relative_to(out)}\n' for p in sorted(out.rglob('*')) if p.is_file() and p.name!='archive.sha256'))
    print(out);print(report['status']);return int(report['status']!='completed_pending_visual_review')

if __name__=='__main__':raise SystemExit(main())
