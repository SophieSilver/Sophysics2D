from sophysics_engine import EnvironmentComponent, Camera, EnvironmentUpdateEvent, PygameEvent
from time import process_time
from typing import Optional
import pygame


class CameraController(EnvironmentComponent):
    """
    Allows the user to control the camera using the mousewheel
    """
    def __init__(self, camera: Camera, rect: pygame.Rect, hold_time: float = 0.05,
                 zoom_strength: float = 0.05, min_camera_scale: float = 1 / 160):
        """
        :param camera: the camera component that is controlled
        :param rect: Any input that's outside of the rect will be ignored
        :param hold_time: time in seconds the user has to hold the middle mouse button for it to be recognized as a hold
        """
        self.__camera = camera
        self.__hold_threshold = hold_time
        self.__rect = rect
        self.__hold_start_time: Optional[float] = None
        self.__prev_hold_position: Optional[pygame.Vector2] = None
        self.__zoom_strength = zoom_strength
        self.__min_camera_scale = min_camera_scale
        super().__init__()

    def setup(self):
        self.environment.event_system.add_listener(EnvironmentUpdateEvent, self.__handle_update_event)
        self.environment.event_system.add_listener(PygameEvent, self.__handle_pygame_event)

    def __handle_pygame_event(self, event: PygameEvent):
        pygame_event = event.pygame_event
        if pygame_event.type == pygame.MOUSEWHEEL:
            scroll = pygame_event.y
            self.__handle_zoom(scroll)

        # when the user starts holding the mousewheel
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN and pygame_event.button == 2:
            self.__handle_button_down_event()
            event.consume()

        # when the user stops holding the mousewheel
        elif pygame_event.type == pygame.MOUSEBUTTONUP and pygame_event.button == 2:
            self.__handle_button_up_event()
            event.consume()

    def __handle_zoom(self, scroll: int):
        # to make zooming feel better, we'll zoom into the cursor instead of the center of the screen.

        # in order to achieve that, we will take a point in the worldspace that corresponds to the mouse position
        # see where it is after the zooming and subtract the difference from the camera position

        # mouse position on the screen
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        # the world point that corresponds to the current mouse position
        world_point = pygame.Vector2(self.__camera.screen_to_world(mouse_pos))

        # applying the zoom
        self.__camera.units_per_pixel -= self.__camera.units_per_pixel * scroll * self.__zoom_strength
        self.__camera.units_per_pixel = max(self.__camera.units_per_pixel, self.__min_camera_scale)

        # finding where the point ended up
        new_point_position = pygame.Vector2(self.__camera.world_to_screen(world_point))
        # subtracting the difference
        displacement = mouse_pos - new_point_position
        self.__camera.position -= displacement

    def __handle_button_down_event(self):
        # ignore the click if it's outside the rect
        if not self.__mouse_inside_the_rect():
            return

        self.__hold_start_time = process_time()

    def __handle_button_up_event(self):
        # even if this happened outside of the rect we are still gonna stop holding, so no checking for the rect

        self.__hold_start_time = None
        self.__prev_hold_position = None

    def __mouse_inside_the_rect(self) -> bool:
        """
        checks if the mouse cursor is inside the self.__rect
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.__rect.collidepoint(mouse_x, mouse_y)

    def __handle_update_event(self, _: EnvironmentUpdateEvent):
        self.__update()

    def __update(self):
        if self.__hold_start_time is not None:
            current_holding_time = process_time() - self.__hold_start_time
            if current_holding_time >= self.__hold_threshold:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                if self.__prev_hold_position is None:
                    delta_pos = pygame.Vector2(0, 0)
                else:
                    delta_pos = mouse_pos - self.__prev_hold_position
                self.__camera.position -= delta_pos
                self.__prev_hold_position = mouse_pos

    def _on_destroy(self):
        self.environment.event_system.remove_listener(EnvironmentUpdateEvent, self.__handle_update_event)

