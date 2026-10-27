import json
from types import SimpleNamespace
import pytest
from PIL import Image
from inbetween.core import InterpolationBackend, ValidationError
from inbetween.rife import RifeBackend, RifeError
from scripts import run_sfp01_frame1_scale as runner


def test_scale_dispatch_preserves_default():
    calls=[]
    model=SimpleNamespace(inference=lambda *args,**kwargs:calls.append(kwargs))
    for scale in [1.0,0.5]:
        RifeBackend(flow_scale=scale)._model_inference(model,None,None,0.5)
    assert calls==[{'timestep':0.5},{'timestep':0.5,'scale':0.5}]
    with pytest.raises(ValidationError):RifeBackend(flow_scale=0)


class Fake(InterpolationBackend):
    name='TEST ONLY'
    version='test'
    def __init__(self,**kwargs):
        assert kwargs['flow_scale']==0.5
        self.last_run_metadata={'TEST_ONLY':True}
    def _require_assets_and_cuda(self):
        return SimpleNamespace(cuda=SimpleNamespace(mem_get_info=lambda _:(1,2),get_device_properties=lambda _:SimpleNamespace(name='TEST ONLY'))),None
    def generate(self,a,b,count):
        assert count==1
        return [a.copy(),Image.blend(a,b,.5),b.copy()]


def test_sample_export_only_frame1_changes(tmp_path,monkeypatch):
    monkeypatch.setattr(runner,'RifeBackend',Fake)
    out=tmp_path/'export'
    assert runner.main(['--output',str(out)])==0
    r=json.loads((out/'results.json').read_text())
    assert r['baseline_and_inputs_unchanged']
    assert len(r['unchanged_saved_frames'])==7 and all(r['unchanged_saved_frames'].values())
    assert (out/'side_by_side/animation.mp4').exists()
    assert (out/'frames_0_1_2.png').exists()
    with pytest.raises(FileExistsError):runner.main(['--output',str(out)])


def test_cuda_failure_is_archived_without_fallback(tmp_path,monkeypatch):
    class Unavailable(Fake):
        def _require_assets_and_cuda(self):raise RifeError('CUDA unavailable TEST ONLY')
        def generate(self,*args):pytest.fail('Inference must not run')
    monkeypatch.setattr(runner,'RifeBackend',Unavailable)
    out=tmp_path/'failure'
    assert runner.main(['--output',str(out)])==1
    r=json.loads((out/'results.json').read_text())
    assert r['status']=='failed' and 'CUDA unavailable' in r['error']
    assert r['baseline_and_inputs_unchanged']
    assert not (out/'candidate').exists()
