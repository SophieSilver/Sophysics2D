from .selection import BodyController
from .reference_frame import ReferenceFrameManager
from sophysics_engine import SimEnvironment


# Deletes a celestial body and resets the reference frame
def delete_body(environment: SimEnvironment, body: BodyController):
    if body is None:
        return

    # If it's the current reference frame, reset it
    reference_frame_manager: ReferenceFrameManager = environment.get_component(ReferenceFrameManager)
    if body.rigidbody is reference_frame_manager.origin_body:
        body.origin_body = None

    body.sim_object.destroy()

