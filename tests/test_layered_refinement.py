import numpy as np
from inbetween.layered_refinement import RefinedLayeredBackend
from inbetween.layered_pilot import ROI
from scripts.run_sfp01_frame1_scale import BASE
from scripts.run_sfp01_extra_breakdown import load_rgb


def test_refinement_preserves_endpoints_region_and_records_full_scale():
    frames=[load_rgb(BASE/'extra_breakdown'/f'frame_{i:04d}.png') for i in range(3)]
    originals=[np.array(f).copy() for f in frames]
    backend=RefinedLayeredBackend(frames[1]);result=backend.generate(frames[0],frames[2],1)
    assert np.array_equal(np.array(result[0]),originals[0])
    assert np.array_equal(np.array(result[2]),originals[2])
    for f,a in zip(frames,originals):assert np.array_equal(np.array(f),a)
    outside=np.ones((512,512),bool);x0,y0,x1,y1=ROI;outside[y0:y1,x0:x1]=False
    assert np.array_equal(np.array(result[1])[outside],originals[1][outside])
    for key in ['upper_matrix','forearm_matrix']:
        linear=np.array(backend.last_run_metadata[key])[:,:2]
        assert np.allclose(linear.T@linear,np.eye(2))
    shoulder=backend.artifacts['shoulder_observed_restore_mask']>0
    cleanup=backend.artifacts['background_cleanup_mask']>0
    plate=backend.artifacts['refined_plate']
    assert np.array_equal(plate[shoulder],originals[2][shoulder])
    assert np.array_equal(plate[cleanup],originals[0][cleanup])
    remaining=backend.artifacts['remaining_reconstruction_mask']>0
    assert not np.any(remaining&(shoulder|cleanup))
