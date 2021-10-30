import pygame.draw

from Sophysics2DCore import *


class CircleRenderer(Renderer):
    """
    Renderer for circles
    """
    # maybe add stuff like stroke width stroke and fill colors, etc, whatever, probably not this year
    def __init__(self, radius: Union[int, float] = 1, color = Color.WHITE, layer: int = 0):
        validate_positive_number(radius, "radius")

        self.__world_radius = 0
        self.radius = radius

        super().__init__(color, layer)

    @property
    def radius(self):
        """
        Radius of the circle in world coordinates.
        """
        return self.__world_radius

    @radius.setter
    def radius(self, value: number):
        validate_positive_number(value, "radius")

        self.__world_radius = value

    @property
    def pixel_radius(self):
        """
        Radius of the circle in pixels on the screen
        """
        return self.__world_radius * self._manager.pixels_per_unit

    @pixel_radius.setter
    def pixel_radius(self, value: number):
        validate_positive_number(value, "radius")

        self.__world_radius = value * self._manager.units_per_pixel

    def render(self, surface: pygame.Surface):
        world_position = self.sim_object.transform.position
        screen_position = self._manager.world_to_screen(world_position)

        pygame.draw.circle(surface, self.color, screen_position, self.pixel_radius)


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
        self._vertices = None
        self._closed = None

        self.closed = closed
        self.vertices = vertices

        super().__init__(color, layer)

    @property
    def vertices(self) -> list[pygame.Vector2]:
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

    @property
    def screen_vertices(self) -> list[pygame.Vector2]:
        """
        The list of vertices of the polygon in screen coordinates
        """
        # loops through the self.vertices list
        return [pygame.Vector2(*self.manager.world_to_screen(vertex)) for vertex in self.vertices]

    def render(self, surface: pygame.Surface):
        if(len(self.vertices) >= 2):
            pygame.draw.lines(surface, self.color, self.closed, self.screen_vertices)


class DefaultEnvironment(SimEnvironment):
    def __init__(self, sim_objects: Iterable[SimObject] = (), components: Iterable[EnvironmentComponent] = ()):
        self.rigidbody_manager: Optional[RigidBodyManager] = None
        self.render_manager: Optional[RenderManager] = None         # will be set later in setup()
        super().__init__(sim_objects, components)

    def _setup(self):
        # get the necessary references
        self.render_manager = self.get_component(RenderManager)
        self.rigidbody_manager = self.get_component(RigidBodyManager)

        # will call setup() on all components and sim_objects
        super()._setup()

    def advance(self):
        self.rigidbody_manager.update()
        super().advance()

    def render(self):
        """
        Renders a snapshot of the simulation
        """
        self.render_manager.update()


class ConstantAcceleration(Force):
    """
    A force that accelerates the body a certain amount of units per second. Could be used to simulate the
    acceleration due to gravity.
    """
    def __init__(self, acceleration: Sequence[number] = (0, 0)):
        """
        acceleration must be an sequence with at least 2 items, e.g. pygame.Vector2, pymunk.Vec2d, a tuple, a list or
        any user defined type that has a __getitem__ method and at least 2 items.

        The first two items represent the x and y components of the acceleration respectively. Any subsequent items
        are ignored.

        Under the hood the acceleration is represented as pygame.Vector2
        """
        super().__init__()

        self._acceleration: Optional[pygame.Vector2] = None
        self.acceleration = acceleration

    @property
    def acceleration(self) -> pygame.Vector2:
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value: Iterable[number]):
        """
        acceleration must be an iterable with at least 2 items, e.g. pygame.Vector2, pymunk.Vec2d, a tuple, a list or
        any user defined iterable type.

        The first two items represent the x and y components of the acceleration respectively. Any subsequent items
        are ignored.

        Under the hood the acceleration is represented as pygame.Vector2
        """
        value_iterator = iter(value)

        x = next(value_iterator)
        y = next(value_iterator)
        self._acceleration = pygame.Vector2(x, y)

    def update(self):
        # applies the force that causes a particular acceleration
        # From the Newton's second law
        # F = m * a
        mass = self._rigidbody.mass
        force = mass * self._acceleration

        self._rigidbody.apply_force(force)


def get_circle_body(tag: str = "", mass: number = 1, elasticity: number = 1, radius: number = 1,
                    color = Color.WHITE, layer: int = 0,
                    components: Iterable[SimObjectComponent] = ()):
    """
    A factory function for creating a sim_object that models a circle
    and has a CircleCollider and a CircleRenderer
    """
    # kinda like a prefab in Unity
    shape = pymunk.Circle(None, radius)
    shape.mass = mass
    shape.elasticity = elasticity
    rigidbody = RigidBody((shape,))
    renderer = CircleRenderer(radius, color, layer)

    return SimObject(tag, components=(renderer, rigidbody, *components))


def get_border_object(tag: str, up: number, down: number, left: number, right: number,
                      elasticity: number = 1, color = Color.WHITE, layer: int = 0,
                      components: Iterable[SimObjectComponent] = ()):
    """
    A factory function for creating a border object for the simulation

    up: the upper edge of the border

    down: the lower edge of the border

    left: the left edge of the border

    right: the right edge of the border
    """
    # Since poly shape is convex, and we need the border to be concave,
    # instead we're gonna make it with 4 segment shapes
    # --------------------------------------------------------------
    # First we check if top >= bottom and right >= left
    if(up < down):
        raise ValueError("up is lower than down")
    if(right < left):
        raise ValueError("right is lower than left")

    # Convert side coordinates into vertices
    a = (left, up)
    b = (right, up)
    c = (right, down)
    d = (left, down)

    # creating a renderer
    renderer = PolyRenderer((a, b, c, d), True, color, layer)

    # create a segment for each side
    ab = pymunk.Segment(None, a, b, 0)
    bc = pymunk.Segment(None, b, c, 0)
    cd = pymunk.Segment(None, c, d, 0)
    da = pymunk.Segment(None, d, a, 0)

    # setting the mass and elasticity for the segments
    for segment in (ab, bc, cd, da):
        segment.mass = 1
        segment.elasticity = elasticity

    # creating the body
    rigidbody = RigidBody((ab, bc, cd, da), pymunk.Body.STATIC)

    # packing everything into a sim_object and returning
    return SimObject(tag, components=(renderer, rigidbody, *components))
