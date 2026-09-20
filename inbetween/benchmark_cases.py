"""Deterministic synthetic character motion diagnostics."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw

SIZE = 256
SCALE = 3
CATEGORIES = (
    'small_translation', 'large_translation', 'curved_arc', 'rigid_rotation',
    'articulated_limb', 'crossing_limbs', 'squash_stretch', 'occlusion',
    'hold_then_fast', 'exaggeration',
)

@dataclass
class Case:
    identifier: str
    metadata: dict
    frames: list[Image.Image]
    landmarks: list[tuple[float, float]]


def _draw(category: str, t: float) -> tuple[Image.Image, tuple[float, float]]:
    image = Image.new('RGB', (SIZE*SCALE, SIZE*SCALE), 'white')
    d = ImageDraw.Draw(image)
    u = t
    if category == 'hold_then_fast':
        u = max(0.0, (t-.65)/.35)
    x = 128 + (12 if category == 'small_translation' else 66 if category == 'large_translation' else 35)*(u-.5)
    y = 130
    if category == 'curved_arc':
        y -= 42*math.sin(math.pi*t)
    if category == 'exaggeration':
        x += 18*math.sin(math.pi*t)
        y -= 20*math.sin(math.pi*t)
    angle = (t-.5)*1.25 if category == 'rigid_rotation' else 0
    sx = 1 + (.45*math.sin(math.pi*t) if category == 'squash_stretch' else 0)
    sy = 1 - (.32*math.sin(math.pi*t) if category == 'squash_stretch' else 0)
    def point(px, py):
        px, py = px*sx, py*sy
        return ((x+px*math.cos(angle)-py*math.sin(angle))*SCALE,
                (y+px*math.sin(angle)+py*math.cos(angle))*SCALE)
    def line(points, width=4):
        d.line([point(*p) for p in points], fill=(20,25,35), width=width*SCALE, joint='curve')
    head = point(0,-39)
    r = 11*SCALE
    d.ellipse((head[0]-r,head[1]-r,head[0]+r,head[1]+r), outline=(20,25,35), width=4*SCALE)
    line([(0,-27),(0,18)])
    arm = (-24+48*t, -3-14*math.sin(math.pi*t)) if category in ('articulated_limb','crossing_limbs') else (-25,-4)
    line([(0,-18),(-13,-10),arm])
    other = (24-48*t, -4) if category == 'crossing_limbs' else (25,-4)
    line([(0,-18),(13,-10),other])
    line([(0,18),(-16,48)])
    line([(0,18),(18,48)])
    if category == 'occlusion':
        # A foreground wall masks and then reveals the moving character.
        d.rectangle((138*SCALE,48*SCALE,158*SCALE,220*SCALE), fill='white')
        d.line(((138*SCALE,48*SCALE),(138*SCALE,220*SCALE)),fill=(100,100,100),width=3*SCALE)
    image = image.resize((SIZE,SIZE), Image.Resampling.LANCZOS)
    return image, (round(x,4),round(y,4))


def make_case(category: str, intermediate_count: int = 6) -> Case:
    if category not in CATEGORIES or not 0 <= intermediate_count <= 120:
        raise ValueError('Unknown case or invalid frame count')
    times = [i/(intermediate_count+1) for i in range(intermediate_count+2)]
    drawn = [_draw(category,t) for t in times]
    metadata = {'case_id':category,'motion_category':category,'resolution':[SIZE,SIZE],
                'ground_truth_frame_count':len(times),'intermediate_count':intermediate_count,
                'timestamps':times,'trajectory_timing': 'hold until t=0.65 then fast' if category=='hold_then_fast' else 'uniform sample of specified parametric motion',
                'expected_difficulty': 'high' if category in ('large_translation','crossing_limbs','occlusion','hold_then_fast','exaggeration') else 'moderate',
                'random_seed':None,'mode':'RGB','background':'white','line_width_px':4,'antialiasing':'3x LANCZOS'}
    return Case(category,metadata,[p[0] for p in drawn],[p[1] for p in drawn])


def generate_assets(output: str | Path, categories=CATEGORIES, intermediate_count=6) -> list[Case]:
    root=Path(output)
    cases=[]
    for category in categories:
        case=make_case(category,intermediate_count)
        folder=root/category
        folder.mkdir(parents=True,exist_ok=True)
        for i,frame in enumerate(case.frames):
            frame.save(folder/f'frame_{i:04d}.png')
        (folder/'metadata.json').write_text(json.dumps({**case.metadata,'landmarks':case.landmarks},indent=2)+'\n')
        cases.append(case)
    return cases
