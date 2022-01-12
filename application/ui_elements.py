"""
A wrapper for pygame_gui.elements designed to work with Sophysics2D framework
"""
import pygame_gui
import pygame
from typing import Callable, Optional, List, Union
from abc import ABC
from sophysics_engine import GUIManager


class UIElement(ABC):
    def __init__(self, gui_manager: GUIManager, update_callback: Optional[Callable], update_every_frame: bool = True,
                 update_on_pause: bool = False, update_on_unpause: bool = True,):
        self._gui_manager = gui_manager
        self.update_every_frame = update_every_frame
        self.update_on_pause = update_on_pause
        self.update_on_unpause = update_on_unpause
        self.__update_callback = update_callback

    def on_frame_update(self):
        if self.update_every_frame and self.__update_callback is not None:
            self.__update_callback()

    def on_pause(self):
        if self.update_on_pause and self.__update_callback is not None:
            self.__update_callback()

    def on_unpause(self):
        if self.update_on_unpause and self.__update_callback is not None:
            self.__update_callback()

    def destroy(self):
        self._gui_manager = None


class TextBox(UIElement):
    def __init__(self, rect: pygame.Rect, gui_manager: GUIManager,
                 container: pygame_gui.core.IContainerLikeInterface,
                 allowed_characters: Optional[Union[str, List[str]]] ,update_callback: Optional[Callable],
                 change_callback: Optional[Callable], finish_callback: Optional[Callable],
                 update_every_frame: bool = True, update_on_pause: bool = False,
                 update_on_unpause: bool = True):
        # that's a thicc argument list lol
        super().__init__(gui_manager, update_callback, update_every_frame, update_on_pause, update_on_unpause)

        self.__textbox = pygame_gui.elements.UITextEntryLine(
            relative_rect=rect,
            manager=gui_manager.ui_manager,
            container=container,
        )
        self.__textbox.set_allowed_characters(allowed_characters)
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
