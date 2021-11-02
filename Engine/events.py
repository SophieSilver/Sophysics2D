"""
Different types of events
"""
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
