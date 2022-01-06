"""
A little component that pauses and unpauses the simulation when the user presses spacebar
"""
from sophysics_engine import PygameEvent, EnvironmentComponent, TimeSettings
from typing import Optional
import pygame


class PauseOnSpacebar(EnvironmentComponent):
    def __init__(self):
        super().__init__()
        self.__time_settings: Optional[TimeSettings] = None

    def setup(self):
        self.__time_settings = self.environment.get_component(TimeSettings)
        self.environment.event_system.add_listener(PygameEvent, self.__handle_pygame_event)

    def __handle_pygame_event(self, event: PygameEvent):
        pygame_event = event.pygame_event

        if pygame_event.type != pygame.KEYDOWN or pygame_event.key != pygame.K_SPACE:
            return

        self.__time_settings.paused = not self.__time_settings.paused

        event.consume()

    def _on_destroy(self):
        self.environment.event_system.remove_listener(PygameEvent, self.__handle_pygame_event)
