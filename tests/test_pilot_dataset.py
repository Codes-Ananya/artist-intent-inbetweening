"""CPU-only schema/ingest tests. All drawings are SYNTHETIC GEOMETRIC FIXTURES.

Temporary files are validator test inputs, never artist data or pilot results.
No interpolation, metric evaluation, model load, or persistent dataset creation.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw, PngImagePlugin
import pytest

from inbetween.pilot_dataset import (
    ValidationError, event_time, load_manifest, sha256, validate_dataset, validate_manifest,
)

TEMPLATES = Path(__file__).resolve().parents[1] / 'docs' / 'real_input_templates'
DATE = '2026-09-22T09:00:00+00:00'


def fill_template(value):
    if isinstance(value, dict):
        return {k: fill_template(v) for k, v in value.items()}
    if isinstance(value, list):
        return [fill_template(v) for v in value]
    if isinstance(value, str) and value.startswith('REPLACE_'):
        if 'ISO8601' in value:
            return DATE
        if 'sha256' in value:
            return '0' * 64
        return 'SYNTHETIC TEST ONLY; no artist, permission, or model claim'
    return value


def make_sequence(root, track='A', number=1):
    """Write only temporary, uniquely positioned geometric test PNGs."""
    m = fill_template(json.loads((TEMPLATES / f'track_{track.lower()}.json').read_text()))
    m['sequence_id'] = f'{track.lower()}{number:02d}'
    m['rights']['consent_status'] = 'not_required'
    m['rights']['consent_basis'] = 'SYNTHETIC TEST ONLY: rectangles; no depicted person'
    if track == 'D':
        m['motion'] = ('curved_jump', 'hold_then_fast_reach',
                       'exaggerated_recoil', 'body_turn_self_occlusion')[number - 1]
    folder = root / f'track_{track.lower()}' / m['sequence_id']
    (folder / 'frames').mkdir(parents=True)
    for f in m['frames']:
        im = Image.new('RGB', (512, 512), (248, 246, 240))
        x = number * 35 + f['index'] * 2
        y = 25 if track == 'A' else 250
        ImageDraw.Draw(im).rectangle((x, y, x + 15, y + 20), fill=(10, 10, 10))
        path = folder / f['path']
        im.save(path)
        f['sha256'] = sha256(path)
        f['preprocessing'].update(source_sha256=f['sha256'], output_sha256=f['sha256'])
    m['selection']['D_sha256'] = m['frames'][3 if track == 'A' else 1]['sha256']
    save_manifest(folder, m)
    return folder, m


def save_manifest(folder, m):
    (folder / 'manifest.json').write_text(json.dumps(m))


@pytest.mark.parametrize('track', ['A', 'D'])
def test_templates_are_not_data_and_filled_contract_passes(tmp_path, track):
    with pytest.raises(ValidationError, match='placeholder'):
        validate_manifest(json.loads((TEMPLATES / f'track_{track.lower()}.json').read_text()))
    _, m = make_sequence(tmp_path, track)
    validate_manifest(m)
    assert validate_dataset(tmp_path, complete=False)['status'] == 'partial_ingest_only'
    with pytest.raises(ValidationError):
        validate_dataset(tmp_path)


def test_full_roster_and_track_separation(tmp_path):
    for track, count in [('A', 6), ('D', 4)]:
        for number in range(1, count + 1):
            make_sequence(tmp_path, track, number)
    result = validate_dataset(tmp_path)
    assert result['status'] == 'complete_ingest'
    assert result['frame_count'] == 60
    assert len(result['primary_sequences']) == 6
    assert len(result['exploratory_sequences']) == 4


def test_track_d_independent_ingest_still_requires_track_a_for_complete(tmp_path):
    for number in range(1, 5):
        make_sequence(tmp_path, 'D', number)
    result = validate_dataset(tmp_path, complete=False)
    assert result['exploratory_sequences'] == ['d01', 'd02', 'd03', 'd04']
    assert result['primary_sequences'] == []
    assert result['frame_count'] == 12
    assert result['status'] == 'partial_ingest_only'
    with pytest.raises(ValidationError, match='missing track_a'):
        validate_dataset(tmp_path)


@pytest.mark.parametrize('k', [0, 7, -1, 3.0, True, '3', None])
def test_invalid_k(tmp_path, k):
    _, m = make_sequence(tmp_path)
    m['selection']['k'] = k
    with pytest.raises(ValidationError, match='k must'):
        validate_manifest(m)


@pytest.mark.parametrize('k', range(1, 7))
def test_all_valid_artist_positions(tmp_path, k):
    _, m = make_sequence(tmp_path)
    m['selection'].update(k=k, D_path=m['frames'][k]['path'], D_sha256=m['frames'][k]['sha256'])
    validate_manifest(m)


@pytest.mark.parametrize('section,key,value', [
    ('selection', 'D_path', 'frames/frame_004.png'),
    ('selection', 'D_sha256', '1' * 64),
    ('selection', 'before_model_results', False),
    ('selection', 'selected_at', '2020-01-01T00:00:00Z'),
    ('selection', 'kind', 'exploratory_curator'),
    ('provenance', 'creator', ''),
    ('provenance', 'tools', []),
    ('provenance', 'source_files', []),
    ('provenance', 'method', 'ai_generated'),
    ('provenance', 'created_at', '2026-09-22'),
    ('rights', 'consent_status', 'pending'),
    ('rights', 'usage_basis', ''),
    ('rights', 'confirmed_at', 'not a date'),
])
def test_incomplete_or_inconsistent_provenance(tmp_path, section, key, value):
    _, m = make_sequence(tmp_path)
    m[section][key] = value
    with pytest.raises(ValidationError):
        validate_manifest(m)


@pytest.mark.parametrize('mutation', ['unknown', 'missing', 'AI', 'purpose', 'count', 'order',
                                     'path', 'hash', 'preprocess', 'original', 'edits', 'frame_AI'])
def test_manifest_contract_rejections(tmp_path, mutation):
    _, m = make_sequence(tmp_path)
    f = m['frames'][0]
    if mutation == 'unknown':
        m['surprise'] = 1
    elif mutation == 'missing':
        del m['rights']
    elif mutation == 'AI':
        m['ai_generation'] = {}
    elif mutation == 'purpose':
        m['purpose'] = 'exploratory_only'
    elif mutation == 'count':
        m['frames'].pop()
    elif mutation == 'order':
        m['frames'].reverse()
    elif mutation == 'path':
        f['path'] = '../outside.png'
    elif mutation == 'hash':
        f['sha256'] = 'bad'
    elif mutation == 'preprocess':
        f['preprocessing']['source_sha256'] = '1' * 64
    elif mutation == 'original':
        f['preprocessing']['original_preserved'] = False
    elif mutation == 'edits':
        f['edits'] = 'cleanup'
    elif mutation == 'frame_AI':
        f['ai_generation'] = {}
    with pytest.raises(ValidationError):
        validate_manifest(m)


def test_preprocessing_is_explicit(tmp_path):
    _, m = make_sequence(tmp_path)
    pre = m['frames'][0]['preprocessing']
    pre['source_sha256'] = '1' * 64
    pre['operations'] = ['SYNTHETIC TEST ONLY: RGB export from retained source']
    validate_manifest(m)
    pre['output_sha256'] = '1' * 64
    with pytest.raises(ValidationError, match='output hash'):
        validate_manifest(m)


@pytest.mark.parametrize('key,value', [('provider', ''), ('prompt_provenance', {}), ('seed', True),
                                     ('model_identifier', {}), ('usage_basis', ''), ('human_role', [])])
def test_generation_disclosure_required_at_both_levels(tmp_path, key, value):
    _, m = make_sequence(tmp_path, 'D')
    for target in ('sequence', 'frame'):
        bad = copy.deepcopy(m)
        g = bad['ai_generation'] if target == 'sequence' else bad['frames'][0]['ai_generation']
        g[key] = value
        with pytest.raises(ValidationError):
            validate_manifest(bad)


def test_multiple_usage_authorities_not_ownership(tmp_path):
    _, m = make_sequence(tmp_path, 'D')
    r = m['rights']
    r['authorities'] = ['SYNTHETIC collaborator one', 'SYNTHETIC collaborator two']
    r['confirmed_by'] = list(r['authorities'])
    validate_manifest(m)
    r['confirmed_by'].pop()
    with pytest.raises(ValidationError, match='authorities must confirm'):
        validate_manifest(m)
    r['confirmed_by'] = list(r['authorities'])
    r['declaration_scope'] = 'legal_ownership'
    with pytest.raises(ValidationError, match='not ownership'):
        validate_manifest(m)


@pytest.mark.parametrize('precision,value,reason,valid', [
    ('exact', DATE, None, True),
    ('date_only', '2026-09-22', None, True),
    ('unavailable', None, 'SYNTHETIC: event time not retained', True),
    ('unavailable', None, '', False),
    ('unavailable', None, '   ', False),
    ('unavailable', DATE, 'not exposed', False),
    ('date_only', DATE, None, False),
    ('date_only', '2026-02-30', None, False),
    ('exact', '2026-09-22T09:00:00', None, False),
    ('exact', '2026-09-22', None, False),
    ('unknown', None, 'missing', False),
    ('date_only', '2026-09-22', 'contradiction', False),
])
def test_timestamp_precision(precision, value, reason, valid):
    value = dict(precision=precision, value=value, reason=reason, source='SYNTHETIC evidence')
    if valid:
        event_time(value, 'test')
    else:
        with pytest.raises(ValidationError):
            event_time(value, 'test')


def test_event_time_is_not_recording_time(tmp_path):
    _, m = make_sequence(tmp_path, 'D')
    before = copy.deepcopy(m['selection']['selected_at'])
    m['selection']['recorded_at'] = '2026-10-01T12:00:00Z'
    validate_manifest(m)
    assert m['selection']['selected_at'] == before
    m['selection']['selected_at'] = dict(precision='date_only', value='2026-09-22',
                                        reason=None, source='SYNTHETIC selection evidence')
    validate_manifest(m)  # No midnight/zone is assigned to the event.
    m['selection']['selected_at']['value'] = '2026-10-10'
    with pytest.raises(ValidationError, match='after recording'):
        validate_manifest(m)


@pytest.mark.parametrize('path', ['model_identifier', 'seed', 'inference_settings', 'internal_expanded_prompt'])
@pytest.mark.parametrize('damage', ['reason', 'value'])
def test_unavailable_disclosures_require_reason_and_null(tmp_path, path, damage):
    _, m = make_sequence(tmp_path, 'D')
    for g in [m['ai_generation']] + [f['ai_generation'] for f in m['frames']]:
        v = g['prompt_provenance'][path] if path == 'internal_expanded_prompt' else g[path]
        v[damage] = '' if damage == 'reason' else 'invented'
    with pytest.raises(ValidationError):
        validate_manifest(m)


@pytest.mark.parametrize('damage', ['no_instructions', 'internal_kind', 'copy_internal',
                                   'pending', 'empty_source', 'gpu', 'provider', 'authorship',
                                   'frame_mismatch', 'event_mismatch', 'no_attestation',
                                   'authorities', 'usage', 'seed_type', 'future_creation'])
def test_v2_incomplete_or_contradictory_disclosures(tmp_path, damage):
    _, m = make_sequence(tmp_path, 'D')
    g = m['ai_generation']
    p = g['prompt_provenance']
    if damage == 'no_instructions':
        p['conversation_instructions'] = []
    elif damage == 'internal_kind':
        p['conversation_instructions'][0]['kind'] = 'internal_generation_prompt'
    elif damage == 'copy_internal':
        p['internal_expanded_prompt'] = dict(status='available', reason=None,
                                             value=p['conversation_instructions'][0]['text'])
    elif damage == 'pending':
        p['conversation_instructions'][0]['text'] = 'pending_transcription_from_conversation'
    elif damage == 'empty_source':
        p['conversation_instructions'][0]['source'] = ''
    elif damage == 'gpu':
        g['local_gpu_used'] = True
    elif damage == 'provider':
        g['provider'] = 'contradictory provider'
    elif damage == 'authorship':
        g['D_authorship'] = 'independently human-drawn'
    elif damage == 'frame_mismatch':
        m['frames'][0]['ai_generation']['seed']['reason'] = 'different source record'
    elif damage == 'event_mismatch':
        g['generated_at']['value'] = '2026-09-01T09:00:00Z'
    elif damage == 'no_attestation':
        m['selection']['before_model_results_basis'] = ''
    elif damage == 'authorities':
        m['rights']['authorities'] = []
    elif damage == 'usage':
        m['rights']['permitted_uses'] = ['portfolio_demonstration']
    elif damage == 'seed_type':
        g['seed'] = dict(status='available', value=True, reason=None)
    else:
        m['provenance']['created_at']['value'] = '2026-10-10T00:00:00Z'
    with pytest.raises(ValidationError):
        validate_manifest(m)


def test_date_only_and_unavailable_d_do_not_relax_primary(tmp_path):
    _, d = make_sequence(tmp_path, 'D')
    event = dict(precision='date_only', value='2026-09-22', reason=None,
                 source='SYNTHETIC date-only evidence')
    d['provenance']['created_at'] = copy.deepcopy(event)
    d['ai_generation']['generated_at'] = copy.deepcopy(event)
    for f in d['frames']:
        f['created_at'] = copy.deepcopy(event)
        f['ai_generation']['generated_at'] = copy.deepcopy(event)
    d['selection']['selected_at'] = copy.deepcopy(event)
    validate_manifest(d)
    d['selection']['selected_at'] = dict(precision='unavailable', value=None,
                                       reason='SYNTHETIC time not retained', source='SYNTHETIC record')
    validate_manifest(d)  # The pre-results attestation is still mandatory.
    _, a = make_sequence(tmp_path, 'A')
    a['provenance']['created_at'] = event
    with pytest.raises(ValidationError):
        validate_manifest(a)
    a['version'] = 2
    with pytest.raises(ValidationError, match='Track D only'):
        validate_manifest(a)


@pytest.mark.parametrize('damage', ['missing', 'extra', 'hash', 'size', 'mode', 'format', 'corrupt', 'symlink'])
def test_image_validation(tmp_path, damage):
    folder, m = make_sequence(tmp_path)
    path = folder / m['frames'][0]['path']
    if damage == 'missing':
        path.unlink()
    elif damage == 'extra':
        (folder / 'frames' / 'D.png').write_bytes(path.read_bytes())
    elif damage == 'hash':
        path.write_bytes(path.read_bytes() + b'changed')
    elif damage == 'symlink':
        path.unlink()
        path.symlink_to(folder / m['frames'][1]['path'])
    else:
        if damage == 'size':
            Image.new('RGB', (64, 64)).save(path)
        elif damage == 'mode':
            Image.new('RGBA', (512, 512)).save(path)
        elif damage == 'format':
            Image.new('RGB', (512, 512)).save(path, format='BMP')
        else:
            path.write_bytes(b'not an image')
        m['frames'][0]['sha256'] = sha256(path)
        m['frames'][0]['preprocessing'].update(source_sha256=sha256(path), output_sha256=sha256(path))
        save_manifest(folder, m)
    with pytest.raises(ValidationError):
        validate_dataset(tmp_path, complete=False)


@pytest.mark.parametrize('cross_track,reencode', [(False, False), (False, True), (True, False)])
def test_duplicates_include_decoded_pixels_and_cross_track(tmp_path, cross_track, reencode):
    folder, m = make_sequence(tmp_path)
    source = folder / m['frames'][0]['path']
    if cross_track:
        folder, m = make_sequence(tmp_path, 'D')
    f = m['frames'][1 if not cross_track else 0]
    dest = folder / f['path']
    if reencode:
        with Image.open(source) as im:
            meta = PngImagePlugin.PngInfo()
            meta.add_text('fixture', 'synthetic duplicate pixels, different PNG bytes')
            im.save(dest, pnginfo=meta)
        assert sha256(source) != sha256(dest)
    else:
        dest.write_bytes(source.read_bytes())
    f['sha256'] = sha256(dest)
    f['preprocessing'].update(source_sha256=f['sha256'], output_sha256=f['sha256'])
    save_manifest(folder, m)
    with pytest.raises(ValidationError, match='duplicate'):
        validate_dataset(tmp_path, complete=False)


def test_one_character_and_directory_identity(tmp_path):
    make_sequence(tmp_path)
    folder, m = make_sequence(tmp_path, number=2)
    m['character_id'] = 'SYNTHETIC second character'
    save_manifest(folder, m)
    with pytest.raises(ValidationError, match='one recurring character'):
        validate_dataset(tmp_path, complete=False)
    folder.rename(folder.with_name('d02'))
    with pytest.raises(ValidationError, match='directory'):
        validate_dataset(tmp_path, complete=False)


@pytest.mark.parametrize('payload', ['{"a": 1, "a": 2}', '{"a": NaN}', '{"a": Infinity}', '{'])
def test_strict_json(tmp_path, payload):
    path = tmp_path / 'bad.json'
    path.write_text(payload)
    with pytest.raises(ValidationError):
        load_manifest(path)


def test_cli_is_read_only_and_requires_explicit_partial(tmp_path):
    make_sequence(tmp_path)
    def snapshot():
        return {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in tmp_path.rglob('*') if p.is_file()}
    before = snapshot()
    command = [sys.executable, '-m', 'inbetween.pilot_dataset', str(tmp_path)]
    partial = subprocess.run(command + ['--partial'], capture_output=True, text=True)
    assert partial.returncode == 0, partial.stderr
    assert json.loads(partial.stdout)['status'] == 'partial_ingest_only'
    complete = subprocess.run(command, capture_output=True, text=True)
    assert complete.returncode == 1
    assert 'Invalid pilot dataset' in complete.stderr
    assert snapshot() == before


@pytest.mark.parametrize('damage', ['transparency', 'animated', 'D_created_later', 'unexpected_root',
                                   'manifest_symlink', 'frames_symlink'])
def test_additional_ingest_guards(tmp_path, damage):
    root = tmp_path / 'dataset'
    folder, m = make_sequence(root)
    f = m['frames'][0]
    path = folder / f['path']
    if damage in ('transparency', 'animated'):
        with Image.open(path) as im:
            first = im.copy()
        if damage == 'transparency':
            first.save(path, transparency=(248, 246, 240))
        else:
            second = Image.new('RGB', (512, 512), (250, 250, 250))
            first.save(path, save_all=True, append_images=[second], duration=100)
        f['sha256'] = sha256(path)
        f['preprocessing'].update(source_sha256=f['sha256'], output_sha256=f['sha256'])
        save_manifest(folder, m)
    elif damage == 'D_created_later':
        m['frames'][3]['created_at'] = '2026-09-23T00:00:00Z'
        save_manifest(folder, m)
    elif damage == 'unexpected_root':
        (root / 'mixed_results').mkdir()
    elif damage == 'manifest_symlink':
        manifest = folder / 'manifest.json'
        outside = tmp_path / 'manifest.json'
        manifest.rename(outside)
        manifest.symlink_to(outside)
    else:
        frames = folder / 'frames'
        outside = tmp_path / 'frames'
        frames.rename(outside)
        frames.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValidationError):
        validate_dataset(root, complete=False)
