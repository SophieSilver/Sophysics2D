import pygame
import pygame_gui

from sophysics_engine import GUIPanel
from typing import Dict


class UpperPanel(GUIPanel):
    def __init__(self, config: Dict):
        self.__config = config

        super().__init__()

    @property
    def is_enabled(self) -> bool:
        return self.__panel.is_enabled

    @is_enabled.setter
    def is_enabled(self, value: bool):
        if value:
            self.__panel.enable()
            self.__panel.show()
        else:
            self.__panel.disable()
            self.__panel.hide()

    def _setup_ui(self):
        self.__create_panel()
        self.__create_buttons()

    def __create_buttons(self):
        button_config = self.__config["buttons"]

        self.__open_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(button_config["open_rect"]),
            text="loc.open_file_button",
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        # TODO add listener

        self.__save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(button_config["save_rect"]),
            text="loc.save_file_button",
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        # TODO add listener

    def __create_panel(self):
        self.__panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(self.__config["rect"]),
            starting_layer_height=self.__config["starting_layer_height"],
            manager=self._pygame_gui_manager
        )