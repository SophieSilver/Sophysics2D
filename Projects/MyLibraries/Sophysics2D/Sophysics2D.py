import pygame.draw

from Sophysics2DCore import *


class BorderCollider(Collider, BoundingVolume):
	"""
	A border collider of the simulation
	"""
	def __init__(self, top: number, bottom: number, left: number, right: number):
		Collider.__init__(self)
		BoundingVolume.__init__(self, top, bottom, left, right)

	def check_collision(self, other: Collider):
		# check if 'other is outside the boundaries basically'
		if(not isinstance(other, Collider)):
			raise TypeError("'other' must be an instance of 'Collider'")

		collided = self.collides_with(other)

		if(collided):
			self.on_collision(other)
			other.on_collision(self)

	def collides_with(self, other: Collider):
		"""
		Check for collision with another collider
		"""
		if (not isinstance(other, Collider)):
			raise TypeError("'other' must be an instance of 'Collider'")

		collided = (
				other.top >= self.top or
				other.bottom <= self.bottom or
				other.left <= self.left or
				other.right >= self.right)

		return collided


class CircleCollider(Collider):
	def __init__(self, radius: number):
		validate_positive_number(radius, "radius")
		self._radius = radius
		super().__init__()

	@property
	def radius(self):
		return self._radius

	@radius.setter
	def radius(self, value: number):
		validate_positive_number(value, "radius")
		self._radius = value

	@property
	def top(self):
		return self.sim_object.transform.position.y + self._radius

	@property
	def bottom(self):
		return self.sim_object.transform.position.y - self._radius

	@property
	def left(self):
		return self.sim_object.transform.position.x - self._radius

	@property
	def right(self):
		return self.sim_object.transform.position.x + self._radius

	def check_collision(self, other: Collider):
		# gonna check for the type of 'other' and then call respective method
		if(not isinstance(other, Collider)):
			raise TypeError("'other' must be an instance of 'Collider'")

		# there is probably a better way to do this
		collided = False
		if(isinstance(other, CircleCollider)):
			# check if 2 circles collide
			collided = self.collides_with_circle(other)
		elif(isinstance(other, BorderCollider)):
			# let the border collider check
			collided = other.collides_with(self)

		# Add more cases here in the future

		if(collided):
			self.on_collision(other)
			other.on_collision(self)

	def collides_with_circle(self, other: Collider):
		"""
		Check for collision with a circle Collider
		"""
		if (not isinstance(other, CircleCollider)):
			raise TypeError("'other' must be an instance of 'CircleCollider'")

		# check if the distance is smaller than the sum of radii
		self_position = self.sim_object.transform.position
		other_position = other.sim_object.transform.position

		distance = self_position.distance_to(other_position)
		return distance <= self.radius + other.radius


class BoundaryRenderer(Renderer):
	"""
	A renderer for bounding boxes
	"""
	def __init__(self, boundary: BoundingVolume, color = (255, 255, 255), stroke_width: int = 1, layer: int = 0):
		# initializing fields
		self.__boundary: Optional[BoundingVolume] = None
		self.__stroke_width = 1
		# calling setters
		self.stroke_width = stroke_width
		self.boundary = boundary
		# too lazy to encapsulate it into a property, if it's invalid, pygame's gonna bite your head off anyway
		self.color = color

		super().__init__(layer)

	@property
	def boundary(self):
		return self.__boundary

	@boundary.setter
	def boundary(self, value: BoundingVolume):
		if (not isinstance(value, BoundingVolume)):
			raise TypeError("'boundary' must be a BoundingVolume")

		self.__boundary = value

	@property
	def stroke_width(self):
		return self.__stroke_width

	@stroke_width.setter
	def stroke_width(self, value: number):
		if(not isinstance(value, int)):
			raise TypeError("stroke_width must be an integer")

		validate_positive_number(value)

		self.__stroke_width = value

	def render(self):
		surface = self._manager.surface

		# getting dimensions in world space
		position = self.sim_object.transform.position

		world_top = self.__boundary.top + position.y
		world_bottom = self.__boundary.bottom + position.y
		world_left = self.__boundary.left + position.x
		world_right = self.__boundary.right + position.x

		# converting dimensions to screen space
		screen_left, screen_top = self._manager.world_to_screen((world_left, world_top))
		screen_right, screen_bottom = self._manager.world_to_screen((world_right, world_bottom))

		# defining the rect
		screen_height = screen_bottom - screen_top      # because y screen coords are flipped (y axis goes down)
		screen_width = screen_right - screen_left

		rect = pygame.Rect(screen_left, screen_top, screen_width, screen_height)
		# actually drawing the box
		pygame.draw.rect(surface, self.color, rect, self.stroke_width)


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

	def render(self):
		surface = self._manager.surface

		world_position = self.sim_object.transform.position
		screen_position = self._manager.world_to_screen(world_position)

		pygame.draw.circle(surface, self.color, screen_position, self.pixel_radius)


class DefaultEnvironment(SimEnvironment):
	def __init__(self, sim_objects: Iterable[SimObject] = (), components: Iterable[EnvironmentComponent] = ()):
		super().__init__(sim_objects, components)
		self.render_manager: Optional[RenderManager] = None      # will be set later in start()
		self.collider_manager: Optional[ColliderManager] = None

	def start(self):
		# get the necessary references
		self.render_manager = self.get_component(RenderManager)
		self.collider_manager = self.try_get_component(ColliderManager)
		# if the collider manager wasn't set
		if(self.collider_manager is None):
			self.collider_manager = ColliderManager()
			self.attach_component(self.collider_manager)

		# will call start() on all components and sim_objects
		super().start()

	def advance(self):
		self.collider_manager.update()

	def render(self):
		"""
		Renders a snapshot of the simulation
		"""
		self.render_manager.update()


def get_circle_body(
		radius: number = 1,
		color = (255, 255, 255), layer: int = 1,
		components: Iterable[SimObjectComponent] = ()):
	"""
	A factory function for creating a sim_object that models a circle
	and has a CircleCollider and a CircleRenderer
	"""
	# kinda like a prefab in Unity
	renderer = CircleRenderer(radius, color, layer)
	collider = CircleCollider(radius)

	return SimObject((renderer, collider, *components))


def get_border_object(
		top: number, bottom: number, left: number, right: number,
		color = (255, 255, 255), stroke_width: int = 1, layer: int = 0,
		components: Iterable[SimObjectComponent] = ()):
	"""
	A factory function for creating a border object for the simulation with a collider and a renderer
	"""
	collider = BorderCollider(top, bottom, left, right)

	bounding_volume = BoundingVolume(top, bottom, left, right)
	renderer = BoundaryRenderer(bounding_volume, color, stroke_width, layer)

	return SimObject((collider, renderer, *components))
