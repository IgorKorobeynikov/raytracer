from dataclasses import dataclass
from PIL import Image

@dataclass
class Pixel:
    r: int = 0
    g: int = 0
    b: int = 0

class Canvas:
    def __init__(self, widht: int, height: int) -> None:
        self._pixels = [[Pixel() for i in range(widht)] for i in range(height)]
    def put_pixel(self, pix: Pixel, x: int, y: int) -> None:
        self._pixels[y][x] = pix
    def get_pixel(self, x: int, y: int) -> Pixel:
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

    def canvasToViewport(self, x: int, y: int) -> tuple[int, int, int]:
        return  (
            x*self.viewport.width/self.canvas.width, 
            y*self.viewport.width/self.canvas.height, 
            self.distance
        )



def traceRay(O, D, t_min, t_max): ...