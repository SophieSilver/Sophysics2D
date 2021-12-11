"""
Events are similar to exceptions, the usually don't carry a lot of data.
"""

from __future__ import annotations
from abc import ABC


class Event(ABC):
    """
    An abstract base class for events.
    """
    # This is an empty class, subclasses might have additional data
    pass
