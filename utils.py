from random import uniform
from typing import List, Tuple
from math import sqrt, atan2, acos, pi
from rtypes import Color
from glm import length2, vec3, dot

def averageColor(colors: List[Color]) -> vec3:
    summed_colors = vec3(*map(sum, zip(*colors)))
    return summed_colors / len(colors)

def ReflectRay(R: vec3, N: vec3) -> vec3:
    """
    Reflects the ray relative to the normal

    Positional arguments:
    R -- incoming vector
    N -- normal of surface
    
    Returns: vector reflected about the normal
    """
    return 2 * N * dot(N, R) - R

def rayToSkyboxXY(ray: vec3, tw: int, th: int) -> Tuple[int, int]:
    r = sqrt(ray.x**2 + ray.y**2 + ray.z**2)
    theta = atan2(ray.z, ray.x)
    phi = acos(ray.y / r)
    u = (theta + pi) / (2 * pi)
    v = 1 - phi / pi
    x = u * tw
    y = v * th
    return x, y

def randomInUnitSphere() -> vec3:
    while True:
        p = vec3(uniform(-1, 1), uniform(-1, 1), uniform(-1, 1))
        if length2(p) < 1:
            return p