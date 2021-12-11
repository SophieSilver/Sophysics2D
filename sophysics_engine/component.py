"""
A component allows us to attach functionality to different objects (ComponentContainers)
"""

from __future__ import annotations
from abc import ABC, abstractmethod


class Component(ABC):
    """
    The base class for Components
    """
    def __init__(self):
        self._is_set_up: bool = False

    @property
    def is_set_up(self) -> bool:
        """
        A flag that tells whether the setup method has been called
        """
        return self._is_set_up

    def setup(self):
        """
        Called when the simulation sets up the component.

        A use case example: get references to all necessary components, managers, etc.

        When subclassing, add super().setup() to set the self._is_set_up to True
        """
        self._is_set_up = True

    def destroy(self):
        """
        Destroy the component
        """
        self._on_destroy()
        self._after_destroy()

    def _on_destroy(self):
        """
        Gets called when the object to which the component is attached to is destroyed

        Used to release all the references so that the GC can free the memory
        """

    @abstractmethod
    def _after_destroy(self):
        """
        Detaches the component from the environment or sim object
        """
