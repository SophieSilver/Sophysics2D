from .simulation import EnvironmentComponent
from .event import Event
from typing import Union


number = Union[int, float]


class PauseEvent(Event):
    pass


class UnpauseEvent(Event):
    pass


class TimeSettings(EnvironmentComponent):
    def __init__(self, dt: number = 1 / 60, steps_per_frame: int = 1, paused: bool = False):
        self.dt = dt
        self.steps_per_frame = steps_per_frame
        self.__paused = paused

        super().__init__()

    @property
    def paused(self) -> bool:
        return self.__paused

    @paused.setter
    def paused(self, value: bool):
        self.__paused = value
        if value:
            self.environment.event_system.raise_event(PauseEvent())
        else:
            self.environment.event_system.raise_event(UnpauseEvent())

