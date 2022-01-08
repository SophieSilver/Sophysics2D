from __future__ import annotations

from sophysics_engine import Force, EnvironmentComponent
from typing import Optional, Set
import pygame


class AttractionManager(EnvironmentComponent):
    def __init__(self, attraction_coefficient: float):
        self.attraction_coefficient = attraction_coefficient
        self.__attractors: Set[Attraction] = set()

        super().__init__()

    @property
    def attractors(self) -> Set[Attraction]:
        return self.__attractors

    def add_attractor(self, attractor: Attraction):
        self.__attractors.add(attractor)

    def remove_attractor(self, attractor: Attraction):
        self.__attractors.remove(attractor)


class Attraction(Force):
    """
    Applies the gravitational attraction force to the body according to the Newton's law of gravitation
    """
    def __init__(self, is_attractor: bool = True):
        """
        :param is_attractor: whether this object generates its own attraction field.
        """
        self.__is_attractor = is_attractor
        self.__attraction_manager: Optional[AttractionManager] = None

        super().__init__()

    def setup(self):
        super().setup()
        self.__attraction_manager: AttractionManager = self.sim_object.environment.get_component(AttractionManager)

        if self.__is_attractor:
            self.__attraction_manager.add_attractor(self)

    def exert(self):
        total_force = pygame.Vector2()

        for other in self.__attraction_manager.attractors:
            if self is other:
                continue

            this_pos = self.sim_object.transform.position
            other_pos = other.sim_object.transform.position

            # if 2 bodies happen to overlap perfectly, we skip them as to not introduce a division by 0 error
            if this_pos == other_pos:
                continue

            this_mass = self._rigidbody.mass
            other_mass = other._rigidbody.mass

            # this is more efficient than computing the actual distance (since we don't need the sqrt)
            # (we still need the sqrt later tho)
            distance_squared = this_pos.distance_squared_to(other_pos)

            coefficient = self.__attraction_manager.attraction_coefficient

            # The Newton's law of Gravitation
            # F = G * m1 * m2 / r^2
            force_scalar = coefficient * this_mass * other_mass / distance_squared

            # to find the vector of the force, multiply the scalar by the direction
            direction = (other_pos - this_pos).normalize()
            force_vector = force_scalar * direction

            total_force += force_vector

        self._rigidbody.apply_force(total_force)

    def _on_destroy(self):
        if self.__is_attractor:
            self.__attraction_manager.remove_attractor(self)

        super()._on_destroy()
