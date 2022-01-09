import pygame
import pygame.gfxdraw

from sophysics_engine import Renderer, Camera, Color
from abc import abstractmethod, ABC


class VectorArrowRenderer(Renderer, ABC):
    """Renders an arrow from the object's center that's equal to some vector"""
    def __init__(self, scale_factor: float = 1.0, base_radius: int = 1, arrow_width: int = 1,
                 arrow_head_length: int = 10, arrow_head_width: int = 10, color = Color.WHITE, layer: int = 0):
        self.scale_factor = scale_factor
        self.base_radius = base_radius
        self.arrow_width = arrow_width
        self.arrow_head_length = arrow_head_length
        self.arrow_head_width = arrow_head_width

        super().__init__(color, layer)

    @abstractmethod
    def get_vector(self) -> pygame.Vector2:
        """
        gets a vector that needs to be rendered
        """
        pass

    def render(self, surface: pygame.Surface, camera: Camera):
        # draw the base (circle in the middle)
        x1, y1 = map(int, camera.world_to_screen(self.sim_object.transform.position))
        pygame.gfxdraw.aacircle(surface, x1, y1, self.base_radius, self.color)
        pygame.gfxdraw.filled_circle(surface, x1, y1, self.base_radius, self.color)

        vector = self.get_vector()
        # don't draw anything else if the length of the vector is 0
        if vector.magnitude_squared() == 0:
            return

        # vector in screen coordinates
        screen_x = vector.x * camera.pixels_per_unit * self.scale_factor
        screen_y = -vector.y * camera.pixels_per_unit * self.scale_factor
        screen_vector = pygame.Vector2(screen_x, screen_y)

        start_pos = pygame.Vector2(x1, y1)
        end_pos = start_pos + screen_vector
        # drawing the actual line
        pygame.draw.line(
            surface=surface,
            color=self.color,
            start_pos=start_pos,
            end_pos=end_pos,
            width=self.arrow_width
        )

        arrow_direction = screen_vector.normalize()

        head_end_pos = end_pos
        # move the arrow head forward if the arrow is too short
        if (start_pos - head_end_pos).length_squared() < self.arrow_head_length * self.arrow_head_length:
            head_end_pos = start_pos + self.arrow_head_length * arrow_direction

        # to get the normal we just swap x and y and also invert the y
        # (you can prove that it's the normal by simplifying sin(a + 90) and cos(a + 90))
        normal = pygame.Vector2(-arrow_direction.y, arrow_direction.x)

        # get the other vertices of the head of the arrow
        vertex1 = (head_end_pos - arrow_direction * self.arrow_head_length) + normal * self.arrow_head_width / 2
        vertex2 = (head_end_pos - arrow_direction * self.arrow_head_length) - normal * self.arrow_head_width / 2

        # draw the arrow head
        pygame.draw.polygon(
            surface,
            self.color,
            (head_end_pos, vertex1, vertex2)
        )

