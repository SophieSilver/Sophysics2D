from sophysics_engine import Renderer, Event, PostPhysicsUpdateEvent, Camera
from collections import deque
import pygame


class TrailResetEvent(Event):
    """
    Raise this event to erase all trails
    """
    pass


class TrailRenderer(Renderer):
    """
    Renders a curve that follows the object's trajectory
    """

    def __init__(self, point_distance: float, max_points: int, thickness: int, color, layer: int):
        # to draw the trail, we will add points to a deque, new points will be added, when the object goes
        # beyond a certain distance from the last point
        # to optimize that comparison, we will compare the squares of those distances, instead of
        # the distances themselves,
        # which will eliminate the pesky square root when finding the distance
        # that's why we store the square of the point distance
        self.__point_distance_squared = point_distance * point_distance
        self.__thickness = thickness
        self.__points = deque(maxlen=max_points)

        super().__init__(color, layer)

    def setup(self):
        super().setup()

        self.sim_object.environment.event_system.add_listener(TrailResetEvent, self.__handle_reset_event)
        self.sim_object.environment.event_system.add_listener(PostPhysicsUpdateEvent, self.__handle_post_physics_event)

    def __handle_reset_event(self, _: TrailResetEvent):
        self.reset_trail()

    def __handle_post_physics_event(self, _: PostPhysicsUpdateEvent):
        if not self.is_active:
            return

        # if there are no points, we just add one
        if len(self.__points) == 0:
            self.__points.append(tuple(self.sim_object.transform.position))
            return

        dist_to_last_point = pygame.Vector2(self.__points[-1]).distance_squared_to(self.sim_object.transform.position)

        if dist_to_last_point >= self.__point_distance_squared:
            self.__points.append(tuple(self.sim_object.transform.position))

    def reset_trail(self):
        self.__points.clear()

    def render(self, surface: pygame.Surface, camera: Camera):
        if len(self.__points) >= 2:
            pygame.draw.lines(
                surface=surface,
                color=self.color,
                closed=False,
                points=[camera.world_to_screen(point) for point in self.__points],
                width=self.__thickness
            )
        if len(self.__points) >= 1:
            pygame.draw.line(
                surface=surface,
                color=self.color,
                start_pos=camera.world_to_screen(self.__points[-1]),
                end_pos=camera.world_to_screen(self.sim_object.transform.position),
                width=self.__thickness
            )

    def _on_destroy(self):
        self.sim_object.environment.event_system.remove_listener(TrailResetEvent, self.__handle_reset_event)
        self.sim_object.environment.event_system.remove_listener(PostPhysicsUpdateEvent,
                                                                 self.__handle_post_physics_event)

        super()._on_destroy()
