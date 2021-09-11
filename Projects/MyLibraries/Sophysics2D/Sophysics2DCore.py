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
	def start(self):
		"""
		Called when the simulation starts to prepare the component.

		I.e. get references to all necessary components, managers, etc.
		"""
		pass

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
		# a reference to the object
		# defaults to None, should be set by the object
		self.sim_object: Optional[SimObject] = None
		# DEPRECATED
		# a reference to the component's _manager
		# the _manager is responsible for calling the update() method on the component
		# self._manager: Optional[EnvironmentComponent] = None

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
		for c in self.components:
			if(isinstance(c, comp_type)):
				return c
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
		try:
			return self.get_component(comp_type)
		except ValueError:
			return None

	def has_component(self, comp_type: type) -> bool:
		"""
		Checks if the object has a component of a specified type.
		"""
		return (self.try_get_component(comp_type) is not None)


class Transform(SimObjectComponent):
	"""
	Holds information about position and rotation of the object.
	"""
	def __init__(
			self, position: pygame.Vector2 = None,
			rotation: float = 0):
		if(position is None):
			position = pygame.Vector2()
		self.position = position
		self.rotation = rotation
		super().__init__()


class SimObject(ComponentContainer):
	"""
	A container for SimObject Components. Must have a Transform
	"""
	def __init__(self, components: Iterable[SimObjectComponent] = ()):
		super().__init__(components)
		self.environment = None

		self._transform: Optional[Transform] = self.try_get_component(Transform)

		if(self._transform is None):
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

	def remove_component(self, component: SimObjectComponent):
		component.sim_object = None
		super().remove_component(component)


class SimEnvironment(ComponentContainer):
	"""
	A container for SimObjects and EnvironmentComponents.
	"""
	def __init__(
			self, sim_objects: Iterable[SimObject] = (),
			components: Iterable[EnvironmentComponent] = ()):
		super().__init__(components)
		# A flag that tells whether the start() method has been called
		self.__has_started = False
		self.sim_objects = []

		for o in sim_objects:
			self.attach_object(o)

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

		self.__has_started = True

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


class RigidBody(Manageable):
	"""
	Handles the movement of the SimObject according to physics.

	A wrapper for pymunk's shape and body
	"""
	def __init__(
			self,
			shape: pymunk.Shape = None,
			body_type: int = pymunk.Body.DYNAMIC):
		# initializing fields
		self._transform: Optional[Transform] = None
		self._space: Optional[pymunk.Space] = None
		self._forces: list[Force] = []
		self._body = pymunk.Body(body_type=body_type)
		self._shape = None

		if(shape is None):
			self._shape = pymunk.Circle(self._body, 1)
			self._shape.mass = 1
			self._shape.elasticity = 0.5
		else:
			self._shape = shape

		self._shape.body = self._body

		# calling setters
		super().__init__(RigidBodyManager)

	def start(self):
		super().start()

		self._transform = self.sim_object.transform
		self._space: pymunk.Space = self.manager.space
		self._space.add(self._body, self._shape)

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
	def shape(self) -> pymunk.Shape:
		"""
		Shape of the rigid body
		"""
		return self._shape

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


class RigidBodyManager(Manager):
	"""
	The manager for RigidBody components
	"""
	def __init__(self, dt: float = 1 / 60):
		super().__init__(RigidBody)
		self.dt = dt
		self._space = pymunk.Space()

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


class Renderer(Manageable):
	"""
	A base class for renderers

	Handles the rendering of an object
	"""
	def __init__(self, layer: int = 0):
		"""
		:param layer: objects on lower layers will be drawn first and may be occluded by objects on higher levels.
		"""
		self.is_active = True
		self._layer = layer
		super().__init__(RenderManager)

	# def start(self):
	#   self._manager = self.sim_object.environment.get_component(RenderManager)
	#   self._manager.attach_manageable(self)

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

	# colors
	TRANSPARENT = (0, 0, 0, 0)
	WHITE = (255, 255, 255)
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	YELLOW = (255, 255, 0)
	CYAN = (0, 255, 255)
	MAGENTA = (255, 0, 255)
	BLACK = (0, 0, 0)

	def __init__(
			self, display: pygame.Surface,
			units_per_pixel: float = 1 / 80,
			background_color = BLACK,
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
			surface.fill(self.TRANSPARENT)
			self._layers.append(surface)

	def __clear_layer_surfaces(self):
		"""
		Fills the layers with the transparent color
		"""
		for i, layer in enumerate(self._layers):
			if(self.__layer_modified[i]):
				layer.fill(self.TRANSPARENT)
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
