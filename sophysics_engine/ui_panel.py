from typing import Optional
from .simulation import EnvironmentComponent, EnvironmentUpdateEvent
from .gui_manager import GUIManager
import pygame_gui


class GUIPanel(EnvironmentComponent):
    """
    A base class that's aimed at making ui panels easier
    """
    def __init__(self):
        # this one is the env component
        self._ui_manager: Optional[GUIManager] = None
        # and this one is the pygame_GUI object
        self._pygame_gui_manager: Optional[pygame_gui.UIManager] = None
        # we will set them later on setup()

        super().__init__()

    def setup(self):
        self.environment.event_system.add_listener(EnvironmentUpdateEvent, self.__handle_update_event)

        self._ui_manager: GUIManager = self.environment.get_component(GUIManager)
        self._pygame_gui_manager = self._ui_manager.ui_manager

        super().setup()

        self._setup_ui()

    def __handle_update_event(self, _: EnvironmentUpdateEvent):
        self._update_ui()

    def _setup_ui(self):
        """
        method that actually sets up the ui
        """
        pass

    def _update_ui(self):
        """
        Called every frame
        """
        pass

    def _on_destroy(self):
        self.environment.event_system.remove_listener(EnvironmentUpdateEvent, self.__handle_update_event)
