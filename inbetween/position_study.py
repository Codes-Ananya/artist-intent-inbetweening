"""Matched leave-one-position-out procedural oracle-position study."""
import argparse
import csv
import json
import random
from pathlib import Path
import numpy as np
from PIL import Image
from .benchmark import _finite_or_none, _landmark, _visuals
from .benchmark_cases import generate_assets
from .benchmark_metrics import endpoint_equal, metrics, trajectory_error
from .guided_benchmark import BACKENDS, CATEGORIES, METRIC_KEYS, _aggregate
from .guided import create_guided_run
from .run import create_run
from .position_recommendation import recommend_position

SEED = 20260921


def midpoint(count):
    return (count + 1) // 2


def random_position(count, seed=SEED):
    return random.Random(seed).randint(1, count)


def rank_candidates(candidates, count):
    for r in candidates:
        r.update(mean_rank=None, metric_ranks={})
    complete = (len(candidates) == count and {r['k'] for r in candidates} == set(range(1, count+1))
                and all(r['status'] == 'ok' and r['evaluated_frame_count'] == count-1
                        and all(r['improvement'][m] is not None for m in ('edge_f1', 'chamfer_px')) for r in candidates))
    if not complete:
        return {"status": "incomplete_candidate_coverage", "metrics": [], "best_k": None, "worst_k": None}
    keys = ['edge_f1', 'chamfer_px']
    if all(len(r['paired_trajectory_indices']) == count-1 for r in candidates):
        keys.append('trajectory_error_px')
    for key in keys:
        values = [r['improvement'][key] for r in candidates]
        for r, value in zip(candidates, values):
            r['metric_ranks'][key] = 1 + sum(v > value for v in values) + (sum(v == value for v in values)-1)/2
    for r in candidates:
        r['mean_rank'] = float(np.mean(list(r['metric_ranks'].values())))
    return {"status": "ok", "metrics": keys,
            "best_k": min(candidates, key=lambda r: (r['mean_rank'], r['k']))['k'],
            "worst_k": min(candidates, key=lambda r: (-r['mean_rank'], r['k']))['k']}


def policy_comparison(candidates, recommendation, oracle, count):
    by_k = {r['k']: r for r in candidates}
    best = by_k.get(oracle['best_k'], {}).get('mean_rank')
    selections = {'heuristic': recommendation.get('recommended_k'), 'midpoint': midpoint(count),
                  'seeded_random': random_position(count), 'oracle_best': oracle['best_k'], 'oracle_worst': oracle['worst_k']}
    rows = []
    for policy, k in selections.items():
        candidate = by_k.get(k, {})
        value = candidate.get('mean_rank')
        rows.append({'policy': policy, 'k': k, 'status': candidate.get('status', 'unavailable'),
                     'mean_rank': value, 'regret': value-best if value is not None and best is not None else None,
                     **candidate.get('improvement', {})})
    return rows


def measure(case, frames):
    rows = []
    for i in range(1, len(frames)-1):
        raw = metrics(case.frames[i], frames[i])
        center = _landmark(frames[i])
        rows.append({'frame_index': i, **{key: _finite_or_none(v) for key, v in raw.items()},
                     'psnr_perfect_match': bool(np.isposinf(raw['psnr_db'])),
                     'trajectory_error_px': trajectory_error([case.landmarks[i]], [center]) if center is not None else None})
    return rows


def aggregate(rows):
    return {'means': _aggregate(rows), 'evaluated_frame_indices': [r['frame_index'] for r in rows],
            'trajectory_measured_frames': sum(r['trajectory_error_px'] is not None for r in rows),
            'trajectory_total_frames': len(rows),
            'psnr_perfect_match_count': sum(r['psnr_perfect_match'] for r in rows),
            'psnr_mean_undefined_due_to_perfect_match': any(r['psnr_perfect_match'] for r in rows)}


def read_frames(manifest):
    frames = []
    for path in manifest['frames']:
        with Image.open(path) as image:
            frames.append(image.copy())
    return frames


def write_table(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return ['| ' + ' | '.join(fields) + ' |', '|' + '|'.join(['---']*len(fields)) + '|',
            *['| ' + ' | '.join(str(row.get(f)) if row.get(f) is not None else '—' for f in fields) + ' |' for row in rows]]


def run_position_study(output='outputs/breakdown-position-study', backend='rife', backend_factory=None):
    count = 6
    root = Path(output)
    factory = backend_factory or BACKENDS[backend]
    reports, flat_candidates, flat_policies = [], [], []
    for category in CATEGORIES:
        report = {'case_id': category, 'endpoint': {'status': 'failed'}, 'recommendation': {}, 'candidates': []}
        reports.append(report)
        try:
            case = generate_assets(root/'ground_truth', [category], count)[0]
            paths = [root/'ground_truth'/category/f'frame_{i:04d}.png' for i in range(count+2)]
            manifest = create_run(paths[0], paths[-1], count, output_root=root/'runs'/category/'endpoint', backend=factory())
            endpoint = read_frames(manifest)
            checks = {'A': endpoint_equal(endpoint[0], case.frames[0]), 'B': endpoint_equal(endpoint[-1], case.frames[-1])}
            if len(endpoint) != count+2 or not all(checks.values()):
                raise ValueError('Endpoint sequence failed exactness/count check')
            report['endpoint'] = {'status': 'ok', 'manifest': manifest, 'exact_pixel_checks': checks,
                                  'backend_wall_seconds': manifest['backend_wall_seconds']}
            report['recommendation'] = recommend_position(endpoint)
            baseline_rows = measure(case, endpoint)
            visual = root/'visuals'/category/'endpoint'
            visual.mkdir(parents=True, exist_ok=True)
            _visuals(visual, case.frames, endpoint)
        except Exception as exc:
            report['endpoint']['status'] = 'failed'
            report['endpoint']['error'] = f'{type(exc).__name__}: {exc}'
        for k in range(1, count+1):
            candidate = {'k': k, 'status': 'failed', 'error': None}
            report['candidates'].append(candidate)
            try:
                if report['endpoint']['status'] != 'ok':
                    raise RuntimeError('Endpoint stage failed: ' + report['endpoint']['error'])
                manifest = create_guided_run(paths[0], paths[k], paths[-1], count, k,
                                            output_root=root/'runs'/category/f'k{k}', backend=factory())
                frames = read_frames(manifest)
                rows = measure(case, frames)
                indices = [i for i in range(1, count+1) if i != k]
                base = aggregate([baseline_rows[i-1] for i in indices])
                guided = aggregate([rows[i-1] for i in indices])
                paired = [i for i in indices if baseline_rows[i-1]['trajectory_error_px'] is not None and rows[i-1]['trajectory_error_px'] is not None]
                gains = {key: (guided['means'][key]-base['means'][key]) * (-1 if key in ('chamfer_px', 'trajectory_error_px') else 1)
                         if guided['means'][key] is not None and base['means'][key] is not None else None for key in METRIC_KEYS}
                gains['trajectory_error_px'] = float(np.mean([baseline_rows[i-1]['trajectory_error_px']-rows[i-1]['trajectory_error_px'] for i in paired])) if paired else None
                visual = root/'visuals'/category/f'k{k}'
                visual.mkdir(parents=True, exist_ok=True)
                _visuals(visual, case.frames, frames)
                candidate.update(status='ok', evaluated_frame_count=len(indices), excluded_frame_indices=[k],
                                 endpoint_only=base, guided=guided, improvement=gains, paired_trajectory_indices=paired,
                                 breakdown_index_metrics={'endpoint_only': {**baseline_rows[k-1], 'is_authoritative_breakdown': False},
                                                          'guided': {**rows[k-1], 'is_authoritative_breakdown': True}},
                                 frame_metrics={'endpoint_only': baseline_rows, 'guided': rows},
                                 exact_pixel_checks=manifest['guided_breakdown']['exact_pixel_checks'],
                                 backend_wall_seconds=manifest['backend_wall_seconds'], manifest=manifest)
            except Exception as exc:
                candidate['error'] = f'{type(exc).__name__}: {exc}'
        report['oracle'] = rank_candidates(report['candidates'], count)
        report['policies'] = policy_comparison(report['candidates'], report['recommendation'], report['oracle'], count)
        flat_candidates.extend({'case_id': category, 'k': r['k'], 'status': r['status'], 'error': r['error'],
                                'mean_rank': r['mean_rank'], 'guided_wall_seconds': r.get('backend_wall_seconds'),
                                **r.get('improvement', {})} for r in report['candidates'])
        flat_policies.extend({'case_id': category, **r} for r in report['policies'])
    root.mkdir(parents=True, exist_ok=True)
    result = {'protocol': 'BREAKDOWN_POSITION_PROTOCOL v1', 'backend': backend, 'count': count, 'random_seed': SEED, 'cases': reports}
    (root/'results.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    write_table(root/'candidates.csv', flat_candidates)
    write_table(root/'policy_comparison.csv', flat_policies)
    lines = ['# Procedural oracle-position study', '',
             'Matched leave-one-position-out estimates: both methods exclude k; different k exclude different frames.',
             'Oracle drawings estimate an upper bound. No real-artist usability conclusion. Experimental ground-truth-free heuristic.',
             'Runtime is diagnostic only; endpoint generation is recorded separately. No cloud compute. Milestone 4 v1 aggregates excluded.',
             'Primary criterion: lower mean rank of structural gains; trajectory only with complete paired coverage for every candidate.', '']
    for report in reports:
        category = report['case_id']
        folder = root/'tables'/category
        folder.mkdir(parents=True, exist_ok=True)
        lines += [f'## {category}', f"Endpoint: {report['endpoint']['status']}; wall seconds: {report['endpoint'].get('backend_wall_seconds')}; error: {report['endpoint'].get('error')}",
                  f"Oracle coverage: {report['oracle']}", '']
        lines += write_table(folder/'position_value.csv', [r for r in flat_candidates if r['case_id'] == category])
        lines += ['', 'Risk components', '']
        risks = [{'k': r['k'], 'score': r['score'], 'missing': ','.join(r['missing']),
                  'active': ','.join(report['recommendation']['active_components']), **r['raw'],
                  **{f'normalized_{key}': v for key, v in r['normalized'].items()}} for r in report['recommendation'].get('positions', [])]
        lines += write_table(folder/'risk_components.csv', risks)
        lines += ['', 'Policy comparison', ''] + write_table(folder/'policies.csv', report['policies']) + ['']
    (root/'summary.md').write_text('\n'.join(lines)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=BACKENDS, default='rife')
    parser.add_argument('--output', default='outputs/breakdown-position-study')
    args = parser.parse_args()
    result = run_position_study(args.output, args.backend)
    print(json.dumps({'output': args.output, 'successful_candidates': sum(r['status']=='ok' for c in result['cases'] for r in c['candidates'])}))
    return 0 if all(c['oracle']['status']=='ok' for c in result['cases']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
