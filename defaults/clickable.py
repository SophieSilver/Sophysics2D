from .global_clickable import ClickEvent
from sophysics_engine import PygameEvent, MonoBehavior
from time import process_time
from typing import Optional
from abc import ABC, abstractmethod
import pygame


class Clickable(MonoBehavior, ABC):
    """
    Note, that, in order for this component to work, the environment must have a global clickable component
    """
    def __init__(self, rect: pygame.Rect, button: int = 1, hold_time: float = 0):
        self.__rect = rect
        self.__button = button
        self.__hold_time = hold_time

        self.__hold_start_time: Optional[float] = None
        self.__was_holding = False

        super().__init__()

    @abstractmethod
    def _mouse_on_object(self) -> bool:
        """
        Returns True if the mouse cursor is pointing at the object
        """
        pass

    def _start(self):
        self.sim_object.environment.event_system.add_listener(ClickEvent, self.__handle_click_event)
        self._clickable_start()

    def _clickable_start(self):
        pass

    def __handle_click_event(self, event: ClickEvent):
        if event.consumed:
            return

        pygame_event = event.pygame_event

        # there are only 2 possible types of click events
        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            self.__handle_mouse_down_event(event)
        else:
            self.__handle_mouse_up_event(event)

    def __handle_mouse_down_event(self, event: ClickEvent):
        if not (self._mouse_inside_the_rect() and self._mouse_on_object()):
            return

        pygame_event = event.pygame_event

        if pygame_event.button != self.__button:
            return

        self._on_click()
        self.__hold_start_time = process_time()

        event.consume()

    def __handle_mouse_up_event(self, _: ClickEvent):
        self.__hold_start_time = None

        if self.__was_holding:
            self._on_hold_end()
            self.__was_holding = False

    def _is_holding(self) -> bool:
        if self.__hold_start_time is None:
            return False

        current_holding_time = process_time() - self.__hold_start_time

        return current_holding_time >= self.__hold_time

    def _update(self):
        if self._is_holding():
            if not self.__was_holding:
                self._on_hold_start()
                self.__was_holding = True

            self._on_hold()

        self._clickable_update()

    def _clickable_update(self):
        pass

    def _mouse_inside_the_rect(self) -> bool:
        """
        checks if the mouse cursor is inside the self.__rect
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.__rect.collidepoint(mouse_x, mouse_y)

    def _on_click(self):
        """
        Method that gets called when the user clicks on the specified mouse button
        """
        pass

    def _on_hold_start(self):
        """
        Method that gets called when the user starts holding the specified mouse button
        """
        pass

    def _on_hold(self):
        """
        Method that's called every frame the user holds the specified mouse button
        """

    def _on_hold_end(self):
        """
        Method that gets called when the user stops holding the specified mouse button
        """
        pass

    def _clickable_end(self):
        pass

    def _end(self):
        self.sim_object.environment.event_system.remove_listener(PygameEvent, self.__handle_click_event)
        self._clickable_end()
