from typing import Optional, Tuple

from glm import cross, dot, vec3
from geometry.sphere import Sphere
from rtypes import Point

INF = float("INF")

def IntersectRaySphere(O: Point, D: Point, sphere: Sphere) -> Tuple[float, float]:
    r = sphere.radius
    CO = O - sphere.center
    a = dot(D, D)
    b  = 2 * dot(CO, D)
    c = dot(CO, CO) - r*r
    discriminant = b*b - 4*a*c
    
    if discriminant < 0:
        return INF, INF
    t1 = (-b + discriminant**0.5) / (2*a)
    t2 = (-b - discriminant**0.5) / (2*a)
    return t1, t2

def IntersectRayTriangle(O: Point, D: Point, v0: Point, v1: Point, v2: Point) -> Optional[Point]:
    """
    Based on the Moller-Trumbore ray-triangle intersection algorithm
    """
    v0, v1, v2 = vec3(v0), vec3(v1), vec3(v2)
    e1 = v1 - v0
    e2 = v2 - v0
    pvec = cross(D, e2)
    det = dot(e1, pvec)
    if det < 1e-8 and det > -1e-8: return
    inv_det = 1/ det
    tvec = O - v0
    u = dot(tvec, pvec) * inv_det
    if u < 0 or u > 1: return
    qvec = cross(tvec, e1)
    v = dot(D, qvec) * inv_det
    if (v < 0) or (u + v) > 1: return
    distance = dot(e2, qvec) * inv_det
    return distance
