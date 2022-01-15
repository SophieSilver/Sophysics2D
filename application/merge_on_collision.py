import pygame

from sophysics_engine import CollisionListener, RigidBody
import pymunk


class MergeOnCollision(CollisionListener):
    def begin(self, other_body: RigidBody, arbiter: pymunk.Arbiter) -> bool:
        # if this body is lighter, then schedule itself for deletion
        # it checks if the other body is scheduled for deletion
        # because if they have the same mass, then the one that's deleted
        # is the one that called this method first
        if self._rigidbody.mass <= other_body.mass and \
                other_body.sim_object not in self.sim_object.environment.to_be_destroyed_sim_objects:
            self.sim_object.environment.destroy_after_step(self.sim_object)
            return False

        mass1, mass2 = self._rigidbody.mass, other_body.mass
        pos1, pos2 = self.sim_object.transform.position, other_body.sim_object.transform.position
        vel1, vel2 = map(pygame.Vector2, (self._rigidbody.velocity, other_body.velocity))

        new_mass = mass1 + mass2

        new_vel = (mass1 * vel1 + mass2 * vel2) / new_mass
        new_pos = (mass1 * pos1 + mass2 * pos2) / new_mass

        self._rigidbody.mass = new_mass
        self._rigidbody.shapes.copy().pop().mass = new_mass     # also need to change the mass on the shape

        self._rigidbody.velocity = new_vel

        self.sim_object.transform.position = new_pos

        return False
