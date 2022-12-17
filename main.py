from dataclasses import dataclass
from PIL import Image
import numpy

from shapes import Sphere

inf = float("inf")

@dataclass
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
@dataclass
class Point:
    x: int
    y: int
    z: int

class Canvas:
    def __init__(self, widht: int, height: int) -> None:
        self.width = widht
        self.height = height
        self._pixels = [[Color() for i in range(widht)] for i in range(height)]
    def put_pixel(self, pix: Color, x: int, y: int) -> None:
        self._pixels[y][x] = pix
    def get_pixel(self, x: int, y: int) -> Color:
        return self._pixels[y][x]

@dataclass
class Viewport:
    width: int
    height: int

@dataclass
class GSystem:
    canvas: Canvas
    viewport: Viewport
    distance: float
    spheres: list

    def canvasToViewport(self, x: int, y: int) -> tuple[int, int, int]:
        return  (
            x*self.viewport.width/self.canvas.width, 
            y*self.viewport.height/self.canvas.height, 
            self.distance
        )



def traceRay(O: Point, D: Point, t_min: float, t_max: float) -> tuple[int, int]:
    closest_t = inf
    closest_sphere = None
    for sphere in gs.spheres:
        t1, t2 = IntersectRaySphere(O, D, sphere)
        if t1 in [t_min, t_max] and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if t2 in [t_min, t_max] and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere
    if closest_sphere == None:
        return (0,0,0)

def IntersectRaySphere(O: Point, D: Point, sphere: Sphere) -> Color:
    r = sphere.radius
    CO = numpy.array(O) - numpy.array(sphere.radius)
    a = numpy.dot(D, D)
    b  = 2 * numpy.dot(CO, D)
    c = numpy.dot(CO, CO) - r*r
    discriminant = b*b - 4*a*c
    
    if discriminant < 0:
        return inf, inf
    
    t1 = (-b + discriminant**0.5) / (2*a)
    t2 = (-b - discriminant**0.5) / (2*a)
    return t1, t2


gs = GSystem(
    Canvas(500, 250), 
    Viewport(250, 125), 
    1, 
    [
        Sphere(
            (0,255,0), 2, (3,3,3)
        )
    ]
)

O = (0, 0, 0)
for x in range(-gs.canvas.width//2, gs.canvas.width//2):
    for y in range(-gs.canvas.height//2, gs.canvas.height//2):
        D =  gs.canvasToViewport(x, y) 
        color = traceRay(O, D, 1, inf)
        gs.canvas.put_pixel(color, x, y )