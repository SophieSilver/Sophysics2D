import pygame

from sophysics_engine import GUIPanel, TimeSettings
from typing import Optional, Dict
import pygame_gui


class TimeControlPanel(GUIPanel):
    def __init__(self, config: Dict):
        self.__config = config

        self.__panel: Optional[pygame_gui.elements.UIPanel] = None
        self.__time_settings: Optional[TimeSettings] = None
        super().__init__()

    def _setup_ui(self):
        self.__time_settings: TimeSettings = self.environment.get_component(TimeSettings)

        self.__panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(self.__config["rect"]),
            starting_layer_height=self.__config["starting_layer_height"],
            manager=self._pygame_gui_manager
        )
