"""
A thing that would update the environment with one method
"""


from abc import ABC, abstractmethod
from .simulation import SimEnvironment


class EnvironmentUpdater(ABC):
    """
    An abstract strategy class that updates the environment
    """

    def __init__(self, environment: SimEnvironment):
        self._environment: SimEnvironment = environment

    @abstractmethod
    def update(self):
        pass
