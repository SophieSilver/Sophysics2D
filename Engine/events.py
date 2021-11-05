"""
Different types of events
"""
from __future__ import annotations
from abc import ABC


class Event(ABC):
    """
    An abstract base class for events.
    """
    # This is an empty class, subclasses might have additional data
    pass


class RigidBodySyncBodyWithSimObjectEvent(Event):
    pass


class RigidBodySyncSimObjectWithBodyEvent(Event):
    pass


class RigidBodyExertForcesEvent(Event):
    pass


# TODO put into rendering file after refactoring stuff
class RenderSceneEvent(Event):
    def __init__(self, render_manager):
        self.__render_manager = render_manager

    @property
    def render_manager(self):
        return self.__render_manager

