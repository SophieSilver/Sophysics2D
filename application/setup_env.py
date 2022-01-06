import pygame
import pygame_gui

from sophysics_engine import SimEnvironment, TimeSettings, PhysicsManager, \
    Camera, GUIManager, PygameEventProcessor
from defaults import CameraController
from .lower_panel import LowerPanel
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
    camera_controller = CameraController(
        camera,
        pygame.Rect(config["cameraControllerCfg"]["rect"]),
        config["cameraControllerCfg"]["hold_time"],
        config["cameraControllerCfg"]["zoom_strength"],
        config["cameraControllerCfg"]["min_camera_scale"])

    time_control_panel = LowerPanel(config["timeControlPanelCfg"])

    env = SimEnvironment((), (
        time_settings, physics_manager, camera, gui_manager_component,
        event_processor, time_control_panel, camera_controller
    ))

    return env
