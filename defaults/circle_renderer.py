import pygame
import pygame.gfxdraw

from sophysics_engine import Renderer, Camera, Color
from typing import Union


number = Union[int, float]


class CircleRenderer(Renderer):
    """
    Renderer for circles
    """
    # maybe add stuff like stroke width stroke and fill colors, etc, whatever, probably not this year
    def __init__(self, radius: Union[int, float] = 1, min_pixel_radius: int = 0, color = Color.WHITE, layer: int = 0):
        """
        :param radius: object's radius in world coordinates
        """
        self.__world_radius: float = 0
        self.min_pixel_radius = min_pixel_radius
        self.radius: float = radius

        super().__init__(color, layer)

    @property
    def radius(self) -> float:
        """
        Radius of the circle in world coordinates.
        """
        return self.__world_radius

    @radius.setter
    def radius(self, value: number):
        self.__world_radius = value

    def get_pixel_radius(self, camera: Camera) -> float:
        """
        Radius of the circle in pixels on the screen
        """
        return max(self.__world_radius * camera.pixels_per_unit, self.min_pixel_radius)

    def render(self, surface: pygame.Surface, camera: Camera):
        world_position = self.sim_object.transform.position
        screen_position = camera.world_to_screen(world_position)

        # pygame.draw.circle(surface, self.color, screen_position, self.get_pixel_radius(camera))

        x, y = map(int, screen_position)
        radius = int(self.get_pixel_radius(camera))
        # the first method draws an unfilled anti-aliased circumference,
        # the seconds draws the filled circle inside of it
        pygame.gfxdraw.aacircle(surface, x, y, radius, self.color)
        pygame.gfxdraw.filled_circle(surface, x, y, radius, self.color)
