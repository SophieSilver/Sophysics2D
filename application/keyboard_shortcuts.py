"""
Some hard-coded QOL keyboard shortcuts.
- areit
"""

from .selection import GlobalSelection, BodyController
from .side_panel import SidePanel
from .revert_simulation import RevertSimulation
from . import utils

from typing import Optional

from sophysics_engine import PygameEvent, EnvironmentComponent
import pygame


class KeyboardShortcuts(EnvironmentComponent):
    def __init__(self):
        self.__global_selection: Optional[GlobalSelection] = None
        self.__revert_simulation: Optional[RevertSimulation] = None

        super().__init__()

    def setup(self):
        self.__global_selection = self.environment.get_component(GlobalSelection)
        self.__revert_simulation = self.environment.get_component(RevertSimulation)

        self.environment.event_system.add_listener(PygameEvent, self.__handle_pygame_event)

    def __handle_pygame_event(self, event: PygameEvent):
        """
        pygame_event = event.pygame_event
        if pygame_event.type != pygame.KEYDOWN or pygame_event.key != pygame.K_DELETE:
            return

        selected_object: BodyController = self.environment.get_component(GlobalSelection).selected_body
        utils.delete_body(self.environment, selected_object)

        event.consume()
        """

        pygame_event = event.pygame_event
        if pygame_event.type != pygame.KEYDOWN:
            return
        key = pygame_event.key

        # The keyboard shortcuts in question
        shortcuts = {
            pygame.K_DELETE: self.delete_selected_body,
            pygame.K_ESCAPE: self.deselect,
            pygame.K_F5:     self.revert
        }

        if key in shortcuts:
            shortcuts[key]()

    def delete_selected_body(self):
        selected_object: BodyController = self.__global_selection.selected_body
        utils.delete_body(self.environment, selected_object)

    def deselect(self):
        self.__global_selection.deselect()

        side_panel = self.environment.get_component(SidePanel)
        side_panel.disable_panels()

    def revert(self):
        self.__revert_simulation.revert()

    def _on_destroy(self):
        self.environment.event_system.remove_listener(PygameEvent, self.__handle_pygame_event)


