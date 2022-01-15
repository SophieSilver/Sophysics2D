import pygame
import pymunk
from typing import Dict, List
from sophysics_engine import Transform, RigidBody, Camera, SimObject
from defaults import Attraction, CircleRenderer, VelocityVectorRenderer
from .select_renderer import SelectionRenderer
from .selection import BodyController
from .trail_renderer import TrailRenderer
from .merge_on_collision import MergeOnCollision


# the data types are such, so that we can fill all the parameters from a json file
def get_celestial_body(config: Dict, name: str, initial_position: List[float], initial_velocity: List[float],
                       mass: float, radius: float, is_attractor: bool, min_screen_radius: int, color,
                       draw_layer: int, camera: Camera) -> SimObject:
    transform = Transform(pygame.Vector2(initial_position))

    shape = pymunk.Circle(None, radius)
    shape.mass = mass
    shape.elasticity = 0.0  # don't want planets bouncing off of each other
    rigid_body = RigidBody((shape, ))
    rigid_body.velocity = initial_velocity

    grav_force = Attraction(is_attractor)

    circle_renderer = CircleRenderer(
        radius=radius,
        min_pixel_radius=min_screen_radius,
        color=pygame.Color(color),
        layer=draw_layer
    )

    selection_config = config["selection_renderer"]

    selection_renderer = SelectionRenderer(
        radius=radius,
        min_pixel_radius=min_screen_radius,
        width=selection_config["width"],
        color=tuple(selection_config["color"]),
        layer=selection_config["layer"]
    )
    selection_renderer.is_active = False

    arrow_config = config["velocity_arrow"]
    # changing color from list to pygame.Color to save on space
    arrow_config["color"] = pygame.Color(arrow_config["color"])

    velocity_renderer = VelocityVectorRenderer(**arrow_config)
    velocity_renderer.is_active = False

    controller_config = config["controller"]

    body_controller = BodyController(
        camera=camera,
        radius=radius,
        rect=pygame.Rect(controller_config["rect"]),
        button=controller_config["button"],
        min_pixel_radius=min_screen_radius,
        hold_time=controller_config["hold_time"]
    )

    trail_config = config["trail"]
    trail_color = pygame.Color(color)
    trail_color.a = trail_config["alpha"]

    trail_renderer = TrailRenderer(
        point_distance=radius,
        max_points=trail_config["max_points"],
        thickness=trail_config["thickness"],
        color=trail_color,
        layer=trail_config["layer"]
    )

    merge_on_collision = MergeOnCollision()

    sim_object = SimObject(
        tag=name,
        components=(
            transform, rigid_body, grav_force, circle_renderer, selection_renderer,
            velocity_renderer, body_controller, trail_renderer, merge_on_collision
        )
    )

    # Add a collision listener
    # add a trace renderer

    return sim_object
