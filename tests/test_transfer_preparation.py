import json
import pytest
from scripts.prepare_transfer_pilot import prepare,audit,ROOT


def test_read_only_prepare_labels_roles_and_missing_references(tmp_path):
    source=ROOT/'.local/real_input_pilot/dataset'
    out=tmp_path/'pack'
    cases=prepare(source,out)
    assert len(cases)==3
    assert all(c['status']=='not_execution_ready' for c in cases)
    assert all(c['withheld_reference'] is None for c in cases)
    assert all(all(e['role']=='supplied_endpoint' for e in c['inputs']) for c in cases)
    assert json.loads((out/'preparation.json').read_text())['changed']==[]
    assert (out/'interventions.csv').exists()
    with pytest.raises(FileExistsError):prepare(source,out)


def test_hash_mismatch_rejected(tmp_path):
    source=ROOT/'.local/real_input_pilot/dataset/track_d/d02/manifest.json'
    d=json.loads(source.read_text());folder=tmp_path/'track_d/d02';folder.mkdir(parents=True)
    for e in d['frames']:
        p=folder/e['path'];p.parent.mkdir(exist_ok=True);p.write_bytes(b'not approved bytes')
    (folder/'manifest.json').write_text(json.dumps(d))
    with pytest.raises(ValueError,match='hash mismatch'):audit(tmp_path)
