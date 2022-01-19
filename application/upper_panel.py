import pygame
import pygame_gui

from sophysics_engine import GUIPanel, Camera
from .simulation_loader import SimulationLoadEvent
from .save_simulation import save_simulation_to_json
from typing import Dict
import tkinter.filedialog


class UpperPanel(GUIPanel):
    def __init__(self, config: Dict):
        self.__config = config

        # hide the tkinter root window
        tkinter.Tk().withdraw()

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
        self._ui_manager.add_callback(
            event_type=pygame_gui.UI_BUTTON_PRESSED,
            element=self.__open_button,
            callback=self.__on_open_file_button_click
        )

        self.__save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(button_config["save_rect"]),
            text="loc.save_file_button",
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        self._ui_manager.add_callback(
            event_type=pygame_gui.UI_BUTTON_PRESSED,
            element=self.__save_button,
            callback=self.__on_save_file_button_click
        )

    def __on_save_file_button_click(self):
        filepath = tkinter.filedialog.asksaveasfilename(confirmoverwrite=True,
                                                        defaultextension=".json",
                                                        filetypes=[("JSON", "*.json")])

        if filepath == "":
            return

        save_simulation_to_json(filepath, self.environment, self.environment.get_component(Camera))

    def __on_open_file_button_click(self):
        filepath = tkinter.filedialog.askopenfilename(filetypes=[("JSON", "*.json")], initialdir="saves")

        # if the user pressed cancel
        if filepath == "":
            return

        self.environment.event_system.raise_event(SimulationLoadEvent(filepath))

    def __create_panel(self):
        self.__panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(self.__config["rect"]),
            starting_layer_height=self.__config["starting_layer_height"],
            manager=self._pygame_gui_manager
        )
