from Sophysics2D import *
import pygame


def main():
    pygame.init()
    # This is a dummy application to test the functionality of Sophysics2D
    display = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Sophysics 2D")

    rm = RenderManager(display)
    rbm = RigidBodyManager()
    env = DefaultEnvironment(components=(rm, rbm))

    ball1_transform = Transform(pygame.Vector2(0, 0))
    grav_acc = ConstantAcceleration((0, -1))
    ball1 = get_circle_body(1, 1, 1, (255, 0, 0), 1, (ball1_transform, grav_acc))
    print(ball1.get_component(RigidBody).shape.radius)

    ball2 = get_circle_body(1, 1, radius=1, color=(0, 255, 0), layer=1)

    env.attach_object(ball1)
    env.attach_object(ball2)
    env.start()
    running = True
    clock = pygame.time.Clock()

    while(running):
        clock.tick(60)
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                running = False

        env.advance()
        env.render()
        # ball1_transform.position.x -= 0.01
        pygame.display.update()


if(__name__ == "__main__"):
    main()
