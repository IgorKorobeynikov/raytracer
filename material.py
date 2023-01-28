from dataclasses import dataclass
from glm import vec3

@dataclass
class Albedo:
    specular: float = 0
    diffuse: float = 0

@dataclass
class Material:
    color: vec3
    specular: float
    reflective: float
    refractive: float
    blurry: float
    albedo: Albedo

