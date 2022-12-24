try:
    from typing import Self
except ImportError:
    Self = ...

from rtypes import Color

class Primitive:
    def __init__(self, center: float, radius: float, color: Color) -> Self:
        self.center = center
        self.color = color

