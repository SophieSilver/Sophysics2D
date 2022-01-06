from .clickable import Clickable
from sophysics_engine import Camera
import pygame


class CircleClickable(Clickable):
    def __init__(self, camera: Camera,
                 radius: float,
                 rect: pygame.Rect,
                 button: int = 1,
                 min_pixel_radius: int = 0,
                 hold_time = 0):
        """
        :param radius: radius of the object in world units
        :param min_pixel_radius: minimal radius of the object in screen units
        """
        self.__camera = camera
        self.radius = radius
        self.min_pixel_radius = min_pixel_radius

        super().__init__(rect, button, hold_time)

    def _mouse_on_object(self):
        # doing squared distances since it's less computationally intensive than doing square roots
        screen_radius_squared = max(self.radius * self.__camera.pixels_per_unit, self.min_pixel_radius)**2
        screen_position = pygame.Vector2(self.__camera.world_to_screen(self.sim_object.transform.position))
        mouse_position = pygame.Vector2(pygame.mouse.get_pos())

        # distance between the mouse and the object
        distance_squared = screen_position.distance_squared_to(mouse_position)

        return distance_squared <= screen_radius_squared
