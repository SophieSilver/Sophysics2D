import pygame

from typing import Sequence, Union, Optional
from sophysics_engine import Force


number = Union[int, float]


class ConstantAcceleration(Force):
    """
    A force that accelerates the body a certain amount of units per second. Could be used to simulate the
    acceleration due to gravity.
    """
    def __init__(self, acceleration: Sequence[number] = (0, 0)):
        """
        acceleration must be a sequence with at least 2 items, e.g. pygame.Vector2, pymunk.Vec2d, a tuple, a list or
        any user defined type that has a __getitem__ method and at least 2 items.

        The first two items represent the x and y components of the acceleration respectively. Any subsequent items
        are ignored.

        Under the hood the acceleration is represented as pygame.Vector2
        """
        super().__init__()

        self._acceleration: Optional[pygame.Vector2] = None
        self.acceleration = acceleration

    @property
    def acceleration(self) -> pygame.Vector2:
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value: Sequence[number]):
        """
        acceleration must be a sequence with at least 2 items, e.g. pygame.Vector2, pymunk.Vec2d, a tuple, a list or
        any user defined type that has a __getitem__ method and at least 2 items.

        The first two items represent the x and y components of the acceleration respectively. Any subsequent items
        are ignored.

        Under the hood the acceleration is represented as pygame.Vector2
        """
        x, y, *_ = value
        del _

        self._acceleration = pygame.Vector2(x, y)

    def exert(self):
        """
        Exerts the force onto the rigidbody
        """
        # applies the force that causes a particular acceleration
        # From the Newton's second law
        # F = m * a
        mass = self._rigidbody.mass
        force = mass * self._acceleration

        self._rigidbody.apply_force(force)
