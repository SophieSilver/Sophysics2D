"""
Contains the crucial to the simulation classes like SimEnvironment and SimObject
"""
from __future__ import annotations

import pygame

from .component import Component
from .component_container import ComponentContainer
from .event_system import EventSystem, Event
from abc import ABC
from typing import Iterable, Set, Optional, Sequence


class SimEnvironment(ComponentContainer):
    """
    A container for SimObjects and EnvironmentComponents.
    """
    def __init__(self, sim_objects: Iterable[SimObject] = (),
                 components: Iterable[EnvironmentComponent] = ()):
        # When subclassing, make sure that the super().__init__() is at the end,
        # so that _setup() is being called at the correct time

        # A flag that tells whether the setup() method has been called
        self._is_set_up = False
        self.sim_objects: Set[SimObject] = set()

        # a set of sim_objects
        # that have to be destroyed at the end of the time step
        self._to_be_destroyed: Set[SimObject] = set()

        self.__event_system: EventSystem = EventSystem()

        for o in sim_objects:
            self.attach_sim_object(o)

        super().__init__(components)
        self._setup()

    @property
    def event_system(self) -> EventSystem:
        """
        The environment's event system
        """
        return self.__event_system

    @property
    def is_set_up(self) -> bool:
        """
        A flag that says whether the environment has been set up or not
        """
        return self._is_set_up

    @property
    def to_be_destroyed_sim_objects(self) -> Set[SimObject]:
        return self._to_be_destroyed

    def attach_sim_object(self, sim_object: SimObject):
        """
        Attaches a sim object to the environment.
        """
        sim_object.attach_environment(self)
        self.sim_objects.add(sim_object)

        if self._is_set_up:
            for component in sim_object.components:
                component.setup()

    def remove_sim_object(self, sim_object: SimObject):
        """
        Removes the sim_object from the environment
        """
        sim_object.remove_environment()
        self.sim_objects.remove(sim_object)

    # overriding a method to connect the component to self
    def attach_component(self, component: EnvironmentComponent):
        """
        Attaches a component to the environment.
        """
        component.attach_environment(self)
        super().attach_component(component)

        if self._is_set_up:
            component.setup()

    def remove_component(self, component: EnvironmentComponent):
        component.remove_environment()
        super().remove_component(component)

    def _setup(self):
        """
        Calls setup() on all environment components and sim object components.
        """
        for env_component in self.components:
            env_component.setup()

        for sim_object in self.sim_objects:
            for component in sim_object.components:
                component.setup()

        self._is_set_up = True

    def destroy_after_step(self, sim_object: SimObject):
        """
        Schedule the sim_object to be destroyed at the end of the current step
        """
        self._to_be_destroyed.add(sim_object)

    def _destroy_marked_sim_objects(self):
        for o in self._to_be_destroyed:
            o.destroy()

        self._to_be_destroyed.clear()

    def advance(self):
        """
        Advance 1 step forward.
        """
        self.event_system.raise_event(AdvanceTimeStepEvent())
        self._destroy_marked_sim_objects()

    def update(self):
        """
        Called after the physics update and before the environment is rendered
        """
        self.event_system.raise_event(EnvironmentUpdateEvent())

    def render(self):
        """
        Renders the current state of the simulation
        """
        self.event_system.raise_event(RenderEvent())

    def destroy(self):
        """
        Destroys the environment and all its components and sim_objects
        """
        for sim_object in self.sim_objects.copy():
            sim_object.destroy()

        for component in self.components.copy():
            component.destroy()

        self.event_system.clear_listeners()


class SimObject(ComponentContainer):
    """
    A container for SimObject Components. Must have a Transform
    """
    def __init__(self, tag: str = "", components: Iterable[SimObjectComponent] = ()):
        self._environment: Optional[SimEnvironment] = None
        self.__tag: str = tag
        super().__init__(components)

        self._transform: Optional[Transform] = self.try_get_component(Transform)

        if (self._transform is None):
            self._transform = Transform()
            self.attach_component(self.transform)

    @property
    def environment(self) -> SimEnvironment:
        """
        A reference to the environment this sim object is attached to
        """
        return self._environment

    def attach_environment(self, environment: SimEnvironment):
        """
        Attaches an environment reference to the sim object
        """
        if not isinstance(environment, SimEnvironment):
            raise TypeError("'environment' must be an instance of 'SimEnvironment'")

        self._environment = environment

    def remove_environment(self):
        """
        removes the environment reference from the sim object
        """
        self._environment = None

    @property
    def tag(self) -> str:
        return self.__tag

    @tag.setter
    def tag(self, value: str):
        self.__tag = value

    @property
    def transform(self) -> Transform:
        return self._transform

    # overriding a method to connect the component to self
    def attach_component(self, component: SimObjectComponent):
        """
        Attaches component to the object
        """
        component.attach_sim_object(self)
        super().attach_component(component)

        if self.environment is not None and self.environment.is_set_up:
            component.setup()

    def remove_component(self, component: SimObjectComponent):
        component.remove_sim_object()
        super().remove_component(component)

    def destroy(self):
        """
        used to destroy the simobject

        Calling this yourself method is not recommended, instead use environment.destroy_after_step() to
        ensure no errors with referencing destroyed objects
        """
        for c in self.components:
            c.destroy()

        self.components.clear()
        self.environment.remove_sim_object(self)


class EnvironmentComponent(Component, ABC):
    """
    The base class for environment components.
    """
    def __init__(self):
        # a reference to the environment
        self._environment: Optional[SimEnvironment] = None
        super().__init__()

    @property
    def environment(self):
        """
        The environment this component is attached to
        """
        return self._environment

    def attach_environment(self, environment: SimEnvironment):
        """
        Attaches an environment reference to the component
        """
        if not isinstance(environment, SimEnvironment):
            raise TypeError("'environment' must be an instance of 'SimEnvironment'")

        self._environment = environment

    def remove_environment(self):
        """
        removes the environment reference from the component
        """
        self._environment = None

    def _on_destroy(self):
        self.environment.remove_component(self)

    def _after_destroy(self):
        self.remove_environment()


class SimObjectComponent(Component, ABC):
    """
    The base class for SimObject components
    """
    def __init__(self):
        self._sim_object: Optional[SimObject] = None
        super().__init__()

    @property
    def sim_object(self) -> SimObject:
        """
        A reference to the sim_object that the component is attached to
        """
        return self._sim_object

    def attach_sim_object(self, sim_object: SimObject):
        """
        Attach a sim_object reference to the component
        """
        if not isinstance(sim_object, SimObject):
            raise TypeError("'sim_object' must be an instance of 'SimObject'")

        self._sim_object = sim_object

    def remove_sim_object(self):
        """
        removes the sim_object reference from the component
        """
        self._sim_object = None

    def _on_destroy(self):
        self.sim_object.remove_component(self)

    def _after_destroy(self):
        self.remove_sim_object()


class Transform(SimObjectComponent):
    """
    Holds information about position and rotation of the object.
    """
    def __init__(self, position: pygame.Vector2 = None,
                 rotation: float = 0):
        if(position is None):
            position = pygame.Vector2()
        self._position: pygame.Vector2 = position
        self.rotation: float = rotation
        super().__init__()

    @property
    def position(self) -> pygame.Vector2:
        return self._position

    @position.setter
    def position(self, value: Sequence[float]):
        self._position.x = value[0]
        self._position.y = value[1]


class RenderEvent(Event):
    """
    An event that's raised by the environment when it renders the current
    state of the simulation on the screen
    """


class AdvanceTimeStepEvent(Event):
    """
    An event that's raised when the environment advances 1 step forward.
    """


class EnvironmentUpdateEvent(Event):
    """
    Raised when the environment updates
    """
