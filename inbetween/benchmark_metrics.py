"""Fixed synthetic benchmark metrics. See docs/METRICS.md."""
import math
import cv2
import numpy as np
from PIL import Image


def gray(image):
    return cv2.cvtColor(np.asarray(image.convert('RGB')),cv2.COLOR_RGB2GRAY)


def edges(image):
    return cv2.Canny(gray(image), 100, 200) > 0


def _distance(mask):
    # Precise Euclidean distance transform, zero at edges.
    return cv2.distanceTransform((~mask).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)


def metrics(reference: Image.Image, candidate: Image.Image, tolerance=2):
    if reference.size != candidate.size:
        raise ValueError('Frame dimensions differ')
    a=gray(reference).astype(np.float64)
    b=gray(candidate).astype(np.float64)
    mse=float(np.mean((a-b)**2))
    psnr=float('inf') if mse==0 else 10*math.log10(255**2/mse)
    af=a.astype(np.float32); bf=b.astype(np.float32)
    mu_a=cv2.GaussianBlur(af,(11,11),1.5); mu_b=cv2.GaussianBlur(bf,(11,11),1.5)
    va=cv2.GaussianBlur(af*af,(11,11),1.5)-mu_a**2
    vb=cv2.GaussianBlur(bf*bf,(11,11),1.5)-mu_b**2
    cov=cv2.GaussianBlur(af*bf,(11,11),1.5)-mu_a*mu_b
    ssim=float(np.mean(((2*mu_a*mu_b+6.5025)*(2*cov+58.5225))/((mu_a**2+mu_b**2+6.5025)*(va+vb+58.5225))))
    ea,eb=edges(reference),edges(candidate)
    if not ea.any() and not eb.any():
        f1=1.0; chamfer=0.0
    elif not ea.any() or not eb.any():
        f1=0.0; chamfer=float(math.hypot(*reference.size))
    else:
        da,db=_distance(ea),_distance(eb)
        precision=float(np.mean(da[eb]<=tolerance))
        recall=float(np.mean(db[ea]<=tolerance))
        f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
        chamfer=(float(np.mean(db[ea]))+float(np.mean(da[eb])))/2
    return {'psnr_db':psnr,'ssim':ssim,'edge_f1':f1,'chamfer_px':chamfer}


def trajectory_error(expected, observed):
    if len(expected)!=len(observed) or not expected:
        raise ValueError('Matched nonempty landmarks required')
    return float(np.mean([math.dist(a,b) for a,b in zip(expected,observed)]))


def endpoint_equal(expected, actual):
    return expected.mode==actual.mode and expected.size==actual.size and np.array_equal(np.asarray(expected),np.asarray(actual))
