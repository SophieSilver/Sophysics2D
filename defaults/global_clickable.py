import pygame

from sophysics_engine import Event, PygameEvent, GlobalBehavior
from typing import Optional
from time import process_time


class ClickEvent(Event):
    """
    A wrapper for a pygame event that represents either button up or button down
    """
    def __init__(self, event: pygame.event.Event):
        self.__event = event
        self.__consumed = False

    @property
    def pygame_event(self) -> pygame.event.Event:
        return self.__event

    @property
    def consumed(self) -> bool:
        """
        Whether the event (such as a click) was consumed by one of the listeners, which signals to the other listeners
        to ignore this event.

        Useful when, for instance, you need an object to react when the user clicks on it, and you don't want other
        objects reacting to that click.
        """
        return self.__consumed

    def consume(self):
        """
        Marks the event as consumed. Note that it's up to the component whether to ignore a consumed event.

        Note: Do not consume mouse up events, or it might break things
        """
        self.__consumed = True


class ClickableManager(GlobalBehavior):
    def __init__(self, rect: pygame.Rect):
        self.__rect = rect

        super().__init__()

    def _start(self):
        self.environment.event_system.add_listener(PygameEvent, self.__handle_pygame_event)

    def _mouse_inside_the_rect(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        return self.__rect.collidepoint(mouse_pos)

    def __handle_pygame_event(self, event: PygameEvent):
        if not self._mouse_inside_the_rect():
            return

        pygame_event = event.pygame_event
        if not (pygame_event.type == pygame.MOUSEBUTTONUP or pygame_event.type == pygame.MOUSEBUTTONDOWN):
            return
        click_event = ClickEvent(pygame_event)
        self.environment.event_system.raise_event(click_event)

    def _end(self):
        self.environment.event_system.remove_listener(PygameEvent, self.__handle_pygame_event)


class GlobalClickable(GlobalBehavior):
    def __init__(self, button: int = 1, hold_time: float = 0):
        self.__button = button
        self.__hold_time = hold_time

        self.__hold_start_time: Optional[float] = None
        self.__was_holding = False

        super().__init__()

    def _start(self):
        self.environment.event_system.add_listener(ClickEvent, self.__handle_click_event)
        self._clickable_start()

    def _clickable_start(self):
        pass

    def __handle_click_event(self, event: ClickEvent):
        if event.consumed:
            return

        pygame_event = event.pygame_event
        if not (pygame_event.type == pygame.MOUSEBUTTONUP or pygame_event.type == pygame.MOUSEBUTTONDOWN):
            return

        if pygame_event.button != self.__button:
            return

        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            self.__handle_mouse_down_event(event)
        else:
            self.__handle_mouse_up_event(event)

    def __handle_mouse_down_event(self, event: ClickEvent):
        self._on_click()
        self.__hold_start_time = process_time()

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
        self.environment.event_system.remove_listener(ClickEvent, self.__handle_click_event)
        self._clickable_end()
