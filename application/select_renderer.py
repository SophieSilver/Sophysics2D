from defaults import CircleRenderer
from sophysics_engine import Camera, Color
from typing import Union
import pygame


class SelectionRenderer(CircleRenderer):
    def __init__(self, radius: Union[int, float] = 1, min_pixel_radius: int = 0,
                 width: int = 1, color = Color.WHITE, layer: int = 0):
        self.__width = width

        super().__init__(radius, min_pixel_radius, color, layer)

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, value: int):
        if value <= 0:
            raise ValueError("width must be equal or greater than 1")

        self.__width = value

    def render(self, surface: pygame.Surface, camera: Camera):
        world_position = self.sim_object.transform.position
        screen_position = camera.world_to_screen(world_position)
        radius = self.get_pixel_radius(camera)

        pygame.draw.circle(
            surface=surface,
            color=self.color,
            center=screen_position,
            radius=radius,
            width=self.__width
        )
