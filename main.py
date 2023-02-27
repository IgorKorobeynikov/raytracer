from typing import Optional, List, Tuple
from dataclasses import dataclass
from random import randint, uniform
from enum import Enum

from PIL import Image
from glm import length2, mat3, mix, radians, rotateX, rotateY, rotateZ, rotate, u8vec3, vec3, length, cross, dot, normalize, vec4
from tqdm import tqdm

from geometry.sphere import Sphere
from geometry.primitive import Primitive
from geometry.triangle import Triangle
from intersections import IntersectRayTriangle, IntersectRaySphere
from material import Material
from rtypes import Color, Point, Vector3f
from vertexloader import Loader
from utils import *
from settings import *

INF = float("INF")

TOTAL_TRACED_RAYS = 0

SKBOX = Image.open("sky.jpg")

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
    lights: List[Light] = []
    objects: List[Primitive] = []
    def __init__(self, lights, objects) -> None:
        self.lights = lights
        self.objects = objects
class Canvas:
    def __init__(self, w: int, h: int) -> None:
        assert w + h != 0
        self._image = Image.new("RGB", (w, h))
        self._pixels = [[(255, 255, 255) for x in range(w)] for y in range(h)] 
    @property
    def width(self) -> int:
        return len(self._pixels[0])
    @property
    def height(self) -> int:
        return len(self._pixels)
    def put_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        self._pixels[y][x] = color
        self._image.putpixel([x+self.width//2, y+self.height//2], color)
    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
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

    def castRay(self, O: Point, D: Point, t_min: float, t_max: float) -> Tuple[Primitive, float]:
        closest_t = INF
        closest_object = None
        for object_ in self.scene.objects:
            if isinstance(object_, Triangle):
                if t1 := IntersectRayTriangle(O, D, object_.v0, object_.v1, object_.v2):

                    if dot(D, object_.normal) > 0: continue

                    if not t1 < closest_t: continue
                    if not ((t_min < t1) and (t1 < t_max)): continue
                    closest_t = t1
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
        L = vec3(0.0)
        F = vec3(1.0)

        for i in range(rdepth):
            closest_object, closest_t = self.castRay(O, D, t_min, t_max)
            if closest_object:
                P = O + closest_t * vec3(D)
                # calculating normal for sphere
                N = P - closest_object.center
                N = normalize(N)
                if not isinstance(closest_object, Sphere):
                    N = closest_object.normal

                #hemisphereDistributedDirection = normal_oriented_hemisphere_point(random2D(), N)
                random_vec = normal_oriented_hemisphere_point(N) # normalize(2.0 * random3D() - 1.0)

                #tangent = cross(random_vec, N)
                #bitangent = cross(N, tangent)
                #transform = mat3(tangent, bitangent, N)
                #newRayDirection = transform * hemisphereDistributedDirection

                #idealReflection = ReflectRay(-D, N)
                #newRayDirection = normalize(mix(newRayDirection, idealReflection, closest_object.material.roughness))
                
                t_min = 0.1
                #D = ReflectRay(-D, N) + closest_object.material.roughness * randomInUnitSphere()
                O = P
                D = normalize(random_vec)
                L += F * closest_object.material.emmitance
                F *= closest_object.material.reflectance
            else: F = vec3(0.0)
        return vec3asColor(u8vec3(L*255))

def avg(colors):
    r, g, b = 0,0,0
    for color in colors:
        r += color[0]
        g += color[1]
        b += color[2]
    r //= len(colors)
    g //= len(colors)
    b //= len(colors)
    return r,g,b

def main() -> None:

    matte = Material(
        reflectance=vec3(1.0), 
        emmitance=vec3(0.0),
        roughness=1
    )
    redm = Material(
        reflectance=vec3(1, 0.0, 0.0), 
        emmitance=vec3(0.0),
        roughness=1
    )
    greenm = Material(
        reflectance=vec3(0.0, 1, 0.0), 
        emmitance=vec3(0.0),
        roughness=1
    )
    mattes = Material(
        reflectance=vec3(1,1,1), 
        emmitance=vec3(0),
        roughness=1
    )
    light = Material(
        reflectance=vec3(0.99, 0.98, 0.85),
        emmitance=vec3(10),
        roughness=0
    )
    grenmatte = Material(
        reflectance=vec3(1, 1, 0),
        emmitance=0.0,
        roughness=1
    )
    a=Triangle(vec3(-1, -1, 3), vec3(-1, 1, 3), vec3(1, -1, 3), material=mattes)
    a1=Triangle(vec3(-1, 1, 3), vec3(1, 1, 3),  vec3(1, -1, 3),material=mattes)
    a.normal=vec3(0,0,-1)
    a1.normal=vec3(0,0,-1)
    s = Scene(
        [
        ],
        [
            Triangle(vec3(-1, -1, 0), vec3(1, -1, 0), vec3(-1, -1, 3), material=matte),
            Triangle(vec3(1, -1, 3), vec3(-1, -1, 3), vec3(1, -1, 0), material=matte),

            Triangle(vec3(-1, -1, 3), vec3(-1, 1, 0), vec3(-1, -1, 0), material=redm),
            Triangle(vec3(-1, -1, 3), vec3(-1, 1, 3), vec3(-1, 1, 0), material=redm),

            Triangle(vec3(1, -1, 0), vec3(1, 1, 0), vec3(1, -1, 3), material=greenm),
            Triangle(vec3(1, 1, 0), vec3(1, 1, 3), vec3(1, -1, 3), material=greenm),
            
            a, a1,
            
            Triangle(vec3(-1, 1, 3), vec3(1, 1, 0), vec3(-1, 1, 0), material=matte),
            Triangle(vec3(1, 1, 0), vec3(-1, 1, 3), vec3(1, 1, 3), material=matte),

            Triangle(vec3(-0.5, 0.99, 1), vec3(-0.5, 0.99, 1.5), vec3(0.5, 0.99, 1), material=light),
            Triangle(vec3(-0.5, 0.99, 1.5), vec3(0.5, 0.99, 1.5), vec3(0.5, 0.99, 1), material=light),

            Sphere(0.5, vec3(-0, -0.5, 1.5), grenmatte)
        ],

    )
    progress_bar = tqdm(total=CWIDTH*CHEIGHT, desc="Traced primary rays", colour="green", unit=" ray")

    gs = GSystem(s, Canvas(CWIDTH, CHEIGHT), Viewport(1, 1, 1), Camera(vec3(0, 0, -2.1)))
    for x in range(-gs.canvas.width//2, gs.canvas.width//2):
        for y in range(-gs.canvas.height//2, gs.canvas.height//2):
            D = rotateX(rotateY(rotateZ(gs.canvasToViewport(x, y), radians(Z_CAM_ROTATION)), radians(Y_CAM_ROTATION)), radians(X_CAM_ROTATION))
            #color = tuple(gs.traceRay(gs.camera.position, D, 1, INF, 10))
            color = avg([tuple(gs.traceRay(gs.camera.position, D, 1, INF, 5)) for i in range(10)])
            gs.canvas.put_pixel(x, y, color)
            progress_bar.update()
    progress_bar.close()
    gs.canvas.show()

if __name__ == "__main__":
    main()