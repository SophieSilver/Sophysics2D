from .simulation import EnvironmentComponent
from .event_system import Event
import pygame


class PygameEvent(Event):
    """
    A wrapper for a pygame event that's compatible with sophysics event system
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
        Whether the event (such as a click) was consumed by a one of the listeners, which signals the other listeners
        to ignore this event.

        Useful when, for instance, you need an object to react when the user clicks it, and you don't want other
        objects reacting to that click.
        """
        return self.__consumed

    def consume(self):
        """
        Marks the event as consumed
        """
        self.__consumed = True


class PygameEventProcessor(EnvironmentComponent):
    """
    An object that processes events that are used by the pygame library
    """
    def process_event(self, event: pygame.event.Event):
        """
        Wraps a pygame event and raises it with the environment's event system
        """
        event_wrapper = PygameEvent(event)
        self.environment.event_system.raise_event(event_wrapper)
