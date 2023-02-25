from dataclasses import dataclass
from glm import vec3

@dataclass
class Material:
    reflectance: vec3
    emmitance: vec3
    roughness: float
    #opacity: float