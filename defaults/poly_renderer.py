import pygame
from typing import Optional, Iterable, List, Sequence, Union
from sophysics_engine import Renderer, Color, Camera


number = Union[int, float]


class PolyRenderer(Renderer):
    """
    Renderer for polygons
    """
    def __init__(self, vertices: Iterable[Sequence[number]],
                 closed: bool = True, color = Color.WHITE, layer: int = 0):
        """
        For the vertices parameter you are free to pass an iterable with any type that has 2 attributes
        that can be accessed using [0] and [1], but internally they will be converted into
        pygame.Vector2 and stored as such.

        Vertices are described using x and y position in WORLD SPACE!
        """
        self._vertices: Optional[List[pygame.Vector2]] = None
        self._closed: bool = False

        self.closed = closed
        self.vertices = vertices

        super().__init__(color, layer)

    @property
    def vertices(self) -> List[pygame.Vector2]:
        """
        The list of vertices of the polygon in world coordinates
        """
        return self._vertices

    @vertices.setter
    def vertices(self, vertices: Iterable[Sequence[number]]):
        """
        For the vertices parameter you are free to pass an iterable with any type that has 2 attributes
        that can be accessed using [0] and [1], but internally they will be converted into
        pygame.Vector2 and stored as such.

        Vertices are described using x and y position in WORLD SPACE!
        """
        if(vertices is not None):
            self._vertices = [pygame.Vector2(v[0], v[1]) for v in vertices]
        else:
            self._vertices = []

    @property
    def closed(self) -> bool:
        """
        Describes whether the polygon is closed
        """
        return self._closed

    @closed.setter
    def closed(self, value: bool):
        self._closed = bool(value)

    def get_screen_vertices(self, camera: Camera) -> List[pygame.Vector2]:
        """
        The list of vertices of the polygon in screen coordinates
        """
        # loops through the self.vertices list and translates them into world coords
        return [pygame.Vector2(*camera.world_to_screen(vertex)) for vertex in self.vertices]

    def render(self, surface: pygame.Surface, camera: Camera):
        if not (len(self.vertices) >= 2):
            return

        pygame.draw.lines(surface, self.color, self.closed, self.get_screen_vertices(camera))
