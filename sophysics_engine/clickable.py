from .pygame_event_processor import PygameEvent
from .monobehavior import MonoBehavior
from abc import abstractmethod
from typing import Optional
from time import process_time

import pygame


class Clickable(MonoBehavior):
    """
    A component that can have scripts that react to clicks
    """
    def __init__(self, rect: pygame.Rect, hold_time: float = 0):
        self.__rect = rect
        self.__hold_time = hold_time

        # on a second thought, all this might be handled globally by one component
        # instead of each object keeping track of all this by itself
        # hmmm, screw it, I'll change it later (probably)
        self.__hold_start_time_left: Optional[float] = None
        self.__hold_start_time_left_global: Optional[float] = None
        self.__hold_start_time_right: Optional[float] = None
        self.__hold_start_time_right_global: Optional[float] = None

        # these are needed to decide when to call hold_start methods
        self.__was_holding_left = False
        self.__was_holding_left_global = False
        self.__was_holding_right = False
        self.__was_holding_right_global = False

        super().__init__()

    def _start(self):
        """
        Used internally as a setup, when overriding, use super()
        """
        self.sim_object.environment.event_system.add_listener(PygameEvent, self.__handle_pygame_event)

    def __handle_pygame_event(self, event: PygameEvent):
        pygame_event = event.pygame_event

        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            self.__handle_mouse_down_event(event)

        elif pygame_event.type == pygame.MOUSEBUTTONUP:
            self.__handle_mouse_up_event(event)

    def __handle_mouse_down_event(self, event: PygameEvent):
        if not self._mouse_inside_the_rect():
            return
        # the reason we're taking the event wrapper instead of an unwrapped pygame event is so that we can consume() it
        pygame_event = event.pygame_event
        # left mouse button
        if pygame_event.button == 1:
            # starting the hold timer and calling the on_click callback
            self.__hold_start_time_left_global = process_time()
            self.on_left_click_global()
            # same stuff, but if the user actually clicks on the object and not anywhere in the world
            if self.mouse_on_object() and not event.consumed:
                self.__hold_start_time_left = process_time()
                self.on_left_click()
                event.consume()

        # same, but for right mouse button
        elif pygame_event.button == 3:
            self.__hold_start_time_right_global = process_time()
            self.on_right_click_global()

            if self.mouse_on_object() and not event.consumed:
                self.__hold_start_time_right = process_time()
                self.on_right_click()
                event.consume()

    def __handle_mouse_up_event(self, event: PygameEvent):
        # reset the hold timers
        pygame_event = event.pygame_event

        # for left
        if pygame_event.button == 1:
            # resetting both btw
            self.__hold_start_time_left = None
            self.__hold_start_time_left_global = None

            if self.__was_holding_left:
                self.__was_holding_left = False
                self.on_left_end_hold()

            if self.__was_holding_left_global:
                self.__was_holding_left_global = False
                self.on_left_end_hold_global()

        # same for right
        elif pygame_event.button == 3:
            self.__hold_start_time_right = None
            self.__hold_start_time_right_global = None

            if self.__was_holding_right:
                self.__was_holding_right = False
                self.on_right_end_hold()

            if self.__was_holding_right_global:
                self.__was_holding_right_global = False
                self.on_right_end_hold_global()

    def is_holding_left(self):
        """
        Whether the user is currently holding the left mouse button on the object
        """
        if self.__hold_start_time_left is None:
            return False

        current_holding_time = process_time() - self.__hold_start_time_left

        return current_holding_time >= self.__hold_time

    def is_holding_left_global(self):
        """
        Whether the user is currently holding the left mouse button anywhere within the rect
        """
        if self.__hold_start_time_left_global is None:
            return False

        current_holding_time = process_time() - self.__hold_start_time_left_global

        return current_holding_time >= self.__hold_time

    def is_holding_right(self):
        """
        Whether the user is currently holding the right mouse button on the object
        """
        if self.__hold_start_time_right is None:
            return False

        current_holding_time = process_time() - self.__hold_start_time_right

        return current_holding_time >= self.__hold_time

    def is_holding_right_global(self):
        """
        Whether the user is currently holding the right mouse button anywhere within the rect
        """
        if self.__hold_start_time_right_global is None:
            return False

        current_holding_time = process_time() - self.__hold_start_time_right_global

        return current_holding_time >= self.__hold_time

    @abstractmethod
    def mouse_on_object(self):
        """
        Returns True if the mouse is hovering over the object
        """
        pass

    def _mouse_inside_the_rect(self) -> bool:
        """
        checks if the mouse cursor is inside the self.__rect
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.__rect.collidepoint(mouse_x, mouse_y)

    def update(self):
        """
        Used internally, when overriding, use super()
        """
        # check if the user is holding anything and if they are, call associated methods
        # maybe there's a better, more elegant way of doing this, but fuck it, it works
        if self.is_holding_right():
            # if it's the first time we're holding, call the hold start method
            if not self.__was_holding_right:
                self.on_right_start_hold()
                self.__was_holding_right = True

            self.on_right_hold()

        if self.is_holding_right_global():
            if not self.__was_holding_right_global:
                self.on_right_start_hold_global()
                self.__was_holding_right_global = True

            self.on_right_hold_global()

        if self.is_holding_left():
            if not self.__was_holding_left:
                self.on_left_start_hold()
                self.__was_holding_left = True

            self.on_left_hold()

        if self.is_holding_left_global():
            if not self.__was_holding_left_global:
                self.on_left_start_hold_global()
                self.__was_holding_left_global = True

            self.on_left_hold_global()

    def on_left_click(self):
        """
        Gets called when the user left clicks on the object
        """
        pass

    def on_right_click(self):
        """
        Gets called when the user right clicks on the object
        """
        pass

    def on_left_click_global(self):
        """
        Gets called when the user left clicks anywhere within the rect
        """
        pass

    def on_right_click_global(self):
        """
        Gets called when the user right clicks anywhere within the rect
        """
        pass

    def on_left_hold(self):
        """
        Gets called when the user holds the left mouse button on the object
        """
        pass

    def on_right_hold(self):
        """
        Gets called when the user holds the right mouse button on the object
        """
        pass

    def on_left_hold_global(self):
        """
        Gets called when the user holds the left mouse button anywhere withing the rect
        """
        pass

    def on_right_hold_global(self):
        """
        Gets called when the user holds the right mouse button anywhere withing the rect
        """
        pass

    def on_left_start_hold(self):
        """
        Gets called the first frame the user holds the left mouse button on the object
        """
        pass
    
    def on_right_start_hold(self):
        """
        Gets called the first frame the user holds the right mouse button on the object
        """
        pass
    
    def on_left_start_hold_global(self):
        """
        Gets called the first frame the user holds the left mouse button
        """
        pass

    def on_right_start_hold_global(self):
        """
        Gets called the first frame the user holds the right mouse button
        """
        pass
    
    def on_left_end_hold(self):
        """
        Gets called the first frame the user stops holding the left mouse button on the object
        """
        pass
    
    def on_right_end_hold(self):
        """
        Gets called the first frame the user stops holding the right mouse button on the object
        """
        pass
    
    def on_left_end_hold_global(self):
        """
        Gets called the first frame the user stops holding the left mouse button
        """
        pass

    def on_right_end_hold_global(self):
        """
        Gets called the first frame the user stops holding the right mouse button
        """
        pass

    def _end(self):
        """
        Used internally, when overriding, use super()
        """
        self.sim_object.environment.event_system.remove_listener(PygameEvent, self.__handle_pygame_event)
