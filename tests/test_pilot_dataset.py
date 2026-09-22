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
    ValidationError, load_manifest, sha256, validate_dataset, validate_manifest,
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


@pytest.mark.parametrize('key,value', [('model', ''), ('prompt', ''), ('seed', True),
                                     ('seed_note', ''), ('usage_basis', ''), ('edits', None)])
def test_generation_disclosure_required_at_both_levels(tmp_path, key, value):
    _, m = make_sequence(tmp_path, 'D')
    for target in ('sequence', 'frame'):
        bad = copy.deepcopy(m)
        g = bad['ai_generation'] if target == 'sequence' else bad['frames'][0]['ai_generation']
        g[key] = value
        with pytest.raises(ValidationError):
            validate_manifest(bad)


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
