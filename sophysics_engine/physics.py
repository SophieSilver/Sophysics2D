"""
A set of components that are used to simulate physics
"""
from __future__ import annotations

import pygame
import pymunk

from abc import ABC, abstractmethod
from .event import Event
from .event_system import EventSystem
from .simulation import SimObjectComponent, Transform, EnvironmentComponent, AdvanceTimeStepEvent
from .time_settings import TimeSettings
from .helper_functions import validate_positive_number

from typing import Optional, Iterable, Set, Union, Sequence


number = Union[int, float]


class RigidBodySyncBodyWithSimObjectEvent(Event):
    pass


class RigidBodySyncSimObjectWithBodyEvent(Event):
    pass


class RigidBodyExertForcesEvent(Event):
    pass


class PostPhysicsUpdateEvent(Event):
    """
    An event that's raised when all physics calculations for the current timestep are done
    """
    pass


class Force(SimObjectComponent, ABC):
    """
    A base class for Force components.

    Force component passes force to the rigidbody of the sim_object
    """
    def __init__(self):
        self._rigidbody: Optional[RigidBody] = None
        super().__init__()

    def setup(self):
        super().setup()
        self._rigidbody: RigidBody = self.sim_object.get_component(RigidBody)
        event_system = self.sim_object.environment.event_system
        event_system.add_listener(RigidBodyExertForcesEvent, self.__handle_exert_force_event)

    def __handle_exert_force_event(self, _: RigidBodyExertForcesEvent):
        self.exert()

    @abstractmethod
    def exert(self):
        """
        Exerts force on the rigidbody
        """
        pass

    def _on_destroy(self):
        event_system = self.sim_object.environment.event_system
        event_system.remove_listener(RigidBodyExertForcesEvent, self.__handle_exert_force_event)
        self._rigidbody = None


class CollisionListener(SimObjectComponent):
    """
    A collision listener contains methods that get called whenever the sim object it is attached to
    is colliding with another sim object.
    """
    def __init__(self):
        self._rigidbody: Optional[RigidBody] = None

        super().__init__()

    def setup(self):
        self._rigidbody = self.sim_object.get_component(RigidBody)
        self._rigidbody.attach_collision_listener(self)

    def begin(self, other_body: RigidBody, arbiter: pymunk.Arbiter) -> bool:
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

    def pre_solve(self, other_body: RigidBody, arbiter: pymunk.Arbiter) -> bool:
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

    def post_solve(self, other_body: RigidBody, arbiter: pymunk.Arbiter):
        """
        Two shapes are touching and their collision response has been processed.

        You can retrieve the collision impulse or kinetic energy at this time if you want
        to use it to calculate sound volumes or damage amounts.
        """
        pass

    def separate(self, other_body: RigidBody, arbiter: pymunk.Arbiter):
        """
        Two shapes have just stopped touching for the first time this step.

        To ensure that begin()/separate() are always called in balanced pairs,
        it will also be called when removing a shape while its in contact with something
        or when de-allocating the space.
        """
        pass

    def _on_destroy(self):
        self._rigidbody.remove_collision_listener(self)


class RigidBody(SimObjectComponent):
    """
    Handles the movement of the SimObject according to physics.

    A wrapper for pymunk's shape and body
    """
    def __init__(self, shapes: Iterable[pymunk.Shape] = (),
                 body_type: int = pymunk.Body.DYNAMIC):
        super().__init__()

        # initializing fields
        self._transform: Optional[Transform] = None
        self._space: Optional[pymunk.Space] = None
        self._body: pymunk.Body = SophysicsBody(self, body_type=body_type)
        self._shapes: Set[pymunk.Shape] = set()
        self._collision_listeners: Set[CollisionListener] = set()

        # attaching the shapes
        for s in shapes:
            self.attach_shape(s)

        # setting a default shape (if no shapes were passed)
        if(len(self.shapes) <= 0):
            default_shape = pymunk.Circle(self._body, 1)
            default_shape.mass = 1
            default_shape.elasticity = 0.5
            self.attach_shape(default_shape)

    def setup(self):
        super().setup()
        self._transform = self.sim_object.transform
        environment = self.sim_object.environment
        rb_manager: PhysicsManager = environment.get_component(PhysicsManager)
        self._space = rb_manager.space
        self._space.add(self._body, *self.shapes)

        # syncing the pymunk body position and sim_object's position
        # (doing that awkwardness because pymunk and pygame use different Vector classes)
        # (Both are iterables so we can unpack like that)
        self._body.position = pymunk.Vec2d(*self._transform.position)

        # subscribing to events
        event_system = environment.event_system
        event_system.add_listener(RigidBodySyncBodyWithSimObjectEvent, self.__handle_sync_with_sim_object_event)
        event_system.add_listener(RigidBodySyncSimObjectWithBodyEvent, self.__handle_sync_with_body_event)

    def __handle_sync_with_body_event(self, _: RigidBodySyncSimObjectWithBodyEvent):
        self.__sync_sim_object_with_body()

    def __handle_sync_with_sim_object_event(self, _: RigidBodySyncBodyWithSimObjectEvent):
        self.__sync_body_with_sim_object()

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
    def shapes(self) -> set[pymunk.Shape]:
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
    def velocity(self, value: Sequence[number]):
        """
        velocity must be an iterable with at least 2 items, e.g. pygame.Vector2, pymunk.Vec2d, a tuple, a list or
        any user defined iterable type.

        The first two items represent the x and y components of the velocity vector respectively. Any subsequent items
        are ignored.

        Under the hood the velocity is represented as pymunk.Vec2d
        """
        x, y, *_ = value
        del _

        self._body.velocity = pymunk.Vec2d(x, y)

    def attach_shape(self, shape: pymunk.Shape):
        """
        Attaches the shape to the rigidbody
        """
        if(not isinstance(shape, pymunk.Shape)):
            raise TypeError("shape should be an instance of pymunk.Shape")

        shape.body = self._body
        self._shapes.add(shape)

        if(self.is_set_up):
            self._space.add(shape)

    def remove_shape(self, shape: pymunk.Shape):
        """
        Removes the shape from the rigidbody
        """
        if (not isinstance(shape, pymunk.Shape)):
            raise TypeError("shape should be an instance of pymunk.Shape")

        if(self.is_set_up):
            self._space.remove(shape)

        shape.body = None
        self._shapes.remove(shape)

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

    def apply_force(self, force: Union[Sequence[number], pygame.Vector2]):
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

        self._collision_listeners.add(listener)

    def remove_collision_listener(self, listener: CollisionListener):
        if (not isinstance(listener, CollisionListener)):
            raise TypeError("listener argument has to be of type CollisionListener")

        self._collision_listeners.remove(listener)

    def collision_begin(self, other_body: RigidBody, arbiter: pymunk.Arbiter) -> bool:
        """
        Calls the begin callback method on all collision listeners

        returns a boolean value that tells whether to further process the collision (which is the return
        values of all called methods AND'ed together)
        """
        process_collision = True
        for listener in self._collision_listeners:
            result = listener.begin(other_body, arbiter)
            process_collision = process_collision and (result if result is not None else True)

        return process_collision

    def collision_pre_solve(self, other_body: RigidBody, arbiter: pymunk.Arbiter) -> bool:
        """
        Calls the pre_solve callback method on all collision listeners

        returns a boolean value that tells whether to further process the collision (which is the return
        values of all called methods AND'ed together)
        """
        process_collision = True
        for listener in self._collision_listeners:
            result = listener.pre_solve(other_body, arbiter)
            process_collision = process_collision and (result if result is not None else True)

        return process_collision

    def collision_post_solve(self, other_body: RigidBody, arbiter: pymunk.Arbiter):
        """
        Calls the post_solve callback method on all collision listeners
        """
        for listener in self._collision_listeners:
            listener.post_solve(other_body, arbiter)

    def collision_separate(self, other_body: RigidBody, arbiter: pymunk.Arbiter):
        """
        Calls the separate callback method on all collision listeners
        """
        for listener in self._collision_listeners:
            listener.separate(other_body, arbiter)

    @property
    def collision_listeners(self) -> set[CollisionListener]:
        """
        all collision listeners attached to this
        """
        return self._collision_listeners

    def _on_destroy(self):
        event_system = self.sim_object.environment.event_system
        event_system.remove_listener(RigidBodySyncBodyWithSimObjectEvent, self.__handle_sync_with_sim_object_event)
        event_system.remove_listener(RigidBodySyncSimObjectWithBodyEvent, self.__handle_sync_with_body_event)

        self._space.remove(*self.shapes, self._body)


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


class PhysicsManager(EnvironmentComponent):
    """
    The manager for RigidBody components
    """
    def __init__(self):
        super().__init__()
        self.__event_system: Optional[EventSystem] = None
        self.__time_settings: Optional[TimeSettings] = None
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

            return body1.collision_begin(body2, arbiter) and body2.collision_begin(body1, arbiter)

        def pre_solve(arbiter: pymunk.Arbiter, *_) -> bool:
            shapes = arbiter.shapes
            body1: RigidBody = shapes[0].body.rigidbody
            body2: RigidBody = shapes[1].body.rigidbody

            return body1.collision_pre_solve(body2, arbiter) and body2.collision_pre_solve(body1, arbiter)

        def post_solve(arbiter: pymunk.Arbiter, *_):
            shapes = arbiter.shapes
            body1: RigidBody = shapes[0].body.rigidbody
            body2: RigidBody = shapes[1].body.rigidbody

            body1.collision_post_solve(body2, arbiter)
            body2.collision_post_solve(body1, arbiter)

        def separate(arbiter: pymunk.Arbiter, *_):
            shapes = arbiter.shapes
            body1: RigidBody = shapes[0].body.rigidbody
            body2: RigidBody = shapes[1].body.rigidbody

            body1.collision_separate(body2, arbiter)
            body2.collision_separate(body1, arbiter)

        collision_handler = self._space.add_default_collision_handler()
        collision_handler.begin = begin
        collision_handler.pre_solve = pre_solve
        collision_handler.post_solve = post_solve
        collision_handler.separate = separate

    def setup(self):
        super().setup()

        self.__time_settings = self.environment.get_component(TimeSettings)
        self.__event_system = self.environment.event_system
        self.__event_system.add_listener(AdvanceTimeStepEvent, self.__handle_advance_timestep_event)

    def __handle_advance_timestep_event(self, _: AdvanceTimeStepEvent):
        self.advance_timestep()

    @property
    def space(self):
        """
        The reference to the current pymunk's simulation space
        """
        return self._space

    def advance_timestep(self):
        # put all pymunk bodies to the same positions as the transforms
        self.__event_system.raise_event(RigidBodySyncBodyWithSimObjectEvent())
        self.__event_system.raise_event(RigidBodyExertForcesEvent())
        self._space.step(self.__time_settings.dt)
        self.__event_system.raise_event(RigidBodySyncSimObjectWithBodyEvent())
        self.__event_system.raise_event(PostPhysicsUpdateEvent())

    def _on_destroy(self):
        self.__event_system.remove_listener(AdvanceTimeStepEvent, self.__handle_advance_timestep_event)
        super()._on_destroy()
