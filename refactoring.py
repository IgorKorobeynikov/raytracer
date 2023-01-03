from typing import Any, Optional
from dataclasses import dataclass
import math
import numpy
from PIL import Image

from geometry.sphere import Sphere
from geometry.primitive import Primitive
from geometry.triangle import Triangle
from rtypes import Color, Point
from vertexloader import Loader
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
            -y*self.viewport.height / self.canvas.height, 
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
        closest_object = None
        for object in self.scene.objects:
            if isinstance(object, Triangle):
                if p := IntersectRayTriangle(O, D, object.v0, object.v1, object.v2):
                    if not numpy.linalg.norm(p) < closest_t: continue
                    closest_t = numpy.linalg.norm(p)
                    closest_tp = p
                    closest_object = object
                else: continue
            elif isinstance(object, Sphere):
                t1, t2 = IntersectRaySphere(O, D, object)
                if (t_min <= t1 <= t_max) and t1 < closest_t:
                    closest_t = t1
                    closest_object = object
                if t_min <= t2 <= t_max and t2 < closest_t:
                    closest_t = t2
                    closest_object = object
            else: 
                raise NotImplementedError("Not implemented yet")
        if closest_object == None:
            return (0, 0, 0)
        L = 1
        if isinstance(closest_object,Sphere):
            P = O + closest_t * numpy.array(D)
            N = P - closest_object.center
            L = computeLighting(self.scene, P, N)
        elif isinstance(closest_object,Triangle):
            P = numpy.array(closest_tp)
            N = closest_object.getnormal()
            L = computeLighting(self.scene, P, N)
            #print(L)
        return tuple(map(int, (numpy.array(closest_object.color) * L)))


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

def computeLighting(scene: Scene, P: Point, N: numpy.ndarray) -> float:
    """
    P: A point on the surface
    N: Normal of surface
    """
    i = 0.0
    for light in scene.lights:
        if light.type_ == LightType.ambient:
            i += light.intensity
        else:
            if light.type_ == LightType.point:
                # L направлен к светильнику
                L = light.position - P
            else:
                L = -numpy.array(light.direction)
            n_dot_l = numpy.dot(N, L)
            if n_dot_l > 0:
                i += light.intensity * n_dot_l/(numpy.linalg.norm(N) * numpy.linalg.norm(L))
    return i
def main() -> None:

    s = Scene(
        [
            #Light(LightType.ambient, 0.2),
            #Light(LightType.point, 0.6, position=(2, 1, 0)),
            #Light(LightType.directional, 1, direction=(1, 4, 4))

            Light(LightType.directional, 1, direction=(0, 0, 1))
            #Light(LightType.point, 1, position=(0, 0, 0)),
        ],
        [
            #Sphere(
            #    (255, 0, 0), 1, (0, -1, 3)
            #),
            #Sphere(
            #    (0, 255, 0), 1, (2, 0, 4)
            #),
            #Sphere(
            #    (0, 0, 255), 1, (-2, 0, 4)
            #),
            #Triangle((-0.5, -0.5, 1), (-0.5, 0.5, 1), (0.5, 0.5, 1), (0, 0, 255)),
            #Triangle((-0.5, -0.5, 1), (0.5, 0.5, 1), (0.5, -0.5, 1), (0, 0, 255)),
            #Triangle((-0.5, -0.5, 1), (-0.5, 0.5, 1), (0.5, 0, 5), (0, 0, 255))
            *Loader("../duck.obj").triangles
        ]
    )
    #gs = GSystem(s, Canvas(800, 400), Viewport(2, 1, 1), Camera((0, 0, 0)))
    gs = GSystem(s, Canvas(200, 100), Viewport(2, 1, 1), Camera((0, 0, 0)))
    iters = 0
    for x in range(-gs.canvas.width//2, gs.canvas.width//2):
        for y in range(-gs.canvas.height//2, gs.canvas.height//2):
            D = gs.canvasToViewport(x, y) 
            color = gs.traceRay(gs.camera.position, D, 1, inf)
            gs.canvas.put_pixel(x, y, color)
            iters += 1
            if iters % 200 == 0:
                print(f"Traced rays {iters}/20000")
    gs.canvas.show()

if __name__ == "__main__":
    main()