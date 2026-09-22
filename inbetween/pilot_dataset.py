"""Read-only Milestone 7 ingest validation; no backend or metric execution.

The two JSON templates in docs/real_input_templates are the manifest contract.
Template placeholders deliberately fail validation. Only real ingest records
or explicitly labelled synthetic test records may pass.
"""
import argparse
from datetime import date, datetime, timedelta, timezone
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


def event_time(value, where):
    """Validate evidence precision; return possible UTC bounds, never invented times.

    Date-only bounds conservatively allow UTC offsets from -12 to +14 hours.
    They are comparison bounds only, never recorded as event timestamps.
    """
    fields(value, 'precision value reason source', where)
    text(value['source'], f'{where}.source')
    precision = value['precision']
    require(precision in ('exact', 'date_only', 'unavailable'), f'{where}: invalid precision')
    if precision == 'unavailable':
        require(value['value'] is None, f'{where}: unavailable value must be null')
        text(value['reason'], f'{where}.reason')
        return None
    require(value['reason'] is None, f'{where}: available event must not have unavailable reason')
    if precision == 'exact':
        moment = timestamp(value['value'], where)
        return moment, moment
    require(isinstance(value['value'], str) and
            re.fullmatch(r'\d{4}-\d{2}-\d{2}', value['value']), f'{where}: expected date only')
    try:
        day = date.fromisoformat(value['value'])
        start = datetime.combine(day, datetime.min.time(), timezone.utc)
        return start - timedelta(hours=14), start + timedelta(days=1, hours=12)
    except (ValueError, OverflowError) as exc:
        raise ValidationError(f'{where}: invalid date') from exc


def chronological(earlier, later, message):
    # Overlap or unavailable evidence does not prove ordering. The separate
    # pre-results attestation is mandatory for Track D regardless of precision.
    if earlier is not None and later is not None:
        require(earlier[0] <= later[1], message)


def check_recorded(event, recorded, where):
    moment = timestamp(recorded, f'{where}.recorded_at')
    chronological(event_time(event, where), (moment, moment),
                  f'{where}: event occurs after recording')


def disclosed_value(v, where, kind=str):
    fields(v, 'status value reason', where)
    require(v['status'] in ('available', 'unavailable'), f'{where}: invalid availability')
    if v['status'] == 'unavailable':
        require(v['value'] is None, f'{where}: unavailable value must be null')
        text(v['reason'], f'{where}.reason')
    else:
        require(v['reason'] is None, f'{where}: available value has unavailable reason')
        if kind is str:
            text(v['value'], where)
        else:
            require(type(v['value']) is kind, f'{where}: invalid value type')
            if kind is dict:
                require(bool(v['value']), f'{where}: empty settings')


def rights_v2(r):
    fields(r, 'authorities capacity organization usage_basis consent_status consent_basis '
           'confirmed_by confirmed_at recorded_at evidence_reference declaration_scope '
           'permitted_uses dataset_redistribution', 'rights')
    for key in ('authorities', 'confirmed_by', 'permitted_uses'):
        texts(r[key], f'rights.{key}', nonempty=True)
        require(len(set(r[key])) == len(r[key]), f'rights.{key}: duplicate entries')
    require(set(r['confirmed_by']) == set(r['authorities']), 'rights: authorities must confirm')
    for key in ('capacity', 'usage_basis', 'consent_basis', 'evidence_reference'):
        text(r[key], f'rights.{key}')
    if r['organization'] is not None:
        text(r['organization'], 'rights.organization')
    require(r['declaration_scope'] == 'project_usage_authority_not_ownership',
            'rights: declaration is project usage authority, not ownership')
    require(r['consent_status'] in ('confirmed', 'not_required'), 'rights: unresolved consent')
    require(set(r['permitted_uses']) >= {'academic_research', 'evaluation'},
            'rights: research and evaluation usage required')
    require(r['dataset_redistribution'] in ('not_authorized', 'authorized'),
            'rights: explicit dataset redistribution scope required')
    check_recorded(r['confirmed_at'], r['recorded_at'], 'rights')


def generation_v2(g):
    fields(g, 'provider interface model_identifier seed inference_settings prompt_provenance '
           'generated_at local_gpu_used generation_compute D_authorship human_role '
           'usage_basis', 'ai_generation')
    for key in ('provider', 'interface', 'usage_basis'):
        text(g[key], f'ai_generation.{key}')
    event_time(g['generated_at'], 'ai_generation.generated_at')
    for key, kind in (('model_identifier', str), ('seed', int), ('inference_settings', dict)):
        disclosed_value(g[key], f'ai_generation.{key}', kind)
    require(type(g['local_gpu_used']) is bool, 'local_gpu_used must be boolean')
    require(g['generation_compute'] in ('OpenAI-hosted', 'local', 'other_hosted'),
            'invalid generation compute')
    require(not g['local_gpu_used'] or g['generation_compute'] == 'local',
            'hosted generation contradicts local GPU use')
    if g['interface'] == 'ChatGPT image generation':
        require(g['provider'] == 'OpenAI' and g['generation_compute'] == 'OpenAI-hosted'
                and g['local_gpu_used'] is False, 'contradictory ChatGPT compute disclosure')
    require(g['D_authorship'] == 'AI-generated and researcher-selected, not independently human-drawn',
            'incorrect exploratory D authorship')
    texts(g['human_role'], 'ai_generation.human_role', nonempty=True)
    p = g['prompt_provenance']
    fields(p, 'conversation_instructions internal_expanded_prompt history_status history_note',
           'prompt_provenance')
    require(p['history_status'] in ('partial', 'complete'), 'prompt history status required')
    text(p['history_note'], 'prompt history note')
    instructions = p['conversation_instructions']
    require(isinstance(instructions, list) and bool(instructions), 'conversation instructions required')
    for item in instructions:
        fields(item, 'kind text source scope', 'conversation instruction')
        require(item['kind'] in ('researcher_instruction', 'researcher_approval',
                                'researcher_approval_summary'), 'incorrect prompt source kind')
        for key in ('text', 'source', 'scope'):
            text(item[key], f'conversation instruction.{key}')
        require(item['text'] != 'pending_transcription_from_conversation',
                'pending marker is not conversation evidence')
    disclosed_value(p['internal_expanded_prompt'], 'internal_expanded_prompt')
    if p['internal_expanded_prompt']['status'] == 'available':
        require(p['internal_expanded_prompt']['value'] not in [i['text'] for i in instructions],
                'conversation instruction cannot substitute for internal prompt')


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
    require(type(m['version']) is int and m['version'] in (1, 2), "version must be 1 or 2")
    v2 = m['version'] == 2
    require(not v2 or m['track'] == 'D', "version 2 is exploratory Track D only")
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
    fields(p, "creator created_at method tools authorship_status source_files" +
           (" recorded_at" if v2 else ""), "provenance")
    for key in ('creator', 'authorship_status'):
        text(p[key], f"provenance.{key}")
    event = event_time if v2 else timestamp
    created = event(p['created_at'], 'provenance.created_at')
    if v2:
        timestamp(p['recorded_at'], 'provenance.recorded_at')
        check_recorded(p['created_at'], p['recorded_at'], 'provenance')
    require(p['method'] == ('rig_assisted_manual_cleanup' if primary else 'ai_generated'),
            "track/provenance method mismatch")
    texts(p['tools'], 'provenance.tools', nonempty=True)
    texts(p['source_files'], 'provenance.source_files', nonempty=True)

    r = m['rights']
    if v2:
        rights_v2(r)
    else:
        fields(r, "holder usage_basis consent_status consent_basis confirmed_by confirmed_at", "rights")
        for key in ('holder', 'usage_basis', 'consent_basis', 'confirmed_by'):
            text(r[key], f"rights.{key}")
        require(r['consent_status'] in ('confirmed', 'not_required'), "rights: unresolved consent")
        timestamp(r['confirmed_at'], 'rights.confirmed_at')

    g = m['ai_generation']
    if primary:
        require(g is None, "primary track cannot contain AI generation")
    else:
        generation_v2(g) if v2 else generation_record(g)
        if v2:
            require(g['generated_at'] == p['created_at'], "generation/creation event mismatch")
            require(g['usage_basis'] == r['usage_basis'], "generation/rights usage mismatch")

    s = m['selection']
    fields(s, "kind k D_path D_sha256 selected_by selected_at before_model_results rationale" +
           (" recorded_at before_model_results_basis" if v2 else ""), "selection")
    require(s['kind'] == ('artist' if primary else 'exploratory_curator'), "selection kind mismatch")
    require(type(s['k']) is int and 1 <= s['k'] <= 6, "k must be integer 1..6")
    for key in ('selected_by', 'rationale'):
        text(s[key], f"selection.{key}")
    selected = event(s['selected_at'], 'selection.selected_at')
    if v2:
        text(s['before_model_results_basis'], 'selection.before_model_results_basis')
        check_recorded(s['selected_at'], s['recorded_at'], 'selection')
        chronological(created, selected, "selection precedes sequence creation")
    else:
        require(selected >= created, "selection precedes sequence creation")
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
        event(f['created_at'], 'frame.created_at')
        require(f['method'] == p['method'], "frame method differs from track")
        texts(f['edits'], 'frame.edits')
        if primary:
            require(f['ai_generation'] is None, "primary frame cannot contain AI generation")
        else:
            generation_v2(f['ai_generation']) if v2 else generation_record(f['ai_generation'])
            if v2:
                require(f['ai_generation'] == g, 'frame/sequence generation disclosure mismatch')
                require(f['created_at'] == p['created_at'], 'frame/source creation mismatch')
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
    if v2:
        chronological(event(d['created_at'], 'D.created_at'), selected,
                      "selection precedes D creation")
    else:
        require(selected >= timestamp(d['created_at'], 'D.created_at'),
                "selection precedes D creation")


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
