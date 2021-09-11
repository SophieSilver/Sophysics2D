import pygame.draw

from Sophysics2DCore import *


class CircleRenderer(Renderer):
	"""
	Renderer for circles
	"""
	# maybe add stuff like stroke width stroke and fill colors, etc, whatever, probably not this year
	def __init__(self, radius: Union[int, float] = 1, color = (255, 255, 255), layer: int = 0):
		validate_positive_number(radius, "radius")

		self.__world_radius = 0
		self.radius = radius

		self.color = color
		super().__init__(layer)

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

	@property
	def diameter(self):
		"""
		Diameter of the circle in world coordinates
		"""
		return self.__world_radius * 2

	@diameter.setter
	def diameter(self, value: number):
		validate_positive_number(value, "diameter")

		self.radius = value / 2

	@property
	def pixel_diameter(self):
		"""
		Diameter of the circle in pixels on the screen
		"""
		return self.pixel_radius * 2

	@pixel_diameter.setter
	def pixel_diameter(self, value: number):
		validate_positive_number(value, "diameter")

		self.pixel_radius = value / 2

	def render(self, surface: pygame.Surface):
		world_position = self.sim_object.transform.position
		screen_position = self._manager.world_to_screen(world_position)

		pygame.draw.circle(surface, self.color, screen_position, self.pixel_radius)


class DefaultEnvironment(SimEnvironment):
	def __init__(self, sim_objects: Iterable[SimObject] = (), components: Iterable[EnvironmentComponent] = ()):
		super().__init__(sim_objects, components)
		self.rigidbody_manager: Optional[RigidBodyManager] = None
		self.render_manager: Optional[RenderManager] = None         # will be set later in start()

	def start(self):
		# get the necessary references
		self.render_manager = self.get_component(RenderManager)
		self.rigidbody_manager = self.get_component(RigidBodyManager)

		# will call start() on all components and sim_objects
		super().start()

	def advance(self):
		self.rigidbody_manager.update()

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
	def acceleration(self, value: Sequence[number]):
		"""
		acceleration must be an sequence with at least 2 items, e.g. pygame.Vector2, pymunk.Vec2d, a tuple, a list or
		any user defined type that has a __getitem__ method and at least 2 items.

		The first two items represent the x and y components of the acceleration respectively. Any subsequent items
		are ignored.

		Under the hood the acceleration is represented as pygame.Vector2
		"""
		x = value[0]
		y = value[1]
		self._acceleration = pygame.Vector2(x, y)

	def update(self):
		# applies the force that causes a particular acceleration
		# From the Newton's second law
		# F = m * a
		mass = self._rigidbody.mass
		force = mass * self._acceleration

		self._rigidbody.apply_force(force)


def get_circle_body(
		mass: number = 1,
		elasticity: number = 1,
		radius: number = 1,
		color = (255, 255, 255), layer: int = 1,
		components: Iterable[SimObjectComponent] = ()):
	"""
	A factory function for creating a sim_object that models a circle
	and has a CircleCollider and a CircleRenderer
	"""
	# kinda like a prefab in Unity
	shape = pymunk.Circle(None, radius)
	shape.mass = mass
	shape.elasticity = elasticity
	rigidbody = RigidBody(shape)
	renderer = CircleRenderer(radius, color, layer)

	return SimObject((renderer, rigidbody, *components))
