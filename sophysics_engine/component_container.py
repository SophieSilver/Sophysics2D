"""
A special object that you can attach different components (behaviors) to
"""
from __future__ import annotations
from abc import ABC
from .component import Component
from typing import Iterable, Set, Any, List


class ComponentContainer(ABC):
    """
    The base class for Component containers such as SimObject and SimEnvironment.
    """
    def __init__(self, components: Iterable[Component] = ()):
        self.components: Set[Component] = set()

        for c in components:
            self.attach_component(c)

    def attach_component(self, component: Component):
        """
        Attaches component to the object.

        Supposed to be overridden in order to connect the component to the container
        """
        # an override method would add something like this
        # component.sim_object = self
        if(not isinstance(component, Component)):
            raise TypeError("component must be of type Component")

        self.components.add(component)

    def remove_component(self, component: Component):
        """
        Removes the component from the container
        """
        self.components.remove(component)

    def get_component(self, comp_type: type) -> Any:
        """
        Returns the first component of a specified type.

        If the component isn't found raises ValueError
        """
        component = self.try_get_component(comp_type)
        if component is not None:
            return component

        raise ValueError(f"component {comp_type} not found")

    def get_components(self, comp_type: type) -> List[Any]:
        """
        Returns a list of all components of a specified type.

        If no components were found returns an empty list.
        """
        components = [c for c in self.components if isinstance(c, comp_type)]
        return components

    def try_get_component(self, comp_type: type) -> Any:
        """
        Returns a component of a specified type or None if the component wasn't found.
        """
        component = None
        for c in self.components:
            if(isinstance(c, comp_type)):
                component = c
                break

        return component

    def has_component(self, comp_type: type) -> bool:
        """
        Checks if the object has a component of a specified type.
        """
        return (self.try_get_component(comp_type) is not None)
