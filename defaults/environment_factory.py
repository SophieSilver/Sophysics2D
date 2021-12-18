from sophysics_engine import SimObject, SimEnvironment, TimeSettings,  PhysicsManager, Camera, \
    GUIManager, PygameEventProcessor
from typing import Iterable


def get_default_environment(time_settings: TimeSettings,
                            physics_manager: PhysicsManager,
                            camera: Camera,
                            gui_manager: GUIManager,
                            sim_objects: Iterable[SimObject] = ()):
    """
    The function that creates a default environment containing a time settings, physics manager, camera,
    components
    """
    pygame_event_processor = PygameEventProcessor()
    environment = SimEnvironment(sim_objects, (
        time_settings,
        physics_manager,
        camera,
        pygame_event_processor,
        gui_manager))

    return environment
