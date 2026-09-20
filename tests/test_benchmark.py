from pathlib import Path
import numpy as np
from PIL import Image
from inbetween.benchmark_cases import CATEGORIES, make_case
from inbetween.benchmark_metrics import metrics, endpoint_equal, trajectory_error
from inbetween.benchmark import run_benchmark, BACKENDS
from inbetween.comparison import compare
from inbetween.core import CrossfadeBackend


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
