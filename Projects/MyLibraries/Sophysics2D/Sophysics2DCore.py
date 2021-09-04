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
		self.is_active = True

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
			if(m.is_active):
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
		The _manager of the component
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

		transform_component = self.try_get_component(Transform)
		self._transform = Transform() if (transform_component is None) else transform_component
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


class RigidBody(Manageable):
	"""
	Handles the movement of the SimObject according to physics.
	"""
	# TODO
	def __init__(
			self,
			mass: number = 1,
			velocity: Optional[pygame.Vector2] = None):
		# initializing fields
		self._transform = None
		self._velocity = None
		self._mass = None
		self._forces: list[Force] = []

		# calling setters
		self.mass = mass
		self.velocity = pygame.Vector2() if (velocity is None) else velocity
		super().__init__()

	def start(self):
		super().start()

		self._transform = self.sim_object.transform

	def update(self):
		pass

	@property
	def mass(self):
		return self._mass

	@mass.setter
	def mass(self, value: number):
		validate_positive_number(value, "mass")

		self._mass = value

	@property
	def velocity(self):
		return self._velocity

	@velocity.setter
	def velocity(self, value: pygame.Vector2):
		if(not isinstance(value, pygame.Vector2)):
			raise TypeError("velocity must be a Vector2")

		self._velocity = value

	def attach_force(self, force):
		"""
		Attaches a force to a rigidbody
		"""
		if(not isinstance(force, Force)):
			raise TypeError("force must be a type of Force")

		self._forces.append(force)


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


class Renderer(Manageable):
	"""
	A base class for renderers

	Handles the rendering of an object
	"""
	def __init__(self, layer: int = 0):
		"""
		:param layer: objects on lower layers will be drawn first and may be occluded by objects on higher levels.
		"""
		self.layer = layer
		super().__init__(RenderManager)

	# def start(self):
	#   self._manager = self.sim_object.environment.get_component(RenderManager)
	#   self._manager.attach_manageable(self)

	def update(self):
		self.render()

	def render(self):
		pass


class RenderManager(Manager):
	"""
	Manages all the renderers.

	Provides methods for converting from World Coordinates into screenspace coordinates and vice versa
	"""
	# TODO rework the way layers work
	def __init__(
			self, surface: pygame.Surface,
			units_per_pixel: float = 1 / 80,
			background_color = (0, 0, 0)):
		# initializing to then call the setters, which would check if the values are valid
		self._surface = None
		self._units_per_pixel = None

		self.surface = surface
		self.units_per_pixel = units_per_pixel
		self.background_color = background_color

		super().__init__(Renderer)

	def attach_manageable(self, renderer: Renderer):
		"""
		attaches the renderer to the manager
		"""
		if(not isinstance(renderer, Renderer)):
			raise TypeError("A renderer object must be an instance of 'Renderer'")

		def get_index():
			"""
			calculates the index at which to insert the renderer
			based on its layer using binary search
			"""
			# start and end indices of the sublist in which we're searching
			# every iteration of the loop the sublist halves (that's how binary search works)
			start = 0
			end = len(self._manageables) - 1

			# a target for binary search
			target = renderer.layer

			while(start <= end):
				i = (start + end) // 2
				value = self._manageables[i].layer

				if(value == target):
					return i + 1

				# since on the end of the loop we might end up on a value
				# that's either smaller or larger than the target,
				# on the last iteration we return either i or i + 1 accordingly
				elif(target < value):
					if(start == end):
						return i
					end = i - 1
				else:
					if(start == end):
						return i + 1
					start = i + 1

			# return 0 if the loop never started
			# (i.e. the list is empty)
			return 0

		self._manageables.insert(get_index(), renderer)

	def update(self):
		"""
		Render the scene
		"""
		# Fills the background
		self.surface.fill(self.background_color)
		for r in self._manageables:
			if(r.is_active):
				r.update()

	@property
	def surface(self):
		return self._surface

	@surface.setter
	def surface(self, value: pygame.Surface):
		if(not isinstance(value, pygame.Surface)):
			raise TypeError("surface can only be of type pygame.Surface")

		self._surface = value

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
		surface_rect = self.surface.get_rect()
		screen_x = world_x * self.pixels_per_unit + surface_rect.centerx
		screen_y = - (world_y * self.pixels_per_unit) + surface_rect.centery
		return (screen_x, screen_y)

	def screen_to_world(self, screen_coords: Union[pygame.Vector2, Tuple[number, number]] = (0, 0)):
		"""
		Converts from a position on the screen into a position in the world
		"""
		screen_x, screen_y = screen_coords
		surface_rect = self.surface.get_rect()
		world_x = (screen_x - surface_rect.centerx) * self.units_per_pixel
		# this might cause world_y to be -0.0 in some cases, but it doesn't really matter.
		world_y = -(screen_y - surface_rect.centery) * self.units_per_pixel

		return (world_x, world_y)
