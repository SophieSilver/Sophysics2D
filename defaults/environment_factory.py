from sophysics_engine import SimObject, SimEnvironment, TimeSettings,  PhysicsManager, Camera
from typing import Iterable


def get_default_environment(time_settings: TimeSettings,
                            physics_manager: PhysicsManager,
                            camera: Camera,
                            sim_objects: Iterable[SimObject] = ()):
    """
    The function that creates a default environment containing time settings, physics manager, and camera components
    """
    environment = SimEnvironment(sim_objects, (time_settings, physics_manager, camera))
    return environment
