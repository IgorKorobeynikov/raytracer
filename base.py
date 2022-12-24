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

    def traceRay(self, O: Point, D: Point, t_min: float, t_max: float) -> tuple[int, int, int]:
        closest_t = inf
        closest_sphere = None
        for sphere in self.scene.objects:
            if not isinstance(sphere, Sphere): raise ValueError("Cant trace ray for non sphere")
            t1, t2 = IntersectRaySphere(O, D, sphere)
            if (t_min <= t1 <= t_max) and t1 < closest_t:
                closest_t = t1
                closest_sphere = sphere
            if t_min <= t2 <= t_max and t2 < closest_t:
                closest_t = t2
                closest_sphere = sphere
        if closest_sphere == None:
            return (0,0,0)
        #print(type(closest_t), type(D), closest_t, D)
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
            Sphere(
                (255, 0, 0), 1, (0, 1, 3)
            ),
            Sphere(
                (0, 255, 0), 1, (2, 0, 4)
            ),
            Sphere(
                (0, 0, 255), 1, (-2, 0, 4)
            ),
        ]
    )
    gs = GSystem(s, Canvas(800, 400), Viewport(2, 1, 1), Camera((0, 0, 0)))
    for x in range(-gs.canvas.width//2, gs.canvas.width//2):
        for y in range(-gs.canvas.height//2, gs.canvas.height//2):
            D = gs.canvasToViewport(x, y) 
            color = gs.traceRay(gs.camera.position, D, 1, inf)
            gs.canvas.put_pixel(x, y, color)
    gs.canvas.show()

if __name__ == "__main__":
    main()