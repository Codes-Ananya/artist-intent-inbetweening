#!/usr/bin/env python3
"""One fixed scale-0.5 midpoint experiment; no downloads or backend fallback."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
from uuid import uuid4
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw
from inbetween.rife import RifeBackend
from inbetween.guided import _equal
from inbetween.run import _sha
from scripts.run_sfp01 import export
from scripts.run_sfp01_extra_breakdown import load_rgb
BASE = ROOT / 'outputs/sfp01-extra-20261027T041321Z-539ba9c6'
MANIFEST = 'fdede7afb3d522340b0568707d7ad584dbe919e41e137c50ad8daa03ae72fdbc'


def verify():
    assert _sha(BASE / 'archive.sha256') == MANIFEST, 'Frozen archive changed'
    for line in (BASE / 'archive.sha256').read_text().splitlines():
        digest, relative = line.split('  ', 1)
        assert _sha(BASE / relative) == digest, relative
    report = json.loads((BASE / 'results.json').read_text())
    for entry in report['inputs']:
        assert _sha(Path(entry['path'])) == entry['sha256'], entry['path']
    return report


def replace_midpoint(frames, backend):
    triplet = backend.generate(frames[0].copy(), frames[2].copy(), 1)
    if len(triplet) != 3 or not _equal(triplet[0], frames[0]) or not _equal(triplet[2], frames[2]):
        raise RuntimeError('Midpoint backend changed endpoints or frame count')
    result = [f.copy() for f in frames]
    result[1] = triplet[1]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    prior = verify()
    out = (args.output or ROOT / 'outputs' / ('sfp01-frame1-scale-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8])).resolve()
    if out.is_relative_to(BASE):
        raise ValueError('Cannot write inside frozen baseline')
    out.mkdir(parents=True, exist_ok=False)
    report = dict(status='running', baseline=str(BASE), baseline_archive_sha256=MANIFEST,
                  method='RIFE midpoint at flow_scale=0.5 (internal scales 8,4,2 versus default 4,2,1); only frame 1 replaced',
                  scope='Same four supplied frames; no new pose, no novelty or artist-intent validation',
                  inputs=prior['inputs'], supplied=[0,2,4,7], newly_inferred=[1], reused_generated=[3,5,6],
                  timestamp=0.5, fps=8, code_sha256={p:_sha(ROOT/p) for p in ['scripts/run_sfp01_frame1_scale.py','inbetween/rife.py']})
    started = time.perf_counter()
    try:
        backend = RifeBackend(flow_scale=0.5)
        torch, _ = backend._require_assets_and_cuda()
        free,total = torch.cuda.mem_get_info(0)
        report['gpu_before'] = dict(name=torch.cuda.get_device_properties(0).name,free_bytes=free,total_bytes=total)
        frames = [load_rgb(BASE/'extra_breakdown'/f'frame_{i:04d}.png') for i in range(8)]
        start = time.perf_counter()
        candidate = replace_midpoint(frames, backend)
        report['generation_wall_seconds'] = time.perf_counter()-start
        report['diagnostics'] = backend.last_run_metadata
        report['export'] = export(candidate, out/'candidate')
        report['unchanged_saved_frames'] = {str(i):_equal(frames[i],load_rgb(out/'candidate'/f'frame_{i:04d}.png')) for i in range(8) if i!=1}
        assert all(report['unchanged_saved_frames'].values())
        paired=[]
        for i in range(8):
            canvas=Image.new('RGB',(1024,560),'white'); draw=ImageDraw.Draw(canvas)
            for x,seq,label in [(0,frames,'Archived scale 1'),(512,candidate,'Candidate scale 0.5 at frame 1 only')]:
                status='supplied' if i in (0,2,4,7) else 'generated' if i==1 else 'reused generated'
                draw.text((x+8,8),f'{label} | frame {i}: {status}',fill='black');canvas.paste(seq[i],(x,48))
            paired.append(canvas)
        report['comparison_export']=export(paired,out/'side_by_side')
        sheet=Image.new('RGB',(1024,560*3),'white')
        for i in range(3):sheet.paste(paired[i],(0,560*i))
        sheet.save(out/'frames_0_1_2.png')
        report['status']='completed_pending_visual_review'
    except Exception as exc:
        report.update(status='failed',error=f'{type(exc).__name__}: {exc}')
    finally:
        try:
            verify(); report['baseline_and_inputs_unchanged']=True
        except Exception as exc:
            report.update(status='failed',preservation_error=str(exc),baseline_and_inputs_unchanged=False)
        report['total_wall_seconds']=time.perf_counter()-started
        report['output_sha256']={str(p.relative_to(out)):_sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
        (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
        (out/'archive.sha256').write_text(''.join(f'{_sha(p)}  {p.relative_to(out)}\n' for p in sorted(out.rglob('*')) if p.is_file() and p.name!='archive.sha256'))
    print(out)
    print(report['status'],report.get('error',''))
    return int(report['status']!='completed_pending_visual_review')

if __name__=='__main__':
    raise SystemExit(main())
