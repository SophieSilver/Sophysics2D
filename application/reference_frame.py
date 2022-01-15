import pymunk

from sophysics_engine import EnvironmentComponent, MonoBehavior, GlobalBehavior, RigidBody, Event, Camera
from .trail_renderer import TrailResetEvent
from typing import Optional
import pygame


class ReferenceFrameCalculateOffsetEvent(Event):
    pass


class ReferenceFrameUpdateValuesEvent(Event):
    pass


class ReferenceFrameOriginChanged(Event):
    def __init__(self, new_origin: Optional[RigidBody]):
        self.__new_origin = new_origin

    @property
    def new_origin(self) -> Optional[RigidBody]:
        return self.__new_origin


class ReferenceFrameManager(GlobalBehavior):
    """
    Holds info, about which object is currently the origin
    """
    def __init__(self):
        self.__origin_body: Optional[RigidBody] = None
        self.__body_changed: bool = False

        super().__init__()

    @property
    def origin_body(self) -> Optional[RigidBody]:
        return self.__origin_body

    @origin_body.setter
    def origin_body(self, value: Optional[RigidBody]):
        self.__origin_body = value
        self.__body_changed = True

    def _physics_update(self):
        print(self.__origin_body)

        if self.__body_changed:
            self.environment.event_system.raise_event(ReferenceFrameOriginChanged(self.origin_body))

        if self.origin_body is not None:
            if self.origin_body.sim_object is not None:
                self.environment.event_system.raise_event(ReferenceFrameCalculateOffsetEvent())
                self.environment.event_system.raise_event(ReferenceFrameUpdateValuesEvent())

            else:
                self.origin_body = None

        if self.__body_changed:
            self.environment.event_system.raise_event(TrailResetEvent())
            self.__body_changed = False


class ReferenceFrame(MonoBehavior):
    def _start(self):
        self.__rigidbody: RigidBody = self.sim_object.get_component(RigidBody)
        self.__position_offset = pygame.Vector2()
        self.__velocity_offset = pymunk.Vec2d(0, 0)

        self.__reference_frame_manager: ReferenceFrameManager = \
            self.sim_object.environment.try_get_component(ReferenceFrameManager)

        if self.__reference_frame_manager is None:
            self.__reference_frame_manager = ReferenceFrameManager()
            self.sim_object.environment.attach_component(self.__reference_frame_manager)

        self.sim_object.environment.event_system.add_listener(
            ReferenceFrameCalculateOffsetEvent, self.__handle_calculate_offset_event)

        self.sim_object.environment.event_system.add_listener(
            ReferenceFrameUpdateValuesEvent, self.__handle_reference_update_event
        )

    def __handle_calculate_offset_event(self, _: ReferenceFrameCalculateOffsetEvent):
        origin = self.__reference_frame_manager.origin_body

        self.__position_offset = origin.sim_object.transform.position.copy()
        self.__velocity_offset = origin.velocity

    def __handle_reference_update_event(self, _: ReferenceFrameUpdateValuesEvent):
        self.__rigidbody.sim_object.transform.position -= self.__position_offset
        self.__rigidbody.velocity -= self.__velocity_offset

    def _end(self):
        self.sim_object.environment.event_system.remove_listener(
            ReferenceFrameCalculateOffsetEvent, self.__handle_calculate_offset_event)

        self.sim_object.environment.event_system.remove_listener(
            ReferenceFrameUpdateValuesEvent, self.__handle_reference_update_event
        )


class ReferenceFrameCameraAdjuster(EnvironmentComponent):
    def __init__(self, camera: Camera):
        self.__camera = camera

        super().__init__()

    def setup(self):
        self.environment.event_system.add_listener(ReferenceFrameOriginChanged, self.__handle_origin_change_event)

    def __handle_origin_change_event(self, event: ReferenceFrameOriginChanged):
        if event.new_origin is None:
            return

        new_origin_point = event.new_origin.sim_object.transform.position

        self.__adjust_camera(new_origin_point)

    def __adjust_camera(self, new_origin_point: pygame.Vector2):
        screen_origin_point = pygame.Vector2(self.__camera.world_to_screen(new_origin_point))
        offset_from_origin = self.__camera.position - screen_origin_point

        new_camera_position = pygame.Vector2(self.__camera.world_to_screen((0, 0))) + offset_from_origin

        self.__camera.position = new_camera_position

    def _on_destroy(self):
        self.environment.event_system.remove_listener(ReferenceFrameOriginChanged, self.__handle_origin_change_event)

        super()._on_destroy()
