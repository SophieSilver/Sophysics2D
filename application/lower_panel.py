import pygame

from sophysics_engine import GUIPanel, TimeSettings, PauseEvent, UnpauseEvent
from .ui_elements import TextBox, UIElement
from typing import Dict, List
import pygame_gui
import math


class LowerPanel(GUIPanel):
    def __init__(self, config: Dict):
        self.__config = config
        self.__elements: List[UIElement] = []

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
        self.environment.event_system.add_listener(PauseEvent, self.__handle_pause_event)
        self.environment.event_system.add_listener(UnpauseEvent, self.__handle_unpause_event)

        self.__time_settings: TimeSettings = self.environment.get_component(TimeSettings)
        self.__create_panel()
        self.__create_pause_button()
        self.__create_timestep_controls()
        self.__create_language_menu()
        self.__create_timestep_per_frame_controls()

    def __create_timestep_per_frame_controls(self):
        local_config = self.__config["timestepPerFrameCfg"]
        self.__timestep_per_frame_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["labelRect"]),
            text="loc.timestep_per_frame_label",
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        textbox = TextBox(
            rect=pygame.Rect(local_config["textBoxRect"]),
            gui_manager=self._ui_manager,
            container=self.__panel,
            allowed_characters="0123456789",
            change_callback=self.__pause_simulation,
            finish_callback=self.__on_timestep_per_frame_changed,
            unpause_callback=self.__on_timestep_per_frame_changed
        )
        self.__elements.append(textbox)
        self.__timestep_per_frame_textbox = textbox.element
        self.__update_time_steps_per_frame_text_box()

        # buttons
        self.__decrease_steps_per_frame_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(local_config["decreaseButtonRect"]),
            text="-1",
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_BUTTON_PRESSED,
            self.__decrease_steps_per_frame_button,
            self.__on_steps_per_frame_decrease
        )

        self.__increase_steps_per_frame_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(local_config["increaseButtonRect"]),
            text="+1",
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_BUTTON_PRESSED,
            self.__increase_steps_per_frame_button,
            self.__on_steps_per_frame_increase
        )

    def __on_steps_per_frame_increase(self):
        self.__time_settings.steps_per_frame += 1
        self.__update_time_steps_per_frame_text_box()

    def __on_steps_per_frame_decrease(self):
        self.__time_settings.steps_per_frame -= 1
        self.__time_settings.steps_per_frame = max(0, self.__time_settings.steps_per_frame)
        self.__update_time_steps_per_frame_text_box()

    def __on_timestep_per_frame_changed(self):
        text = self.__timestep_per_frame_textbox.text

        try:
            new_steps_per_frame = int(text)
            # don't need to assert that the value is positive,
            # coz that's pretty much only values you can input
            self.__time_settings.steps_per_frame = new_steps_per_frame
        except ValueError:
            self.__update_time_steps_per_frame_text_box()

    def __update_time_steps_per_frame_text_box(self):
        self.__timestep_per_frame_textbox.set_text(str(self.__time_settings.steps_per_frame))

    def __create_language_menu(self):
        local_config = self.__config["languageMenuCfg"]
        self.__language_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=list(local_config["options"]),
            starting_option=local_config["startingOption"],
            relative_rect=pygame.Rect(local_config["rect"]),
            manager=self._pygame_gui_manager,
            container=self.__panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@dropdowns",
                object_id="#language_menu"
            )
        )
        # sync the locale between the gui manager and the menu
        self.__on_language_change()
        self._ui_manager.add_callback(
            pygame_gui.UI_DROP_DOWN_MENU_CHANGED,
            self.__language_dropdown,
            self.__on_language_change
        )

    def __on_language_change(self):
        local_config = self.__config["languageMenuCfg"]
        selected_language = local_config["options"][self.__language_dropdown.selected_option]
        self._pygame_gui_manager.set_locale(selected_language)

    def __create_timestep_controls(self):
        local_config = self.__config["dtControlCfg"]

        self.__timestep_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["labelRect"]),
            text="loc.timestep_label",
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        textbox = TextBox(
            rect=pygame.Rect(local_config["textboxRect"]),
            gui_manager=self._ui_manager,
            container=self.__panel,
            allowed_characters=".-+0123456789Ee",
            change_callback=self.__pause_simulation,
            finish_callback=self.__on_timestep_changed,
            unpause_callback=self.__on_timestep_changed
        )
        self.__timestep_textbox = textbox.element
        self.__elements.append(textbox)
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
        new_dt = self.__time_settings.dt / 2

        if not math.isfinite(new_dt):
            return

        self.__time_settings.dt = new_dt
        self.__update_timestep_textbox()

    def __increase_timestep(self):
        new_dt = self.__time_settings.dt * 2

        if not math.isfinite(new_dt):
            return

        self.__time_settings.dt = new_dt
        self.__update_timestep_textbox()

    def __on_timestep_changed(self):
        text = self.__timestep_textbox.text

        try:
            new_dt = float(text)

            if new_dt < 0.0 or not math.isfinite(new_dt):
                raise ValueError()

            self.__time_settings.dt = new_dt

        except ValueError:
            self.__update_timestep_textbox()

    def __pause_simulation(self):
        self.__time_settings.paused = True

    def __update_timestep_textbox(self):
        self.__timestep_textbox.set_text(str(self.__time_settings.dt))

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
            text="▶" if self.__time_settings.paused else "▮▮",
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

    def __handle_pause_event(self, _: PauseEvent):
        self.__pause_button.set_text("▶")

        for element in self.__elements:
            element.on_pause()

    def __handle_unpause_event(self, _: UnpauseEvent):
        self.__pause_button.set_text("▮▮")

        for element in self.__elements:
            element.on_unpause()

    def _update_ui(self):
        if not self.__time_settings.paused:
            for element in self.__elements:
                element.on_step()

    def _on_destroy(self):
        self.environment.event_system.remove_listener(PauseEvent, self.__handle_pause_event)
        self.environment.event_system.remove_listener(UnpauseEvent, self.__handle_unpause_event)

        super()._on_destroy()
