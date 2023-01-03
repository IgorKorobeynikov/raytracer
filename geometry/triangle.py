from dataclasses import dataclass
from rtypes import Color, Point
import numpy
@dataclass
class Triangle:
    v0: Point
    v1: Point
    v2: Point
    color: Color
    def getcenter(self) -> Point:
        x0 = (self.v0[0]+self.v1[0]+self.v2[0])/3
        y0 = (self.v0[1]+self.v1[1]+self.v2[1])/3
        z0 = (self.v0[2]+self.v1[2]+self.v2[2])/3
        return x0, y0, z0
    def getnormal(self) -> numpy.ndarray:
        N = numpy.cross(numpy.array(self.v1)-numpy.array(self.v0), numpy.array(self.v2)-numpy.array(self.v0))
        #print(N / numpy.linalg.norm(N))
        return N / numpy.linalg.norm(N)