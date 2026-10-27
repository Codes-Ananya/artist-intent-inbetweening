#!/usr/bin/env python3
"""Read-only asset audit and prospective annotation pack; never runs inference."""
import argparse
import csv
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
from uuid import uuid4
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CASES=[('T01','d02',0,4,'arm/torso reach'),('T02','d03',0,3,'recoil with two arms and body lean'),('T03','d04',0,3,'body turn/self-occlusion stress case')]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(dataset):
    cases=[]
    for case,sequence,a,b,description in CASES:
        folder=dataset/'track_d'/sequence
        manifest=folder/'manifest.json';d=json.loads(manifest.read_text())
        entries={f['index']:f for f in d['frames']};inputs=[]
        for index in (a,b):
            e=entries[index];p=(folder/e['path']).resolve()
            if not p.is_relative_to(folder.resolve()):raise ValueError('Frame path escapes sequence')
            if sha(p)!=e['sha256']:raise ValueError(f'Input hash mismatch: {p}')
            with Image.open(p) as im:
                if im.size!=(512,512) or im.mode!='RGB':raise ValueError(f'Expected prepared RGB 512x512: {p}')
            inputs.append({'index':index,'path':str(p),'sha256':sha(p),'role':'supplied_endpoint'})
        cases.append(dict(case_id=case,sequence=sequence,description=description,inputs=inputs,
            manifest_path=str(manifest.resolve()),manifest_sha256=sha(manifest),
            source_files=d['provenance']['source_files'],character_id=d['character_id'],
            provenance='Previously reviewed AI-generated Track D inputs; exploratory reuse only',
            withheld_reference=None,unused_pose_note='frame 7 is outside selected interval, not an intermediate ground truth',
            held_out_status='Provisional transfer away from SFP development; source images already reviewed; not blind or independently sourced',
            annotation_minutes_limit=20,baseline={'backend':'RIFE','flow_scale':1.0,'device':'cuda:0','dtype':'float32','times':[0.5],'fallback':False},
            status='not_execution_ready',blockers=['Endpoint-only annotation session and hash-bound frozen config missing','Generic config-driven layered runner not implemented; SFP coordinate-specific runner must not be used'],
            additional_risk='Changing depth/torso orientation may require abstention' if case=='T03' else 'Multiple moving regions/appearance changes may exceed single-arm model'))
    return cases


def prepare(dataset,out):
    before={p:sha(p) for p in dataset.rglob('*') if p.is_file()}
    cases=audit(dataset)
    out.mkdir(parents=True,exist_ok=False)
    (out/'roster.json').write_text(json.dumps({'status':'preparation_only','cases':cases,'no_inference':True},indent=2)+'\n')
    for c in cases:
        annotation={'case_id':c['case_id'],'status':'unstarted','annotator':None,'inputs':c['inputs'],
            'started_at':None,'finished_at':None,'active_seconds':None,'baseline_or_reference_seen_before_freeze':None,
            'endpoint_arm_masks':[None,None],'endpoint_shoulder_elbow_wrist':[None,None],
            'depth_order_consistent':None,'roi':None,'frozen_at':None,'annotation_sha256':None,
            'outcome':None,'abstention_reason':None}
        (out/f"{c['case_id']}_annotation.json").write_text(json.dumps(annotation,indent=2)+'\n')
    with (out/'interventions.csv').open('w') as f:
        csv.writer(f).writerow(['case_id','operator','phase','started_at_utc','ended_at_utc','active_seconds','action','source_path','source_sha256','output_path','output_sha256','reason','output_seen','budget_exceeded'])
    with (out/'ratings.csv').open('w') as f:
        csv.writer(f).writerow(['case_id','reviewer','blind_condition','opacity_1_to_5','contour_1_to_5','anatomy_1_to_5','transition_1_to_5','new_artifacts','preference_or_tie','reference_seen','notes'])
    changed=[str(p) for p,h in before.items() if sha(p)!=h]
    if changed:raise RuntimeError(f'Source changed: {changed}')
    (out/'preparation.json').write_text(json.dumps({'created_at':datetime.now(timezone.utc).isoformat(),'source_files_checked':len(before),'changed':changed,'script_sha256':sha(Path(__file__))},indent=2)+'\n')
    return cases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=ROOT/'.local/real_input_pilot/dataset')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    out=args.output or ROOT/'.local/transfer_pilot'/('prepared-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid4().hex[:8])
    if out.resolve().is_relative_to((ROOT/'.local/real_input_pilot').resolve()):raise ValueError('Do not write into Track A/D source tree')
    prepare(args.dataset,out);print(out);print('Preparation only: no inference; three provisional cases, zero execution-ready cases.')

if __name__=='__main__':main()
