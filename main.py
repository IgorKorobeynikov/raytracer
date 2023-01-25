from typing import Any, Optional, List, Tuple
from dataclasses import dataclass
import math
from PIL import Image
from glm import u8vec3, vec2, vec3, length, cross, dot, normalize

from geometry.sphere import Sphere
from geometry.primitive import Primitive
from geometry.triangle import Triangle
from rtypes import Color, Point, Vector3f
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
    lights = List[Light]
    objects: List[Primitive] = []
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
        self._image.save("rendered.png")
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
        return vec3(x, y, d)

    def closestIntersection(self, O: Point, D: Point, t_min: float, t_max: float) -> Tuple[Primitive, float]:
        closest_t = inf
        closest_object = None
        for object_ in self.scene.objects:
            if isinstance(object_, Triangle):
                if p := IntersectRayTriangle(O, D, object_.v0, object_.v1, object_.v2):
                    if not length(p) < closest_t: continue
                    if not ((t_min < length(p)) and (length(p) < t_max)): continue
                    closest_t = length(p)
                    closest_object = object_
                else: continue
            elif isinstance(object_, Sphere):
                t1, t2 = IntersectRaySphere(O, D, object_)
                if ((t_min < t1) and (t1 < t_max)) and t1 < closest_t:
                    closest_t = t1
                    closest_object = object_
                if ((t_min < t2) and (t2 < t_max)) and t2 < closest_t:
                    closest_t = t2
                    closest_object = object_
            else: 
                raise NotImplementedError("Not implemented yet")

        return closest_object, closest_t
    def traceRay(self, O: Point, D: Point, t_min: float, t_max: float, rdepth: float) -> Color:
        closest_object, closest_t = self.closestIntersection(O, D, t_min, t_max)

        if closest_object == None:
            return u8vec3(0, 0, 0)

        P = O + closest_t * vec3(D)
        N = P - closest_object.center
        N = normalize(N)

        if not isinstance(closest_object, Sphere):
            N = -closest_object.normal

        L = self.computeLighting(P, N, -D, closest_object.specular)
        local_color = vec3asColor(vec3(closest_object.color) * L)

        r = closest_object.reflective
        if rdepth <= 0 or r <= 0:
            return local_color

        R = ReflectRay(-D, N)
        reflected_color = self.traceRay(P, R, 0.1, inf, rdepth - 1)

        return vec3asColor(vec3(local_color) * (1 - r) + vec3(reflected_color) * r)
    
    def computeLighting(self, P: Point, N: Vector3f, V: Vector3f, s: float) -> float:
        """
        P: A point on the surface
        N: Normal of surface
        """
        i = vec3()
        for light in self.scene.lights:
            if light.type_ == LightType.ambient:
                i += light.intensity
            else:
                if light.type_ == LightType.point:
                    # L направлен к светильнику
                    L = light.position - P
                    t_max = 1
                else:
                    L = -light.direction
                    t_max = inf

                shadow_obj, shadow_t = self.closestIntersection(P, L, 0.001, t_max)

                if shadow_obj != None:
                    continue

                n_dot_l = dot(N, L)
                if n_dot_l > 0:
                    i += light.intensity * n_dot_l/(length(N) * length(L))
                if s != -1:
                    R = 2 * N * dot(N, L) - L
                    r_dot_v = dot(R, V)
                    if r_dot_v > 0:
                        i += light.intensity * pow(r_dot_v/(length(R) * length(V)), s)

        assert isinstance(i, vec3)
        return i

def ReflectRay(R, N):
    return 2 * N * dot(N, R) - R

def IntersectRaySphere(O: Point, D: Point, sphere: Sphere) -> Color:
    r = sphere.radius
    CO = O - sphere.center
    a = dot(D, D)
    b  = 2 * dot(CO, D)
    c = dot(CO, CO) - r*r
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
    v0, v1, v2 = vec3(v0), vec3(v1), vec3(v2)
    e1 = v1 - v0
    e2 = v2 - v0
    pvec = cross(D, e2)
    det = dot(e1, pvec)
    if det < 1e-8 and det > -1e-8: return
    inv_det = 1/ det
    tvec = O - v0
    u = dot(tvec, pvec) * inv_det
    if u < 0 or u > 1: return
    qvec = cross(tvec, e1)
    v = dot(D, qvec) * inv_det
    if (v < 0) or (u + v) > 1: return
    distance = dot(e2, qvec) * inv_det
    return vec3((O + distance) * D)


def vec3asColor(V: vec3) -> Color:
    return tuple(map(int, V))

def main() -> None:

    s = Scene(
        [
            Light(
                type_=LightType.ambient, 
                intensity=vec3(0.2, 0.2, 0.2)
            ),
            Light(
                type_=LightType.point, 
                intensity=vec3(0.6, 0.6, 0.6), 
                position=vec3(2, 1, 0)
            ),
            Light(
                type_=LightType.directional,
                intensity=vec3(0.2, 0.2, 0.2), 
                direction=-vec3(1, 4, 4)
            ),
        ],
        [
            Triangle(vec3(-1.5, 0.5, 5.2), vec3(1.5, 0.5, 5.2), vec3(-1.5, 2, 4), vec3(0, 0, 0), 500, 1),
            Triangle(vec3(1.5, 0.5, 5.2), vec3(1.5, 2, 4), vec3(-1.5, 2, 4), vec3(0, 0, 0), 500, 1),
            Sphere(
                color=u8vec3(255, 0, 0), 
                radius=1, 
                center=vec3(0, -1, 3),
                specular=500,
                reflective = 0.2
            ),
            Sphere(
                color=u8vec3(0, 0, 255), 
                radius=1, 
                center=vec3(2, 0, 4),
                specular=500,
                reflective=0.3
            ),
            Sphere(
                color=u8vec3(0, 255, 0), 
                radius=1, 
                center=vec3(-2, 0, 4),
                specular=10,
                reflective=0.4 
            ),
            Sphere(
                color=u8vec3(255, 255, 0), 
                radius=5000, 
                center=vec3(0, -5001, 0),
                specular=1000,
                reflective=0.5
            )
            #*Loader("./duck.obj").triangles
        ]
    )
    gs = GSystem(s, Canvas(1200, 600), Viewport(2, 1, 1), Camera(vec3(0, 0, 0)))
    for x in range(-gs.canvas.width//2, gs.canvas.width//2):
        for y in range(-gs.canvas.height//2, gs.canvas.height//2):

            D = gs.canvasToViewport(x, y) 
            
            color = tuple(gs.traceRay(gs.camera.position, D, 1, inf, 4))
            gs.canvas.put_pixel(x, y, color)

    gs.canvas.show()

if __name__ == "__main__":
    main()
