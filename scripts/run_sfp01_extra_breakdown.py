#!/usr/bin/env python3
"""Exploratory unequal-input SFP-01 comparison; requires recorded visual approval."""
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
from scripts.run_sfp01 import inputs, export
from inbetween.guided import GuidedBackend, _equal
from inbetween.run import _sha

BASELINE = ROOT / 'outputs/sfp01-20261027T033651Z-462f2bc4'
BASELINE_ARCHIVE_SHA256 = '909036f46408347285d4328706b7c7ef3f8a36800417fff5b34b51e847d79c39'


def verify_archive(folder):
    manifest = folder / 'archive.sha256'
    if _sha(manifest) != BASELINE_ARCHIVE_SHA256:
        raise ValueError('Baseline archive manifest differs from the frozen completed run')
    for line in manifest.read_text().splitlines():
        digest, relative = line.split('  ', 1)
        path = (folder / relative).resolve()
        if not path.is_relative_to(folder.resolve()) or _sha(path) != digest:
            raise ValueError(f'Baseline archive mismatch: {relative}')


def load_rgb(path):
    with Image.open(path) as source:
        if source.mode != 'RGB' or source.size != (512, 512):
            raise ValueError(f'Expected 512x512 RGB: {path}')
        return source.copy()


def verify_approval(path, frame2):
    approval = json.loads(path.read_text())
    if (approval.get('status') != 'approved_for_inference'
            or approval.get('frame2_sha256') != _sha(frame2)
            or not all(isinstance(approval.get(k), str) and approval[k].strip()
                       for k in ('reviewer', 'approved_at', 'user_approval_text'))):
        raise ValueError('Explicit visual approval bound to the exact frame-2 hash is required')
    return approval


def assemble(source, frame2, baseline, backend):
    guided = GuidedBackend(backend, frame2, 2)
    frames = guided.generate(source[0], source[1], 3)
    frames.extend([baseline[5].copy(), baseline[6].copy(), source[2].copy()])
    expected = {0: source[0], 2: frame2, 4: source[1], 5: baseline[5], 6: baseline[6], 7: source[2]}
    if len(frames) != 8 or not all(_equal(frames[i], value) for i, value in expected.items()):
        raise RuntimeError('Timeline or supplied/reused pixel preservation failure')
    return frames, guided.last_run_metadata


def labels(treatment=False):
    return [('supplied' if i in ((0, 2, 4, 7) if treatment else (0, 4, 7))
             else 'reused historical generated' if treatment and i in (5, 6)
             else 'newly generated' if treatment else 'historical generated') for i in range(8)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame2', type=Path, required=True)
    parser.add_argument('--approval', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, default=BASELINE)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    # All approval, immutable input and archive checks precede CUDA/model initialization.
    approval = verify_approval(args.approval, args.frame2)
    verify_archive(args.baseline)
    source, records = inputs()
    pose = load_rgb(args.frame2)
    baseline = [load_rgb(args.baseline / 'segmented_rife' / f'frame_{i:04d}.png') for i in range(8)]
    if not all(_equal(image, baseline[i]) for image, i in zip(source, (0, 4, 7))):
        raise ValueError('Baseline authoritative pixels differ')
    prior = json.loads((args.baseline / 'results.json').read_text())
    from inbetween.rife import RifeBackend, SOURCE_COMMIT, CHECKPOINT_SHA256
    old = prior['conditions']['segmented_rife']['diagnostics']
    if (old['source_commit'], old['checkpoint_sha256'], old['dtype'], old['device']) != (SOURCE_COMMIT, CHECKPOINT_SHA256, 'float32', 'cuda:0'):
        raise ValueError('RIFE configuration differs from baseline')
    out = (args.output or ROOT / 'outputs' / ('sfp01-extra-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8])).resolve()
    if out.is_relative_to(args.baseline.resolve()):
        raise ValueError('Output must not be inside baseline evidence')
    out.mkdir(parents=True, exist_ok=False)
    records.append(dict(index=2, path=str(args.frame2.resolve()), sha256=_sha(args.frame2)))
    report = dict(status='running', scope='Exploratory workflow with unequal supplied information; no novel algorithm or artist-intent validation',
                  started_at=datetime.now(timezone.utc).isoformat(), baseline=str(args.baseline.resolve()),
                  baseline_archive_sha256=BASELINE_ARCHIVE_SHA256, inputs=records, approval=approval,
                  approval_sha256=_sha(args.approval), settings={'frames': 8, 'fps': 8, 'new_inference_indices': [1, 3], 'local_segment_times': [[0.5], [0.5]]},
                  budgets={'baseline': {'supplied': 3, 'historical_generated': 5}, 'extra_breakdown': {'supplied': 4, 'newly_generated': 2, 'reused_historical_generated': 2}},
                  code_sha256={str(p.relative_to(ROOT)): _sha(p) for p in [Path(__file__), ROOT / 'scripts/run_sfp01.py', ROOT / 'inbetween/guided.py', ROOT / 'inbetween/rife.py']})
    began = time.perf_counter()
    try:
        backend = RifeBackend()
        torch, _ = backend._require_assets_and_cuda()
        free, total = torch.cuda.mem_get_info(0)
        report['gpu_before'] = {'name': torch.cuda.get_device_properties(0).name, 'free_bytes': free, 'total_bytes': total}
        start = time.perf_counter()
        treatment, report['diagnostics'] = assemble(source, pose, baseline, backend)
        report['new_generation_wall_seconds'] = time.perf_counter() - start
        report['treatment_export'] = export(treatment, out / 'extra_breakdown')
        report['per_frame_provenance'] = {}
        for name, frames, statuses in [('baseline', baseline, labels()), ('extra_breakdown', treatment, labels(True))]:
            report['per_frame_provenance'][name] = [dict(index=i, status=statuses[i],
                source_path=(str(args.baseline / 'segmented_rife' / f'frame_{i:04d}.png') if name == 'baseline' or i in (5, 6)
                             else next((r['path'] for r in records if r['index'] == i), None))) for i in range(8)]
        for entries in report['per_frame_provenance'].values():
            for entry in entries:
                entry['source_sha256'] = _sha(Path(entry['source_path'])) if entry['source_path'] else None
        checks = {}
        for i in (0, 2, 4, 5, 6, 7):
            checks[str(i)] = _equal(treatment[i], load_rgb(out / 'extra_breakdown' / f'frame_{i:04d}.png'))
        report['saved_supplied_reused_exact_pixel_checks'] = checks
        if not all(checks.values()):
            raise RuntimeError('Saved PNG pixel mismatch')
        comparison = []
        for i in range(8):
            canvas = Image.new('RGB', (1024, 560), 'white')
            draw = ImageDraw.Draw(canvas)
            for column, (frames, name, statuses) in enumerate([(baseline, 'Baseline: 3 supplied / 5 historical generated', labels()), (treatment, 'Extra: 4 supplied / 2 new / 2 reused', labels(True))]):
                draw.text((column * 512 + 8, 4), name, fill='black')
                draw.text((column * 512 + 8, 22), f'Frame {i}: {statuses[i]}', fill='black')
                canvas.paste(frames[i], (column * 512, 48))
            comparison.append(canvas)
        report['comparison_export'] = export(comparison, out / 'side_by_side')
        sheet = Image.new('RGB', (1024, 560 * 8), 'white')
        for i, frame in enumerate(comparison):
            sheet.paste(frame, (0, i * 560))
        sheet.save(out / 'labelled_contact_sheet.png')
        report['status'] = 'completed_pending_visual_review'
    except Exception as exc:
        report.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        try:
            verify_archive(args.baseline)
            if not all(_sha(Path(r['path'])) == r['sha256'] for r in records):
                raise RuntimeError('Input hash changed')
            report['baseline_and_inputs_unchanged'] = True
        except Exception as exc:
            report.update(status='failed', preservation_error=str(exc), baseline_and_inputs_unchanged=False)
        report['total_wall_seconds'] = time.perf_counter() - began
        report['output_sha256'] = {str(p.relative_to(out)): _sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
        (out / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
        (out / 'archive.sha256').write_text(''.join(f'{_sha(p)}  {p.relative_to(out)}\n' for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'archive.sha256'))
    print(out)
    return 0 if report['status'] == 'completed_pending_visual_review' else 1


if __name__ == '__main__':
    raise SystemExit(main())
