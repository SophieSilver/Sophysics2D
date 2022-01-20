from defaults import Clickable, CircleRenderer
from sophysics_engine import Camera
import pygame
from typing import Dict, Optional
from .celestial_body import get_celestial_body


class BodyCreator(Clickable):
    """
    A special object that creates objects with particular parameters when you click
    """
    def __init__(self, rect: pygame.Rect, camera: Camera, body_parameters: Dict, body_config: Dict,
                 is_enabled: bool = True, alpha: int = 128, button: int = 1, hold_time: float = 0):
        self.__body_parameters = body_parameters
        self.__body_config = body_config
        self.__is_enabled = is_enabled

        self.__alpha = 0
        self.alpha = alpha

        self.__rect = rect

        self.__camera = camera
        self.__renderer: Optional[CircleRenderer] = None

        super().__init__(button, hold_time)

    @property
    def is_enabled(self) -> bool:
        return self.__is_enabled

    @is_enabled.setter
    def is_enabled(self, value: bool):
        self.__is_enabled = value
        self.__renderer.is_active = value

    @property
    def body_config(self) -> Dict:
        return self.__body_config

    @property
    def body_parameters(self) -> Dict:
        return self.__body_parameters

    @property
    def alpha(self) -> int:
        return self.__alpha

    @alpha.setter
    def alpha(self, value: int):
        if not (0 <= value <= 255):
            raise ValueError("alpha must be between 0 and 255")

        self.__alpha = value

    def refresh_parameters(self):
        """
        Changes the color and radius of the creator according to the parameters
        """
        self.__renderer.radius = self.__body_parameters["radius"]
        self.__renderer.min_pixel_radius = self.__body_parameters["min_screen_radius"]

        self.__renderer.color = pygame.Color(self.__body_parameters["color"])
        self.__renderer.color.a = self.__alpha

    def _clickable_start(self):
        self.__renderer = self.sim_object.get_component(CircleRenderer)
        self.__renderer.is_active = self.is_enabled
        self.refresh_parameters()

    def _clickable_update(self):
        if not self.is_enabled:
            return

        if not self._mouse_inside_the_rect():
            # don't render is not inside the rect
            self.__renderer.is_active = False
            return

        # to undo the change made in previous if block
        self.__renderer.is_active = True

        # set the position to whenever the mouse is
        screen_pos = pygame.mouse.get_pos()
        world_pos = pygame.Vector2(self.__camera.screen_to_world(screen_pos))

        self.sim_object.transform.position = world_pos

    def _mouse_on_object(self) -> bool:
        # don't want to fire on_click methods and consume events when not enabled
        return self.__is_enabled

    def _mouse_inside_the_rect(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        return self.__rect.collidepoint(mouse_pos)

    def _on_click(self):
        body = get_celestial_body(
            config=self.__body_config,
            initial_position=list(self.sim_object.transform.position),
            initial_velocity=[0, 0],
            camera=self.__camera,
            **self.__body_parameters
        )
        self.sim_object.environment.attach_sim_object(body)

    def _clickable_end(self):
        self.__renderer = None
