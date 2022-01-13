"""
A wrapper for pygame_gui.elements designed to work with Sophysics2D framework
"""
import pygame_gui
import pygame
from typing import Callable, Optional, List, Union
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
