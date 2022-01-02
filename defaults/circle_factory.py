from typing import Iterable, Union

import pymunk

from .circle_renderer import CircleRenderer
from sophysics_engine import Color, SimObjectComponent, RigidBody, SimObject


number = Union[int, float]


def get_circle_body(tag: str = "", mass: number = 1, elasticity: number = 1, radius: number = 1,
                    min_pixel_radius: int = 0,
                    color = Color.WHITE, layer: int = 0,
                    components: Iterable[SimObjectComponent] = ()):
    """
    A factory function for creating a sim_object that models a circle
    and has a CircleCollider and a CircleRenderer
    """
    # kinda like a prefab in Unity
    shape = pymunk.Circle(None, radius)
    shape.mass = mass
    shape.elasticity = elasticity
    rigidbody = RigidBody((shape,))
    renderer = CircleRenderer(radius, min_pixel_radius, color, layer)

    return SimObject(tag, components=(renderer, rigidbody, *components))
