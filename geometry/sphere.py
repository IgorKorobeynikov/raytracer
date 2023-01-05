from dataclasses import dataclass
from rtypes import Color, Point
@dataclass
class Sphere:
    color: Color
    radius: float
    center: Point
    specular: float