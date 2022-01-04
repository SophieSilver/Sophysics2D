from .simulation import EnvironmentComponent, EnvironmentUpdateEvent


class GlobalBehavior(EnvironmentComponent):
    """
    Same as MonoBehavior, but for the entire environment
    """
    def setup(self):
        super().setup()
        self.environment.event_system.add_listener(EnvironmentUpdateEvent, self.__handle_update_event)
        self._start()

    def __handle_update_event(self, _: EnvironmentUpdateEvent):
        self._update()

    def _start(self):
        """
        Called once the component was added to the simulation
        """
        pass

    def _update(self):
        """
        Called every frame
        """
        pass

    def _end(self):
        """
        Gets called when the component is destroyed
        """
        pass

    def _on_destroy(self):
        self._end()
        self.environment.event_system.remove_listener(EnvironmentUpdateEvent, self.__handle_update_event)

