"""Milestone 6: fixed temporal intent guidance with deterministic abstention."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from . import position_study as m5
from .intent_cases import make_cases, pixel_hash
from .intent_guidance import decide_intent

POLICIES = ('intent', 'midpoint', 'frozen_heuristic', 'oracle_best', 'forced_choice_intent_ablation')


def evaluate_case(case, root, factory):
    """Decisions precede all candidate evaluation; M5 receives endpoint frames only."""
    name = case.identifier
    decision = decide_intent(case.metadata['intent'])
    report = {'case_id': name, 'metadata': case.metadata, 'decision': decision,
              'endpoint': {'status': 'failed'}, 'recommendation': {}, 'candidates': []}
    folder = root/'ground_truth'/name
    folder.mkdir(parents=True)
    paths = [folder/f'frame_{i:04d}.png' for i in range(8)]
    for frame, path in zip(case.frames, paths):
        frame.save(path)
    (folder/'metadata.json').write_text(json.dumps(case.metadata, indent=2, allow_nan=False)+'\n')
    report['truth_pixel_hashes'] = [pixel_hash(frame) for frame in case.frames]
    try:
        manifest = m5.create_run(paths[0], paths[7], 6, output_root=root/'runs'/name/'endpoint', backend=factory())
        frames = m5.read_frames(manifest)
        checks = {'A': m5.endpoint_equal(frames[0], case.frames[0]), 'B': m5.endpoint_equal(frames[-1], case.frames[-1])}
        if len(frames) != 8 or not all(checks.values()):
            raise ValueError('Endpoint count/pixel check failed')
        report['endpoint'] = {'status': 'ok', 'manifest': manifest, 'exact_pixel_checks': checks}
        report['recommendation'] = m5.recommend_position(frames)
        baseline = m5.measure(case, frames)
    except Exception as exc:
        report['endpoint'] = {'status': 'failed', 'error': f'{type(exc).__name__}: {exc}'}
    for k in range(1,7):
        row = {'k': k, 't': k/7, 'status': 'failed', 'error': None}
        report['candidates'].append(row)
        try:
            if report['endpoint']['status'] != 'ok':
                raise RuntimeError('Endpoint stage failed')
            manifest = m5.create_guided_run(paths[0], paths[k], paths[7], 6, k,
                                           output_root=root/'runs'/name/f'k{k}', backend=factory())
            frames = m5.read_frames(manifest)
            checks = {label: m5.endpoint_equal(frames[i], case.frames[i]) for label, i in [('A',0),('D',k),('B',7)]}
            if len(frames) != 8 or not all(checks.values()):
                raise ValueError('Guided count/pixel check failed')
            measured = m5.measure(case, frames)
            indices = [i for i in range(1,7) if i != k]
            base = m5.aggregate([baseline[i-1] for i in indices])
            guided = m5.aggregate([measured[i-1] for i in indices])
            paired = [i for i in indices if baseline[i-1]['trajectory_error_px'] is not None
                      and measured[i-1]['trajectory_error_px'] is not None]
            gains = {key: (guided['means'][key]-base['means'][key]) * (-1 if key in ('chamfer_px','trajectory_error_px') else 1)
                     if guided['means'][key] is not None and base['means'][key] is not None else None
                     for key in m5.METRIC_KEYS}
            gains['trajectory_error_px'] = float(np.mean([baseline[i-1]['trajectory_error_px']-measured[i-1]['trajectory_error_px']
                                                        for i in paired])) if paired else None
            row.update(status='ok', evaluated_frame_count=5, excluded_frame_indices=[k], endpoint_only=base,
                       guided=guided, paired_trajectory_indices=paired, improvement=gains,
                       exact_pixel_checks=checks, manifest=manifest,
                       frame_metrics={'endpoint_only': baseline, 'guided': measured},
                       breakdown_index_metrics={'endpoint_only': {**baseline[k-1], 'is_authoritative_breakdown': False},
                                                'guided': {**measured[k-1], 'is_authoritative_breakdown': True}})
        except Exception as exc:
            row['error'] = f'{type(exc).__name__}: {exc}'
    report['oracle'] = m5.rank_candidates(report['candidates'], 6)
    selections = dict(zip(POLICIES, [decision['recommended_k'], 3,
                                    report['recommendation'].get('recommended_k'), report['oracle']['best_k'],
                                    decision['forced_choice_ablation_k']]))
    by_k = {r['k']: r for r in report['candidates']}
    best = by_k.get(report['oracle']['best_k'], {}).get('mean_rank')
    report['policies'] = []
    for policy, k in selections.items():
        candidate = by_k.get(k, {})
        rank = candidate.get('mean_rank')
        status = 'abstained' if policy == 'intent' and decision['status'] == 'abstained' else (
            'ok' if rank is not None else 'unavailable')
        report['policies'].append({'policy': policy, 'k': k, 'status': status, 'mean_rank': rank,
                                   'regret': rank-best if rank is not None and best is not None else None,
                                   **m5.flat_improvements(candidate)})
    return report


def summarize(cases):
    answered = [c for c in cases if c['decision']['status'] == 'answered']
    abstained = [c for c in cases if c['decision']['status'] == 'abstained']
    def complete(case, policies):
        rows = {r['policy']: r for r in case['policies']}
        return all(rows[p]['regret'] is not None for p in policies)
    def group(name, requested, policies):
        eligible = [c for c in requested if complete(c, policies)]
        rows = []
        for policy in policies:
            values = [next(r for r in c['policies'] if r['policy'] == policy) for c in eligible]
            rows.append({'subset': name, 'policy': policy, 'requested_cases': len(requested),
                         'evaluated_cases': len(eligible),
                         'case_ids': ','.join(c['case_id'] for c in eligible),
                         'mean_rank': float(np.mean([r['mean_rank'] for r in values])) if values else None,
                         'mean_regret': float(np.mean([r['regret'] for r in values])) if values else None})
        return rows, eligible
    selective, selective_cases = group('selective_answered', answered, POLICIES)
    full, full_cases = group('full_suite', cases, POLICIES[1:])
    abstention, _ = group('abstained_forced_choice_analysis', abstained, POLICIES[1:])
    comparisons = []
    for subset, selected, policy in [('selective_answered', selective_cases, 'intent'),
                                     ('full_suite', full_cases, 'forced_choice_intent_ablation')]:
        for baseline in ('midpoint','frozen_heuristic'):
            differences = []
            for case in selected:
                rows = {r['policy']: r for r in case['policies']}
                differences.append(rows[policy]['regret']-rows[baseline]['regret'])
            comparisons.append({'subset': subset, 'policy': policy, 'baseline': baseline,
                                'evaluated_cases': len(selected), 'case_ids': ','.join(c['case_id'] for c in selected),
                                'mean_regret_difference': float(np.mean(differences)) if differences else None,
                                'wins': sum(v < 0 for v in differences), 'ties': sum(v == 0 for v in differences),
                                'losses': sum(v > 0 for v in differences)})
    selective_forced = next(r for r in selective if r['policy'] == 'forced_choice_intent_ablation')
    abstained_forced = next(r for r in abstention if r['policy'] == 'forced_choice_intent_ablation')
    # Missing candidates cannot yield a positive preregistered conclusion.
    fully_evaluable = len(full_cases) == len(cases) and len(selective_cases) == len(answered)
    placement = all(r['mean_regret_difference'] is not None and r['mean_regret_difference'] < 0
                    for r in comparisons if r['subset'] == 'selective_answered') if fully_evaluable and answered else None
    a, b = selective_forced['mean_regret'], abstained_forced['mean_regret']
    selective_quality = a < b if fully_evaluable and a is not None and b is not None else None
    return {'total_cases': len(cases), 'answered_cases': len(answered), 'abstained_cases': len(abstained),
            'recommendation_coverage': len(answered)/len(cases) if cases else None,
            'abstention_reasons': dict(Counter(c['decision']['abstention_reason'] for c in abstained)),
            'rankable_answered_cases': sum(c['oracle']['status']=='ok' for c in answered),
            'evaluation_completeness': sum(c['oracle']['status']=='ok' for c in answered)/len(answered) if answered else None,
            'rankable_total_cases': sum(c['oracle']['status']=='ok' for c in cases),
            'aggregates': selective+full+abstention, 'comparisons': comparisons,
            'criteria': {'placement_lower_regret_than_both_baselines': placement,
                         'answered_lower_forced_choice_regret_than_abstained': selective_quality},
            'interpretation': 'Criteria are descriptive; CPU/fake-backend values are not RIFE effectiveness evidence.'}


def run_intent_study(output='outputs/intent-guidance-study', backend='rife', backend_factory=None):
    root = Path(output)
    if root.exists() and any(root.iterdir()):
        raise ValueError('Use a fresh empty output directory; reports must not overwrite prior results')
    cases = make_cases()  # Collision validation before any backend execution.
    root.mkdir(parents=True, exist_ok=True)
    repo = Path(__file__).resolve().parents[1]
    frozen_files = ['docs/INTENT_GUIDANCE_PROTOCOL.md', 'inbetween/intent_cases.py',
                    'inbetween/intent_guidance.py', 'inbetween/intent_study.py',
                    'inbetween/position_study.py', 'inbetween/position_recommendation.py',
                    'inbetween/benchmark_metrics.py']
    provenance = {p: hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in frozen_files}
    # Persist the preregistered inputs before endpoint or candidate inference.
    preregistration = {'source_sha256': provenance, 'cases': [dict(c.metadata,
                      truth_pixel_hashes=[pixel_hash(f) for f in c.frames],
                      method_output=decide_intent(c.metadata['intent'])) for c in cases]}
    (root/'preregistration.json').write_text(json.dumps(preregistration, indent=2, allow_nan=False)+'\n')
    factory = backend_factory or m5.BACKENDS[backend]
    reports = [evaluate_case(c, root, factory) for c in cases]
    summary = summarize(reports)
    result = {'protocol': 'INTENT_GUIDANCE_PROTOCOL v1', 'backend': backend,
              'execution_kind': 'injected_backend_validation' if backend_factory else (
                  'local_rife_evaluation' if backend == 'rife' else 'cpu_validation'),
              'count': 6, 'source_sha256': provenance, 'cases': reports, 'summary': summary}
    (root/'results.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    policies = [{'case_id': c['case_id'], **r} for c in reports for r in c['policies']]
    candidates = [{'case_id': c['case_id'], 'k': r['k'], 't': r['t'], 'status': r['status'],
                   'error': r['error'], 'mean_rank': r['mean_rank'], **m5.flat_improvements(r)}
                  for c in reports for r in c['candidates']]
    decisions = [{'case_id': c['case_id'], **{k:v for k,v in c['decision'].items() if k != 'admitted_positions'},
                  'admitted_positions': ','.join(map(str,c['decision']['admitted_positions'])),
                  'oracle_status': c['oracle']['status'], 'endpoint_status': c['endpoint']['status'],
                  'endpoint_error': c['endpoint'].get('error')} for c in reports]
    lines = ['# Milestone 6 intent guidance with abstention', '',
             f"Execution: {result['execution_kind']}. Backend: {backend}.",
             'Deterministic ambiguity handling; not calibrated confidence or predicted RIFE failure.',
             'Procedural oracle drawings; no artist usability or final research contribution claim.',
             'Each candidate uses one D. Generated-only matched exclusions differ across k. Lower rank/regret is better.',
             'All method comparisons within each subset use identical cases. Abstention has null rank/regret; no fallback.',
             'Forced-choice intent is a separately labelled ablation. Runtime is diagnostic only.', '',
             f"Coverage: {summary['answered_cases']}/{summary['total_cases']} ({summary['recommendation_coverage']}); "
             f"rankable answered: {summary['rankable_answered_cases']}/{summary['answered_cases']}; "
             f"rankable total: {summary['rankable_total_cases']}/{summary['total_cases']}.",
             f"Abstention reasons: {summary['abstention_reasons']}",
             f"Descriptive criteria (CPU values are validation only): {summary['criteria']}", '']
    coverage = [{k: v for k, v in summary.items() if k not in ('aggregates', 'comparisons', 'criteria', 'interpretation', 'abstention_reasons')}]
    for filename, rows in [('coverage',coverage), ('decisions',decisions), ('aggregates',summary['aggregates']),
                           ('comparisons',summary['comparisons']), ('policy_comparison',policies), ('candidates',candidates)]:
        lines += [f'## {filename}', ''] + m5.write_table(root/f'{filename}.csv', rows) + ['']
    (root/'summary.md').write_text('\n'.join(lines)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=m5.BACKENDS, default='rife')
    parser.add_argument('--output', default='outputs/intent-guidance-study')
    args = parser.parse_args()
    result = run_intent_study(args.output, args.backend)
    print(json.dumps({'output': args.output, 'execution_kind': result['execution_kind'],
                      'successful_candidates': sum(r['status']=='ok' for c in result['cases'] for r in c['candidates']),
                      'coverage': result['summary']['recommendation_coverage']}))
    return 0 if all(c['oracle']['status']=='ok' for c in result['cases']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
