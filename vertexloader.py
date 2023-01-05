from geometry.triangle import Triangle
from rtypes import Color, Point

from glm import u8vec3, vec3
from random import randint

rnd = lambda: randint(0, 255)
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
                    v0 = vec3(self.vertexmap[parsed[2]])
                    v1 = vec3(self.vertexmap[parsed[1]])
                    v2 = vec3(self.vertexmap[parsed[0]])
                    triangle = Triangle(v0, v1, v2, u8vec3(rnd(), rnd(), rnd()))
                    self.triangles.append(triangle)
