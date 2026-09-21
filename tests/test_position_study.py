import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import gradio as gr
import pytest
from PIL import Image
from inbetween import app, position_study as study
from inbetween.core import CrossfadeBackend
from inbetween.position_recommendation import normalize, recommend_position


class Fake(CrossfadeBackend):
    name = 'fake_position_test'
    calls = []

    def generate(self, a, b, count):
        self.calls.append(count)
        return super().generate(a, b, count)


@pytest.fixture(scope='module')
def full_study(tmp_path_factory):
    root = tmp_path_factory.mktemp('positions')
    Fake.calls = []
    result = study.run_position_study(root, backend_factory=Fake)
    return root, result, list(Fake.calls)


def test_complete_matched_exact_and_reports(full_study):
    root, result, calls = full_study
    assert len(calls) == 4 * 13
    for case in result['cases']:
        assert [r['k'] for r in case['candidates']] == list(range(1, 7))
        assert case['endpoint']['exact_pixel_checks'] == {'A': True, 'B': True}
        for r in case['candidates']:
            k = r['k']
            assert r['status'] == 'ok'
            assert r['endpoint_only']['evaluated_frame_indices'] == r['guided']['evaluated_frame_indices'] == [i for i in range(1, 7) if i != k]
            assert r['exact_pixel_checks'] == {'A': True, 'D': True, 'B': True}
            for method in ('endpoint_only', 'guided'):
                assert r['breakdown_index_metrics'][method]['frame_index'] == k
            assert r['breakdown_index_metrics']['guided']['is_authoritative_breakdown']
            assert (root/'visuals'/case['case_id']/f'k{k}'/'contact_sheet.png').exists()
        assert (root/'tables'/case['case_id']/'risk_components.csv').exists()
    json.loads((root/'results.json').read_text(), parse_constant=lambda x: pytest.fail(x))
    assert (root/'policy_comparison.csv').exists()


def test_recommender_only_observable_deterministic_and_missing():
    assert list(inspect.signature(recommend_position).parameters) == ['frames']
    frames = [Image.new('RGB', (16, 16), 'white') for _ in range(8)]
    a = recommend_position(frames)
    assert a == recommend_position(frames)
    assert a['recommended_k'] == 1
    assert 'centroid_acceleration' not in a['active_components']
    assert all(r['score'] == 0 and r['raw']['centroid_acceleration'] is None for r in a['positions'])
    assert normalize([4, 4, None]) == [0, 0, None]
    assert normalize([None, float('inf')]) == [None, None]
    json.dumps(a, allow_nan=False)


def candidates():
    return [{'k': k, 'status': 'ok', 'evaluated_frame_count': 2, 'paired_trajectory_indices': [1, 2],
             'improvement': {'edge_f1': v, 'chamfer_px': v, 'trajectory_error_px': -v}} for k, v in enumerate([0, 2, 1], 1)]


def test_oracle_directions_missing_ties_regret():
    rows = candidates()
    oracle = study.rank_candidates(rows, 3)
    assert oracle['best_k'] == 2 and oracle['worst_k'] == 1
    assert rows[1]['mean_rank'] == pytest.approx(5/3)
    rows[0]['paired_trajectory_indices'] = []
    rows[0]['improvement']['trajectory_error_px'] = None
    oracle = study.rank_candidates(rows, 3)
    assert oracle['metrics'] == ['edge_f1', 'chamfer_px']
    assert [r['mean_rank'] for r in rows] == [3, 1, 2]
    policies = study.policy_comparison(rows, {'recommended_k': 3}, oracle, 3)
    assert policies[0]['regret'] == 1
    for row in rows:
        row['improvement']['edge_f1'] = row['improvement']['chamfer_px'] = 0
    oracle = study.rank_candidates(rows, 3)
    assert oracle['best_k'] == oracle['worst_k'] == 1
    assert all(r['mean_rank'] == 2 for r in rows)
    rows[0]['status'] = 'failed'
    assert study.rank_candidates(rows, 3)['best_k'] is None
    assert all(r['mean_rank'] is None for r in rows)


def test_baselines():
    assert [study.midpoint(n) for n in (1, 2, 5, 6)] == [1, 1, 3, 3]
    assert study.random_position(6) == study.random_position(6)
    assert 1 <= study.random_position(6) <= 6


def test_candidate_failure_isolated_and_no_truth_to_recommendation(tmp_path, monkeypatch):
    monkeypatch.setattr(study, 'CATEGORIES', ('curved_arc',))
    original = study.create_guided_run
    def fail_one(*args, **kwargs):
        if args[4] == 2:
            raise RuntimeError('candidate two failed')
        return original(*args, **kwargs)
    monkeypatch.setattr(study, 'create_guided_run', fail_one)
    seen = []
    def observable_only(frames):
        seen.append(len(frames))
        assert len(Fake.calls) == 1  # recommendation precedes ALL oracle calls
        return recommend_position(frames)
    Fake.calls = []
    monkeypatch.setattr(study, 'recommend_position', observable_only)
    result = study.run_position_study(tmp_path, backend_factory=Fake)['cases'][0]
    assert seen == [8]
    assert [r['status'] for r in result['candidates']] == ['ok', 'failed', 'ok', 'ok', 'ok', 'ok']
    assert result['oracle']['status'] == 'incomplete_candidate_coverage'
    assert all(p['regret'] is None for p in result['policies'])


def test_endpoint_failure_records_all_candidates(tmp_path, monkeypatch):
    monkeypatch.setattr(study, 'CATEGORIES', ('curved_arc', 'occlusion'))
    class Failed(Fake):
        def generate(self, *args):
            raise RuntimeError('endpoint failed')
    result = study.run_position_study(tmp_path, backend_factory=Failed)
    assert len(result['cases']) == 2
    assert all(len(c['candidates']) == 6 and all(r['status']=='failed' for r in c['candidates']) for c in result['cases'])


def test_cli_without_pythonpath(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
    proc = subprocess.run([sys.executable, '-m', 'inbetween.position_study', '--help'], env=env,
                          cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
    assert proc.returncode == 0 and '--backend' in proc.stdout


def test_ui_error_no_fallback(monkeypatch):
    calls = []
    def fail(*args, **kwargs):
        calls.append(type(kwargs['backend']).__name__)
        raise RuntimeError('RIFE error')
    monkeypatch.setattr(app, 'create_run', fail)
    with pytest.raises(gr.Error, match='RIFE error'):
        app.recommend_ui('a.png', 'b.png', 6)
    assert calls == ['RifeBackend']


def test_real_model_guard():
    import importlib
    with pytest.raises(AssertionError, match='forbidden'):
        importlib.import_module('model.RIFE')


def test_paired_gain_directions_and_perfect_psnr(full_study):
    for case in full_study[1]['cases']:
        for r in case['candidates']:
            a, b = r['endpoint_only']['means'], r['guided']['means']
            assert r['improvement']['edge_f1'] == pytest.approx(b['edge_f1']-a['edge_f1'])
            assert r['improvement']['chamfer_px'] == pytest.approx(a['chamfer_px']-b['chamfer_px'])
            oracle = r['breakdown_index_metrics']['guided']
            assert oracle['psnr_db'] is None and oracle['psnr_perfect_match']
    row = {'frame_index': 1, 'psnr_db': None, 'psnr_perfect_match': True,
           'ssim': 1, 'edge_f1': 1, 'chamfer_px': 0, 'trajectory_error_px': None}
    agg = study.aggregate([row])
    assert agg['means']['psnr_db'] is None
    assert agg['psnr_mean_undefined_due_to_perfect_match']


def test_risk_nonconstant_and_partial_centroid():
    import numpy as np
    frames = []
    for x in (1, 2, 3, 12, 13):
        a = np.full((24, 24, 3), 255, dtype=np.uint8)
        a[8:16, x:x+3] = 0
        frames.append(Image.fromarray(a))
    result = recommend_position(frames)
    assert 'centroid_acceleration' in result['active_components']
    assert len({r['score'] for r in result['positions']}) > 1
    frames[2] = Image.new('RGB', (24, 24), 'white')
    result = recommend_position(frames)
    assert 'centroid_acceleration' not in result['active_components']
    json.dumps(result, allow_nan=False)


def test_ui_success_requires_only_endpoints(tmp_path, monkeypatch):
    a, b = tmp_path/'a.png', tmp_path/'b.png'
    Image.new('RGB', (16, 16), 'white').save(a)
    Image.new('RGB', (16, 16), 'black').save(b)
    original = app.create_run
    def local_run(*args, **kwargs):
        return original(*args, **kwargs, output_root=tmp_path/'ui')
    monkeypatch.setattr(app, 'create_run', local_run)
    monkeypatch.setattr(app, 'RifeBackend', Fake)
    Fake.calls = []
    k, scores, preview = app.recommend_ui(a, b, 6)
    assert 1 <= k <= 6 and len(scores['positions']) == 6
    assert Fake.calls == [6] and Path(preview).exists()
