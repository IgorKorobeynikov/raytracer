from dataclasses import dataclass
from glm import vec3

@dataclass
class Material:
    albedo: vec3
    reflective: float
    specular_glare: float
    refractive: float
    blurry: float