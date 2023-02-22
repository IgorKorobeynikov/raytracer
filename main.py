from typing import Optional, List, Tuple
from dataclasses import dataclass
from random import randint, uniform
from enum import Enum

from PIL import Image
from glm import length2, radians, rotateX, rotateY, rotateZ, rotate, u8vec3, vec3, length, cross, dot, normalize, vec4
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
    def put_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
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
        global TOTAL_TRACED_RAYS
        TOTAL_TRACED_RAYS += 1
        closest_object, closest_t = self.closestIntersection(O, D, t_min, t_max)

        if closest_object == None:
            x, y = rayToSkyboxXY(D, SKBOX.width, SKBOX.height)
            return SKBOX.getpixel((x, y))

        # calculating point on object
        P = O + closest_t * vec3(D)
        # calculating normal for sphere
        N = P - closest_object.center
        N = normalize(N)

        if not isinstance(closest_object, Sphere):
            N = closest_object.normal

        L = self.computeLighting(P, N, -D, closest_object.material.specular_glare)
        local_color = vec3asColor(vec3(closest_object.material.albedo) * L)

        r = closest_object.material.reflective
        if rdepth <= 0 or r <= 0:
            return local_color

        colors = []
        for samples in range(ANTI_NOISE_SAMPLES if closest_object.material.blurry else 1):
            R = ReflectRay(-D, N) + closest_object.material.blurry * randomInUnitSphere()
            reflected_color = self.traceRay(P, R, 0.1, INF, rdepth - 1)
            colors.append(reflected_color)
        reflected_color = averageColor(colors)

        return vec3asColor((vec3(local_color) * (1 - r) + vec3(reflected_color) * r) * local_color/255)

    def computeLighting(self, P: Point, N: Vector3f, V: Vector3f, s: float) -> vec3:
        assert s != 0, "specular must be -1, or specular > 0"
        """
        Based on Phong shading model
 
        P: A point on the surface
        N: Normal of surface
        """
        i = vec3()
        for light in self.scene.lights:
            if light.type_ == LightType.ambient:
                i += light.intensity
            else:
                if light.type_ == LightType.point:
                    L = light.position - P
                    t_max = 1
                else:
                    L = -light.direction
                    t_max = INF

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

        return i

def main() -> None:

    silver = Material(
        albedo=vec3(255, 255, 255), 
        reflective=1, 
        specular_glare=100,
        refractive=0.0,
        blurry=0
    )

    s = Scene(
        [
            Light(
                type_=LightType.ambient, 
                intensity=vec3(0.5, 0.5, 0.5)
            ),
            Light(
                type_=LightType.point, 
                intensity=vec3(0.8, 0.8, 0.8), 
                position=vec3(5, 8, 7)
            ),
        ],
        [
            Sphere(
                radius=4, 
                center=vec3(0, 0, -14),
                material=silver
            )
        ],

    )
    progress_bar = tqdm(total=CWIDTH*CHEIGHT, desc="Traced primary rays", colour="green", unit=" ray")

    gs = GSystem(s, Canvas(CWIDTH, CHEIGHT), Viewport(2, 1, 1), Camera(vec3(0, 0, 0)))
    for x in range(-gs.canvas.width//2, gs.canvas.width//2):
        for y in range(-gs.canvas.height//2, gs.canvas.height//2):
            D = rotateX(rotateY(rotateZ(gs.canvasToViewport(x, y), radians(Z_CAM_ROTATION)), radians(Y_CAM_ROTATION)), radians(X_CAM_ROTATION))
            color = tuple(gs.traceRay(gs.camera.position, D, 1, INF, 4))
            gs.canvas.put_pixel(x, y, color)
            progress_bar.update()
    progress_bar.close()
    print(f"\n\033[1m\033[37mTOTAL PRIMARY TRACED RAYS:\033[0m \033[1m\033[42m{CWIDTH*CHEIGHT:,}\033[0m")
    print(f"\n\033[1m\033[37mTOTAL SHADOW/REFLECTED RAYS:\033[0m \033[1m\033[42m{TOTAL_TRACED_RAYS-CWIDTH*CHEIGHT:,}\033[0m")
    print(f"\n\033[1m\033[37mTOTAL TRACED RAYS:\033[0m \033[1m\033[42m{TOTAL_TRACED_RAYS:,}\033[0m")
    gs.canvas.show()

if __name__ == "__main__":
    main()