"""
The core structure of Sophysics2D
"""
# TODO refactor code, put classes into separate files
import pygame
import pymunk
from helperFunctions import *


class Component:
    """
    The base class for Components
    """
    def __init__(self):
        self._started: bool = False

    @property
    def started(self) -> bool:
        """
        A boolean that tells whether the start method has been called
        """
        return self._started

    def start(self):
        """
        Called when the simulation starts to prepare the component.

        I.e. get references to all necessary components, managers, etc.
        """
        self._started = True

    def update(self):
        """
        Gets called every timestep of the simulation
        """
        pass


class SimObjectComponent(Component):
    """
    The base class for SimObject components
    """
    def __init__(self):
        self.sim_object: Optional[SimObject] = None
        super().__init__()


class EnvironmentComponent(Component):
    """
    The base class for environment components.

    Typically an EnvironmentComponent would call update() on every corresponding SimObjectComponent
    """
    def __init__(self):
        # a reference to the environment
        # defaults to None, should be set by the environment
        self.environment: Optional[SimEnvironment] = None
        super().__init__()


class Manager(EnvironmentComponent):
    """
    The base class for managers

    Managers provide an efficient way for the environment to communicate with sim object components
    """
    def __init__(self, manageable_type: type = None):
        # Type of the objects that the _manager manages
        self._manageable_type: type = Manageable if manageable_type is None else manageable_type
        self._manageables: list[manageable_type] = []
        super().__init__()

    @property
    def manageables(self):
        """
        Returns a copy of the manageables list
        """
        return self._manageables.copy()

    def attach_manageable(self, manageable: SimObjectComponent):
        """
        Attaches a manageable object to the _manager.
        """
        if(not isinstance(manageable, self._manageable_type)):
            raise TypeError(f"A manageable object must be an instance of '{self._manageable_type.__name__}'")

        self._manageables.append(manageable)

    def update(self):
        for m in self._manageables:
            m.update()


class Manageable(SimObjectComponent):
    """
    An object that's managed by a _manager
    """
    def __init__(self, manager_type: type = Manager):
        self._manager_type = manager_type
        self._manager = None

        super().__init__()

    @property
    def manager(self):
        """
        The manager of the component
        """
        return self._manager

    def start(self):
        self._manager = self.sim_object.environment.get_component(self._manager_type)
        self._manager.attach_manageable(self)
        super().start()


class ComponentContainer:
    """
    The base class for Component containers such as SimObject and SimEnvironment.
    """
    def __init__(self, components: Iterable[Component] = ()):
        self.components = []

        for c in components:
            self.attach_component(c)

    def attach_component(self, component: Component):
        """
        Attaches component to the object.

        Supposed to be overridden in order to connect the component to the container
        """
        # an override method would add something like this
        # component.sim_object = self
        if(not isinstance(component, Component)):
            raise TypeError("component must be of type Component")

        self.components.append(component)

    def remove_component(self, component: Component):
        """
        Removes the component from the container
        """
        self.components.remove(component)

    def get_component(self, comp_type: type) -> Any:
        """
        Returns the first component of a specified type.

        If the component isn't found raises ValueError
        """
        component = self.try_get_component(comp_type)
        if component is not None:
            return component

        raise ValueError(f"component {comp_type} not found")

    def get_components(self, comp_type: type) -> Any:
        """
        Returns a list of all components of a specified type.

        If no components were found returns an empty list.
        """
        components = []

        for c in self.components:
            if(isinstance(c, comp_type)):
                components.append(c)

        return components

    def try_get_component(self, comp_type: type) -> Any:
        """
        Returns a component of a specified type or None if the component wasn't found.
        """
        component = None
        for c in self.components:
            if(isinstance(c, comp_type)):
                component = c

        return component

    def has_component(self, comp_type: type) -> bool:
        """
        Checks if the object has a component of a specified type.
        """
        return (self.try_get_component(comp_type) is not None)


class Transform(SimObjectComponent):
    """
    Holds information about position and rotation of the object.
    """
    def __init__(self, position: pygame.Vector2 = None,
                 rotation: float = 0):
        if(position is None):
            position = pygame.Vector2()
        self._position = position
        self.rotation = rotation
        super().__init__()

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Sequence[float]):
        self._position.x = value[0]
        self._position.y = value[1]


class SimObject(ComponentContainer):
    """
    A container for SimObject Components. Must have a Transform
    """
    def __init__(self, components: Iterable[SimObjectComponent] = ()):
        self.environment = None
        super().__init__(components)

        self._transform: Optional[Transform] = self.try_get_component(Transform)

        if (self._transform is None):
            self._transform = Transform()
            self.attach_component(self.transform)

    @property
    def transform(self):
        return self._transform

    # overriding a method to connect the component to self
    def attach_component(self, component: SimObjectComponent):
        """
        Attaches component to the object
        """
        component.sim_object = self
        super().attach_component(component)

        if self.environment is not None and self.environment.started:
            component.start()

    def remove_component(self, component: SimObjectComponent):
        component.sim_object = None
        super().remove_component(component)


class SimEnvironment(ComponentContainer):
    """
    A container for SimObjects and EnvironmentComponents.
    """
    def __init__(self, sim_objects: Iterable[SimObject] = (),
                 components: Iterable[EnvironmentComponent] = ()):
        # A flag that tells whether the start() method has been called
        self._started = False
        self.sim_objects = []

        for o in sim_objects:
            self.attach_object(o)

        super().__init__(components)

    @property
    def started(self):
        """
        A bool that says_whether the environment has started or not
        """
        return self._started

    def attach_object(self, sim_object: SimObject):
        """
        Attaches an object to the environment.
        """
        sim_object.environment = self
        self.sim_objects.append(sim_object)

    # overriding a method to connect the component to self
    def attach_component(self, component: EnvironmentComponent):
        """
        Attaches a component to the environment.
        """
        component.environment = self
        super().attach_component(component)

        if self._started:
            component.start()

    def remove_component(self, component: EnvironmentComponent):
        component.environment = None
        super().remove_component(component)

    def start(self):
        """
        Calls start() on all environment components and sim object components.

        Gets necessary references for use in other methods
        """
        for env_component in self.components:
            env_component.start()

        for sim_object in self.sim_objects:
            for component in sim_object.components:
                component.start()

        self._started = True

    def advance(self):
        """
        Advance 1 step forward.

        Abstract
        """
        pass

    def render(self):
        """
        Renders a snapshot of the simulation

        Abstract
        """
        pass


class Force(SimObjectComponent):
    """
    A base class for Force components.

    Force component passes force to the rigidbody of the sim_object
    """
    def __init__(self):
        self._rigidbody = None
        super().__init__()

    def start(self):
        self._rigidbody: RigidBody = self.sim_object.get_component(RigidBody)
        self._rigidbody.attach_force(self)
        super().start()


class CollisionListener(SimObjectComponent):
    """
    A collision listener contains methods that get called whenever the sim object it is attached to
    is colliding with another sim object.
    """
    def __init__(self):
        self._rigidbody: Optional[RigidBody] = None

        super().__init__()

    def start(self):
        self._rigidbody = self.sim_object.get_component(RigidBody)
        self._rigidbody.attach_collision_listener(self)

    def begin(self, other_body, arbiter: pymunk.Arbiter) -> bool:
        """
        Two shapes just started touching for the first time this step.

        Return true from the callback to process the collision normally or false
        to cause pymunk to ignore the collision entirely. If you return false,
        the pre_solve and post_solve callbacks will never be run, but you will still
        receive a separate event when the shapes stop overlapping.

        When returning a bool, be aware that the final value, that determines whether the collision will be processed
        is the 'and' operation of all return values of all collision listeners on both bodies.
        """
        pass

    def pre_solve(self, other_body, arbiter: pymunk.Arbiter) -> bool:
        """
        Two shapes are touching and their collision response has been processed.

        Return false from the callback to make pymunk ignore the collision this
        step or true to process it normally. Additionally, you may override collision
        values using Arbiter.friction, Arbiter.elasticity or Arbiter.surfaceVelocity to provide custom
        friction, elasticity, or surface velocity values.

        When returning a bool, be aware that the final value, that determines whether the collision will be processed
        is the 'and' operation of all return values of all collision listeners on both bodies.
        """
        pass

    def post_solve(self, other_body, arbiter: pymunk.Arbiter):
        """
        Two shapes are touching and their collision response has been processed.

        You can retrieve the collision impulse or kinetic energy at this time if you want
        to use it to calculate sound volumes or damage amounts.
        """
        pass

    def separate(self, other_body, arbiter: pymunk.Arbiter):
        """
        Two shapes have just stopped touching for the first time this step.

        To ensure that begin()/separate() are always called in balanced pairs,
        it will also be called when removing a shape while its in contact with something
        or when de-allocating the space.
        """
        pass


class RigidBody(Manageable):
    """
    Handles the movement of the SimObject according to physics.

    A wrapper for pymunk's shape and body
    """
    def __init__(self, shapes: Iterable[pymunk.Shape] = (),
                 body_type: int = pymunk.Body.DYNAMIC):
        super().__init__(RigidBodyManager)

        # initializing fields
        self._transform: Optional[Transform] = None
        self._space: Optional[pymunk.Space] = None
        self._forces: list[Force] = []
        self._body: pymunk.Body = SophysicsBody(self, body_type=body_type)
        self._shapes: list[pymunk.Shape] = []
        self._collision_listeners: list[CollisionListener] = []

        # attaching the shapes
        for s in shapes:
            self.attach_shape(s)

        # setting a default shape (if no shapes were passed)
        if(len(self.shapes) <= 0):
            default_shape = pymunk.Circle(self._body, 1)
            default_shape.mass = 1
            default_shape.elasticity = 0.5
            self.attach_shape(default_shape)

    def start(self):
        super().start()

        self._transform = self.sim_object.transform
        self._space: pymunk.Space = self.manager.space
        self._space.add(self._body, *self.shapes)

        # syncing the pymunk body position and sim_object's position
        # (doing that awkwardness because pymunk and pygame use different Vector classes)
        # (Both are iterables so we can unpack like that)
        self._body.position = pymunk.Vec2d(*self._transform.position)

    def update(self):
        self.__sync_body_with_sim_object()

        for force in self._forces:
            force.update()

    def post_update(self):
        """
        Executes after all physics calculations were done for the current timestep

        Updates the sim_object's position to match the pymunk's body position
        """
        self.__sync_sim_object_with_body()

    def __sync_sim_object_with_body(self):
        """
        Synchronizes the orientation of the sim_object with the pymunk body
        """
        self._transform.position.x = self._body.position.x
        self._transform.position.y = self._body.position.y
        self._transform.rotation = self._body.angle

    def __sync_body_with_sim_object(self):
        """
        Synchronizes the orientation of the pymunk body with the sim_object
        """
        # In case the sim_object's position was updated externally
        self._body.position = pymunk.Vec2d(*self._transform.position)
        self._body.angle = self._transform.rotation
        self._space.reindex_shapes_for_body(self._body)

    @property
    def body(self) -> pymunk.Body:
        return self._body

    @property
    def shapes(self) -> list[pymunk.Shape]:
        """
        A list of shapes attached to the rigidbody
        """
        return self._shapes

    @property
    def velocity(self) -> pymunk.Vec2d:
        """
        The object's velocity
        """
        return self._body.velocity

    @velocity.setter
    def velocity(self, value: Iterable[number]):
        """
        velocity must be an iterable with at least 2 items, e.g. pygame.Vector2, pymunk.Vec2d, a tuple, a list or
        any user defined iterable type.

        The first two items represent the x and y components of the velocity vector respectively. Any subsequent items
        are ignored.

        Under the hood the velocity is represented as pymunk.Vec2d
        """
        value_iterator = iter(value)
        x = next(value_iterator)
        y = next(value_iterator)

        self._body.velocity = pymunk.Vec2d(x, y)

    def attach_shape(self, shape: pymunk.Shape):
        """
        Attaches the shape to the rigidbody
        """
        if(not isinstance(shape, pymunk.Shape)):
            raise TypeError("shape should be an instance of pymunk.Shape")

        shape.body = self._body
        self._shapes.append(shape)

        if(self.started):
            self._space.add(shape)

    def remove_shape(self, shape: pymunk.Shape):
        """
        Removes the shape from the rigidbody
        """
        if (not isinstance(shape, pymunk.Shape)):
            raise TypeError("shape should be an instance of pymunk.Shape")

        shape.body = None
        self._shapes.remove(shape)

        if(self.started):
            self._space.remove(shape)

    @property
    def mass(self) -> float:
        """
        Same as RigidBody.body.mass
        """
        return self._body.mass

    @mass.setter
    def mass(self, value: float):
        validate_positive_number(value, "mass")

        self._body.mass = value

    def attach_force(self, force: Force):
        """
        Attaches a force component to the list of forces
        """
        if(not isinstance(force, Force)):
            raise TypeError("force must be a type of Force")

        self._forces.append(force)

    def remove_force(self, force: Force):
        """
        Removes a force component from the list of forces
        """
        self._forces.remove(force)

    def apply_force(self, force: Sequence[number]):
        """
        Applies a force to the center of mass of the object's pymunk body
        """
        x = force[0]
        y = force[1]

        self._body.apply_force_at_local_point((x, y))

    def attach_collision_listener(self, listener: CollisionListener):
        """
        adds a collision listener to the list of collision listeners
        """
        if (not isinstance(listener, CollisionListener)):
            raise TypeError("listener argument has to be of type CollisionListener")

        self._collision_listeners.append(listener)

    def remove_collision_listener(self, listener: CollisionListener):
        if (not isinstance(listener, CollisionListener)):
            raise TypeError("listener argument has to be of type CollisionListener")

        self._collision_listeners.remove(listener)

    @property
    def collision_listeners(self) -> list[CollisionListener]:
        """
        all collision listeners attached to this
        """
        return self._collision_listeners


class SophysicsBody(pymunk.Body):
    """
    A subclass of pymunk.Body that includes a reference to the Sophysics RigidBody component
    """
    def __init__(self, rigidbody: RigidBody, mass: float = 0,
                 moment: float = 0, body_type: int = pymunk.Body.DYNAMIC):

        if (not isinstance(rigidbody, RigidBody)):
            raise TypeError("rigidbody argument has to be a type of RigidBody")

        self._rigidbody = rigidbody

        super().__init__(mass, moment, body_type)

    @property
    def rigidbody(self) -> RigidBody:
        """
        A reference to the Sophysics RigidBody component
        """
        return self._rigidbody


class RigidBodyManager(Manager):
    """
    The manager for RigidBody components
    """
    def __init__(self, dt: float = 1 / 60):
        super().__init__(RigidBody)		# giving the type of the manageable to the superclass initializer
        self.dt: float = dt
        self._space: pymunk.Space = pymunk.Space()
        self.__initialize_collision_callback_functions()

    def __initialize_collision_callback_functions(self):
        """
        configures collision callbacks to call collision listeners
        """

        # these functions iterate over all the collision listeners attached to the 2 bodies and call respective
        # methods on them
        def begin(arbiter: pymunk.Arbiter, *_) -> bool:
            shapes = arbiter.shapes
            body1: RigidBody = shapes[0].body.rigidbody
            body2: RigidBody = shapes[1].body.rigidbody

            process_collision = True

            # call the method on all collision listeners that are attached to the 2 colliding bodies
            for listener in body1.collision_listeners:
                result = listener.begin(body2, arbiter)
                process_collision = process_collision and result if result is not None else process_collision

            for listener in body2.collision_listeners:
                result = listener.begin(body1, arbiter)
                process_collision = process_collision and result if result is not None else process_collision

            return process_collision

        def pre_solve(arbiter: pymunk.Arbiter, *_) -> bool:
            shapes = arbiter.shapes
            body1: RigidBody = shapes[0].body.rigidbody
            body2: RigidBody = shapes[1].body.rigidbody

            process_collision = True

            # call the method on all collision listeners that are attached to the 2 colliding bodies
            for listener in body1.collision_listeners:
                result = listener.pre_solve(body2, arbiter)
                process_collision = process_collision and result if result is not None else process_collision

            for listener in body2.collision_listeners:
                result = listener.pre_solve(body1, arbiter)
                process_collision = process_collision and result if result is not None else process_collision

            return process_collision

        def post_solve(arbiter: pymunk.Arbiter, *_):
            shapes = arbiter.shapes
            body1: RigidBody = shapes[0].body.rigidbody
            body2: RigidBody = shapes[1].body.rigidbody

            # call the method on all collision listeners that are attached to the 2 colliding bodies
            for listener in body1.collision_listeners:
                listener.post_solve(body2, arbiter)

            for listener in body2.collision_listeners:
                listener.post_solve(body1, arbiter)

        def separate(arbiter: pymunk.Arbiter, *_):
            shapes = arbiter.shapes
            body1: RigidBody = shapes[0].body.rigidbody
            body2: RigidBody = shapes[1].body.rigidbody

            # call the method on all collision listeners that are attached to the 2 colliding bodies
            for listener in body1.collision_listeners:
                listener.separate(body2, arbiter)

            for listener in body2.collision_listeners:
                listener.separate(body1, arbiter)

        collision_handler = self._space.add_default_collision_handler()
        collision_handler.begin = begin
        collision_handler.pre_solve = pre_solve
        collision_handler.post_solve = post_solve
        collision_handler.separate = separate

    @property
    def space(self):
        """
        The reference to the current pymunk's simulation space
        """
        return self._space

    def update(self):
        for rb in self.manageables:
            rb.update()

        self._space.step(self.dt)

        for rb in self.manageables:
            rb.post_update()


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


class Renderer(Manageable):
    """
    A base class for renderers

    Handles the rendering of an object
    """
    def __init__(self, color = Color.WHITE, layer: int = 0):
        """
        :param layer: objects on lower layers will be drawn first and may be occluded by objects on higher levels.
        """
        self.is_active = True

        self._layer = None
        self.layer = layer

        self.color = color
        super().__init__(RenderManager)

    def render(self, surface: pygame.Surface):
        pass

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value: int):
        if(value < 0):
            raise ValueError("layer cannot be lower than zero")

        self._layer = value


class RenderManager(Manager):
    """
    Manages all the renderers.

    Provides methods for converting from World Coordinates into screenspace coordinates and vice versa
    """
    def __init__(self, display: pygame.Surface,
                 units_per_pixel: float = 1 / 80,
                 background_color = Color.BLACK,
                 n_layers: int = 32):
        """
        :param display: surface on which the image will be drawn
        :param units_per_pixel: number of world space units 1 pixel represents
        :param background_color: color of the background
        :param n_layers: amount of layers. More layers give more flexibility, but take up more memory.
        """
        # initializing to then call the setters, which would check if the values are valid
        self._surface: Optional[pygame.Surface] = None
        self._units_per_pixel: Optional[float] = None

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

        super().__init__(Renderer)

    def update(self):
        """
        Render the scene
        """
        # Clear the screen
        self.display.fill(self.background_color)
        self.__clear_layer_surfaces()

        # render onto the layers
        for renderer in self._manageables:
            if(renderer.is_active):
                renderer.render(self._layers[renderer.layer])
                self.__layer_modified[renderer.layer] = True

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
            if(self.__layer_modified[i]):
                layer.fill(Color.TRANSPARENT)
                self.__layer_modified[i] = False

    @property
    def display(self):
        return self._display

    @display.setter
    def display(self, value: pygame.Surface):
        if(not isinstance(value, pygame.Surface)):
            raise TypeError("display can only be of type pygame.Surface")

        self._display = value

    @property
    def units_per_pixel(self):
        """
        Worldspace units per pixel on the screen
        """
        return self._units_per_pixel

    @units_per_pixel.setter
    def units_per_pixel(self, value: number):
        validate_positive_number(value, "units_per_pixel")

        self._units_per_pixel = value

    @property
    def pixels_per_unit(self):
        """
        pixels on the screen per worldspace unit
        """
        return 1 / self._units_per_pixel

    @pixels_per_unit.setter
    def pixels_per_unit(self, value: number):
        validate_positive_number(value, "pixels_per_unit")

        self._units_per_pixel = 1 / value

    def world_to_screen(self, world_coords: Union[pygame.Vector2, Tuple[number, number]] = (0, 0)):
        """
        Converts a worldspace position into a position on the screen in pixels
        """
        world_x, world_y = world_coords
        surface_rect = self.display.get_rect()
        screen_x = world_x * self.pixels_per_unit + surface_rect.centerx
        screen_y = - (world_y * self.pixels_per_unit) + surface_rect.centery
        return (screen_x, screen_y)

    def screen_to_world(self, screen_coords: Union[pygame.Vector2, Tuple[number, number]] = (0, 0)):
        """
        Converts from a position on the screen into a position in the world
        """
        screen_x, screen_y = screen_coords
        surface_rect = self.display.get_rect()
        world_x = (screen_x - surface_rect.centerx) * self.units_per_pixel
        # this might cause world_y to be -0.0 in some cases, but it doesn't really matter.
        world_y = -(screen_y - surface_rect.centery) * self.units_per_pixel

        return (world_x, world_y)
