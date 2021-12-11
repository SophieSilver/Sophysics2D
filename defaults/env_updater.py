from sophysics_engine import EnvironmentUpdater, SimEnvironment, TimeSettings


class DefaultUpdater(EnvironmentUpdater):
    """
    A default updater that advances a step and renders the scene
    """
    def __init__(self, environment: SimEnvironment):
        super().__init__(environment)
        self.__time_settings: TimeSettings = self._environment.get_component(TimeSettings)

    def update(self):
        if not self.__time_settings.paused:
            for _ in range(self.__time_settings.steps_per_frame):
                self._environment.advance()

        self._environment.render()
