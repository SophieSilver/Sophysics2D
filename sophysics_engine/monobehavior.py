from .simulation import SimObjectComponent, EnvironmentUpdateEvent


class MonoBehavior(SimObjectComponent):
    """
    A base class for various scripts
    """
    def setup(self):
        super().setup()
        self.sim_object.environment.event_system.add_listener(EnvironmentUpdateEvent, self.__handle_update_event)
        self._start()

    def __handle_update_event(self, _: EnvironmentUpdateEvent):
        self._update()

    def _start(self):
        """
        Called once the object was added to the simulation
        """
        pass

    def _update(self):
        """
        Called every frame
        """
        pass

    def _end(self):
        """
        Gets called when the object is destroyed
        """
        pass

    def _on_destroy(self):
        self._end()
        self.sim_object.environment.event_system.remove_listener(EnvironmentUpdateEvent, self.__handle_update_event)

