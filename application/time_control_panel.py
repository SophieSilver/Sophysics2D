import pygame

from sophysics_engine import GUIPanel, TimeSettings
from typing import Dict
import pygame_gui


class TimeControlPanel(GUIPanel):
    def __init__(self, config: Dict):
        self.__config = config

        super().__init__()

    @property
    def is_enabled(self):
        return self.__panel.is_enabled

    def _setup_ui(self):
        self.__time_settings: TimeSettings = self.environment.get_component(TimeSettings)
        self.__create_panel()
        self.__create_pause_button()
        self.__create_timestep_controls()

    def __create_timestep_controls(self):
        local_config = self.__config["dtControlCfg"]

        self.__timestep_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["labelRect"]),
            text="loc.timestep_label",
            manager=self._pygame_gui_manager,
            container=self.__panel
        )

        self.__timestep_text_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(local_config["textboxRect"]),
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        self.__timestep_text_box.allowed_characters = ".-+0123456789E"
        self._ui_manager.add_callback(
            pygame_gui.UI_TEXT_ENTRY_CHANGED,
            self.__timestep_text_box,
            self.__pause_the_simulation
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_TEXT_ENTRY_FINISHED,
            self.__timestep_text_box,
            self.__on_timestep_changed
        )
        self.__update_timestep_textbox()
        # the buttons
        self.__fast_forward_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(local_config["fasterButtonRect"]),
            text="2x▶▶",
            manager=self._pygame_gui_manager,
            container=self.__panel,
            tool_tip_text="loc.timestep_tooltip"
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_BUTTON_PRESSED,
            self.__fast_forward_button,
            self.__increase_timestep
        )

        self.__slow_down_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(local_config["slowerButtonRect"]),
            text="◀◀1/2x",
            manager=self._pygame_gui_manager,
            container=self.__panel,
            tool_tip_text="loc.timestep_tooltip"
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_BUTTON_PRESSED,
            self.__slow_down_button,
            self.__decrease_timestep
        )

    def __decrease_timestep(self):
        self.__time_settings.dt /= 2
        self.__update_timestep_textbox()

    def __increase_timestep(self):
        self.__time_settings.dt *= 2
        self.__update_timestep_textbox()

    def __on_timestep_changed(self):
        text = self.__timestep_text_box.text

        try:
            new_dt = float(text)
            assert new_dt >= 0.0
            self.__time_settings.dt = new_dt
        except ValueError or AssertionError:
            self.__timestep_text_box.set_text(str(self.__time_settings.dt))

    def __pause_the_simulation(self):
        self.__time_settings.paused = True

    def __update_timestep_textbox(self):
        self.__timestep_text_box.set_text(str(self.__time_settings.dt))

    def __create_panel(self):
        self.__panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(self.__config["rect"]),
            starting_layer_height=self.__config["starting_layer_height"],
            manager=self._pygame_gui_manager
        )

    def __create_pause_button(self):
        button_config = self.__config["pauseButtonCfg"]

        self.__pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(button_config["rect"]),
            text="font test",
            manager=self._pygame_gui_manager,
            container=self.__panel,
            object_id="#pause_button"
        )
        # add callback
        self._ui_manager.add_callback(
            pygame_gui.UI_BUTTON_PRESSED,
            self.__pause_button,
            self.__pause_button_click
        )

    def __pause_button_click(self):
        self.__time_settings.paused = not self.__time_settings.paused
        # self.__update_pause_button()

    def __update_pause_button(self):
        if self.__is_pause_button_text_correct():
            return

        self.__pause_button.set_text("▶" if self.__time_settings.paused else "▮▮")

    def __is_pause_button_text_correct(self) -> bool:
        return (self.__pause_button.text == "▶" and self.__time_settings.paused) or \
               (self.__pause_button.text == "▮▮" and not self.__time_settings.paused)

    def _update_ui(self):
        self.__update_pause_button()
