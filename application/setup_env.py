import pygame
import pygame_gui

from sophysics_engine import SimEnvironment, TimeSettings, PhysicsManager, \
    Camera, GUIManager, PygameEventProcessor, SimObject
from defaults import CameraController, PauseOnSpacebar, \
    AttractionManager, ClickableManager, CircleRenderer
from .keyboard_shortcuts import KeyboardShortcuts
from .lower_panel import LowerPanel
from .selection import GlobalSelection
from .velocity_controller import VelocityController
from .reference_frame import ReferenceFrameManager, ReferenceFrameCameraAdjuster
from .upper_panel import UpperPanel
from .side_panel import SidePanel
from .body_creator import BodyCreator
from .simulation_loader import SimulationLoader
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

    clickable_manager_config = config["clickableManagerCfg"]
    clickable_manager = ClickableManager(pygame.Rect(clickable_manager_config["rect"]))

    selection_config = config["globalSelectionCfg"]
    global_selection = GlobalSelection(
        button=selection_config["button"],
        hold_time=selection_config["hold_time"]
    )

    vel_controller_config = config["velocityControllerCfg"]
    vel_controller = VelocityController(
        camera=camera,
        scale_factor=vel_controller_config["scale_factor"],
        button=vel_controller_config["button"],
        hold_time=vel_controller_config["hold_time"]
    )

    time_control_panel = LowerPanel(config["timeControlPanelCfg"])

    reference_frame_manager = ReferenceFrameManager()
    camera_adjuster = ReferenceFrameCameraAdjuster(camera)

    upper_panel = UpperPanel(config["upperPanelCfg"])

    body_creator_config = config["bodyCreatorCfg"]
    body_creator_component = BodyCreator(
        rect=pygame.Rect(body_creator_config["rect"]),
        camera=camera,
        body_config=config["celestialBodyCfg"],
        body_parameters=body_creator_config["default_body"],
        is_enabled=True,    # this doesn't matter
        alpha=body_creator_config["alpha"],
        button=body_creator_config["button"],
        hold_time=body_creator_config["hold_time"],
    )
    body_creator_renderer = CircleRenderer(layer=body_creator_config["layer"])
    body_creator_object = SimObject("body creator", (body_creator_component,  body_creator_renderer))

    sim_loader = SimulationLoader(config["celestialBodyCfg"], camera)

    pause_on_spacebar = PauseOnSpacebar()
    keyboard_shortcuts = KeyboardShortcuts()

    env = SimEnvironment((), (
        time_settings, physics_manager, camera, gui_manager_component,
        event_processor, time_control_panel, camera_controller, pause_on_spacebar, keyboard_shortcuts,
        attraction_manager, global_selection, vel_controller, reference_frame_manager,
        camera_adjuster, clickable_manager, upper_panel, sim_loader
    ))

    env.attach_sim_object(body_creator_object)

    side_panel = SidePanel(config["sidePanelCfg"], body_creator_component)
    env.attach_component(side_panel)

    return env
