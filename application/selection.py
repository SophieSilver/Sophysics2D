"""
Scripts that allow the user to select particular components
"""
from __future__ import annotations
import pygame

from sophysics_engine import Event
from defaults import CircleClickable, GlobalClickable
from typing import Optional


class SelectionUpdateEvent(Event):
    def __init__(self, selected_body: Optional[BodyController]):
        self.__selected_body = selected_body

        super().__init__()

    @property
    def selected_body(self) -> BodyController:
        return self.__selected_body


class GlobalSelection(GlobalClickable):
    """
    A component that keeps track of the object selected by the user
    """
    def __init__(self, rect: pygame.Rect, button: int = 1, hold_time: float = 0):
        self.__selected_body: Optional[BodyController] = None

        super().__init__(rect, button, hold_time)

    @property
    def selected_body(self) -> BodyController:
        return self.__selected_body

    def select(self, body: Optional[BodyController]):
        """
        Selects a body
        """
        self.__selected_body = body
        self.environment.event_system.raise_event(SelectionUpdateEvent(self.__selected_body))

    def deselect(self):
        """
        A method to deselect the currently selected body
        """
        self.__selected_body = None
        self.environment.event_system.raise_event(SelectionUpdateEvent(self.__selected_body))

    def _on_click(self):
        self.deselect()


class BodyController(CircleClickable):
    def _clickable_start(self):
        self.__was_selected = False
        self.__global_selection: GlobalSelection = self.sim_object.environment.get_component(GlobalSelection)

        self.sim_object.environment.event_system.add_listener(SelectionUpdateEvent, self.__handle_selection_update)

    @property
    def is_selected(self) -> bool:
        return self.__global_selection.selected_body is self

    def __handle_selection_update(self, event: SelectionUpdateEvent):
        selected_body = event.selected_body

        if selected_body is self and not self.__was_selected:
            self.__was_selected = True
            self._on_select()

        elif selected_body is not self and self.__was_selected:
            self.__was_selected = False
            self._on_deselect()

    def _on_click(self):
        if self.is_selected:
            return

        self.__global_selection.select(self)

    def _on_select(self):
        """
        The method that's called when the body gets selected
        """
        print(f"{self.sim_object.tag} selected")

    def _on_deselect(self):
        """
        The method that's called when the body is deselected
        """
        print(f"{self.sim_object.tag} deselected")

    def _clickable_end(self):
        self.sim_object.environment.event_system.remove_listener(SelectionUpdateEvent, self.__handle_selection_update)
