from dataclasses import dataclass
from rtypes import Color, Point
from glm import cross, normalize
@dataclass
class Triangle:
    v0: Point
    v1: Point
    v2: Point
    color: Color
    specular: float
    reflective: float

    def __post_init__(self) -> None:
        N = cross(self.v1-self.v0, self.v2-self.v0)
        self.normal = normalize(N)
        self.center = self.getcenter()

    def getcenter(self) -> Point:
        x0 = (self.v0.x+self.v1.x+self.v2.x)/3
        y0 = (self.v0.y+self.v1.y+self.v2.y)/3
        z0 = (self.v0.z+self.v1.z+self.v2.z)/3
        return x0, y0, z0