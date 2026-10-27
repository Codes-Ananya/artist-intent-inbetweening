import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from PIL import Image
from inbetween.core import InterpolationBackend
from inbetween.guided import _equal
from inbetween.run import _sha
from scripts import run_sfp01_extra_breakdown as runner


class FakeBackend(InterpolationBackend):
    name = 'test_only_no_inference'
    version = 'test'

    def __init__(self):
        self.calls = []
        self.last_run_metadata = {}

    def generate(self, first, last, intermediate_count):
        self.calls.append((first.copy(), last.copy(), intermediate_count))
        assert intermediate_count == 1
        return [first.copy(), Image.blend(first, last, .5), last.copy()]

    def _require_assets_and_cuda(self):
        return SimpleNamespace(cuda=SimpleNamespace(mem_get_info=lambda _: (1, 2), get_device_properties=lambda _: SimpleNamespace(name='TEST ONLY'))), None


def test_only_two_local_midpoints_and_exact_reuse():
    baseline = [Image.new('RGB', (8, 8), (i * 20, 0, 0)) for i in range(8)]
    pose = Image.new('RGB', (8, 8), 'green')
    backend = FakeBackend()
    result, metadata = runner.assemble([baseline[i] for i in (0, 4, 7)], pose, baseline, backend)
    assert len(result) == 8
    assert len(backend.calls) == 2
    assert _equal(backend.calls[0][0], baseline[0]) and _equal(backend.calls[0][1], pose)
    assert _equal(backend.calls[1][0], pose) and _equal(backend.calls[1][1], baseline[4])
    for i in (0, 4, 5, 6, 7):
        assert _equal(result[i], baseline[i])
    assert _equal(result[2], pose)
    assert metadata['inferred_frame_count'] == 2
    assert runner.labels(True).count('supplied') == 4
    assert runner.labels(True).count('reused historical generated') == 2


def test_approval_requires_matching_hash_and_explicit_review(tmp_path):
    pose = tmp_path / 'pose.png'
    Image.new('RGB', (512, 512)).save(pose)
    path = tmp_path / 'approval.json'
    approval = dict(status='pending_visual_review', frame2_sha256=_sha(pose))
    path.write_text(json.dumps(approval))
    with pytest.raises(ValueError, match='Explicit visual approval'):
        runner.verify_approval(path, pose)
    approval.update(status='approved_for_inference', reviewer='TEST FIXTURE', approved_at='TEST ONLY', user_approval_text='TEST FIXTURE ONLY')
    path.write_text(json.dumps(approval))
    assert runner.verify_approval(path, pose) == approval
    Image.new('RGB', (512, 512), 'red').save(pose)
    with pytest.raises(ValueError):
        runner.verify_approval(path, pose)


def test_pending_approval_stops_before_backend_and_output(tmp_path, monkeypatch):
    pose = tmp_path / 'pose.png'
    Image.new('RGB', (512, 512)).save(pose)
    approval = tmp_path / 'approval.json'
    approval.write_text(json.dumps({'status': 'pending_visual_review'}))
    monkeypatch.setattr(runner, 'verify_archive', lambda _: pytest.fail('Reached archive before approval gate'))
    with pytest.raises(ValueError):
        runner.main(['--frame2', str(pose), '--approval', str(approval), '--output', str(tmp_path / 'out')])
    assert not (tmp_path / 'out').exists()


def test_fake_backend_sample_export(tmp_path, monkeypatch):
    if not runner.BASELINE.exists():
        pytest.skip('Local archived baseline unavailable')
    import inbetween.rife
    monkeypatch.setattr(inbetween.rife, 'RifeBackend', FakeBackend)
    pose = tmp_path / 'TEST_ONLY_pose.png'
    Image.new('RGB', (512, 512), 'green').save(pose)
    approval = tmp_path / 'TEST_ONLY_approval.json'
    approval.write_text(json.dumps(dict(status='approved_for_inference', frame2_sha256=_sha(pose), reviewer='TEST FIXTURE', approved_at='TEST ONLY', user_approval_text='TEST FIXTURE ONLY; not user approval')))
    out = tmp_path / 'TEST_ONLY_fake_backend_export'
    assert runner.main(['--frame2', str(pose), '--approval', str(approval), '--output', str(out)]) == 0
    report = json.loads((out / 'results.json').read_text())
    assert report['baseline_and_inputs_unchanged']
    assert report['budgets']['extra_breakdown']['newly_generated'] == 2
    assert all(report['saved_supplied_reused_exact_pixel_checks'].values())
    assert len(list((out / 'extra_breakdown').glob('frame_*.png'))) == 8
    assert (out / 'side_by_side/animation.mp4').is_file()
    assert (out / 'side_by_side/animation.gif').is_file()
    assert (out / 'labelled_contact_sheet.png').is_file()
    with pytest.raises(FileExistsError):
        runner.main(['--frame2', str(pose), '--approval', str(approval), '--output', str(out)])


def test_baseline_tamper_rejected(tmp_path, monkeypatch):
    data = tmp_path / 'evidence.txt'
    data.write_text('original')
    manifest = tmp_path / 'archive.sha256'
    manifest.write_text(f'{_sha(data)}  evidence.txt\n')
    monkeypatch.setattr(runner, 'BASELINE_ARCHIVE_SHA256', _sha(manifest))
    runner.verify_archive(tmp_path)
    data.write_text('tampered')
    with pytest.raises(ValueError, match='archive mismatch'):
        runner.verify_archive(tmp_path)
    manifest.write_text('tampered manifest')
    with pytest.raises(ValueError, match='manifest differs'):
        runner.verify_archive(tmp_path)
