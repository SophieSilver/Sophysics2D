"""
Some hard-coded QOL keyboard shortcuts.
- areit
"""

from .selection import GlobalSelection, BodyController
from . import utils

from sophysics_engine import PygameEvent, EnvironmentComponent
import pygame


class KeyboardShortcuts(EnvironmentComponent):
    def __init__(self):
        super().__init__()
        # self.__time_settings: Optional[TimeSettings] = None

    def setup(self):
        # self.__time_settings = self.environment.get_component(TimeSettings)
        self.environment.event_system.add_listener(PygameEvent, self.__handle_pygame_event)

    def __handle_pygame_event(self, event: PygameEvent):
        pygame_event = event.pygame_event

        selected_object: BodyController = self.environment.get_component(GlobalSelection).selected_body

        if pygame_event.type != pygame.KEYDOWN or pygame_event.key != pygame.K_DELETE:
            return

        utils.delete_body(self.environment, selected_object)

        event.consume()

    def _on_destroy(self):
        self.environment.event_system.remove_listener(PygameEvent, self.__handle_pygame_event)


    #def hotkey_delete_object(self):

