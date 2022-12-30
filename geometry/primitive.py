try:
    from typing import Self
except ImportError:
    Self = ...

from rtypes import Color

class Primitive:
    def __init__(self, color: Color) -> Self:
        self.color = color

