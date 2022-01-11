from .selection import GlobalSelection, BodyController
from defaults import GlobalClickable
from sophysics_engine import Camera, TimeSettings, Event
from typing import Optional
import pygame


class SelectedBodyVelocityUpdateEvent(Event):
    pass


class VelocityController(GlobalClickable):
    """
    Allows the user to control the velocity of the object by holding one of the mouse buttons.
    Supposed to be used together with a velocity arrow renderer
    The relative position between the mouse and the center of the object determines the objects velocity
    """
    def __init__(self, camera: Camera, rect: pygame.Rect, scale_factor: float = 1.0,
                 button: int = 1, hold_time: float = 0):
        self.__camera = camera
        self.scale_factor = scale_factor

        self.__global_selection: Optional[GlobalSelection] = None
        self.__time_settings: Optional[TimeSettings] = None

        super().__init__(rect, button, hold_time)

    def _clickable_start(self):
        self.__time_settings = self.environment.get_component(TimeSettings)
        self.__global_selection = self.environment.get_component(GlobalSelection)

    def __get_selected_body(self) -> Optional[BodyController]:
        return self.__global_selection.selected_body

    def __get_cursor_object_relative_pos(self) -> Optional[pygame.Vector2]:
        """
        Returns the difference between the mouse position and the currently selected object screen coordinates.
        The returned vector points FROM the object TO the cursor!
        If no object is selected, returns None.
        """
        if self.__get_selected_body() is None:
            return None

        body_world_pos = self.__get_selected_body().sim_object.transform.position
        body_screen_pos = pygame.Vector2(self.__camera.world_to_screen(body_world_pos))

        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        return mouse_pos - body_screen_pos

    def _on_hold_start(self):
        if self.__get_selected_body() is None:
            return

        self.__time_settings.paused = True

    def _on_hold(self):
        if self.__get_selected_body() is None:
            return

        relative_pos = self.__get_cursor_object_relative_pos()

        new_velocity = relative_pos * self.__camera.units_per_pixel / self.scale_factor

        # flipping the y axis, coz in the screen coordinates it points downwards
        new_velocity.y = -new_velocity.y

        # applying the new velocity
        rigidbody = self.__get_selected_body().rigidbody

        rigidbody.velocity = new_velocity

        self.environment.event_system.raise_event(SelectedBodyVelocityUpdateEvent())
