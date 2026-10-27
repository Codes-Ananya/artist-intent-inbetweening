"""One fixed two-piece refinement of the SFP-01 manual layer diagnostic."""
import cv2
import numpy as np
from PIL import Image
from .layered_pilot import LayeredPilotBackend, mask, ARM2, ROI


class RefinedLayeredBackend(LayeredPilotBackend):
    name='sfp01_manual_layer_refinement_cpu'
    version='1'

    def generate(self, first, last, intermediate_count):
        # Preserve original implementation and archive; reuse its documented plate procedure.
        super().generate(first,last,intermediate_count)
        a,b=np.array(first),np.array(last)
        plate=self.artifacts['reconstructed_plate'].copy()
        # Observed source shoulder anchor, not an inferred clean hidden vest patch.
        shoulder=np.zeros((512,512),np.uint8)
        cv2.ellipse(shoulder,(215,213),(15,19),0,0,360,255,-1)
        plate[shoulder>0]=b[shoulder>0]
        # Known background in endpoint 0 replaces residual mark from removal mask miss.
        cleanup=np.zeros_like(shoulder);cleanup[234:255,334:363]=255
        plate[cleanup>0]=a[cleanup>0]
        alpha=mask(ARM2).astype(np.float32)/255
        x=np.arange(512)[None,:]
        upper_weight=np.clip((256-x)/12,0,1).astype(np.float32)
        upper=alpha*upper_weight
        fore=alpha*(1-upper_weight)
        shoulder_pivot=(216,218);elbow=np.array([252.,240.])
        upper_matrix=cv2.getRotationMatrix2D(shoulder_pivot,-40,1.0)
        elbow_dest=upper_matrix@np.r_[elbow,1]
        fore_matrix=cv2.getRotationMatrix2D(tuple(elbow),-10,1.0)
        fore_matrix[:,2]+=elbow_dest-elbow
        def warp_layer(weights,matrix):
            wa=cv2.warpAffine(weights,matrix,(512,512),flags=cv2.INTER_LINEAR)
            rgb=cv2.warpAffine(b.astype(np.float32)*weights[:,:,None],matrix,(512,512),flags=cv2.INTER_LINEAR)
            return wa,rgb
        au,cu=warp_layer(upper,upper_matrix);af,cf=warp_layer(fore,fore_matrix)
        # Normalize overlap at elbow, preserving foreground opacity instead of fading twice.
        coverage=au+af
        union=np.clip(coverage,0,1)
        color=(cu+cf)/np.maximum(coverage[:,:,None],1e-6)
        composite=np.rint(np.clip(color*union[:,:,None]+plate*(1-union[:,:,None]),0,255)).astype(np.uint8)
        candidate=np.array(self.archived_midpoint).copy()
        x0,y0,x1,y1=ROI;candidate[y0:y1,x0:x1]=composite[y0:y1,x0:x1]
        unknown=(self.artifacts['unknown_reconstruction_mask']>0)&(shoulder==0)&(cleanup==0)
        exposed=unknown&(union<0.99)
        self.artifacts.update(shoulder_observed_restore_mask=shoulder,background_cleanup_mask=cleanup,
            upper_source_alpha=np.rint(upper*255).astype(np.uint8),forearm_source_alpha=np.rint(fore*255).astype(np.uint8),
            warped_upper_alpha=np.rint(au*255).astype(np.uint8),warped_forearm_alpha=np.rint(af*255).astype(np.uint8),
            refined_arm_alpha=np.rint(union*255).astype(np.uint8),refined_plate=plate,
            remaining_reconstruction_mask=unknown.astype(np.uint8)*255,
            refined_exposed_reconstruction_mask=exposed.astype(np.uint8)*255)
        original=self.last_run_metadata.copy()
        self.last_run_metadata=dict(device='cpu',opencv_version=cv2.__version__,
            original_plate_procedure=original,
            refinement='one fixed manual two-piece unscaled articulation; observed shoulder restoration and observed background cleanup',
            shoulder_restore={'source':'frame2','ellipse_center':[215,213],'radii':[15,19]},
            cleanup={'source':'frame0','rectangle':[334,234,363,255]},
            upper_rotation_degrees=-40,forearm_rotation_degrees=-10,segment_scales=[1.0,1.0],
            source_elbow=elbow.tolist(),target_elbow=elbow_dest.tolist(),shoulder_pivot=list(shoulder_pivot),
            upper_matrix=upper_matrix.tolist(),forearm_matrix=fore_matrix.tolist(),
            source_split='linear upper-to-forearm transition across x=244..256; approximate manual joint',
            overlap='normalized premultiplied colors; clipped sum alpha',
            remaining_reconstructed_pixels=int(unknown.sum()),exposed_reconstructed_pixels=int(exposed.sum()),
            roi=ROI,limitation='Manual joints/angles, approximate masks, unchanged estimated plate outside restorations; no ground truth or automatic intent preservation')
        return [first.copy(),Image.fromarray(candidate),last.copy()]
