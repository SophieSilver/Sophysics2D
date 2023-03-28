"""

"""
from sophysics_engine import Camera, EnvironmentComponent, UnpauseEvent, TimeSettings

from . import save_simulation
from .simulation_loader import SimulationLoader

from typing import Optional


class RevertSimulation(EnvironmentComponent):
    def __init__(self):
        self.__simulation_backup = None

        self.__time_settings: Optional[TimeSettings] = None
        self.__simulation_loader: Optional[SimulationLoader] = None
        self.__camera: Optional[Camera] = None

        super().__init__()

    def setup(self):
        self.__time_settings = self.environment.get_component(TimeSettings)
        self.__simulation_loader = self.environment.get_component(SimulationLoader)
        self.__camera = self.environment.get_component(Camera)

        self.environment.event_system.add_listener(UnpauseEvent, self.__handle_unpause_event)

    def __handle_unpause_event(self, _: UnpauseEvent):
        self.__simulation_backup = save_simulation.get_simulation_dict(self.environment, self.__camera)

    def revert(self):
        if self.__simulation_backup is None:
            return
        self.__simulation_loader.load_from_dict(self.__simulation_backup)
        self.__time_settings.paused = True
        self.__simulation_backup = None

