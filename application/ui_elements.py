"""
A wrapper for pygame_gui.elements designed to work with Sophysics2D framework
"""
import pygame_gui
import pygame
from typing import Callable, Optional, List, Union, Tuple
from abc import ABC
from sophysics_engine import GUIManager


class UIElement(ABC):
    def __init__(self, gui_manager: GUIManager, step_callback: Optional[Callable] = None,
                 pause_callback: Optional[Callable] = None, unpause_callback: Optional[Callable] = None,
                 refresh_callback: Optional[Callable] = None):
        self._gui_manager = gui_manager

        self.__step_callback = step_callback
        self.__pause_callback = pause_callback
        self.__unpause_callback = unpause_callback
        self.__refresh_callback = refresh_callback

    def on_step(self):
        if self.__step_callback is not None:
            self.__step_callback()

    def on_pause(self):
        if self.__pause_callback is not None:
            self.__pause_callback()

    def on_unpause(self):
        if self.__unpause_callback is not None:
            self.__unpause_callback()

    def refresh(self):
        if self.__refresh_callback is not None:
            self.__refresh_callback()

    def destroy(self):
        self._gui_manager = None


class SwitchButtons(UIElement):
    def __init__(self, rect1: pygame.Rect, rect2: pygame.Rect, texts: Tuple[str, str],
                 gui_manager: GUIManager,
                 container: pygame_gui.core.IContainerLikeInterface,
                 is_enabled: bool = True,
                 state_change_callback: Optional[Callable] = None,
                 step_callback: Optional[Callable] = None,
                 pause_callback: Optional[Callable] = None,
                 unpause_callback: Optional[Callable] = None,
                 refresh_callback: Optional[Callable] = None):
        super().__init__(gui_manager, step_callback, pause_callback, unpause_callback, refresh_callback)
        self.__is_enabled: bool = is_enabled
        self.__state_change_callback = state_change_callback

        self.__enable_button = pygame_gui.elements.UIButton(
            relative_rect=rect1,
            text=texts[0],
            manager=gui_manager.ui_manager,
            container=container
        )
        gui_manager.add_callback(
            pygame_gui.UI_BUTTON_START_PRESS,
            self.__enable_button,
            self.__on_enable_button_click
        )

        self.__disable_button = pygame_gui.elements.UIButton(
            relative_rect=rect2,
            text=texts[1],
            manager=gui_manager.ui_manager,
            container=container
        )
        gui_manager.add_callback(
            pygame_gui.UI_BUTTON_START_PRESS,
            self.__disable_button,
            self.__on_disable_button_click
        )
        # to update the buttons
        self.is_enabled = is_enabled

    @property
    def is_enabled(self) -> bool:
        return self.__is_enabled

    @is_enabled.setter
    def is_enabled(self, value: bool):
        self.__is_enabled = value

        if self.__is_enabled:
            self.__enable_button.disable()
            self.__disable_button.enable()
        else:
            self.__enable_button.enable()
            self.__disable_button.disable()

    def __on_enable_button_click(self):
        self.is_enabled = True
        if self.__state_change_callback is not None:
            self.__state_change_callback()

    def __on_disable_button_click(self):
        self.is_enabled = False
        if self.__state_change_callback is not None:
            self.__state_change_callback()


class TextBox(UIElement):
    def __init__(self, rect: pygame.Rect, gui_manager: GUIManager,
                 container: pygame_gui.core.IContainerLikeInterface,
                 allowed_characters: Optional[Union[str, List[str]]] = None,
                 change_callback: Optional[Callable] = None,
                 finish_callback: Optional[Callable] = None,
                 step_callback: Optional[Callable] = None,
                 pause_callback: Optional[Callable] = None,
                 unpause_callback: Optional[Callable] = None,
                 refresh_callback: Optional[Callable] = None
                 ):
        # that's a thicc argument list lol
        super().__init__(gui_manager, step_callback, pause_callback, unpause_callback, refresh_callback)

        self.__textbox = pygame_gui.elements.UITextEntryLine(
            relative_rect=rect,
            manager=gui_manager.ui_manager,
            container=container,
        )
        self.__textbox.allowed_characters = allowed_characters
        if change_callback is not None:
            self._gui_manager.add_callback(
                pygame_gui.UI_TEXT_ENTRY_CHANGED,
                self.__textbox,
                change_callback
            )
        if finish_callback is not None:
            self._gui_manager.add_callback(
                pygame_gui.UI_TEXT_ENTRY_FINISHED,
                self.__textbox,
                finish_callback
            )

    @property
    def element(self) -> pygame_gui.elements.UITextEntryLine:
        return self.__textbox
