from dataclasses import dataclass
from rtypes import Color, Point

@dataclass
class Triangle:
    v0: Point
    v1: Point
    v2: Point
    color: Color