from .vector_arrow_renderer import VectorArrowRenderer
from sophysics_engine import RigidBody, Color
from typing import Optional
import pygame


class VelocityVectorRenderer(VectorArrowRenderer):
    def __init__(self, scale_factor: float = 1.0, base_radius: int = 1, arrow_width: int = 1,
                 arrow_head_length: int = 10, arrow_head_width: int = 10, color = Color.WHITE, layer: int = 0):
        self.__rigidbody: Optional[RigidBody] = None

        super(VelocityVectorRenderer, self).__init__(scale_factor, base_radius, arrow_width,
                                                     arrow_head_length, arrow_head_width, color, layer)

    def setup(self):
        self.__rigidbody = self.sim_object.get_component(RigidBody)

        super().setup()

    def get_vector(self) -> pygame.Vector2:
        return pygame.Vector2(self.__rigidbody.velocity)