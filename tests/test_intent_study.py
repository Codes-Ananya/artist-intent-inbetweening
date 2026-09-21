import copy
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys

import pytest
from inbetween.core import CrossfadeBackend
from inbetween import intent_cases, intent_guidance, intent_study
from inbetween import position_study as m5


class Fake(CrossfadeBackend):
    name = 'fake_intent_test'
    calls = []

    def generate(self, a, b, count):
        self.calls.append(count)
        return super().generate(a, b, count)


@pytest.fixture(scope='module')
def full(tmp_path_factory):
    root = tmp_path_factory.mktemp('intent')
    Fake.calls = []
    result = intent_study.run_intent_study(root, backend_factory=Fake)
    return root, result, list(Fake.calls)


def test_vocabulary_phases_and_ambiguity():
    assert [intent_guidance.phase_at(k) for k in range(1,7)] == ['early','early','middle','middle','late','late']
    for phase, k in [('early',2),('middle',3),('late',5)]:
        record = [{'event':'path_turn', 'phase':phase}]
        output = intent_guidance.decide_intent(record)
        assert output['recommended_k'] == k and output['status'] == 'answered'
        assert output == intent_guidance.decide_intent(record*2)
    for record, reason in [(None,'missing_intent'), ([], 'missing_intent'),
                           ([{'event':'unknown','phase':'early'}], 'unsupported_intent'),
                           ([{'event':'path_turn','phase':'unspecified'}], 'unspecified_phase'),
                           ([{'event':'path_turn','phase':'early'}, {'event':'pose_extremum','phase':'late'}], 'conflicting_event_phases')]:
        output = intent_guidance.decide_intent(record)
        assert output['recommended_k'] is None and output['abstention_reason'] == reason
    assert list(inspect.signature(intent_guidance.decide_intent).parameters) == ['events']
    with pytest.raises(ValueError):
        intent_guidance.phase_at(1,5)


def test_cases_frozen_unique_and_collision_rejection():
    a, b = intent_cases.make_cases(), intent_cases.make_cases()
    assert len(a) == 10
    hashes = [[intent_cases.pixel_hash(f) for f in c.frames] for c in a]
    assert hashes == [[intent_cases.pixel_hash(f) for f in c.frames] for c in b]
    assert len({h[i] for h in hashes for i in (0,7)}) == 20
    assert [intent_guidance.decide_intent(c.metadata['intent'])['recommended_k'] for c in a] == [2,2,3,3,5,5,None,None,None,None]
    a[1].frames[0] = a[0].frames[7].copy()
    with pytest.raises(ValueError, match='collision'):
        intent_cases.validate_endpoints(a)
    a = intent_cases.make_cases()
    a[0].frames[0] = intent_cases.make_case('curved_arc',6).frames[0]
    with pytest.raises(ValueError, match='collision'):
        intent_cases.validate_endpoints(a)


def test_full_one_breakdown_exact_pairing_and_strict_reports(full):
    root, result, calls = full
    assert result['execution_kind'] == 'injected_backend_validation'
    assert calls == [6,0,5,1,4,2,3,3,2,4,1,5,0]*10
    summary = result['summary']
    assert summary['recommendation_coverage'] == .6
    assert summary['evaluation_completeness'] == 1
    assert summary['rankable_total_cases'] == 10
    assert summary['abstention_reasons'] == {'unspecified_phase':2, 'conflicting_event_phases':2}
    for case in result['cases']:
        assert all(case['endpoint']['exact_pixel_checks'].values())
        assert len(case['candidates']) == 6
        for candidate in case['candidates']:
            k = candidate['k']
            assert candidate['status'] == 'ok'
            assert candidate['t'] == k/7
            assert candidate['exact_pixel_checks'] == {'A':True,'D':True,'B':True}
            assert candidate['endpoint_only']['evaluated_frame_indices'] == candidate['guided']['evaluated_frame_indices'] == [i for i in range(1,7) if i != k]
            assert candidate['breakdown_index_metrics']['guided']['psnr_perfect_match']
            assert candidate['manifest']['guided_breakdown']['inferred_frame_count'] == 5
        independent = copy.deepcopy(case['candidates'])
        assert m5.rank_candidates(independent,6) == case['oracle']
        assert [r['mean_rank'] for r in independent] == [r['mean_rank'] for r in case['candidates']]
        intent = case['policies'][0]
        if case['decision']['status'] == 'abstained':
            assert intent['k'] is intent['mean_rank'] is intent['regret'] is None
            assert intent['status'] == 'abstained'
    for path in root.rglob('*.json'):
        json.loads(path.read_text(), parse_constant=lambda x: pytest.fail(x))
    for name in ('decisions','aggregates','comparisons','policy_comparison','candidates'):
        assert (root/f'{name}.csv').is_file()
    for subset in ('selective_answered','full_suite','abstained_forced_choice_analysis'):
        rows = [r for r in summary['aggregates'] if r['subset']==subset]
        assert len({r['case_ids'] for r in rows}) == 1
        assert all(r['evaluated_cases'] == (6 if subset=='selective_answered' else 10 if subset=='full_suite' else 4) for r in rows)
    assert all(r['policy'] != 'intent' for r in summary['aggregates'] if r['subset']=='full_suite')
    assert 'pre-registered method outputs' in (root/'summary.md').read_text()
    with pytest.raises(ValueError, match='fresh'):
        intent_study.run_intent_study(root, backend_factory=Fake)


def test_candidate_failure_inference_isolation_and_predecision(tmp_path, monkeypatch):
    monkeypatch.setattr(intent_study, 'make_cases', lambda: intent_cases.make_cases()[:1])
    original = m5.create_guided_run
    seen = []
    def frozen_input(frames):
        assert Fake.calls == [6]
        assert (tmp_path/'preregistration.json').exists()
        seen.append(len(frames))
        return {'recommended_k': 1}
    def fail_one(*args, **kwargs):
        if args[4] == 2:
            raise RuntimeError('failed candidate')
        return original(*args, **kwargs)
    monkeypatch.setattr(m5, 'recommend_position', frozen_input)
    monkeypatch.setattr(m5, 'create_guided_run', fail_one)
    Fake.calls = []
    result = intent_study.run_intent_study(tmp_path, backend_factory=Fake)
    case = result['cases'][0]
    assert seen == [8]
    assert [r['status'] for r in case['candidates']] == ['ok','failed','ok','ok','ok','ok']
    assert all(r['regret'] is None for r in case['policies'])
    assert result['summary']['evaluation_completeness'] == 0
    assert all(v is None for v in result['summary']['criteria'].values())


def test_endpoint_failure_does_not_change_coverage_or_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(intent_study, 'make_cases', lambda: intent_cases.make_cases()[5:7])
    class Failed(Fake):
        def generate(self, *args):
            raise RuntimeError('endpoint unavailable')
    result = intent_study.run_intent_study(tmp_path, backend_factory=Failed)
    assert result['summary']['recommendation_coverage'] == .5
    assert result['summary']['rankable_total_cases'] == 0
    assert all(c['endpoint']['status']=='failed' for c in result['cases'])
    assert all(r['status']=='failed' for c in result['cases'] for r in c['candidates'])
    assert all(r['mean_regret'] is None for r in result['summary']['aggregates'])


def test_missing_policy_uses_shared_intersection(full):
    cases = copy.deepcopy(full[1]['cases'])
    cases[0]['policies'][2]['regret'] = None
    summary = intent_study.summarize(cases)
    for subset in ('selective_answered','full_suite'):
        rows = [r for r in summary['aggregates'] if r['subset']==subset]
        assert all('hinged_gate' not in r['case_ids'] for r in rows)
        assert len({r['case_ids'] for r in rows}) == 1
    assert all(v is None for v in summary['criteria'].values())


def test_all_abstain_no_zero_regret(full):
    cases = copy.deepcopy(full[1]['cases'][6:])
    summary = intent_study.summarize(cases)
    assert summary['recommendation_coverage'] == 0
    assert summary['evaluation_completeness'] is None
    assert all(r['mean_regret'] is None for r in summary['aggregates'] if r['subset']=='selective_answered')


def test_cli_and_frozen_m5_sources():
    repo = Path(__file__).resolve().parents[1]
    proc = subprocess.run([sys.executable,'-m','inbetween.intent_study','--help'], cwd=repo, capture_output=True, text=True)
    assert proc.returncode == 0 and '--backend' in proc.stdout
    # Literal hashes freeze the baseline without requiring git at test time.
    expected = json.loads((repo/'tests/fixtures/milestone5_source_hashes.json').read_text())
    for path, digest in expected.items():
        assert hashlib.sha256((repo/path).read_bytes()).hexdigest() == digest


def test_malformed_nested_values_abstain():
    for record in ([{'event': [], 'phase': 'early'}], [{'event':'path_turn', 'phase': {}}],
                   [{'event':'path_turn', 'phase':'early', 'oracle_k':2}],
                   [{'event':'path_turn', 'phase':'early'}]*3):
        result = intent_guidance.decide_intent(record)
        assert result['abstention_reason'] == 'unsupported_intent'
        assert result['recommended_k'] is None
        assert result['forced_choice_ablation_k'] == 3


def test_success_criteria_strict_ties_and_paired_differences(full):
    cases = copy.deepcopy(full[1]['cases'])
    for c in cases:
        for p in c['policies']:
            if p['status'] == 'abstained':
                continue
            p['regret'] = {'intent': 1, 'midpoint': 2, 'frozen_heuristic': 3,
                           'oracle_best': 0, 'forced_choice_intent_ablation':
                           1 if c['decision']['status']=='answered' else 4}[p['policy']]
    summary = intent_study.summarize(cases)
    assert all(v is True for v in summary['criteria'].values())
    paired = [r for r in summary['comparisons'] if r['subset']=='selective_answered']
    assert all(r['wins']==6 and r['ties']==r['losses']==0 for r in paired)
    for c in cases:
        for p in c['policies']:
            if p['policy']=='midpoint':
                p['regret'] = 1
            if p['policy']=='forced_choice_intent_ablation':
                p['regret'] = 1
    assert all(v is False for v in intent_study.summarize(cases)['criteria'].values())


@pytest.mark.parametrize('execution_kind, expected', [
    ('local_rife_evaluation', 'GPU experimental results'),
    ('cpu_validation', 'CPU/injected runs are validation-only'),
    ('injected_backend_validation', 'CPU/injected runs are validation-only'),
])
def test_criteria_description_uses_execution_provenance(execution_kind, expected):
    # Exercise GPU reporting with synthetic values only; never invoke inference.
    criteria = {'placement_lower_regret_than_both_baselines': False,
                'answered_lower_forced_choice_regret_than_abstained': False}
    line = intent_study.criteria_description(execution_kind, criteria)
    assert line == f'Descriptive criteria ({expected}): {criteria}'


def test_injected_rife_summary_is_validation_only(full):
    root, result, _ = full
    assert result['backend'] == 'rife'
    assert result['execution_kind'] == 'injected_backend_validation'
    summary = (root/'summary.md').read_text()
    assert 'Descriptive criteria (CPU/injected runs are validation-only):' in summary
    assert 'GPU experimental results' not in summary
