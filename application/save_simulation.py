from sophysics_engine import SimEnvironment, Camera, TimeSettings, RigidBody, SimObject
from defaults import CircleRenderer, Attraction
from .reference_frame import ReferenceFrameManager
from typing import Optional, Dict, List
import json


def save_simulation_to_json(file, environment: SimEnvironment, camera: Optional[Camera]):
    """
    Saves the current state of the simulation into a json file
    """
    simulation_dict = get_simulation_dict(environment, camera)

    json_string = json.dumps(simulation_dict, indent=4)

    with open(file, "w", encoding="utf-8") as f:
        f.write(json_string)


def get_simulation_dict(environment: SimEnvironment, camera: Optional[Camera]) -> Dict:
    # save the time settings
    time_settings: TimeSettings = environment.get_component(TimeSettings)
    time_settings_dict = {
        "dt": time_settings.dt,
        "steps_per_frame": time_settings.steps_per_frame,
        "paused": time_settings.paused
    }

    # save the camera settings
    camera_settings_dict = {
        "units_per_pixel": camera.units_per_pixel,
        "position": list(camera.position)
    }

    # get the origin id
    # get the reference to the origin object
    reference_frame_manager: ReferenceFrameManager = environment.get_component(ReferenceFrameManager)
    origin = reference_frame_manager.origin_body
    origin_id = id(origin)

    # get the bodies
    bodies = []

    for sim_object in environment.sim_objects:
        body_dict = get_body_dict(sim_object)

        if body_dict is not None:
            bodies.append(body_dict)

    simulation_dict = {
        "origin_id": origin_id,
        "time_settings": time_settings_dict,
        "camera_settings": camera_settings_dict,
        "bodies": bodies
    }

    return simulation_dict


def get_body_dict(sim_object: SimObject) -> Optional[Dict]:
    rigidbody: Optional[RigidBody] = sim_object.try_get_component(RigidBody)
    if rigidbody is None:
        return None

    body_id = id(rigidbody)

    renderers: List[CircleRenderer] = sim_object.get_components(CircleRenderer)
    attraction: Attraction = sim_object.get_component(Attraction)

    circle_renderer = None

    # because both selection and circle renderers are circle renderers we need to filter them
    for r in renderers:
        if type(r) is CircleRenderer:
            circle_renderer = r
            break

    # parameters
    parameters = {
        "name": sim_object.tag,
        "initial_position": list(sim_object.transform.position),
        "initial_velocity": list(rigidbody.velocity),
        "mass": rigidbody.mass,
        "radius": circle_renderer.radius,
        "min_screen_radius": circle_renderer.min_pixel_radius,
        "is_attractor": attraction.is_attractor,
        "color": list(circle_renderer.color),
        "draw_layer": circle_renderer.layer
    }

    # compiling everything into 1 dict
    body_dict = {
        "id": body_id,
        "parameters": parameters
    }

    return body_dict
