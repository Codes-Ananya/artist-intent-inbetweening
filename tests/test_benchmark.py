from pathlib import Path
import csv
import json
import os
import subprocess
import sys
import runpy
import time
import numpy as np
import pytest
from PIL import Image
from inbetween.benchmark_cases import CATEGORIES, make_case
from inbetween.benchmark_metrics import metrics, endpoint_equal, trajectory_error
from inbetween.benchmark import run_benchmark, BACKENDS
from inbetween.comparison import compare
from inbetween.core import CrossfadeBackend
from inbetween import benchmark as benchmark_module


def test_cases_deterministic_and_complete():
    assert len(CATEGORIES)==10
    for category in CATEGORIES:
        a=make_case(category,2);b=make_case(category,2)
        assert len(a.frames)==4 and a.metadata['ground_truth_frame_count']==4
        assert a.metadata['timestamps']==[0,1/3,2/3,1]
        assert all(np.array_equal(np.asarray(x),np.asarray(y)) for x,y in zip(a.frames,b.frames))
        assert endpoint_equal(a.frames[0],b.frames[0]) and endpoint_equal(a.frames[-1],b.frames[-1])


def test_metric_behavior_and_tolerance():
    a=Image.new('RGB',(64,64),'white'); arr=np.asarray(a).copy();arr[20:40,30:33]=0;a=Image.fromarray(arr)
    shifted=Image.fromarray(np.roll(arr,1,axis=1));wrong=Image.new('RGB',(64,64),'white')
    same=metrics(a,a);near=metrics(a,shifted);bad=metrics(a,wrong)
    assert same['psnr_db']==float('inf') and same['edge_f1']==1 and same['chamfer_px']==0
    assert near['psnr_db']<same['psnr_db'] and near['edge_f1']==1 and near['chamfer_px']>0
    assert bad['edge_f1']==0 and bad['psnr_db']<near['psnr_db']
    assert trajectory_error([(0,0),(1,1)],[(3,4),(1,1)])==2.5


def test_failure_isolation_and_reports(tmp_path,monkeypatch):
    class Failing:
        name='failing'
        def generate(self,*args): raise RuntimeError('intentional failure')
    monkeypatch.setitem(BACKENDS,'rife',Failing)
    records=run_benchmark(tmp_path,['small_translation'],['rife','crossfade'],2)
    assert [r['status'] for r in records]==['failed','ok']
    assert (tmp_path/'frames.csv').exists() and (tmp_path/'results.json').exists() and (tmp_path/'summary.md').exists()
    assert (tmp_path/'visuals/small_translation/crossfade/contact_sheet.png').exists()
    assert (tmp_path/'visuals/small_translation/crossfade/comparison.gif').exists()


def test_comparison_keeps_backend_failures_separate(tmp_path):
    class Failing:
        name='rife_local_ai'
        def generate(self,*args): raise RuntimeError('RIFE failed')
    case=make_case('small_translation',1)
    a=tmp_path/'a.png';b=tmp_path/'b.png';case.frames[0].save(a);case.frames[-1].save(b)
    result=compare(a,b,1,output=tmp_path/'compare',backend_factories={'crossfade':CrossfadeBackend,'rife':Failing})
    assert result['crossfade']['status']=='ok'
    assert result['rife']['status']=='failed' and 'RIFE failed' in result['rife']['error']
    assert result['crossfade']['manifest']['backend']=='deterministic_crossfade'


def test_cli_entrypoints(tmp_path, monkeypatch):
    root=Path(__file__).resolve().parents[1]
    env={k:v for k,v in os.environ.items() if k!='PYTHONPATH'}
    help_result=subprocess.run([sys.executable,'-m','inbetween.benchmark','--help'],cwd=root,env=env,capture_output=True,text=True)
    assert help_result.returncode==0 and '--quick' in help_result.stdout
    calls=[]
    monkeypatch.setattr(benchmark_module,'run_benchmark',lambda *args: calls.append(args) or [{'case_id':'synthetic','status':'ok'}])
    with pytest.raises(SystemExit) as result:
        runpy.run_path(str(root/'scripts/benchmark_smoke_test.py'),run_name='__main__')
    assert result.value.code == 0
    assert len(calls) == 1


@pytest.mark.parametrize('missing',[(1,),(1,2)])
def test_trajectory_missing_serialization_and_summary(tmp_path,monkeypatch,missing):
    calls=iter(range(1,3))
    original=benchmark_module._landmark
    def landmark(image):
        return None if next(calls) in missing else original(image)
    monkeypatch.setattr(benchmark_module,'_landmark',landmark)
    records=run_benchmark(tmp_path,['small_translation'],['crossfade'],2)
    record=records[0]
    assert record['status']=='ok'
    assert record['trajectory_measured_frames']==2-len(missing)
    assert record['trajectory_missing_frames']==len(missing)
    assert (record['means']['trajectory_error_px'] is None)==(len(missing)==2)
    raw=(tmp_path/'results.json').read_text()
    assert not any(s in raw for s in ('NaN','Infinity','-Infinity'))
    parsed=json.loads(raw,parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    assert [f['trajectory_error_px'] is None for f in parsed['frames']]==[i in missing for i in (1,2)]
    with (tmp_path/'frames.csv').open() as stream:
        csv_rows=list(csv.DictReader(stream))
    assert [row['trajectory_error_px']=='' for row in csv_rows]==[i in missing for i in (1,2)]
    summary=(tmp_path/'summary.md').read_text()
    assert 'Trajectory error px' in summary and f'{2-len(missing)}/2' in summary
    assert (summary.splitlines()[-1].split('|')[8].strip()=='—')==(len(missing)==2)


def test_ground_truth_numeric_order_and_rejection(tmp_path):
    first=tmp_path/'frame_1.png';middle=tmp_path/'frame_2.png';last=tmp_path/'frame_10.png'
    for path,color in ((first,'black'),(middle,'gray'),(last,'white')):
        Image.new('RGB',(8,8),color).save(path)
    class Failing:
        name='rife_local_ai'
        def generate(self,*args): raise RuntimeError('expected')
    factories={'crossfade':CrossfadeBackend,'rife':Failing}
    result=compare(first,last,1,ground_truth=[last,first,middle],output=tmp_path/'ok',backend_factories=factories)
    assert result['crossfade']['status']=='ok' and result['crossfade']['metrics']['psnr_db']>0
    for sequence in ([first,middle], [first,middle,middle], [first,tmp_path/'other.png',last]):
        with pytest.raises(ValueError,match='Ground truth'):
            compare(first,last,1,ground_truth=sequence,output=tmp_path/'bad',backend_factories=factories)
    with pytest.raises(ValueError,match='endpoints differ'):
        compare(last,first,1,ground_truth=[last,first,middle],output=tmp_path/'bad-endpoints',backend_factories=factories)


def test_backend_wall_time_is_not_inference_time(tmp_path):
    first=tmp_path/'first.png';last=tmp_path/'last.png'
    Image.new('RGB',(8,8),'black').save(first)
    Image.new('RGB',(8,8),'white').save(last)
    class Timed(CrossfadeBackend):
        def generate(self,*args):
            frames=super().generate(*args)
            self.last_run_metadata={'inference_seconds':0.001}
            time.sleep(0.01)
            return frames
    from inbetween.run import create_run
    manifest=create_run(first,last,1,output_root=tmp_path/'runs',backend=Timed())
    assert manifest['backend_wall_seconds']>manifest['inference_seconds']
