from dataclasses import dataclass

@dataclass
class Sphere:
    color: tuple[float, float, float]
    radius: float
    center: tuple[float, float, float]