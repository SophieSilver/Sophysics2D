"""
The event system of Sophysics2D
"""
from __future__ import annotations
from events import *
from weakref import WeakSet
from typing import *


event_listener_function = Callable[[Event], None]


class EventSystem:
    """
    An event system that is responsible for handling events by calling listeners of an event each time it's raised
    """
    def __init__(self):
        self.__listeners: dict[type, WeakSet[event_listener_function]] = {}

    def add_listener(self, event_type: type, listener: Callable):
        """
        Adds the given listener function that gets called every time an event of a given type is raised
        """
        if not isinstance(listener, Callable):
            raise TypeError("the 'listener' argument must be callable")

        if event_type not in self.__listeners:
            self.__listeners[event_type] = WeakSet()

        self.__listeners[event_type].add(listener)

    def remove_listener(self, event_type: type, listener: Callable):
        """
        Removes the given listener function from the listeners of the given event type.
        """
        self.__listeners[event_type].remove(listener)

    def raise_event(self, event: Event):
        """
        Raises and event, which subsequently calls all of it's listeners
        """
        event_type = type(event)
        # terminate method if there are no listeners for this event type
        if event_type not in self.__listeners:
            return

        for listener in self.__listeners[event_type]:
            listener(event)
