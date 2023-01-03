from geometry.triangle import Triangle
from rtypes import Color, Point

class Loader:
    def __init__(self, objfilepath: str) -> None:
        self.vertexmap = {}
        self.triangles = []
        with open(objfilepath) as obj:
            l = 0
            while data := obj.readline().split():
                l += 1
                if data[0].lower() == "v":
                    parsed = list(map(float, data[1:]))
                    parsed[2]=-parsed[2]
                    self.vertexmap[l] = parsed
                else:
                    parsed = list(map(int, data[1:]))
                    triangle = Triangle(self.vertexmap[parsed[2]], self.vertexmap[parsed[1]], self.vertexmap[parsed[0]], (0, 255, 0))
                    self.triangles.append(triangle)
