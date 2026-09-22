"""Read-only Milestone 7 ingest validation; no backend or metric execution.

The two JSON templates in docs/real_input_templates are the manifest contract.
Template placeholders deliberately fail validation. Only real ingest records
or explicitly labelled synthetic test records may pass.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

from PIL import Image


class ValidationError(ValueError):
    """An incomplete or inconsistent pilot dataset."""


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def fields(value, names, where):
    require(isinstance(value, dict), f"{where}: expected object")
    require(set(value) == set(names.split()), f"{where}: expected fields {names}")


def text(value, where):
    require(isinstance(value, str) and bool(value.strip()), f"{where}: required text")
    require(not value.startswith("REPLACE_"), f"{where}: template placeholder")


def texts(value, where, nonempty=False):
    require(isinstance(value, list), f"{where}: expected list")
    require(not nonempty or bool(value), f"{where}: empty list")
    for item in value:
        text(item, where)


def timestamp(value, where):
    text(value, where)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(parsed.utcoffset() is not None, f"{where}: timezone required")
    except ValueError as exc:
        raise ValidationError(f"{where}: invalid timestamp") from exc
    return parsed


def digest(value, where):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value),
            f"{where}: expected lowercase SHA-256")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def generation_record(g):
    fields(g, "model model_version prompt generated_at seed seed_note edits "
           "authorship_status usage_basis", "ai_generation")
    for key in ('model', 'model_version', 'prompt', 'seed_note', 'authorship_status', 'usage_basis'):
        text(g[key], f"ai_generation.{key}")
    timestamp(g['generated_at'], 'ai_generation.generated_at')
    require(g['seed'] is None or type(g['seed']) is int, "generation seed must be integer or null")
    texts(g['edits'], 'ai_generation.edits')


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_manifest(path):
    def invalid_constant(value):
        raise ValidationError(f"nonfinite JSON constant: {value}")
    try:
        return json.loads(Path(path).read_text(), object_pairs_hook=_unique_keys,
                          parse_constant=invalid_constant)
    except (OSError, ValueError) as exc:
        raise ValidationError(f"{path}: {exc}") from exc


def validate_manifest(m):
    """Validate all six provenance sections without reading image files."""
    fields(m, "version track sequence_id purpose character_id motion provenance rights "
           "ai_generation selection frames", "manifest")
    require(type(m['version']) is int and m['version'] == 1, "version must be 1")
    require(m['track'] in ('A', 'D'), "track must be A or D")
    primary = m['track'] == 'A'
    ids = [f"a{i:02d}" for i in range(1, 7)] if primary else [f"d{i:02d}" for i in range(1, 5)]
    require(m['sequence_id'] in ids, "sequence_id outside frozen track roster")
    require(m['purpose'] == ('primary_evaluation' if primary else 'exploratory_only'),
            "track/purpose mismatch")
    for key in ('character_id', 'motion'):
        text(m[key], key)
    if not primary:
        motions = {'d01': 'curved_jump', 'd02': 'hold_then_fast_reach',
                   'd03': 'exaggerated_recoil', 'd04': 'body_turn_self_occlusion'}
        require(m['motion'] == motions[m['sequence_id']], "incorrect exploratory motion")

    p = m['provenance']
    fields(p, "creator created_at method tools authorship_status source_files", "provenance")
    for key in ('creator', 'authorship_status'):
        text(p[key], f"provenance.{key}")
    created = timestamp(p['created_at'], 'provenance.created_at')
    require(p['method'] == ('rig_assisted_manual_cleanup' if primary else 'ai_generated'),
            "track/provenance method mismatch")
    texts(p['tools'], 'provenance.tools', nonempty=True)
    texts(p['source_files'], 'provenance.source_files', nonempty=True)

    r = m['rights']
    fields(r, "holder usage_basis consent_status consent_basis confirmed_by confirmed_at", "rights")
    for key in ('holder', 'usage_basis', 'consent_basis', 'confirmed_by'):
        text(r[key], f"rights.{key}")
    require(r['consent_status'] in ('confirmed', 'not_required'), "rights: unresolved consent")
    timestamp(r['confirmed_at'], 'rights.confirmed_at')

    g = m['ai_generation']
    if primary:
        require(g is None, "primary track cannot contain AI generation")
    else:
        generation_record(g)

    s = m['selection']
    fields(s, "kind k D_path D_sha256 selected_by selected_at before_model_results rationale", "selection")
    require(s['kind'] == ('artist' if primary else 'exploratory_curator'), "selection kind mismatch")
    require(type(s['k']) is int and 1 <= s['k'] <= 6, "k must be integer 1..6")
    for key in ('selected_by', 'rationale'):
        text(s[key], f"selection.{key}")
    require(timestamp(s['selected_at'], 'selection.selected_at') >= created,
            "selection precedes sequence creation")
    require(s['before_model_results'] is True, "selection must precede model results")
    digest(s['D_sha256'], 'selection.D_sha256')

    frames = m['frames']
    require(isinstance(frames, list), "frames must be a list")
    expected = list(range(8)) if primary else [0, s['k'], 7]
    require(len(frames) == len(expected), "wrong required frame count")
    for f, index in zip(frames, expected):
        fields(f, "index path sha256 creator created_at method edits ai_generation preprocessing", "frame")
        require(type(f['index']) is int and f['index'] == index, "required frame indices/order mismatch")
        require(f['path'] == f"frames/frame_{index:03d}.png", "noncanonical frame path")
        digest(f['sha256'], 'frame.sha256')
        text(f['creator'], 'frame.creator')
        timestamp(f['created_at'], 'frame.created_at')
        require(f['method'] == p['method'], "frame method differs from track")
        texts(f['edits'], 'frame.edits')
        if primary:
            require(f['ai_generation'] is None, "primary frame cannot contain AI generation")
        else:
            generation_record(f['ai_generation'])
        pre = f['preprocessing']
        fields(pre, "source_path source_sha256 output_sha256 operations original_preserved "
               "recorded_by recorded_at", "preprocessing")
        for key in ('source_path', 'recorded_by'):
            text(pre[key], f"preprocessing.{key}")
        for key in ('source_sha256', 'output_sha256'):
            digest(pre[key], f"preprocessing.{key}")
        texts(pre['operations'], 'preprocessing.operations')
        require(pre['original_preserved'] is True, "original source must be preserved")
        require(pre['output_sha256'] == f['sha256'], "preprocessing output hash mismatch")
        if not pre['operations']:
            require(pre['source_sha256'] == f['sha256'], "changed input requires preprocessing record")
        timestamp(pre['recorded_at'], 'preprocessing.recorded_at')
    d = next(f for f in frames if f['index'] == s['k'])
    require(s['D_path'] == d['path'] and s['D_sha256'] == d['sha256'],
            "D must reference exactly frame k and its hash")
    require(timestamp(s['selected_at'], 'selection.selected_at') >=
            timestamp(d['created_at'], 'D.created_at'), "selection precedes D creation")


def validate_dataset(root, *, complete=True):
    """Validate canonical RGB PNGs; reject duplicates within/across tracks.

    Partial mode is for ingest only and never certifies a complete pilot.
    Source archive paths are provenance references, not paths opened by this CLI.
    """
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), "dataset root missing or symlinked")
    allowed = {'track_a', 'track_d'}
    require({p.name for p in root.iterdir()} <= allowed, "unexpected dataset root entries")
    seen_bytes, seen_pixels, characters, ids = {}, {}, set(), set()
    for track, folder in (('A', 'track_a'), ('D', 'track_d')):
        directory = root / folder
        if not directory.exists():
            require(not complete, f"missing {folder}")
            continue
        require(directory.is_dir() and not directory.is_symlink(), "invalid track directory")
        for sequence in sorted(directory.iterdir()):
            require(sequence.is_dir() and not sequence.is_symlink(), "invalid sequence directory")
            require({p.name for p in sequence.iterdir()} == {'manifest.json', 'frames'},
                    f"{sequence}: expected only manifest.json and frames")
            require(not (sequence / 'manifest.json').is_symlink(), "manifest symlink forbidden")
            m = load_manifest(sequence / 'manifest.json')
            validate_manifest(m)
            require(m['track'] == track and m['sequence_id'] == sequence.name,
                    "manifest/directory track or ID mismatch")
            ids.add(m['sequence_id'])
            if track == 'A':
                characters.add(m['character_id'])
            frame_dir = sequence / 'frames'
            require(frame_dir.is_dir() and not frame_dir.is_symlink(), "invalid frames directory")
            require({p.name for p in frame_dir.iterdir()} == {Path(f['path']).name for f in m['frames']},
                    "missing or unexpected frame files")
            for f in m['frames']:
                path = sequence / f['path']
                require(path.is_file() and not path.is_symlink(), f"invalid image file: {path}")
                actual = sha256(path)
                require(actual == f['sha256'], f"file hash mismatch: {path}")
                require(actual not in seen_bytes, f"duplicate file: {path} and {seen_bytes.get(actual)}")
                seen_bytes[actual] = str(path)
                try:
                    with Image.open(path) as im:
                        require(im.format == 'PNG' and im.size == (512, 512) and im.mode == 'RGB',
                                f"expected 512x512 RGB PNG: {path}")
                        require('transparency' not in im.info, f"transparent PNG forbidden: {path}")
                        require(getattr(im, 'n_frames', 1) == 1, f"animated PNG forbidden: {path}")
                        pixels = hashlib.sha256(im.tobytes()).hexdigest()
                except (OSError, ValueError) as exc:
                    raise ValidationError(f"{path}: {exc}") from exc
                require(pixels not in seen_pixels, f"duplicate pixels: {path} and {seen_pixels.get(pixels)}")
                seen_pixels[pixels] = str(path)
    require(bool(ids), "no sequences supplied")
    require(len(characters) <= 1, "Track A requires one recurring character")
    if complete:
        expected_ids = {f'a{i:02d}' for i in range(1, 7)} | {f'd{i:02d}' for i in range(1, 5)}
        require(ids == expected_ids, "complete pilot requires six A sequences and four D triplets")
    return {'status': 'complete_ingest' if complete else 'partial_ingest_only',
            'sequences': sorted(ids), 'frame_count': len(seen_bytes),
            'primary_sequences': sorted(i for i in ids if i.startswith('a')),
            'exploratory_sequences': sorted(i for i in ids if i.startswith('d'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--partial', action='store_true', help='ingest only; never evaluation readiness')
    args = parser.parse_args()
    try:
        print(json.dumps(validate_dataset(args.root, complete=not args.partial), indent=2))
    except (ValidationError, OSError) as exc:
        parser.exit(1, f"Invalid pilot dataset: {exc}\n")


if __name__ == '__main__':
    main()
