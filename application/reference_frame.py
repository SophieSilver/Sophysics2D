import pymunk

from sophysics_engine import EnvironmentComponent, MonoBehavior, GlobalBehavior, RigidBody, Event
from typing import Optional
import pygame


class ReferenceFrameCalculateOffsetEvent(Event):
    pass


class ReferenceFrameUpdateValuesEvent(Event):
    pass


class ReferenceFrameManager(GlobalBehavior):
    """
    Holds info, about which object is currently the origin
    """
    def __init__(self):
        self.origin_body: Optional[RigidBody] = None

        super().__init__()

    def _physics_update(self):
        if self.origin_body is None:
            return

        if self.origin_body.sim_object is None:
            self.origin_body = None
            return

        self.environment.event_system.raise_event(ReferenceFrameCalculateOffsetEvent())
        self.environment.event_system.raise_event(ReferenceFrameUpdateValuesEvent())


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

    def _on_destroy(self):
        self.sim_object.environment.event_system.remove_listener(
            ReferenceFrameCalculateOffsetEvent, self.__handle_calculate_offset_event)

        self.sim_object.environment.event_system.remove_listener(
            ReferenceFrameUpdateValuesEvent, self.__handle_reference_update_event
        )
