import pymunk

from typing import Union, Iterable
from .poly_renderer import PolyRenderer
from sophysics_engine import SimObjectComponent, Color, RigidBody, SimObject


number = Union[int, float]


def get_border_object(tag: str, up: number, down: number, left: number, right: number,
                      elasticity: number = 1, color = Color.WHITE, layer: int = 0,
                      components: Iterable[SimObjectComponent] = ()):
    """
    A factory function for creating a border object for the simulation

    up: the upper edge of the border

    down: the lower edge of the border

    left: the left edge of the border

    right: the right edge of the border
    """
    # Since poly shape is convex, and we need the border to be concave,
    # instead we're gonna make it with 4 segment shapes
    # --------------------------------------------------------------
    # First we check if top >= bottom and right >= left
    if(up < down):
        raise ValueError("up is lower than down")
    if(right < left):
        raise ValueError("right is lower than left")

    # Convert side coordinates into vertices
    a = (left, up)
    b = (right, up)
    c = (right, down)
    d = (left, down)

    # creating a renderer
    renderer = PolyRenderer((a, b, c, d), True, color, layer)

    # create a segment for each side
    ab = pymunk.Segment(None, a, b, 0)
    bc = pymunk.Segment(None, b, c, 0)
    cd = pymunk.Segment(None, c, d, 0)
    da = pymunk.Segment(None, d, a, 0)

    # setting the mass and elasticity for the segments
    for segment in (ab, bc, cd, da):
        segment.mass = 1
        segment.elasticity = elasticity

    # creating the body
    rigidbody = RigidBody((ab, bc, cd, da), pymunk.Body.STATIC)

    # packing everything into a sim_object and returning
    return SimObject(tag, components=(renderer, rigidbody, *components))
