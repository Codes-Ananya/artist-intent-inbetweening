"""Frozen Milestone 6 procedural geometry. See INTENT_GUIDANCE_PROTOCOL.md."""
import hashlib
import math
from PIL import Image, ImageDraw
from .benchmark_cases import Case, make_case

CASE_IDS = ('hinged_gate', 'obstacle_reach', 'landing_ball', 'folding_panel',
            'pendulum', 'screen_cart', 'depth_exchange', 'waving_hand', 's_ribbon', 'bounce_barrier')
INTENTS = (
    [('timing_change', 'early')], [('path_turn', 'early')],
    [('pose_extremum', 'middle')], [('pose_extremum', 'middle')],
    [('path_turn', 'late')], [('visibility_change', 'late')],
    [('visibility_change', 'unspecified')], [('pose_extremum', 'unspecified')],
    [('path_turn', 'early'), ('path_turn', 'late')],
    [('pose_extremum', 'early'), ('visibility_change', 'late')],
)


def pulse(t, center, width):
    return max(0., 1 - abs(t-center)/width)


def render(case_id, t):
    image = Image.new('RGB', (768, 768), 'white')
    d = ImageDraw.Draw(image)
    ink = (20, 25, 35)
    def line(points, color=ink, width=4):
        d.line([(round(x*3), round(y*3)) for x, y in points], fill=color, width=width*3, joint='curve')
    def ellipse(x, y, rx, ry, fill=None):
        d.ellipse(tuple(round(v*3) for v in (x-rx, y-ry, x+rx, y+ry)), fill=fill, outline=ink, width=12)
    def poly(points, fill='white'):
        p = [(round(x*3), round(y*3)) for x, y in points]
        d.polygon(p, fill=fill)
        line(points + [points[0]])
    if case_id == 'hinged_gate':
        a = .15 + 1.15*min(t/.24, 1) - .12*max(0, (t-.24)/.76)
        x, y = 55+130*math.cos(a), 90+45*math.sin(a)
        poly([(55,65), (x,y-25), (x,y+85), (55,175)])
        line([(48,45),(48,210)])
        center = ((55+x)/2, (150+y)/2)
    elif case_id == 'obstacle_reach':
        x, y = 95+115*t, 125-62*pulse(t,.26,.26)
        elbow = (65+55*t, 162-40*math.sin(math.pi*t))
        line([(35,205),elbow,(x,y)])
        ellipse(*elbow, 7, 7)
        poly([(130,145),(160,145),(160,210),(130,210)])
        center = (x,y)
    elif case_id == 'landing_ball':
        p = pulse(t,.46,.22)
        x, y = 55+140*t, 70+105*p+28*t
        ellipse(x,y,15+10*p,18-9*p)
        line([(25,198),(230,198)])
        center = (x,y)
    elif case_id == 'folding_panel':
        q = pulse(t,.56,.44)
        x, y = 145-55*q+18*t, 72+85*q
        poly([(45,60),(110,65),(110,190),(45,180)])
        poly([(110,65),(x,y),(x+15,y+85),(110,190)])
        center = (110,y+45)
    elif case_id == 'pendulum':
        a = -.8+1.7*min(t/.77,1)-.7*max(0,(t-.77)/.23)
        x, y = 128+105*math.sin(a), 40+105*math.cos(a)
        line([(95,35),(160,35)])
        line([(128,40),(x,y)])
        ellipse(x,y,18,18)
        center = (x,y)
    elif case_id == 'screen_cart':
        x, y = 35+185*t, 175
        poly([(x-23,145),(x+23,145),(x+23,178),(x-23,178)])
        ellipse(x-14,184,8,8); ellipse(x+14,184,8,8)
        poly([(65,60),(166,90),(166,210),(65,210)])
        center = (x,y)
    elif case_id == 'depth_exchange':
        x, y = 55+140*t, 115+12*t
        def disk():
            ellipse(x,y,25,25,fill='white')
        def square():
            z = 200-130*t
            poly([(z-24,105),(z+24,105),(z+24,153),(z-24,153)])
        if t < .52:
            disk(); square()
        else:
            square(); disk()
        center = (x,y)
    elif case_id == 'waving_hand':
        a = -.6+1.0*math.sin(2*math.pi*t)+.3*t
        x, y = 125+55*math.sin(a), 140-55*math.cos(a)
        line([(80,215),(125,140),(x,y)])
        ellipse(x,y,13,17)
        for offset in (-10,0,10):
            line([(x+offset,y-10),(x+offset+4,y-32)])
        center = (x,y)
    elif case_id == 's_ribbon':
        x, y = 35+185*t, 125+50*math.sin(2*math.pi*t)
        line([(x-22,y-12),(x,y),(x-22,y+12)])
        line([(x-22,y-12),(x-32,y-8),(x-22,y+12)])
        center = (x,y)
    elif case_id == 'bounce_barrier':
        x = 35+190*t
        p = pulse(t,.23,.23)
        y = 90+90*p+35*t
        ellipse(x,y,12+7*p,16-7*p)
        line([(20,215),(235,215)])
        poly([(181,65),(240,65),(240,210),(181,210)])
        center = (x,y)
    else:
        raise ValueError('Unknown held-out case')
    return image.resize((256,256), Image.Resampling.LANCZOS), center


def pixel_hash(image):
    h = hashlib.sha256()
    h.update(f'{image.mode}:{image.size}:'.encode())
    h.update(image.tobytes())
    return h.hexdigest()


def make_cases():
    cases = []
    for name, events in zip(CASE_IDS, INTENTS):
        drawn = [render(name, i/7) for i in range(8)]
        intent = [{'event': event, 'phase': phase} for event, phase in events]
        cases.append(Case(name, {'case_id': name, 'seed': None, 'randomness': 'none',
                                'intent': intent, 'timestamps': [i/7 for i in range(8)],
                                'resolution': [256,256], 'mode': 'RGB', 'stroke_px': 4,
                                'supersampling': 3}, [p[0] for p in drawn], [p[1] for p in drawn]))
    validate_endpoints(cases)
    return cases


def validate_endpoints(cases):
    """Reject even individual endpoint collisions, stronger than pair uniqueness."""
    seen = {pixel_hash(c.frames[i]) for name in ('curved_arc','hold_then_fast','exaggeration','occlusion')
            for c in [make_case(name,6)] for i in (0,7)}
    for case in cases:
        for index in (0,7):
            digest = pixel_hash(case.frames[index])
            if digest in seen:
                raise ValueError(f'Endpoint hash collision: {case.identifier} frame {index}')
            seen.add(digest)
