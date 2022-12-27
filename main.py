from typing import Any, Optional
from dataclasses import dataclass
import math

import numpy
from PIL import Image

from geometry.sphere import Sphere
from geometry.primitive import Primitive
from rtypes import Color, Point
from enum import Enum
inf = float("inf")

class LightType(Enum):
    ambient = 0
    point = 1
    directional = 2

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
@dataclass
class Light:
    type_: LightType
    intensity: float
    position: Optional[Point] = None
    direction: Optional[Point] = None

class Scene:
    lights = list[Light]
    objects: list[Primitive] = []
    def __init__(self, ligths, objects) -> None:
        self.lights = ligths
        self.objects = objects
class Canvas:
    def __init__(self, w: int, h: int) -> None:
        assert w + h != 0
        self._image = Image.new("RGB", (w, h))
        self._pixels = [[(0, 0, 0) for x in range(w)] for y in range(h)] 
    @property
    def width(self) -> int:
        return len(self._pixels[0])
    @property
    def height(self) -> int:
        return len(self._pixels)
    def put_pixel(self, x: int, y: int, color: Color) -> None:
        self._pixels[y][x] = color
        self._image.putpixel([x+self.width//2, y+self.height//2], color)
    def get_pixel(self, x: int, y: int) -> Color:
        return self._pixels[y][x]
    def show(self) -> None:
        self._image.show()
@dataclass
class Viewport:
    width: float
    height: float
    distanse: float

@dataclass
class Camera:
    position: Point

class GSystem:
    def __init__(self, scene: Scene, canvas: Canvas, viewport: Viewport, camera: Camera) -> None:
        self.camera = camera
        self.canvas = canvas
        self.viewport = viewport
        self.scene = scene

    def canvasToViewport(self, x: int, y: int) -> Point:
        x, y, d = (
            x*self.viewport.width / self.canvas.width,
            y*self.viewport.height / self.canvas.height, 
            self.viewport.distanse
        )
        center = numpy.array([0, 0])

        cathet1 = numpy.linalg.norm(numpy.array([x, y]) - center) # scalar value, cathet opposite the fov angle
        cathet2 = d # scalar value
        hypot = math.sqrt(cathet1 ** 2 + cathet2 ** 2)

        sin_of_hfov = (math.sin(math.radians(90)) * cathet1) / hypot # Sine theorem
        hfov = math.degrees(math.asin(sin_of_hfov))

        d *= math.cos(math.radians(hfov))

        return x, y, d

    def traceRay(self, O: Point, D: Point, t_min: float, t_max: float) -> Color:
        closest_t = inf
        closest_sphere = None
        for sphere in self.scene.objects:

            if not isinstance(sphere, Sphere): 
                p = IntersectRayTriangle(O, D, sphere.v0, sphere.v1, sphere.v2)
                if p != None:
                    return tuple(map(int, (numpy.array(sphere.color) * computeLighting(self.scene, P, N))))
                else: continue
            
            t1, t2 = IntersectRaySphere(O, D, sphere)
            if (t_min <= t1 <= t_max) and t1 < closest_t:
                closest_t = t1
                closest_sphere = sphere
            if t_min <= t2 <= t_max and t2 < closest_t:
                closest_t = t2
                closest_sphere = sphere
        if closest_sphere == None:
            return (0,0,0)
        P = O + closest_t * numpy.array(D)
        N = P - closest_sphere.center 
        return tuple(map(int, (numpy.array(closest_sphere.color) * computeLighting(self.scene, P, N))))


def IntersectRaySphere(O: Point, D: Point, sphere: Sphere) -> Color:
    r = sphere.radius
    CO = numpy.array(O) - numpy.array(sphere.center)
    a = numpy.dot(D, D)
    b  = 2 * numpy.dot(CO, D)
    c = numpy.dot(CO, CO) - r*r
    discriminant = b*b - 4*a*c
    
    if discriminant < 0:
        return inf, inf
    t1 = (-b + discriminant**0.5) / (2*a)
    t2 = (-b - discriminant**0.5) / (2*a)
    return t1, t2

def IntersectRayTriangle(O: Point, D: Point, v0: Point, v1: Point, v2: Point) -> Optional[Point]:
    """
    Based on the Moller-Trumbore ray-triangle intersection algorithm
    """
    v0, v1, v2 = numpy.array(v0), numpy.array(v1), numpy.array(v2)

    e1 = v1 - v0
    e2 = v2 - v0
    pvec = numpy.cross(D, e2)
    det = numpy.dot(e1, pvec)
    if det < 1e-8 and det > -1e-8: return
    inv_det = 1/ det
    tvec = O - v0
    u = numpy.dot(tvec, pvec) * inv_det
    if u < 0 or u > 1: return
    qvec = numpy.cross(tvec, e1)
    v = numpy.dot(D, qvec) * inv_det
    if (v < 0) or (u + v) > 1: return
    distance = (numpy.dot(e2, qvec) * inv_det)
    return tuple((O + distance) * D)

def computeLighting(scene: Scene, P: Point, N: Point) -> float:
    i = 0.0
    for light in scene.lights:
        if light.type_ == LightType.ambient:
            i += light.intensity
        else:
            if light.type_ == LightType.point:
                L = light.position - P
            else:
                L = light.direction
            n_dot_l = numpy.dot(N, L)
            if n_dot_l > 0:
                i += light.intensity * n_dot_l/(numpy.linalg.norm(N) * numpy.linalg.norm(L))
    return i
def main() -> None:

    s = Scene(
        [
            Light(LightType.ambient, 0.2),
            Light(LightType.point, 0.6, position=(2, 1, 0)),
            Light(LightType.directional, 0.2, direction=(1, 4, 4))
        ],
        [
            #Sphere(
            #    (255, 0, 0), 1, (0, 1, 3)
            #),
            Sphere(
                (0, 255, 0), 1, (2, 0, 4)
            ),
            #Sphere(
            #    (0, 0, 255), 1, (-2, 0, 4)
            #),
            Triangle((-4, 0, 8), (1, 0, 8), (-3, 3.5, 8), (0, 255, 255))
        ]
    )
    gs = GSystem(s, Canvas(800, 400), Viewport(2, 1, 1), Camera((0, 0, 0)))
    #gs = GSystem(s, Canvas(200, 100), Viewport(2, 1, 1), Camera((0, 0, 0)))
    for x in range(-gs.canvas.width//2, gs.canvas.width//2):
        for y in range(-gs.canvas.height//2, gs.canvas.height//2):
            D = gs.canvasToViewport(x, y) 
            color = gs.traceRay(gs.camera.position, D, 1, inf)
            gs.canvas.put_pixel(x, y, color)
    gs.canvas.show()

if __name__ == "__main__":
    main()