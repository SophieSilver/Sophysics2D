import sys
from Sophysics2D import *


def main():
    pygame.init()
    pygame.font.init()
    # This is a dummy application to test the functionality of Sophysics2D
    display = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Sophysics 2D")
    consolas = pygame.font.SysFont("consolas", 16)

    rm = RenderManager(display, 1/80)
    rbm = PhysicsManager()
    env = DefaultEnvironment(components=(rm, rbm))

    ball1_transform = Transform(pygame.Vector2(0, 0))
    grav_acc = lambda: ConstantAcceleration((0, -9.8))
    ball1 = get_circle_body("red ball", 1, 1, 1, (255, 0, 0), 1, (ball1_transform, grav_acc()))
    ball2 = get_circle_body("green ball", 1, 1, radius=1, color=(0, 255, 0), layer=1, components=(grav_acc(),))
    border = get_border_object("border", 4, -4, -7, 7, 1, Color.WHITE, 0)

    env.attach_sim_object(ball1)
    ball1.get_component(RigidBody).body.velocity = pymunk.Vec2d(3, 4)
    env.attach_sim_object(border)
    env.attach_sim_object(ball2)
    clock = pygame.time.Clock()
    steps = 1

    del ball1_transform

    rb1 = ball1.get_component(RigidBody)
    rb2 = ball2.get_component(RigidBody)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                sys.exit()

        if steps % 307 == 1:
            env.destroy_after_step(ball1)

        if steps % 307 == 134:
            env.attach_sim_object(ball1)
        env.advance()
        env.render()
        e1 = get_energy(rb1)
        e2 = get_energy(rb2)
        text = consolas.render(f"e1: {e1:.3}, e2: {e2:.3}, e_total: {e1 + e2:.2f}", True, (0, 255, 0))

        display.blit(text, (0, 0))

        pygame.display.update()
        steps += 1


def get_energy(obj: RigidBody):
    kin_energy = (obj.body.mass * obj.body.velocity.length ** 2) / 2
    pot_energy = obj.body.mass * 9.8 * (obj.sim_object.transform.position.y + 4)
    return pot_energy + kin_energy


if(__name__ == "__main__"):
    main()
