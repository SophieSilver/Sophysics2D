import pygame
import pygame_gui

from sophysics_engine import SimEnvironment, TimeSettings, PhysicsManager, \
    Camera, GUIManager, PygameEventProcessor
from defaults import CameraController, PauseOnSpacebar, AttractionManager
from .lower_panel import LowerPanel
from .selection import GlobalSelection
from .velocity_controller import VelocityController
from .reference_frame import ReferenceFrameManager, ReferenceFrameCameraAdjuster
from typing import Dict


def get_environment_from_config(display: pygame.Surface, config: Dict) -> SimEnvironment:
    """
    As a config, pass it an "environmentCfg" dictionary
    """
    time_settings = TimeSettings(**config["timeSettingsArgs"])
    physics_manager = PhysicsManager()
    camera = Camera(display, **config["cameraArgs"])
    pygame_ui_manager = pygame_gui.UIManager(
        window_resolution=display.get_size(),
        **config["UIManagerArgs"],
    )
    gui_manager_component = GUIManager(pygame_ui_manager, **config["GUIManagerComponentArgs"])
    event_processor = PygameEventProcessor()
    # can't store rect in a json, so we have to do this awkwardness
    cam_controller_config = config["cameraControllerCfg"]
    camera_controller = CameraController(
        camera,
        pygame.Rect(cam_controller_config["rect"]),
        cam_controller_config["hold_time"],
        cam_controller_config["zoom_strength"],
        cam_controller_config["min_camera_scale"]
    )

    attraction_manager = AttractionManager(config["attractionCfg"]["attraction_coefficient"])
    
    selection_config = config["globalSelectionCfg"]
    global_selection = GlobalSelection(
        rect=pygame.Rect(selection_config["rect"]),
        button=selection_config["button"],
        hold_time=selection_config["hold_time"]
    )

    vel_controller_config = config["velocityControllerCfg"]
    vel_controller = VelocityController(
        camera=camera,
        rect=pygame.Rect(vel_controller_config["rect"]),
        scale_factor=vel_controller_config["scale_factor"],
        button=vel_controller_config["button"],
        hold_time=vel_controller_config["hold_time"]
    )

    time_control_panel = LowerPanel(config["timeControlPanelCfg"])

    reference_frame_manager = ReferenceFrameManager()
    camera_adjuster = ReferenceFrameCameraAdjuster(camera)

    pause_on_spacebar = PauseOnSpacebar()

    env = SimEnvironment((), (
        time_settings, physics_manager, camera, gui_manager_component,
        event_processor, time_control_panel, camera_controller, pause_on_spacebar,
        attraction_manager, global_selection, vel_controller, reference_frame_manager,
        camera_adjuster
    ))

    return env
