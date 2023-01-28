from dataclasses import dataclass
from material import Material
from rtypes import Point
@dataclass
class Sphere:
    material: Material
    radius: float
    center: Point