from dataclasses import dataclass
from material import Material
from rtypes import Point

@dataclass
class Sphere:
    radius: float
    center: Point
    material: Material