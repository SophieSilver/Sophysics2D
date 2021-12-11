from .simulation import EnvironmentComponent
from typing import Union


number = Union[int, float]


class TimeSettings(EnvironmentComponent):
    def __init__(self, dt: number = 1 / 60, steps_per_frame: int = 1, paused: bool = False):
        self.dt = dt
        self.steps_per_frame = steps_per_frame
        self.paused = paused

        super().__init__()
