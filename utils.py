from random import uniform
from typing import List, Tuple
from math import sqrt, atan2, acos, pi
from rtypes import Color
from glm import length2, vec2, vec3, dot

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

import glm
pi = glm.pi()
def random_hemisphere_point(rand):
    cos_theta = glm.sqrt(1.0 - rand.x)
    sin_theta = glm.sqrt(rand.x)
    phi = 2.0 * pi * rand.y
    return glm.vec3(
        glm.cos(phi) * sin_theta,
        glm.sin(phi) * sin_theta,
        cos_theta
    )
def normal_oriented_hemisphere_point(n):
    v = random_hemisphere_point(vec3(*(uniform(0, 1) for i in range(3))))
    return -v if glm.dot(v, n) < 0.0 else v
def vec3asColor(V: vec3) -> Color:
    return tuple(map(int, V))
def random2D():
    return vec2(uniform(0, 1), uniform(0, 1))
def random3D():
    return vec3(uniform(0, 1), uniform(0, 1), uniform(0, 1))
