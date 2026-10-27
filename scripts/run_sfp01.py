#!/usr/bin/env python3
"""Run the approved SFP-01 exploration locally; no downloads or CPU RIFE fallback."""
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw
from inbetween.core import CrossfadeBackend
from inbetween.diagnostics import collect
from inbetween.guided import GuidedBackend, _equal
from inbetween.rife import RifeBackend
from inbetween.run import _sha

BASE = ROOT / '.local/real_input_pilot/synthetic_pilot/sfp_01'
APPROVED = [
    (0, 'r001', 'e062af70b522307f276142db5232f86dfe6bbd7a2211ce50052eee358029c5cb'),
    (4, 'r001', 'ab1615c77d4657fef940874bb8f9b59be1b3297d2daf92dbaf0319ae2c86ae6e'),
    (7, 'r002', 'ff03296cee9d51b00f5d503f23cc387c4da6d9d52fcead75e65c6875740f85c3'),
]


def inputs():
    images, records = [], []
    for index, revision, expected in APPROVED:
        path = BASE / f'assets/synthetic_input/{revision}/sfp01_synthetic_input_taluvi_exploratory_reach01_f{index:03d}_prepared_{revision}.png'
        actual = _sha(path)
        if actual != expected:
            raise RuntimeError(f'Approved hash mismatch: {path}')
        with Image.open(path) as source:
            if source.mode != 'RGB' or source.size != (512, 512):
                raise RuntimeError(f'Unexpected input format: {path}')
            images.append(source.copy())
        records.append(dict(index=index, path=str(path), sha256=actual))
    return images, records


def export(frames, folder):
    folder.mkdir()
    for index, frame in enumerate(frames):
        frame.save(folder / f'frame_{index:04d}.png')
    # GIF uses centiseconds: alternate 120/130 ms for an exact 1 s cycle.
    frames[0].save(folder / 'animation.gif', save_all=True, append_images=frames[1:],
                   duration=[120, 130] * 4, loop=0, disposal=2, optimize=False)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n',
                    '-framerate', '8', '-i', str(folder / 'frame_%04d.png'),
                    '-frames:v', '8', '-vf', 'format=yuv420p', '-c:v', 'libx264',
                    '-movflags', '+faststart', str(folder / 'animation.mp4')], check=True)
    with Image.open(folder / 'animation.gif') as gif:
        durations = []
        for index in range(gif.n_frames):
            gif.seek(index)
            durations.append(gif.info['duration'])
        if len(durations) != 8 or sum(durations) != 1000:
            raise RuntimeError('GIF frame count/duration validation failed')
    return dict(frame_count=8, fps=8, gif_duration_ms=durations,
                gif_timing_note='120/130 ms alternating; 8 fps average, GIF centisecond limitation')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New directory only; existing paths are refused')
    args = parser.parse_args()
    out = (args.output or ROOT / 'outputs' / ('sfp01-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8])).resolve()
    out.mkdir(parents=True, exist_ok=False)
    began = time.perf_counter()
    report = dict(status='running', output=str(out), started_at=datetime.now(timezone.utc).isoformat(),
                  scope='SFP-01 exploratory synthetic demo; no artist-intent validation or independent reference',
                  prior_evidence=str(BASE / 'exploratory_execution_r001'),
                  researcher_reported_cuda={'available': True, 'gpu': 'NVIDIA GeForce RTX 4050 Laptop GPU', 'vram_mib': 6141},
                  settings={'frames': 8, 'fps': 8, 'authoritative_indices': [0, 4, 7],
                            'segment_times': [[0.25, 0.5, 0.75], [1/3, 2/3]],
                            'rife_device': 'cuda:0', 'fallback': False}, conditions={})
    code = 1
    try:
        source, report['inputs'] = inputs()
        report['environment'] = collect()
        rife = RifeBackend()
        torch, _ = rife._require_assets_and_cuda()
        props = torch.cuda.get_device_properties(0)
        report['gpu'] = {'name': props.name, 'total_memory_bytes': props.total_memory}
        sequences = []
        for name, backend in [('segmented_cross_dissolve', CrossfadeBackend()), ('segmented_rife', rife)]:
            guided = GuidedBackend(backend, source[1], 4)
            start = time.perf_counter()
            frames = guided.generate(source[0], source[2], 6)
            runtime = time.perf_counter() - start
            if len(frames) != 8:
                raise RuntimeError('Expected exactly eight frames')
            record = dict(generation_wall_seconds=runtime, diagnostics=guided.last_run_metadata)
            report['conditions'][name] = record
            record['export'] = export(frames, out / name)
            checks = {}
            for original, index in zip(source, [0, 4, 7]):
                with Image.open(out / name / f'frame_{index:04d}.png') as saved:
                    checks[str(index)] = _equal(original, saved)
            record['saved_png_exact_pixel_checks'] = checks
            if not all(checks.values()):
                raise RuntimeError('Saved authoritative pixels differ')
            sequences.append(frames)
        comparison = []
        for index in range(8):
            canvas = Image.new('RGB', (1024, 544), 'white')
            draw = ImageDraw.Draw(canvas)
            for column, (name, frames) in enumerate(zip(report['conditions'], sequences)):
                draw.text((column * 512 + 8, 8), f'{name} | frame {index} | ' + ('INPUT' if index in (0,4,7) else 'generated'), fill='black')
                canvas.paste(frames[index], (column * 512, 32))
            comparison.append(canvas)
        report['comparison_export'] = export(comparison, out / 'side_by_side')
        sheet = Image.new('RGB', (1024, 544 * 8), 'white')
        for index, frame in enumerate(comparison):
            sheet.paste(frame, (0, index * 544))
        sheet.save(out / 'labelled_contact_sheet.png')
        report['status'] = 'completed_pending_visual_review'
        code = 0
    except Exception as exc:
        report.update(status='failed', error=f'{type(exc).__name__}: {exc}', traceback=traceback.format_exc())
    finally:
        if 'inputs' in report:
            report['input_file_hashes_unchanged'] = all(_sha(Path(r['path'])) == r['sha256'] for r in report['inputs'])
            if not report['input_file_hashes_unchanged']:
                report['status'] = 'failed'
                code = 1
        report['total_wall_seconds'] = time.perf_counter() - began
        report['output_sha256'] = {str(p.relative_to(out)): _sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
        report['runner_sha256'] = _sha(Path(__file__))
        (out / 'results.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
        (out / 'archive.sha256').write_text(''.join(f'{_sha(p)}  {p.relative_to(out)}\n' for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'archive.sha256'))
        print(f"{report['status']}: {out}\nResults: {out / 'results.json'}", flush=True)
        if code:
            print(report.get('error', 'Preservation validation failed'), file=sys.stderr)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
