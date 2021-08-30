"""
The core structure of Sophysics2D
"""
# TODO refactor code, put classes into separate files
import pygame
from helperFunctions import *


class Component:
	"""
	A base class for Components
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
	A base class for SimObject components
	"""
	def __init__(self):
		# a reference to the object
		# defaults to None, should be set by the object
		self.sim_object: Optional[SimObject] = None
		# a reference to the component's manager
		# the manager is responsible for calling the update() method on the component
		self.manager: Optional[EnvironmentComponent] = None
		super().__init__()


class EnvironmentComponent(Component):
	"""
	A base class for environment components.

	Typically an EnvironmentComponent would call update() on every corresponding SimObjectComponent
	"""
	def __init__(self):
		# a reference to the environment
		# defaults to None, should be set by the environment
		self.environment: Optional[SimEnvironment] = None
		super().__init__()


class ComponentContainer:
	"""
	A base class for Component containers such as SimObject and SimEnvironment.
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


class BoundingBox:
	"""
	Abstract base class for BoundingBox objects.

	Represents a box around some object. Has properties describing top, bottom, left, and right edges of the box.
	Has a method for checking if the current bounding box intersects with another bounding box.
	"""
	# when overriding these, make sure they're properties
	# Those are supposed to be abstract, but pyCharm gives a warning if getters don't return anything
	# So, by default they return 0
	@property
	def top(self) -> number:
		"""
		Top edge of the bounding box.
		"""
		return 0

	@property
	def bottom(self) -> number:
		"""
		Bottom edge of the bounding box.
		"""
		return 0

	@property
	def left(self) -> number:
		"""
		Left edge of the bounding box.
		"""
		return 0

	@property
	def right(self) -> number:
		"""
		Right edge of the bounding box
		"""
		return 0

	def intersects_bounding_box(self, other) -> bool:
		"""
		Checks if this bounding box intersects another bounding box
		"""
		# check if the argument is valid
		# (thanks python for dynamic typing btw)
		if(not isinstance(other, BoundingBox)):
			raise TypeError("'other' must be of type BoundingBox")

		# check if boxes intersect on x and y axes
		x_intersect = intervals_intersect(self.left, self.right, other.left, other.right)
		y_intersect = intervals_intersect(self.bottom, self.top, other.bottom, other.top)

		return x_intersect and y_intersect


class BoundingVolume(BoundingBox):
	"""
	Represents a volume in space. Could be used for space partitioning.
	"""
	def __init__(self, top: number, bottom: number, left: number, right: number):
		"""
		:param top: top edge of the bounding box
		:param bottom: bottom edge of the bounding box
		:param left: left edge of the bounding box
		:param right: right edge of the bounding box
		"""
		# validate values
		validate_number(top, "parameter 'top'")
		validate_number(bottom, "parameter 'bottom'")
		validate_number(left, "parameter 'left'")
		validate_number(right, "parameter 'right'")

		# check if top >= bottom and right >= left
		if (top < bottom):
			raise ValueError("'top' is lower than 'bottom'")
		if (right < left):
			raise ValueError("'right' is lower than 'left'")

		# assign values
		self._top = top
		self._bottom = bottom
		self._left = left
		self._right = right

	@property
	def top(self):
		return self._top

	@top.setter
	def top(self, value: number):
		# validate value
		validate_number(value, "top argument")

		if(value < self._bottom):
			raise ValueError("top is lower than bottom")

		self._top = value

	@property
	def bottom(self):
		return self._bottom

	@bottom.setter
	def bottom(self, value: number):
		# validate value
		validate_number(value)

		if (self._top < value):
			raise ValueError("top is lower than bottom")

		# assign value
		self._bottom = value

	@property
	def left(self):
		return self._left

	@left.setter
	def left(self, value: number):
		# validate value
		validate_number(value)

		if (self._right < value):
			raise ValueError("right is lower than left")

		# assign value
		self._left = value

	@property
	def right(self):
		return self._right

	@right.setter
	def right(self, value: number):
		# validate value
		validate_number(value)

		if (value < self._left):
			raise ValueError("right is lower than right")

		# assign value
		self._right = value


class CollisionListener(SimObjectComponent):
	"""
	A base class for collision listeners.

	Collision listeners have on_collision method which
	gets called by the collider whenever it detects a collision
	"""
	def start(self):
		colliders = self.sim_object.get_components(Collider)

		for c in colliders:
			c.attach_collision_listener(self)

	def on_collision(self, other):
		"""
		Method that gets called when the corresponding sim object's collider detects a collision

		:param other: Collider of the object with which the collision was detected
		"""
		pass


class Collider(SimObjectComponent, BoundingBox):
	"""
	A base class for colliders.

	Colliders check for collisions with other sim objects.
	"""
	# !IMPORTANT! When inheriting, don't forget to override top, bottom, left, right properties
	def __init__(self):
		super().__init__()
		self._listeners: list[CollisionListener] = []

	def start(self):
		self.manager = self.sim_object.environment.get_component(ColliderManager)
		self.manager.attach_collider(self)

	def attach_collision_listener(self, listener: CollisionListener):
		"""
		Attaches a listener to the collider. When the collider detects a collision
		it calls the on_collision method on all of its listeners.
		"""
		if(not isinstance(listener, CollisionListener)):
			raise TypeError("listener must be of type CollisionListener")

		self._listeners.append(listener)

	def check_collision(self, other):
		"""
		Checks if this collider collides with the 'other' collider.
		"""
		pass

	def on_collision(self, other):
		"""
		Method to be called when the collision with 'other' is detected

		Calls on_collision on every collision listener
		"""
		if(not isinstance(other, Collider)):
			raise TypeError("'other' must be an instance of 'Collider'")

		print("Collision")

		for listener in self._listeners:
			listener.on_collision(other)


class ColliderManager(EnvironmentComponent):
	"""
	A manager for Colliders
	"""
	def __init__(self):
		self._colliders: list[Collider] = []

		super().__init__()

	def attach_collider(self, collider: Collider):
		"""
		attaches the collider to the manager
		"""
		if(not isinstance(collider, Collider)):
			raise TypeError("A collider object must be an instance of 'Collider'")

		self._colliders.append(collider)

	def update(self):
		checked_pairs = []
		# TODO implement sweep and prune (or maybe even some kind if object partitioning)
		# check collision in pairs
		for i in self._colliders:
			for j in self._colliders:
				# skip if i and j are the same collider or if i and j were already checked
				if(i is j or (i, j) in checked_pairs or (j, i) in checked_pairs):
					continue
				i.check_collision(j)
				checked_pairs.append((i, j))


class RigidBody(CollisionListener):
	"""
	Handles the movement of the SimObject according to physics.
	"""
	# TODO
	def __init__(
			self,
			mass: number = 1,
			velocity: Optional[pygame.Vector2] = None,
			acceleration: Optional[pygame.Vector2] = None):
		# initializing fields
		self._transform = None
		self._velocity = None
		self._acceleration = None
		self._mass = None
		self._forces: list[Force] = []

		# calling setters
		self.mass = mass
		self.velocity = pygame.Vector2() if (velocity is None) else velocity
		self.acceleration = pygame.Vector2() if (acceleration is None) else acceleration
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

	@property
	def acceleration(self):
		return self._acceleration

	@acceleration.setter
	def acceleration(self, value):
		if (not isinstance(value, pygame.Vector2)):
			raise TypeError("acceleration must be a Vector2")

		self._acceleration = value

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


class Renderer(SimObjectComponent):
	"""
	A base class for renderers

	Handles the rendering of an object
	"""
	def __init__(self, layer: int = 0):
		"""
		:param layer: objects on lower layers will be drawn first and may be occluded by objects on higher levels.
		"""
		self.layer = layer
		super().__init__()

	def start(self):
		self.manager = self.sim_object.environment.get_component(RenderManager)
		# self.manager.renderers.append(self)
		self.manager.attach_renderer(self)

	def update(self):
		self.render()

	def render(self):
		pass


class RenderManager(EnvironmentComponent):
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
		# self._units_per_pixel = units_per_pixel TODO check if it works or not
		self.units_per_pixel = units_per_pixel
		self.background_color = background_color

		self._renderers: list[Renderer] = []
		super().__init__()

	number = Union[int, float]		# a shortcut for typing

	@property
	def renderers(self):
		"""
		returns a copy of the renderers list.
		"""
		return self._renderers.copy()

	def attach_renderer(self, renderer: Renderer):
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
			end = len(self._renderers) - 1

			# a target for binary search
			target = renderer.layer

			while(start <= end):
				i = (start + end) // 2
				value = self._renderers[i].layer

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

		self._renderers.insert(get_index(), renderer)

	def update(self):
		"""
		Render the scene
		"""
		# Fills the background
		self.surface.fill(self.background_color)
		for r in self.renderers:
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
