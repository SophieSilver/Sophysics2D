"""
Scripts that allow the user to select particular components
"""
from __future__ import annotations
import pygame

from sophysics_engine import Event, TimeSettings, RigidBody
from defaults import CircleClickable, GlobalClickable, VectorArrowRenderer, CircleRenderer
from typing import Optional, List

from .select_renderer import SelectionRenderer


class SelectionUpdateEvent(Event):
    def __init__(self, selected_body: Optional[BodyController]):
        self.__selected_body = selected_body

        super().__init__()

    @property
    def selected_body(self) -> BodyController:
        return self.__selected_body


class SelectedBodyPositionUpdateEvent(Event):
    pass


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
        self.__selection_renderer: SelectionRenderer = self.sim_object.get_component(SelectionRenderer)
        self.__vector_renderer: VectorArrowRenderer = self.sim_object.get_component(VectorArrowRenderer)
        self.__renderers: List[CircleRenderer] = self.sim_object.get_components(CircleRenderer)
        self.__time_settings: TimeSettings = self.sim_object.environment.get_component(TimeSettings)

        self.__mouse_offset_from_body: Optional[pygame.Vector2] = None

        # commonly used by other scripts
        self.__rigidbody: Optional[RigidBody] = self.sim_object.try_get_component(RigidBody)

        self.sim_object.environment.event_system.add_listener(SelectionUpdateEvent, self.__handle_selection_update)

    @property
    def rigidbody(self) -> Optional[RigidBody]:
        """
        A reference to the object's rigidbody component. If the object doesn't have one,
        the value is None.
        """
        return self.__rigidbody

    @property
    def renderers(self) -> List[CircleRenderer]:
        return self.__renderers

    @property
    def is_selected(self) -> bool:
        return self.__global_selection.selected_body is self

    @property
    def screen_position(self) -> pygame.Vector2:
        return pygame.Vector2(self._camera.world_to_screen(self.sim_object.transform.position))

    @screen_position.setter
    def screen_position(self, value: pygame.Vector2):
        self.sim_object.transform.position = self._camera.screen_to_world(value)

    def __handle_selection_update(self, event: SelectionUpdateEvent):
        selected_body = event.selected_body

        if selected_body is self and not self.__was_selected:
            self.__was_selected = True
            self._on_select()

        elif selected_body is not self and self.__was_selected:
            self.__was_selected = False
            self._on_deselect()

    def _on_hold_start(self):
        # record the relative position between the body and the mouse cursor
        self.__mouse_offset_from_body = pygame.Vector2(pygame.mouse.get_pos()) - self.screen_position
        # pause the simulation
        self.__time_settings.paused = True

    def _on_hold(self):
        self.screen_position = pygame.Vector2(pygame.mouse.get_pos()) - self.__mouse_offset_from_body

        self.sim_object.environment.event_system.raise_event(SelectedBodyPositionUpdateEvent())

    def _on_hold_end(self):
        self.__mouse_offset_from_body = None

    def _on_click(self):
        if self.is_selected:
            return

        self.__global_selection.select(self)

    def _on_select(self):
        """
        The method that's called when the body gets selected
        """
        # print("selected")
        self.__selection_renderer.is_active = True
        self.__vector_renderer.is_active = True

    def _on_deselect(self):
        """
        The method that's called when the body is deselected
        """
        # print("deselected")
        self.__selection_renderer.is_active = False
        self.__vector_renderer.is_active = False

    def _clickable_end(self):
        self.sim_object.environment.event_system.remove_listener(SelectionUpdateEvent, self.__handle_selection_update)
        # if the object is selected, deselect it
        if self.is_selected:
            self.__global_selection.deselect()
