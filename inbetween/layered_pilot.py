"""Fixed SFP-01 CPU compositing diagnostic, not a general pose interpolator."""
import cv2
import numpy as np
from PIL import Image
from .core import InterpolationBackend, ValidationError

# Manually traced from 512x512 approved poses; assistant annotations, not artist masks.
ARM2 = [(210,203),(218,201),(230,207),(243,219),(252,229),(273,228),
        (304,222),(329,205),(343,199),(349,202),(350,207),(344,212),
        (354,212),(361,216),(361,221),(354,226),(345,226),(354,232),
        (356,238),(351,242),(341,239),(334,235),(336,243),(332,248),
        (324,247),(310,241),(285,248),(258,253),(245,251),(225,242),
        (215,235),(208,225),(207,214)]
ARM0 = [(207,199),(219,202),(226,213),(224,226),(214,241),(232,244),
        (245,253),(248,265),(244,277),(238,289),(226,288),(218,279),
        (199,275),(180,269),(168,260),(166,249),(178,229),(193,208)]
ROI = (160,190,370,295)


def mask(points):
    out=np.zeros((512,512),np.uint8)
    cv2.fillPoly(out,[np.asarray(points,np.int32)],255)
    return out


class LayeredPilotBackend(InterpolationBackend):
    name='sfp01_manual_layer_cpu_diagnostic'
    version='1'
    def __init__(self, archived_midpoint):
        self.archived_midpoint=archived_midpoint.copy()
        self.artifacts={}
        self.last_run_metadata={}

    def generate(self, first, last, intermediate_count):
        if intermediate_count!=1 or any(im.mode!='RGB' or im.size!=(512,512) for im in [first,last,self.archived_midpoint]):
            raise ValidationError('Layered pilot requires one midpoint and 512x512 RGB images')
        a,b=np.array(first),np.array(last)
        m0,m2=mask(ARM0),mask(ARM2)
        kernel=np.ones((5,5),np.uint8)
        removal=cv2.dilate(m2,kernel)
        unsafe0=cv2.dilate(m0,kernel)
        observed=(removal>0)&(unsafe0==0)
        unknown=((removal>0)&(unsafe0>0)).astype(np.uint8)*255
        plate=b.copy()
        plate[observed]=a[observed]
        # This is estimated artwork, never claimed as known hidden torso pixels.
        plate=cv2.inpaint(plate,unknown,3,cv2.INPAINT_TELEA)
        # Fixed diagnostic pose: no inferred joints or motion field.
        transform=cv2.getRotationMatrix2D((216,218),-15,0.75)
        alpha=m2.astype(np.float32)/255
        premult=b.astype(np.float32)*alpha[:,:,None]
        warped_alpha=cv2.warpAffine(alpha,transform,(512,512),flags=cv2.INTER_LINEAR)
        warped=cv2.warpAffine(premult,transform,(512,512),flags=cv2.INTER_LINEAR)
        composite=np.clip(np.rint(warped+plate*(1-warped_alpha[:,:,None])),0,255).astype(np.uint8)
        candidate=np.array(self.archived_midpoint).copy()
        x0,y0,x1,y1=ROI
        candidate[y0:y1,x0:x1]=composite[y0:y1,x0:x1]
        roi=np.zeros_like(m0);roi[y0:y1,x0:x1]=255
        exposed=((unknown>0)&(warped_alpha<0.99)&(roi>0)).astype(np.uint8)*255
        self.artifacts={
            'arm0_mask':m0,'arm2_mask':m2,'arm2_removal_mask':removal,
            'observed_endpoint0_fill_mask':observed.astype(np.uint8)*255,
            'unknown_reconstruction_mask':unknown,'exposed_reconstruction_mask':exposed,
            'roi_mask':roi,'warped_arm_alpha':np.rint(warped_alpha*255).astype(np.uint8),
            'reconstructed_plate':plate,
            'arm2_cutout':np.dstack([b,m2]),
        }
        self.last_run_metadata=dict(device='cpu',opencv_version=cv2.__version__,
            arm0_polygon=ARM0,arm2_polygon=ARM2,roi=ROI,
            mask_author='assistant manual image-coordinate annotation; not artist approved',
            reconstruction='frame2 plate; replace removed arm with visible frame0 pixels outside dilated arm0; Telea for remaining overlap',
            dilation_kernel=[5,5],inpaint_radius=3,inpaint_method='INPAINT_TELEA',
            unknown_pixels=int(np.count_nonzero(unknown)),exposed_unknown_pixels=int(np.count_nonzero(exposed)),
            observed_fill_pixels=int(np.count_nonzero(observed)),
            affine_matrix=transform.tolist(),rotation_degrees=-15,scale=0.75,pivot=[216,218],
            compositing='premultiplied RGB and alpha warped with bilinear sampling; opaque over plate; hard fixed ROI over archived midpoint',
            limitation='Manual rigid scaled arm placement, not articulated midpoint estimation; plate includes unverified reconstruction and endpoint appearance mismatch')
        return [first.copy(),Image.fromarray(candidate),last.copy()]
