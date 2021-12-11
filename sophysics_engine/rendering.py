"""
A module with base components for rendering the scene
"""

from __future__ import annotations

import pygame

from abc import ABC, abstractmethod
from .simulation import EnvironmentComponent, SimObjectComponent, RenderEvent
from .event_system import EventSystem
from .event import Event
from typing import Optional, List, Union, Tuple
from .helper_functions import validate_positive_number


number = Union[int, float]


class Color:
    """
    A class containing constants for colors
    """
    TRANSPARENT = (0, 0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    BLACK = (0, 0, 0)


class Camera(EnvironmentComponent):
    """
    Manages all the renderers.

    Provides methods for converting from World Coordinates into screenspace coordinates and vice versa
    """
    def __init__(self, display: pygame.Surface,
                 position: Union[Tuple[number, number], List[number]] = (0, 0),
                 units_per_pixel: float = 1 / 80,
                 background_color = Color.BLACK,
                 n_layers: int = 32):
        """
        :param display: surface on which the image will be drawn
        :param units_per_pixel: number of world space units 1 pixel represents
        :param background_color: color of the background
        :param position: how much the camera is offset from the center of the screen (in pixels)
        :param n_layers: amount of layers. More layers give more flexibility, but take up more memory.
        """
        # initializing to then call the setters, which would check if the values are valid
        self._units_per_pixel: Optional[float] = None
        self._position = pygame.Vector2(position)

        self._display = display
        self.units_per_pixel = units_per_pixel
        self.background_color = background_color

        # layers are a list of surfaces. Each renderer has a layer that it draws on, to ensure that certain
        # elements are drawn on top of each other
        # after all drawing is done, the layers are blitted onto the display
        # before the drawing all layers are cleared (i.e. filled with the transparent color)
        self._layers: List[pygame.Surface] = []
        self.__create_layer_surfaces(n_layers)

        # tells the program which layers have been modified, unmodified layers will not be blitted onto the display
        # and the will not be cleared (since it is assumed that they're transparent)
        self.__layer_modified: List[bool] = [False] * n_layers

        super().__init__()

    def setup(self):
        self.environment.event_system.add_listener(RenderEvent, self.__handle_render_event)

    def __handle_render_event(self, _: RenderEvent):
        self.render_scene()

    def render_scene(self):
        """
        Render the scene
        """
        # Clear the screen
        self.display.fill(self.background_color)
        self.__clear_layer_surfaces()

        # render onto the layers
        self.environment.event_system.raise_event(CameraRenderEvent(self))

        # blit the layers onto the display
        for i, layer in enumerate(self._layers):
            if(self.__layer_modified[i]):
                self._display.blit(layer, (0, 0))

    def __create_layer_surfaces(self, n_layers: int):
        if(n_layers < 1):
            raise ValueError("The amount of layers cannot be lower than 1")

        for _ in range(n_layers):
            # create a surface that uses per pixel alpha
            surface = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
            # make the surface transparent
            surface.fill(Color.TRANSPARENT)
            self._layers.append(surface)

    def __clear_layer_surfaces(self):
        """
        Fills the layers with the transparent color
        """
        for i, layer in enumerate(self._layers):
            # only clear the surfaces that are modified
            # unmodified surfaces should already be transparent
            if not self.__layer_modified[i]:
                continue

            layer.fill(Color.TRANSPARENT)
            self.__layer_modified[i] = False

    def get_layer_for_rendering(self, index: int):
        """
        Get's the layer surface with the specified index and marks that layer as modified
        """
        self.__layer_modified[index] = True
        return self._layers[index]

    @property
    def position(self) -> pygame.Vector2:
        """
        The vector that describes how much the camera is offset from the world origin (in pixels).

        The x direction is right
        The y direction is up
        """
        return self._position

    @property
    def display(self) -> pygame.Surface:
        return self._display

    @display.setter
    def display(self, value: pygame.Surface):
        if(not isinstance(value, pygame.Surface)):
            raise TypeError("display can only be of type pygame.Surface")

        self._display = value

    @property
    def units_per_pixel(self) -> float:
        """
        Worldspace units per pixel on the screen
        """
        return self._units_per_pixel

    @units_per_pixel.setter
    def units_per_pixel(self, value: number):
        validate_positive_number(value, "units_per_pixel")

        self._units_per_pixel = value

    @property
    def pixels_per_unit(self) -> float:
        """
        pixels on the screen per worldspace unit
        """
        return 1 / self._units_per_pixel

    @pixels_per_unit.setter
    def pixels_per_unit(self, value: number):
        validate_positive_number(value, "pixels_per_unit")

        self._units_per_pixel = 1 / value

    def world_to_screen(self, world_coords: Union[pygame.Vector2, Tuple[number, number]]) -> Tuple[float, float]:
        """
        Converts a worldspace position into a position on the screen in pixels
        """
        world_x, world_y = world_coords
        surface_rect = self.display.get_rect()
        screen_x = world_x * self.pixels_per_unit + surface_rect.centerx - self.position.x
        screen_y = -(world_y * self.pixels_per_unit) + surface_rect.centery + self.position.y
        return (screen_x, screen_y)

    def screen_to_world(self, screen_coords: Union[pygame.Vector2, Tuple[number, number]]) -> Tuple[float, float]:
        """
        Converts from a position on the screen into a position in the world
        """
        screen_x, screen_y = screen_coords
        surface_rect = self.display.get_rect()
        world_x = (screen_x - surface_rect.centerx + self.position.x) * self.units_per_pixel
        # this might cause world_y to be -0.0 in some cases, but it doesn't really matter.
        world_y = -(screen_y - surface_rect.centery - self.position.y) * self.units_per_pixel

        return (world_x, world_y)

    def _on_destroy(self):
        self.environment.event_system.remove_listener(RenderEvent, self.__handle_render_event)


class Renderer(SimObjectComponent, ABC):
    """
    A base class for renderers

    Handles the rendering of an object
    """
    def __init__(self, color = Color.WHITE, layer: int = 0):
        """
        :param layer: objects on lower layers will be drawn first and may be occluded by objects on higher levels.
        """
        self.__is_active = True

        self._layer = None
        self.layer = layer

        self.color = color
        super().__init__()

    @property
    def is_active(self) -> bool:
        return self.__is_active

    @is_active.setter
    def is_active(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("'is_active' property should be a bool")

        self.__is_active = value

    def setup(self):
        event_system: EventSystem = self.sim_object.environment.event_system
        event_system.add_listener(CameraRenderEvent, self.__handle_render_event)

        super().setup()

    def __handle_render_event(self, event: CameraRenderEvent):
        if not self.is_active:
            return

        camera = event.camera
        surface = camera.get_layer_for_rendering(self._layer)

        self.render(surface, camera)

    @abstractmethod
    def render(self, surface: pygame.Surface, render_manager: Camera):
        """
        Render the object on a specific surface
        """
        pass

    @property
    def layer(self) -> int:
        return self._layer

    @layer.setter
    def layer(self, value: int):
        if(value < 0):
            raise ValueError("layer cannot be lower than zero")

        self._layer = value

    def _on_destroy(self):
        event_system = self.sim_object.environment.event_system
        event_system.remove_listener(CameraRenderEvent, self.__handle_render_event)


class CameraRenderEvent(Event):
    """
    An event raised by the camera when rendering the scene.

    Has a reference to the camera.
    """
    def __init__(self, render_manager: Camera):
        self.__camera = render_manager

    @property
    def camera(self) -> Camera:
        return self.__camera
