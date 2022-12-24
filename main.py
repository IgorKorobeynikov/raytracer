from dataclasses import dataclass
from PIL import Image
import numpy
from geometry.sphere import Sphere

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
        self._pixels = [[Color(255,255,255) for i in range(widht)] for i in range(height)]
        self._image = Image.new('RGB', [widht, height])
    def put_pixel(self, pix: Color, x: int, y: int) -> None:
        self._pixels[y][x] = pix
        self._image.putpixel([x+self.width//2, y+self.height//2], pix)
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

    def canvasToViewport(self, x: int, y: int) -> tuple[float, float, float]:
        return  (
            x*self.viewport.width/self.canvas.width, 
            y*self.viewport.height/self.canvas.height, 
            self.distance
        )
def traceRay(O: Point, D: Point, t_min: float, t_max: float) -> tuple[int, int, int]:
    closest_t = inf
    closest_sphere = None
    for sphere in gs.spheres:
        t1, t2 = IntersectRaySphere(O, D, sphere)
        if (t_min <= t1 <= t_max) and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if t_min <= t2 <= t_max and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere
    if closest_sphere == None:
        return (0,0,0)
    return closest_sphere.color
    #return tuple( map( round, (numpy.array(closest_sphere.color) * (2/closest_t))))
    

def IntersectRaySphere(O: Point, D: Point, sphere: Sphere) -> Color:
    r = sphere.radius
    CO = numpy.array(O) - numpy.array(sphere.center)
    #CO = numpy.array(O) - numpy.array(sphere.radius)
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
    Canvas(400,400), 
    Viewport(0.95, 1), 
    1, 
    [
        Sphere(
            (255, 0, 0), 1, (0, 1, 3)
        ),
        Sphere(
            (0, 0, 255), 1, (2, 0, 4)
        ),
        Sphere(
            (0, 255, 0), 1, (-2, 0, 4)
        ),
    ]
)

O = (0, 0, 0)
for x in range(-gs.canvas.width//2, gs.canvas.width//2):
    for y in range(-gs.canvas.height//2, gs.canvas.height//2):
        D = gs.canvasToViewport(x, y) 
        #print(D); input()
        color = traceRay(O, D, 1, inf)
        gs.canvas.put_pixel(color, x, y)

gs.canvas._image.show()