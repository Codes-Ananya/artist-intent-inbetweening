import numpy as np
import pytest
from PIL import Image
from inbetween.core import ValidationError
from inbetween.layered_pilot import LayeredPilotBackend,ROI
from scripts.run_sfp01_frame1_scale import BASE
from scripts.run_sfp01_extra_breakdown import load_rgb


def test_layered_preserves_endpoints_and_outside_roi_and_records_unknowns():
    frames=[load_rgb(BASE/'extra_breakdown'/f'frame_{i:04d}.png') for i in range(3)]
    before=[np.array(f).copy() for f in frames]
    backend=LayeredPilotBackend(frames[1]);out=backend.generate(frames[0],frames[2],1)
    for original,image in zip(before,frames):assert np.array_equal(original,np.array(image))
    assert np.array_equal(np.array(out[0]),before[0])
    assert np.array_equal(np.array(out[2]),before[2])
    x0,y0,x1,y1=ROI;outside=np.ones((512,512),bool);outside[y0:y1,x0:x1]=False
    assert np.array_equal(np.array(out[1])[outside],before[1][outside])
    assert not np.array_equal(np.array(out[1]),before[1])
    assert backend.last_run_metadata['unknown_pixels']>0
    unknown=backend.artifacts['unknown_reconstruction_mask']>0
    observed=backend.artifacts['observed_endpoint0_fill_mask']>0
    removal=backend.artifacts['arm2_removal_mask']>0
    assert not np.any(unknown&observed)
    assert np.array_equal(unknown|observed,removal)
    assert np.array_equal(backend.artifacts['reconstructed_plate'][~removal],before[2][~removal])
    assert np.array_equal(np.array(backend.generate(frames[0],frames[2],1)[1]),np.array(out[1]))


def test_layered_refuses_other_sizes_and_counts():
    image=Image.new('RGB',(512,512));backend=LayeredPilotBackend(image)
    with pytest.raises(ValidationError):backend.generate(image,image,2)
    with pytest.raises(ValidationError):backend.generate(image.resize((256,256)),image,1)
