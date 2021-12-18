from .simulation import EnvironmentComponent, EnvironmentUpdateEvent
from .rendering import CameraRenderEvent, Camera
from .event_system import Event, EventSystem
from .pygame_event_processor import PygameEvent
from time import process_time
from typing import Optional, Dict, Callable, Union
import pygame
import pygame_gui


class GUIManager(EnvironmentComponent):
    """
    A necessary dependency for all GUI components.

    The event handling is done by listening to PygameGUIEvent events.
    The user must raise them before calling the ui_update.
    """
    def __init__(self, ui_manager: pygame_gui.UIManager, layer: int = 6):
        super().__init__()
        self.__layer = layer
        self.__ui_manager = ui_manager
        self.__event_system: Optional[EventSystem] = None

        # a nested dictionary with the following structure:
        # __ui_event_listeners[event_type][ui_element] = callback_func
        self.__ui_event_listeners: Dict[Union[int, str], Dict[pygame_gui.core.UIElement, Callable]] = {}

        # a field to compute time delta for the update method
        self.__last_update_time: Optional[int] = None

        # when adding ui elements, initialize the fields here with None
        # and actually create them on setup_ui()

    @property
    def ui_manager(self) -> pygame_gui.UIManager:
        return self.__ui_manager

    def setup(self):
        self.__event_system = self.environment.event_system
        self.__event_system.add_listener(CameraRenderEvent, self.__handle_render_event)
        self.__event_system.add_listener(EnvironmentUpdateEvent, self.__handle_update_event)
        self.__event_system.add_listener(PygameEvent, self.__handle_pygame_event)

    def add_callback(self, event_type: Union[int, str], element: pygame_gui.core.UIElement, callback: Callable):
        """
        Add a function that will be called when an event of a given type with a given element gets raised

        The callback function does not have any arguments
        """
        if event_type not in self.__ui_event_listeners:
            self.__ui_event_listeners[event_type] = {}

        event_callbacks = self.__ui_event_listeners[event_type]
        event_callbacks[element] = callback

    def __handle_render_event(self, event: CameraRenderEvent):
        camera = event.camera
        self.draw_ui(camera)

    def __handle_update_event(self, _: EnvironmentUpdateEvent):
        self.update_ui()

    def __handle_pygame_event(self, event_wrapper: PygameEvent):
        pygame_event = event_wrapper.pygame_event
        self.__ui_manager.process_events(pygame_event)

        if pygame_event.type != pygame.USEREVENT:
            return

        event_type = pygame_event.user_type
        ui_element = pygame_event.ui_element

        if event_type not in self.__ui_event_listeners or ui_element not in self.__ui_event_listeners[event_type]:
            return

        callback = self.__ui_event_listeners[pygame_event.user_type][pygame_event.ui_element]
        callback()

    def update_ui(self):
        # if the update is called for the first time we just use a default value of 1/60 of a second as time delta
        time_delta = process_time() - self.__last_update_time if self.__last_update_time is not None else 1 / 60

        self.__ui_manager.update(time_delta)

    def draw_ui(self, camera: Camera):
        """
        Draws the ui on the screen
        """
        self.__ui_manager.draw_ui(camera.get_layer_for_rendering(self.__layer))

    def _on_destroy(self):
        self.__event_system.remove_listener(CameraRenderEvent, self.__handle_render_event)
        self.__event_system.remove_listener(EnvironmentUpdateEvent, self.__handle_update_event)
        self.__event_system.remove_listener(PygameEvent, self.__handle_pygame_event)

